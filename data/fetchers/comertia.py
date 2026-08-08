"""
Indicador Comertia — variació interanual de les vendes dels socis de Comertia
(associació d'empreses familiars catalanes del comerç, comertia.net).

ÚS INTERN, NO PUBLICABLE
------------------------
Són dades d'un tercer, obtingudes de les seves notes de premsa mensuals. Serveixen
per contrastar el nostre motor amb un indicador privat del sector, no per publicar-les
al dashboard. Per això la sortida va a `data/raw/` (ignorat per .gitignore, igual que
l'export de SABI) i aquest fetcher NO està registrat a `data/processor.py`: el workflow
diari no el crida i el repo públic no conté cap xifra seva. Si algun dia han de sortir
cap enfora, ha de ser amb permís de Comertia.

Font
----
API de WordPress de comertia.net. Cada mes publiquen una nota de premsa que porta la
xifra al titular, amb la forma "Els establiments adherits a Comertia creixen un <valor>%
al <mes>, respecte del mateix mes de l'any anterior". D'aquí surten el valor i el mes de
referència; la data del post dona el retard de publicació (habitualment els primers dies
del mes següent, unes tres setmanes abans que l'INE publiqui l'ICM del mateix mes).

Mesos sense nota de premsa
--------------------------
Alguns mesos no tenen nota però sí apareixen etiquetats al gràfic del PDF de l'Indicador
del mes següent. Aquests valors es llegeixen a mà i es posen a
`data/raw/comertia/overrides.json` ({"AAAA-MM-01": <valor>, ...}), que tampoc es
committeja. Si el fitxer no hi és, `build_serie()` avisa de quins mesos queden buits.

Avís de qualitat: Comertia revisa xifres sense dir-ho, i algun mes el valor de la nota de
premsa i el que apareix al gràfic del PDF del mes següent no coincideixen. Aquí la font
primària és la nota de premsa, per ser text i no píxel.
"""
import calendar
import json
import os
import re
import unicodedata
from datetime import date

import pandas as pd
import requests

API = "https://www.comertia.net/wp-json/wp/v2/posts"
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw", "comertia")
CSV_PATH = os.path.join(RAW_DIR, "indicador_comertia.csv")
OVERRIDES_PATH = os.path.join(RAW_DIR, "overrides.json")

MESOS = {
    "gener": 1, "febrer": 2, "marc": 3, "abril": 4, "maig": 5, "juny": 6,
    "juliol": 7, "agost": 8, "setembre": 9, "octubre": 10, "novembre": 11,
    "desembre": 12,
}
# Verbs que indiquen caiguda: el titular dona la magnitud en positiu i el signe al verb.
NEGATIUS = ("cauen", "baixen", "decreixen", "redueixen", "disminueixen",
            "descens", "caiguda", "per sota")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Observatori-Comerc/1.0",
    "Accept": "application/json",
}


def _sense_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _neteja_titol(html):
    """Treu etiquetes i entitats HTML del titular i normalitza els apòstrofs."""
    t = re.sub(r"<[^>]+>", "", html)
    for ent, ch in (("&#8217;", "'"), ("&#8211;", "-"), ("&amp;", "&"),
                    ("&nbsp;", " "), ("&#8220;", '"'), ("&#8221;", '"')):
        t = t.replace(ent, ch)
    return t.replace("’", "'").strip()


def _mes_referencia(titol, data_post):
    """Mes al qual es refereix la xifra: el més recent anterior a la publicació.

    Cal la regla del "més recent anterior" perquè les notes de desembre surten al
    gener següent i el nom del mes, tot sol, seria ambigu.
    """
    m = re.search(r"\b(" + "|".join(MESOS) + r")\b", _sense_accents(titol.lower()))
    if not m:
        return None
    mi = MESOS[m.group(1)]
    candidats = [date(y, mi, 1) for y in (data_post.year, data_post.year - 1)]
    anteriors = [d for d in candidats if d <= data_post]
    return max(anteriors) if anteriors else None


def _parse_titol(titol, data_post):
    """Retorna (mes_referencia, valor) o (None, None) si el titular no és l'indicador."""
    if "comertia" not in titol.lower():
        return None, None
    mv = re.search(r"(\d+(?:[,\.]\d+)?)\s*%", titol)
    if not mv:
        return None, None
    mes = _mes_referencia(titol, data_post)
    if mes is None:
        # Titulars com "el mes de Nadal" o "el mes del Black Friday": el mes no és
        # identificable de manera fiable, no els inventem.
        return None, None
    valor = float(mv.group(1).replace(",", "."))
    if any(w in _sense_accents(titol.lower()) for w in NEGATIUS):
        valor = -valor
    return mes, valor


def fetch_notes(max_pagines=6, timeout=30):
    """Descarrega els titulars de comertia.net i n'extreu la sèrie mensual.

    Retorna un DataFrame amb data (mes de referència), valor, data_publicacio,
    retard_dies i titol. Llista buida si l'API no respon: aquesta font no és
    crítica i no ha de fer caure res.
    """
    posts = []
    for pagina in range(1, max_pagines + 1):
        params = {"per_page": 100, "page": pagina, "_fields": "date,title,link"}
        try:
            resp = requests.get(API, params=params, headers=HEADERS, timeout=timeout)
        except requests.RequestException as e:
            print(f"Comertia: error de xarxa a la pagina {pagina}: {e}")
            break
        # La API retorna 400 quan es demana una pagina mes enlla de l'ultima.
        if resp.status_code == 400:
            break
        if resp.status_code != 200:
            print(f"Comertia: HTTP {resp.status_code} a la pagina {pagina}")
            break
        lot = resp.json()
        if not lot:
            break
        posts.extend(lot)

    files = []
    for p in posts:
        titol = _neteja_titol(p["title"]["rendered"])
        data_post = date.fromisoformat(p["date"][:10])
        mes, valor = _parse_titol(titol, data_post)
        if mes is None:
            continue
        final_de_mes = date(mes.year, mes.month,
                            calendar.monthrange(mes.year, mes.month)[1])
        files.append({
            "data": mes.isoformat(),
            "valor": valor,
            "data_publicacio": data_post.isoformat(),
            "retard_dies": (data_post - final_de_mes).days,
            "font": "nota_premsa",
            "titol": titol,
        })

    if not files:
        return pd.DataFrame()

    df = pd.DataFrame(files).sort_values("data")
    # Si un mes surt a dues notes, ens quedem amb la publicacio mes antiga (la
    # primera lectura), coherent amb usar la nota com a font primaria.
    return df.drop_duplicates(subset="data", keep="first").reset_index(drop=True)


def _carrega_overrides():
    if not os.path.exists(OVERRIDES_PATH):
        return {}
    with open(OVERRIDES_PATH, encoding="utf-8") as f:
        dades = json.load(f)
    # Les claus que comencen amb "_" son notes del fitxer, no mesos.
    return {k: v for k, v in dades.items() if not k.startswith("_")}


def build_serie(desa=True, verbose=True):
    """Sèrie mensual completa: notes de premsa + valors llegits del gràfic del PDF.

    Retorna un DataFrame [data, valor, font, data_publicacio, retard_dies, titol]
    ordenat per data. Avisa dels mesos que queden buits dins el rang.
    """
    df = fetch_notes()
    if df.empty:
        if verbose:
            print("Comertia: cap nota descarregada")
        return df

    overrides = _carrega_overrides()
    ja_hi_son = set(df["data"])
    extres = [{"data": k, "valor": float(v), "font": "grafic_pdf",
               "data_publicacio": None, "retard_dies": None, "titol": None}
              for k, v in overrides.items() if k not in ja_hi_son]
    if extres:
        df = pd.concat([df, pd.DataFrame(extres)], ignore_index=True)
    df = df.sort_values("data").reset_index(drop=True)

    if verbose:
        idx = pd.to_datetime(df["data"])
        rang = pd.date_range(idx.min(), idx.max(), freq="MS")
        buits = [d.strftime("%Y-%m") for d in rang.difference(idx)]
        print(f"Comertia: {len(df)} mesos, de {df['data'].iloc[0][:7]} "
              f"a {df['data'].iloc[-1][:7]}")
        print(f"  Notes de premsa: {(df['font'] == 'nota_premsa').sum()}, "
              f"grafic del PDF: {(df['font'] == 'grafic_pdf').sum()}")
        if buits:
            print(f"  Mesos sense dada ({len(buits)}): {', '.join(buits)}")
            print(f"  Per omplir-los, afegeix-los a {OVERRIDES_PATH} "
                  "llegint-los del grafic de l'Indicador del mes seguent.")
        retards = df["retard_dies"].dropna()
        if len(retards):
            print(f"  Retard de publicacio: mediana {retards.median():.0f} dies "
                  f"des del tancament del mes de referencia")

    if desa:
        os.makedirs(RAW_DIR, exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
        if verbose:
            print(f"  Desat: {CSV_PATH}")
    return df


def load_serie():
    """Llegeix la sèrie desada a data/raw/. DataFrame buit si no existeix encara."""
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)


if __name__ == "__main__":
    build_serie()

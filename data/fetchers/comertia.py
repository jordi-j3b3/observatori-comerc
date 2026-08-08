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


# ─── Detall sectorial (cos de la nota de premsa) ────────────────────────────
#
# El titular només porta la mitjana. El cos de cada nota porta dues coses més que no
# hi ha en cap altra font: el creixement per sector i el pes de la venda en línia
# sobre la facturació de cada sector. Cap de les dues es publica en sèrie enlloc.
#
# El text és prosa, no una taula, i canvia de forma cada mes. La regla d'aquest parser
# és no endevinar mai: només s'accepta un valor quan el patró és inequívoc i quan el
# nombre de sectors citats coincideix amb el de xifres. Un mes amb cobertura parcial és
# un mes amb cobertura parcial; un mes amb un valor inventat contamina tota la sèrie.

SECTORS = {
    "moda": "Moda",
    "complements persona": "Complements Persona",
    "compl persona": "Complements Persona",
    "alimentacio basica": "Alimentació Bàsica",
    "alimentacio no basica": "Alimentació No Bàsica",
    "oci-cultura": "Oci-Cultura",
    "oci cultura": "Oci-Cultura",
    "equipament de la llar": "Equipament de la Llar",
    "equipament llar": "Equipament de la Llar",
    "equip llar": "Equipament de la Llar",
    "restauracio": "Restauració",
    "altres": "Altres",
}
# Es prova primer el nom més llarg: si no, "alimentacio basica" engoliria
# "alimentacio no basica".
_CLAUS_SECTOR = sorted(SECTORS, key=len, reverse=True)

# Marges de plausibilitat. El pes en línia és una proporció i no pot ser negatiu; el
# febrer de 2026 la nota de Comertia en publica dos de negatius (Equip Llar −3,8%,
# Moda −9%), que són impossibles com a pes i que aquest filtre deixa fora.
LIMIT_CREIXEMENT = 60.0
LIMIT_ONLINE = (0.0, 60.0)


def _norm(s):
    """Minúscules, sense accents i amb els separadors uniformats."""
    s = s.replace("’", "'").replace("\xa0", " ")
    s = "".join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    s = s.lower().replace(".", " ").replace("-", "-")
    s = re.sub(r"-\s+", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def _sector_de(fragment):
    n = _norm(fragment)
    for clau in _CLAUS_SECTOR:
        if clau in n:
            return SECTORS[clau]
    return None


def _frases(text):
    """Talla per frases protegint "Equip. Llar" i "Compl. Persona".

    Aquests dos sectors s'abreugen amb un punt enmig del nom i qualsevol tall ingenu
    per punt els parteix, deixant mitja frase sense sector.
    """
    t = text
    for a, b in (("Equip. ", "Equip‧ "), ("Compl. ", "Compl‧ "),
                 ("equip. ", "equip‧ "), ("compl. ", "compl‧ ")):
        t = t.replace(a, b)
    return [f.replace("‧", "").strip() for f in re.split(r"(?<=[.!?])\s+", t)]


def _sectors_en_ordre(fragment):
    """Sectors citats en un fragment, sense repetir i en ordre d'aparició."""
    trobats, vistos = [], set()
    for m in re.finditer(r"[A-Za-zÀ-ÿ'·\-\. ]{3,45}", fragment):
        s = _sector_de(m.group(0))
        if s and s not in vistos:
            vistos.add(s)
            trobats.append(s)
    return trobats


def _xifres(fragment):
    return [float(x.replace(",", ".")) for x in
            re.findall(r"(-?\d+(?:[,\.]\d+)?)\s*%", fragment)]


def _parell_parentesi(frase):
    """Patró dominant i més segur: 'Sector (12,3%)'."""
    out = []
    for m in re.finditer(r"([A-Za-zÀ-ÿ'·\-\. ]{3,45}?)\s*\((-?\d+(?:[,\.]\d+)?)\s*%\)",
                         frase):
        s = _sector_de(m.group(1))
        if s:
            out.append((s, float(m.group(2).replace(",", ".")), "parentesi"))
    return out


def _parell_llista(frase):
    """Patró 'A, B i C han liderat ... amb 8,1%, 7,8% i 4,6%'.

    Només s'aparella quan hi ha tants sectors com xifres. Si no quadren, no hi ha cap
    manera segura de saber quina xifra és de qui i es descarta la frase sencera.
    """
    n = _norm(frase)
    if not re.search(r"lidera|liderat|segueix|segueixen", n):
        return []
    tall = re.split(r"\bamb\b", frase)
    if len(tall) < 2:
        return []
    sectors = _sectors_en_ordre(tall[0])
    valors = _xifres("amb".join(tall[1:]))
    if not sectors or len(sectors) != len(valors):
        return []
    negatiu = bool(re.search(r"descens|caiguda|patit|negatiu", n))
    return [(s, -abs(v) if negatiu and v > 0 else v, "llista")
            for s, v in zip(sectors, valors)]


def _parell_descens(frase):
    """'Moda ha patit un descens important amb un resultat del -1,2%'."""
    n = _norm(frase)
    if not re.search(r"descens|caiguda|resultat negatiu", n):
        return []
    sectors = _sectors_en_ordre(frase.split(" ha ")[0].split(" han ")[0])
    valors = _xifres(frase)
    if len(sectors) != len(valors) or not sectors:
        return []
    return [(s, -abs(v), "descens") for s, v in zip(sectors, valors)]


def _parseja_cos(text):
    """Retorna (creixement_per_sector, pes_online_per_sector) d'una nota."""
    creix, online = {}, {}
    for frase in _frases(text):
        if "%" not in frase:
            continue
        n = _norm(frase)
        if "pes en linia" in n or "pes online" in n or "linia respecte" in n:
            parells = _parell_parentesi(frase)
            # Si un sol valor de la frase és impossible com a proporció, la frase
            # sencera és sospitosa i es descarta. El gener de 2026 la nota publica
            # pesos negatius (Equip Llar −3,8%, Moda −9%) i, al mateix llistat,
            # valors positius fora d'escala (Alimentació Bàsica 12,5% quan la resta
            # de mesos ronda el 3%): sembla que aquell mes van publicar una altra
            # cosa, no el pes. Salvar-ne la meitat seria pitjor que perdre'ls tots.
            if parells and all(LIMIT_ONLINE[0] <= v <= LIMIT_ONLINE[1]
                               for _, v, _ in parells):
                for s, v, _ in parells:
                    online.setdefault(s, v)
            continue
        for s, v, metode in (_parell_parentesi(frase) + _parell_llista(frase)
                             + _parell_descens(frase)):
            if abs(v) <= LIMIT_CREIXEMENT:
                creix.setdefault(s, (v, metode))
    return creix, online


def fetch_detall_sectorial(max_pagines=6, timeout=30):
    """Sèrie mensual per sector: creixement i pes de la venda en línia.

    Retorna un DataFrame llarg amb data, sector, indicador ('creixement' o
    'pes_online'), valor i metode (quin patró l'ha capturat, per poder auditar).
    """
    posts = []
    for pagina in range(1, max_pagines + 1):
        params = {"per_page": 100, "page": pagina, "_fields": "date,title,content"}
        try:
            resp = requests.get(API, params=params, headers=HEADERS, timeout=timeout)
        except requests.RequestException as e:
            print(f"Comertia: error de xarxa a la pagina {pagina}: {e}")
            break
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
        mes, _ = _parse_titol(titol, data_post)
        if mes is None:
            continue
        text = _neteja_titol(p["content"]["rendered"])
        creix, online = _parseja_cos(text)
        for s, (v, metode) in creix.items():
            files.append({"data": mes.isoformat(), "sector": s,
                          "indicador": "creixement", "valor": v, "metode": metode})
        for s, v in online.items():
            files.append({"data": mes.isoformat(), "sector": s,
                          "indicador": "pes_online", "valor": v, "metode": "parentesi"})

    if not files:
        return pd.DataFrame()
    df = pd.DataFrame(files).drop_duplicates(subset=["data", "sector", "indicador"])
    return df.sort_values(["data", "indicador", "sector"]).reset_index(drop=True)


def build_detall(desa=True, verbose=True):
    """Construeix el detall sectorial i informa de la cobertura mes a mes."""
    df = fetch_detall_sectorial()
    if df.empty:
        if verbose:
            print("Comertia: cap detall sectorial obtingut")
        return df
    if verbose:
        for ind in ("creixement", "pes_online"):
            g = df[df.indicador == ind]
            if g.empty:
                continue
            per_mes = g.groupby("data").size()
            print(f"Comertia {ind}: {len(per_mes)} mesos, "
                  f"{per_mes.min()}-{per_mes.max()} sectors per mes "
                  f"(mediana {per_mes.median():.0f} de {len(set(SECTORS.values()))})")
            fluixos = per_mes[per_mes < 5]
            if len(fluixos):
                print(f"  Mesos amb menys de 5 sectors: "
                      f"{', '.join(f'{k[:7]} ({v})' for k, v in fluixos.items())}")
        print(f"  Metodes: {df.metode.value_counts().to_dict()}")
    if desa:
        os.makedirs(RAW_DIR, exist_ok=True)
        df.to_csv(os.path.join(RAW_DIR, "detall_sectorial.csv"), index=False)
        if verbose:
            print(f"  Desat: {os.path.join(RAW_DIR, 'detall_sectorial.csv')}")
    return df


def load_detall():
    ruta = os.path.join(RAW_DIR, "detall_sectorial.csv")
    return pd.read_csv(ruta) if os.path.exists(ruta) else pd.DataFrame()


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
    print()
    build_detall()

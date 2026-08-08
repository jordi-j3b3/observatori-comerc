"""
Eix 1 de la diagnosi per a Comertia: posició competitiva per format de distribució.

La pregunta que l'Indicador Comertia no es fa. Ells es comparen amb el territori
(Catalunya, Espanya), que és l'eix obvi. L'eix que els retrata és el **format**: contra
quin tipus d'operador creixen i contra quin perden. L'INE publica l'ICM desagregat per
modo de distribució (empreses unilocalitzades, petites cadenes, grans cadenes, grans
superfícies), taules 60105 i 75809, que van substituir l'antiga d'Índexs de Grans
Superfícies descatalogada el desembre de 2023.

El que en surt: Comertia són 65 empreses amb 160 marques i 3.200 establiments, o sigui
estructuralment cadenes, i creixen com la botiga independent d'un sol local, uns tres
punts l'any per sota de les grans cadenes. I qui els menja no és el gran format —les
grans superfícies creixen menys que ells— sinó la xarxa de cadena gran i el canal en
línia.

Sortides, totes a `data/raw/comertia/` (ignorat pel git):
  · posicio_competitiva.csv   — taula mensual completa, per portar a Excel o a Word
  · posicio_competitiva.svg   — gràfic net, sense cap ornament, per encastar al lliurable

Ús: python analisi/comertia_posicio_competitiva.py

Bases de comparació (dir-ho sempre al lliurable)
------------------------------------------------
· Indicador Comertia: facturació autodeclarada dels socis, preus corrents, Catalunya,
  sense cap ajust.
· ICM per modo de distribució: Espanya, preus corrents, ajustat de calendari (NO
  desestacionalitzat: la sèrie de l'INE diu "Datos ajustados de calendario").
· ICM per comunitats i total: preus corrents, sèrie bruta.
Tot es compara en variació interanual, que neutralitza l'estacionalitat i deixa només
l'efecte calendari com a diferència de base, d'unes poques dècimes.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.fetchers import comertia  # noqa: E402

DIR = os.path.dirname(__file__)
CACHE = os.path.join(DIR, "..", "data", "cache")
OUT_DIR = os.path.join(DIR, "..", "data", "raw", "comertia")
BRANCA = "Comercio al por menor, excepto de vehículos de motor y motocicletas"
ONLINE = "Comercio al por menor por correspondencia o Internet"
INICI = "2023-09-01"          # primer mes del tram contigu de la sèrie de Comertia
BASE_MESOS = 12               # any base per a l'índex de posició relativa

COLORS = {
    "Comertia": "#b07d2b",
    "Grans cadenes": "#003366",
    "Empreses unilocalitzades": "#6a6a6a",
    "Petites cadenes": "#8fa6bd",
    "Grans superfícies": "#5a8f3d",
    "Catalunya, total": "#c0c0c0",
}


def _icm(indicador, ambit, tipus, branca=BRANCA):
    d = pd.read_csv(os.path.join(CACHE, "icm.csv"))
    d = d[(d.indicador == indicador) & (d.ambit == ambit)
          & (d.tipus == tipus) & (d.branca == branca)]
    s = d.assign(data=pd.to_datetime(d["data"])).set_index("data")["valor"].sort_index()
    return s[~s.index.duplicated()]


def _formats(indicador, tipus="nominal"):
    d = pd.read_csv(os.path.join(CACHE, "icm_distribucion.csv"))
    d = d[(d.indicador == indicador) & (d.tipus == tipus)]
    p = d.assign(data=pd.to_datetime(d["data"])).pivot_table(
        index="data", columns="modo", values="valor")
    return p.rename(columns={
        "Empresas unilocalizadas": "Empreses unilocalitzades",
        "Pequeñas cadenas": "Petites cadenes",
        "Grandes cadenas": "Grans cadenes",
        "Grandes Superficies": "Grans superfícies",
    })


def carrega():
    com = comertia.load_serie()
    if com.empty:
        com = comertia.build_serie(verbose=False)
    com = (com.assign(data=pd.to_datetime(com["data"]))
              .set_index("data")["valor"].sort_index())

    t = _formats("var_anual")
    t["Comertia"] = com
    t["Catalunya, total"] = _icm("var_anual", "Cataluña", "nominal")
    t["Espanya, total"] = _icm("var_anual", "nacional", "nominal")
    fi = t.drop(columns=["Comertia"]).dropna(how="all").index.max()
    return t.loc[INICI:fi], fi


def index_relatiu(taula):
    """Índex de posició acumulada des de la variació interanual.

    I(t) = I(t−12) · (1 + g(t)/100), amb els 12 primers mesos fixats a 100. Cada sèrie
    rep exactament el mateix tractament, o sigui que la comparació entre elles és neta
    encara que el nivell absolut de cadascuna sigui convencional.
    """
    idx = taula.index
    out = pd.DataFrame(index=idx, columns=taula.columns, dtype=float)
    out.iloc[:BASE_MESOS] = 100.0
    for i in range(BASE_MESOS, len(idx)):
        out.iloc[i] = out.iloc[i - BASE_MESOS] * (1 + taula.iloc[i] / 100.0)
    return out


def valida_reconstruccio(rel):
    """Contrasta l'índex reconstruït amb els nivells que publica l'INE per als formats.

    La comparació ha de fer-se sobre mitjanes mòbils de 12 mesos. L'índex reconstruït
    neix d'un any base pla (els 12 primers mesos valen 100) i per tant no porta perfil
    estacional; el de l'INE sí que en porta, i n'hi ha molt (l'agost i el desembre es
    disparen). Contrastar-los mes a mes mesuraria l'estacionalitat de l'INE, no l'error
    de la reconstrucció. Amb la mitjana anual, l'estacionalitat cau als dos costats.
    """
    nivells = _formats("index")
    res = {}
    for c in [c for c in rel.columns if c in nivells.columns]:
        real = nivells[c].reindex(rel.index)
        base = real.iloc[:BASE_MESOS].mean()
        if pd.isna(base) or base == 0:
            continue
        rebasat = (real / base * 100).rolling(12).mean()
        dif = (rel[c].rolling(12).mean() - rebasat).iloc[BASE_MESOS:].abs().dropna()
        if len(dif):
            res[c] = float(dif.mean())
    return res


def escletxa_anual(anys, a="Comertia", b="Grans cadenes"):
    """Divergència acumulada encadenant els creixements de cada any mòbil.

    L'índex de `index_relatiu` només encadena a partir del mes 13, o sigui que amb 34
    mesos mesura poc més d'un any i mig de divergència. Encadenar els tres anys mòbils
    cobreix tot el que les dades descriuen, inclòs l'any que va del setembre de 2022 al
    d'abans que s'obri la finestra. És una aproximació —l'últim any és parcial— i s'ha
    de presentar com a tal, al costat de la xifra estricta.
    """
    fa, fb = 1.0, 1.0
    for tram in anys.values():
        if a in tram and b in tram and pd.notna(tram[a]) and pd.notna(tram[b]):
            fa *= 1 + tram[a] / 100
            fb *= 1 + tram[b] / 100
    return (fb / fa - 1) * 100


def _svg(rel, fi, amplada=760, alcada=330):
    series = [c for c in ["Comertia", "Grans cadenes", "Empreses unilocalitzades",
                          "Grans superfícies", "Catalunya, total"] if c in rel.columns]
    dades = rel[series].iloc[BASE_MESOS - 1:]
    lo = float(dades.min().min())
    hi = float(dades.max().max())
    marge = (hi - lo) * 0.12
    lo, hi = lo - marge, hi + marge
    PL, PR, PT, PB = 42, 176, 14, 30
    n = len(dades)

    def px(i):
        return PL + i * (amplada - PL - PR) / max(n - 1, 1)

    def py(v):
        return PT + (hi - v) * (alcada - PT - PB) / (hi - lo)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {amplada} {alcada}" '
         f'width="{amplada}" height="{alcada}" font-family="Helvetica, Arial, sans-serif">']
    p.append(f'<rect width="{amplada}" height="{alcada}" fill="#ffffff"/>')
    pas = 5 if (hi - lo) < 40 else 10
    marca = int(lo // pas * pas)
    while marca <= hi:
        if lo <= marca <= hi:
            y = py(marca)
            p.append(f'<line x1="{PL}" y1="{y:.1f}" x2="{amplada - PR}" y2="{y:.1f}" '
                     f'stroke="{"#333" if marca == 100 else "#ececec"}" stroke-width="1"/>')
            p.append(f'<text x="{PL - 7}" y="{y + 3.5:.1f}" font-size="10" fill="#6a6a6a" '
                     f'text-anchor="end">{marca}</text>')
        marca += pas
    for c in series:
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}"
                       for i, v in enumerate(dades[c]) if pd.notna(v))
        gruix = 2.4 if c in ("Comertia", "Grans cadenes") else 1.4
        p.append(f'<polyline fill="none" stroke="{COLORS[c]}" stroke-width="{gruix}" '
                 f'points="{pts}"/>')
        ult = dades[c].dropna()
        if len(ult):
            i = list(dades.index).index(ult.index[-1])
            p.append(f'<text x="{px(i) + 7:.1f}" y="{py(ult.iloc[-1]) + 3.5:.1f}" '
                     f'font-size="11" fill="{COLORS[c]}">{c} {ult.iloc[-1]:.0f}</text>')
    for i, d in enumerate(dades.index):
        if d.month in (1, 7) or i == n - 1:
            p.append(f'<text x="{px(i):.1f}" y="{alcada - 10}" font-size="10" '
                     f'fill="#6a6a6a" text-anchor="middle">'
                     f'{d.strftime("%m/%y")}</text>')
    p.append("</svg>")
    return "".join(p)


def main():
    taula, fi = carrega()
    rel = index_relatiu(taula)
    os.makedirs(OUT_DIR, exist_ok=True)

    ordre = ["Comertia", "Grans cadenes", "Empreses unilocalitzades", "Petites cadenes",
             "Grans superfícies", "Catalunya, total", "Espanya, total"]
    ordre = [c for c in ordre if c in taula.columns]

    print(f"Finestra: {taula.index.min():%Y-%m} → {fi:%Y-%m} "
          f"({len(taula)} mesos). Variacio interanual nominal.\n")

    print("=== 1. Creixement mitja del periode ===")
    for c, v in taula[ordre].mean().sort_values(ascending=False).items():
        marca = "  <<<" if c == "Comertia" else ""
        print(f"  {c:<28} {v:+.2f}%{marca}")

    print("\n=== 2. Per anys mobils (setembre-agost) ===")
    anys = {}
    for k in range(0, 4):
        ini = taula.index.min() + pd.DateOffset(months=12 * k)
        f = min(ini + pd.DateOffset(months=11), fi)
        if ini > fi:
            break
        tram = taula.loc[ini:f, ordre]
        etiqueta = f"{ini:%m/%y}-{f:%m/%y}" + (" (parcial)" if f < ini + pd.DateOffset(months=11) else "")
        anys[etiqueta] = tram.mean()
    print(pd.DataFrame(anys).round(1).to_string())

    print(f"\n=== 3. Posicio relativa acumulada (base 100 = any 1) a {fi:%m/%Y} ===")
    ultim = rel[ordre].iloc[-1].sort_values(ascending=False)
    for c, v in ultim.items():
        marca = "  <<<" if c == "Comertia" else ""
        print(f"  {c:<28} {v:6.1f}{marca}")
    if "Grans cadenes" in rel.columns:
        forat = rel["Grans cadenes"].iloc[-1] - rel["Comertia"].iloc[-1]
        print(f"\n  Escletxa mesurada DINS la finestra: {forat:.1f} punts "
              f"en {len(taula) - BASE_MESOS} mesos d'encadenament.")
        print(f"  Escletxa encadenant els {len(anys)} anys mobils: "
              f"{escletxa_anual(anys):.1f} punts (l'ultim any es parcial).")

    if "Grans cadenes" in taula.columns:
        dif = (taula["Comertia"] - taula["Grans cadenes"]).dropna()
        guanya = int((dif > 0).sum())
        print("\n=== 4. Mes a mes contra les grans cadenes ===")
        print(f"  Comertia creix mes en {guanya} de {len(dif)} mesos "
              f"({guanya / len(dif) * 100:.0f}%). Diferencial mitja {dif.mean():+.2f} punts.")
        print(f"  Anys mobils en que Comertia queda per sota: "
              f"{sum(1 for t in anys.values() if t['Comertia'] < t['Grans cadenes'])} "
              f"de {len(anys)}.")

    online = _icm("var_anual", "nacional", "real", ONLINE).loc[INICI:fi]
    total_real = _icm("var_anual", "nacional", "real").loc[INICI:fi]
    print("\n=== 5. Canal en linia (preus constants, Espanya) ===")
    print(f"  Venda per correspondencia o internet {online.mean():+.2f}% de mitjana, "
          f"contra {total_real.mean():+.2f}% del comerc al detall total.")

    dev = valida_reconstruccio(rel)
    print("\n=== 6. Validacio de l'index reconstruit contra els nivells de l'INE ===")
    for c, v in dev.items():
        print(f"  {c:<28} desviacio mitjana {v:.2f} punts")

    sortida = taula[ordre].copy()
    for c in ordre:
        sortida[f"{c} — index"] = rel[c]
    ruta_csv = os.path.join(OUT_DIR, "posicio_competitiva.csv")
    sortida.round(2).to_csv(ruta_csv, index_label="mes")
    ruta_svg = os.path.join(OUT_DIR, "posicio_competitiva.svg")
    with open(ruta_svg, "w", encoding="utf-8") as f:
        f.write(_svg(rel, fi))
    print(f"\nTaula: {os.path.abspath(ruta_csv)}")
    print(f"Grafic: {os.path.abspath(ruta_svg)}")


if __name__ == "__main__":
    main()

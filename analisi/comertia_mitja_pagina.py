"""
Genera la mitja pàgina de "context oficial" per a l'Indicador Comertia.

És el producte que es proposa a Comertia: cada mes, quan publiquen la seva nota, una
mitja pàgina signada per l'Observatori que posa la seva xifra al costat de la sèrie
oficial que li és comparable (INE, preus corrents), separa quina part del creixement és
preu i quina és volum, i situa Catalunya dins Espanya.

Regla de comparació: l'Indicador Comertia és facturació en euros, o sigui **preus
corrents**. La sèrie comparable de l'INE és la de preus corrents, no la de preus
constants. Tot el document es construeix sobre aquesta equivalència.

Sortida: HTML autocontingut a `data/raw/comertia/` (carpeta ignorada pel git: el
document porta xifres de Comertia i no ha d'anar al repo públic). S'imprimeix o
s'exporta a PDF des del navegador; ocupa mitja A4.

Ús:
    python analisi/comertia_mitja_pagina.py             # últim mes amb dades d'ICM
    python analisi/comertia_mitja_pagina.py 2026-07     # un mes concret

Avís: la sèrie de l'INE per comunitats és **bruta**, sense ajust d'estacionalitat ni de
calendari (veure TODO.md). Per això el document compara sempre variacions interanuals,
que és on l'efecte estacional queda neutralitzat, i ho diu explícitament al peu.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.fetchers import comertia  # noqa: E402

CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "icm.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "comertia")
BRANCA = "Comercio al por menor, excepto de vehículos de motor y motocicletas"

BRAND = "#003366"
INK = "#1a2b3a"
BODY = "#37485a"
GRAY = "#6a6a6a"
LINE = "#e4e9ee"
OCRE = "#b07d2b"

MESOS = ["gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost",
         "setembre", "octubre", "novembre", "desembre"]


def _fmt(x, decimals=1):
    """Format de taula: coma decimal, signe explícit i menys tipogràfic."""
    if x is None or pd.isna(x):
        return "n. d."
    return f"{x:+.{decimals}f}".replace(".", ",").replace("-", "−")


def _num(x, decimals=1):
    """Format de prosa: magnitud sense signe, que el signe ja el diu la frase."""
    if x is None or pd.isna(x):
        return "n. d."
    return f"{abs(x):.{decimals}f}".replace(".", ",")


def carrega(mes=None):
    icm = pd.read_csv(CACHE)
    icm = icm[(icm.indicador == "var_anual") & (icm.branca == BRANCA)]
    icm["data"] = pd.to_datetime(icm["data"])
    series = {
        f"{lbl}_{tipus}": (icm[(icm.ambit == ambit) & (icm.tipus == tipus)]
                           .set_index("data")["valor"].sort_index())
        for ambit, lbl in (("Cataluña", "cat"), ("nacional", "esp"))
        for tipus in ("nominal", "real")
    }
    com = comertia.load_serie()
    if com.empty:
        com = comertia.build_serie(verbose=False)
    com = (com.assign(data=pd.to_datetime(com["data"]))
              .set_index("data")["valor"].sort_index())

    data = pd.Timestamp(mes + "-01") if mes else max(s.index.max() for s in series.values())
    return data, com, series


def _svg_linies(com, cat_nom, data, mesos=13):
    """Sparkline de 13 mesos amb les dues sèries comparables. SVG inline, sense llibreries."""
    fi = data
    inici = fi - pd.DateOffset(months=mesos - 1)
    idx = pd.date_range(inici, fi, freq="MS")
    a = com.reindex(idx)
    b = cat_nom.reindex(idx)
    vals = pd.concat([a, b]).dropna()
    if vals.empty:
        return ""
    lo, hi = float(vals.min()), float(vals.max())
    marge = max((hi - lo) * 0.18, 0.6)
    lo, hi = lo - marge, hi + marge
    W, H, PL, PR, PT, PB = 470, 118, 6, 6, 10, 20

    def px(i):
        return PL + i * (W - PL - PR) / max(len(idx) - 1, 1)

    def py(v):
        return PT + (hi - v) * (H - PT - PB) / (hi - lo)

    def punts(s):
        return " ".join(f"{px(i):.1f},{py(v):.1f}"
                        for i, v in enumerate(s) if pd.notna(v))

    y0 = py(0) if lo < 0 < hi else None
    parts = [f'<svg viewBox="0 0 {W} {H}" width="100%" height="{H}" '
             f'role="img" aria-label="Evolucio interanual dels darrers {mesos} mesos">']
    if y0 is not None:
        parts.append(f'<line x1="{PL}" y1="{y0:.1f}" x2="{W - PR}" y2="{y0:.1f}" '
                     f'stroke="{LINE}" stroke-width="1"/>')
    parts.append(f'<polyline fill="none" stroke="{BRAND}" stroke-width="2" '
                 f'stroke-linejoin="round" points="{punts(b)}"/>')
    parts.append(f'<polyline fill="none" stroke="{OCRE}" stroke-width="2" '
                 f'stroke-dasharray="4 3" stroke-linejoin="round" points="{punts(a)}"/>')
    for s, color in ((b, BRAND), (a, OCRE)):
        ult = s.dropna()
        if len(ult):
            i = list(s.index).index(ult.index[-1])
            parts.append(f'<circle cx="{px(i):.1f}" cy="{py(ult.iloc[-1]):.1f}" r="3" '
                         f'fill="{color}"/>')
    for i, d in enumerate(idx):
        if i % 3 == 0 or i == len(idx) - 1:
            parts.append(f'<text x="{px(i):.1f}" y="{H - 6}" font-size="9" fill="{GRAY}" '
                         f'text-anchor="middle">{MESOS[d.month - 1][:3]}</text>')
    parts.append("</svg>")
    return "".join(parts)


def construeix(mes=None):
    data, com, s = carrega(mes)
    etiqueta = f"{MESOS[data.month - 1]} de {data.year}"
    c = com.get(data)
    cat_n, cat_r = s["cat_nominal"].get(data), s["cat_real"].get(data)
    esp_n, esp_r = s["esp_nominal"].get(data), s["esp_real"].get(data)
    preus = None if (pd.isna(cat_n) or pd.isna(cat_r)) else cat_n - cat_r
    pendent = pd.isna(cat_n)

    if pendent:
        titular = (f"L'INE encara no ha publicat les dades de {etiqueta}. "
                   "Document pendent de completar.")
    elif c is None or pd.isna(c):
        verb = "va facturar un" if cat_n >= 0 else "va facturar un"
        titular = (f"El comerç al detall català {verb} {_num(cat_n)}% "
                   f"{'més' if cat_n >= 0 else 'menys'} que un any abans el {etiqueta}, "
                   "a preus corrents.")
    else:
        diff = c - cat_n
        rel = "per damunt" if diff > 0 else "per sota"
        titular = (f"Els socis de Comertia van créixer un {_num(c)}% el {etiqueta}, "
                   f"{_num(diff)} punts {rel} del comerç al detall català, que va "
                   f"facturar un {_num(cat_n)}% "
                   f"{'més' if cat_n >= 0 else 'menys'} a preus corrents.")

    files = [
        ("Indicador Comertia", "Facturació dels socis, preus corrents", c),
        ("Comerç al detall, Catalunya", "INE, preus corrents — sèrie comparable", cat_n),
        ("Comerç al detall, Catalunya", "INE, preus constants — volum de vendes", cat_r),
        ("Comerç al detall, Espanya", "INE, preus corrents", esp_n),
        ("Comerç al detall, Espanya", "INE, preus constants", esp_r),
    ]
    cos_files = "".join(
        f'<tr><td class="s">{nom}<span>{det}</span></td>'
        f'<td class="v{"" if i else " destaca"}">{_fmt(v)}%</td></tr>'
        for i, (nom, det, v) in enumerate(files)
    )

    if preus is None:
        lectura = ("La lectura del mes es completarà quan l'INE publiqui les dades.")
    else:
        moviment = "va créixer" if cat_n >= 0 else "va caure"
        cua = (f"i {_num(cat_r)} punts, volum de vendes." if cat_r >= 0
               else f"i el volum de vendes hi resta {_num(cat_r)} punts.")
        lectura = (f"Del {_num(cat_n)}% que {moviment} la facturació del comerç al detall "
                   f"català, {_num(preus)} punts són preu {cua}")

    grafic = _svg_linies(com, s["cat_nominal"], data)
    html = f"""<!doctype html>
<html lang="ca"><head><meta charset="utf-8">
<title>Context oficial — Indicador Comertia, {etiqueta}</title>
<style>
  @page {{ size: A4; margin: 18mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: Georgia, "Times New Roman", serif; color: {BODY};
         margin: 0; padding: 24px; background: #fff; }}
  .full {{ max-width: 640px; }}
  .kicker {{ font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 10px;
             letter-spacing: .12em; text-transform: uppercase; color: {OCRE};
             margin: 0 0 6px; }}
  h1 {{ font-size: 19px; line-height: 1.3; color: {INK}; margin: 0 0 10px;
        font-weight: 600; }}
  .lectura {{ font-size: 13px; line-height: 1.5; margin: 0 0 14px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 12px; }}
  td {{ padding: 5px 0; border-bottom: 1px solid {LINE}; vertical-align: baseline; }}
  td.s {{ color: {INK}; }}
  td.s span {{ display: block; font-size: 10.5px; color: {GRAY};
               font-family: -apple-system, Helvetica, Arial, sans-serif; }}
  td.v {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums;
          font-size: 14px; color: {INK}; padding-left: 12px; }}
  td.v.destaca {{ color: {OCRE}; font-weight: 700; }}
  .llegenda {{ font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 10.5px;
               color: {GRAY}; margin: 2px 0 10px; }}
  .llegenda i {{ font-style: normal; display: inline-block; width: 14px; height: 2px;
                 vertical-align: middle; margin-right: 5px; }}
  .peu {{ font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 10px;
          line-height: 1.5; color: {GRAY}; border-top: 2px solid {BRAND};
          padding-top: 8px; margin-top: 4px; }}
  .peu strong {{ color: {BRAND}; }}
</style></head>
<body><div class="full">
  <p class="kicker">Context oficial · Indicador Comertia · {etiqueta}</p>
  <h1>{titular}</h1>
  <p class="lectura">{lectura}</p>
  <table>{cos_files}</table>
  {grafic}
  <p class="llegenda">
    <i style="background:{OCRE}"></i>Indicador Comertia &nbsp;&nbsp;
    <i style="background:{BRAND}"></i>Comerç al detall, Catalunya (INE, preus corrents)
    &nbsp;— darrers 13 mesos, variació interanual
  </p>
  <p class="peu">
    <strong>Observatori del Comerç · J3B3 Consulting</strong><br>
    Fonts: Indicador Comertia (nota de premsa mensual) i INE, Índices de Comercio al por
    Menor, comerç al detall excepte vehicles de motor. Totes les xifres són variacions
    respecte del mateix mes de l'any anterior. Les sèries de l'INE per comunitats no estan
    ajustades d'estacionalitat ni de calendari; la comparació interanual neutralitza
    l'efecte estacional. L'Indicador Comertia és facturació en euros, o sigui que la sèrie
    de l'INE comparable és la de preus corrents.
  </p>
</div></body></html>"""

    os.makedirs(OUT_DIR, exist_ok=True)
    ruta = os.path.join(OUT_DIR, f"context_oficial_{data:%Y_%m}.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)
    return ruta, data, pendent


if __name__ == "__main__":
    mes_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    ruta, data, pendent = construeix(mes_arg)
    print(f"Mitja pagina de {data:%Y-%m}: {os.path.abspath(ruta)}")
    if pendent:
        print("  ATENCIO: l'INE encara no ha publicat aquest mes. Document incomplet.")

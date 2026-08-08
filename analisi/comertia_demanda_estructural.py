"""
Eix 3 de la diagnosi per a Comertia: estructura de la demanda.

L'Indicador Comertia és cicle pur: diu com ha anat el mes. La pregunta que no es fa
ningú és si la part del consum de les llars que arriba a una botiga creix o s'encongeix,
i quines categories concretes es mouen. Un comerç pot créixer un 7% en una categoria que
fa una dècada que perd terreny dins la cistella de la llar; és créixer sobre gel prim.

El que en surt:

1. **Deu punts del consum de les llars han passat de béns a serveis en trenta anys.**
   A Espanya, els béns eren el 48,6% del consum el 1995 i són el 38,2% el 2025. Cada any
   que passa, una part més petita del que gasta una llar pot acabar en un taulell.

2. **Les categories que millor paguen són les que més s'encongeixen.** En volum per
   llar, entre el 2016 i el 2025, vestit i calçat cau un 12% i parament de la llar un
   13%, amb el consum total per llar pla. I vestit i calçat és, segons l'eix de marges,
   la branca que deixa més excedent de tot el comerç al detall (11,8 cèntims per euro).
   O sigui que el comerç familiar està sent expulsat de la seva categoria més rendible
   per la conducta de les llars, no per cap competidor.

3. L'espai que ho absorbeix tot és **l'habitatge i els subministraments**, que passen del
   31,0% al 35,0% del consum de la llar en nou anys. Quatre punts que surten de la resta.

Fonts:
· INE, Enquesta de Pressupostos Familiars, taula 75003 — despesa mitjana per llar per
  grup COICOP. ATENCIÓ: la sèrie ja ve **a preus constants** (el nom de sèrie diu
  "Precios constantes"), o sigui que els percentatges d'aquest eix són pes dins el
  consum real i les variacions ja són de volum. No s'ha de tornar a deflactar: seria
  deflactar dues vegades, error en què aquest script va caure a la primera versió.
· Eurostat, comptes nacionals — repartiment entre béns i serveis del consum de les
  llars, Espanya i eurozona, des del 1995.

Sortides a `data/raw/comertia/` (ignorat pel git):
  · demanda_estructural.csv
  · demanda_estructural.svg   — variació del volum per llar, per categoria

Ús: python analisi/comertia_demanda_estructural.py
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DIR = os.path.dirname(__file__)
CACHE = os.path.join(DIR, "..", "data", "cache")
OUT_DIR = os.path.join(DIR, "..", "data", "raw", "comertia")
TOTAL = "Total despesa"

# Etiquetes curtes i en català. Les de l'INE vénen en castellà i són quilomètriques.
NOMS = {
    "Alimentos y bebidas no alcohólicas": "Alimentació",
    "Bebidas alcohólicas, tabaco y estupefacientes": "Begudes alcohòliques i tabac",
    "Vestido y calzado": "Vestit i calçat",
    "Vivienda, agua, electricidad, gas y otros combustibles": "Habitatge i subministraments",
    "Muebles, artículos del hogar y artículos para el mantenimiento corriente del hogar":
        "Parament de la llar",
    "Sanidad": "Sanitat",
    "Transporte": "Transport",
    "Información y comunicaciones": "Informació i comunicacions",
    "Actividades recreativas, deporte y cultura": "Oci, esport i cultura",
    "Servicios de educación": "Educació",
    "Restaurantes y servicios de alojamiento": "Restauració i allotjament",
    "Cuidado personal, protección social, y bienes y servicios diversos":
        "Cura personal i altres",
}
# Categories que es venen en una botiga i que toquen les branques de Comertia.
TAULELL = {"Vestit i calçat", "Parament de la llar", "Oci, esport i cultura",
           "Alimentació", "Informació i comunicacions", "Cura personal i altres"}
# Categoria de marge més alt segons l'eix 2 (CNAE 477).
CLAU = "Vestit i calçat"


def epf():
    e = pd.read_csv(os.path.join(CACHE, "subsectors_epf.csv"))
    total = e[e.nom == TOTAL].set_index("any")["despesa_per_llar"]
    d = e[e.nom != TOTAL].copy()
    d["categoria"] = d["nom"].map(NOMS).fillna(d["nom"])
    volum = d.pivot_table(index="categoria", columns="any", values="despesa_per_llar")
    pes = volum.div(total, axis=1) * 100
    return volum, pes, total


def bens_serveis():
    c = pd.read_csv(os.path.join(CACHE, "estructura_consum.csv"))
    return {k: g.set_index("any")[["bens_share", "serveis_share"]]
            for k, g in c.groupby("pais_codi")}


def _svg(t, a0, a1, amplada=700, alt_fila=25):
    """Barres horitzontals de la variació del volum per llar. Una fila per categoria."""
    t = t.sort_values("volum_pct")
    n = len(t)
    PT, PB, PL = 30, 34, 210
    alcada = PT + PB + n * alt_fila
    lo = min(float(t["volum_pct"].min()), 0.0)
    hi = max(float(t["volum_pct"].max()), 0.0)
    span = max(hi - lo, 1e-9)
    ample_util = amplada - PL - 58

    def px(v):
        return PL + (v - lo) * ample_util / span

    zero = px(0)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {amplada} {alcada}" '
         f'width="{amplada}" height="{alcada}" '
         f'font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{amplada}" height="{alcada}" fill="#ffffff"/>']
    for i, (cat, f) in enumerate(t.iterrows()):
        y = PT + i * alt_fila
        v = f["volum_pct"]
        x = px(v)
        if cat == CLAU:
            color = "#b07d2b"
        elif cat in TAULELL:
            color = "#003366"
        else:
            color = "#c8d0d8"
        x0, x1 = (zero, x) if v >= 0 else (x, zero)
        p.append(f'<rect x="{x0:.1f}" y="{y + 4:.1f}" width="{max(x1 - x0, 0.5):.1f}" '
                 f'height="{alt_fila - 11}" fill="{color}"/>')
        pes_txt = "700" if cat in TAULELL else "400"
        p.append(f'<text x="{PL - 12}" y="{y + alt_fila / 2 + 2:.1f}" font-size="11.5" '
                 f'fill="#37485a" text-anchor="end" font-weight="{pes_txt}">{cat}</text>')
        etx = x1 + 6 if v >= 0 else x0 - 6
        anc = "start" if v >= 0 else "end"
        p.append(f'<text x="{etx:.1f}" y="{y + alt_fila / 2 + 2:.1f}" font-size="11.5" '
                 f'fill="{color if cat in TAULELL else "#6a6a6a"}" text-anchor="{anc}" '
                 f'font-weight="{pes_txt}">{v:+.0f}%</text>')
    p.append(f'<line x1="{zero:.1f}" y1="{PT}" x2="{zero:.1f}" y2="{PT + n * alt_fila}" '
             f'stroke="#37485a" stroke-width="1"/>')
    p.append(f'<text x="{PL - 12}" y="{PT - 12}" font-size="11" fill="#1a2b3a" '
             f'text-anchor="end" font-weight="700">Volum consumit per llar</text>')
    p.append(f'<text x="{zero + 6:.1f}" y="{PT - 12}" font-size="11" fill="#6a6a6a">'
             f'variació {a0}–{a1}, a preus constants</text>')
    p.append(f'<text x="{zero + 6:.1f}" y="{alcada - 12}" font-size="10.5" fill="#9aa6b2" '
             f'text-anchor="start">En blau, el que es ven en una botiga</text>')
    p.append("</svg>")
    return "".join(p)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    volum, pes, total = epf()
    a0, a1 = int(volum.columns.min()), int(volum.columns.max())

    t = pd.DataFrame({
        "pes_inici": pes[a0], "pes_final": pes[a1],
        "volum_pct": (volum[a1] / volum[a0] - 1) * 100,
    })
    t["canvi_pes"] = t["pes_final"] - t["pes_inici"]

    print(f"Enquesta de Pressupostos Familiars, {a0}–{a1}, preus constants.")
    print(f"Consum total per llar: {total[a0]:,.0f} € → {total[a1]:,.0f} €, "
          f"{(total[a1] / total[a0] - 1) * 100:+.1f}% en volum.\n")

    print("=== 1. Volum consumit per llar i pes dins el consum (%) ===")
    mostra = t.sort_values("volum_pct")[["pes_inici", "pes_final", "canvi_pes",
                                         "volum_pct"]]
    print(mostra.round(2).to_string())

    print("\n=== 2. Nomes el que es ven en una botiga ===")
    botiga = t[t.index.isin(TAULELL)].sort_values("volum_pct")
    print(botiga[["pes_inici", "pes_final", "canvi_pes", "volum_pct"]].round(2).to_string())
    print(f"  Pes conjunt: {botiga['pes_inici'].sum():.1f}% → "
          f"{botiga['pes_final'].sum():.1f}% del consum de la llar "
          f"({botiga['canvi_pes'].sum():+.1f} punts).")

    bs = bens_serveis()
    print("\n=== 3. Bens contra serveis al consum de les llars ===")
    for codi, etiqueta in (("ES", "Espanya"), ("EA20", "Eurozona")):
        if codi not in bs:
            continue
        s = bs[codi]
        p0, p1 = int(s.index.min()), int(s.index.max())
        print(f"  {etiqueta}: bens {s.loc[p0, 'bens_share']:.1f}% ({p0}) → "
              f"{s.loc[p1, 'bens_share']:.1f}% ({p1}), "
              f"{s.loc[p1, 'bens_share'] - s.loc[p0, 'bens_share']:+.1f} punts.")

    print("\n=== 4. Lectura per a Comertia ===")
    clau = t.loc[CLAU]
    print(f"  {CLAU}: volum per llar {clau['volum_pct']:+.1f}%, pes "
          f"{clau['pes_inici']:.2f}% → {clau['pes_final']:.2f}%. "
          f"Es la branca de marge mes alt del comerc al detall (11,8% el 2024, eix 2).")
    hab = t.loc["Habitatge i subministraments"]
    print(f"  Habitatge i subministraments: {hab['canvi_pes']:+.1f} punts de pes. "
          f"D'aqui surt el que perden les altres.")
    guanyen = t[t["canvi_pes"] > 0].sort_values("canvi_pes", ascending=False)
    print(f"  Nomes {len(guanyen)} de {len(t)} categories guanyen pes: "
          f"{', '.join(guanyen.index)}.")

    t.round(2).to_csv(os.path.join(OUT_DIR, "demanda_estructural.csv"),
                      index_label="categoria")
    ruta_svg = os.path.join(OUT_DIR, "demanda_estructural.svg")
    with open(ruta_svg, "w", encoding="utf-8") as f:
        f.write(_svg(t, a0, a1))
    print(f"\nTaula: {os.path.abspath(os.path.join(OUT_DIR, 'demanda_estructural.csv'))}")
    print(f"Grafic: {os.path.abspath(ruta_svg)}")


if __name__ == "__main__":
    main()

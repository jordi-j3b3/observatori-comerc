"""
Eix 2 de la diagnosi per a Comertia: conversió del creixement en marge.

L'Indicador Comertia mesura facturació. La pregunta que ni ell ni cap comparació amb
l'INE responen és si aquells euros de més arriben a baix. L'Enquesta Estructural
d'Empreses de l'INE dona, per branca del comerç al detall, l'excedent brut d'explotació
sobre la xifra de negoci: quant de cada euro venut queda abans d'amortitzacions.

El que en surt no és el que semblava. La hipòtesi de partida era que el creixement
nominal se l'estava empassant l'estructura de costos, i **és falsa**: al conjunt del
comerç al detall espanyol, l'excedent brut ha passat de 6,8 a 7,4 cèntims per euro venut
entre el 2018 i el 2024, i el repartiment de l'euro amb prou feines s'ha mogut.

El que sí que hi ha, i val molt més com a diagnòstic, és que **la conversió és
radicalment desigual per branca**: de 4,4 cèntims per euro a les gasolineres a 11,8 a
moda i altres articles, gairebé el triple, amb un ordre que no es mou en set anys. O
sigui que el que determina el que guanyes no és quant creixes sinó **per on** creixes.
És una pregunta de mescla de branques, no de control de costos, i és la que cap
indicador de facturació pot respondre.

Per a Comertia: les dues branques que declaren com a motor del creixement al seu
Indicador de juliol de 2026 —oci i cultura, equipament de la llar— deixen 7,5 cèntims
per euro; la branca de moda i altres articles en deixa 11,8. Un 36% menys per cada euro
venut. No sabem la mescla real dels seus socis, i aquest és precisament un dels motius
pels quals val la pena asseure's amb ells: amb els seus pesos per branca, aquest mapa
es converteix en el seu compte d'explotació.

Fonts:
· INE, EEE Comercio (Encuesta Anual de Comercio), taula 76818 — excedent brut sobre
  xifra de negoci per branca CNAE 47 a tres dígits, anual des de 2018.
· INE, EEE Comercio, taula 36199 — compte d'explotació agregat del comerç al detall,
  d'on surt el destí de cada euro venut.
· INE, ICM — índex de vendes per branca, per creuar creixement amb marge.

Sortides a `data/raw/comertia/` (ignorat pel git):
  · conversio_marge.csv   — taula per branca
  · conversio_marge.svg   — creixement de vendes contra marge, per branca

Ús: python analisi/comertia_conversio_marge.py

Nota de mètode: la xifra de negoci nominal no ve com a columna a `productivitat.csv`,
que la porta a preus constants. Es recupera com a `cogs / (1 − marge_brut)`, identitat
que es comprova al mateix script contra la columna `marge_brut` publicada. Els
percentatges del compte d'explotació no sumen exactament 100: la diferència són altres
ingressos i despeses d'explotació, i es mostra explícitament en lloc d'amagar-la.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DIR = os.path.dirname(__file__)
CACHE = os.path.join(DIR, "..", "data", "cache")
OUT_DIR = os.path.join(DIR, "..", "data", "raw", "comertia")

# Correspondencia entre les branques de l'ICM i els codis CNAE de la taula de marges.
ICM_A_CNAE = {
    "Comercio al por menor en establecimientos no especializados": "471",
    "Comercio al por menor de productos alimenticios, bebidas y tabaco "
    "en establecimientos especializados": "472",
    "Comercio al por menor de combustible para la automoción "
    "en establecimientos especializados": "473",
    "Comercio al por menor de equipos para las tecnologías de la información "
    "y las comunicaciones en establecimientos especializados": "474",
    "Comercio al por menor de otros artículos de uso doméstico "
    "en establecimientos especializados": "475",
    "Comercio al por menor de artículos culturales y recreativos "
    "en establecimientos especializados": "476",
    "Comercio al por menor de otros artículos en establecimientos especializados": "477",
    "Comercio al por menor no realizado ni en establecimientos, ni en puestos "
    "de venta ni en mercadillos": "479",
}
# Branques que Comertia declara com a motor del creixement (Indicador, juliol 2026).
FOCUS = {"475", "476"}
# Branca de marge mes alt del comerc al detall, on hi ha bona part de les marques de
# moda i complements. NO sabem quin pes te dins Comertia: la comparacio ensenya el mapa
# de marges, no la mescla dels seus socis, i aixo s'ha de dir al lliurable.
REFERENCIA = "477"

# Etiquetes curtes per al grafic. Les de l'INE no caben al marge i, a mes, aixi
# comparteixen vocabulari amb el grafic de l'eix de demanda.
CURT = {
    "471": "Súper i hiper",
    "472": "Alimentació especialitzada",
    "473": "Gasolineres",
    "474": "Equips TIC",
    "475": "Equipament de la llar",
    "476": "Oci i cultura",
    "477": "Moda, calçat i altres",
    "479": "Internet",
}


def compte_explotacio():
    """Destí de cada euro venut, en termes nominals, del compte d'explotació agregat."""
    p = pd.read_csv(os.path.join(CACHE, "productivitat.csv")).sort_values("any")
    xn = p["cogs"] / (1 - p["marge_brut"])          # xifra de negoci nominal
    control = (1 - p["cogs"] / xn) - p["marge_brut"]  # ha de ser zero
    out = pd.DataFrame({
        "any": p["any"].values,
        "Cost de la mercaderia": (p["cogs"] / xn * 100).values,
        "Serveis exteriors": (p["serveis_exteriors"] / xn * 100).values,
        "Despeses de personal": (p["gastos_personal"] / xn * 100).values,
        "Excedent brut": (p["excedent_brut"] / xn * 100).values,
    }).set_index("any")
    out["Resta (altres ingressos i despeses)"] = 100 - out.sum(axis=1)
    return out, float(control.abs().max())


def marges():
    m = pd.read_csv(os.path.join(CACHE, "marges_branca_ine.csv"))
    m["cnae"] = m["cnae"].astype(str)
    return m.pivot_table(index=["cnae", "branca"], columns="any",
                         values="marge_vendes_pct")


def vendes_per_branca(anys):
    """Índex de vendes de l'ICM per branca, mitjana anual, Espanya, PREUS CONSTANTS.

    L'ICM només publica el detall de branca a tres dígits a preus constants; en preus
    corrents només hi ha les agrupacions grans, que no lliguen amb els codis CNAE de la
    taula de marges. O sigui que el creixement de vendes d'aquest eix és en volum, i
    l'excedent que se'n deriva també. Es diu al lliurable.
    """
    d = pd.read_csv(os.path.join(CACHE, "icm.csv"))
    d = d[(d.indicador == "index") & (d.ambit == "nacional") & (d.tipus == "real")]
    d = d[d.branca.isin(ICM_A_CNAE)]
    d["cnae"] = d["branca"].map(ICM_A_CNAE)
    d = d[d["any"].isin(anys)]
    return d.pivot_table(index="cnae", columns="any", values="valor")


def primer_any_complet(m):
    """Primer any amb els dotze mesos publicats per a totes les branques mapejades."""
    d = pd.read_csv(os.path.join(CACHE, "icm.csv"))
    d = d[(d.indicador == "index") & (d.ambit == "nacional") & (d.tipus == "real")
          & (d.branca.isin(ICM_A_CNAE))]
    d["cnae"] = d["branca"].map(ICM_A_CNAE)
    comptes = d.groupby(["any", "cnae"]).size().unstack()
    complets = comptes[(comptes == 12).all(axis=1)]
    anys_marge = set(m.columns)
    return min(a for a in complets.index if a in anys_marge)


def compara(m, a0, a1):
    """Creixement de vendes i d'excedent per branca entre dos anys."""
    v = vendes_per_branca([a0, a1])
    files = []
    for (cnae, branca), fila in m.iterrows():
        if cnae not in v.index or pd.isna(v.loc[cnae, a0]) or pd.isna(v.loc[cnae, a1]):
            continue
        files.append({
            "cnae": cnae, "branca": branca,
            "marge_inici": fila[a0], "marge_final": fila[a1],
            "vendes_pct": (v.loc[cnae, a1] / v.loc[cnae, a0] - 1) * 100,
            "excedent_pct": ((v.loc[cnae, a1] * fila[a1])
                             / (v.loc[cnae, a0] * fila[a0]) - 1) * 100,
        })
    t = pd.DataFrame(files).set_index("cnae")
    t["bretxa"] = t["excedent_pct"] - t["vendes_pct"]
    return t


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    euro, control = compte_explotacio()
    m = marges()
    anys = sorted(c for c in m.columns)
    a0, a1 = anys[0], anys[-1]

    print(f"Marges per branca disponibles: {a0}–{a1}. "
          f"Control de la identitat de la xifra de negoci: {control:.1e}\n")

    print("=== 1. On va cada euro venut al comerc al detall (%, Espanya) ===")
    print(euro.round(1).to_string())
    var = euro.loc[a1] - euro.loc[a0]
    print(f"\n  Variacio {a0}→{a1}, en cents per euro:")
    for c, v in var.sort_values().items():
        print(f"    {c:<38} {v:+.1f}")

    print("\n=== 2. Excedent brut sobre vendes, per branca (%) ===")
    print(m.round(1).to_string())

    # La sèrie de branca a tres dígits de l'ICM arrenca el 2021 per a gairebé totes
    # (només 472 i 473 vénen del 2016), o sigui que el 2018 no és una base possible.
    # El 2021 encara porta el rebot de la pandèmia, així que la finestra de titular és
    # 2022→2024 i la del 2021 queda com a comprovació.
    base = primer_any_complet(m)
    t = compara(m, base + 1, a1)
    t_alt = compara(m, base, a1)

    print(f"\n=== 3. Vendes en volum contra excedent, {base + 1}→{a1} (%) ===")
    print("  El creixement de l'excedent es el de les vendes corregit pel canvi de marge.")
    mostra = t[["branca", "marge_inici", "marge_final", "vendes_pct",
                "excedent_pct", "bretxa"]].sort_values("vendes_pct", ascending=False)
    print(mostra.round(1).to_string())
    print(f"\n  Comprovacio amb base {base} (any de rebot, llegir amb reserva):")
    print(t_alt[["branca", "vendes_pct", "excedent_pct", "bretxa"]]
          .sort_values("vendes_pct", ascending=False).round(1).to_string())
    a0 = base + 1

    print("\n=== 4. Lectura per a Comertia ===")
    focus = t[t.index.isin(FOCUS)]
    trad = t.loc[REFERENCIA] if REFERENCIA in t.index else None
    if len(focus) and trad is not None:
        print(f"  Branques on declaren el creixement mes fort: "
              f"{', '.join(focus['branca'])}.")
        print(f"    Marge {a1}: {', '.join(f'{x:.1f}%' for x in focus['marge_final'])}.")
        print(f"  Branca de marge mes alt ({trad['branca']}): "
              f"{trad['marge_final']:.1f}%.")
        dif = trad["marge_final"] - focus["marge_final"].mean()
        print(f"    Diferencia: {dif:.1f} punts de marge, o sigui que cada euro venut "
              f"a les branques que estiren deixa un {dif / trad['marge_final'] * 100:.0f}% "
              f"menys d'excedent que un euro venut a la de marge mes alt.")
        print("    No coneixem la mescla per branca dels socis de Comertia: aixo es el "
              "mapa de marges del sector, no el seu compte d'explotacio.")
    pitjor = t.sort_values("bretxa").head(1)
    millor = t.sort_values("bretxa").tail(1)
    print(f"  Pitjor conversio del periode: {pitjor['branca'].iloc[0]} "
          f"({pitjor['bretxa'].iloc[0]:+.1f} punts). "
          f"Millor: {millor['branca'].iloc[0]} ({millor['bretxa'].iloc[0]:+.1f}).")

    ruta_csv = os.path.join(OUT_DIR, "conversio_marge.csv")
    t.round(2).to_csv(ruta_csv)
    ruta_svg = os.path.join(OUT_DIR, "conversio_marge.svg")
    with open(ruta_svg, "w", encoding="utf-8") as f:
        f.write(_svg(t, m, a1))
    euro.round(2).to_csv(os.path.join(OUT_DIR, "conversio_marge_euro.csv"),
                         index_label="any")
    print(f"\nTaula: {os.path.abspath(ruta_csv)}")
    print(f"Grafic: {os.path.abspath(ruta_svg)}")


def _svg(t, m, a1, amplada=700, alt_fila=25):
    """Barres horitzontals: excedent brut sobre vendes per branca.

    Mateixa forma que el gràfic de l'eix de demanda, perquè els dos es llegeixin com a
    peces d'una mateixa sèrie. El senyal fi de cada barra marca el valor del primer any
    disponible: ensenya que l'ordre de les branques no s'ha mogut en set anys sense
    haver de dibuixar un segon gràfic.
    """
    anys = sorted(m.columns)
    a_ini = anys[0]
    marges_ini = {cnae: m.loc[(cnae, br), a_ini] for cnae, br in m.index}

    d = t.sort_values("marge_final")
    n = len(d)
    PT, PB, PL = 32, 34, 210
    alcada = PT + PB + n * alt_fila
    hi = float(d["marge_final"].max()) * 1.14
    ample_util = amplada - PL - 58

    def px(v):
        return PL + v * ample_util / hi

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {amplada} {alcada}" '
         f'width="{amplada}" height="{alcada}" '
         f'font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{amplada}" height="{alcada}" fill="#ffffff"/>']
    for i, (cnae, f) in enumerate(d.iterrows()):
        y = PT + i * alt_fila
        v = float(f["marge_final"])
        if cnae == REFERENCIA:
            color, gruix = "#b07d2b", "700"
        elif cnae in FOCUS:
            color, gruix = "#003366", "700"
        else:
            color, gruix = "#c8d0d8", "400"
        p.append(f'<rect x="{PL:.1f}" y="{y + 4:.1f}" width="{px(v) - PL:.1f}" '
                 f'height="{alt_fila - 11}" fill="{color}"/>')
        ini = marges_ini.get(cnae)
        if ini is not None and pd.notna(ini):
            xi = px(float(ini))
            p.append(f'<line x1="{xi:.1f}" y1="{y + 2:.1f}" x2="{xi:.1f}" '
                     f'y2="{y + alt_fila - 5:.1f}" stroke="#37485a" stroke-width="1.2"/>')
        etiqueta = CURT.get(cnae, f["branca"])
        p.append(f'<text x="{PL - 12}" y="{y + alt_fila / 2 + 2:.1f}" font-size="11.5" '
                 f'fill="#37485a" text-anchor="end" font-weight="{gruix}">{etiqueta}</text>')
        p.append(f'<text x="{px(v) + 6:.1f}" y="{y + alt_fila / 2 + 2:.1f}" '
                 f'font-size="11.5" fill="{color if gruix == "700" else "#6a6a6a"}" '
                 f'font-weight="{gruix}">{v:.1f}</text>')
    p.append(f'<line x1="{PL:.1f}" y1="{PT}" x2="{PL:.1f}" y2="{PT + n * alt_fila}" '
             f'stroke="#37485a" stroke-width="1"/>')
    p.append(f'<text x="{PL - 12}" y="{PT - 13}" font-size="11" fill="#1a2b3a" '
             f'text-anchor="end" font-weight="700">Cèntims per euro venut</text>')
    p.append(f'<text x="{PL + 6}" y="{PT - 13}" font-size="11" fill="#6a6a6a">'
             f'excedent brut sobre vendes per branca, {a1}</text>')
    p.append(f'<text x="{PL - 12}" y="{alcada - 12}" font-size="10.5" fill="#9aa6b2" '
             f'text-anchor="end">El senyal fi marca el {a_ini}</text>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    main()

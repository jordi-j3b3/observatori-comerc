"""Pàgina: Líders del comerç (CNAE 47) — mostra de grans empreses (comptes del Registre Mercantil)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout, PALETTE, BRAND, BRAND_DEEP, RED, GREEN)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"
_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "lideres_empreses.csv")


@st.cache_data(ttl=3600)
def load_emp(sig):
    return pd.read_csv(_PATH) if os.path.exists(_PATH) else pd.DataFrame()


_sig = ((os.path.getsize(_PATH), int(os.path.getmtime(_PATH))) if os.path.exists(_PATH) else (0, 0))
d = load_emp(_sig)

st.title("Líders del comerç" if _ca else "Líderes del comercio")
intro(
    ("Una <strong>mostra de grans empreses del comerç al detall</strong> (CNAE 47) a partir dels "
     "<strong>comptes anuals dipositats al Registre Mercantil</strong> (2020-2024). Analitzem la "
     "<strong>mida</strong>, la <strong>rendibilitat</strong> (marges, retorn sobre actiu), la "
     "<strong>productivitat i el cost laboral</strong>, i el <strong>creixement</strong>. "
     "<em>És una mostra il·lustrativa dels grans formats, no el rànquing exhaustiu del sector.</em>"
     if _ca else
     "Una <strong>muestra de grandes empresas del comercio minorista</strong> (CNAE 47) a partir de las "
     "<strong>cuentas anuales depositadas en el Registro Mercantil</strong> (2020-2024). Analizamos el "
     "<strong>tamaño</strong>, la <strong>rentabilidad</strong> (márgenes, retorno sobre activo), la "
     "<strong>productividad y el coste laboral</strong>, y el <strong>crecimiento</strong>. "
     "<em>Es una muestra ilustrativa de los grandes formatos, no el ranking exhaustivo del sector.</em>")
)

if d.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

r = d.dropna(subset=["ing_2024"]).sort_values("ing_2024", ascending=False).reset_index(drop=True)
cmap = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted(d["subsector"].unique()))}


def ranked_bar(data, col, xlab, fmt="pct", n=10, height=560, color=None):
    dd = data.dropna(subset=[col]).sort_values(col)
    sel = pd.concat([dd.head(n), dd.tail(n)]).drop_duplicates("nombre")
    if color is None:
        color = [GREEN if v >= 0 else RED for v in sel[col]]
    fig = go.Figure(go.Bar(
        y=sel["nombre"], x=sel[col], orientation="h", marker_color=color,
        text=[(f"{v:.1f}%".replace(".", ",") if fmt == "pct" else f"{fnum(v)}") for v in sel[col]],
        textposition="outside", textfont=dict(size=10)))
    fig.add_vline(x=0, line_color="rgba(0,0,0,0.25)")
    apply_layout(fig, xaxis_title=xlab, height=height, margin=dict(l=220, r=70, t=20, b=40))
    return fig


k1, k2, k3, k4 = st.columns(4)
k1.metric(("Empreses a la mostra" if _ca else "Empresas en la muestra"), f"{d['nombre'].nunique()}")
k2.metric(("Facturació agregada" if _ca else "Facturación agregada") + " (2024)", f"{fnum(r['ing_2024'].sum()/1e6, 1)} Md€")
k3.metric(("Ocupació agregada" if _ca else "Empleo agregado"), fnum(d["empleados"].sum()))
k4.metric(("Marge EBITDA mitjà" if _ca else "Margen EBITDA medio"), fpct(r["marge_ebitda"].median(), 1, sign=False),
          help=("mediana de la mostra" if _ca else "mediana de la muestra"))

tab_mida, tab_rend, tab_prod, tab_creix = st.tabs([
    ("Mida" if _ca else "Tamaño"),
    ("Rendibilitat" if _ca else "Rentabilidad"),
    ("Productivitat i cost laboral" if _ca else "Productividad y coste laboral"),
    ("Creixement 2020-2024" if _ca else "Crecimiento 2020-2024"),
])

# ── TAB 1: MIDA ──
with tab_mida:
    st.markdown(("**Les 20 majors de la mostra per facturació** (2024)" if _ca
                 else "**Las 20 mayores de la muestra por facturación** (2024)"))
    top = r.head(20).iloc[::-1]
    fig = go.Figure(go.Bar(
        y=top["nombre"], x=top["ing_2024"]/1000, orientation="h",
        marker_color=[cmap[s] for s in top["subsector"]],
        text=[f"{fnum(v/1000)} M€" for v in top["ing_2024"]], textposition="outside", textfont=dict(size=10),
        customdata=top["subsector"], hovertemplate="<b>%{y}</b><br>%{x:,.0f} M€<br>%{customdata}<extra></extra>"))
    apply_layout(fig, xaxis_title="Facturació (M€)" if _ca else "Facturación (M€)",
                 height=620, margin=dict(l=230, r=90, t=20, b=40))
    st.plotly_chart(fig, use_container_width=True)
    source("Comptes anuals dipositats al Registre Mercantil" if _ca else "Cuentas anuales depositadas en el Registro Mercantil")
    insight(
        ("L'alimentació ocupa la franja alta de la mostra; la moda i la llar hi apareixen a la franja mitjana. "
         "Entre la primera i la darrera empresa la mida varia en més de dos ordres de magnitud: dins el mateix "
         "CNAE 47 hi conviuen hipermercats de milers de milions i cadenes especialitzades de pocs centenars de milions."
         if _ca else
         "La alimentación ocupa la franja alta de la muestra; moda y hogar aparecen en la franja media. Entre la "
         "primera y la última empresa el tamaño varía en más de dos órdenes de magnitud: dentro del mismo CNAE 47 "
         "conviven hipermercados de miles de millones y cadenas especializadas de pocos centenares de millones.")
    )

# ── TAB 2: RENDIBILITAT ──
with tab_rend:
    st.markdown(("**Mida vs rendibilitat** — cada bombolla és una empresa (mida = empleats)" if _ca
                 else "**Tamaño vs rentabilidad** — cada burbuja es una empresa (tamaño = empleados)"))
    sc = r.dropna(subset=["marge_ebitda", "empleados"])
    maxe = sc["empleados"].max()
    fig = go.Figure()
    for s in sorted(sc["subsector"].unique()):
        ss = sc[sc["subsector"] == s]
        fig.add_trace(go.Scatter(
            x=ss["ing_2024"]/1000, y=ss["marge_ebitda"], mode="markers", name=s,
            marker=dict(size=ss["empleados"], sizemode="area", sizeref=2.*maxe/(45.**2), sizemin=5,
                        color=cmap[s], line=dict(width=0.5, color="white")),
            customdata=ss[["nombre", "empleados"]],
            hovertemplate="<b>%{customdata[0]}</b><br>%{x:,.0f} M€ · marge %{y:.1f}%<br>%{customdata[1]:,.0f} empleats<extra></extra>"))
    apply_layout(fig, xaxis_title="Facturació 2024 (M€, escala log)" if _ca else "Facturación 2024 (M€, escala log)",
                 yaxis_title="Marge EBITDA (%)" if _ca else "Margen EBITDA (%)", height=460)
    fig.update_xaxes(type="log")
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(0,0,0,0.25)")
    st.plotly_chart(fig, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Marge EBITDA per empresa** (2024 · 10 majors i 10 menors)" if _ca
                 else "**Margen EBITDA por empresa** (2024 · 10 mayores y 10 menores)"))
    st.plotly_chart(ranked_bar(r, "marge_ebitda", "Marge EBITDA (%)" if _ca else "Margen EBITDA (%)"),
                    use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Retorn sobre l'actiu (ROA)** (2024 · resultat / actiu total)" if _ca
                 else "**Retorno sobre el activo (ROA)** (2024 · resultado / activo total)"))
    st.plotly_chart(ranked_bar(r, "roa", "ROA (%)", height=520), use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    insight(
        ("La rendibilitat dibuixa dos mons. Els grans operadors d'<strong>alimentació</strong> tenen marges EBITDA "
         "ajustats (entorn del 5-8 %) compensats per un volum enorme; la <strong>moda i la cosmètica</strong> "
         "treballen amb marges molt superiors (Mango, Stradivarius, Tous o Christian Dior superen el 12 % i fins al "
         "30 %), gràcies a la marca i al valor afegit del producte. Alguns formats (mobles, grans magatzems, calçat) "
         "operen amb marges nuls o negatius. El <strong>ROA</strong> ho amplifica: les empreses de moda i luxe, amb "
         "menys actiu immobilitzat, obtenen retorns sobre l'actiu molt elevats, mentre que la distribució alimentària, "
         "intensiva en actiu, en treu menys per cada euro invertit."
         if _ca else
         "La rentabilidad dibuja dos mundos. Los grandes operadores de <strong>alimentación</strong> tienen márgenes "
         "EBITDA ajustados (en torno al 5-8 %) compensados por un volumen enorme; la <strong>moda y la cosmética</strong> "
         "trabajan con márgenes muy superiores (Mango, Stradivarius, Tous o Christian Dior superan el 12 % y hasta el "
         "30 %), gracias a la marca y al valor añadido del producto. Algunos formatos (muebles, grandes almacenes, "
         "calzado) operan con márgenes nulos o negativos. El <strong>ROA</strong> lo amplifica: las empresas de moda y "
         "lujo, con menos activo inmovilizado, obtienen retornos sobre el activo muy elevados, mientras que la "
         "distribución alimentaria, intensiva en activo, saca menos por cada euro invertido.")
    )

# ── TAB 3: PRODUCTIVITAT I COST LABORAL ──
with tab_prod:
    st.markdown(("**Facturació per empleat** (2024 · 10 majors i 10 menors)" if _ca
                 else "**Facturación por empleado** (2024 · 10 mayores y 10 menores)"))
    rp = r.copy(); rp["prod_k"] = rp["productivitat"]/1000
    st.plotly_chart(ranked_bar(rp, "prod_k", "Facturació per empleat (k€)" if _ca else "Facturación por empleado (k€)",
                               fmt="num", color=BRAND_DEEP), use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Cost laboral mitjà per empleat** (2024 · despeses de personal / plantilla)" if _ca
                 else "**Coste laboral medio por empleado** (2024 · gastos de personal / plantilla)"))
    rc = r.copy(); rc["cost_k"] = rc["cost_empleat"]/1000
    st.plotly_chart(ranked_bar(rc, "cost_k", "Cost per empleat (k€/any)" if _ca else "Coste por empleado (k€/año)",
                               fmt="num", color=BRAND), use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    _med_prod = r["productivitat"].median()/1000
    insight(
        (f"La <strong>productivitat</strong> (facturació per empleat) separa clarament l'autoservei de l'atenció "
         f"personal: els supermercats i les grans superfícies superen els 200-300 k€ per empleat, mentre que els "
         f"formats de moda, òptica o regal es mouen molt per sota (mediana de la mostra: {fnum(_med_prod)} k€). El "
         f"<strong>cost laboral per empleat</strong> matisa la lectura: una facturació per empleat alta no implica "
         f"sous alts —depèn de l'autoservei i del mix de jornades—, però algunes cadenes (com Mercadona) combinen alta "
         f"productivitat amb un cost per empleat per sobre de la mediana."
         if _ca else
         f"La <strong>productividad</strong> (facturación por empleado) separa claramente el autoservicio de la "
         f"atención personal: los supermercados y las grandes superficies superan los 200-300 k€ por empleado, mientras "
         f"que los formatos de moda, óptica o regalo se mueven muy por debajo (mediana de la muestra: {fnum(_med_prod)} k€). "
         f"El <strong>coste laboral por empleado</strong> matiza la lectura: una facturación por empleado alta no implica "
         f"salarios altos —depende del autoservicio y del mix de jornadas—, pero algunas cadenas (como Mercadona) "
         f"combinan alta productividad con un coste por empleado por encima de la mediana.")
    )

# ── TAB 4: CREIXEMENT ──
with tab_creix:
    if _ca:
        st.markdown(
            "Creixement de la facturació amb el **CAGR** (taxa anual composta) 2020-2024, entre les empreses amb "
            "comptes per als dos anys. **N'excloem les que presenten una ruptura en la sèrie d'ingressos** —salts "
            "incompatibles amb creixement orgànic, típics de reorganitzacions societàries (fusions, canvis de "
            "perímetre)— perquè el seu CAGR no seria comparable."
        )
    else:
        st.markdown(
            "Crecimiento de la facturación con el **CAGR** (tasa anual compuesta) 2020-2024, entre las empresas con "
            "cuentas para ambos años. **Excluimos las que presentan una ruptura en la serie de ingresos** —saltos "
            "incompatibles con crecimiento orgánico, típicos de reorganizaciones societarias (fusiones, cambios de "
            "perímetro)— porque su CAGR no sería comparable."
        )
    st.plotly_chart(ranked_bar(d, "cagr", "CAGR 2020-2024 (%)", n=8, height=560), use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    _brk = d[d["break_flag"]]["nombre"].tolist()
    insight(
        ("Entre les empreses amb creixement orgànic comparable, els <strong>guanyadors</strong> són cadenes de moda, "
         "cosmètica i nous formats de descompte en plena expansió; els <strong>perdedors</strong> arrosseguen "
         "reestructuracions o formats sota pressió. "
         "<br><br><strong>Un aclariment important.</strong> "
         f"Empreses com <strong>MediaMarkt</strong> mostren un salt enorme de facturació (de pocs milions a més de "
         f"2.000 M€), però <strong>no és creixement real</strong>: respon a una <strong>reorganització societària</strong> "
         f"(consolidació de l'entitat operativa cap al 2023). Per això l'excloem d'aquesta anàlisi. Això resol l'aparent "
         f"contradicció amb la pàgina de Subsectors, on l'electrònica i els electrodomèstics figuren entre els que menys "
         f"creixen: el sector creix poc en conjunt, i el repunt comptable d'un sol operador és un artefacte, no una "
         f"tendència. Empreses excloses per ruptura de sèrie: {', '.join(_brk)}."
         if _ca else
         "Entre las empresas con crecimiento orgánico comparable, los <strong>ganadores</strong> son cadenas de moda, "
         "cosmética y nuevos formatos de descuento en plena expansión; los <strong>perdedores</strong> arrastran "
         "reestructuraciones o formatos bajo presión. "
         "<br><br><strong>Una aclaración importante.</strong> "
         f"Empresas como <strong>MediaMarkt</strong> muestran un salto enorme de facturación (de pocos millones a más de "
         f"2.000 M€), pero <strong>no es crecimiento real</strong>: responde a una <strong>reorganización societaria</strong> "
         f"(consolidación de la entidad operativa hacia 2023). Por eso la excluimos de este análisis. Esto resuelve la "
         f"aparente contradicción con la página de Subsectores, donde la electrónica y los electrodomésticos figuran "
         f"entre los que menos crecen: el sector crece poco en conjunto, y el repunte contable de un solo operador es un "
         f"artefacto, no una tendencia. Empresas excluidas por ruptura de serie: {', '.join(_brk)}.")
    )

page_meta("Comptes anuals dipositats al Registre Mercantil (2020-2024) · mostra de grans empreses CNAE 47" if _ca
          else "Cuentas anuales depositadas en el Registro Mercantil (2020-2024) · muestra de grandes empresas CNAE 47",
          st.session_state.lang)

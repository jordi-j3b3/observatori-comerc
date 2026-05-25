"""Pàgina: Líders del comerç (CNAE 47) — mostra de grans empreses (comptes del Registre Mercantil).
Es publiquen NOMÉS indicadors i ràtios (no xifres absolutes de facturació ni plantilla)."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout, PALETTE, BRAND, RED, GREEN)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"
_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "lideres_empreses.csv")


@st.cache_data(ttl=3600)
def _load(sig):
    return pd.read_csv(_PATH) if os.path.exists(_PATH) else pd.DataFrame()


_sig = ((os.path.getsize(_PATH), int(os.path.getmtime(_PATH))) if os.path.exists(_PATH) else (0, 0))
d = _load(_sig)

st.title("Líders del comerç" if _ca else "Líderes del comercio")
intro(
    ("Una <strong>mostra de grans empreses del comerç al detall</strong> (CNAE 47) a partir dels "
     "<strong>comptes anuals dipositats al Registre Mercantil</strong> (2020-2024). Per respectar la "
     "confidencialitat de les dades, no en mostrem les xifres absolutes: només <strong>indicadors i ràtios</strong> "
     "(marges, rendibilitat, productivitat, creixement), a escala de subsector i d'empresa."
     if _ca else
     "Una <strong>muestra de grandes empresas del comercio minorista</strong> (CNAE 47) a partir de las "
     "<strong>cuentas anuales depositadas en el Registro Mercantil</strong> (2020-2024). Para respetar la "
     "confidencialidad de los datos, no mostramos las cifras absolutas: solo <strong>indicadores y ratios</strong> "
     "(márgenes, rentabilidad, productividad, crecimiento), a escala de subsector y de empresa.")
)

if d.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

cmap = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted(d["subsector"].unique()))}
sub = (d.groupby("subsector").agg(
    n=("nombre", "count"),
    marge_ebitda=("marge_ebitda", "median"), roa=("roa", "median"),
    productivitat=("productivitat", "median"), ratio_personal=("ratio_personal", "median")).reset_index())
s3 = sub[sub["n"] >= 3].copy()

k1, k2, k3, k4 = st.columns(4)
k1.metric(("Empreses a la mostra" if _ca else "Empresas en la muestra"), f"{d['nombre'].nunique()}")
k2.metric(("Subsectors analitzats" if _ca else "Subsectores analizados"), f"{len(s3)}",
          help=("amb 3+ empreses a la mostra" if _ca else "con 3+ empresas en la muestra"))
k3.metric(("Marge EBITDA (mediana)" if _ca else "Margen EBITDA (mediana)"), fpct(d["marge_ebitda"].median(), 1))
k4.metric(("Productivitat (mediana)" if _ca else "Productividad (mediana)"), f"{fnum(d['productivitat'].median()/1000)} k€",
          help=("facturació per empleat" if _ca else "facturación por empleado"))

tab_rend, tab_creix, tab_emp = st.tabs([
    ("Rendibilitat per subsector" if _ca else "Rentabilidad por subsector"),
    ("Creixement 2020-2024" if _ca else "Crecimiento 2020-2024"),
    ("Indicadors per empresa" if _ca else "Indicadores por empresa"),
])

# ── TAB 1: RENDIBILITAT PER SUBSECTOR ──
with tab_rend:
    st.markdown(("**Mapa de posicionament dels subsectors** — productivitat vs marge (mediana, 3+ empreses)"
                 if _ca else
                 "**Mapa de posicionamiento de los subsectores** — productividad vs margen (mediana, 3+ empresas)"))
    fig = go.Figure()
    for _, row in s3.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["productivitat"]/1000], y=[row["marge_ebitda"]], mode="markers+text",
            text=[row["subsector"]], textposition="top center", textfont=dict(size=11),
            marker=dict(size=22, color=cmap.get(row["subsector"], BRAND), line=dict(width=1, color="white")),
            hovertemplate=f"<b>{row['subsector']}</b><br>%{{x:,.0f}} k€/empleat<br>marge EBITDA %{{y:.1f}}%<extra></extra>"))
    apply_layout(fig, xaxis_title="Facturació per empleat (k€)" if _ca else "Facturación por empleado (k€)",
                 yaxis_title="Marge EBITDA (mediana, %)" if _ca else "Margen EBITDA (mediana, %)",
                 height=460, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Comparativa per subsector** (medianes, 2024)" if _ca else "**Comparativa por subsector** (medianas, 2024)"))
    tbl = s3.sort_values("marge_ebitda", ascending=False)
    show = pd.DataFrame({
        "Subsector": tbl["subsector"],
        ("Empreses" if _ca else "Empresas"): tbl["n"].astype(int),
        ("Marge EBITDA" if _ca else "Margen EBITDA"): tbl["marge_ebitda"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
        "ROA": tbl["roa"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
        ("Fact./empleat" if _ca else "Fact./empleado"): tbl["productivitat"].map(lambda v: f"{fnum(v/1000)} k€"),
        ("Cost personal/vendes" if _ca else "Coste personal/ventas"): tbl["ratio_personal"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
    })
    st.dataframe(show, use_container_width=True, hide_index=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    insight(
        ("No hi ha un únic model dins la mostra. L'<strong>electrònica i informàtica</strong> tenen la productivitat "
         "més alta (ticket elevat, plantilla reduïda i pes de la venda online) però el <strong>marge EBITDA més prim</strong> "
         "(mediana 2,6 %), senyal d'una competència de preu intensa. La <strong>cosmètica</strong> i la <strong>moda</strong> "
         "registren els marges mitjans més alts del grup. L'<strong>alimentació</strong> i els <strong>esports</strong>, amb "
         "més atenció de botiga, tenen productivitat i marges més continguts i el cost de personal sobre vendes més elevat."
         if _ca else
         "No hay un único modelo dentro de la muestra. La <strong>electrónica e informática</strong> tienen la productividad "
         "más alta (ticket elevado, plantilla reducida y peso de la venta online) pero el <strong>margen EBITDA más fino</strong> "
         "(mediana 2,6 %), señal de una competencia de precio intensa. La <strong>cosmética</strong> y la <strong>moda</strong> "
         "registran los márgenes medios más altos del grupo. La <strong>alimentación</strong> y los <strong>deportes</strong>, con "
         "más atención de tienda, tienen productividad y márgenes más contenidos y el coste de personal sobre ventas más elevado.")
    )

# ── TAB 2: CREIXEMENT ──
with tab_creix:
    st.markdown(("Creixement de la facturació amb el **CAGR** 2020-2024 (taxa anual composta). **N'excloem les empreses "
                 "amb ruptura en la sèrie d'ingressos** —salts incompatibles amb creixement orgànic, típics de "
                 "reorganitzacions societàries— perquè el seu CAGR no seria comparable."
                 if _ca else
                 "Crecimiento de la facturación con el **CAGR** 2020-2024 (tasa anual compuesta). **Excluimos las empresas "
                 "con ruptura en la serie de ingresos** —saltos incompatibles con crecimiento orgánico, típicos de "
                 "reorganizaciones societarias— porque su CAGR no sería comparable."))
    g = d.dropna(subset=["cagr"]).sort_values("cagr")
    sel = pd.concat([g.head(8), g.tail(8)]).drop_duplicates("nombre")
    figg = go.Figure(go.Bar(
        y=sel["nombre"], x=sel["cagr"], orientation="h",
        marker_color=[GREEN if v >= 0 else RED for v in sel["cagr"]],
        text=[fpct(v, 1) for v in sel["cagr"]], textposition="outside", textfont=dict(size=10)))
    figg.add_vline(x=0, line_color="rgba(0,0,0,0.3)")
    apply_layout(figg, xaxis_title="CAGR 2020-2024 (%)" if _ca else "CAGR 2020-2024 (%)",
                 height=560, margin=dict(l=230, r=70, t=20, b=40))
    st.plotly_chart(figg, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    _brk = d[d["break_flag"]]["nombre"].tolist()
    insight(
        ("Entre les empreses amb creixement orgànic comparable, els <strong>guanyadors</strong> són cadenes de moda, "
         "cosmètica i nous formats de descompte en expansió; els <strong>perdedors</strong>, formats sota pressió o en "
         "reestructuració. <br><br><strong>Aclariment.</strong> Operadors com <strong>MediaMarkt</strong> mostren un salt "
         "enorme de facturació que <strong>no és creixement real</strong>, sinó una reorganització societària "
         "(consolidació de l'entitat operativa cap al 2023); per això els excloem. Això resol l'aparent contradicció amb "
         "la pàgina de Subsectors, on l'electrònica figura entre els que menys creixen: el subsector creix poc, i el "
         f"repunt comptable d'un operador és un artefacte, no una tendència. Excloses per ruptura: {', '.join(_brk)}."
         if _ca else
         "Entre las empresas con crecimiento orgánico comparable, los <strong>ganadores</strong> son cadenas de moda, "
         "cosmética y nuevos formatos de descuento en expansión; los <strong>perdedores</strong>, formatos bajo presión o "
         "en reestructuración. <br><br><strong>Aclaración.</strong> Operadores como <strong>MediaMarkt</strong> muestran un "
         "salto enorme de facturación que <strong>no es crecimiento real</strong>, sino una reorganización societaria "
         "(consolidación de la entidad operativa hacia 2023); por eso los excluimos. Esto resuelve la aparente "
         "contradicción con la página de Subsectores, donde la electrónica figura entre los que menos crecen: el "
         f"subsector crece poco, y el repunte contable de un operador es un artefacto, no una tendencia. Excluidas por ruptura: {', '.join(_brk)}.")
    )

# ── TAB 3: INDICADORS PER EMPRESA (taula interactiva de ràtios) ──
with tab_emp:
    st.markdown(("Indicadors de cada empresa de la mostra (clica les capçaleres per ordenar). Es mostren **només "
                 "ràtios** —no xifres absolutes de facturació ni plantilla."
                 if _ca else
                 "Indicadores de cada empresa de la muestra (clica las cabeceras para ordenar). Se muestran **solo "
                 "ratios** —no cifras absolutas de facturación ni plantilla."))
    tbl = d.copy()
    tbl["prod_keur"] = tbl["productivitat"]/1000
    tbl = tbl[["nombre", "subsector", "marge_ebitda", "roa", "prod_keur", "ratio_personal", "cagr"]]
    tbl = tbl.sort_values("marge_ebitda", ascending=False)
    tbl.columns = ["Empresa", "Subsector",
                   "Marge EBITDA %" if _ca else "Margen EBITDA %", "ROA %",
                   "Fact./empleat (k€)" if _ca else "Fact./empleado (k€)",
                   "Cost pers./vendes %" if _ca else "Coste pers./ventas %",
                   "CAGR 20-24 %"]
    st.dataframe(
        tbl, use_container_width=True, hide_index=True, height=560,
        column_config={
            ("Marge EBITDA %" if _ca else "Margen EBITDA %"): st.column_config.NumberColumn(format="%.1f"),
            "ROA %": st.column_config.NumberColumn(format="%.1f"),
            ("Fact./empleat (k€)" if _ca else "Fact./empleado (k€)"): st.column_config.NumberColumn(format="%.0f"),
            ("Cost pers./vendes %" if _ca else "Coste pers./ventas %"): st.column_config.NumberColumn(format="%.1f"),
            "CAGR 20-24 %": st.column_config.NumberColumn(format="%.1f"),
        })
    source("Comptes anuals dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas anuales depositadas en el Registro Mercantil. Cálculo propio")
    st.caption(("CAGR buit = empresa amb ruptura de sèrie (reorganització) o sense comptes per als dos anys."
                if _ca else
                "CAGR vacío = empresa con ruptura de serie (reorganización) o sin cuentas para ambos años."))

page_meta("Comptes anuals dipositats al Registre Mercantil (2020-2024) · mostra de grans empreses CNAE 47 · només indicadors i ràtios" if _ca
          else "Cuentas anuales depositadas en el Registro Mercantil (2020-2024) · muestra de grandes empresas CNAE 47 · solo indicadores y ratios",
          st.session_state.lang)

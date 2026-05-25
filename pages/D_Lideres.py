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
_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
_RANK = os.path.join(_DIR, "lideres_ranking.csv")
_SUB = os.path.join(_DIR, "lideres_subsector.csv")


@st.cache_data(ttl=3600)
def _load(path, sig):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def _sig(p):
    return (os.path.getsize(p), int(os.path.getmtime(p))) if os.path.exists(p) else (0, 0)


rank = _load(_RANK, _sig(_RANK))
sub = _load(_SUB, _sig(_SUB))

st.title("Líders del comerç" if _ca else "Líderes del comercio")
intro(
    ("Una <strong>mostra de grans empreses del comerç al detall</strong> (CNAE 47) a partir dels "
     "<strong>comptes anuals dipositats al Registre Mercantil</strong> (2020-2024). Com que és una mostra "
     "il·lustrativa dels grans formats —no el rànquing exhaustiu del sector—, l'anàlisi de rendibilitat i "
     "productivitat es fa <strong>per subsectors</strong>, on els contrastos sí que són significatius."
     if _ca else
     "Una <strong>muestra de grandes empresas del comercio minorista</strong> (CNAE 47) a partir de las "
     "<strong>cuentas anuales depositadas en el Registro Mercantil</strong> (2020-2024). Como es una muestra "
     "ilustrativa de los grandes formatos —no el ranking exhaustivo del sector—, el análisis de rentabilidad y "
     "productividad se hace <strong>por subsectores</strong>, donde los contrastes sí son significativos.")
)

if rank.empty or sub.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

r = rank.dropna(subset=["ing_2024"]).sort_values("ing_2024", ascending=False).reset_index(drop=True)
cmap = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted(sub["subsector"].unique()))}
s3 = sub[sub["n"] >= 3].copy()  # subsectors robustos (3+ empreses) per als contrastos

k1, k2, k3, k4 = st.columns(4)
k1.metric(("Empreses a la mostra" if _ca else "Empresas en la muestra"), f"{rank['nombre'].nunique()}")
k2.metric(("Facturació agregada" if _ca else "Facturación agregada") + " (2024)", f"{fnum(sub['ing_total'].sum()/1e6, 1)} Md€")
k3.metric(("Ocupació agregada" if _ca else "Empleo agregado"), fnum(sub["empleats_total"].sum()))
k4.metric(("Subsectors analitzats" if _ca else "Subsectores analizados"), f"{len(s3)}",
          help=("amb 3+ empreses a la mostra" if _ca else "con 3+ empresas en la muestra"))

tab_mida, tab_rend, tab_creix = st.tabs([
    ("Mida" if _ca else "Tamaño"),
    ("Rendibilitat per subsector" if _ca else "Rentabilidad por subsector"),
    ("Creixement 2020-2024" if _ca else "Crecimiento 2020-2024"),
])

# ── TAB 1: MIDA (rànquing per empresa) ──
with tab_mida:
    st.markdown(("**Les 20 majors de la mostra per facturació** (2024)" if _ca
                 else "**Las 20 mayores de la muestra por facturación** (2024)"))
    top = r.head(20).iloc[::-1]
    fig = go.Figure(go.Bar(
        y=top["nombre"], x=top["ing_2024"]/1000, orientation="h",
        marker_color=[cmap.get(s, BRAND) for s in top["subsector"]],
        text=[f"{fnum(v/1000)} M€" for v in top["ing_2024"]], textposition="outside", textfont=dict(size=10),
        customdata=top["subsector"], hovertemplate="<b>%{y}</b><br>%{x:,.0f} M€<br>%{customdata}<extra></extra>"))
    apply_layout(fig, xaxis_title="Facturació (M€)" if _ca else "Facturación (M€)",
                 height=620, margin=dict(l=230, r=90, t=20, b=40))
    st.plotly_chart(fig, use_container_width=True)
    source("Comptes anuals dipositats al Registre Mercantil" if _ca else "Cuentas anuales depositadas en el Registro Mercantil")
    insight(
        ("L'alimentació ocupa la franja alta de la mostra; la moda i la llar hi apareixen a la franja mitjana. "
         "Entre la primera i la darrera empresa la mida varia en més de dos ordres de magnitud."
         if _ca else
         "La alimentación ocupa la franja alta de la muestra; moda y hogar aparecen en la franja media. Entre la "
         "primera y la última empresa el tamaño varía en más de dos órdenes de magnitud.")
    )

# ── TAB 2: RENDIBILITAT PER SUBSECTOR (mapa de posicionament + taula) ──
with tab_rend:
    st.markdown(("**Mapa de posicionament dels subsectors** — productivitat vs marge (mediana, subsectors amb 3+ empreses)"
                 if _ca else
                 "**Mapa de posicionamiento de los subsectores** — productividad vs margen (mediana, subsectores con 3+ empresas)"))
    fig = go.Figure()
    for _, row in s3.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["productivitat"]/1000], y=[row["marge_ebitda"]], mode="markers+text",
            name=row["subsector"], text=[row["subsector"]], textposition="top center",
            textfont=dict(size=11),
            marker=dict(size=22, color=cmap.get(row["subsector"], BRAND), line=dict(width=1, color="white")),
            hovertemplate=f"<b>{row['subsector']}</b><br>%{{x:,.0f}} k€/empleat<br>marge EBITDA %{{y:.1f}}%<extra></extra>"))
    apply_layout(fig, xaxis_title="Facturació per empleat (k€)" if _ca else "Facturación por empleado (k€)",
                 yaxis_title="Marge EBITDA (mediana, %)" if _ca else "Margen EBITDA (mediana, %)",
                 height=460, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Comparativa per subsector** (medianes, 2024)" if _ca else "**Comparativa por subsector** (medianas, 2024)"))
    tbl = s3.sort_values("marge_ebitda", ascending=False).copy()
    show = pd.DataFrame({
        ("Subsector"): tbl["subsector"],
        ("Empreses" if _ca else "Empresas"): tbl["n"].astype(int),
        ("Marge EBITDA" if _ca else "Margen EBITDA"): tbl["marge_ebitda"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
        ("ROA"): tbl["roa"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
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
         "més atenció de botiga, tenen productivitat i marges més continguts i el cost de personal sobre vendes més elevat. "
         "Cada format combina productivitat, marge i intensitat de personal de manera diferent."
         if _ca else
         "No hay un único modelo dentro de la muestra. La <strong>electrónica e informática</strong> tienen la productividad "
         "más alta (ticket elevado, plantilla reducida y peso de la venta online) pero el <strong>margen EBITDA más fino</strong> "
         "(mediana 2,6 %), señal de una competencia de precio intensa. La <strong>cosmética</strong> y la <strong>moda</strong> "
         "registran los márgenes medios más altos del grupo. La <strong>alimentación</strong> y los <strong>deportes</strong>, con "
         "más atención de tienda, tienen productividad y márgenes más contenidos y el coste de personal sobre ventas más elevado. "
         "Cada formato combina productividad, margen e intensidad de personal de manera distinta.")
    )

# ── TAB 3: CREIXEMENT (per empresa, ruptures excloses) ──
with tab_creix:
    if _ca:
        st.markdown(
            "Creixement de la facturació amb el **CAGR** (taxa anual composta) 2020-2024, entre les empreses amb "
            "comptes per als dos anys. **N'excloem les que presenten una ruptura en la sèrie d'ingressos** —salts "
            "incompatibles amb creixement orgànic, típics de reorganitzacions societàries— perquè el seu CAGR no seria "
            "comparable."
        )
    else:
        st.markdown(
            "Crecimiento de la facturación con el **CAGR** (tasa anual compuesta) 2020-2024, entre las empresas con "
            "cuentas para ambos años. **Excluimos las que presentan una ruptura en la serie de ingresos** —saltos "
            "incompatibles con crecimiento orgánico, típicos de reorganizaciones societarias— porque su CAGR no sería "
            "comparable."
        )
    g = rank.dropna(subset=["cagr"]).copy()
    g = g[(g["ing_2020"] > 0)].sort_values("cagr")
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
    _brk = rank[rank["break_flag"]]["nombre"].tolist()
    insight(
        ("Entre les empreses amb creixement orgànic comparable, els <strong>guanyadors</strong> són cadenes de moda, "
         "cosmètica i nous formats de descompte en expansió; els <strong>perdedors</strong>, formats sota pressió o en "
         "reestructuració. "
         "<br><br><strong>Aclariment.</strong> Operadors com <strong>MediaMarkt</strong> mostren un salt enorme de "
         "facturació (de pocs milions a més de 2.000 M€) que <strong>no és creixement real</strong>, sinó una "
         "reorganització societària (consolidació de l'entitat operativa cap al 2023); per això els excloem. Això resol "
         "l'aparent contradicció amb la pàgina de Subsectors, on l'electrònica figura entre els que menys creixen: el "
         "subsector creix poc, i el repunt comptable d'un operador és un artefacte, no una tendència. "
         f"Excloses per ruptura: {', '.join(_brk)}."
         if _ca else
         "Entre las empresas con crecimiento orgánico comparable, los <strong>ganadores</strong> son cadenas de moda, "
         "cosmética y nuevos formatos de descuento en expansión; los <strong>perdedores</strong>, formatos bajo presión "
         "o en reestructuración. "
         "<br><br><strong>Aclaración.</strong> Operadores como <strong>MediaMarkt</strong> muestran un salto enorme de "
         "facturación (de pocos millones a más de 2.000 M€) que <strong>no es crecimiento real</strong>, sino una "
         "reorganización societaria (consolidación de la entidad operativa hacia 2023); por eso los excluimos. Esto "
         "resuelve la aparente contradicción con la página de Subsectores, donde la electrónica figura entre los que "
         "menos crecen: el subsector crece poco, y el repunte contable de un operador es un artefacto, no una tendencia. "
         f"Excluidas por ruptura: {', '.join(_brk)}.")
    )

page_meta("Comptes anuals dipositats al Registre Mercantil (2020-2024) · mostra de grans empreses CNAE 47" if _ca
          else "Cuentas anuales depositadas en el Registro Mercantil (2020-2024) · muestra de grandes empresas CNAE 47",
          st.session_state.lang)

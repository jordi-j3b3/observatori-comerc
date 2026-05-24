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
def load_csv(path, sig):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def _sig(p):
    return (os.path.getsize(p), int(os.path.getmtime(p))) if os.path.exists(p) else (0, 0)


rank = load_csv(_RANK, _sig(_RANK))
sub = load_csv(_SUB, _sig(_SUB))

st.title("Líders del comerç" if _ca else "Líderes del comercio")
intro(
    ("Una <strong>mostra de grans empreses del comerç al detall</strong> (CNAE 47), seleccionades d'entre "
     "les més grans del sector, a partir dels <strong>comptes anuals dipositats al Registre Mercantil</strong> "
     "(2020-2024). Permet comparar la <strong>mida</strong>, els <strong>marges</strong>, la <strong>productivitat</strong> "
     "i el <strong>cost de personal</strong> dels operadors de referència. "
     "<em>No és el rànquing exhaustiu del sector ni un estudi de concentració de mercat: és una mostra "
     "il·lustrativa dels grans formats.</em>"
     if _ca else
     "Una <strong>muestra de grandes empresas del comercio minorista</strong> (CNAE 47), seleccionadas de entre "
     "las mayores del sector, a partir de las <strong>cuentas anuales depositadas en el Registro Mercantil</strong> "
     "(2020-2024). Permite comparar el <strong>tamaño</strong>, los <strong>márgenes</strong>, la <strong>productividad</strong> "
     "y el <strong>coste de personal</strong> de los operadores de referencia. "
     "<em>No es el ranking exhaustivo del sector ni un estudio de concentración de mercado: es una muestra "
     "ilustrativa de los grandes formatos.</em>")
)

if rank.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

r = rank.dropna(subset=["ing_2024"]).sort_values("ing_2024", ascending=False).reset_index(drop=True)
cmap = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted(rank["subsector"].unique()))}

# ─── KPIs ───
k1, k2, k3, k4 = st.columns(4)
k1.metric(("Empreses a la mostra" if _ca else "Empresas en la muestra"), f"{rank['nombre'].nunique()}")
k2.metric(("Facturació agregada" if _ca else "Facturación agregada") + " (2024)",
          f"{fnum(r['ing_2024'].sum()/1e6, 1)} Md€")
if not sub.empty:
    k3.metric(("Ocupació agregada" if _ca else "Empleo agregado"), fnum(sub["empleats_total"].sum()))
k4.metric(("Facturació mediana" if _ca else "Facturación mediana") + " (2024)",
          f"{fnum(r['ing_2024'].median()/1000)} M€")

tab_rank, tab_marg, tab_pers, tab_creix = st.tabs([
    ("Rànquing de la mostra" if _ca else "Ranking de la muestra"),
    ("Marges i productivitat" if _ca else "Márgenes y productividad"),
    ("Cost de personal" if _ca else "Coste de personal"),
    ("Creixement 2020-2024" if _ca else "Crecimiento 2020-2024"),
])

# ════════════════════════════════════════════════════════════
# TAB 1 — RÀNQUING
# ════════════════════════════════════════════════════════════
with tab_rank:
    st.markdown(("**Les 20 majors de la mostra per facturació** (2024)" if _ca
                 else "**Las 20 mayores de la muestra por facturación** (2024)"))
    top = r.head(20).iloc[::-1]
    figr = go.Figure()
    figr.add_trace(go.Bar(
        y=top["nombre"].str.title(), x=top["ing_2024"]/1000, orientation="h",
        marker_color=[cmap[s] for s in top["subsector"]],
        text=[f"{fnum(v/1000)} M€" for v in top["ing_2024"]],
        textposition="outside", textfont=dict(size=10),
        customdata=top["subsector"],
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} M€<br>%{customdata}<extra></extra>"))
    apply_layout(figr, xaxis_title="Facturació (M€)" if _ca else "Facturación (M€)",
                 height=620, margin=dict(l=230, r=90, t=20, b=40))
    st.plotly_chart(figr, use_container_width=True)
    source("Comptes anuals dipositats al Registre Mercantil" if _ca
           else "Cuentas anuales depositadas en el Registro Mercantil")
    insight(
        ("La franja alta de la mostra l'ocupen els grans operadors d'<strong>alimentació</strong> "
         "(supermercats i cadenes de distribució), seguits a distància pels líders de <strong>moda</strong> i de "
         "<strong>llar i bricolatge</strong>. La mida entre el primer i el darrer de la mostra varia en més de dos "
         "ordres de magnitud, fet que reflecteix la coexistència de formats molt diferents dins el mateix CNAE 47."
         if _ca else
         "La franja alta de la muestra la ocupan los grandes operadores de <strong>alimentación</strong> "
         "(supermercados y cadenas de distribución), seguidos a distancia por los líderes de <strong>moda</strong> y de "
         "<strong>hogar y bricolaje</strong>. El tamaño entre el primero y el último de la muestra varía en más de dos "
         "órdenes de magnitud, lo que refleja la coexistencia de formatos muy distintos dentro del mismo CNAE 47.")
    )

# ════════════════════════════════════════════════════════════
# TAB 2 — MARGES I PRODUCTIVITAT (mediana per subsector, n>=2)
# ════════════════════════════════════════════════════════════
with tab_marg:
    s2 = sub[sub["n"] >= 2].copy()
    st.markdown(("**Marge EBITDA mitjà per subsector** (2024 · subsectors amb 2+ empreses)" if _ca
                 else "**Margen EBITDA medio por subsector** (2024 · subsectores con 2+ empresas)"))
    g = s2.dropna(subset=["marge_ebitda"]).sort_values("marge_ebitda")
    figm = go.Figure()
    figm.add_trace(go.Bar(y=g["subsector"], x=g["marge_ebitda"], orientation="h", marker_color=BRAND,
                          text=[f"{v:.1f}%".replace(".", ",") for v in g["marge_ebitda"]],
                          textposition="outside", textfont=dict(size=10)))
    apply_layout(figm, xaxis_title="Marge EBITDA (mediana, %)" if _ca else "Margen EBITDA (mediana, %)",
                 height=420, margin=dict(l=190, r=70, t=20, b=40))
    st.plotly_chart(figm, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Productivitat: facturació per empleat** (2024 · subsectors amb 2+ empreses)" if _ca
                 else "**Productividad: facturación por empleado** (2024 · subsectores con 2+ empresas)"))
    p = s2.dropna(subset=["productivitat"]).sort_values("productivitat")
    figp = go.Figure()
    figp.add_trace(go.Bar(y=p["subsector"], x=p["productivitat"]/1000, orientation="h", marker_color=BRAND_DEEP,
                          text=[f"{fnum(v/1000)} k€" for v in p["productivitat"]],
                          textposition="outside", textfont=dict(size=10)))
    apply_layout(figp, xaxis_title="Facturació per empleat (k€)" if _ca else "Facturación por empleado (k€)",
                 height=420, margin=dict(l=190, r=80, t=20, b=40))
    st.plotly_chart(figp, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    insight(
        ("Els subsectors de <strong>moda i cosmètica</strong> presenten marges EBITDA més amplis que els "
         "d'<strong>alimentació</strong>, que operen amb marges més estrets i alta rotació. La productivitat va en "
         "sentit invers: els grans supermercats facturen molt per empleat (autoservei i volum), mentre que els formats "
         "de més atenció personal facturen menys per persona. Es mostren només els subsectors amb 2 o més empreses a "
         "la mostra (la mediana d'una sola empresa no seria representativa)."
         if _ca else
         "Los subsectores de <strong>moda y cosmética</strong> presentan márgenes EBITDA más amplios que los de "
         "<strong>alimentación</strong>, que operan con márgenes más estrechos y alta rotación. La productividad va en "
         "sentido inverso: los grandes supermercados facturan mucho por empleado (autoservicio y volumen), mientras que "
         "los formatos de más atención personal facturan menos por persona. Se muestran solo los subsectores con 2 o "
         "más empresas en la muestra (la mediana de una sola empresa no sería representativa).")
    )

# ════════════════════════════════════════════════════════════
# TAB 3 — COST DE PERSONAL (sense referències externes)
# ════════════════════════════════════════════════════════════
with tab_pers:
    st.markdown(("**Cost de personal sobre vendes, per subsector** (2024 · subsectors amb 2+ empreses)" if _ca
                 else "**Coste de personal sobre ventas, por subsector** (2024 · subsectores con 2+ empresas)"))
    rp = sub[sub["n"] >= 2].dropna(subset=["ratio_personal"]).sort_values("ratio_personal")
    figrp = go.Figure()
    figrp.add_trace(go.Bar(y=rp["subsector"], x=rp["ratio_personal"], orientation="h", marker_color=BRAND,
                           text=[f"{v:.1f}%".replace(".", ",") for v in rp["ratio_personal"]],
                           textposition="outside", textfont=dict(size=10)))
    apply_layout(figrp, xaxis_title="Despeses de personal / vendes (mediana, %)" if _ca
                 else "Gastos de personal / ventas (mediana, %)",
                 height=440, margin=dict(l=190, r=70, t=20, b=40))
    st.plotly_chart(figrp, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    insight(
        ("El <strong>cost de personal sobre vendes</strong> varia àmpliament segons el format: els grans operadors "
         "d'alimentació i electrònica el mantenen baix (autoservei, alt volum de venda per empleat), mentre que els "
         "formats amb més atenció personal o de menor escala el tenen sensiblement més alt. La diferència mesura "
         "directament l'efecte de l'escala sobre l'estructura de costos."
         if _ca else
         "El <strong>coste de personal sobre ventas</strong> varía ampliamente según el formato: los grandes operadores "
         "de alimentación y electrónica lo mantienen bajo (autoservicio, alto volumen de venta por empleado), mientras "
         "que los formatos con más atención personal o de menor escala lo tienen sensiblemente más alto. La diferencia "
         "mide directamente el efecto de la escala sobre la estructura de costes.")
    )

# ════════════════════════════════════════════════════════════
# TAB 4 — CREIXEMENT 2020-2024
# ════════════════════════════════════════════════════════════
with tab_creix:
    if _ca:
        st.markdown(
            "Mesurem el creixement amb el **CAGR** (taxa de creixement anual composta) de la facturació entre 2020 i "
            "2024. Mostrem les **8 empreses de la mostra que més han crescut i les 8 que més han caigut**, entre les "
            "que tenen comptes dipositats per als dos anys. Queden fora les que no van dipositar el 2024 o que no "
            "operaven el 2020 (sense base de comparació)."
        )
    else:
        st.markdown(
            "Medimos el crecimiento con el **CAGR** (tasa de crecimiento anual compuesta) de la facturación entre 2020 "
            "y 2024. Mostramos las **8 empresas de la muestra que más han crecido y las 8 que más han caído**, entre "
            "las que tienen cuentas depositadas para ambos años. Quedan fuera las que no depositaron 2024 o que no "
            "operaban en 2020 (sin base de comparación)."
        )
    g = rank.dropna(subset=["cagr"]).copy()
    g = g[(g["ing_2020"] > 0)]
    g = g.sort_values("cagr")
    sel = pd.concat([g.head(8), g.tail(8)]).drop_duplicates("nombre")
    figg = go.Figure()
    figg.add_trace(go.Bar(y=sel["nombre"].str.title(), x=sel["cagr"], orientation="h",
                          marker_color=[GREEN if v >= 0 else RED for v in sel["cagr"]],
                          text=[fpct(v, 1) for v in sel["cagr"]],
                          textposition="outside", textfont=dict(size=10)))
    figg.add_vline(x=0, line_color="rgba(0,0,0,0.3)")
    apply_layout(figg, xaxis_title="CAGR 2020-2024 (%)" if _ca else "CAGR 2020-2024 (%)",
                 height=560, margin=dict(l=230, r=70, t=20, b=40))
    st.plotly_chart(figg, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")
    _w = g.iloc[-1]; _l = g.iloc[0]
    insight(
        (f"Dins la mostra, el creixement és molt desigual: <strong>{_w['nombre'].title()}</strong> encapçala amb un "
         f"CAGR del {fpct(_w['cagr'],1)}, mentre que <strong>{_l['nombre'].title()}</strong> registra {fpct(_l['cagr'],1)}. "
         f"Conviuen formats en expansió accelerada amb d'altres en retrocés o reestructuració durant el període 2020-2024."
         if _ca else
         f"Dentro de la muestra, el crecimiento es muy desigual: <strong>{_w['nombre'].title()}</strong> encabeza con un "
         f"CAGR del {fpct(_w['cagr'],1)}, mientras que <strong>{_l['nombre'].title()}</strong> registra {fpct(_l['cagr'],1)}. "
         f"Conviven formatos en expansión acelerada con otros en retroceso o reestructuración durante el período 2020-2024.")
    )

page_meta("Comptes anuals dipositats al Registre Mercantil (2020-2024) · mostra de grans empreses CNAE 47" if _ca
          else "Cuentas anuales depositadas en el Registro Mercantil (2020-2024) · muestra de grandes empresas CNAE 47",
          st.session_state.lang)

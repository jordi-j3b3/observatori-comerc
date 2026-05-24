"""Pàgina: Líders del comerç (CNAE 47) — top empreses per comptes dipositats al Registre Mercantil"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout, PALETTE, BRAND, BRAND_DEEP, RED, GREEN, GRAY)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"
_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "lideres_comerc.csv")


@st.cache_data(ttl=3600)
def load_lid(sig):
    if os.path.exists(_PATH):
        return pd.read_csv(_PATH)
    return pd.DataFrame()


_sig = ((os.path.getsize(_PATH), int(os.path.getmtime(_PATH))) if os.path.exists(_PATH) else (0, 0))
df = load_lid(_sig)

st.title("Líders del comerç" if _ca else "Líderes del comercio")
intro(
    ("Qui són els grans operadors del comerç al detall espanyol (CNAE 47) i quin pes tenen. "
     "A partir dels <strong>comptes anuals dipositats al Registre Mercantil</strong> (2020-2024) "
     "radiografiem els principals líders del sector: la seva <strong>mida</strong> i concentració, "
     "els <strong>marges</strong> i la productivitat, i el <strong>cost de personal</strong> per escala. "
     "És la cara <strong>microeconòmica</strong> que complementa les sèries agregades de la resta de l'observatori."
     if _ca else
     "Quiénes son los grandes operadores del comercio minorista español (CNAE 47) y qué peso tienen. "
     "A partir de las <strong>cuentas anuales depositadas en el Registro Mercantil</strong> (2020-2024) "
     "radiografiamos los principales líderes del sector: su <strong>tamaño</strong> y concentración, "
     "los <strong>márgenes</strong> y la productividad, y el <strong>coste de personal</strong> por escala. "
     "Es la cara <strong>microeconómica</strong> que complementa las series agregadas del resto del observatorio.")
)

if df.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

ULT = 2024
d24 = df[(df["any"] == ULT) & df["ingresos"].notna()].copy()
rank = d24.sort_values("ingresos", ascending=False).reset_index(drop=True)
tot_ing = rank["ingresos"].sum()
tot_emp = rank["empleados"].sum()

# ─── KPIs ───
k1, k2, k3, k4 = st.columns(4)
k1.metric(("Empreses al rànquing" if _ca else "Empresas en el ranking"), f"{len(rank)}",
          help=(f"amb comptes {ULT} dipositats" if _ca else f"con cuentas {ULT} depositadas"))
k2.metric(("Facturació agregada" if _ca else "Facturación agregada") + f" ({ULT})",
          f"{fnum(tot_ing/1e6, 1)} Md€")
k3.metric(("Ocupació agregada" if _ca else "Empleo agregado"), fnum(tot_emp))
k4.metric(("Pes del líder (Mercadona)" if _ca else "Peso del líder (Mercadona)"),
          fpct(rank.iloc[0]["ingresos"]/tot_ing*100, 1, sign=False),
          help=("% sobre la facturació del grup de líders" if _ca else "% sobre la facturación del grupo de líderes"))

tab_rank, tab_marg, tab_pers, tab_creix = st.tabs([
    ("Rànquing i concentració" if _ca else "Ranking y concentración"),
    ("Marges i productivitat" if _ca else "Márgenes y productividad"),
    ("Ocupació i cost de personal" if _ca else "Empleo y coste de personal"),
    ("Creixement 2020-2024" if _ca else "Crecimiento 2020-2024"),
])

# ════════════════════════════════════════════════════════════
# TAB 1 — RÀNQUING I CONCENTRACIÓ
# ════════════════════════════════════════════════════════════
with tab_rank:
    st.markdown(("**Els 20 majors per facturació** " if _ca else "**Los 20 mayores por facturación** ") + f"({ULT})")
    top = rank.head(20).iloc[::-1]
    subs = list(top["subsector"].unique())
    cmap = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted(d24["subsector"].unique()))}
    figr = go.Figure()
    figr.add_trace(go.Bar(
        y=top["nombre"].str.title(), x=top["ingresos"]/1000, orientation="h",
        marker_color=[cmap[s] for s in top["subsector"]],
        text=[f"{fnum(v/1000)} M€" for v in top["ingresos"]],
        textposition="outside", textfont=dict(size=10),
        customdata=top["subsector"],
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} M€<br>%{customdata}<extra></extra>"))
    apply_layout(figr, xaxis_title="Facturació (M€)" if _ca else "Facturación (M€)",
                 height=620, margin=dict(l=230, r=90, t=20, b=40))
    st.plotly_chart(figr, use_container_width=True)
    source("Comptes anuals dipositats al Registre Mercantil" if _ca
           else "Cuentas anuales depositadas en el Registro Mercantil")

    # Concentració acumulada
    st.markdown(("**Concentració: corba acumulada**" if _ca else "**Concentración: curva acumulada**"))
    cum = rank["ingresos"].cumsum()/tot_ing*100
    figc = go.Figure()
    figc.add_trace(go.Scatter(x=list(range(1, len(rank)+1)), y=cum, mode="lines",
                              line=dict(color=BRAND, width=2.5), fill="tozeroy",
                              fillcolor="rgba(0,51,102,0.08)"))
    for r in [5, 10, 20]:
        if r <= len(rank):
            figc.add_vline(x=r, line_dash="dot", line_color=GRAY,
                           annotation_text=f"top {r}: {cum.iloc[r-1]:.0f}%", annotation_position="top")
    apply_layout(figc, xaxis_title=("Nombre d'empreses" if _ca else "Número de empresas"),
                 yaxis_title="% acumulat de la facturació" if _ca else "% acumulado de la facturación",
                 height=360, yaxis_range=[0, 100])
    st.plotly_chart(figc, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    _t5 = rank.head(5)["ingresos"].sum()/tot_ing*100
    _t10 = rank.head(10)["ingresos"].sum()/tot_ing*100
    _t20 = rank.head(20)["ingresos"].sum()/tot_ing*100
    insight(
        (f"El comerç al detall espanyol és <strong>fortament concentrat</strong> en la part alta. "
         f"Dins el grup de líders, els <strong>5 primers concentren el {fpct(_t5,0,sign=False)}</strong> de la facturació, "
         f"els 10 primers el {fpct(_t10,0,sign=False)} i els 20 primers el {fpct(_t20,0,sign=False)}. "
         f"<strong>Mercadona sol</strong> en representa el {fpct(rank.iloc[0]['ingresos']/tot_ing*100,0,sign=False)}. "
         f"L'alimentació domina la part alta del rànquing; la moda i la llar hi apareixen a partir de la franja mitjana. "
         f"És la traducció micro de la tesi de l'observatori: un mercat on els grans operadors guanyen escala."
         if _ca else
         f"El comercio minorista español está <strong>fuertemente concentrado</strong> en la parte alta. "
         f"Dentro del grupo de líderes, los <strong>5 primeros concentran el {fpct(_t5,0,sign=False)}</strong> de la facturación, "
         f"los 10 primeros el {fpct(_t10,0,sign=False)} y los 20 primeros el {fpct(_t20,0,sign=False)}. "
         f"<strong>Mercadona solo</strong> representa el {fpct(rank.iloc[0]['ingresos']/tot_ing*100,0,sign=False)}. "
         f"La alimentación domina la parte alta; moda y hogar aparecen a partir de la franja media. "
         f"Es la traducción micro de la tesis del observatorio: un mercado donde los grandes operadores ganan escala.")
    )

# ════════════════════════════════════════════════════════════
# TAB 2 — MARGES I PRODUCTIVITAT
# ════════════════════════════════════════════════════════════
with tab_marg:
    st.markdown(("**Marge EBITDA mitjà per subsector**" if _ca else "**Margen EBITDA medio por subsector**") + f" ({ULT})")
    g = (d24.dropna(subset=["marge_ebitda"]).groupby("subsector")
         .agg(marge=("marge_ebitda", "median"), n=("nombre", "count")).reset_index())
    g = g[g["n"] >= 1].sort_values("marge")
    figm = go.Figure()
    figm.add_trace(go.Bar(y=g["subsector"], x=g["marge"], orientation="h",
                          marker_color=BRAND,
                          text=[f"{v:.1f}%".replace(".", ",") for v in g["marge"]],
                          textposition="outside", textfont=dict(size=10)))
    apply_layout(figm, xaxis_title="Marge EBITDA (mediana, %)" if _ca else "Margen EBITDA (mediana, %)",
                 height=460, margin=dict(l=180, r=70, t=20, b=40))
    st.plotly_chart(figm, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    st.markdown(("**Productivitat: facturació per empleat**" if _ca else "**Productividad: facturación por empleado**") + f" ({ULT})")
    p = (d24.dropna(subset=["ingressos_per_empleat"]).groupby("subsector")
         .agg(prod=("ingressos_per_empleat", "median")).reset_index().sort_values("prod"))
    figp = go.Figure()
    figp.add_trace(go.Bar(y=p["subsector"], x=p["prod"]/1000, orientation="h",
                          marker_color=BRAND_DEEP,
                          text=[f"{fnum(v/1000)} k€" for v in p["prod"]],
                          textposition="outside", textfont=dict(size=10)))
    apply_layout(figp, xaxis_title="Facturació per empleat (k€)" if _ca else "Facturación por empleado (k€)",
                 height=460, margin=dict(l=180, r=80, t=20, b=40))
    st.plotly_chart(figp, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    insight(
        ("Els <strong>marges varien molt per subsector</strong>: la moda i la cosmètica treballen amb marges "
         "EBITDA superiors (producte amb més valor afegit i marca), mentre que l'alimentació i el combustible "
         "operen amb marges estrets compensats per <strong>volum i rotació</strong>. La productivitat ho confirma: "
         "els grans supermercats i les benzineres facturen molt per empleat (escala i autoservei), mentre que els "
         "formats de servei i atenció personal facturen menys per persona. Marge i productivitat dibuixen dos "
         "models de negoci dins el mateix CNAE 47."
         if _ca else
         "Los <strong>márgenes varían mucho por subsector</strong>: moda y cosmética trabajan con márgenes EBITDA "
         "superiores (producto con más valor añadido y marca), mientras que alimentación y combustible operan con "
         "márgenes estrechos compensados por <strong>volumen y rotación</strong>. La productividad lo confirma: los "
         "grandes supermercados y las gasolineras facturan mucho por empleado (escala y autoservicio), mientras que "
         "los formatos de servicio y atención personal facturan menos por persona. Margen y productividad dibujan "
         "dos modelos de negocio dentro del mismo CNAE 47.")
    )

# ════════════════════════════════════════════════════════════
# TAB 3 — OCUPACIÓ I COST DE PERSONAL
# ════════════════════════════════════════════════════════════
with tab_pers:
    st.markdown(("**Cost de personal sobre vendes, per subsector**" if _ca
                 else "**Coste de personal sobre ventas, por subsector**") + f" ({ULT})")
    rp = (d24.dropna(subset=["ratio_personal"]).groupby("subsector")
          .agg(ratio=("ratio_personal", "median")).reset_index().sort_values("ratio"))
    figrp = go.Figure()
    figrp.add_trace(go.Bar(y=rp["subsector"], x=rp["ratio"], orientation="h",
                           marker_color=BRAND,
                           text=[f"{v:.1f}%".replace(".", ",") for v in rp["ratio"]],
                           textposition="outside", textfont=dict(size=10)))
    figrp.add_vline(x=34.9, line_dash="dash", line_color=RED, line_width=2,
                    annotation_text=("Bar petit (Rubí): 34,9%" if _ca else "Bar pequeño (Rubí): 34,9%"),
                    annotation_position="top")
    apply_layout(figrp, xaxis_title="Despeses de personal / vendes (mediana, %)" if _ca
                 else "Gastos de personal / ventas (mediana, %)",
                 height=480, margin=dict(l=180, r=70, t=40, b=40))
    st.plotly_chart(figrp, use_container_width=True)
    source("Comptes dipositats al Registre Mercantil. Càlcul propi" if _ca
           else "Cuentas depositadas en el Registro Mercantil. Cálculo propio")

    insight(
        ("El <strong>cost de personal sobre vendes</strong> és el millor termòmetre de l'efecte escala. Els grans "
         "operadors d'alimentació i combustible es mouen entre el 4 % i el 13 % (autoservei, alt volum per empleat); "
         "els formats petits i de servei intensiu pugen fins al 30-35 %. La línia vermella marca el "
         "<strong>34,9 %</strong> d'un bar de proximitat (cas Rubí): la distància respecte als grans líders mesura, "
         "literalment, el cost de no tenir escala. És la mateixa lògica que explica per què el petit comerç perd "
         "quota davant els grans formats."
         if _ca else
         "El <strong>coste de personal sobre ventas</strong> es el mejor termómetro del efecto escala. Los grandes "
         "operadores de alimentación y combustible se mueven entre el 4 % y el 13 % (autoservicio, alto volumen por "
         "empleado); los formatos pequeños y de servicio intensivo suben hasta el 30-35 %. La línea roja marca el "
         "<strong>34,9 %</strong> de un bar de proximidad (caso Rubí): la distancia respecto a los grandes líderes "
         "mide, literalmente, el coste de no tener escala.")
    )

# ════════════════════════════════════════════════════════════
# TAB 4 — CREIXEMENT 2020-2024
# ════════════════════════════════════════════════════════════
with tab_creix:
    base = df[df["any"].isin([2020, 2024])].pivot_table(index=["nombre", "subsector"], columns="any",
                                                         values="ingresos").reset_index()
    base = base.dropna(subset=[2020, 2024])
    base = base[base[2020] > 0]
    base["cagr"] = ((base[2024]/base[2020])**(1/4) - 1) * 100
    base = base.sort_values("cagr")
    sel = pd.concat([base.head(8), base.tail(8)]).drop_duplicates("nombre")
    st.markdown(("**Creixement anual mitjà (CAGR) de la facturació 2020-2024**" if _ca
                 else "**Crecimiento anual medio (CAGR) de la facturación 2020-2024**"))
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
    _win = base.iloc[-1]; _los = base.iloc[0]
    insight(
        (f"Entre 2020 i 2024, els <strong>guanyadors</strong> combinen expansió de xarxa i posicionament en preu o "
         f"experiència —<strong>{_win['nombre'].title()}</strong> lidera amb un CAGR del {fpct(_win['cagr'],1)}—, "
         f"mentre que els <strong>perdedors</strong> arrosseguen reestructuracions o formats sota pressió "
         f"(<strong>{_los['nombre'].title()}</strong>, {fpct(_los['cagr'],1)}). El creixement no és uniforme: "
         f"dins del sector hi conviuen models en expansió accelerada i models en retrocés."
         if _ca else
         f"Entre 2020 y 2024, los <strong>ganadores</strong> combinan expansión de red y posicionamiento en precio o "
         f"experiencia —<strong>{_win['nombre'].title()}</strong> lidera con un CAGR del {fpct(_win['cagr'],1)}—, "
         f"mientras que los <strong>perdedores</strong> arrastran reestructuraciones o formatos bajo presión "
         f"(<strong>{_los['nombre'].title()}</strong>, {fpct(_los['cagr'],1)}). El crecimiento no es uniforme.")
    )

# ─── Descàrrega (taula derivada, no l'export brut) ───
with st.expander(t("download_data")):
    out = rank[["nombre", "subsector", "ingresos", "marge_ebitda", "ratio_personal", "ingressos_per_empleat", "empleados"]].copy()
    out.columns = ["Empresa", "Subsector", "Facturació (mil€)", "Marge EBITDA %", "Personal/vendes %", "€/empleat", "Empleats"]
    st.dataframe(out, use_container_width=True)
    st.download_button("CSV", out.to_csv(index=False).encode("utf-8"), "lideres_comerc_resum.csv", "text/csv")

page_meta("Comptes anuals dipositats al Registre Mercantil (2020-2024)" if _ca
          else "Cuentas anuales depositadas en el Registro Mercantil (2020-2024)", st.session_state.lang)

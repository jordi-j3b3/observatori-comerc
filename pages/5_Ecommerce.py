"""Pàgina 5: Comerç Electrònic (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, GREEN, GRAY)

inject_css()
t = setup_lang(show_selector=False)
page_header()

@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "ecommerce.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

st.title(t("ec_title"))

_ca = st.session_state.lang == "ca"

if _ca:
    intro(
        "El <strong>comerç electrònic</strong> és el canal de venda amb major creixement del sector del detall. "
        "Aquesta secció analitza el volum de negoci online generat per les empreses CNAE 47 i el compara "
        "amb el total del comerç electrònic a Espanya. El <strong>pes sobre el total</strong> indica "
        "quina proporció de l'e-commerce correspon al comerç al detall — si baixa, vol dir que altres "
        "sectors (serveis, turisme, continguts digitals) creixen encara més ràpid en el canal online. "
        "El <strong>CAGR</strong> permet comparar el ritme de creixement amb el del comerç físic."
    )
else:
    intro(
        "El <strong>comercio electrónico</strong> es el canal de venta con mayor crecimiento del sector minorista. "
        "Esta sección analiza el volumen de negocio online generado por las empresas CNAE 47 y lo compara "
        "con el total del comercio electrónico en España. El <strong>peso sobre el total</strong> indica "
        "qué proporción del e-commerce corresponde al comercio minorista — si baja, significa que otros "
        "sectores (servicios, turismo, contenidos digitales) crecen aún más rápido en el canal online. "
        "El <strong>CAGR</strong> permite comparar el ritmo de crecimiento con el del comercio físico."
    )

if df.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

df = df.sort_values("any")

# ─── KPIs ─────────────────────────────────────────────────────

if "ecommerce_cnae47_eur" in df.columns:
    first = df.dropna(subset=["ecommerce_cnae47_eur"]).iloc[0]
    last = df.dropna(subset=["ecommerce_cnae47_eur"]).iloc[-1]
    n_years = int(last["any"]) - int(first["any"])
    multiplicador = last["ecommerce_cnae47_eur"] / first["ecommerce_cnae47_eur"]
    cagr_ec = cagr(first["ecommerce_cnae47_eur"], last["ecommerce_cnae47_eur"], n_years)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"E-commerce CNAE 47 ({int(last['any'])})",
                f"{fnum(last['ecommerce_cnae47_eur'] / 1e9, 1)} Md EUR")
    col2.metric(f"{'Multiplicador' if _ca else 'Multiplicador'} {int(first['any'])}-{int(last['any'])}",
                f"x{fnum(multiplicador)}")
    col3.metric("CAGR", fpct(cagr_ec))
    if "pes_cnae47_ecommerce" in df.columns:
        col4.metric(f"{'Pes sobre total' if _ca else 'Peso sobre total'} ({int(last['any'])})",
                    fpct(last['pes_cnae47_ecommerce'] * 100, 1, sign=False))

# ─── Nota metodològica any parcial ───────────────────────────

if len(df) >= 2:
    _last_yr = df.iloc[-1]
    _prev_yr = df.iloc[-2]
    if "ecommerce_total_eur" in df.columns:
        _ratio = _last_yr["ecommerce_total_eur"] / _prev_yr["ecommerce_total_eur"]
        if _ratio < 0.85:
            _any_parcial = int(_last_yr["any"])
            if _ca:
                st.warning(
                    f"**Nota metodològica:** Les dades de {_any_parcial} són provisionals i corresponen "
                    f"a un any incomplet (dades publicades fins al moment per la CNMC). "
                    f"La caiguda aparent respecte a {_any_parcial - 1} reflecteix la manca de dades dels últims trimestres, "
                    f"no una reducció real del volum de negoci."
                )
            else:
                st.warning(
                    f"**Nota metodológica:** Los datos de {_any_parcial} son provisionales y corresponden "
                    f"a un año incompleto (datos publicados hasta el momento por la CNMC). "
                    f"La caída aparente respecto a {_any_parcial - 1} refleja la falta de datos de los últimos trimestres, "
                    f"no una reducción real del volumen de negocio."
                )

# ─── Gràfic 1: Volum e-commerce ──────────────────────────────

st.subheader(t("ec_volume"))

fig = go.Figure()

if "ecommerce_total_eur" in df.columns:
    fig.add_trace(go.Bar(
        x=df["any"], y=df["ecommerce_total_eur"] / 1e9,
        name=t("ec_total"),
        marker_color=GRAY,
    ))

if "ecommerce_cnae47_eur" in df.columns:
    fig.add_trace(go.Bar(
        x=df["any"], y=df["ecommerce_cnae47_eur"] / 1e9,
        name=t("ec_cnae47"),
        marker_color=PURPLE,
    ))

apply_layout(fig,
    yaxis_title=("Milers de milions EUR" if _ca else "Miles de millones EUR"),
    barmode="group", height=450)
st.plotly_chart(fig, use_container_width=True)
source("CNMC, Comerç electrònic a Espanya" if _ca
       else "CNMC, Comercio electrónico en España")

# ─── Gràfic 2: Pes CNAE 47 sobre total ────────────────────────

if "pes_cnae47_ecommerce" in df.columns:
    st.subheader(t("ec_weight"))

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["any"], y=df["pes_cnae47_ecommerce"] * 100,
        mode="lines+markers",
        line=dict(color=PURPLE, width=3),
        marker=dict(size=8),
        fill="tozeroy", fillcolor="rgba(93,79,255,0.08)",
    ))
    apply_layout(fig2,
        yaxis_title=("% sobre total e-commerce" if _ca else "% sobre total e-commerce"),
        height=400)
    st.plotly_chart(fig2, use_container_width=True)
    source("CNMC. Càlcul propi" if _ca else "CNMC. Cálculo propio")

# ─── Gràfic 3: Creixement interanual ──────────────────────────

if "ecommerce_cnae47_eur" in df.columns and len(df) > 1:
    df["creix_ec"] = df["ecommerce_cnae47_eur"].pct_change() * 100

    st.subheader("Creixement interanual e-commerce CNAE 47" if _ca
                 else "Crecimiento interanual e-commerce CNAE 47")
    fig3 = go.Figure()
    df_creix = df.dropna(subset=["creix_ec"])
    colors = [GREEN if v >= 0 else RED for v in df_creix["creix_ec"]]
    fig3.add_trace(go.Bar(
        x=df_creix["any"], y=df_creix["creix_ec"],
        marker_color=colors,
        text=[fpct(v) for v in df_creix["creix_ec"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig3,
        yaxis_title=("Variació interanual (%)" if _ca else "Variación interanual (%)"),
        height=400)
    fig3.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    st.plotly_chart(fig3, use_container_width=True)
    source("CNMC. Càlcul propi" if _ca else "CNMC. Cálculo propio")

# ─── Insight e-commerce ──────────────────────────────────────

if "ecommerce_cnae47_eur" in df.columns and "pes_cnae47_ecommerce" in df.columns:
    pes_first = df.dropna(subset=["pes_cnae47_ecommerce"]).iloc[0]["pes_cnae47_ecommerce"] * 100
    pes_last = df.dropna(subset=["pes_cnae47_ecommerce"]).iloc[-1]["pes_cnae47_ecommerce"] * 100
    pes_var = pes_last - pes_first

    if _ca:
        txt = (
            f"El comerç electrònic del CNAE 47 ha multiplicat el seu volum per <strong>x{fnum(multiplicador)}</strong> "
            f"en {n_years} anys, amb un CAGR del <strong>{fpct(cagr_ec)}</strong>. "
            f"El pes del detall sobre el total d'e-commerce "
            f"ha passat del {fpct(pes_first, 1, sign=False)} al {fpct(pes_last, 1, sign=False)} ({fpct(pes_var)} pp). "
        )
        if pes_var < 0:
            txt += (
                "Això indica que <strong>altres sectors han crescut encara més ràpidament</strong> en el canal digital. "
                "El comerç al detall, tot i ser un adoptant significatiu, "
                "perd quota relativa davant serveis, turisme i sectors amb major marge digital. "
                "La digitalització del sector ha estat reactiva (accelerada per la pandèmia) "
                "més que proactiva, cosa que explica la pèrdua de quota relativa."
            )
        else:
            txt += (
                "Això indica que <strong>el comerç al detall guanya quota en el canal digital</strong> "
                "per sobre d'altres sectors, consolidant la seva posició en l'ecosistema d'e-commerce."
            )
    else:
        txt = (
            f"El comercio electrónico del CNAE 47 ha multiplicado su volumen por <strong>x{fnum(multiplicador)}</strong> "
            f"en {n_years} años, con un CAGR del <strong>{fpct(cagr_ec)}</strong>. "
            f"El peso del minorista sobre el total de e-commerce "
            f"ha pasado del {fpct(pes_first, 1, sign=False)} al {fpct(pes_last, 1, sign=False)} ({fpct(pes_var)} pp). "
        )
        if pes_var < 0:
            txt += (
                "Esto indica que <strong>otros sectores han crecido aún más rápidamente</strong> en el canal digital. "
                "El comercio minorista, aun siendo un adoptante significativo, "
                "pierde cuota relativa frente a servicios, turismo y sectores con mayor margen digital. "
                "La digitalización del sector ha sido reactiva (acelerada por la pandemia) "
                "más que proactiva, lo que explica la pérdida de cuota relativa."
            )
        else:
            txt += (
                "Esto indica que <strong>el minorista gana cuota en el canal digital</strong> "
                "por encima de otros sectores, consolidando su posición en el ecosistema de e-commerce."
            )
    insight(txt)

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "ecommerce_cnae47.csv", "text/csv")

page_meta("CNMC, Comissió Nacional dels Mercats i la Competència" if _ca
          else "CNMC, Comisión Nacional de los Mercados y la Competencia", st.session_state.lang)

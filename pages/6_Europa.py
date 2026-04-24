"""Pàgina 6: Comparativa Europea (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout,
                   PURPLE, RED, BLUE, GREEN, ORANGE, GRAY)

inject_css()
t = setup_lang(show_selector=False)

@st.cache_data(ttl=3600)
def load_europa():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "europa_vab.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_europa()

st.title(t("eu_title"))

_ca = st.session_state.lang == "ca"

if _ca:
    intro(
        "Aquesta secció posiciona el comerç al detall espanyol en el context europeu. "
        "El <strong>pes del CNAE 47 sobre el PIB</strong> de cada país reflecteix l'estructura econòmica: "
        "els països amb més pes del comerç al detall solen tenir economies més orientades al consum final, "
        "mentre que els de menor pes tenen més pes industrial o de serveis avançats. "
        "El <strong>VAB absolut</strong> indica la dimensió total del sector a cada país. "
        "Espanya es destaca en vermell per facilitar la comparació."
    )
else:
    intro(
        "Esta sección posiciona el comercio minorista español en el contexto europeo. "
        "El <strong>peso del CNAE 47 sobre el PIB</strong> de cada país refleja la estructura económica: "
        "los países con más peso del comercio minorista suelen tener economías más orientadas al consumo final, "
        "mientras que los de menor peso tienen más peso industrial o de servicios avanzados. "
        "El <strong>VAB absoluto</strong> indica la dimensión total del sector en cada país. "
        "España se destaca en rojo para facilitar la comparación."
    )

if df.empty:
    st.warning("No hi ha dades europees disponibles." if _ca
               else "No hay datos europeos disponibles.")
    st.stop()

# ─── Selector d'any ─────────────────────────��──────────────────

anys = sorted(df["any"].dropna().unique(), reverse=True)
any_sel = st.selectbox(t("year"), anys, index=0)

df_year = df[df["any"] == any_sel].copy()

# ─── KPIs posició Espanya ────────────────────────────────────

exclude_agg = ["EU27_2020", "EA20", "EA19"]
df_countries = df_year[~df_year["pais_codi"].isin(exclude_agg)].copy()
es_data = df_year[df_year["pais_codi"] == "ES"]
eu_data = df_year[df_year["pais_codi"] == "EU27_2020"]

if not es_data.empty and "pes_cnae47" in es_data.columns:
    col1, col2, col3 = st.columns(3)

    es_pes = es_data.iloc[0]["pes_cnae47"] * 100
    lbl_pes = "Pes CNAE 47 Espanya" if _ca else "Peso CNAE 47 España"
    col1.metric(f"{lbl_pes} ({int(any_sel)})", fpct(es_pes, 2, sign=False))

    if not eu_data.empty:
        eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100
        diff = es_pes - eu_pes
        col2.metric("Mitjana UE-27" if _ca else "Media UE-27",
                    fpct(eu_pes, 2, sign=False), f"{fpct(diff, 2)} vs UE")

    if not df_countries.empty:
        ranking = df_countries.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=False)
        pos_es = list(ranking["pais_codi"]).index("ES") + 1 if "ES" in list(ranking["pais_codi"]) else "—"
        col3.metric("Posició al rànquing" if _ca else "Posición en el ranking",
                    f"#{pos_es} de {len(ranking)}")

# ─── Gràfic 1: Pes CNAE 47 sobre PIB ─────────────────────────

st.subheader(t("eu_weight"))

if "pes_cnae47" in df_year.columns:
    df_sorted = df_year.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=True)

    colors = [RED if code == "ES" else PURPLE if code == "EU27_2020" else GRAY
              for code in df_sorted["pais_codi"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["pais"], x=df_sorted["pes_cnae47"] * 100,
        orientation="h",
        marker_color=colors,
        text=[fpct(v, 2, sign=False) for v in df_sorted["pes_cnae47"] * 100],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig,
        xaxis_title="% PIB",
        height=max(450, len(df_sorted) * 28),
        margin=dict(l=140, r=80, t=40, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Gràfic 2: VAB absolut ──────────────────────────────────

st.subheader(f"VAB CNAE 47 ({int(any_sel)}) — {t('pib_meur')}")

if "vab_meur" in df_year.columns:
    df_abs = df_countries.dropna(subset=["vab_meur"])
    df_abs = df_abs.sort_values("vab_meur", ascending=True).tail(15)

    colors2 = [RED if code == "ES" else BLUE for code in df_abs["pais_codi"]]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=df_abs["pais"], x=df_abs["vab_meur"],
        orientation="h",
        marker_color=colors2,
        text=[fnum(v) for v in df_abs["vab_meur"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig2,
        xaxis_title=t("pib_meur"),
        height=500,
        margin=dict(l=140, r=80, t=40, b=50),
    )
    st.plotly_chart(fig2, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Gràfic 3: Evolució temporal ─────────────────────────────

st.subheader("Evolució pes CNAE 47 — principals països" if _ca
             else "Evolución peso CNAE 47 — principales países")

highlight = ["ES", "DE", "FR", "IT", "PT", "EU27_2020"]
colors_map = {
    "ES": RED, "DE": BLUE, "FR": GREEN,
    "IT": ORANGE, "PT": "#8E44AD", "EU27_2020": PURPLE,
}

if "pes_cnae47" in df.columns:
    fig3 = go.Figure()
    for code in highlight:
        df_c = df[df["pais_codi"] == code].sort_values("any")
        if not df_c.empty:
            fig3.add_trace(go.Scatter(
                x=df_c["any"], y=df_c["pes_cnae47"] * 100,
                mode="lines+markers",
                name=df_c["pais"].iloc[0],
                line=dict(color=colors_map.get(code, "#999"), width=2.5),
                marker=dict(size=5),
            ))

    apply_layout(fig3, yaxis_title="% PIB", height=450)
    st.plotly_chart(fig3, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Insight Europa ──────────────────────────────────────────

if not es_data.empty and not eu_data.empty and "pes_cnae47" in es_data.columns:
    es_pes = es_data.iloc[0]["pes_cnae47"] * 100
    eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100

    es_hist = df[df["pais_codi"] == "ES"].sort_values("any")
    if len(es_hist) > 1:
        es_first = es_hist.iloc[0]["pes_cnae47"] * 100
        es_last = es_hist.iloc[-1]["pes_cnae47"] * 100
        es_trend = es_last - es_first

        if _ca:
            txt = (
                f"Espanya destina un <strong>{fpct(es_pes, 2, sign=False)}</strong> del seu PIB al comerç al detall, "
            )
            if es_pes > eu_pes:
                txt += (
                    f"<strong>{fpct(es_pes - eu_pes, 2)} per sobre</strong> de la mitjana europea ({fpct(eu_pes, 2, sign=False)}). "
                    "Això pot reflectir una estructura econòmica amb més pes del consum final "
                    "i una menor industrialització relativa comparada amb països com Alemanya. "
                    "El pes superior també s'explica per la importància del turisme, que impulsa "
                    "el consum al detall especialment en zones costaneres i urbanes. "
                )
            else:
                txt += (
                    f"<strong>{fpct(eu_pes - es_pes, 2)} per sota</strong> de la mitjana europea ({fpct(eu_pes, 2, sign=False)}). "
                )
            txt += (
                f"La tendència mostra una variació de <strong>{fpct(es_trend, 2)} pp</strong> des de "
                f"{int(es_hist.iloc[0]['any'])}. "
            )
            if es_trend < -0.2:
                txt += (
                    "La pèrdua de pes és consistent amb la transformació digital i la concentració empresarial: "
                    "menys empreses, però més grans i eficients, generant menys VAB relatiu però amb major productivitat."
                )
        else:
            txt = (
                f"España destina un <strong>{fpct(es_pes, 2, sign=False)}</strong> de su PIB al comercio minorista, "
            )
            if es_pes > eu_pes:
                txt += (
                    f"<strong>{fpct(es_pes - eu_pes, 2)} por encima</strong> de la media europea ({fpct(eu_pes, 2, sign=False)}). "
                    "Esto puede reflejar una estructura económica con más peso del consumo final "
                    "y una menor industrialización relativa comparada con países como Alemania. "
                    "El peso superior también se explica por la importancia del turismo, que impulsa "
                    "el consumo minorista especialmente en zonas costeras y urbanas. "
                )
            else:
                txt += (
                    f"<strong>{fpct(eu_pes - es_pes, 2)} por debajo</strong> de la media europea ({fpct(eu_pes, 2, sign=False)}). "
                )
            txt += (
                f"La tendencia muestra una variación de <strong>{fpct(es_trend, 2)} pp</strong> desde "
                f"{int(es_hist.iloc[0]['any'])}. "
            )
            if es_trend < -0.2:
                txt += (
                    "La pérdida de peso es consistente con la transformación digital y la concentración empresarial: "
                    "menos empresas, pero más grandes y eficientes, generando menos VAB relativo pero con mayor productividad."
                )
        insight(txt)

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "europa_cnae47.csv", "text/csv")

page_meta("Eurostat, Comptes Nacionals d'Europa" if _ca
          else "Eurostat, Cuentas Nacionales de Europa", st.session_state.lang)

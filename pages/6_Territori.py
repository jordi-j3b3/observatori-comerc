"""Pàgina 6: Territori — Magnituds del CNAE 47 per CCAA"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout,
                   PURPLE, PURPLE_LIGHT, RED, PALETTE)

inject_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"

st.title("Territori" if _ca else "Territorio")

if _ca:
    intro(
        "La Comptabilitat Regional de l'INE no desglossa el CNAE 47 per comunitats autonomes. "
        "Per estimar el VAB del comerc al detall per CCAA, combinem dues fonts: "
        "la <strong>comptabilitat regional d'Eurostat</strong> (VAB de la seccio G-I: comerc, transport i hostaleria) "
        "i la <strong>xifra de negoci per CCAA</strong> de l'Enquesta Estructural d'Empreses de l'INE. "
        "El metode hibrid distribueix el VAB nacional del CNAE 47 entre CCAA ponderant "
        "les quotes regionals de G-I (top-down) amb les quotes de facturacio (bottom-up), "
        "garantint que la suma coincideixi amb el total nacional d'Eurostat."
    )
else:
    intro(
        "La Contabilidad Regional del INE no desglosa el CNAE 47 por comunidades autonomas. "
        "Para estimar el VAB del comercio minorista por CCAA, combinamos dos fuentes: "
        "la <strong>contabilidad regional de Eurostat</strong> (VAB de la seccion G-I: comercio, transporte y hosteleria) "
        "y la <strong>cifra de negocio por CCAA</strong> de la Encuesta Estructural de Empresas del INE. "
        "El metodo hibrido distribuye el VAB nacional del CNAE 47 entre CCAA ponderando "
        "las cuotas regionales de G-I (top-down) con las cuotas de facturacion (bottom-up), "
        "garantizando que la suma coincida con el total nacional de Eurostat."
    )

@st.cache_data(ttl=3600)
def load_data():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "eee_ccaa.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data
def load_geojson():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "geo", "spain_ccaa.geojson")
    with open(p, "r") as f:
        return json.load(f)

df_eee = load_data()

if df_eee.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

geojson = load_geojson()
df_ccaa = df_eee[df_eee["territori"] != "espanya"].copy()
df_esp = df_eee[df_eee["territori"] == "espanya"].copy()
_tots_anys = sorted(df_ccaa["any"].dropna().unique())
if "pes_cnae47_pib" in df_ccaa.columns:
    anys = sorted(df_ccaa.dropna(subset=["pes_cnae47_pib"])["any"].unique())
else:
    anys = _tots_anys
if not anys:
    anys = _tots_anys

# ─── Selector d'any ──────────────────────────────────────────

any_sel = st.select_slider(
    t("emp_ccaa_year"),
    options=anys,
    value=max(anys),
)

# ─── KPIs ────────────────────────────────────────────────────

VAB_COL = "vab_eurostat" if "vab_eurostat" in df_eee.columns else "vab_estimat"

d_yr_esp = df_esp[df_esp["any"] == any_sel]
if not d_yr_esp.empty:
    row = d_yr_esp.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    if pd.notna(row.get("pes_cnae47_pib")):
        c1.metric(
            f"{'Pes CNAE 47 / PIB' if _ca else 'Peso CNAE 47 / PIB'} ({int(any_sel)})",
            fpct(row["pes_cnae47_pib"] * 100, 2, sign=False))
    if "xifra_negoci" in row and pd.notna(row.get("xifra_negoci")):
        c2.metric(t("eee_ccaa_xn") + " (M EUR)", fnum(row["xifra_negoci"] / 1e6))
    if "personal_ocupat" in row and pd.notna(row.get("personal_ocupat")):
        c3.metric(t("eee_ccaa_personal"), fnum(row["personal_ocupat"]))
    if "locals" in row and pd.notna(row.get("locals")):
        c4.metric("Locals" if _ca else "Locales", fnum(row["locals"]))

# ─── Pes del CNAE 47 sobre el PIB per CCAA ──────────────────

_lbl_pes = ("Pes del comerc al detall sobre el PIB de cada CCAA" if _ca
            else "Peso del comercio minorista sobre el PIB de cada CCAA")
st.subheader(f"{_lbl_pes} ({int(any_sel)})")

if "pes_cnae47_pib" in df_ccaa.columns:
    d_pes = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["pes_cnae47_pib"]).copy()
    d_pes = d_pes.sort_values("pes_cnae47_pib", ascending=True)

    if not d_pes.empty:
        d_pes["_pct"] = d_pes["pes_cnae47_pib"] * 100

        esp_pes_row = df_esp[df_esp["any"] == any_sel]
        esp_pes = None
        if not esp_pes_row.empty and pd.notna(esp_pes_row.iloc[0].get("pes_cnae47_pib")):
            esp_pes = esp_pes_row.iloc[0]["pes_cnae47_pib"] * 100

        colors_pes = []
        for _, r in d_pes.iterrows():
            if esp_pes is not None and r["_pct"] >= esp_pes:
                colors_pes.append(PURPLE)
            else:
                colors_pes.append(PURPLE_LIGHT)

        fig_pes = go.Figure()
        fig_pes.add_trace(go.Bar(
            y=d_pes["territori"], x=d_pes["_pct"],
            orientation="h",
            marker_color=colors_pes,
            text=[fpct(v, 2, sign=False) for v in d_pes["_pct"]],
            textposition="outside",
            textfont=dict(size=11),
        ))

        if esp_pes is not None:
            fig_pes.add_vline(
                x=esp_pes, line_dash="dash", line_color=RED, line_width=2,
                annotation_text=f"{'Espanya' if _ca else 'Espana'}: {fpct(esp_pes, 2, sign=False)}",
                annotation_position="top right",
            )

        apply_layout(fig_pes,
            xaxis_title="% PIB",
            height=max(450, len(d_pes) * 32 + 100),
            margin=dict(l=200, r=100, t=50, b=50),
        )
        st.plotly_chart(fig_pes, use_container_width=True)
        source("Eurostat + INE. Estimacio hibrida propia" if _ca
               else "Eurostat + INE. Estimacion hibrida propia")

    # ── Mapa del pes ──
    d_map = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["pes_cnae47_pib"]).copy()
    d_map["_pct"] = d_map["pes_cnae47_pib"] * 100

    if not d_map.empty:
        fig_map = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=d_map["territori"],
            featureidkey="properties.territori",
            z=d_map["_pct"],
            zmin=d_map["_pct"].min() * 0.9,
            zmax=d_map["_pct"].max() * 1.05,
            colorscale=[
                [0, "#e8f0fe"], [0.15, "#a8c8e8"], [0.35, "#5a9fd4"],
                [0.55, "#0055a4"], [0.75, "#003d7a"], [1, "#001d3d"],
            ],
            colorbar=dict(title="% PIB", thickness=15),
            marker=dict(line=dict(width=1.5, color="white")),
            text=d_map["territori"],
            hovertemplate="<b>%{text}</b><br>Pes CNAE 47: %{z:.2f}%<extra></extra>",
        ))
        fig_map.update_layout(
            map=dict(style="white-bg", center=dict(lat=39.5, lon=-3.5), zoom=4.8),
            height=700, margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig_map, use_container_width=True)

# ─── Productivitat per CCAA ──────────────────────────────────

d_derived = df_ccaa[df_ccaa["any"] == any_sel].copy()
if "xifra_negoci" in d_derived.columns and "personal_ocupat" in d_derived.columns:
    d_derived["prod_xn_ocupat"] = d_derived["xifra_negoci"] / d_derived["personal_ocupat"]

    st.subheader(f"{t('eee_ccaa_prod')} ({int(any_sel)})")
    d_prod = d_derived.dropna(subset=["prod_xn_ocupat"]).sort_values("prod_xn_ocupat", ascending=True)

    fig_prod = go.Figure()
    fig_prod.add_trace(go.Bar(
        y=d_prod["territori"], x=d_prod["prod_xn_ocupat"] / 1000,
        orientation="h", marker_color=PURPLE_LIGHT,
        text=[f"{fnum(v/1000, 1)} k" for v in d_prod["prod_xn_ocupat"]],
        textposition="outside", textfont=dict(size=11),
    ))

    esp_row = df_esp[df_esp["any"] == any_sel]
    if not esp_row.empty and "xifra_negoci" in esp_row.columns:
        esp_p = esp_row["xifra_negoci"].values[0] / esp_row["personal_ocupat"].values[0]
        fig_prod.add_vline(
            x=esp_p / 1000, line_dash="dash", line_color=RED, line_width=2,
            annotation_text=f"{'Espanya' if _ca else 'España'}: {fnum(esp_p/1000, 1)} k",
            annotation_position="top right",
        )

    apply_layout(fig_prod,
        xaxis_title=("Milers EUR / ocupat" if _ca else "Miles EUR / ocupado"),
        height=max(450, len(d_prod) * 32 + 100),
        margin=dict(l=200, r=100, t=50, b=50),
    )
    st.plotly_chart(fig_prod, use_container_width=True)
    source("INE, Enquesta Estructural d'Empreses. Càlcul propi" if _ca
           else "INE, Encuesta Estructural de Empresas. Cálculo propio")

# ─── Salari mitjà per CCAA ───────────────────────────────────

if "sous_salaris" in d_derived.columns and "personal_ocupat" in d_derived.columns:
    d_derived["sal_med"] = d_derived["sous_salaris"] / d_derived["personal_ocupat"]

    st.subheader(f"{t('eee_ccaa_sal_med')} ({int(any_sel)})")
    d_sal = d_derived.dropna(subset=["sal_med"]).sort_values("sal_med", ascending=True)

    fig_sal = go.Figure()
    fig_sal.add_trace(go.Bar(
        y=d_sal["territori"], x=d_sal["sal_med"],
        orientation="h", marker_color=PURPLE_LIGHT,
        text=[f"{fnum(v)} EUR" for v in d_sal["sal_med"]],
        textposition="outside", textfont=dict(size=11),
    ))

    esp_s = df_esp[df_esp["any"] == any_sel]
    if not esp_s.empty and "sous_salaris" in esp_s.columns:
        sal_esp = esp_s["sous_salaris"].values[0] / esp_s["personal_ocupat"].values[0]
        fig_sal.add_vline(
            x=sal_esp, line_dash="dash", line_color=RED, line_width=2,
            annotation_text=f"{'Espanya' if _ca else 'España'}: {fnum(sal_esp)} EUR",
            annotation_position="top right",
        )

    apply_layout(fig_sal,
        xaxis_title="EUR / ocupat" if _ca else "EUR / ocupado",
        height=max(450, len(d_sal) * 32 + 100),
        margin=dict(l=200, r=100, t=50, b=50),
    )
    st.plotly_chart(fig_sal, use_container_width=True)
    source("INE, Enquesta Estructural d'Empreses. Càlcul propi" if _ca
           else "INE, Encuesta Estructural de Empresas. Cálculo propio")

# ─── Insight ─────────────────────────────────────────────────

if "pes_cnae47_pib" in df_ccaa.columns:
    _ins_yr = max(anys)
    d_ins = df_ccaa[df_ccaa["any"] == _ins_yr].dropna(subset=["pes_cnae47_pib"])
    if d_ins.empty:
        _ins_yr = max(anys) - 1
        d_ins = df_ccaa[df_ccaa["any"] == _ins_yr].dropna(subset=["pes_cnae47_pib"])
    if not d_ins.empty:
        top2 = d_ins.nlargest(2, "pes_cnae47_pib")
        bot2 = d_ins.nsmallest(2, "pes_cnae47_pib")
        top_names = f"{top2.iloc[0]['territori']} ({fpct(top2.iloc[0]['pes_cnae47_pib']*100, 2, sign=False)})"
        top_names += f" i {top2.iloc[1]['territori']} ({fpct(top2.iloc[1]['pes_cnae47_pib']*100, 2, sign=False)})" if _ca \
            else f" y {top2.iloc[1]['territori']} ({fpct(top2.iloc[1]['pes_cnae47_pib']*100, 2, sign=False)})"
        bot_names = f"{bot2.iloc[0]['territori']} ({fpct(bot2.iloc[0]['pes_cnae47_pib']*100, 2, sign=False)})"
        bot_names += f" i {bot2.iloc[1]['territori']} ({fpct(bot2.iloc[1]['pes_cnae47_pib']*100, 2, sign=False)})" if _ca \
            else f" y {bot2.iloc[1]['territori']} ({fpct(bot2.iloc[1]['pes_cnae47_pib']*100, 2, sign=False)})"
        spread = (top2.iloc[0]["pes_cnae47_pib"] - bot2.iloc[0]["pes_cnae47_pib"]) * 100

        esp_ins = df_esp[df_esp["any"] == _ins_yr]
        esp_txt = ""
        if not esp_ins.empty and pd.notna(esp_ins.iloc[0].get("pes_cnae47_pib")):
            esp_txt = fpct(esp_ins.iloc[0]["pes_cnae47_pib"] * 100, 2, sign=False)

        if _ca:
            insight(
                f"El pes del comerc al detall sobre el PIB varia significativament entre CCAA ({int(_ins_yr)}). "
                f"Les comunitats on mes pesa son <strong>{top_names}</strong>, "
                f"amb economies orientades al consum i al turisme. "
                f"A l'extrem oposat, <strong>{bot_names}</strong> tenen economies mes industrials o de serveis avancats. "
                f"La diferencia entre la CCAA amb mes pes i la que menys en te es de "
                f"<strong>{fpct(spread, 1, sign=False)} punts</strong>"
                + (f", amb una mitjana nacional del <strong>{esp_txt}</strong>." if esp_txt else ".")
            )
        else:
            insight(
                f"El peso del comercio minorista sobre el PIB varia significativamente entre CCAA ({int(_ins_yr)}). "
                f"Las comunidades donde mas pesa son <strong>{top_names}</strong>, "
                f"con economias orientadas al consumo y al turismo. "
                f"En el extremo opuesto, <strong>{bot_names}</strong> tienen economias mas industriales o de servicios avanzados. "
                f"La diferencia entre la CCAA con mas peso y la que menos es de "
                f"<strong>{fpct(spread, 1, sign=False)} puntos</strong>"
                + (f", con una media nacional del <strong>{esp_txt}</strong>." if esp_txt else ".")
            )

# ─── Taula ────────────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_eee, use_container_width=True)
    st.download_button("CSV", df_eee.to_csv(index=False).encode("utf-8"),
                       "territori_cnae47.csv", "text/csv")

page_meta("INE + Eurostat. Estimacio hibrida propia" if _ca
          else "INE + Eurostat. Estimacion hibrida propia", st.session_state.lang)

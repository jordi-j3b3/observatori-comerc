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
        "La Comptabilitat Regional de l'INE no desglossa el CNAE 47 per comunitats autònomes. "
        "Per obtenir una visió territorial, apliquem la <strong>ràtio nacional VAB/xifra de negoci</strong> "
        "(de l'Enquesta Estructural d'Empreses) a la xifra de negoci declarada per cada CCAA. "
        "Això ens permet estimar el VAB regional i comparar <strong>productivitat</strong>, "
        "<strong>sous</strong> i <strong>estructura comercial</strong> entre territoris."
    )
else:
    intro(
        "La Contabilidad Regional del INE no desglosa el CNAE 47 por comunidades autónomas. "
        "Para obtener una visión territorial, aplicamos la <strong>ratio nacional VAB/cifra de negocio</strong> "
        "(de la Encuesta Estructural de Empresas) a la cifra de negocio declarada por cada CCAA. "
        "Esto nos permite estimar el VAB regional y comparar <strong>productividad</strong>, "
        "<strong>sueldos</strong> y <strong>estructura comercial</strong> entre territorios."
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
anys = sorted(df_ccaa["any"].dropna().unique())

# ─── Selector d'any ──────────────────────────────────────────

any_sel = st.select_slider(
    t("emp_ccaa_year"),
    options=anys,
    value=max(anys),
)

# ─── KPIs ────────────────────────────────────────────────────

d_yr_esp = df_esp[df_esp["any"] == any_sel]
if not d_yr_esp.empty:
    row = d_yr_esp.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    if "vab_estimat" in row and pd.notna(row.get("vab_estimat")):
        c1.metric("VAB real (M EUR)", fnum(row["vab_estimat"] / 1e6))
    if "xifra_negoci" in row and pd.notna(row.get("xifra_negoci")):
        c2.metric(t("eee_ccaa_xn") + " (M EUR)", fnum(row["xifra_negoci"] / 1e6))
    if "personal_ocupat" in row and pd.notna(row.get("personal_ocupat")):
        c3.metric(t("eee_ccaa_personal"), fnum(row["personal_ocupat"]))
    if "locals" in row and pd.notna(row.get("locals")):
        c4.metric("Locals" if _ca else "Locales", fnum(row["locals"]))

# ─── Rànquing per magnitud ───────────────────────────────────

st.subheader(t("eee_ccaa_title"))

METRICS = {
    "vab_estimat": (t("eee_ccaa_vab"), "M EUR"),
    "xifra_negoci": (t("eee_ccaa_xn"), "M EUR"),
    "personal_ocupat": (t("eee_ccaa_personal"), ""),
    "sous_salaris": (t("eee_ccaa_sous"), "M EUR"),
}

available = {k: v for k, v in METRICS.items() if k in df_ccaa.columns}
sel_metric = st.radio(
    t("eee_ccaa_metric"),
    list(available.keys()),
    format_func=lambda x: available[x][0],
    horizontal=True,
)

d_yr = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=[sel_metric]).copy()

if not d_yr.empty:
    d_yr = d_yr.sort_values(sel_metric, ascending=True)
    lbl, unit = available[sel_metric]

    if unit == "M EUR":
        d_yr["_display"] = d_yr[sel_metric] / 1e6
        txt_vals = [f"{fnum(v / 1e6)} M" for v in d_yr[sel_metric]]
        ax_title = f"{lbl} (M EUR)"
    else:
        d_yr["_display"] = d_yr[sel_metric]
        txt_vals = [fnum(v) for v in d_yr[sel_metric]]
        ax_title = lbl

    fig_rank = go.Figure()
    fig_rank.add_trace(go.Bar(
        y=d_yr["territori"], x=d_yr["_display"],
        orientation="h",
        marker_color=PURPLE_LIGHT,
        text=txt_vals,
        textposition="outside",
        textfont=dict(size=11),
    ))

    esp_val = df_esp[df_esp["any"] == any_sel][sel_metric].values
    if len(esp_val) > 0 and len(d_yr) > 0:
        avg_val = esp_val[0] / len(d_yr)
        if unit == "M EUR":
            avg_disp = avg_val / 1e6
            avg_txt = f"{'Mitjana' if _ca else 'Media'}: {fnum(avg_val / 1e6)} M"
        else:
            avg_disp = avg_val
            avg_txt = f"{'Mitjana' if _ca else 'Media'}: {fnum(avg_val)}"
        fig_rank.add_vline(
            x=avg_disp, line_dash="dash", line_color=RED, line_width=2,
            annotation_text=avg_txt, annotation_position="top right",
        )

    apply_layout(fig_rank,
        title=f"{lbl} ({int(any_sel)})",
        xaxis_title=ax_title,
        height=max(450, len(d_yr) * 32 + 100),
        margin=dict(l=200, r=120, t=50, b=50),
    )
    st.plotly_chart(fig_rank, use_container_width=True)
    source("INE, Enquesta Estructural d'Empreses. Càlcul propi" if _ca
           else "INE, Encuesta Estructural de Empresas. Cálculo propio")

# ─── Mapa VAB estimat ────────────────────────────────────────

if "vab_estimat" in df_ccaa.columns:
    lbl_mapa = ("Distribució territorial del VAB del comerç al detall" if _ca
                else "Distribución territorial del VAB del comercio minorista")
    st.subheader(f"{lbl_mapa} ({int(any_sel)})")
    d_map = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["vab_estimat"]).copy()
    d_map["vab_meur"] = d_map["vab_estimat"] / 1e6

    if not d_map.empty:
        zmin_v = df_ccaa["vab_estimat"].min() / 1e6
        zmax_v = df_ccaa["vab_estimat"].max() / 1e6

        fig_map = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=d_map["territori"],
            featureidkey="properties.territori",
            z=d_map["vab_meur"],
            zmin=zmin_v, zmax=zmax_v,
            colorscale=[
                [0, "#e8f0fe"], [0.15, "#a8c8e8"], [0.35, "#5a9fd4"],
                [0.55, "#0055a4"], [0.75, "#003d7a"], [1, "#001d3d"],
            ],
            colorbar=dict(title="M EUR", thickness=15),
            marker=dict(line=dict(width=1.5, color="white")),
            text=d_map["territori"],
            hovertemplate="<b>%{text}</b><br>VAB: %{z:,.0f} M EUR<extra></extra>",
        ))
        fig_map.update_layout(
            map=dict(style="white-bg", center=dict(lat=39.5, lon=-3.5), zoom=4.8),
            height=700, margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        source("INE, Enquesta Estructural d'Empreses. Càlcul propi" if _ca
               else "INE, Encuesta Estructural de Empresas. Cálculo propio")

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

if "vab_estimat" in df_ccaa.columns:
    d_last = df_ccaa[df_ccaa["any"] == max(anys)].dropna(subset=["vab_estimat"])
    if not d_last.empty:
        top3 = d_last.nlargest(3, "vab_estimat")
        top_names = ", ".join(top3["territori"].values[:2]) + f" {'i' if _ca else 'y'} " + top3["territori"].values[2]
        top_pct = top3["vab_estimat"].sum() / d_last["vab_estimat"].sum() * 100
        if _ca:
            insight(
                f"Les tres CCAA amb més VAB estimat del CNAE 47 ({int(max(anys))}) són "
                f"<strong>{top_names}</strong>, que concentren el <strong>{fpct(top_pct, 1, sign=False)}</strong> "
                f"del total. "
                f"Les diferències en productivitat per ocupat i salari mitjà entre comunitats reflecteixen "
                f"l'heterogeneïtat del sector: cost de vida, estructura comercial (gran superfície vs. petit comerç) "
                f"i especialització territorial condicionen els resultats."
            )
        else:
            insight(
                f"Las tres CCAA con mayor VAB estimado del CNAE 47 ({int(max(anys))}) son "
                f"<strong>{top_names}</strong>, que concentran el <strong>{fpct(top_pct, 1, sign=False)}</strong> "
                f"del total. "
                f"Las diferencias en productividad por ocupado y salario medio entre comunidades reflejan "
                f"la heterogeneidad del sector: coste de vida, estructura comercial (gran superficie vs. pequeño comercio) "
                f"y especialización territorial condicionan los resultados."
            )

# ─── Taula ────────────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_eee, use_container_width=True)
    st.download_button("CSV", df_eee.to_csv(index=False).encode("utf-8"),
                       "territori_cnae47.csv", "text/csv")

page_meta("INE, Enquesta Estructural d'Empreses" if _ca
          else "INE, Encuesta Estructural de Empresas", st.session_state.lang)

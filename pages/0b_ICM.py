"""Pols mensual del comerç al detall espanyol (ICM, INE).

Sèrie mensual oficial de l'INE — Índices de Comercio al por Menor:
cifra de negoci a preus constants i corrents + ocupació, per branca
CNAE 47 i per Comunitat Autònoma. Base 2021=100.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source,
                   page_meta, fnum, fpct, apply_layout, highlight_expander,
                   PURPLE, RED, GREEN, GRAY_DARK, YELLOW, PALETTE)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"


@st.cache_data(ttl=3600)
def load_icm():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "icm.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df.dropna(subset=["data"])


df = load_icm()

st.title("Pols mensual del comerç" if _ca else "Pulso mensual del comercio")

if _ca:
    intro(
        "L'ICM (Índices de Comercio al por Menor) és la sèrie oficial mensual "
        "de l'INE que recull la <strong>cifra de negoci</strong> i "
        "l'<strong>ocupació</strong> del comerç al detall espanyol, en valors "
        "índex base 2021=100. Permet seguir el cicle del consum amb retard "
        "de ~45 dies. Aquesta pàgina mostra Espanya, branques principals i "
        "Comunitats Autònomes."
    )
else:
    intro(
        "El ICM (Índices de Comercio al por Menor) es la serie oficial mensual "
        "del INE que recoge la <strong>cifra de negocio</strong> y el "
        "<strong>empleo</strong> del comercio minorista español, en valores "
        "índice base 2021=100. Permite seguir el ciclo del consumo con retraso "
        "de ~45 días. Esta página muestra España, ramas principales y "
        "Comunidades Autónomas."
    )

if df.empty:
    st.warning(
        "No hi ha dades ICM disponibles. Executa el processador."
        if _ca else
        "No hay datos ICM disponibles. Ejecuta el procesador."
    )
    st.stop()

# Branca general CNAE 47 estricta (sense vehicles)
BRANCA_GENERAL_47 = "Comercio al por menor, excepto de vehículos de motor y motocicletas"
# Branca neta (sense estacions de servei)
BRANCA_NETA = "Comercio al por menor sin Estaciones de Servicio (47 sin 473)"

# Mapping codis CNAE → etiqueta editorial
BRANCA_LBL_CA = {
    BRANCA_GENERAL_47: "General CNAE 47",
    BRANCA_NETA: "Sense benzineres (47 sense 473)",
    "Alimentación (4711+472)": "Alimentació",
    "Resto (sin Alim. ni Est. Serv.)": "Resta (no alim., no benzineres)",
    "Equipo personal (4771+4772)": "Equipament personal",
    "Equipo del hogar": "Equipament de la llar",
    "Equipamiento del hogar (475)": "Equipament de la llar (475)",
    "Otros bienes para uso doméstico (475)": "Altres béns ús domèstic",
    "Comercio al por menor de combustible para la automoción en establecimientos especializados": "Estacions de servei",
    "Salud (4773+4774+4775)": "Salut i cura personal",
    "Establecimientos no especializados (471)": "Establiments no especialitzats (471)",
}
BRANCA_LBL_ES = {
    BRANCA_GENERAL_47: "General CNAE 47",
    BRANCA_NETA: "Sin gasolineras (47 sin 473)",
    "Alimentación (4711+472)": "Alimentación",
    "Resto (sin Alim. ni Est. Serv.)": "Resto (no alim., no gasolineras)",
    "Equipo personal (4771+4772)": "Equipo personal",
    "Equipo del hogar": "Equipo del hogar",
    "Equipamiento del hogar (475)": "Equipamiento del hogar (475)",
    "Otros bienes para uso doméstico (475)": "Otros bienes uso doméstico",
    "Comercio al por menor de combustible para la automoción en establecimientos especializados": "Estaciones de servicio",
    "Salud (4773+4774+4775)": "Salud y cuidado personal",
    "Establecimientos no especializados (471)": "Establecimientos no especializados (471)",
}
BRANCA_LBL = BRANCA_LBL_CA if _ca else BRANCA_LBL_ES

# ─── KPIs nacionals ────────────────────────────────────────────

df_nac_real = df[(df["ambit"] == "nacional") &
                 (df["tipus"] == "real") &
                 (df["branca"] == BRANCA_GENERAL_47)]
df_nac_nom = df[(df["ambit"] == "nacional") &
                (df["tipus"] == "nominal") &
                (df["branca"] == BRANCA_NETA)]
df_nac_ocu = df[(df["ambit"] == "nacional") &
                (df["tipus"] == "ocupacio") &
                (df["branca"] == BRANCA_GENERAL_47)]

# Última dada del general real (índex + variació anual)
_last_real_idx = df_nac_real[df_nac_real["indicador"] == "index"].sort_values("data")
_last_real_var = df_nac_real[df_nac_real["indicador"] == "var_anual"].sort_values("data")
_last_nom_var = df_nac_nom[df_nac_nom["indicador"] == "var_anual"].sort_values("data")
_last_ocu_var = df_nac_ocu[df_nac_ocu["indicador"] == "var_anual"].sort_values("data")

if not _last_real_idx.empty:
    last_data = _last_real_idx.iloc[-1]["data"]
    st.caption(
        ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
        + last_data.strftime("%B %Y").capitalize()
    )

c1, c2, c3, c4 = st.columns(4)
with c1:
    if not _last_real_idx.empty:
        val = _last_real_idx.iloc[-1]["valor"]
        st.metric(
            ("Índex real (base 2021)" if _ca else "Índice real (base 2021)"),
            f"{fnum(val, 1)}",
        )
with c2:
    if not _last_real_var.empty:
        val = _last_real_var.iloc[-1]["valor"]
        st.metric(
            ("Variació anual (real)" if _ca else "Variación anual (real)"),
            fpct(val, 1),
        )
with c3:
    if not _last_nom_var.empty:
        val = _last_nom_var.iloc[-1]["valor"]
        st.metric(
            ("Variació anual (nominal)" if _ca else "Variación anual (nominal)"),
            fpct(val, 1),
        )
with c4:
    if not _last_ocu_var.empty:
        val = _last_ocu_var.iloc[-1]["valor"]
        st.metric(
            ("Variació ocupació" if _ca else "Variación empleo"),
            fpct(val, 1),
        )

# ─── 1. Evolució nacional ─────────────────────────────────────

st.header("1. " + ("Evolució nacional" if _ca else "Evolución nacional"))

periodes = {
    ("12 mesos" if _ca else "12 meses"): 12,
    ("24 mesos" if _ca else "24 meses"): 24,
    ("60 mesos" if _ca else "60 meses"): 60,
    ("Des de 2020" if _ca else "Desde 2020"): 999,
}
per_lbl = st.radio(
    ("Període" if _ca else "Período"),
    list(periodes.keys()), index=1, horizontal=True, key="icm_per",
)
per_n = periodes[per_lbl]

df_serie_real = df_nac_real[df_nac_real["indicador"] == "var_anual"].sort_values("data")
df_serie_nom = df[(df["ambit"] == "nacional") & (df["tipus"] == "nominal") &
                  (df["branca"] == BRANCA_NETA) &
                  (df["indicador"] == "var_anual")].sort_values("data")

if per_n < 999:
    df_serie_real = df_serie_real.tail(per_n)
    df_serie_nom = df_serie_nom.tail(per_n)
else:
    df_serie_real = df_serie_real[df_serie_real["data"] >= "2020-01-01"]
    df_serie_nom = df_serie_nom[df_serie_nom["data"] >= "2020-01-01"]

fig_evo = go.Figure()
fig_evo.add_trace(go.Scatter(
    x=df_serie_real["data"], y=df_serie_real["valor"],
    mode="lines+markers",
    name=("Real (preus constants)" if _ca else "Real (precios constantes)"),
    line=dict(color=PURPLE, width=2.6),
    marker=dict(size=5),
    hovertemplate="%{x|%b %Y}: <b>%{y:+.1f}%</b><extra></extra>",
))
fig_evo.add_trace(go.Scatter(
    x=df_serie_nom["data"], y=df_serie_nom["valor"],
    mode="lines+markers",
    name=("Nominal (preus corrents)" if _ca else "Nominal (precios corrientes)"),
    line=dict(color=GRAY_DARK, width=2, dash="dot"),
    marker=dict(size=4),
    hovertemplate="%{x|%b %Y}: <b>%{y:+.1f}%</b><extra></extra>",
))
fig_evo.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
apply_layout(fig_evo,
    yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
    height=420,
)
st.plotly_chart(fig_evo, use_container_width=True)
source("INE, Índices de Comercio al por Menor (ICM). Sense estacions de servei (47 sense 473)"
       if _ca else
       "INE, Índices de Comercio al por Menor (ICM). Sin estaciones de servicio (47 sin 473)")

# Insight evolució
if not df_serie_real.empty and len(df_serie_real) >= 2:
    _last_v = float(df_serie_real.iloc[-1]["valor"])
    _last_dt = df_serie_real.iloc[-1]["data"]
    _avg_12 = df_nac_real[df_nac_real["indicador"] == "var_anual"]["valor"].tail(12).mean()
    _signe = "creix" if _last_v > 0 else ("cau" if _last_v < 0 else "s'estabilitza")
    if _ca:
        insight(
            f"Al <strong>{_last_dt.strftime('%B %Y').capitalize()}</strong>, la cifra de negoci real "
            f"del comerç al detall espanyol <strong>{_signe} un {abs(_last_v):.1f}%</strong> respecte "
            f"al mateix mes de l'any anterior. En els darrers 12 mesos, la variació anual mitjana s'ha "
            f"situat al <strong>{_avg_12:+.1f}%</strong>. "
            f"La diferència entre nominal i real és l'efecte preu: si el nominal creix més que el real, "
            f"part del creixement és simplement inflació."
        )
    else:
        _signe_es = "crece" if _last_v > 0 else ("cae" if _last_v < 0 else "se estabiliza")
        insight(
            f"En <strong>{_last_dt.strftime('%B %Y').capitalize()}</strong>, la cifra de negocio real "
            f"del comercio minorista español <strong>{_signe_es} un {abs(_last_v):.1f}%</strong> "
            f"respecto al mismo mes del año anterior. En los últimos 12 meses, la variación anual "
            f"media se ha situado en el <strong>{_avg_12:+.1f}%</strong>. "
            f"La diferencia entre nominal y real es el efecto precio: si el nominal crece más que "
            f"el real, parte del crecimiento es simplemente inflación."
        )

# ─── 2. Variació per branca ───────────────────────────────────

st.header("2. " + ("Variació anual per branca" if _ca else "Variación anual por rama"))

# Última data disponible amb dades de branques
_last_dt = df_nac_real["data"].max()
df_branca = df[(df["ambit"] == "nacional") &
               (df["tipus"] == "real") &
               (df["indicador"] == "var_anual") &
               (df["data"] == _last_dt)].copy()

# Excloure les variants "Comercio al por menor sin Estaciones..." amb sub-variants
df_branca = df_branca[~df_branca["branca"].str.contains("General", na=False, regex=False)]
df_branca["label"] = df_branca["branca"].map(BRANCA_LBL).fillna(df_branca["branca"])
df_branca = df_branca.drop_duplicates(subset=["branca"]).sort_values("valor", ascending=True)

if not df_branca.empty:
    colors_br = [GREEN if v >= 0 else RED for v in df_branca["valor"]]
    fig_br = go.Figure()
    fig_br.add_trace(go.Bar(
        y=df_branca["label"], x=df_branca["valor"],
        orientation="h",
        marker_color=colors_br,
        text=[fpct(v, 1) for v in df_branca["valor"]],
        textposition="outside",
        textfont=dict(size=11),
        name="",
        hovertemplate="<b>%{y}</b>: %{x:+.1f}%<extra></extra>",
    ))
    fig_br.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    apply_layout(fig_br,
        xaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
        height=max(380, len(df_branca) * 32 + 100),
        margin=dict(l=240, r=80, t=30, b=50),
    )
    st.plotly_chart(fig_br, use_container_width=True)
    source(f"INE, ICM. Cifra de negoci a preus constants — {_last_dt.strftime('%B %Y').capitalize()}"
           if _ca else
           f"INE, ICM. Cifra de negocio a precios constantes — {_last_dt.strftime('%B %Y').capitalize()}")

# ─── 3. Per CCAA ──────────────────────────────────────────────

st.header("3. " + ("Variació anual per CCAA" if _ca else "Variación anual por CCAA"))

df_ccaa = df[(df["ambit"] != "nacional") &
             (df["tipus"] == "real") &
             (df["indicador"] == "var_anual") &
             (df["data"] == _last_dt)].copy()
df_ccaa = df_ccaa.drop_duplicates(subset=["ambit"]).sort_values("valor", ascending=True)

if not df_ccaa.empty:
    colors_cc = [GREEN if v >= 0 else RED for v in df_ccaa["valor"]]
    fig_cc = go.Figure()
    fig_cc.add_trace(go.Bar(
        y=df_ccaa["ambit"], x=df_ccaa["valor"],
        orientation="h",
        marker_color=colors_cc,
        text=[fpct(v, 1) for v in df_ccaa["valor"]],
        textposition="outside",
        textfont=dict(size=11),
        name="",
        hovertemplate="<b>%{y}</b>: %{x:+.1f}%<extra></extra>",
    ))
    fig_cc.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    apply_layout(fig_cc,
        xaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
        height=max(450, len(df_ccaa) * 30 + 100),
        margin=dict(l=200, r=80, t=30, b=50),
    )
    st.plotly_chart(fig_cc, use_container_width=True)
    source(f"INE, ICM per CCAA. Cifra de negoci a preus constants — {_last_dt.strftime('%B %Y').capitalize()}"
           if _ca else
           f"INE, ICM por CCAA. Cifra de negocio a precios constantes — {_last_dt.strftime('%B %Y').capitalize()}")

# ─── Expander: evolució ocupació ──────────────────────────────

_lbl_ocu_exp = ("Veure evolució de l'ocupació mensual"
                if _ca else
                "Ver evolución del empleo mensual")
with highlight_expander(_lbl_ocu_exp, expanded=False):
    df_ocu_serie = df_nac_ocu[df_nac_ocu["indicador"] == "var_anual"].sort_values("data")
    if per_n < 999:
        df_ocu_serie = df_ocu_serie.tail(per_n)
    else:
        df_ocu_serie = df_ocu_serie[df_ocu_serie["data"] >= "2020-01-01"]

    fig_ocu = go.Figure()
    fig_ocu.add_trace(go.Scatter(
        x=df_ocu_serie["data"], y=df_ocu_serie["valor"],
        mode="lines+markers",
        line=dict(color=PURPLE, width=2.6),
        marker=dict(size=5),
        name="",
        hovertemplate="%{x|%b %Y}: <b>%{y:+.1f}%</b><extra></extra>",
    ))
    fig_ocu.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
    apply_layout(fig_ocu,
        yaxis_title=("Variació anual ocupats (%)" if _ca else "Variación anual ocupados (%)"),
        height=380,
    )
    st.plotly_chart(fig_ocu, use_container_width=True)
    source("INE, ICM ocupació mensual" if _ca else "INE, ICM empleo mensual")

page_meta("INE, Índices de Comercio al por Menor (ICM)", st.session_state.lang)

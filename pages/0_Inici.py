"""Pàgina d'inici: KPIs i resum de l'Observatori."""
import streamlit as st
import pandas as pd
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, fnum, fpct, page_meta

inject_css()
t = setup_lang(show_selector=False)

# ─── DADES ─────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data(name):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df_pib = load_data("pib_vab")
df_empreses = load_data("empreses")
df_prod = load_data("productivitat")

# ─── HEADER ────────────────────────────────────────────────────

st.markdown("""
<div class="j3b3-header">
    <img src="https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg" alt="J3B3 Consulting">
    <span class="j3b3-badge">OBSERVATORI</span>
</div>
""", unsafe_allow_html=True)
st.title(t("app_title"))
st.markdown(f"*{t('app_subtitle')}*")

# ─── KPIs ──────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_pib.empty and "vab_cnae47_corrents" in df_pib.columns:
        rows = df_pib.dropna(subset=["vab_cnae47_corrents"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["vab_cnae47_corrents"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["vab_cnae47_corrents"]) - 1) * 100)
        st.metric(t("kpi_pib"), f"{fnum(val)} {t('kpi_meur')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_pib"), "—")

with col2:
    if not df_empreses.empty:
        esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if not esp.empty:
            last = esp.iloc[-1]
            val = int(last["empreses"])
            any_ = int(last["any"])
            if len(esp) > 1:
                prev = esp.iloc[-2]
                any_prev = int(prev["any"])
                delta = fpct(((val / int(prev["empreses"])) - 1) * 100)
                st.metric(t("kpi_empreses"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
            else:
                st.metric(t("kpi_empreses"), fnum(val), help=f"{any_}")
    else:
        st.metric(t("kpi_empreses"), "—")

with col3:
    if not df_prod.empty and "personal_ocupat" in df_prod.columns:
        rows = df_prod.dropna(subset=["personal_ocupat"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["personal_ocupat"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["personal_ocupat"]) - 1) * 100)
        st.metric(t("kpi_ocupacio"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_ocupacio"), "—")

with col4:
    if not df_prod.empty and "productivitat_va_hora" in df_prod.columns:
        rows = df_prod.dropna(subset=["productivitat_va_hora"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["productivitat_va_hora"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["productivitat_va_hora"]) - 1) * 100)
        st.metric(t("kpi_productivitat"), f"{fnum(val, 1)} {t('kpi_eur_h')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_productivitat"), "—")

# ─── RESUM ─────────────────────────────────────────────────────

st.divider()

if st.session_state.lang == "ca":
    st.markdown("""
    ### Sobre l'Observatori

    Aquest observatori monitoritza l'evolució del **comerç al detall** (CNAE 47) a Espanya,
    analitzant la seva contribució al PIB, el teixit empresarial, l'ocupació,
    la productivitat, el comerç electrònic i la posició relativa a Europa.

    **Fonts de dades:** INE, Eurostat, CNMC

    **Actualització:** Trimestral automàtica (gener, abril, juliol, octubre)

    Navega per les seccions del menú lateral per explorar cada dimensió.
    """)
else:
    st.markdown("""
    ### Sobre el Observatorio

    Este observatorio monitoriza la evolución del **comercio minorista** (CNAE 47) en España,
    analizando su contribución al PIB, el tejido empresarial, el empleo,
    la productividad, el comercio electrónico y la posición relativa en Europa.

    **Fuentes de datos:** INE, Eurostat, CNMC

    **Actualización:** Trimestral automática (enero, abril, julio, octubre)

    Navega por las secciones del menú lateral para explorar cada dimensión.
    """)

# ─── META ─────────────────────────────────────────────────────

page_meta("INE, Eurostat, CNMC", st.session_state.lang)

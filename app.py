"""
Observatori del Comerç Minorista a Espanya (CNAE 47)
Punt d'entrada: navegació SUPERIOR per pregunta del visitant
(Actualitat / El sector / Canal i concentració / El territori / Sobre).

No hi ha sidebar: la navegació va a dalt (st.navigation position="top") i les
utilitats que hi vivien s'han repartit — l'idioma, a la barra d'utilitats sota
la nav; el butlletí i els recursos, al peu global de page_meta().
"""
import os
import streamlit as st

st.set_page_config(
    page_title="Observatori Comerç",
    layout="wide",
)

# Logo nadiu de Streamlit: apareix a dalt de tot del sidebar, abans de la nav
st.logo(
    "https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg",
    link="https://www.j3b3.com",
    size="large",
)

from style import inject_css, setup_lang, render_lang_selector

inject_css()
t = setup_lang(show_selector=False)  # el selector es renderitza a la barra d'utilitats

_ca = st.session_state.lang == "ca"

# Pagines NOMES locals (no es publiquen al Streamlit Cloud).
# Per veure-les en local: `OBSERVATORI_LOCAL=1 streamlit run app.py`
LOCAL_ONLY = os.environ.get("OBSERVATORI_LOCAL", "0") == "1"

# ─── NAVEGACIÓ JERÀRQUICA AMB TÍTOLS TRADUÏTS ──────────────────

# Etiquetes de seccions (grups de la nav superior). Arquitectura per pregunta del
# visitant (2026-07-06): què passa ara · com és el sector · com canvia i qui
# domina · com se situa · sobre nosaltres.
SEC_HOME = "Inicio" if not _ca else "Inici"
SEC_ARA = "La actualidad" if not _ca else "L'actualitat"
SEC_SECTOR = "El sector"
SEC_CANAL = "Canal y concentración" if not _ca else "Canal i concentració"
SEC_TERRITORI = "El territorio" if not _ca else "El territori"
SEC_SOBRE = "Acerca" if not _ca else "Sobre"

# HOME
p_inici = st.Page(
    "pages/0_Inici.py",
    title=("Inici" if _ca else "Inicio"),
    default=True,
)

# POLS — Pols diari, Pols mensual i Pulso setmanal (editorial)
p_lecturas = st.Page(
    "pages/L_Editorial.py",
    title="Editorial",
)

# RADIOGRAFIA — sèries anuals estructurals
p_pols = st.Page(
    "pages/0a_Pols_diari.py",
    title=("Pols diari" if _ca else "Pulso diario"),
)
p_icm = st.Page(
    "pages/0b_ICM.py",
    title=("Pols mensual" if _ca else "Pulso mensual"),
)
p_pib = st.Page(
    "pages/1_PIB_i_VAB.py",
    title=("PIB i VAB" if _ca else "PIB y VAB"),
)
p_emp = st.Page(
    "pages/2_Empreses.py",
    title=("Empreses" if _ca else "Empresas"),
)
p_ocu = st.Page(
    "pages/3_Ocupació.py",
    title=("Ocupació" if _ca else "Empleo"),
)
p_prod = st.Page(
    "pages/4_Productivitat.py",
    title=("Productivitat" if _ca else "Productividad"),
)
p_ec = st.Page(
    "pages/5_Ecommerce.py",
    title=("Digitalització" if _ca else "Digitalización"),
)
p_estructura = st.Page(
    "pages/E_Estructura.py",
    title=("Trajectòria estructural" if _ca else "Trayectoria estructural"),
)
p_europa = st.Page(
    "pages/7_Comparativa_Europa.py",
    title=("Comparativa Europa" if _ca else "Comparativa Europa"),
)

# ANÀLISI
p_subs = st.Page(
    "pages/9_Subsectors.py",
    title=("Subsectors" if _ca else "Subsectores"),
)
p_terr = st.Page(
    "pages/6_Territori.py",
    title=("Territori" if _ca else "Territorio"),
)
p_lideres = st.Page(
    "pages/D_Lideres.py",
    title=("Líders del comerç" if _ca else "Líderes del comercio"),
)

# RECURSOS
p_metod = st.Page(
    "pages/8_Metodologia.py",
    title=("Metodologia" if _ca else "Metodología"),
)
p_premsa = st.Page(
    "pages/B_Premsa.py",
    title=("Recull de premsa" if _ca else "Resumen de prensa"),
)

# Construcció del diccionari de navegació
nav = {
    SEC_HOME: [p_inici],
    SEC_ARA: [p_pols, p_icm, p_lecturas, p_premsa],
    SEC_SECTOR: [p_pib, p_emp, p_ocu, p_prod, p_subs],
    SEC_CANAL: [p_ec, p_estructura, p_lideres],
    SEC_TERRITORI: [p_europa, p_terr],
    SEC_SOBRE: [p_metod],
}

# A_Municipis.py només es publica si OBSERVATORI_LOCAL=1.
# Es manté al disc però fora del routing per defecte.
if LOCAL_ONLY:
    p_municipis = st.Page(
        "pages/A_Municipis.py",
        title=("Municipis (local)" if _ca else "Municipios (local)"),
    )
    nav[SEC_TERRITORI].append(p_municipis)

# position="top": la navegació nativa va a la capçalera, amb un menú per grup.
# Sense sidebar: res no s'escriu a st.sidebar, així Streamlit no el mostra.
pg = st.navigation(nav, position="top")

# ─── BARRA D'UTILITATS (sota la nav, a totes les pàgines) ────────
# app.py és el marc: el que es rendaritza aquí surt sobre el contingut de la
# pàgina activa. Hi posem només l'idioma, alineat a la dreta.

# La identitat del web va aquí, no només al logo: qui entra per una pàgina
# interior ha de saber on és sense haver de deduir-ho.
_util_l, _util_r = st.columns([5, 1], vertical_alignment="center")
with _util_l:
    st.markdown(
        '<div class="site-id">'
        + ("<b>Observatori del Comerç Minorista</b> · CNAE 47 · Espanya "
           "<span class='by'>· una iniciativa de "
           "<a href='https://www.j3b3.com' target='_blank' rel='noopener'>"
           "J3B3 Consulting</a></span>" if _ca else
           "<b>Observatorio del Comercio Minorista</b> · CNAE 47 · España "
           "<span class='by'>· una iniciativa de "
           "<a href='https://www.j3b3.com' target='_blank' rel='noopener'>"
           "J3B3 Consulting</a></span>")
        + "</div>",
        unsafe_allow_html=True,
    )
with _util_r:
    render_lang_selector(collapsed=True)

pg.run()

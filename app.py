"""
Observatori del Comerç Minorista a Espanya (CNAE 47)
Punt d'entrada: navegació amb títols traduïts.
"""
import streamlit as st

st.set_page_config(
    page_title="Observatori Comerç",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from style import inject_css, setup_lang

inject_css()
t = setup_lang(show_selector=True)

_ca = st.session_state.lang == "ca"

# ─── NAVEGACIÓ AMB TÍTOLS TRADUÏTS ──────────────────────────────

pg = st.navigation([
    st.Page("pages/0_Inici.py",
            title="Inici" if _ca else "Inicio", icon="🏪", default=True),
    st.Page("pages/1_PIB_i_VAB.py",
            title="PIB i VAB" if _ca else "PIB y VAB", icon="📊"),
    st.Page("pages/2_Empreses.py",
            title="Empreses" if _ca else "Empresas", icon="🏢"),
    st.Page("pages/3_Ocupació.py",
            title="Ocupació" if _ca else "Empleo", icon="👥"),
    st.Page("pages/4_Productivitat.py",
            title="Productivitat" if _ca else "Productividad", icon="⚡"),
    st.Page("pages/5_Ecommerce.py",
            title="E-commerce", icon="🛒"),
    st.Page("pages/6_Europa.py",
            title="Europa", icon="🇪🇺"),
    st.Page("pages/7_Metodologia.py",
            title="Metodologia" if _ca else "Metodología", icon="📖"),
])

# ─── SIDEBAR BRANDING ───────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<img src="https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg" '
        'alt="J3B3 Consulting" style="width:160px; margin-bottom:0.5rem;">',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(t("footer"))

pg.run()

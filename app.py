"""
Observatori del Comerç Minorista a Espanya (CNAE 47)
Punt d'entrada: navegació amb títols traduïts.
"""
import os
import streamlit as st

st.set_page_config(
    page_title="Observatori Comerç",
    layout="wide",
    initial_sidebar_state="expanded",
)

from style import inject_css, setup_lang

inject_css()
t = setup_lang(show_selector=True)

_ca = st.session_state.lang == "ca"

# Pagines NOMES locals (no es publiquen al Streamlit Cloud).
# Per veure-les en local: `OBSERVATORI_LOCAL=1 streamlit run app.py`
LOCAL_ONLY = os.environ.get("OBSERVATORI_LOCAL", "0") == "1"

# ─── NAVEGACIÓ AMB TÍTOLS TRADUÏTS ──────────────────────────────

_pages = [
    st.Page("pages/0_Inici.py",
            title="Inici" if _ca else "Inicio", default=True),
    st.Page("pages/1_PIB_i_VAB.py",
            title="PIB i VAB" if _ca else "PIB y VAB"),
    st.Page("pages/2_Empreses.py",
            title="Empreses" if _ca else "Empresas"),
    st.Page("pages/3_Ocupació.py",
            title="Ocupació" if _ca else "Empleo"),
    st.Page("pages/4_Productivitat.py",
            title="Productivitat" if _ca else "Productividad"),
    st.Page("pages/5_Ecommerce.py",
            title="E-commerce"),
    st.Page("pages/6_Territori.py",
            title="Territori" if _ca else "Territorio"),
    st.Page("pages/7_Europa.py",
            title="Europa"),
    st.Page("pages/9_Subsectors.py",
            title="Subsectors" if _ca else "Subsectores"),
]

if LOCAL_ONLY:
    _pages.append(st.Page("pages/A_Municipis.py",
                          title="Municipis (local)" if _ca else "Municipios (local)"))

_pages.append(st.Page("pages/8_Metodologia.py",
                      title="Metodologia" if _ca else "Metodología"))

pg = st.navigation(_pages)

# ─── SIDEBAR BRANDING ───────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<a href="https://www.j3b3.com" target="_blank" rel="noopener">'
        '<img src="https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg" '
        'alt="J3B3 Consulting" style="width:160px; margin-bottom:0.5rem;"></a>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(t("footer"))

pg.run()

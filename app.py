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

# Logo nadiu de Streamlit: apareix a dalt de tot del sidebar, abans de la nav
st.logo(
    "https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg",
    link="https://www.j3b3.com",
    size="large",
)

from style import inject_css, setup_lang, newsletter_form

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
    st.divider()

    # Butlletí: expander en lloc de popover (millor llegibilitat, no es desplaça)
    _nl_label = "📧 Butlletí trimestral" if _ca else "📧 Boletín trimestral"
    with st.expander(_nl_label, expanded=False):
        newsletter_form(st.session_state.lang, compact=True)

    st.divider()

    # Secció Recursos
    _lbl_recursos = "Recursos" if _ca else "Recursos"
    _lbl_about = "Sobre l'observatori" if _ca else "Sobre el observatorio"
    _lbl_consulting = "J3B3 Consulting"
    _lbl_contact = "Contacte" if _ca else "Contacto"
    st.markdown(
        f"""
        <div style="font-family:'DM Sans',sans-serif; font-size:13px; line-height:1.7; padding:0 4px;">
            <div style="font-size:10px; font-weight:700; letter-spacing:1.5px;
                        text-transform:uppercase; color:#0055a4; margin-bottom:8px;">
                {_lbl_recursos}
            </div>
            <div><a href="https://www.j3b3.com/observatori-comerc" target="_blank"
                    rel="noopener" style="color:#333; text-decoration:none;">→ {_lbl_about}</a></div>
            <div><a href="https://www.j3b3.com" target="_blank"
                    rel="noopener" style="color:#333; text-decoration:none;">→ {_lbl_consulting}</a></div>
            <div><a href="mailto:info@j3b3.com" style="color:#333; text-decoration:none;">→ {_lbl_contact}: info@j3b3.com</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption(t("footer"))

pg.run()

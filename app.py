"""
Observatori del Comerç Minorista a Espanya (CNAE 47)
Punt d'entrada: navegació jeràrquica HOME / LECTURAS / RADIOGRAFIA / DETALL / RECURSOS.
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

# ─── NAVEGACIÓ JERÀRQUICA AMB TÍTOLS TRADUÏTS ──────────────────

# Etiquetes de seccions (capçaleres del sidebar)
SEC_HOME = "Inicio" if not _ca else "Inici"
SEC_LECTURAS = "Lecturas" if not _ca else "Lectures"
SEC_RADIO = "Radiografía" if not _ca else "Radiografia"
SEC_DETALL = "Detalle" if not _ca else "Detall"
SEC_RECURSOS = "Recursos"

# HOME
p_inici = st.Page(
    "pages/0_Inici.py",
    title=("Inici" if _ca else "Inicio"),
    default=True,
)

# LECTURAS (placeholder Fase 2)
p_lecturas = st.Page(
    "pages/L_Lecturas.py",
    title=("Pulso de la setmana" if _ca else "Pulso de la semana"),
)

# RADIOGRAFIA — comença amb Pols diari (conjuntural diari), segueixen sèries anuals
p_pols = st.Page(
    "pages/0a_Pols_diari.py",
    title=("Pols diari" if _ca else "Pulso diario"),
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
    title="E-commerce",
)
p_europa = st.Page(
    "pages/7_Comparativa_Europa.py",
    title=("Comparativa Europa" if _ca else "Comparativa Europa"),
)

# DETALL
p_subs = st.Page(
    "pages/9_Subsectors.py",
    title=("Subsectors" if _ca else "Subsectores"),
)
p_terr = st.Page(
    "pages/6_Territori.py",
    title=("Territori" if _ca else "Territorio"),
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
    SEC_LECTURAS: [p_lecturas],
    SEC_RADIO: [p_pib, p_emp, p_ocu, p_prod, p_ec, p_europa],
    SEC_DETALL: [p_subs, p_terr, p_pols],
    SEC_RECURSOS: [p_metod, p_premsa],
}

# A_Municipis.py només es publica si OBSERVATORI_LOCAL=1.
# Es manté al disc però fora del routing per defecte.
if LOCAL_ONLY:
    p_municipis = st.Page(
        "pages/A_Municipis.py",
        title=("Municipis (local)" if _ca else "Municipios (local)"),
    )
    nav[SEC_DETALL].append(p_municipis)

pg = st.navigation(nav)

# ─── SIDEBAR BRANDING ───────────────────────────────────────────

with st.sidebar:
    st.divider()

    # Butlletí: CTA tipogràfic dins el sidebar (sense embed MailerLite,
    # que forçava una caixa blanca lletja sobre el blau marí). El form
    # complet segueix a la home i a la pàgina Pulso.
    _nl_eyebrow = "Butlletí" if _ca else "Boletín"
    _nl_title = "Rep El Pulso cada dilluns" if _ca else "Recibe El Pulso cada lunes"
    _nl_desc = ("El Pulso setmanal + resum trimestral al teu correu. "
                "Subscriu-te des de la pàgina d'inici."
                if _ca else
                "El Pulso semanal + resumen trimestral en tu correo. "
                "Suscríbete desde la página de inicio.")
    st.markdown(
        f"""
        <div style="font-family:'Inter',sans-serif; padding:0 4px; color:#ffffff;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.78rem;
                        font-weight:700; text-transform:uppercase; color:#ffffff;
                        opacity:0.7; margin-bottom:10px;">
                {_nl_eyebrow}
            </div>
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:1.05rem;
                        font-weight:700; color:#ffffff; margin-bottom:8px;
                        line-height:1.2;
                        background: linear-gradient(180deg, transparent 0%, transparent 60%,
                                    rgba(245, 216, 0, 0.55) 60%, rgba(245, 216, 0, 0.55) 92%,
                                    transparent 92%);
                        display: inline;">
                {_nl_title}
            </div>
            <div style="font-size:12px; line-height:1.55; color:#ffffff; opacity:0.85;
                        margin: 10px 0 0 0;">
                {_nl_desc}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Secció Recursos (peu del sidebar)
    _lbl_recursos = "Recursos" if _ca else "Recursos"
    _lbl_about = "Sobre l'observatori" if _ca else "Sobre el observatorio"
    _lbl_consulting = "J3B3 Consulting"
    _lbl_contact = "Contacte" if _ca else "Contacto"
    st.markdown(
        f"""
        <div style="font-family:'Inter',sans-serif; font-size:13px; line-height:1.7; padding:0 4px; color:#ffffff;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.78rem;
                        font-weight:700; letter-spacing:0;
                        text-transform:uppercase; color:#ffffff; opacity:0.7;
                        margin-bottom:10px;">
                {_lbl_recursos}
            </div>
            <div><a href="https://www.j3b3.com/observatori-comerc" target="_blank"
                    rel="noopener" style="color:#ffffff; text-decoration:none;">→ {_lbl_about}</a></div>
            <div><a href="https://www.j3b3.com" target="_blank"
                    rel="noopener" style="color:#ffffff; text-decoration:none;">→ {_lbl_consulting}</a></div>
            <div><a href="mailto:info@j3b3.com" style="color:#ffffff; text-decoration:none;">→ {_lbl_contact}: info@j3b3.com</a></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption(t("footer"))

pg.run()

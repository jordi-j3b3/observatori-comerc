"""Placeholder de la secció LECTURAS — Pulso de la setmana (Fase 2)."""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header  # noqa: E402

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"

st.title("Pulso de la semana" if not _ca else "Pulso de la setmana")

st.info(
    ("Sección en construcción. El **Pulso de la semana** —análisis editorial breve "
     "del momento del consumo, con tesis signada y predicciones condicionadas— "
     "se publicará aquí a partir de junio de 2026.")
    if not _ca else
    ("Secció en construcció. El **Pulso de la setmana** —anàlisi editorial breu "
     "del moment del consum, amb tesi signada i prediccions condicionades— "
     "es publicarà aquí a partir de juny de 2026.")
)

st.caption(
    "Jordi Bacaria · J3B3 Consulting"
)

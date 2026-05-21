"""Pols trimestral: infografia narrativa del comerç al detall.
Incrusta l'HTML estàtic generat amb cura editorial cada trimestre."""
import os
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header, page_meta

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# Catàleg d'infografies trimestrals: nou arxiu = afegir entrada aquí.
# Estructura: (id_humà, fitxer html, alçada iframe en px)
TRIMESTRES = [
    ("Q1 2026", "infografia_q1_2026.html", 8800),
]


st.title("Pols trimestral" if _ca else "Pulso trimestral")

if _ca:
    st.markdown(
        "Infografia narrativa del comerç al detall espanyol amb cadència "
        "**trimestral**. Cada edició desenvolupa una tesi sobre l'estat "
        "estructural del sector amb gràfics dissenyats per a l'argument."
    )
else:
    st.markdown(
        "Infografía narrativa del comercio minorista español con cadencia "
        "**trimestral**. Cada edición desarrolla una tesis sobre el estado "
        "estructural del sector con gráficos diseñados para el argumento."
    )


# Selector si hi ha més d'una edició disponible
if len(TRIMESTRES) > 1:
    _opts = {label: (fname, h) for label, fname, h in TRIMESTRES}
    _sel = st.selectbox(
        "Edició" if _ca else "Edición",
        list(_opts.keys()),
        index=0,
    )
    _fname, _height = _opts[_sel]
else:
    _label, _fname, _height = TRIMESTRES[0]
    st.caption(f"Edició: {_label}" if _ca else f"Edición: {_label}")

_path = STATIC_DIR / _fname

if not _path.exists():
    st.error(
        f"No s'ha trobat la infografia: {_fname}"
        if _ca else
        f"No se ha encontrado la infografía: {_fname}"
    )
else:
    _html = _path.read_text(encoding="utf-8")
    components.html(_html, height=_height, scrolling=True)


page_meta("INE, Eurostat", st.session_state.lang)

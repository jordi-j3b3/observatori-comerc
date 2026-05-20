"""Pulso de la semana — arxiu cronològic mirall de la newsletter setmanal."""
import os
import re
import sys
from datetime import date
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header, newsletter_form  # noqa: E402

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"

NEWSLETTER_DIR = Path(__file__).resolve().parent.parent / "data" / "newsletter"

MESOS_CA = ["gener", "febrer", "març", "abril", "maig", "juny",
            "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def format_data(d: date) -> str:
    mesos = MESOS_CA if _ca else MESES_ES
    if _ca:
        return f"{d.day} de {mesos[d.month - 1]} de {d.year}"
    return f"{d.day} de {mesos[d.month - 1]} de {d.year}"


def strip_trazabilidad(md: str) -> str:
    """Elimina la secció TRAZABILIDAD (no se envía) i tot el que segueix."""
    marker = "### TRAZABILIDAD"
    idx = md.find(marker)
    if idx < 0:
        return md.rstrip()
    return md[:idx].rstrip()


def extract_meta(md: str) -> tuple[dict, str]:
    """Extreu Asunto / Pre-header / Titular i retorna metadata + body net.

    Strip també del primer '---' que separa les metadades del cos.
    """
    meta = {"asunto": None, "preheader": None, "titular": None}
    lines = md.split("\n")
    body_start = 0
    for i, raw in enumerate(lines):
        line = raw.strip()
        m = re.match(r"^\*\*(Asunto|Pre-header|Titular)\:\*\*\s*(.+)$", line)
        if m:
            key = m.group(1).lower().replace("-", "")
            if key == "preheader":
                meta["preheader"] = m.group(2).strip()
            elif key == "asunto":
                meta["asunto"] = m.group(2).strip()
            elif key == "titular":
                meta["titular"] = m.group(2).strip()
            body_start = i + 1
        elif line == "---" and body_start > 0:
            body_start = i + 1
            break
        elif line and body_start == 0:
            break
    body = "\n".join(lines[body_start:]).lstrip("\n")
    return meta, body


def load_issues() -> list[tuple[date, dict, str]]:
    """Retorna llista de (data, meta, body_net) ordenada del més recent al més antic."""
    if not NEWSLETTER_DIR.is_dir():
        return []
    issues: list[tuple[date, dict, str]] = []
    for path in sorted(NEWSLETTER_DIR.glob("semana-*.md"), reverse=True):
        m = re.match(r"semana-(\d{4})-(\d{2})-(\d{2})", path.stem)
        if not m:
            continue
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        raw = path.read_text(encoding="utf-8")
        meta, body = extract_meta(strip_trazabilidad(raw))
        issues.append((d, meta, body))
    return issues


# ─── PÀGINA ────────────────────────────────────────────────────

st.title("El Pulso de la setmana" if _ca else "El Pulso de la semana")

st.markdown(
    "*Cada dilluns, una mirada concisa al moment del consum minorista a Espanya i Europa: "
    "una xifra, tres notícies amb angle, dades comparades i una predicció signada. "
    "Aquí pots consultar l'arxiu cronològic complet, del més recent al més antic.*"
    if _ca else
    "*Cada lunes, una mirada concisa al momento del consumo minorista en España y Europa: "
    "una cifra, tres noticias con ángulo, datos comparados y una predicción firmada. "
    "Aquí puedes consultar el archivo cronológico completo, del más reciente al más antiguo.*"
)

issues = load_issues()

if not issues:
    st.info(
        "Encara no s'ha publicat cap número. El primer arribarà a l'inici de juny de 2026."
        if _ca else
        "Todavía no se ha publicado ningún número. El primero llegará a inicios de junio de 2026."
    )
else:
    for i, (d, meta, body) in enumerate(issues):
        st.divider()
        eyebrow = f"Núm. {len(issues) - i} · setmana del {format_data(d)}" if _ca \
            else f"Núm. {len(issues) - i} · semana del {format_data(d)}"
        st.caption(eyebrow)
        if meta.get("titular"):
            st.subheader(meta["titular"])
        if meta.get("preheader"):
            st.markdown(
                f'<p style="color:#4a4a4a; font-style:italic; margin-top:-0.5rem; '
                f'margin-bottom:1.5rem;">{meta["preheader"]}</p>',
                unsafe_allow_html=True,
            )
        st.markdown(body)

# ─── CTA SUBSCRIPCIÓ ────────────────────────────────────────────
st.divider()
newsletter_form(lang=st.session_state.lang, compact=False)

st.caption("Observatorio del Comercio · J3B3 Consulting")

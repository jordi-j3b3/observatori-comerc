"""Pulso de la semana — arxiu cronològic mirall de la newsletter setmanal.

Estètica editorial crítica alt contrast (Politico/Axios/Bloomberg Opinion):
fons blanc, negre intens, accent groc highlighter, sense caixes ni
border-left. Archivo Narrow per titulars, Inter per cos, Lora italic
per pull-quotes, IBM Plex Mono per xifres comparades.
"""
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


# ─── CSS Pulso (editorial alt contrast) ──────────────────────────

PULSO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;500;700&family=Inter:wght@400;500;700&family=Lora:ital,wght@1,400;1,500&family=IBM+Plex+Mono:wght@500;700&display=swap');

.pulso-intro {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    color: #444;
    max-width: 720px;
    margin: 4px 0 56px 0;
}

.pulso-issue {
    padding: 56px 0 72px 0;
    border-top: 8px solid #0a0a0a;
    margin-top: 32px;
}
.pulso-issue:first-of-type { margin-top: 16px; }

.pulso-eyebrow {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 0.92rem;
    font-weight: 500;
    color: #6a6a6a;
    margin: 0 0 14px 0;
    text-transform: none;
    letter-spacing: 0;
}

.pulso-title {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 3rem;
    line-height: 1.02;
    color: #0a0a0a;
    font-weight: 700;
    margin: 0 0 18px 0;
    text-transform: none;
    letter-spacing: -0.5px;
}

.pulso-preheader {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 1.15rem;
    line-height: 1.5;
    color: #555;
    max-width: 720px;
    margin: 0 0 40px 0;
    padding-bottom: 32px;
    border-bottom: 1px solid #d0d0d0;
}

.pulso-section { margin: 44px 0 32px 0; }

.pulso-section-label {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0a0a0a;
    margin: 0 0 28px 0;
    padding-bottom: 8px;
    border-bottom: 3px solid #0a0a0a;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0;
}

.pulso-prosa {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    line-height: 1.7;
    color: #1a1a1a;
    margin: 0 0 18px 0;
}

/* CIFRA — sense caixa, xifra gegant amb subratllat groc */
.pulso-cifra-wrap { margin: 8px 0 32px 0; }
.pulso-cifra-value {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 6.5rem;
    line-height: 1;
    color: #0a0a0a;
    font-weight: 700;
    letter-spacing: -3px;
    margin: 0;
    display: inline-block;
    background: linear-gradient(180deg, transparent 0%, transparent 58%,
                #f5d800 58%, #f5d800 92%, transparent 92%);
    padding: 0 8px;
}
.pulso-cifra-context {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 1.05rem;
    font-weight: 500;
    color: #1a1a1a;
    text-transform: uppercase;
    margin: 22px 0 4px 0;
    letter-spacing: 0;
}
.pulso-cifra-fuente {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: #6a6a6a;
    margin: 0 0 28px 0;
}

/* NOTÍCIES — numeració gran + filets, sense card */
.pulso-noticia {
    display: grid;
    grid-template-columns: 72px 1fr;
    gap: 24px;
    padding: 26px 0;
    border-top: 1px solid #d0d0d0;
}
.pulso-noticia:last-child { border-bottom: 1px solid #d0d0d0; }
.pulso-noticia-num {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 3rem;
    line-height: 0.9;
    color: #0a0a0a;
    font-weight: 700;
}
.pulso-noticia-content { min-width: 0; }
.pulso-noticia-fuente {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 0.86rem;
    color: #6a6a6a;
    text-transform: uppercase;
    margin: 2px 0 8px 0;
    letter-spacing: 0;
}
.pulso-noticia-titulo {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 1.5rem;
    line-height: 1.18;
    color: #0a0a0a;
    font-weight: 700;
    margin: 0 0 12px 0;
}
.pulso-noticia-body p {
    font-family: 'Inter', sans-serif;
    font-size: 0.97rem;
    line-height: 1.65;
    color: #1a1a1a;
    margin: 0 0 10px 0;
}
.pulso-noticia-body p:last-child { margin-bottom: 0; }

/* DADES — taula austera amb barres negres + Espanya groc */
.pulso-data-intro {
    font-family: 'Inter', sans-serif;
    font-size: 0.98rem;
    line-height: 1.55;
    color: #1a1a1a;
    margin: 0 0 20px 0;
}
.pulso-bars {
    margin: 12px 0 28px 0;
    border-top: 1px solid #0a0a0a;
    border-bottom: 1px solid #0a0a0a;
    padding: 14px 0;
}
.pulso-bar-row {
    display: grid;
    grid-template-columns: 140px 72px 1fr;
    align-items: center;
    gap: 16px;
    padding: 6px 0;
}
.pulso-bar-label {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 0.95rem;
    color: #0a0a0a;
    text-transform: uppercase;
    font-weight: 500;
}
.pulso-bar-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.92rem;
    color: #0a0a0a;
    font-weight: 500;
    text-align: right;
}
.pulso-bar-track {
    position: relative;
    height: 14px;
}
.pulso-bar-fill {
    position: absolute;
    top: 2px;
    bottom: 2px;
    background: #0a0a0a;
    left: 0;
}
.pulso-bar-fill.neg { background: #6a6a6a; }
.pulso-bar-row.highlight .pulso-bar-fill { background: #f5d800; }
.pulso-bar-row.highlight .pulso-bar-label,
.pulso-bar-row.highlight .pulso-bar-value { font-weight: 700; }

/* PREDICCIÓ — pull-quote tipogràfic, sense caixa fosca */
.pulso-prediccion {
    padding: 20px 0 8px 0;
    margin: 16px 0 8px 0;
    position: relative;
}
.pulso-prediccion-mark {
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 6rem;
    line-height: 0.6;
    color: #f5d800;
    font-weight: 700;
    position: absolute;
    top: -8px;
    left: -4px;
    user-select: none;
}
.pulso-prediccion-body {
    padding-left: 56px;
}
.pulso-prediccion-body p {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 1.25rem;
    line-height: 1.5;
    color: #1a1a1a;
    margin: 0 0 16px 0;
    font-weight: 400;
}
.pulso-prediccion-firma {
    text-align: right;
    font-family: 'Archivo Narrow', sans-serif;
    font-size: 0.95rem;
    color: #0a0a0a;
    text-transform: uppercase;
    margin: 24px 0 0 0;
    font-weight: 500;
    letter-spacing: 0;
}
.pulso-prediccion-firma::before {
    content: "— ";
    color: #f5d800;
    font-weight: 700;
}
</style>
"""


# ─── Parser / helpers ───────────────────────────────────────────

def format_data(d: date) -> str:
    mesos = MESOS_CA if _ca else MESES_ES
    return f"{d.day} de {mesos[d.month - 1]} de {d.year}"


def strip_trazabilidad(md: str) -> str:
    idx = md.find("### TRAZABILIDAD")
    return (md[:idx] if idx >= 0 else md).rstrip()


def extract_meta(md: str) -> tuple[dict, str]:
    meta = {"asunto": None, "preheader": None, "titular": None}
    lines = md.split("\n")
    body_start = 0
    for i, raw in enumerate(lines):
        line = raw.strip()
        m = re.match(r"^\*\*(Asunto|Pre-header|Titular):\*\*\s*(.+)$", line)
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


def md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def paragraphs(text: str, css_class: str = "pulso-prosa") -> str:
    parts = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "".join(f'<p class="{css_class}">{md_inline(p)}</p>' for p in parts)


def parse_sections(body: str) -> list[tuple[str, str]]:
    body = re.split(r"\n+\-{3,}\s*\n+\*\*Observatorio del Comercio\*\*", body)[0].rstrip()
    body = re.sub(
        r"^\*\*EL PULSO[^*]*\*\*\s*\n\*[^*]+\*\s*\n+\-{3,}\s*\n+",
        "", body, count=1,
    ).strip()
    parts = re.split(r"\n*\*\*◆\s+([^*]+?)\*\*\s*\n+", body)
    sections = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        content = re.sub(r"\n+\-{3,}\s*$", "", content).strip()
        sections.append((title, content))
    return sections


# ─── Renderers per bloc ─────────────────────────────────────────

def render_cifra(content: str) -> str:
    cifra_m = re.search(r"\*\*Cifra:\*\*\s*(.+)", content)
    ctx_m = re.search(r"\*\*Contexto:\*\*\s*(.+)", content)
    fnt_m = re.search(r"\*\*Fuente:\*\*\s*(.+)", content)
    cifra = cifra_m.group(1).strip() if cifra_m else ""
    ctx = ctx_m.group(1).strip() if ctx_m else ""
    fnt = fnt_m.group(1).strip() if fnt_m else ""

    prosa = re.sub(
        r"^\*\*(Cifra|Contexto|Fuente):\*\*.+$\n?",
        "", content, flags=re.MULTILINE,
    ).strip()

    label = ("La xifra de la setmana" if _ca else "La cifra de la semana")
    cifra_html = (
        f'<div class="pulso-cifra-wrap">'
        f'<div class="pulso-cifra-value">{cifra}</div>'
        f'<div class="pulso-cifra-context">{ctx}</div>'
        f'<div class="pulso-cifra-fuente">{fnt}</div>'
        f'</div>'
    )
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{label}</div>'
        f'{cifra_html}'
        f'{paragraphs(prosa)}'
        f'</div>'
    )


def render_noticias(content: str) -> str:
    label = ("Tres notícies amb angle" if _ca else "Tres noticias con ángulo")
    pattern = re.compile(
        r"\*\*(?P<titol>[^*]+?)\*\*\s*\n"
        r"\*(?P<fuente>[^*]+?)\*\s*\n+"
        r"(?P<body>.+?)"
        r"(?=\n+\*\*[^*]+\*\*\s*\n\*[^*]+\*|\Z)",
        re.DOTALL,
    )
    cards = []
    for idx, m in enumerate(pattern.finditer(content), start=1):
        titol = m.group("titol").strip()
        fuente = m.group("fuente").strip()
        body = m.group("body").strip()
        body_html = "".join(
            f'<p>{md_inline(p.strip())}</p>'
            for p in body.split("\n\n") if p.strip()
        )
        cards.append(
            f'<div class="pulso-noticia">'
            f'<div class="pulso-noticia-num">{idx:02d}</div>'
            f'<div class="pulso-noticia-content">'
            f'<div class="pulso-noticia-fuente">{fuente}</div>'
            f'<div class="pulso-noticia-titulo">{titol}</div>'
            f'<div class="pulso-noticia-body">{body_html}</div>'
            f'</div>'
            f'</div>'
        )
    cards_html = "".join(cards) if cards else paragraphs(content)
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{label}</div>'
        f'{cards_html}'
        f'</div>'
    )


def render_datos(content: str) -> str:
    label = ("Dades de la setmana" if _ca else "Datos de la semana")
    intro_m = re.search(r"\*\*Datos:\*\*\s*(.+)", content)
    intro = intro_m.group(1).strip() if intro_m else ""

    bullets = re.findall(
        r"^\-\s+([^:]+?):\s*([+-]?[\d,\.]+)\s*%",
        content, flags=re.MULTILINE,
    )

    prosa = re.sub(r"^\*\*Datos:\*\*.+$\n?", "", content, flags=re.MULTILINE)
    prosa = re.sub(r"^\-\s+.+%\s*$\n?", "", prosa, flags=re.MULTILINE).strip()

    bars_html = ""
    if bullets:
        items = [(p.strip(), v.strip()) for p, v in bullets]
        nums = [float(v.replace("+", "").replace(",", ".")) for _, v in items]
        max_abs = max((abs(n) for n in nums), default=1.0) or 1.0
        rows = []
        for (pais, v_str), n in zip(items, nums):
            pct = abs(n) / max_abs * 100
            cls = "neg" if n < 0 else ""
            is_spain = pais.lower() in ("españa", "espanya", "spain")
            highlight = " highlight" if is_spain else ""
            val_display = f"{v_str}%" if "%" not in v_str else v_str
            if not val_display.startswith(("+", "-")):
                val_display = ("+" + val_display) if n >= 0 else val_display
            rows.append(
                f'<div class="pulso-bar-row{highlight}">'
                f'<div class="pulso-bar-label">{pais}</div>'
                f'<div class="pulso-bar-value">{val_display}</div>'
                f'<div class="pulso-bar-track">'
                f'<div class="pulso-bar-fill {cls}" style="width:{pct:.1f}%;"></div>'
                f'</div>'
                f'</div>'
            )
        bars_html = f'<div class="pulso-bars">{"".join(rows)}</div>'

    intro_html = (
        f'<div class="pulso-data-intro">{md_inline(intro)}</div>' if intro else ""
    )
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{label}</div>'
        f'{intro_html}{bars_html}{paragraphs(prosa)}'
        f'</div>'
    )


def render_prediccion(content: str) -> str:
    label = ("La predicció" if _ca else "La predicción")
    firma_m = re.search(r"\n\s*\*\s*[—\-]\s*J3B3\s*\*\s*$", content)
    body = content[:firma_m.start()].strip() if firma_m else content.strip()
    body_html = "".join(
        f'<p>{md_inline(p.strip())}</p>'
        for p in body.split("\n\n") if p.strip()
    )
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{label}</div>'
        f'<div class="pulso-prediccion">'
        f'<div class="pulso-prediccion-mark">&ldquo;</div>'
        f'<div class="pulso-prediccion-body">{body_html}</div>'
        f'<div class="pulso-prediccion-firma">J3B3, observatori</div>'
        f'</div>'
        f'</div>'
    )


def render_block(title: str, content: str) -> str:
    nm = title.upper()
    if "CIFRA" in nm:
        return render_cifra(content)
    if "NOTICIA" in nm or "NOTÍCIA" in nm:
        return render_noticias(content)
    if "DATOS" in nm or "DADES" in nm:
        return render_datos(content)
    if "PREDICC" in nm:
        return render_prediccion(content)
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{title}</div>'
        f'{paragraphs(content)}'
        f'</div>'
    )


# ─── Càrrega d'issues ───────────────────────────────────────────

def load_issues() -> list[tuple[date, dict, str]]:
    if not NEWSLETTER_DIR.is_dir():
        return []
    out: list[tuple[date, dict, str]] = []
    for path in sorted(NEWSLETTER_DIR.glob("semana-*.md"), reverse=True):
        m = re.match(r"semana-(\d{4})-(\d{2})-(\d{2})", path.stem)
        if not m:
            continue
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        raw = path.read_text(encoding="utf-8")
        meta, body = extract_meta(strip_trazabilidad(raw))
        out.append((d, meta, body))
    return out


# ─── Pàgina ─────────────────────────────────────────────────────

st.markdown(PULSO_CSS, unsafe_allow_html=True)

st.title("El Pulso de la setmana" if _ca else "El Pulso de la semana")
st.markdown(
    '<div class="pulso-intro">'
    + ("Cada dilluns, una mirada concisa al moment del consum minorista a Espanya i Europa: "
       "una xifra, tres notícies amb angle, dades comparades i una predicció signada. "
       "Aquí pots consultar l'arxiu cronològic complet, del més recent al més antic."
       if _ca else
       "Cada lunes, una mirada concisa al momento del consumo minorista en España y Europa: "
       "una cifra, tres noticias con ángulo, datos comparados y una predicción firmada. "
       "Aquí puedes consultar el archivo cronológico completo, del más reciente al más antiguo.")
    + "</div>",
    unsafe_allow_html=True,
)

issues = load_issues()

if not issues:
    st.info(
        "Encara no s'ha publicat cap número. El primer arribarà a l'inici de juny de 2026."
        if _ca else
        "Todavía no se ha publicado ningún número. El primero llegará a inicios de junio de 2026."
    )
else:
    total = len(issues)
    for i, (d, meta, body) in enumerate(issues):
        num = total - i
        eyebrow = f"Núm. {num}  ·  {format_data(d)}"
        titular = meta.get("titular") or ""
        preheader = meta.get("preheader") or ""

        st.markdown(
            f'<div class="pulso-issue">'
            f'<div class="pulso-eyebrow">{eyebrow}</div>'
            f'<h2 class="pulso-title">{titular}</h2>'
            f'<p class="pulso-preheader">{preheader}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        try:
            sections = parse_sections(body)
            if not sections:
                st.markdown(body)
            else:
                blocks_html = "".join(render_block(t, c) for t, c in sections)
                st.markdown(blocks_html, unsafe_allow_html=True)
        except Exception:
            st.markdown(body)

# ─── CTA SUBSCRIPCIÓ ────────────────────────────────────────────
st.divider()
newsletter_form(lang=st.session_state.lang, compact=False)

st.caption("Observatorio del Comercio · J3B3 Consulting")

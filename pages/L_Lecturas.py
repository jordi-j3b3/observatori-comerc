"""Pulso de la semana — arxiu cronològic mirall de la newsletter setmanal.

Cada número del .md es parseja per blocs (◆ LA CIFRA, ◆ TRES NOTICIAS, ◆ DATOS,
◆ LA PREDICCIÓN) i es renderitza amb un estil consultant-grade: exhibit per
la xifra, cards per les notícies, barres divergents per les dades comparades
i una caixa fosca destacada per la predicció. Si el parser troba un format
inesperat, fa fallback a markdown plain.
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


# ─── CSS específic del Pulso ─────────────────────────────────────

PULSO_CSS = """
<style>
.pulso-intro {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.02rem;
    line-height: 1.65;
    color: #4a4a4a;
    font-style: italic;
    max-width: 760px;
    margin: 8px 0 40px 0;
}
.pulso-issue {
    padding: 32px 0 48px 0;
    border-top: 1px solid #e0e0e0;
}
.pulso-issue:first-of-type {
    border-top: 3px solid #0a0a0a;
}
.pulso-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #0055a4;
    margin: 0 0 10px 0;
}
.pulso-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.1rem;
    line-height: 1.15;
    color: #0a0a0a;
    margin: 0 0 14px 0;
    font-weight: 400;
}
.pulso-preheader {
    font-family: 'DM Sans', sans-serif;
    font-style: italic;
    color: #4a4a4a;
    font-size: 1rem;
    line-height: 1.5;
    margin: 0 0 36px 0;
    max-width: 720px;
}
.pulso-section {
    margin: 36px 0 28px 0;
}
.pulso-section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.8px;
    text-transform: uppercase;
    color: #0055a4;
    padding-bottom: 8px;
    border-bottom: 2px solid #0055a4;
    display: inline-block;
    margin-bottom: 20px;
}
.pulso-prosa {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.97rem;
    line-height: 1.7;
    color: #1a1a1a;
    margin: 0 0 14px 0;
}
.pulso-cifra-exhibit {
    background: #f4f4f2;
    border-left: 4px solid #0055a4;
    padding: 36px 32px;
    margin: 8px 0 28px 0;
    text-align: center;
}
.pulso-cifra-value {
    font-family: 'DM Serif Display', serif;
    font-size: 4.5rem;
    line-height: 1;
    color: #0055a4;
    margin: 0 0 16px 0;
    font-weight: 400;
    letter-spacing: -1px;
}
.pulso-cifra-context {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #1a1a1a;
    margin-bottom: 8px;
    font-weight: 500;
}
.pulso-cifra-fuente {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: #4a4a4a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}
.pulso-noticia {
    background: #ffffff;
    border-left: 3px solid #0055a4;
    padding: 22px 26px;
    margin: 0 0 18px 0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.pulso-noticia-fuente {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.74rem;
    color: #c0392b;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-bottom: 8px;
    font-weight: 600;
}
.pulso-noticia-titulo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    line-height: 1.3;
    color: #0a0a0a;
    margin: 0 0 14px 0;
    font-weight: 400;
}
.pulso-noticia-body p {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.65;
    color: #1a1a1a;
    margin: 0 0 10px 0;
}
.pulso-noticia-body p:last-child { margin-bottom: 0; }

.pulso-data-intro {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: #1a1a1a;
    margin: 0 0 20px 0;
    line-height: 1.6;
}
.pulso-bars {
    margin: 16px 0 24px 0;
    padding: 8px 0;
}
.pulso-bar-row {
    display: grid;
    grid-template-columns: 130px 1fr 64px;
    align-items: center;
    gap: 14px;
    padding: 5px 0;
    font-family: 'DM Sans', sans-serif;
}
.pulso-bar-label {
    font-size: 0.92rem;
    color: #1a1a1a;
    text-align: right;
    padding-right: 8px;
}
.pulso-bar-track {
    position: relative;
    height: 22px;
}
.pulso-bar-center {
    position: absolute;
    left: 50%;
    top: -2px;
    bottom: -2px;
    width: 1px;
    background: #c8c8c8;
}
.pulso-bar-fill {
    position: absolute;
    top: 3px;
    bottom: 3px;
    border-radius: 1px;
}
.pulso-bar-fill.pos { background: #0055a4; left: 50%; }
.pulso-bar-fill.neg { background: #c0392b; right: 50%; }
.pulso-bar-value {
    font-size: 0.88rem;
    font-weight: 600;
    color: #0a0a0a;
}
.pulso-bar-row.highlight .pulso-bar-label {
    font-weight: 700;
    color: #0055a4;
}
.pulso-bar-row.highlight .pulso-bar-value {
    color: #0055a4;
}
.pulso-prediccion-box {
    background: #0a0a0a;
    padding: 36px 36px 28px 36px;
    margin: 12px 0 16px 0;
    position: relative;
}
.pulso-prediccion-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.8px;
    text-transform: uppercase;
    color: #c0392b;
    margin-bottom: 18px;
}
.pulso-prediccion-box p {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.02rem;
    line-height: 1.7;
    color: #f4f4f2;
    margin: 0 0 14px 0;
}
.pulso-prediccion-firma {
    text-align: right;
    font-family: 'DM Serif Display', serif;
    font-style: italic;
    color: #c0392b;
    margin-top: 22px;
    font-size: 1.05rem;
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
    """Extreu Asunto / Pre-header / Titular del frontmatter."""
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
    """Converteix **bold** i *italic* mantenint la resta tal qual."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def paragraphs(text: str, css_class: str = "pulso-prosa") -> str:
    parts = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "".join(f'<p class="{css_class}">{md_inline(p)}</p>' for p in parts)


def parse_sections(body: str) -> list[tuple[str, str]]:
    """Tornar [(titol_seccio, contingut), ...] dividint per '**◆ TITLE**'.

    Strip del header redundant (EL PULSO DE LA SEMANA · Núm. X) i del
    footer email (Observatorio del Comercio · Darse de baja).
    """
    # Strip footer email
    body = re.split(r"\n+\-{3,}\s*\n+\*\*Observatorio del Comercio\*\*", body)[0].rstrip()
    # Strip prelude redundant
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
    exhibit = (
        f'<div class="pulso-cifra-exhibit">'
        f'<div class="pulso-cifra-value">{cifra}</div>'
        f'<div class="pulso-cifra-context">{ctx}</div>'
        f'<div class="pulso-cifra-fuente">{fnt}</div>'
        f'</div>'
    )
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-section-label">{label}</div>'
        f'{exhibit}'
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
    for m in pattern.finditer(content):
        titol = m.group("titol").strip()
        fuente = m.group("fuente").strip()
        body = m.group("body").strip()
        body_html = "".join(
            f'<p>{md_inline(p.strip())}</p>'
            for p in body.split("\n\n") if p.strip()
        )
        cards.append(
            f'<div class="pulso-noticia">'
            f'<div class="pulso-noticia-fuente">{fuente}</div>'
            f'<div class="pulso-noticia-titulo">{titol}</div>'
            f'<div class="pulso-noticia-body">{body_html}</div>'
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

    # Treu meta + bullets, queda la prosa interpretativa
    prosa = re.sub(r"^\*\*Datos:\*\*.+$\n?", "", content, flags=re.MULTILINE)
    prosa = re.sub(r"^\-\s+.+%\s*$\n?", "", prosa, flags=re.MULTILINE).strip()

    bars_html = ""
    if bullets:
        valors = [(p.strip(), v.strip()) for p, v in bullets]
        nums = [float(v.replace("+", "").replace(",", ".")) for _, v in valors]
        max_abs = max((abs(n) for n in nums), default=1.0) or 1.0
        rows = []
        for (pais, v_str), n in zip(valors, nums):
            pct = abs(n) / max_abs * 46
            cls = "pos" if n >= 0 else "neg"
            is_spain = pais.lower() in ("españa", "espanya", "spain")
            highlight = " highlight" if is_spain else ""
            val_display = f"{v_str}%" if "%" not in v_str else v_str
            if not val_display.startswith(("+", "-")):
                val_display = ("+" + val_display) if n >= 0 else val_display
            rows.append(
                f'<div class="pulso-bar-row{highlight}">'
                f'<div class="pulso-bar-label">{pais}</div>'
                f'<div class="pulso-bar-track">'
                f'<div class="pulso-bar-center"></div>'
                f'<div class="pulso-bar-fill {cls}" style="width:{pct:.1f}%;"></div>'
                f'</div>'
                f'<div class="pulso-bar-value">{val_display}</div>'
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
    if firma_m:
        body = content[:firma_m.start()].strip()
    else:
        body = content.strip()
    body_html = "".join(
        f'<p>{md_inline(p.strip())}</p>'
        for p in body.split("\n\n") if p.strip()
    )
    return (
        f'<div class="pulso-section">'
        f'<div class="pulso-prediccion-box">'
        f'<div class="pulso-prediccion-label">{label}</div>'
        f'{body_html}'
        f'<div class="pulso-prediccion-firma">— J3B3</div>'
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
    # Fallback genèric
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
        eyebrow_label = (f"Núm. {num}  ·  {format_data(d)}"
                         if _ca else
                         f"Núm. {num}  ·  {format_data(d)}")
        titular = meta.get("titular") or ""
        preheader = meta.get("preheader") or ""

        st.markdown(
            f'<div class="pulso-issue">'
            f'<div class="pulso-eyebrow">{eyebrow_label}</div>'
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
            # Si el parser falla per qualsevol raó, fallback a markdown plain
            st.markdown(body)

# ─── CTA SUBSCRIPCIÓ ────────────────────────────────────────────
st.divider()
newsletter_form(lang=st.session_state.lang, compact=False)

st.caption("Observatorio del Comercio · J3B3 Consulting")

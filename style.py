"""
Estils compartits: layout Plotly, CSS global, helpers de presentació.
Disseny editorial alt contrast: Archivo Narrow + Inter + Lora italic +
IBM Plex Mono. Paleta negre/blanc/groc highlighter.
"""
import contextlib
import streamlit as st
import os
import json

# Counter per assignar keys úniques als highlight_expander
_highlight_expander_counter = 0

# ─── COLORS ───────────────────────────────────────────────────
# Es mantenen els noms antics (PURPLE, BLUE, PURPLE_LIGHT, ...) com a
# àlies per a compatibilitat amb codi existent. Els valors han canviat
# a la nova paleta editorial.

# Paleta J3B3 — blau marí fosc + crema/blanc + groc highlighter
BRAND = "#003366"         # blau marca j3b3.com (links, accents, filets, hovers)
BRAND_DEEP = "#001f3f"    # variant més fosca per a contrastos extrems
INK = "#2c2c2c"           # tinta de cos (gris fosc, no negre absolut)
INK_STRONG = "#1a1a1a"    # tinta destacada per a titulars
GRAY_DARK = "#6a6a6a"
GRAY = "#c0c0c0"
GRAY_LIGHT = "#d0d0d0"
SURFACE = "#ffffff"       # fons principal
SURFACE_SOFT = "#f5f5f5"  # fons secundari j3b3 per a separadors discretos
YELLOW = "#f5d800"        # highlighter (subratllats, accent destacat)
YELLOW_SOFT = "#fff9b8"
RED = "#c0392b"           # accent dur (negatius/atenció)

# Àlies retrocompatibles
DARK = INK_STRONG
DARK_SOFT = INK
PURPLE = BRAND
PURPLE_LIGHT = GRAY_DARK
PURPLE_BG = SURFACE_SOFT
BLUE = BRAND
GREEN = "#5a8f3d"          # verd terròs (no pas saturat)
ORANGE = "#c75d2c"         # taronja terròs (no pas saturat)

# ─── PALETA PREMIUM (consultora — pilot PIB i VAB) ────────────
NAVY = "#0b3a66"          # navy fosc: display, emphasis
OCRE = "#b07d2b"          # ocre càlid: accent, kicker
OCRE_DEEP = "#946618"     # ocre fosc: end-label real
INK_P = "#1a2b3a"         # tinta display premium
BODY_P = "#37485a"        # cos text premium
G1_P = "#5e6b78"          # gris labels / ticks
G2_P = "#9aa6b2"          # gris clar: axis title, font
LINE_P = "#e4e9ee"        # filet molt subtil

# Paleta editorial per a sèries múltiples: comença amb el blau marca
# i alterna amb groc highlighter, gris i accents discretos.
PALETTE = [BRAND, YELLOW, GRAY_DARK, RED, "#5a8f3d", "#c75d2c", BRAND_DEEP, "#3d8f8f", GRAY, INK_STRONG]


# ─── FORMAT NUMÈRIC (europeu: 1.234,56) ─────────────────────

def fnum(n, decimals=0):
    """Formata un nombre amb punt per milers i coma per decimals."""
    if n is None:
        return "—"
    if decimals == 0:
        return f"{int(round(n)):,}".replace(",", ".")
    formatted = f"{n:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def fpct(n, decimals=1, sign=True):
    """Formata un percentatge amb format europeu. Evita +0,0% / -0,0%."""
    if n is None:
        return "—"
    rounded = round(n, decimals)
    if rounded == 0:
        return f"0,{('0' * decimals)}%"
    if sign:
        raw = f"{rounded:+.{decimals}f}"
    else:
        raw = f"{rounded:.{decimals}f}"
    return raw.replace(".", ",") + "%"


# ─── PLOTLY LAYOUT ────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=13, color=DARK),
    plot_bgcolor="#ffffff",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=60, r=20, t=40, b=50),
    colorway=PALETTE,
    hoverlabel=dict(
        bgcolor="#003366",
        font_size=13,
        font_family="Inter, sans-serif",
        font_color="#ffffff",
        bordercolor="#003366",
    ),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.05)",
        linecolor="#003366",
        linewidth=1,
        zeroline=True,
        zerolinecolor="rgba(0,51,102,0.18)",
        zerolinewidth=1,
        tickfont=dict(family="Archivo Narrow, sans-serif", size=12, color="#1a1a1a"),
        title_font=dict(family="Archivo Narrow, sans-serif", size=13, color="#003366"),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.05)",
        linecolor="#003366",
        linewidth=1,
        zeroline=True,
        zerolinecolor="rgba(0,51,102,0.18)",
        zerolinewidth=1,
        tickfont=dict(family="Archivo Narrow, sans-serif", size=12, color="#1a1a1a"),
        title_font=dict(family="Archivo Narrow, sans-serif", size=13, color="#003366"),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(family="Archivo Narrow, sans-serif", size=12, color="#1a1a1a"),
        bgcolor="rgba(0,0,0,0)",
    ),
    hovermode="x unified",
    title=dict(
        text="",
        font=dict(family="Archivo Narrow, sans-serif", size=15, color="#003366"),
        x=0,
        xanchor="left",
    ),
)


def apply_layout(fig, **overrides):
    """Aplica el layout estàndard a un gràfic Plotly amb overrides opcionals."""
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


# ─── i18n COMPARTIT ──────────────────────────────────────────

@st.cache_data(ttl=300)
def _load_translations():
    path = os.path.join(os.path.dirname(__file__), "i18n", "translations.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_LANG_OPTIONS = {"Castellano": "es", "Català": "ca"}


def render_lang_selector(label="Idioma"):
    """Renderitza el selector d'idioma (selectbox amb clau persistent
    'lang_selector'). Cal cridar-lo dins d'un context de sidebar; permet
    col·locar-lo on convingui (p. ex. al peu del sidebar)."""
    st.selectbox(label, list(_LANG_OPTIONS.keys()), key="lang_selector")


def setup_lang(show_selector=True):
    """Configura l'idioma i retorna la funció de traducció t().

    L'idioma es deriva del selector (clau de sessió 'lang_selector'); per
    defecte, castellà. Així el selector es pot renderitzar separadament
    (al peu del sidebar) amb render_lang_selector() i l'idioma queda fixat
    abans de construir títols i navegació.
    """
    TRANS = _load_translations()
    _label = st.session_state.get("lang_selector", "Castellano")
    st.session_state.lang = _LANG_OPTIONS.get(_label, "es")

    if show_selector:
        with st.sidebar:
            render_lang_selector()

    def t(key):
        return TRANS.get(st.session_state.lang, {}).get(key, key)

    return t


# ─── CSS GLOBAL ───────────────────────────────────────────────

def inject_css():
    """Injecta CSS global a la pàgina (cridar a cada page).

    Estètica editorial alt contrast (Politico/Axios/Bloomberg Opinion):
    Archivo Narrow per titulars, Inter per cos, Lora italic per cites,
    IBM Plex Mono per xifres. Paleta negre/blanc/groc highlighter.
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;500;700&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@1,400;1,500&family=IBM+Plex+Mono:wght@500;700&family=Manrope:wght@400;600;700;800&display=swap');

        /* Tipografia global */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        h1, .stMarkdown h1 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #003366;
            font-size: 2.6rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.5px;
        }
        h2, .stMarkdown h2 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #003366;
            font-size: 1.9rem !important;
            line-height: 1.1 !important;
        }
        h3, .stMarkdown h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #003366;
            font-size: 1.4rem !important;
            line-height: 1.15 !important;
        }
        h4, h5, h6,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            color: #003366;
        }

        /* Mètriques editorial — fons blanc, valor en Archivo Narrow,
           delta sense píndola arrodonida amb fons de color */
        [data-testid="stMetric"] {
            background: #ffffff !important;
            border-radius: 0 !important;
            padding: 12px 16px 12px 0 !important;
            border: none !important;
            border-top: 1px solid #003366 !important;
            box-shadow: none !important;
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] div,
        [data-testid="stMetricLabel"] label {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            color: #6a6a6a !important;
            font-size: 0.78rem !important;
            letter-spacing: 0 !important;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div,
        [data-testid="stMetricValue"] span {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #003366 !important;
            font-size: 2.2rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.5px !important;
        }
        /* Delta — sense fons píndola, sense arrodoniment, només color i fletxa */
        [data-testid="stMetricDelta"] {
            background: transparent !important;
            border-radius: 0 !important;
            padding: 4px 0 0 0 !important;
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }
        [data-testid="stMetricDelta"] div,
        [data-testid="stMetricDelta"] span {
            background: transparent !important;
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 600 !important;
        }
        /* Color del valor del delta: negre intens per positius, vermell pels negatius */
        [data-testid="stMetricDeltaIcon-Up"] ~ div,
        [data-testid="stMetricDelta"] [data-testid="stMetricDeltaIcon-Up"] + div {
            color: #003366 !important;
        }
        [data-testid="stMetricDeltaIcon-Down"] ~ div,
        [data-testid="stMetricDelta"] [data-testid="stMetricDeltaIcon-Down"] + div {
            color: #c0392b !important;
        }
        /* Icona delta — preservar font Material Symbols */
        [data-testid="stMetricDeltaIcon-Up"],
        [data-testid="stMetricDeltaIcon-Down"] {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
        }
        [data-testid="stMetricDeltaIcon-Up"] svg { fill: #003366 !important; }
        [data-testid="stMetricDeltaIcon-Down"] svg { fill: #c0392b !important; }
        /* Help icon (?) — discreta */
        [data-testid="stMetricLabel"] [data-testid="stTooltipIcon"],
        [data-testid="stMetric"] [data-testid="stTooltipIcon"] {
            color: #c0c0c0 !important;
        }

        /* Sidebar (es manté fosc per coherència de chrome) */
        [data-testid="stSidebar"] {
            background-color: #001f3f;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebarNavViewButton"] {
            display: none !important;
        }

        /* ── Navegació plegable al sidebar: expanders transparents sobre el
           navy (anul·la el fons blanc global dels expanders) ── */
        [data-testid="stSidebar"] [data-testid="stExpander"],
        [data-testid="stSidebar"] [data-testid="stExpander"] > div,
        [data-testid="stSidebar"] [data-testid="stExpander"] details,
        [data-testid="stSidebar"] [data-testid="stExpander"] details > div,
        [data-testid="stSidebar"] [data-testid="stExpanderDetails"],
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            margin: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            border-top: 1px solid rgba(255,255,255,0.12) !important;
            padding: 8px 4px !important;
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.02em;
            opacity: 0.82;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
            opacity: 1 !important;
        }
        /* Enllaços de pàgina dins el sidebar */
        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            background: transparent !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] p {
            color: #FFFFFF !important;
            font-size: 0.92rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
            background: rgba(255,255,255,0.08) !important;
            border-radius: 4px;
        }
        /* Pàgina activa (Inici fora d'expander i enllaços actius) */
        [data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"],
        [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
            background: rgba(255,255,255,0.14) !important;
            border-radius: 4px;
        }

        /* Botons */
        .stDownloadButton button {
            background-color: #003366;
            color: #ffffff;
            border: none;
            border-radius: 0;
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
        }
        .stDownloadButton button:hover {
            background-color: #001f3f;
            box-shadow: inset 0 -3px 0 0 #f5d800;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            color: #6a6a6a;
        }
        .stTabs [aria-selected="true"] {
            color: #003366 !important;
            border-bottom-color: #003366 !important;
            border-bottom-width: 3px !important;
        }

        /* Dividers */
        hr { border-color: #d0d0d0 !important; }

        /* Cards de mètriques: filet superior fi, sense rampa lateral */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 0;
            padding: 14px 16px 12px 0;
            border: none;
            border-top: 1px solid #003366;
        }

        /* Insight box — fons blanc, filet gruixut superior negre + accent groc */
        .insight-box {
            background: #ffffff;
            border-top: 3px solid #003366;
            border-radius: 0;
            padding: 20px 22px 18px 22px;
            margin: 16px 0 24px 0;
            font-family: 'Inter', sans-serif;
            font-size: 0.97rem;
            line-height: 1.65;
            color: #1a1a1a;
        }
        .insight-box strong {
            background: linear-gradient(180deg, transparent 0%, transparent 60%,
                        #f5d800 60%, #f5d800 92%, transparent 92%);
            padding: 0 2px;
        }
        .insight-box .insight-title {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            margin-bottom: 12px;
            letter-spacing: 0;
        }

        /* Intro box — fons blanc, sense decoració més enllà del marge */
        .intro-box {
            background: #ffffff;
            border-radius: 0;
            padding: 0 0 18px 0;
            margin: 0 0 28px 0;
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            line-height: 1.65;
            color: #444;
            border-bottom: 1px solid #d0d0d0;
        }

        /* Conclusions block (Inici) — filet superior gruixut + accent groc, sense gradient */
        .conclusions-block {
            background: #ffffff;
            border: none;
            border-top: 3px solid #003366;
            border-radius: 0;
            padding: 28px 0 24px 0;
            margin: 24px 0;
            box-shadow: none;
        }
        .conclusions-block .conclusions-eyebrow {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            margin-bottom: 10px;
            letter-spacing: 0;
        }
        .conclusions-block h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            color: #003366 !important;
            margin: 0 0 14px 0 !important;
            padding: 0 !important;
            border: none !important;
            line-height: 1.08 !important;
        }
        .conclusions-block .conclusions-update {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: #6a6a6a;
            margin-bottom: 18px;
            font-style: italic;
        }
        .conclusions-block ul {
            margin: 0;
            padding-left: 20px;
        }
        .conclusions-block li {
            font-family: 'Inter', sans-serif;
            font-size: 0.97rem;
            line-height: 1.7;
            color: #1a1a1a;
            margin-bottom: 10px;
        }
        .conclusions-block li strong {
            background: linear-gradient(180deg, transparent 0%, transparent 60%,
                        #f5d800 60%, #f5d800 92%, transparent 92%);
            padding: 0 2px;
            color: #003366;
        }

        /* Newsletter (subscripció combinada Pulso setmanal + trimestral) */
        .newsletter-block {
            background: #ffffff;
            border: none;
            border-top: 2px solid #003366;
            border-bottom: 1px solid #d0d0d0;
            border-radius: 0;
            padding: 24px 0 16px 0;
            margin: 32px 0 16px 0;
            box-shadow: none;
        }
        .newsletter-block .newsletter-eyebrow {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            margin-bottom: 10px;
            letter-spacing: 0;
        }
        .newsletter-block h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.7rem !important;
            color: #003366 !important;
            margin: 0 0 12px 0 !important;
            padding: 0 !important;
            border: none !important;
            line-height: 1.1 !important;
        }
        .newsletter-block .newsletter-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.97rem;
            line-height: 1.6;
            color: #1a1a1a;
            margin: 0 0 20px 0;
        }
        .newsletter-block .newsletter-desc strong {
            background: linear-gradient(180deg, transparent 0%, transparent 60%,
                        #f5d800 60%, #f5d800 92%, transparent 92%);
            padding: 0 2px;
        }
        .newsletter-block .newsletter-foot {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            color: #6a6a6a;
            margin: 4px 0 0 0;
        }

        /* CDMGE — Pols diari (alta freqüència) */
        .cdmge-block {
            background: #ffffff;
            border: none;
            border-top: 2px solid #003366;
            border-bottom: 1px solid #d0d0d0;
            border-radius: 0;
            padding: 26px 0 20px 0;
            margin: 32px 0 24px 0;
            box-shadow: none;
        }
        .cdmge-block .cdmge-eyebrow {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            margin-bottom: 8px;
            letter-spacing: 0;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .cdmge-block .cdmge-pulse {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #f5d800;
            border-radius: 0;
            animation: cdmgePulse 1.6s ease-in-out infinite;
        }
        @keyframes cdmgePulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.45; transform: scale(1.25); }
        }
        .cdmge-block h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.9rem !important;
            color: #003366 !important;
            margin: 0 0 8px 0 !important;
            padding: 0 !important;
            border: none !important;
            line-height: 1.1 !important;
        }
        .cdmge-block .cdmge-sub {
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            color: #444;
            margin-bottom: 18px;
            line-height: 1.55;
        }
        .cdmge-block .cdmge-asof {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            color: #6a6a6a;
            font-style: italic;
            margin-bottom: 14px;
        }

        /* Font de dades */
        .source-label {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            color: #6a6a6a;
            margin-top: -8px;
            margin-bottom: 20px;
            padding-left: 0;
            letter-spacing: 0;
        }

        /* Meta info */
        .meta-info {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: #6a6a6a;
            border-top: 1px solid #d0d0d0;
            padding-top: 12px;
            margin-top: 30px;
        }

        /* Footer global */
        .j3b3-footer {
            font-family: 'Inter', sans-serif;
            margin-top: 56px;
            padding-top: 28px;
            border-top: 3px solid #003366;
            color: #444;
            font-size: 13px;
            line-height: 1.6;
        }
        .j3b3-footer .footer-grid {
            display: grid;
            grid-template-columns: 1.4fr 1fr 1fr 1fr;
            gap: 28px;
            margin-bottom: 24px;
        }
        @media (max-width: 720px) {
            .j3b3-footer .footer-grid { grid-template-columns: 1fr; gap: 20px; }
        }
        .j3b3-footer .footer-brand-title {
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            font-size: 1.15rem;
            color: #003366;
            margin: 6px 0 6px 0;
            line-height: 1.2;
        }
        .j3b3-footer .footer-brand-desc {
            color: #444;
            font-size: 12.5px;
            margin: 0;
        }
        .j3b3-footer .footer-col-title {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            margin: 6px 0 10px 0;
            letter-spacing: 0;
        }
        .j3b3-footer ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .j3b3-footer ul li {
            margin: 0 0 6px 0;
        }
        .j3b3-footer a {
            color: #1a1a1a;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.15s, background 0.15s;
        }
        .j3b3-footer a:hover {
            color: #003366;
            background: linear-gradient(180deg, transparent 0%, transparent 70%,
                        #f5d800 70%, #f5d800 100%);
            border-bottom-color: transparent;
        }
        .j3b3-footer .footer-bottom {
            border-top: 1px solid #d0d0d0;
            padding-top: 14px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 11.5px;
            color: #6a6a6a;
        }
        .j3b3-footer .footer-bottom .copy strong {
            color: #1a1a1a;
            font-weight: 700;
        }

        /* Logo header */
        .j3b3-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 0.5rem;
        }
        .j3b3-header img {
            height: 30px;
        }
        .j3b3-badge {
            font-family: 'Archivo Narrow', sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: #003366;
            letter-spacing: 0;
        }

        /* Expander default — pelat editorial (per a expanders utilitaris
           tipus 'descarregar dades', 'metodologia tècnica', etc.) */
        .streamlit-expanderHeader,
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] details > summary,
        details > summary[role="button"] {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            color: #003366 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0 !important;
            background: #ffffff !important;
            padding: 8px 0 !important;
            cursor: pointer;
        }

        /* Expander destacat — només quan el container pare té key
           "highlight_expander_*" (helper highlight_expander() a style.py).
           Subratllat groc al header per indicar contingut addicional rellevant. */
        [class*="st-key-highlight_expander_"] [data-testid="stExpander"] summary,
        [data-testid^="stVerticalBlock"] [class*="st-key-highlight_expander_"] summary,
        .st-key-highlight_expander summary,
        div[class*="highlight_expander"] [data-testid="stExpander"] summary {
            background: linear-gradient(180deg,
                        transparent 0%, transparent 55%,
                        rgba(245, 216, 0, 0.45) 55%, rgba(245, 216, 0, 0.45) 92%,
                        transparent 92%) !important;
            font-size: 1rem !important;
            padding: 10px 8px !important;
            transition: background 0.15s ease;
        }
        [class*="st-key-highlight_expander_"] [data-testid="stExpander"] summary:hover,
        div[class*="highlight_expander"] [data-testid="stExpander"] summary:hover {
            background: linear-gradient(180deg,
                        transparent 0%, transparent 30%,
                        #f5d800 30%, #f5d800 95%,
                        transparent 95%) !important;
        }
        [data-testid="stExpander"],
        [data-testid="stExpander"] > div,
        [data-testid="stExpander"] > div > div,
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] details > div,
        [data-testid="stExpanderDetails"],
        [data-testid="stExpanderHeader"],
        .streamlit-expander,
        .streamlit-expanderHeader,
        .streamlit-expanderContent {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }
        /* Container exterior — només filets superior i inferior */
        [data-testid="stExpander"] {
            border: none !important;
            border-top: 1px solid #003366 !important;
            border-bottom: 1px solid #d0d0d0 !important;
            margin: 8px 0 16px 0 !important;
        }
        /* Cos del contingut expandit — respir moderat (no caixa, no enganxat).
           Padding lateral lleuger perquè els títols i gràfics no toquin el
           marge de la pàgina, mantenint l'alineació visual editorial. */
        [data-testid="stExpanderDetails"],
        [data-testid="stExpander"] [data-testid="stExpanderDetails"],
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] > div,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] > div > div,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] .stVerticalBlock,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"],
        [data-testid="stExpander"] details > div:not(summary),
        [data-testid="stExpander"] details > div > div {
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
        [data-testid="stExpanderDetails"] {
            padding: 16px 16px 16px 16px !important;
        }
        /* Eliminar markers natius del details (carret arrodonit del browser) */
        [data-testid="stExpander"] summary::-webkit-details-marker,
        [data-testid="stExpander"] summary::marker {
            display: none !important;
        }

        /* Inputs (selectbox, multiselect, text, number, date) — sense arrodoniments */
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextInput > div > div,
        .stNumberInput > div > div,
        .stDateInput > div > div,
        .stTextArea > div > div {
            border-radius: 0 !important;
        }
        .stSelectbox label, .stMultiSelect label,
        .stTextInput label, .stNumberInput label,
        .stDateInput label, .stTextArea label,
        .stRadio label, .stCheckbox label,
        .stSlider label {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 500 !important;
            color: #003366 !important;
            text-transform: uppercase;
            font-size: 0.85rem !important;
            letter-spacing: 0;
        }

        /* Botons (st.button, no només downloadButton) */
        .stButton > button {
            background-color: #ffffff;
            color: #003366;
            border: 1px solid #003366;
            border-radius: 0;
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .stButton > button:hover {
            background-color: #003366;
            color: #ffffff;
            box-shadow: inset 0 -3px 0 0 #f5d800;
        }
        .stButton > button:active,
        .stButton > button:focus {
            background-color: #003366;
            color: #ffffff;
            box-shadow: inset 0 -3px 0 0 #f5d800;
        }

        /* Alerts: st.info / st.warning / st.error / st.success */
        [data-testid="stAlert"],
        [data-testid="stNotification"] {
            border-radius: 0 !important;
            border-left: 4px solid #003366 !important;
            background: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
            color: #1a1a1a !important;
            box-shadow: none !important;
        }
        [data-testid="stAlertContentInfo"] { background: #ffffff !important; }
        [data-testid="stAlertContentWarning"] {
            background: #ffffff !important;
            border-left-color: #f5d800 !important;
        }
        [data-testid="stAlertContentError"] {
            background: #ffffff !important;
            border-left-color: #c0392b !important;
        }
        [data-testid="stAlertContentSuccess"] {
            background: #ffffff !important;
            border-left-color: #003366 !important;
        }
        /* Selectors alternatius per a la versió actual de Streamlit */
        div[data-baseweb="notification"] {
            border-radius: 0 !important;
            background: #ffffff !important;
            border-left: 4px solid #003366 !important;
            box-shadow: none !important;
        }

        /* Sidebar — tipografia editorial sobre fons negre.
           IMPORTANT: NO usar selector universal (*) perquè les icones de
           Material Symbols (keyboard_double_arrow_left, expand_more...)
           usen la font 'Material Symbols Outlined' per renderitzar-se
           com a glyphs. Si els hi forcem Inter, surt el text literal. */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] button {
            font-family: 'Inter', sans-serif;
        }
        /* Items de navegació (PIB i VAB, Empreses, etc.) — més discrets
           que el títol de secció: Inter regular, case normal, mida petita */
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebar"] nav a span,
        [data-testid="stSidebar"] li span {
            font-family: 'Inter', sans-serif !important;
            font-weight: 400 !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
            font-size: 0.85rem !important;
        }
        /* Item actiu lleugerament més marcat */
        [data-testid="stSidebar"] [aria-current="page"] span,
        [data-testid="stSidebar"] nav a[aria-current="page"] span {
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        /* Capçaleres de secció del nav (EDITORIAL, POLS, RADIOGRAFIA, etc.)
           — clarament destacades vs els items per sota */
        [data-testid="stSidebarNav"] section,
        [data-testid="stSidebarNav"] header,
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] > div > div > span,
        [data-testid="stSidebar"] [data-testid="stSidebarNavSection"] {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            font-size: 0.78rem !important;
            letter-spacing: 1px !important;
            opacity: 0.85;
            margin-top: 18px !important;
            margin-bottom: 6px !important;
        }
        /* Selectbox idioma dins sidebar */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background: #1a1a1a !important;
            border: 1px solid #2a2a2a !important;
        }
        /* Logo J3B3 al top del sidebar — invertir a blanc perquè el SVG
           original és blau marca i quedaria invisible sobre el sidebar blau */
        [data-testid="stSidebar"] [data-testid="stLogo"],
        [data-testid="stSidebar"] [data-testid="stSidebarLogo"],
        [data-testid="stSidebar"] [data-testid="stLogo"] img,
        [data-testid="stSidebar"] [data-testid="stSidebarLogo"] img,
        [data-testid="stSidebar"] img[src*="logo"] {
            filter: brightness(0) invert(1) !important;
        }
        /* Icones Material Symbols — preservar font icònica.
           Streamlit utilitza 'Material Symbols Rounded'/'Outlined' per
           a icones de col·lapse, expansió, navegació, etc. Els spans
           tenen classes/atributs específics. Forcem la font icònica
           amb especificitat alta. */
        [data-testid="stSidebar"] [class*="material-symbols"],
        [data-testid="stSidebar"] [class*="material-icons"],
        [data-testid="stSidebar"] [class*="MaterialSymbols"],
        [data-testid="stSidebar"] [data-testid="stIconMaterial"],
        [data-testid="stSidebar"] [data-baseweb="icon"] span,
        [class*="material-symbols"],
        [class*="material-icons"],
        [data-testid="stIconMaterial"] {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
            font-weight: normal !important;
            font-style: normal !important;
            text-transform: none !important;
            letter-spacing: normal !important;
            line-height: 1 !important;
            font-feature-settings: 'liga';
        }

        /* Background general de la pàgina + container */
        .stApp {
            background: #ffffff;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stAppViewContainer"] > .main {
            background: #ffffff;
        }

        /* Dataframes — esborrar arrodoniments i ombres */
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border-radius: 0 !important;
            border: 1px solid #d0d0d0 !important;
        }
        [data-testid="stDataFrame"] table thead th {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            background: #003366 !important;
            color: #ffffff !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stDataFrame"] table tbody td {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
        }
        [data-testid="stDataFrame"] table tbody td:has(span:not(:empty)),
        [data-testid="stDataFrame"] [role="gridcell"] {
            font-variant-numeric: tabular-nums;
        }

        /* Tabs — substituir background gris pels filets editorial */
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 2px solid #003366;
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 0;
            background: transparent !important;
        }

        /* Slider thumb negre */
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background: #003366 !important;
            border-color: #003366 !important;
        }
        .stSlider [data-baseweb="slider"] > div > div {
            background: #003366 !important;
        }

        /* Pills (segmented control) — sense arrodoniments, blanc/negre */
        [data-testid="stPills"] button,
        button[kind="pillsSegment"] {
            border-radius: 0 !important;
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 500;
            text-transform: uppercase;
        }
        [data-testid="stPills"] button[aria-pressed="true"],
        button[kind="pillsSegment"][aria-pressed="true"] {
            background: #003366 !important;
            color: #ffffff !important;
        }

        /* Toggle */
        [data-testid="stToggle"] label {
            font-family: 'Archivo Narrow', sans-serif !important;
            text-transform: uppercase;
            font-weight: 500;
        }

        /* Top horitzontal app bar (Deploy menu) — discreta */
        header[data-testid="stHeader"] {
            background: #ffffff !important;
            border-bottom: 1px solid #e4e9ee !important;
        }

        /* ── Barra de navegació superior (model prototip j3b3) ── */
        [data-testid="stTopNavLink"],
        [data-testid="stTopNavLink"] *,
        [data-testid="stTopNavSection"],
        [data-testid="stTopNavSection"] * {
            font-family: 'Manrope', system-ui, sans-serif !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            letter-spacing: .01em !important;
            color: #5e6b78 !important;
            text-transform: none !important;
        }
        [data-testid="stTopNavLink"]:hover,
        [data-testid="stTopNavLink"]:hover *,
        [data-testid="stTopNavSection"]:hover,
        [data-testid="stTopNavSection"]:hover * {
            color: #0b3a66 !important;
        }
        /* Enllaç/secció actiu: navy + subratllat ocre */
        [data-testid="stTopNavLink"][aria-current="page"],
        [data-testid="stTopNavLink"][aria-current="page"] *,
        [data-testid="stTopNavSection"]:has([aria-current="page"]),
        [data-testid="stTopNavSection"]:has([aria-current="page"]) * {
            color: #0b3a66 !important;
            font-weight: 700 !important;
        }
        [data-testid="stTopNavLink"][aria-current="page"] {
            border-bottom: 2px solid #b07d2b !important;
        }
        /* Desplegable de secció: fons blanc, tipografia Manrope */
        [data-testid="stTopNavPopover"] {
            background: #ffffff !important;
            border: 1px solid #e4e9ee !important;
        }
        [data-testid="stTopNavDropdownLink"],
        [data-testid="stTopNavDropdownLink"] * {
            font-family: 'Manrope', system-ui, sans-serif !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            color: #5e6b78 !important;
        }
        [data-testid="stTopNavDropdownLink"]:hover,
        [data-testid="stTopNavDropdownLink"]:hover * {
            color: #0b3a66 !important;
            background: #f5f7f9 !important;
        }
        [data-testid="stTopNavDropdownLink"][aria-current="page"],
        [data-testid="stTopNavDropdownLink"][aria-current="page"] * {
            color: #0b3a66 !important;
            font-weight: 700 !important;
        }
        /* Logo de marca a la capçalera */
        [data-testid="stHeaderLogo"] {
            height: 30px !important;
        }

        /* ── Peu de pàgina global (utilitats fora del sidebar) ── */
        .p-foot-sep {
            border-top: 2px solid #1a2b3a;
            margin: 64px 0 28px;
        }
        .p-foot-links { font-family: 'Manrope', system-ui, sans-serif; }
        .p-foot-lab {
            font-size: 11px; font-weight: 700; letter-spacing: .14em;
            text-transform: uppercase; color: #5e6b78; margin-bottom: 12px;
        }
        .p-foot-links a {
            display: block; color: #0b3a66; text-decoration: none;
            font-size: 14px; font-weight: 600; line-height: 1.9;
        }
        .p-foot-links a:hover { color: #b07d2b; }
        .p-foot-legal {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 12px; color: #9aa6b2; margin: 36px 0 24px;
            border-top: 1px solid #e4e9ee; padding-top: 18px;
        }

        /* ── Components premium (consultora — pilot PIB i VAB) ── */
        .p-kicker {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 12px; font-weight: 700; letter-spacing: .16em;
            text-transform: uppercase; color: #b07d2b; margin-bottom: 0;
        }
        .p-kicker::after {
            content: ""; display: inline-block; width: 34px; height: 2px;
            background: #b07d2b; vertical-align: middle; margin-left: 14px;
        }
        .p-h1 {
            font-family: 'Manrope', system-ui, sans-serif !important;
            font-size: clamp(1.7rem, 3.5vw, 2.4rem) !important;
            font-weight: 800 !important; letter-spacing: -.025em !important;
            line-height: 1.1 !important; color: #1a2b3a !important;
            margin: 10px 0 0 !important; max-width: 26ch;
        }
        .p-deck {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 16px; line-height: 1.6; color: #37485a;
            margin: 14px 0 0; max-width: 62ch;
        }
        .p-takeaways {
            border-top: 2px solid #1a2b3a; padding: 20px 0 16px;
            margin: 28px 0 8px;
        }
        .p-tk-lab {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 11px; font-weight: 700; letter-spacing: .14em;
            text-transform: uppercase; color: #5e6b78; margin-bottom: 14px;
        }
        .p-takeaways ul {
            list-style: none; margin: 0; padding: 0; display: grid; gap: 11px;
        }
        .p-takeaways li {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 15px; line-height: 1.5; color: #37485a;
            padding-left: 20px; position: relative;
        }
        .p-takeaways li::before {
            content: ""; position: absolute; left: 0; top: 7px;
            width: 8px; height: 8px; background: #b07d2b; border-radius: 1px;
        }
        .p-takeaways li b { color: #1a2b3a; font-weight: 800; }
        .p-shock {
            background: #0b3a66; color: #e4e9ee; padding: 28px 28px 24px;
            margin: 28px 0 32px; display: flex; align-items: baseline;
            gap: 20px; flex-wrap: wrap;
        }
        .p-shock-v {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 3rem; font-weight: 800; letter-spacing: -.04em;
            color: #ffffff; line-height: 1; font-variant-numeric: tabular-nums;
        }
        .p-shock-u {
            font-size: 1.4rem; font-weight: 600; color: #b07d2b; margin-left: 2px;
        }
        .p-shock-l {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 15px; line-height: 1.5; color: #9aa6b2; max-width: 40ch;
        }
        .p-exhibit-no {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 11px; font-weight: 700; letter-spacing: .16em;
            text-transform: uppercase; color: #b07d2b; margin-bottom: 2px;
        }
        .p-exhibit-h2 {
            font-family: 'Manrope', system-ui, sans-serif !important;
            font-size: clamp(1.1rem, 2.2vw, 1.45rem) !important;
            font-weight: 800 !important; letter-spacing: -.015em !important;
            line-height: 1.2 !important; color: #1a2b3a !important;
            margin: 4px 0 14px !important; max-width: 44ch;
        }
        .p-note {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 15.5px; line-height: 1.6; color: #37485a;
            margin: 0 0 20px; max-width: 64ch;
        }
        .p-shock-sub {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 13px; color: #8aa0b8; margin-top: 14px;
            text-transform: uppercase; letter-spacing: .08em; font-weight: 600;
            flex-basis: 100%;
        }
        .p-metrics {
            margin-top: 36px; display: grid;
            grid-template-columns: repeat(4, 1fr); border-top: 2px solid #1a2b3a;
        }
        .p-metric {
            padding: 26px 18px; border-left: 1px solid #e4e9ee; text-align: center;
        }
        .p-metric:first-child { border-left: none; }
        .p-metric-v {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 1.9rem; font-weight: 800; letter-spacing: -.03em;
            color: #1a2b3a; line-height: 1; font-variant-numeric: tabular-nums;
        }
        .p-metric-u {
            font-size: .82rem; font-weight: 700; color: #0b3a66; margin-left: 2px;
        }
        .p-metric-l {
            font-family: 'Manrope', system-ui, sans-serif;
            font-size: 13px; color: #5e6b78; margin: 11px auto 0;
            line-height: 1.45; font-weight: 500; max-width: 24ch;
        }
        @media (max-width: 640px) {
            .p-metrics { grid-template-columns: 1fr 1fr; }
            .p-metric:nth-child(3) { border-left: none; }
            .p-metric:nth-child(3), .p-metric:nth-child(4) {
                border-top: 1px solid #e4e9ee;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    _inject_analytics()


def _inject_analytics():
    """Injecta script d'analítica Plausible si PLAUSIBLE_DOMAIN és definit.

    Activació: afegir PLAUSIBLE_DOMAIN als Secrets del Streamlit Cloud
    (Settings → Secrets), amb el domini del dashboard com a valor
    (p.ex. 'observatori-comerc.streamlit.app' o 'observatori.j3b3.com').

    Plausible és GDPR-compliant: sense cookies, sense banner de consentiment,
    dades agregades úniques. Pla Starter: https://plausible.io (9 €/mes).
    """
    domain = os.environ.get("PLAUSIBLE_DOMAIN", "").strip()
    if not domain:
        return
    st.markdown(
        f'<script defer data-domain="{domain}" '
        f'src="https://plausible.io/js/script.js"></script>',
        unsafe_allow_html=True,
    )


def page_header():
    """No-op. El logo J3B3 i la marca 'Observatorio' es mostren ara al
    sidebar via st.logo() a app.py. Es manté la funció buida per
    compatibilitat amb les crides existents a totes les pàgines."""
    return


def insight(text):
    """Mostra un bloc d'insight/conclusió."""
    title = "Anàlisi" if st.session_state.get("lang", "es") == "ca" else "Análisis"
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">{title}</div>
        {text}
    </div>
    """, unsafe_allow_html=True)


def intro(text):
    """Mostra un bloc introductori a l'inici de la pàgina."""
    st.markdown(f'<div class="intro-box">{text}</div>', unsafe_allow_html=True)


@contextlib.contextmanager
def highlight_expander(label, expanded=False):
    """Expander destacat amb subratllat groc al header per indicar
    contingut addicional rellevant (gràfics secundaris, anàlisi extra...).

    Ús: substitueix `st.expander(...)` per `highlight_expander(...)` als
    blocs on cal cridar l'atenció. NO usar per a expanders utilitaris
    (download de dades, info tècnica), que han de quedar amb estil pelat.

    Implementació: embolicalla l'expander dins un st.container(key=...)
    amb una key prefix 'highlight_expander_', que el CSS scoped detecta
    via class*="st-key-highlight_expander_" per aplicar el highlight groc.
    """
    global _highlight_expander_counter
    _highlight_expander_counter += 1
    key = f"highlight_expander_{_highlight_expander_counter}"
    with st.container(key=key):
        with st.expander(label, expanded=expanded):
            yield


# ─── Helpers editorials reutilitzables ──────────────────────────

NOMS_CCAA_EDITORIALS = {
    "Madrid (Comunidad de)": "Madrid",
    "Balears (Illes)": "Baleares",
    "Rioja (La)": "La Rioja",
    "Asturias (Principado de)": "Asturias",
    "Navarra (Comunidad Foral de)": "Navarra",
    "Murcia (Región de)": "Murcia",
    "Castilla - La Mancha": "Castilla-La Mancha",
}


def nom_ccaa_editorial(s):
    """Format editorial dels noms de CCAA per a textos generats.

    Mapeja noms literals del CSV (que mantenen la denominació institucional
    oficial) a versions netes per a frases narratives. Aplicar només a textos;
    CSVs, mapes, taules i etiquetes de gràfics mantenen els noms literals.
    """
    return NOMS_CCAA_EDITORIALS.get(s, s)


def minilectura(text):
    """Paràgraf gris discret sota un gràfic.

    Observació analítica curta (15-25 paraules) sense caixa ni border.
    Tipografia Inter, color gris fosc, line-height 1.5.
    """
    st.markdown(
        f'<div style="color:#6a6a6a; font-size:14px; line-height:1.55; '
        f'font-family:\'Inter\',sans-serif; '
        f'margin:12px 0 24px 0; font-style:italic;">{text}</div>',
        unsafe_allow_html=True,
    )


def lectura_vigent_box(titol, data_referencia,
                      autor="Observatorio del Comercio · J3B3 Consulting",
                      eyebrow="LECTURA VIGENTE"):
    """Caixa visual de Lectura Vigent a les pàgines de dades.

    Estètica editorial alt contrast: filet gruixut superior negre, eyebrow
    en Archivo Narrow uppercase sense letter-spacing forçat, titular gran
    amb tensió interpretativa, signatura corporativa discreta a sota.
    """
    st.markdown(
        f"""
        <div style="background:#ffffff; border-top:2px solid #003366;
                    padding:20px 0 18px 0; margin:18px 0 28px;
                    border-bottom:1px solid #d0d0d0;
                    font-family:'Inter',sans-serif;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.92rem;
                        font-weight:700; text-transform:uppercase;
                        color:#003366; margin-bottom:10px;">
                {eyebrow}
            </div>
            <div style="font-family:'Archivo Narrow',sans-serif; color:#003366;
                        font-size:1.45rem; font-weight:700; line-height:1.2;
                        margin-bottom:10px;">
                {titol}
            </div>
            <div style="color:#6a6a6a; font-size:12px;">
                {autor} · {data_referencia}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source(text):
    """Mostra la font de dades sota un gràfic, amb link a metodologia si escau."""
    lang = st.session_state.get("lang", "es")
    lbl = "Font" if lang == "ca" else "Fuente"
    if "Càlcul propi" in text or "Cálculo propio" in text:
        meto_lbl = "Veure metodologia" if lang == "ca" else "Ver metodología"
        extra = f' · <a href="/Metodologia" target="_self" style="color:#003366; border-bottom:1px solid #003366;">{meto_lbl}</a>'
    else:
        extra = ""
    st.markdown(f'<div class="source-label">{lbl}: {text}{extra}</div>', unsafe_allow_html=True)


# ─── MAPES: GEOJSON AMB INSET CANARIES ────────────────────────

# Coordenades del rectangle del inset (calculades amb les Canaries traslladades
# al sud-oest del mapa peninsular per evitar problemes d'escala estil meteorologic)
CANARIES_INSET_BOUNDS = {
    "lon_min": -13.0, "lon_max": -7.0,
    "lat_min": 33.7,  "lat_max": 36.3,
}

def load_geojson_spain_ccaa(with_canaries_inset=True):
    """Carrega el GeoJSON de CCAA. Si with_canaries_inset=True, retorna la
    versio amb les Canaries traslladades a un requadre al SO del mapa."""
    import json
    base = os.path.dirname(__file__)
    fname = "spain_ccaa_inset.geojson" if with_canaries_inset else "spain_ccaa.geojson"
    with open(os.path.join(base, "data", "geo", fname), "r") as f:
        return json.load(f)


def canaries_inset_layers():
    """Retorna les capes mapbox per dibuixar el requadre i l'etiqueta CANARIES
    al voltant de l'inset traslladat. Per usar com a `map_layers=...` al
    `update_layout` d'un fig Plotly amb Choroplethmap."""
    b = CANARIES_INSET_BOUNDS
    # Marge addicional al voltant del inset
    pad = 0.3
    lon_min = b["lon_min"] - pad
    lon_max = b["lon_max"] + pad
    lat_min = b["lat_min"] - pad
    lat_max = b["lat_max"] + pad
    rectangle = [
        [lon_min, lat_min], [lon_max, lat_min],
        [lon_max, lat_max], [lon_min, lat_max],
        [lon_min, lat_min],
    ]
    return [
        {
            "sourcetype": "geojson",
            "type": "line",
            "source": {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": rectangle},
            },
            "color": "rgba(10,10,10,0.55)",
            "line": {"width": 1.2},
        }
    ]


def cagr(first_val, last_val, years):
    """Calcula la taxa de creixement anual compost (CAGR)."""
    if first_val <= 0 or years <= 0:
        return 0
    return ((last_val / first_val) ** (1 / years) - 1) * 100


_MESOS_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
_MESOS_CA = ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
             "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]


def format_mes_any(dt, lang="es"):
    """Format 'Mes Any' en català o castellà sense dependre del locale del SO.

    strftime('%B %Y') retorna mesos en anglès si el locale no està configurat
    (típic en GitHub Actions / Streamlit Cloud). Aquesta funció força la
    traducció amb un diccionari estàtic.
    """
    if dt is None:
        return ""
    mes = _MESOS_CA[dt.month - 1] if lang == "ca" else _MESOS_ES[dt.month - 1]
    return f"{mes} {dt.year}"


def page_meta(sources, lang="es"):
    """Footer global de cada pàgina: branding, recursos, contacte i meta info.

    Manté la signatura històrica per no haver de modificar les pàgines existents.
    """
    update_path = os.path.join(os.path.dirname(__file__), "data", "cache", "last_update.txt")
    date_str = "—"
    if os.path.exists(update_path):
        with open(update_path, "r") as f:
            raw = f.read().strip()
        try:
            parts = raw.split(" ")
            ymd = parts[0].split("-")
            date_str = f"{ymd[2]}/{ymd[1]}/{ymd[0]} {parts[1]}"
        except (IndexError, ValueError):
            date_str = raw

    _ca = lang == "ca"

    brand_desc = ("Radiografia trimestral del comerç al detall espanyol. "
                  "Producte propi de J3B3 Consulting."
                  if _ca else
                  "Radiografía trimestral del comercio minorista español. "
                  "Producto propio de J3B3 Consulting.")
    col_about = "Sobre" if _ca else "Sobre"
    col_resources = "Recursos" if _ca else "Recursos"
    col_contact = "Contacte" if _ca else "Contacto"
    lbl_methodology = "Metodologia" if _ca else "Metodología"
    lbl_data_dl = "Descàrrega de dades" if _ca else "Descarga de datos"
    lbl_consulting = "J3B3 Consulting" if _ca else "J3B3 Consulting"
    lbl_about_obs = "Sobre l'observatori" if _ca else "Sobre el observatorio"
    lbl_email = "Correu electrònic" if _ca else "Correo electrónico"
    lbl_sources = "Fonts" if _ca else "Fuentes"
    lbl_update = "Última actualització" if _ca else "Última actualización"
    lbl_license = ("Llicència CC BY 4.0 · Citació recomanada"
                   if _ca else
                   "Licencia CC BY 4.0 · Cita recomendada")
    lbl_copy = "© 2026 J3B3 Consulting"

    st.markdown(
        f"""
        <div class="j3b3-footer">
            <div class="footer-grid">
                <div>
                    <div class="footer-brand-title">Observatori del Comerç Minorista</div>
                    <p class="footer-brand-desc">{brand_desc}</p>
                </div>
                <div>
                    <div class="footer-col-title">{col_about}</div>
                    <ul>
                        <li><a href="https://www.j3b3.com" target="_blank" rel="noopener">{lbl_consulting}</a></li>
                        <li><a href="https://www.j3b3.com/observatori-comerc" target="_blank" rel="noopener">{lbl_about_obs}</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-col-title">{col_resources}</div>
                    <ul>
                        <li>{lbl_methodology}</li>
                        <li>{lbl_data_dl}</li>
                        <li>{lbl_sources}: {sources}</li>
                    </ul>
                </div>
                <div>
                    <div class="footer-col-title">{col_contact}</div>
                    <ul>
                        <li><a href="mailto:observatorio@j3b3.com">observatorio@j3b3.com</a></li>
                        <li><a href="https://www.linkedin.com/company/j3b3-consulting/" target="_blank" rel="noopener">LinkedIn</a></li>
                        <li><a href="https://www.j3b3.com" target="_blank" rel="noopener">www.j3b3.com</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <div class="copy"><strong>{lbl_copy}</strong> · {lbl_license}</div>
                <div class="updated">{lbl_update}: {date_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_BREVO_LIST_ID = 4  # newsletter-observatorio (Brevo)


def _brevo_subscribe(email: str) -> tuple[bool, str]:
    """POST /v3/contacts. Retorna (ok, error_code) per a l'UI."""
    import sys
    import requests

    api_key = ""
    try:
        api_key = st.secrets.get("BREVO_API_KEY", "")
    except (FileNotFoundError, AttributeError):
        pass
    api_key = api_key or os.environ.get("BREVO_API_KEY", "")
    if not api_key:
        return False, "no_api_key"
    try:
        r = requests.post(
            "https://api.brevo.com/v3/contacts",
            headers={
                "api-key": api_key,
                "content-type": "application/json",
                "accept": "application/json",
            },
            json={
                "email": email,
                "listIds": [_BREVO_LIST_ID],
                "updateEnabled": True,
            },
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"[newsletter_form] Network error: {type(e).__name__}", file=sys.stderr)
        return False, "network"
    if r.status_code in (200, 201, 204):
        return True, ""
    if r.status_code == 400 and "duplicate" in r.text.lower():
        return True, ""
    print(
        f"[newsletter_form] Brevo {r.status_code}: {r.text[:300]}",
        file=sys.stderr,
    )
    return False, f"api_{r.status_code}"


def newsletter_form(lang="es", compact=False, sidebar=False):
    """Caixa de subscripció al butlletí (Brevo, llista newsletter-observatorio).

    compact=False: caixa gran amb capçalera (al peu d'Inici).
    compact=True: només descripció breu + form (per usar dins popover).
    sidebar=True: versió mínima per al sidebar (etiqueta + input + botó apilats).
    """
    _ca = lang == "ca"
    eyebrow = "Butlletí" if _ca else "Boletín"
    title = ("Rep El Pulso cada dilluns"
             if _ca else "Recibe El Pulso cada lunes")
    desc = ("Subscriu-te una vegada i rep dues cadències al teu correu: "
            "cada dilluns, <strong>El Pulso de la setmana</strong> —una xifra, "
            "tres notícies comentades i una predicció signada—; cada trimestre, "
            "el <strong>resum complet de l'observatori</strong> amb les xifres "
            "noves del comerç minorista i les conclusions destacades."
            if _ca else
            "Suscríbete una vez y recibe dos cadencias en tu correo: "
            "cada lunes, <strong>El Pulso de la semana</strong> —una cifra, "
            "tres noticias comentadas y una predicción firmada—; cada trimestre, "
            "el <strong>resumen completo del observatorio</strong> con las cifras "
            "nuevas del comercio minorista y las conclusiones destacadas.")
    desc_compact = ("El Pulso cada dilluns i el resum d'observatori cada trimestre. Una sola subscripció."
                    if _ca else
                    "El Pulso cada lunes y el resumen del observatorio cada trimestre. Una sola suscripción.")
    foot = ("Pots donar-te de baixa en qualsevol moment. Email gestionat amb Brevo."
            if _ca else
            "Puedes darte de baja en cualquier momento. Email gestionado con Brevo.")
    placeholder = "Adreça electrònica" if _ca else "Correo electrónico"
    submit_label = "Subscriu-me" if _ca else "Suscríbeme"
    ok_title = "Gràcies!" if _ca else "¡Gracias!"
    ok_desc = ("Ja estàs subscrit. El proper dilluns rebràs El Pulso al teu correu."
               if _ca else
               "Ya estás suscrito. El próximo lunes recibirás El Pulso en tu correo.")
    err_invalid = "Adreça no vàlida." if _ca else "Dirección no válida."
    err_generic = ("No s'ha pogut completar la subscripció. Torna-ho a provar més tard."
                   if _ca else
                   "No se ha podido completar la suscripción. Inténtalo de nuevo más tarde.")
    err_config = ("Servei no disponible. Avisa l'administrador."
                  if _ca else
                  "Servicio no disponible. Avisa al administrador.")

    if sidebar:
        label_sidebar = "El Pulso cada dilluns" if _ca else "El Pulso cada lunes"
        st.markdown(
            f'<div style="border-top:2px solid #E8B33A; padding-top:8px; margin-bottom:10px;">'
            f'<span style="font-family:\'Archivo Narrow\',sans-serif; font-size:0.82rem;'
            f' font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'
            f' color:#ffffff;">{label_sidebar}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] [data-testid="stForm"] {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
            }
            [data-testid="stSidebar"] .stTextInput > div > div > input {
                background: rgba(255,255,255,0.10) !important;
                border: 1px solid rgba(255,255,255,0.30) !important;
                color: #ffffff !important;
                border-radius: 0 !important;
            }
            [data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
                color: rgba(255,255,255,0.45) !important;
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
                background-color: #E8B33A !important;
                color: #003366 !important;
                border: none !important;
                font-weight: 700 !important;
                border-radius: 0 !important;
                font-size: 0.78rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.04em !important;
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button:hover {
                background-color: #c89b2a !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        form_key = f"newsletter_form_sidebar_{lang}"
        with st.form(form_key, clear_on_submit=True):
            email_raw = st.text_input(
                placeholder,
                key=f"{form_key}_email",
                label_visibility="collapsed",
                placeholder=placeholder,
            )
            submitted = st.form_submit_button(submit_label, use_container_width=True)
        if submitted:
            email = (email_raw or "").strip().lower()
            valid = ("@" in email and "." in email.split("@")[-1] and len(email) <= 254)
            if not valid:
                st.error(err_invalid)
            else:
                ok, err = _brevo_subscribe(email)
                if ok:
                    st.success(f"**{ok_title}** {ok_desc}")
                elif err == "no_api_key":
                    st.error(err_config)
                else:
                    st.error(err_generic)
        return

    if not compact:
        st.markdown(
            f"""
            <div class="newsletter-block">
                <div class="newsletter-eyebrow">{eyebrow}</div>
                <h3>{title}</h3>
                <p class="newsletter-desc">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p style="font-family:\'DM Sans\',sans-serif; font-size:0.9rem; '
            f'line-height:1.45; color:#1a1a1a; margin:0 0 12px 0;">{desc_compact}</p>',
            unsafe_allow_html=True,
        )

    form_key = f"newsletter_form_{'compact' if compact else 'full'}_{lang}"
    with st.form(form_key, clear_on_submit=True):
        col_input, col_button = st.columns([3, 1])
        with col_input:
            email_raw = st.text_input(
                placeholder,
                key=f"{form_key}_email",
                label_visibility="collapsed",
                placeholder=placeholder,
            )
        with col_button:
            submitted = st.form_submit_button(submit_label, use_container_width=True)

    if submitted:
        email = (email_raw or "").strip().lower()
        valid = ("@" in email and "." in email.split("@")[-1] and len(email) <= 254)
        if not valid:
            st.error(err_invalid)
        else:
            ok, err = _brevo_subscribe(email)
            if ok:
                st.success(f"**{ok_title}** {ok_desc}")
            elif err == "no_api_key":
                st.error(err_config)
            else:
                st.error(err_generic)

    foot_style = ("font-size:11px; color:#999; font-family:'DM Sans',sans-serif; margin-top:4px;"
                  if compact else "")
    if compact:
        st.markdown(f'<p style="{foot_style}">{foot}</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="newsletter-foot">{foot}</p>', unsafe_allow_html=True)


# ─── HELPERS PREMIUM (consultora — pilot PIB i VAB) ─────────────────────────

def inject_premium_page_css():
    """Sobreescriu tipografia i accents per a pàgines amb disseny premium.

    Cridar DESPRÉS d'inject_css(). Canvia Archivo Narrow → Manrope en tots
    els elements de la pàgina: headings, tabs, expanders, insight boxes, etc.
    El sidebar no es toca (és chrome global).
    """
    st.markdown("""
    <style>
    /* Tipografia global → Manrope */
    html, body,
    .stMarkdown, .stMarkdown p,
    [class*="css"] p, [class*="css"] li {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #37485a;
    }
    /* Headings: Manrope 800, navy fosc */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp .stMarkdown h1, .stApp .stMarkdown h2,
    .stApp .stMarkdown h3, .stApp .stMarkdown h4 {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #1a2b3a !important;
        letter-spacing: -.02em !important;
    }
    /* Tabs: Manrope, subratllat ocre */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Manrope', system-ui, sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #5e6b78 !important;
        font-size: 0.82rem !important;
        letter-spacing: .08em !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0b3a66 !important;
        border-bottom-color: #b07d2b !important;
        border-bottom-width: 3px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #e4e9ee !important;
    }
    /* Expander header: Manrope, navy */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details > summary,
    details > summary[role="button"] {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #0b3a66 !important;
        font-size: 0.9rem !important;
        letter-spacing: .04em !important;
    }
    /* Insight box: Manrope, acent ocre */
    .insight-box {
        font-family: 'Manrope', system-ui, sans-serif !important;
        border-top-color: #0b3a66 !important;
    }
    .insight-box .insight-title {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #b07d2b !important;
    }
    .insight-box strong {
        background: linear-gradient(180deg,
            transparent 0%, transparent 60%,
            rgba(176,125,43,0.25) 60%, rgba(176,125,43,0.25) 92%,
            transparent 92%) !important;
    }
    /* Source label */
    .source-label {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #9aa6b2 !important;
        font-size: 11.5px !important;
        letter-spacing: .05em !important;
    }
    /* Input labels */
    .stSelectbox label, .stMultiSelect label {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #0b3a66 !important;
    }
    /* Metric */
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span {
        font-family: 'Manrope', system-ui, sans-serif !important;
        color: #0b3a66 !important;
    }
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        font-family: 'Manrope', system-ui, sans-serif !important;
    }
    [data-testid="stMetric"] {
        border-top-color: #0b3a66 !important;
    }
    /* Highlight expander (highlight_expander) - canvia groc → ocre */
    [class*="st-key-highlight_expander_"] [data-testid="stExpander"] summary,
    div[class*="highlight_expander"] [data-testid="stExpander"] summary {
        background: linear-gradient(180deg,
            transparent 0%, transparent 55%,
            rgba(176,125,43,0.22) 55%, rgba(176,125,43,0.22) 92%,
            transparent 92%) !important;
    }
    [class*="st-key-highlight_expander_"] [data-testid="stExpander"] summary:hover,
    div[class*="highlight_expander"] [data-testid="stExpander"] summary:hover {
        background: linear-gradient(180deg,
            transparent 0%, transparent 30%,
            rgba(176,125,43,0.40) 30%, rgba(176,125,43,0.40) 95%,
            transparent 95%) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def kicker(text):
    """Eyebrow ocre uppercase amb línia decorativa."""
    st.markdown(f'<div class="p-kicker">{text}</div>', unsafe_allow_html=True)


def action_title(text):
    """Títol-tesi H1 premium: Manrope 800, navy fosc, màx 26ch."""
    st.markdown(f'<h1 class="p-h1">{text}</h1>', unsafe_allow_html=True)


def deck(text):
    """Paràgraf deck sota l'action title (1-2 frases, màx 62ch)."""
    st.markdown(f'<p class="p-deck">{text}</p>', unsafe_allow_html=True)


def key_takeaways(items, label="Conclusions clau"):
    """Bloc de 2-4 conclusions amb marca ocre. items: llista de strings (HTML permès)."""
    lis = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(
        f'<div class="p-takeaways">'
        f'<div class="p-tk-lab">{label}</div>'
        f'<ul>{lis}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )


def shock_stat(value, unit, label, sub=None):
    """Banda xifra-xoc: fons navy, valor gran blanc, unitat ocre, etiqueta gris.

    sub: caption opcional en majúscules sota la banda (ex. lectura del titular).
    """
    _sub = f'<div class="p-shock-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="p-shock">'
        f'<div class="p-shock-v">{value}<span class="p-shock-u">{unit}</span></div>'
        f'<div class="p-shock-l">{label}</div>'
        f'{_sub}'
        f'</div>',
        unsafe_allow_html=True,
    )


def exhibit_header(n, title, note=None):
    """Capçalera d'exhibit: número petit ocre + títol-tesi H2 Manrope.

    note: paràgraf explicatiu opcional sota el títol (1-2 frases, màx 64ch).
    """
    _note = f'<p class="p-note">{note}</p>' if note else ""
    st.markdown(
        f'<div class="p-exhibit-no">Ex. {n}</div>'
        f'<h2 class="p-exhibit-h2">{title}</h2>'
        f'{_note}',
        unsafe_allow_html=True,
    )


def metrics_band(items):
    """Banda final de KPIs: graella de mètriques amb separadors.

    items: llista de (value, unit, label). value/unit ja formatats (str).
    """
    cells = "".join(
        f'<div class="p-metric">'
        f'<div class="p-metric-v">{v}<span class="p-metric-u">{u}</span></div>'
        f'<div class="p-metric-l">{l}</div>'
        f'</div>'
        for v, u, l in items
    )
    st.markdown(f'<div class="p-metrics">{cells}</div>', unsafe_allow_html=True)


def premium_plotly_layout(height=480, margin_right=150, ytitle="M€"):
    """Layout Plotly premium: Manrope, navy+ocre, hover blanc, spike, separadors catalans."""
    return dict(
        font=dict(family="Manrope, system-ui, sans-serif", color=BODY_P, size=14),
        paper_bgcolor="white",
        plot_bgcolor="white",
        separators=",.",
        height=height,
        showlegend=False,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=LINE_P,
            font=dict(family="Manrope, sans-serif", color=INK_P, size=13),
        ),
        margin=dict(l=8, r=margin_right, t=14, b=42),
        xaxis=dict(
            tickfont=dict(color=G1_P, size=12),
            showgrid=False,
            showline=True,
            linecolor=LINE_P,
            linewidth=1,
            ticks="outside",
            tickcolor=LINE_P,
            dtick=5,
            showspikes=True,
            spikecolor=G2_P,
            spikethickness=1,
            spikedash="dot",
            spikemode="across",
            spikesnap="cursor",
        ),
        yaxis=dict(
            tickfont=dict(color=G1_P, size=12),
            title=dict(font=dict(color=G2_P, size=12), text=ytitle),
            showgrid=True,
            gridcolor=LINE_P,
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickformat=",.0f",
            automargin=True,
            rangemode="tozero",
        ),
    )


# ─── Frescor de dades (senyal de pàgina viva) ──────────────────
_UPDATES_LOG_CACHE = None

_MESOS_CA_1IDX = ["", "gener", "febrer", "març", "abril", "maig", "juny",
             "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]
_MESOS_ES_1IDX = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _load_updates_log():
    global _UPDATES_LOG_CACHE
    if _UPDATES_LOG_CACHE is None:
        p = os.path.join(os.path.dirname(__file__), "data", "cache", "updates_log.json")
        try:
            with open(p, encoding="utf-8") as f:
                _UPDATES_LOG_CACHE = json.load(f)
        except Exception:
            _UPDATES_LOG_CACHE = {}
    return _UPDATES_LOG_CACHE


def _fmt_period(s, ca):
    """'2024' | '2026-05' | '2026-04-01' -> text llegible (any / mes any / dia mes any)."""
    s = str(s).strip()
    parts = s.split("-")
    mesos = _MESOS_CA_1IDX if ca else _MESOS_ES_1IDX
    try:
        if len(parts) == 1:
            return parts[0]
        y, m = parts[0], int(parts[1])
        if len(parts) == 2:
            return f"{mesos[m]} {y}"
        d = int(parts[2])
        if d == 1:
            return f"{mesos[m]} {y}"
        return f"{d} de {mesos[m]} de {y}" if ca else f"{d} de {mesos[m]} de {y}"
    except (ValueError, IndexError):
        return s


def _fmt_detected(s, ca):
    """'2026-05-22' -> '22 de maig de 2026' / '22 de mayo de 2026'."""
    try:
        y, m, d = str(s).split("-")
        mesos = _MESOS_CA_1IDX if ca else _MESOS_ES_1IDX
        return f"{int(d)} de {mesos[int(m)]} de {y}"
    except (ValueError, IndexError):
        return str(s)


def freshness_badge(datasets, lang="es"):
    """Subtítol discret de frescor, per fer que la pàgina sembli viva.

    Ex.: 'Actualitzat 26 de juny de 2026 · dades fins a maig 2026'.
    datasets: clau o llista de claus de updates_log.json['datasets'].
    Mostra l'entrada amb detected_at més recent; si no n'hi ha cap, no renderitza res.
    """
    if isinstance(datasets, str):
        datasets = [datasets]
    log = _load_updates_log().get("datasets", {})
    entries = [log[d] for d in datasets if d in log and log[d].get("detected_at")]
    if not entries:
        return
    best = max(entries, key=lambda e: e.get("detected_at", ""))
    ca = lang == "ca"
    updated = _fmt_detected(best.get("detected_at", ""), ca)
    period = _fmt_period(best.get("last_data", ""), ca)
    lbl_upd = "Actualitzat" if ca else "Actualizado"
    lbl_data = "dades fins a" if ca else "datos hasta"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin:-6px 0 20px 0;'
        f'font-family:Manrope,system-ui,sans-serif;font-size:0.82rem;color:{G1_P};">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{OCRE};'
        f'box-shadow:0 0 0 3px rgba(176,125,43,0.15);flex:none;"></span>'
        f'<span>{lbl_upd} <b style="color:{INK_P};font-weight:600;">{updated}</b>'
        f' · {lbl_data} {period}</span></div>',
        unsafe_allow_html=True,
    )


# ─── HOME (portada-resum, arquitectura home_v5) ─────────────────────────────
# Components exclusius de la portada: banda de xifres amb delta, capçaleres i
# peus de les figures, pull-quote editorial i llista numerada de dimensions.
# Es carreguen amb inject_home_css() DESPRÉS d'inject_premium_page_css().

def inject_home_css():
    """CSS dels blocs propis de la portada (banda de xifres, figures, tesi, llista)."""
    st.markdown("""
    <style>
    /* ── banda de xifres estructurals ── */
    .h-stats {
        display: grid; grid-template-columns: repeat(4, 1fr);
        border-top: 2px solid #1a2b3a; border-bottom: 1px solid #e4e9ee;
        margin: 30px 0 6px;
    }
    .h-stat { padding: 24px 22px; border-left: 1px solid #e4e9ee; }
    .h-stat:first-child { border-left: none; padding-left: 0; }
    .h-stat-v {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 1.95rem; font-weight: 800; letter-spacing: -.03em;
        color: #1a2b3a; line-height: 1; font-variant-numeric: tabular-nums;
    }
    .h-stat-u { font-size: .95rem; font-weight: 700; color: #0b3a66; margin-left: 2px; }
    .h-stat-l {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 13px; color: #5e6b78; font-weight: 500;
        line-height: 1.45; margin-top: 9px; max-width: 22ch;
    }
    .h-stat-d {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 12.5px; font-weight: 700; margin-top: 7px;
        font-variant-numeric: tabular-nums;
    }
    .h-stat-d.up { color: #1f7a4d; }
    .h-stat-d.down { color: #b03a2e; }
    .h-stat-d.flat { color: #9aa6b2; }
    @media (max-width: 900px) {
        .h-stats { grid-template-columns: 1fr 1fr; }
        .h-stat:nth-child(3) { border-left: none; padding-left: 0; }
        .h-stat:nth-child(3), .h-stat:nth-child(4) { border-top: 1px solid #e4e9ee; }
    }

    /* ── capçalera i peu de figura (targeta) ── */
    .h-fig-eyebrow {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 11.5px; font-weight: 700; letter-spacing: .12em;
        text-transform: uppercase; color: #b07d2b;
    }
    .h-fig-title {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 17px; font-weight: 800; color: #1a2b3a;
        letter-spacing: -.015em; line-height: 1.25; margin-top: 5px;
    }
    .h-fig-sub {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 13.5px; color: #5e6b78; line-height: 1.5; margin-top: 6px;
    }
    .h-fig-foot {
        display: flex; justify-content: space-between; align-items: baseline;
        gap: 14px; flex-wrap: wrap; border-top: 1px solid #e4e9ee;
        margin-top: 4px; padding-top: 11px;
        font-family: 'Manrope', system-ui, sans-serif;
    }
    .h-fig-src { font-size: 11.5px; color: #9aa6b2; }
    .h-fig-last {
        font-size: 13px; font-weight: 700; color: #0b3a66;
        font-variant-numeric: tabular-nums; white-space: nowrap;
    }
    .h-legend { display: flex; gap: 18px; flex-wrap: wrap; margin: 10px 0 2px; }
    .h-legend span {
        display: inline-flex; align-items: center; gap: 7px;
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 12.5px; font-weight: 600; color: #37485a;
    }
    .h-legend i { width: 11px; height: 11px; border-radius: 2px; display: inline-block; }

    /* ── intro de secció ── */
    .h-sec-eyebrow {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 12px; font-weight: 700; letter-spacing: .14em;
        text-transform: uppercase; color: #b07d2b; margin-bottom: 10px;
    }
    .h-sec-h2 {
        font-family: 'Manrope', system-ui, sans-serif !important;
        font-size: clamp(1.35rem, 2.4vw, 1.85rem) !important;
        font-weight: 800 !important; letter-spacing: -.02em !important;
        line-height: 1.15 !important; color: #1a2b3a !important; margin: 0 !important;
    }
    .h-sec-p {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 16px; line-height: 1.6; color: #37485a;
        margin: 12px 0 0; max-width: 62ch;
    }

    /* ── tesi editorial (pull-quote + aside) ── */
    /* Sense barra lateral: el filet decoratiu va sota la cita, no al costat. */
    .h-quote {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: clamp(1.2rem, 1.9vw, 1.55rem); font-weight: 600;
        line-height: 1.4; color: #1a2b3a; max-width: 32ch;
        margin: 0 !important; padding: 0 !important;
        border: none !important; background: none !important;
        font-style: normal !important; quotes: none;
        opacity: 1 !important;  /* Streamlit apaga els blockquote al 60% */
    }
    .h-quote::before, .h-quote::after { content: none !important; }
    .h-quote-src {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 13.5px; font-weight: 600; color: #5e6b78; margin-top: 20px;
    }
    .h-quote-src::before {
        content: ""; display: block; width: 40px; height: 2px;
        background: #b07d2b; margin-bottom: 15px;
    }
    .h-quote-src .d { color: #0b3a66; }
    .h-aside {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 15.5px; line-height: 1.65; color: #37485a;
    }
    .h-aside p + p { margin-top: 13px; }

    /* ── llista numerada de dimensions ── */
    .h-field {
        display: grid; grid-template-columns: auto 1fr; gap: 18px;
        padding: 20px 0 6px; border-top: 1px solid #e4e9ee; align-items: baseline;
    }
    .h-field-n {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 13.5px; font-weight: 800; color: #b07d2b;
        font-variant-numeric: tabular-nums; letter-spacing: .04em;
    }
    .h-field-t {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 17px; font-weight: 800; color: #1a2b3a;
        letter-spacing: -.015em; margin-bottom: 4px;
    }
    .h-field-p {
        font-family: 'Manrope', system-ui, sans-serif;
        font-size: 14px; color: #5e6b78; line-height: 1.5;
    }

    /* ── tira de novetats ── */
    .h-upd-row {
        display: flex; justify-content: space-between; align-items: baseline;
        gap: 12px; padding: 7px 0; border-bottom: 1px solid #eef1f5;
        font-family: 'Manrope', system-ui, sans-serif;
    }
    .h-upd-row span.l { font-size: 13px; color: #37485a; }
    .h-upd-row span.l b { color: #0b3a66; font-weight: 700; }
    .h-upd-row span.r { font-size: 11.5px; color: #9aa6b2; white-space: nowrap; }

    /* ── butlletí: el bloc gran només surt a la portada, l'entrem a la paleta ── */
    .newsletter-block { border-top-color: #1a2b3a !important; }
    .newsletter-block .newsletter-eyebrow {
        font-family: 'Manrope', system-ui, sans-serif !important;
        font-size: 12px !important; letter-spacing: .14em !important;
        color: #b07d2b !important;
    }
    .newsletter-block h3 {
        font-family: 'Manrope', system-ui, sans-serif !important;
        font-size: clamp(1.35rem, 2.4vw, 1.85rem) !important;
        font-weight: 800 !important; color: #1a2b3a !important;
        letter-spacing: -.02em !important;
    }
    .newsletter-block .newsletter-desc {
        font-family: 'Manrope', system-ui, sans-serif !important;
        font-size: 16px !important; color: #37485a !important;
    }
    .newsletter-block .newsletter-desc strong {
        background: linear-gradient(180deg, transparent 0%, transparent 60%,
                    rgba(176,125,43,0.25) 60%, rgba(176,125,43,0.25) 92%,
                    transparent 92%) !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)


def home_stats(items):
    """Banda de xifres estructurals de la portada.

    items: llista de (value, unit, label, delta, direction) amb direction
    'up' | 'down' | 'flat' | None (sense línia de delta).
    """
    cells = ""
    for value, unit, label, delta, direction in items:
        _u = f'<span class="h-stat-u">{unit}</span>' if unit else ""
        _d = (f'<div class="h-stat-d {direction or "flat"}">{delta}</div>'
              if delta else "")
        cells += (f'<div class="h-stat">'
                  f'<div class="h-stat-v">{value}{_u}</div>'
                  f'<div class="h-stat-l">{label}</div>{_d}</div>')
    st.markdown(f'<div class="h-stats">{cells}</div>', unsafe_allow_html=True)


def home_section(eyebrow, title, text=None):
    """Intro de secció de la portada: eyebrow ocre + H2-tesi + paràgraf."""
    _p = f'<p class="h-sec-p">{text}</p>' if text else ""
    st.markdown(
        f'<div class="h-sec-eyebrow">{eyebrow}</div>'
        f'<h2 class="h-sec-h2">{title}</h2>{_p}',
        unsafe_allow_html=True,
    )


def home_fig_head(eyebrow, title, sub=None, legend=None):
    """Capçalera d'una figura de la portada. legend: llista de (color, etiqueta)."""
    _sub = f'<div class="h-fig-sub">{sub}</div>' if sub else ""
    _leg = ""
    if legend:
        _leg = ('<div class="h-legend">' + "".join(
            f'<span><i style="background:{c}"></i>{lab}</span>' for c, lab in legend
        ) + '</div>')
    st.markdown(
        f'<div class="h-fig-eyebrow">{eyebrow}</div>'
        f'<div class="h-fig-title">{title}</div>{_sub}{_leg}',
        unsafe_allow_html=True,
    )


def home_fig_foot(src, last=None):
    """Peu d'una figura de la portada: font a l'esquerra, última lectura a la dreta."""
    _last = f'<span class="h-fig-last">{last}</span>' if last else ""
    st.markdown(
        f'<div class="h-fig-foot"><span class="h-fig-src">{src}</span>{_last}</div>',
        unsafe_allow_html=True,
    )


def home_quote(text, source_line):
    """Pull-quote editorial de la portada, amb filet ocre sobre la línia de font."""
    st.markdown(
        f'<blockquote class="h-quote">{text}</blockquote>'
        f'<div class="h-quote-src">{source_line}</div>',
        unsafe_allow_html=True,
    )


def home_field(num, title, text):
    """Entrada de la llista numerada de dimensions (el page_link va a continuació)."""
    st.markdown(
        f'<div class="h-field"><span class="h-field-n">{num}</span>'
        f'<div><div class="h-field-t">{title}</div>'
        f'<div class="h-field-p">{text}</div></div></div>',
        unsafe_allow_html=True,
    )

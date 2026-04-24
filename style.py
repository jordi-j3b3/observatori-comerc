"""
Estils compartits: layout Plotly, CSS global, helpers de presentació.
"""
import streamlit as st
import os
import json

# ─── COLORS ───────────────────────────────────────────────────

PURPLE = "#5d4fff"
PURPLE_LIGHT = "#aaa3ff"
PURPLE_BG = "#F5F4FF"
RED = "#E74C3C"
BLUE = "#2E86C1"
GREEN = "#27AE60"
ORANGE = "#F39C12"
DARK = "#02000F"
GRAY = "#BDC3C7"
GRAY_DARK = "#7F8C8D"

PALETTE = [PURPLE, RED, GREEN, ORANGE, "#8E44AD", "#1ABC9C", "#E67E22", "#3498DB", "#2C3E50", "#D35400"]


# ─── FORMAT NUMÈRIC (europeu: 1.234,56) ─────────────────────

def fnum(n, decimals=0):
    """Formata un nombre amb punt per milers i coma per decimals."""
    if n is None:
        return "—"
    if decimals == 0:
        return f"{int(round(n)):,}".replace(",", ".")
    formatted = f"{n:,.{decimals}f}"
    # Swap: , → temp, . → , temp → .
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def fpct(n, decimals=1, sign=True):
    """Formata un percentatge amb format europeu. Evita +0,0% / -0,0%."""
    if n is None:
        return "—"
    # Arrodonir i evitar -0,0 o +0,0
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
    font=dict(family="Manrope, sans-serif", size=13, color=DARK),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=60, r=20, t=40, b=50),
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Manrope, sans-serif",
        bordercolor="#ddd",
    ),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.06)",
        linecolor="rgba(0,0,0,0.1)",
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.06)",
        linecolor="rgba(0,0,0,0.1)",
        zeroline=False,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=12),
    ),
    hovermode="x unified",
)


def apply_layout(fig, **overrides):
    """Aplica el layout estàndard a un gràfic Plotly amb overrides opcionals."""
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


# ─── i18n COMPARTIT ──────────────────────────────────────────

@st.cache_data
def _load_translations():
    path = os.path.join(os.path.dirname(__file__), "i18n", "translations.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_lang(show_selector=True):
    """Configura l'idioma: inicialitza session_state i retorna funció t()."""
    TRANS = _load_translations()
    if "lang" not in st.session_state:
        st.session_state.lang = "ca"

    if show_selector:
        with st.sidebar:
            lang_options = {"Català": "ca", "Castellano": "es"}
            selected = st.selectbox(
                "Idioma",
                list(lang_options.keys()),
                index=0 if st.session_state.lang == "ca" else 1,
            )
            st.session_state.lang = lang_options[selected]

    def t(key):
        return TRANS.get(st.session_state.lang, {}).get(key, key)

    return t


# ─── CSS GLOBAL ───────────────────────────────────────────────

def inject_css():
    """Injecta CSS global a la pàgina (cridar a cada page)."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

        /* Tipografia global */
        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'Manrope', sans-serif;
            font-weight: 700;
            color: #02000F;
        }

        /* Accent principal */
        .stMetricValue { color: #5d4fff !important; font-weight: 700; }
        .stMetricDelta svg { display: inline; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #02000F;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #FFFFFF !important;
        }

        /* Botons */
        .stDownloadButton button {
            background-color: #5d4fff;
            color: white;
            border: none;
            border-radius: 6px;
            font-family: 'Manrope', sans-serif;
            font-weight: 600;
        }
        .stDownloadButton button:hover {
            background-color: #4a3fd9;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            font-family: 'Manrope', sans-serif;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            border-bottom-color: #5d4fff !important;
        }

        /* Dividers */
        hr { border-color: #F5F4FF !important; }

        /* Cards de mètriques */
        [data-testid="stMetric"] {
            background-color: #FAFAFA;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #5d4fff;
        }

        /* Insight box */
        .insight-box {
            background: linear-gradient(135deg, #F5F4FF 0%, #FAFAFA 100%);
            border-left: 4px solid #5d4fff;
            border-radius: 0 10px 10px 0;
            padding: 20px 24px;
            margin: 16px 0 24px 0;
            font-family: 'Manrope', sans-serif;
            font-size: 0.95rem;
            line-height: 1.7;
            color: #02000F;
        }
        .insight-box strong {
            color: #5d4fff;
        }
        .insight-box .insight-title {
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #5d4fff;
            margin-bottom: 8px;
        }

        /* Intro box */
        .intro-box {
            background: #FAFAFA;
            border-radius: 10px;
            padding: 20px 24px;
            margin: 0 0 24px 0;
            font-family: 'Manrope', sans-serif;
            font-size: 0.93rem;
            line-height: 1.7;
            color: #333;
        }

        /* Font de dades */
        .source-label {
            font-family: 'Manrope', sans-serif;
            font-size: 0.78rem;
            color: #999;
            margin-top: -8px;
            margin-bottom: 20px;
            padding-left: 4px;
        }

        /* Meta info (data actualització) */
        .meta-info {
            font-family: 'Manrope', sans-serif;
            font-size: 0.8rem;
            color: #999;
            border-top: 1px solid #eee;
            padding-top: 12px;
            margin-top: 30px;
        }

        /* Logo header */
        .j3b3-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.5rem;
        }
        .j3b3-header img {
            height: 36px;
        }
        .j3b3-badge {
            background-color: #5d4fff;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'Manrope', sans-serif;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-family: 'Manrope', sans-serif;
            font-weight: 600;
        }

        /* Selectbox */
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        .stMultiSelect > div > div {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


def insight(text):
    """Mostra un bloc d'insight/conclusió."""
    title = "Anàlisi" if st.session_state.get("lang", "ca") == "ca" else "Análisis"
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">{title}</div>
        {text}
    </div>
    """, unsafe_allow_html=True)


def intro(text):
    """Mostra un bloc introductori a l'inici de la pàgina."""
    st.markdown(f'<div class="intro-box">{text}</div>', unsafe_allow_html=True)


def source(text):
    """Mostra la font de dades sota un gràfic, amb link a metodologia si escau."""
    lang = st.session_state.get("lang", "ca")
    lbl = "Font" if lang == "ca" else "Fuente"
    # Afegir link a metodologia quan hi ha càlcul propi
    if "Càlcul propi" in text or "Cálculo propio" in text:
        meto_lbl = "Veure metodologia" if lang == "ca" else "Ver metodología"
        extra = f' · <a href="/Metodologia" target="_self" style="color:#5d4fff;">{meto_lbl}</a>'
    else:
        extra = ""
    st.markdown(f'<div class="source-label">{lbl}: {text}{extra}</div>', unsafe_allow_html=True)


def cagr(first_val, last_val, years):
    """Calcula la taxa de creixement anual compost (CAGR)."""
    if first_val <= 0 or years <= 0:
        return 0
    return ((last_val / first_val) ** (1 / years) - 1) * 100


def page_meta(sources, lang="ca"):
    """Mostra la meta info al final de la pàgina: fonts i data d'actualització."""
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

    lbl_update = "Última actualització de dades" if lang == "ca" else "Última actualización de datos"
    lbl_fonts = "Fonts" if lang == "ca" else "Fuentes"
    st.markdown(
        f'<div class="meta-info">{lbl_fonts}: {sources} · {lbl_update}: {date_str}</div>',
        unsafe_allow_html=True,
    )

"""
Estils compartits: layout Plotly, CSS global, helpers de presentació.
Disseny editorial basat en DM Serif Display + DM Sans.
"""
import streamlit as st
import os
import json

# ─── COLORS ───────────────────────────────────────────────────

PURPLE = "#0055a4"
PURPLE_LIGHT = "#5a9fd4"
PURPLE_BG = "#e8f0fe"
RED = "#c0392b"
BLUE = "#2980b9"
GREEN = "#27ae60"
ORANGE = "#e67e22"
DARK = "#1a1a1a"
GRAY = "#bdc3c7"
GRAY_DARK = "#7f8c8d"

PALETTE = [PURPLE, RED, GREEN, ORANGE, "#8e44ad", "#1abc9c", "#e67e22", "#3498db", "#2c3e50", "#d35400"]


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
    font=dict(family="DM Sans, sans-serif", size=13, color=DARK),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=60, r=20, t=40, b=50),
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="DM Sans, sans-serif",
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

@st.cache_data(ttl=300)
def _load_translations():
    path = os.path.join(os.path.dirname(__file__), "i18n", "translations.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_lang(show_selector=True):
    """Configura l'idioma: inicialitza session_state i retorna funció t().

    Per defecte: castellà (es). El selector ca/es es manté visible al header.
    """
    TRANS = _load_translations()
    if "lang" not in st.session_state:
        st.session_state.lang = "es"

    if show_selector:
        with st.sidebar:
            # Ordre: Castellano primer (default), Català segon
            lang_options = {"Castellano": "es", "Català": "ca"}
            selected = st.selectbox(
                "Idioma",
                list(lang_options.keys()),
                index=0 if st.session_state.lang == "es" else 1,
            )
            st.session_state.lang = lang_options[selected]

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
        @import url('https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;500;700&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@1,400;1,500&family=IBM+Plex+Mono:wght@500;700&display=swap');

        /* Tipografia global */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        h1, .stMarkdown h1 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #0a0a0a;
            font-size: 2.6rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.5px;
        }
        h2, .stMarkdown h2 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #0a0a0a;
            font-size: 1.9rem !important;
            line-height: 1.1 !important;
        }
        h3, .stMarkdown h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            color: #0a0a0a;
            font-size: 1.4rem !important;
            line-height: 1.15 !important;
        }
        h4, h5, h6,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            color: #0a0a0a;
        }

        /* Mètriques: tinta negra + mono per al valor (numèric) */
        .stMetricValue {
            color: #0a0a0a !important;
            font-weight: 700 !important;
            font-family: 'IBM Plex Mono', monospace !important;
        }
        .stMetricLabel {
            font-family: 'Archivo Narrow', sans-serif !important;
            text-transform: uppercase;
            color: #6a6a6a !important;
        }
        .stMetricDelta svg { display: inline; }

        /* Sidebar (es manté fosc per coherència de chrome) */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
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

        /* Botons */
        .stDownloadButton button {
            background-color: #0a0a0a;
            color: #ffffff;
            border: none;
            border-radius: 0;
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
        }
        .stDownloadButton button:hover {
            background-color: #1a1a1a;
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
            color: #0a0a0a !important;
            border-bottom-color: #0a0a0a !important;
            border-bottom-width: 3px !important;
        }

        /* Dividers */
        hr { border-color: #d0d0d0 !important; }

        /* Cards de mètriques: filet negre lateral curt, sense fons gris */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 0;
            padding: 14px 16px;
            border-left: 3px solid #0a0a0a;
        }

        /* Insight box — fons blanc, filet gruixut superior negre + accent groc */
        .insight-box {
            background: #ffffff;
            border-top: 3px solid #0a0a0a;
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
            color: #0a0a0a;
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
            border-top: 6px solid #0a0a0a;
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
            color: #0a0a0a;
            margin-bottom: 10px;
            letter-spacing: 0;
        }
        .conclusions-block h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            color: #0a0a0a !important;
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
            color: #0a0a0a;
        }

        /* Newsletter (subscripció combinada Pulso setmanal + trimestral) */
        .newsletter-block {
            background: #ffffff;
            border: none;
            border-top: 4px solid #0a0a0a;
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
            color: #0a0a0a;
            margin-bottom: 10px;
            letter-spacing: 0;
        }
        .newsletter-block h3 {
            font-family: 'Archivo Narrow', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.7rem !important;
            color: #0a0a0a !important;
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
            border-top: 4px solid #0a0a0a;
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
            color: #0a0a0a;
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
            color: #0a0a0a !important;
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
            border-top: 3px solid #0a0a0a;
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
            color: #0a0a0a;
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
            color: #0a0a0a;
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
            color: #0a0a0a;
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
            color: #0a0a0a;
            letter-spacing: 0;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-family: 'Archivo Narrow', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
        }

        /* Selectbox */
        .stSelectbox > div > div {
            border-radius: 0;
        }
        .stMultiSelect > div > div {
            border-radius: 0;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header():
    """Mostra la capçalera J3B3 + OBSERVATORI a qualsevol pàgina. Logo enllaça a j3b3.com."""
    lang = st.session_state.get("lang", "es")
    badge = "OBSERVATORI" if lang == "ca" else "OBSERVATORIO"
    st.markdown(f"""
    <div class="j3b3-header">
        <a href="https://www.j3b3.com" target="_blank" rel="noopener" style="display:inline-flex; align-items:center;">
            <img src="https://www.j3b3.com/wp-content/uploads/2025/04/logo-j3b3-new.svg" alt="J3B3 Consulting">
        </a>
        <span class="j3b3-badge">{badge}</span>
    </div>
    """, unsafe_allow_html=True)


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
        <div style="background:#ffffff; border-top:4px solid #0a0a0a;
                    padding:20px 0 18px 0; margin:18px 0 28px;
                    border-bottom:1px solid #d0d0d0;
                    font-family:'Inter',sans-serif;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.92rem;
                        font-weight:700; text-transform:uppercase;
                        color:#0a0a0a; margin-bottom:10px;">
                {eyebrow}
            </div>
            <div style="font-family:'Archivo Narrow',sans-serif; color:#0a0a0a;
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
        extra = f' · <a href="/Metodologia" target="_self" style="color:#0a0a0a; border-bottom:1px solid #0a0a0a;">{meto_lbl}</a>'
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
                        <li><a href="mailto:info@j3b3.com">info@j3b3.com</a></li>
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


def newsletter_form(lang="es", compact=False):
    """Caixa de subscripció al butlletí trimestral (MailerLite embed).

    compact=False: caixa gran amb capçalera (al peu d'Inici).
    compact=True: només descripció breu + form (per usar dins popover).
    """
    import streamlit.components.v1 as components

    _ca = lang == "ca"
    eyebrow = "Butlletí" if _ca else "Boletín"
    title = ("Rep El Pulso cada dilluns"
             if _ca else "Recibe El Pulso cada lunes")
    desc = ("Subscriu-te una vegada i rep dues cadències al teu correu: "
            "cada dilluns, <strong>El Pulso de la setmana</strong> —una xifra, "
            "tres notícies amb angle i una predicció signada—; cada trimestre, "
            "el <strong>resum complet de l'observatori</strong> amb les xifres "
            "noves del comerç minorista i les conclusions destacades."
            if _ca else
            "Suscríbete una vez y recibe dos cadencias en tu correo: "
            "cada lunes, <strong>El Pulso de la semana</strong> —una cifra, "
            "tres noticias con ángulo y una predicción firmada—; cada trimestre, "
            "el <strong>resumen completo del observatorio</strong> con las cifras "
            "nuevas del comercio minorista y las conclusiones destacadas.")
    desc_compact = ("El Pulso cada dilluns i el resum d'observatori cada trimestre. Una sola subscripció."
                    if _ca else
                    "El Pulso cada lunes y el resumen del observatorio cada trimestre. Una sola suscripción.")
    foot = ("Pots donar-te de baixa en qualsevol moment. Email gestionat amb MailerLite."
            if _ca else
            "Puedes darte de baja en cualquier momento. Email gestionado con MailerLite.")
    placeholder = "Adreça electrònica" if _ca else "Correo electrónico"
    submit_label = "Subscriu-me" if _ca else "Suscríbeme"
    ok_title = "Gràcies!" if _ca else "¡Gracias!"
    ok_desc = ("T'hem enviat un correu de confirmació. Cal que el confirmis "
               "per activar la subscripció."
               if _ca else
               "Te hemos enviado un correo de confirmación. Debes confirmarlo "
               "para activar la suscripción.")

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

    html_path = os.path.join(os.path.dirname(__file__), "assets", "newsletter_mailerlite.html")
    with open(html_path, "r", encoding="utf-8") as f:
        snippet = f.read()
    snippet = (snippet
               .replace("__SUCCESS_TITLE__", "")
               .replace("__SUCCESS_DESC__", "")
               .replace("__EMAIL_PLACEHOLDER__", placeholder)
               .replace("__SUBMIT_LABEL__", submit_label)
               .replace("__SUCCESS_OK_TITLE__", ok_title)
               .replace("__SUCCESS_OK_DESC__", ok_desc))

    components.html(snippet, height=160, scrolling=False)
    foot_style = ("font-size:11px; color:#999; font-family:'DM Sans',sans-serif; margin-top:4px;"
                  if compact else "")
    if compact:
        st.markdown(f'<p style="{foot_style}">{foot}</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="newsletter-foot">{foot}</p>', unsafe_allow_html=True)

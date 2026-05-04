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
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600;700&display=swap');

        /* Tipografia global */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        h1, .stMarkdown h1 {
            font-family: 'DM Serif Display', serif !important;
            font-weight: 400 !important;
            color: #0a0a0a;
            font-size: 2.2rem !important;
        }
        h2, h3, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'DM Serif Display', serif !important;
            font-weight: 400 !important;
            color: #1a1a1a;
        }
        h4, h5, h6,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'DM Sans', sans-serif;
            font-weight: 600;
            color: #1a1a1a;
        }

        /* Accent principal */
        .stMetricValue { color: #0055a4 !important; font-weight: 700; }
        .stMetricDelta svg { display: inline; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #FFFFFF !important;
        }

        /* Botons */
        .stDownloadButton button {
            background-color: #0055a4;
            color: white;
            border: none;
            border-radius: 3px;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            font-size: 14px;
        }
        .stDownloadButton button:hover {
            background-color: #003d7a;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            border-bottom-color: #0055a4 !important;
        }

        /* Dividers */
        hr { border-color: #e0e0e0 !important; }

        /* Cards de mètriques */
        [data-testid="stMetric"] {
            background-color: #fcfcfc;
            border-radius: 4px;
            padding: 15px;
            border-left: 3px solid #0055a4;
        }

        /* Insight box */
        .insight-box {
            background: #f4f4f2;
            border-left: 3px solid #0055a4;
            border-radius: 0 4px 4px 0;
            padding: 24px 28px;
            margin: 16px 0 24px 0;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            line-height: 1.7;
            color: #1a1a1a;
        }
        .insight-box strong {
            color: #0055a4;
        }
        .insight-box .insight-title {
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #0055a4;
            margin-bottom: 10px;
        }

        /* Intro box */
        .intro-box {
            background: #f4f4f2;
            border-radius: 4px;
            padding: 24px 28px;
            margin: 0 0 24px 0;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.93rem;
            line-height: 1.7;
            color: #555;
        }

        /* Conclusions block (Inici) */
        .conclusions-block {
            background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
            border: 1px solid #d8e2f0;
            border-left: 4px solid #0055a4;
            border-radius: 6px;
            padding: 28px 32px;
            margin: 24px 0 24px 0;
            box-shadow: 0 2px 8px rgba(0, 85, 164, 0.06);
        }
        .conclusions-block .conclusions-eyebrow {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #0055a4;
            margin-bottom: 8px;
        }
        .conclusions-block h3 {
            font-family: 'DM Serif Display', serif !important;
            font-weight: 400 !important;
            font-size: 1.6rem !important;
            color: #0a0a0a !important;
            margin: 0 0 12px 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        .conclusions-block .conclusions-update {
            font-size: 12px;
            color: #999;
            margin-bottom: 16px;
            font-style: italic;
        }
        .conclusions-block ul {
            margin: 0;
            padding-left: 20px;
        }
        .conclusions-block li {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            line-height: 1.7;
            color: #1a1a1a;
            margin-bottom: 10px;
        }
        .conclusions-block li strong {
            color: #0055a4;
        }

        /* Newsletter (subscripció butlletí trimestral) */
        .newsletter-block {
            background: linear-gradient(180deg, #fffbf3 0%, #ffffff 100%);
            border: 1px solid #ead9b8;
            border-left: 4px solid #c89a3c;
            border-radius: 6px;
            padding: 24px 28px 12px 28px;
            margin: 24px 0;
            box-shadow: 0 2px 8px rgba(200, 154, 60, 0.08);
        }
        .newsletter-block .newsletter-eyebrow {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #c89a3c;
            margin-bottom: 8px;
        }
        .newsletter-block h3 {
            font-family: 'DM Serif Display', serif !important;
            font-weight: 400 !important;
            font-size: 1.5rem !important;
            color: #0a0a0a !important;
            margin: 0 0 8px 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        .newsletter-block .newsletter-desc {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            line-height: 1.55;
            color: #1a1a1a;
            margin: 0 0 16px 0;
        }
        .newsletter-block .newsletter-foot {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            color: #999;
            margin: 4px 0 0 0;
        }

        /* Font de dades */
        .source-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #999;
            margin-top: -8px;
            margin-bottom: 20px;
            padding-left: 4px;
        }

        /* Meta info (data actualització) */
        .meta-info {
            font-family: 'DM Sans', sans-serif;
            font-size: 13px;
            color: #999;
            border-top: 1px solid #e0e0e0;
            padding-top: 12px;
            margin-top: 30px;
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
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #0055a4;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
        }

        /* Selectbox */
        .stSelectbox > div > div {
            border-radius: 3px;
        }
        .stMultiSelect > div > div {
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header():
    """Mostra la capçalera J3B3 + OBSERVATORI a qualsevol pàgina. Logo enllaça a j3b3.com."""
    lang = st.session_state.get("lang", "ca")
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
    if "Càlcul propi" in text or "Cálculo propio" in text:
        meto_lbl = "Veure metodologia" if lang == "ca" else "Ver metodología"
        extra = f' · <a href="/Metodologia" target="_self" style="color:#0055a4;">{meto_lbl}</a>'
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
            "color": "rgba(0,85,164,0.55)",
            "line": {"width": 1.2},
        }
    ]


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


def newsletter_form(lang="ca", compact=False):
    """Caixa de subscripció al butlletí trimestral (MailerLite embed).

    compact=False: caixa gran amb capçalera (al peu d'Inici).
    compact=True: només descripció breu + form (per usar dins popover).
    """
    import streamlit.components.v1 as components

    _ca = lang == "ca"
    eyebrow = "Butlletí" if _ca else "Boletín"
    title = ("Rep les actualitzacions trimestrals"
             if _ca else "Recibe las actualizaciones trimestrales")
    desc = ("Cada trimestre t'enviem les noves dades de l'observatori, "
            "les conclusions destacades i breus anàlisis sectorials. "
            "Sense spam: només l'enviament trimestral."
            if _ca else
            "Cada trimestre te enviamos los nuevos datos del observatorio, "
            "las conclusiones destacadas y breves análisis sectoriales. "
            "Sin spam: solo el envío trimestral.")
    desc_compact = ("Rep cada trimestre les noves dades i conclusions de l'observatori."
                    if _ca else
                    "Recibe cada trimestre los nuevos datos y conclusiones del observatorio.")
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

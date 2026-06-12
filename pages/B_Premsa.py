"""Recull de premsa: agregador RSS de fonts especialitzades en comerç minorista."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header, page_meta  # noqa: E402
from modules.press import fetch_press  # noqa: E402

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"


@st.cache_data(ttl=1800, show_spinner=False)
def _load():
    return fetch_press()


title_col, btn_col = st.columns([5, 1])
with title_col:
    st.title("Recull de premsa" if _ca else "Resumen de prensa")
with btn_col:
    st.write("")  # spacer per alinear vertical
    if st.button(
        ("Actualitzar" if _ca else "Actualizar"),
        help=("Forçar la recàrrega dels feeds (cache 30 min)"
              if _ca else "Forzar la recarga de los feeds (caché 30 min)"),
        use_container_width=True,
    ):
        _load.clear()
        st.rerun()

st.markdown(
    "*Notícies seleccionades de fonts sectorials, generalistes i institucionals sobre comerç al detall, distribució i consum a Espanya.*"
    if _ca else
    "*Noticias seleccionadas de fuentes sectoriales, generalistas e institucionales sobre comercio minorista, distribución y consumo en España.*"
)

with st.spinner("Carregant feeds…" if _ca else "Cargando feeds…"):
    df = _load()

if df.empty:
    st.warning(
        "No s'han pogut carregar els feeds. Torna-ho a provar més tard."
        if _ca else
        "No se han podido cargar los feeds. Inténtalo más tarde."
    )
    st.stop()

# ─── FILTRES ──────────────────────────────────────────────────
# Filtre primari: tipus de font (segmentat). Filtre fi de font dins un expander.

TIPUS_ORDER = ["sectorial", "generalista", "institucional", "agregador"]
TIPUS_LBL_CA = {
    "sectorial": "Sectorial",
    "generalista": "Generalista",
    "institucional": "Institucional",
    "agregador": "Agregador",
}
TIPUS_LBL_ES = TIPUS_LBL_CA  # idèntic en castellà
TIPUS_LBL = TIPUS_LBL_CA if _ca else TIPUS_LBL_ES

AREA_LBL_CA = {
    "multisector": "Multisector",
    "moda": "Moda i tèxtil",
    "alimentacio": "Alimentació",
    "institucional": "Institucional",
}
AREA_LBL_ES = {
    "multisector": "Multisector",
    "moda": "Moda y textil",
    "alimentacio": "Alimentación",
    "institucional": "Institucional",
}
AREA_LBL = AREA_LBL_CA if _ca else AREA_LBL_ES

periode_opts = {
    "7": ("Última setmana", "Última semana"),
    "15": ("Últims 15 dies", "Últimos 15 días"),
    "30": ("Últims 30 dies", "Últimos 30 días"),
    "90": ("Últims 90 dies", "Últimos 90 días"),
    "all": ("Tot", "Todo"),
}

tipus_present = [t for t in TIPUS_ORDER if t in df["tipus"].unique()]
tipus_sel = st.pills(
    "Tipus de font" if _ca else "Tipo de fuente",
    options=tipus_present,
    default=tipus_present,
    format_func=lambda t: TIPUS_LBL.get(t, t),
    selection_mode="multi",
    key="press_tipus",
)

c1, c2, c3 = st.columns([1, 1.5, 2.5])

with c1:
    p = st.selectbox(
        "Període" if _ca else "Período",
        options=list(periode_opts.keys()),
        index=2,
        format_func=lambda k: periode_opts[k][0 if _ca else 1],
    )

with c2:
    arees_opt = [a for a in ["multisector", "moda", "alimentacio", "institucional"]
                 if a in df["area"].unique()]
    arees_sel = st.multiselect(
        "Àrea" if _ca else "Área",
        options=arees_opt,
        default=arees_opt,
        format_func=lambda a: AREA_LBL.get(a, a),
    )

with c3:
    cerca = st.text_input(
        "Cerca" if _ca else "Buscar",
        placeholder="paraula clau…" if _ca else "palabra clave…",
    )

# Filtre fi de fonts (opcional, dins expander) — només operatiu si l'usuari hi entra.
with st.expander("Fonts específiques (avançat)" if _ca else "Fuentes específicas (avanzado)"):
    fonts_disponibles = sorted(
        df[df["tipus"].isin(tipus_sel) if tipus_sel else df.index.notnull()]["font"].unique().tolist()
    )
    fonts_sel = st.multiselect(
        "Selecciona fonts" if _ca else "Selecciona fuentes",
        options=fonts_disponibles,
        default=fonts_disponibles,
        label_visibility="collapsed",
        key="press_fonts",
    )

# ─── APLICA FILTRES ──────────────────────────────────────────
df_f = df.copy()

if tipus_sel:
    df_f = df_f[df_f["tipus"].isin(tipus_sel)]

if fonts_sel and set(fonts_sel) != set(fonts_disponibles):
    df_f = df_f[df_f["font"].isin(fonts_sel)]

if p != "all":
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(p))
    df_f = df_f[df_f["data"].notna() & (df_f["data"] >= cutoff)]

if arees_sel:
    df_f = df_f[df_f["area"].isin(arees_sel)]

if cerca.strip():
    needle = cerca.strip().lower()
    mask = (df_f["titol"].str.lower().str.contains(needle, na=False, regex=False) |
            df_f["snippet"].str.lower().str.contains(needle, na=False, regex=False))
    df_f = df_f[mask]

st.caption(
    f"{len(df_f)} notícies · actualitzat cada 30 min"
    if _ca else
    f"{len(df_f)} noticias · actualizado cada 30 min"
)

# ─── ESTIL ──────────────────────────────────────────────────
st.markdown("""
<style>
.press-item {padding:14px 0; border-bottom:1px solid #eee;}
.press-item:last-child {border-bottom:none;}
.press-meta {color:#666; font-size:12px; margin-bottom:4px; font-family:'Inter',sans-serif;}
.press-meta .font {font-weight:600; color:#003366;}
.press-meta .badge {display:inline-block; padding:1px 6px; border-radius:0;
                    background:#f0f0f0; color:#555; font-size:10px; margin-left:6px;
                    text-transform:uppercase; letter-spacing:0;}
.press-meta .badge.institucional {background:#f4f4f2; color:#003366;}
.press-meta .badge.sectorial {background:#fff3e0; color:#c47200;}
.press-meta .badge.generalista {background:#f5f5f5; color:#666;}
.press-meta .badge.agregador {background:#f5f5f5; color:#666;}
.press-titol a {color:#222; text-decoration:none; font-weight:600; font-size:16px;
                font-family:'Inter',sans-serif; line-height:1.35;}
.press-titol a:hover {color:#003366; text-decoration:underline;}
.press-snippet {color:#555; font-size:13px; margin-top:4px; line-height:1.5;
                font-family:'Inter',sans-serif;}
</style>
""", unsafe_allow_html=True)


def _fmt_data(d):
    if pd.isna(d):
        return "—"
    now = datetime.now(timezone.utc)
    delta = now - d
    if delta.days >= 1:
        return d.strftime("%d/%m/%Y")
    h = int(delta.total_seconds() // 3600)
    if h >= 1:
        return (f"fa {h} h" if _ca else f"hace {h} h")
    m = max(1, int(delta.total_seconds() // 60))
    return (f"fa {m} min" if _ca else f"hace {m} min")


# ─── LLISTA ──────────────────────────────────────────────────
MAX_ITEMS = 100
# Límit per font: evita que una font de molt volum (AGECU/CCAM/Viaempresa…)
# domini la vista mixta i empenyi avall la resta. df_f ja ve ordenat per data
# desc des de press.py, així que head() per grup conserva els més recents.
# NOMÉS s'aplica a la vista mixta: si l'usuari ha triat fonts concretes vol
# profunditat sobre elles → s'aixeca el cap.
PER_FONT_CAP = 6
_total_filtrat = len(df_f)
_fonts_triades = bool(fonts_sel) and set(fonts_sel) != set(fonts_disponibles)
if _fonts_triades:
    items_to_show = df_f.head(MAX_ITEMS)
else:
    items_to_show = (
        df_f.groupby("font", group_keys=False).head(PER_FONT_CAP)
            .sort_values("data", ascending=False, na_position="last")
            .head(MAX_ITEMS)
    )

for _, row in items_to_show.iterrows():
    tipus = row["tipus"]
    snippet = row["snippet"] if row["snippet"] else ""
    snippet_html = f"<div class='press-snippet'>{snippet}</div>" if snippet else ""
    html = (
        f"<div class='press-item'>"
        f"<div class='press-meta'><span class='font'>{row['font']}</span> · "
        f"{_fmt_data(row['data'])}"
        f"<span class='badge {tipus}'>{tipus}</span></div>"
        f"<div class='press-titol'><a href='{row['link']}' target='_blank' rel='noopener'>{row['titol']}</a></div>"
        f"{snippet_html}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

if _total_filtrat > len(items_to_show):
    if _fonts_triades:
        _msg = (f"Mostrant {len(items_to_show)} de {_total_filtrat} resultats. "
                f"Afina filtres per veure'n més."
                if _ca else
                f"Mostrando {len(items_to_show)} de {_total_filtrat} resultados. "
                f"Afina filtros para ver más.")
    else:
        _msg = (f"Mostrant {len(items_to_show)} de {_total_filtrat} resultats "
                f"(màx. {PER_FONT_CAP} per font). Selecciona una font per veure-la sencera."
                if _ca else
                f"Mostrando {len(items_to_show)} de {_total_filtrat} resultados "
                f"(máx. {PER_FONT_CAP} por fuente). Selecciona una fuente para verla entera.")
    st.caption(_msg)

st.divider()

sources_str = ("Distribución Actualidad, Alimarket, Modaes, El Economista, "
               "Cinco Días, INE, Idescat, Google News")
page_meta(sources=sources_str, lang=st.session_state.lang)

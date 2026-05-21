"""Tesi vigent ampliada: titol curt de la tesi + argumentació completa del
Pulso de la setmana (parsejat del markdown) + dades vives de l'observatori
que sostenen l'argument."""
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, page_meta,
                   apply_layout, fnum, fpct, format_mes_any,
                   BRAND, BRAND_DEEP, GRAY_DARK, GREEN, RED, YELLOW, PURPLE)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"
_lang = st.session_state.lang


# ─── DADES ─────────────────────────────────────────────────────

DATA_CACHE = Path(__file__).resolve().parent.parent / "data" / "cache"
NEWSLETTER_DIR = Path(__file__).resolve().parent.parent / "data" / "newsletter"


@st.cache_data(ttl=3600)
def load_tesi():
    p = DATA_CACHE / "tesi_vigent.json"
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


@st.cache_data(ttl=3600)
def load_csv(name):
    p = DATA_CACHE / f"{name}.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


@st.cache_data(ttl=3600)
def load_latest_pulso():
    """Carrega el markdown del Pulso més recent de data/newsletter/."""
    files = sorted(NEWSLETTER_DIR.glob("semana-*.md"), reverse=True)
    if not files:
        return None, None
    path = files[0]
    m = re.match(r"semana-(\d{4})-(\d{2})-(\d{2})", path.stem)
    if not m:
        return None, None
    try:
        dt = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        dt = None
    return dt, path.read_text(encoding="utf-8")


def _strip_trazabilidad(md):
    """Elimina la secció de trazabilidad final si existeix."""
    idx = md.find("### TRAZABILIDAD")
    return (md[:idx] if idx >= 0 else md).rstrip()


def _safe_str(v, default=""):
    return v.strip() if isinstance(v, str) else default


# ─── HEADER + HERO TESI ────────────────────────────────────────

_tesi = load_tesi()
_pulso_dt, _pulso_md = load_latest_pulso()

_tesi_titol = _safe_str(_tesi.get("titol")) if _tesi else ""
_tesi_data_str = _safe_str(_tesi.get("data_publicacio")) if _tesi else ""
_tesi_autor = (_safe_str(_tesi.get("autor"), "Observatorio del Comercio · J3B3 Consulting")
               if _tesi else "Observatorio del Comercio · J3B3 Consulting")
try:
    _tesi_data = date.fromisoformat(_tesi_data_str) if _tesi_data_str else None
except ValueError:
    _tesi_data = None

_avui = date.today()
_tesi_obsoleta = (_tesi_data is None) or ((_avui - _tesi_data).days > 10)

st.title("Tesi vigent" if _ca else "Tesis vigente")

_eyebrow_data = (
    f"Setmana del {_pulso_dt.strftime('%d/%m/%Y')}" if _ca and _pulso_dt
    else f"Semana del {_pulso_dt.strftime('%d/%m/%Y')}" if _pulso_dt
    else ("Pendent d'actualitzar" if _ca else "Pendiente de actualizar")
)

if _tesi_titol and not _tesi_obsoleta:
    st.markdown(
        f"""
        <div style="border-top:3px solid #003366; padding:18px 0 22px 0;
                    margin:6px 0 30px 0;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.85rem;
                        font-weight:700; text-transform:uppercase; color:#003366;
                        opacity:0.7; margin-bottom:14px;">
                {_eyebrow_data}
            </div>
            <div style="font-family:'Archivo Narrow',sans-serif; color:#003366;
                        font-size:1.9rem; font-weight:700; line-height:1.2;
                        letter-spacing:-0.4px;">
                {_tesi_titol}
            </div>
            <div style="color:#6a6a6a; font-size:12px; margin-top:14px;">
                {_tesi_autor} · {_tesi_data.strftime('%d/%m/%Y') if _tesi_data else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    _fb = ("La tesi vigent es publicarà aquí cada dilluns."
           if _ca else
           "La tesis vigente se publicará aquí cada lunes.")
    st.info(_fb)


# ─── ARGUMENT EXTENS (Pulso markdown) ──────────────────────────

st.markdown("---")

_section_lbl = "L'argumentació completa" if _ca else "La argumentación completa"
st.header(_section_lbl)

if _pulso_md:
    _md_clean = _strip_trazabilidad(_pulso_md)
    # Renderitza directament el markdown del Pulso. L'estil bàsic es manté
    # consistent amb la resta de la pàgina via inject_css; no reapliquem
    # l'estilització editorial complexa de L_Lecturas.
    st.markdown(_md_clean)
else:
    st.info(
        "Encara no hi ha cap edició del Pulso disponible al directori "
        "data/newsletter/. Quan es publiqui la primera setmana, "
        "apareixerà aquí automàticament."
        if _ca else
        "Aún no hay ninguna edición del Pulso disponible en el directorio "
        "data/newsletter/. Cuando se publique la primera semana, "
        "aparecerá aquí automáticamente."
    )


# ─── DADES VIVES QUE SOSTENEN ──────────────────────────────────

st.markdown("---")
_data_section_lbl = ("Les dades vives que la sostenen" if _ca
                     else "Los datos vivos que la sostienen")
st.header(_data_section_lbl)

st.caption(
    "Aquestes xifres surten directament del cache de l'observatori i "
    "s'actualitzen automàticament: són el suport quantitatiu que recolza la "
    "lectura editorial de més amunt."
    if _ca else
    "Estas cifras salen directamente del caché del observatorio y se "
    "actualizan automáticamente: son el soporte cuantitativo que respalda "
    "la lectura editorial de más arriba."
)


# ── A) Pols diari (CDMGE) ─────────────────────────────────────

df_cdmge = load_csv("cdmge")
st.subheader("A. " + ("Pols diari del consum" if _ca else "Pulso diario del consumo"))

if not df_cdmge.empty and "indicador" in df_cdmge.columns:
    df_cdmge["data"] = pd.to_datetime(df_cdmge["data"], errors="coerce")
    _ta = (df_cdmge[df_cdmge["indicador"] == "tasa_anual"]
           .dropna(subset=["data", "valor"]).sort_values("data").reset_index(drop=True))
    if len(_ta) > 30:
        _last_dt = _ta["data"].max()
        _avg_30 = float(_ta.tail(30)["valor"].mean())
        _avg_90 = float(_ta.tail(90)["valor"].mean())
        _lag = (pd.Timestamp(_avui) - _last_dt).days
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(("Mitjana 30 dies (YoY)" if _ca else "Media 30 días (YoY)"),
                      fpct(_avg_30, 1))
        with c2:
            st.metric(("Mitjana 90 dies (YoY)" if _ca else "Media 90 días (YoY)"),
                      fpct(_avg_90, 1))
        with c3:
            st.metric(("Última dada" if _ca else "Último dato"),
                      _last_dt.strftime("%d/%m/%Y"),
                      help=f"{_lag} dies de retard INE" if _ca else f"{_lag} días de retraso INE")

        _cutoff = _last_dt - pd.Timedelta(days=365)
        _plot = _ta[_ta["data"] >= _cutoff].copy()
        _plot["mm30"] = _plot["valor"].rolling(window=30, min_periods=8).mean()
        fig_a = go.Figure()
        fig_a.add_trace(go.Scatter(
            x=_plot["data"], y=_plot["mm30"],
            mode="lines",
            line=dict(color=BRAND, width=2.6),
            fill="tozeroy", fillcolor="rgba(245,216,0,0.18)",
            hovertemplate="%{x|%d/%m/%Y}: %{y:+.1f}%<extra></extra>",
            showlegend=False,
        ))
        fig_a.add_hline(y=0, line_dash="solid", line_color="#888", line_width=1)
        apply_layout(fig_a,
            yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
            height=260, margin=dict(l=40, r=20, t=20, b=40),
        )
        st.plotly_chart(fig_a, use_container_width=True)
else:
    st.caption("Cap dada de Pols diari disponible." if _ca else "Sin datos de Pulso diario.")


# ── B) ICM Grandes Superficies vs altres formats ──────────────

df_distrib = load_csv("icm_distribucion")
st.subheader("B. " + ("Format de venda · variació anual"
                       if _ca else "Formato de venta · variación anual"))

if not df_distrib.empty and "modo" in df_distrib.columns:
    df_distrib["data"] = pd.to_datetime(df_distrib["data"], errors="coerce")
    _ds = df_distrib[(df_distrib["tipus"] == "real") &
                     (df_distrib["indicador"] == "var_anual")].copy()
    _ds = _ds.dropna(subset=["data", "valor"]).sort_values("data")
    _last_dt_d = _ds["data"].max()
    _modo_order = ["Empresas unilocalizadas", "Pequeñas cadenas",
                   "Grandes cadenas", "Grandes Superficies"]
    _modo_lbl = ({
        "Empresas unilocalizadas": "Unilocalitzades" if _ca else "Unilocalizadas",
        "Pequeñas cadenas": "Petites cadenes" if _ca else "Pequeñas cadenas",
        "Grandes cadenas": "Grans cadenes" if _ca else "Grandes cadenas",
        "Grandes Superficies": "Grans superfícies" if _ca else "Grandes Superficies",
    })

    st.caption(
        ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
        + format_mes_any(_last_dt_d, _lang)
    )

    _cutoff = _last_dt_d - pd.Timedelta(days=365 * 3)
    _plot_b = _ds[_ds["data"] >= _cutoff]
    _colors = {
        "Empresas unilocalizadas": GRAY_DARK,
        "Pequeñas cadenas": GREEN,
        "Grandes cadenas": BRAND,
        "Grandes Superficies": RED,
    }
    fig_b = go.Figure()
    for m in _modo_order:
        _s = _plot_b[_plot_b["modo"] == m].sort_values("data")
        if _s.empty:
            continue
        _lbls = [format_mes_any(d, _lang) for d in _s["data"]]
        fig_b.add_trace(go.Scatter(
            x=_s["data"], y=_s["valor"],
            mode="lines+markers",
            name=_modo_lbl[m],
            line=dict(color=_colors[m], width=2.3),
            marker=dict(size=4),
            customdata=_lbls,
            hovertemplate=f"<b>{_modo_lbl[m]}</b><br>%{{customdata}}: %{{y:+.1f}}%<extra></extra>",
        ))
    fig_b.add_hline(y=0, line_dash="solid", line_color="#888", line_width=1)
    apply_layout(fig_b,
        yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
        height=340, margin=dict(l=40, r=20, t=20, b=40),
    )
    fig_b.update_xaxes(tickformat="%m/%Y")
    st.plotly_chart(fig_b, use_container_width=True)
else:
    st.caption("Cap dada de modos de distribució disponible." if _ca
               else "Sin datos de modos de distribución.")


# ── C) Eurostat ES vs UE-27 ───────────────────────────────────

df_eu_m = load_csv("europa_retail_mensual")
st.subheader("C. " + ("Posicionament europeu · ES vs UE-27"
                       if _ca else "Posicionamiento europeo · ES vs UE-27"))

if not df_eu_m.empty and "yoy" in df_eu_m.columns and "pais_codi" in df_eu_m.columns:
    _eu = df_eu_m[df_eu_m["pais_codi"].isin(["ES", "EA20", "EU27_2020", "DE", "FR", "IT", "PT"])].copy()
    _eu["data"] = pd.to_datetime(_eu["periode"] + "-01", errors="coerce")
    _eu = _eu.dropna(subset=["data", "yoy"]).sort_values(["pais_codi", "data"])
    _last_eu_dt = _eu["data"].max()
    if pd.notna(_last_eu_dt):
        st.caption(
            ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
            + format_mes_any(_last_eu_dt, _lang)
        )
        _cutoff = _last_eu_dt - pd.Timedelta(days=365 * 2)
        _eu_plot = _eu[_eu["data"] >= _cutoff]
        _colors_eu = {
            "ES": BRAND, "EU27_2020": YELLOW, "DE": RED, "FR": GREEN,
            "IT": GRAY_DARK, "PT": PURPLE, "EA20": "#999",
        }
        _name_eu = {
            "ES": "Espanya" if _ca else "España",
            "EU27_2020": "UE-27",
            "EA20": "Zona euro",
            "DE": "Alemanya" if _ca else "Alemania",
            "FR": "França" if _ca else "Francia",
            "IT": "Itàlia" if _ca else "Italia",
            "PT": "Portugal",
        }
        fig_c = go.Figure()
        for code in ["ES", "EU27_2020", "DE", "FR", "IT", "PT"]:
            _s = _eu_plot[_eu_plot["pais_codi"] == code]
            if _s.empty:
                continue
            _lw = 3 if code == "ES" else 1.6
            _lbls = [format_mes_any(d, _lang) for d in _s["data"]]
            fig_c.add_trace(go.Scatter(
                x=_s["data"], y=_s["yoy"],
                mode="lines",
                name=_name_eu.get(code, code),
                line=dict(color=_colors_eu.get(code, "#888"), width=_lw),
                customdata=_lbls,
                hovertemplate=f"<b>{_name_eu.get(code, code)}</b><br>%{{customdata}}: %{{y:+.1f}}%<extra></extra>",
            ))
        fig_c.add_hline(y=0, line_dash="solid", line_color="#888", line_width=1)
        apply_layout(fig_c,
            yaxis_title=("Variació anual vendes minoristes (%)"
                          if _ca else "Variación anual ventas minoristas (%)"),
            height=360, margin=dict(l=40, r=20, t=20, b=40),
        )
        fig_c.update_xaxes(tickformat="%m/%Y")
        st.plotly_chart(fig_c, use_container_width=True)
else:
    st.caption("Cap dada Eurostat mensual disponible." if _ca
               else "Sin datos Eurostat mensual.")


# ─── PEU ──────────────────────────────────────────────────────

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/0_Inici.py",
                 label=("← Tornar a la home" if _ca else "← Volver a la home"))
with col2:
    st.page_link("pages/L_Lecturas.py",
                 label=("Veure totes les edicions del Pulso →"
                        if _ca else "Ver todas las ediciones del Pulso →"))

page_meta("INE, Eurostat", _lang)

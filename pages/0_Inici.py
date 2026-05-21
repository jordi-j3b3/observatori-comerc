"""Pàgina d'inici: hero amb número-xoc + tesi vigent, KPIs, Pols diari, cards de
navegació per dimensió, conclusions executives, butlletí."""
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys
from datetime import datetime, date, timedelta
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, fnum, fpct, cagr,
                   page_meta, newsletter_form, highlight_expander)

inject_css()
t = setup_lang(show_selector=False)

# ─── DADES ─────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data(name):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_tesi():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "tesi_vigent.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

df_pib = load_data("pib_vab")
df_empreses = load_data("empreses")
df_prod = load_data("productivitat")
df_ecommerce = load_data("ecommerce")
df_europa = load_data("europa_vab")
df_territori = load_data("eee_ccaa")
df_cdmge = load_data("cdmge")
df_distrib = load_data("icm_distribucion")
df_eu_m = load_data("europa_retail_mensual")

# ─── HEADER ────────────────────────────────────────────────────

page_header()
st.title(t("app_title"))
st.markdown(f"*{t('app_subtitle')}*")

_ca = st.session_state.lang == "ca"

# ─── PROCESSING CDMGE (per HERO + chart de Pols diari) ─────────

_pulse = None
if not df_cdmge.empty and "indicador" in df_cdmge.columns:
    _df_p = df_cdmge.copy()
    _df_p["data"] = pd.to_datetime(_df_p["data"], errors="coerce")
    _ta = (_df_p[_df_p["indicador"] == "tasa_anual"]
           .dropna(subset=["data", "valor"])
           .sort_values("data")
           .reset_index(drop=True))
    if len(_ta) > 30:
        _last_dt = _ta["data"].max()
        _last_val = float(_ta.iloc[-1]["valor"])
        _avg_30 = float(_ta.tail(30)["valor"].mean())
        _avg_90 = float(_ta.tail(90)["valor"].mean())
        _today_ts = pd.Timestamp(date.today())
        _lag_days = int((_today_ts - _last_dt).days)
        _cutoff = _last_dt - pd.Timedelta(days=365)
        _plot_p = _ta[_ta["data"] >= _cutoff].copy()
        _plot_p["mm30"] = _plot_p["valor"].rolling(window=30, min_periods=8).mean()
        _pulse = {
            "last_dt": _last_dt, "last_val": _last_val,
            "avg_30": _avg_30, "avg_90": _avg_90,
            "lag_days": _lag_days, "plot": _plot_p,
        }

# ─── HERO: NÚMERO-XOC (esquerra) + TESI VIGENT (dreta) ─────────

_tesi = load_tesi()
_tesi_titol = None
_tesi_data = None
_tesi_autor = "Observatorio del Comercio · J3B3 Consulting"
_tesi_enllac = ""

def _safe_str(value, default=""):
    """Retorna value.strip() si és str, default altrament."""
    if isinstance(value, str):
        return value.strip()
    return default

if _tesi:
    _tesi_titol = _safe_str(_tesi.get("titol"))
    _tesi_data_str = _safe_str(_tesi.get("data_publicacio"))
    _tesi_autor = (
        _safe_str(_tesi.get("autor"), "Observatorio del Comercio · J3B3 Consulting")
        or "Observatorio del Comercio · J3B3 Consulting"
    )
    _tesi_enllac = _safe_str(_tesi.get("enllac_pulso"))
    try:
        _tesi_data = date.fromisoformat(_tesi_data_str)
    except (TypeError, ValueError):
        _tesi_data = None

_avui = date.today()
_tesi_obsoleta = (_tesi_data is None) or ((_avui - _tesi_data).days > 10)

hero_l, hero_r = st.columns([3, 2], gap="large")

with hero_l:
    if _pulse:
        _sign_color = "#003366" if _pulse["avg_30"] >= 0 else "#c0392b"
        _sign_text = fpct(_pulse["avg_30"], 1)
        _eyebrow_l = ("Pols del consum · darrers 30 dies"
                      if _ca else
                      "Pulso del consumo · últimos 30 días")
        _sub_l = ("Variació anual mitjana de vendes diàries · grans empreses retail"
                  if _ca else
                  "Variación anual media de ventas diarias · grandes empresas retail")
        _accel = _pulse["avg_30"] - _pulse["avg_90"]
        if abs(_accel) < 0.5:
            _dir_l = "estable vs trimestre anterior" if _ca else "estable vs trimestre anterior"
        elif _accel > 0:
            _dir_l = "accelerant" if _ca else "acelerando"
        else:
            _dir_l = "desaccelerant" if _ca else "desacelerando"
        _asof_l = "Darrera dada" if _ca else "Último dato"
        _lag_l = (f"INE publica amb {_pulse['lag_days']} dies de retard"
                  if _ca else
                  f"INE publica con {_pulse['lag_days']} días de retraso")
        st.markdown(
            f"""
            <div style="font-family:'Inter',sans-serif; border-top:3px solid #003366;
                        padding:18px 0 8px 0; margin-top:18px;">
                <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.82rem;
                            font-weight:700; text-transform:uppercase; color:#003366;
                            margin-bottom:4px;">
                    {_eyebrow_l}
                </div>
                <div style="font-family:'Archivo Narrow',sans-serif; font-size:5.2rem;
                            font-weight:700; line-height:1; color:{_sign_color};
                            letter-spacing:-2px; margin:10px 0 6px;">
                    {_sign_text}
                </div>
                <div style="color:#1a1a1a; font-size:14px; line-height:1.5; margin-top:8px;">
                    {_sub_l} · <strong>{_dir_l}</strong>
                </div>
                <div style="color:#6a6a6a; font-size:12px; margin-top:10px;">
                    {_asof_l}: {_pulse['last_dt'].strftime('%d/%m/%Y')} · {_lag_l}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        _na_lbl = ("Pols del consum no disponible"
                   if _ca else "Pulso del consumo no disponible")
        st.markdown(
            f"""
            <div style="border-top:3px solid #c0c0c0; padding:18px 0; margin-top:18px;
                        color:#6a6a6a; font-size:14px; font-style:italic;">
                {_na_lbl}
            </div>
            """,
            unsafe_allow_html=True,
        )

with hero_r:
    _eyebrow_r = "Tesi vigent" if _ca else "Tesis vigente"
    if _tesi_titol and not _tesi_obsoleta:
        _tesi_data_fmt = _tesi_data.strftime("%d/%m/%Y")
        st.markdown(
            f"""
            <div style="background:#ffffff; border-top:3px solid #003366;
                        padding:18px 18px 14px 18px; margin-top:18px;
                        font-family:'Inter',sans-serif;
                        background-color:rgba(0,51,102,0.03);">
                <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.82rem;
                            font-weight:700; text-transform:uppercase;
                            color:#003366; margin-bottom:10px;">
                    {_eyebrow_r}
                </div>
                <div style="color:#003366; font-size:17px; font-weight:600;
                            line-height:1.35; margin-bottom:12px;
                            font-family:'Archivo Narrow',sans-serif;">
                    {_tesi_titol}
                </div>
                <div style="color:#6a6a6a; font-size:11.5px;">
                    {_tesi_autor} · {_tesi_data_fmt}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/L_Lecturas.py",
            label=("Llegir el Pulso de la setmana →" if _ca
                   else "Leer el Pulso de la semana →"),
        )
    else:
        # Tesi obsoleta/absent: en lloc d'un "aviat disponible" gris,
        # mostrem 3 dades calentes del cache (sense inventar text).
        _hot_lines = []
        # 1) Pols diari 30d
        if _pulse:
            _lbl_pd = ("Pols 30d (vendes diàries grans empreses)"
                       if _ca else "Pulso 30d (ventas diarias grandes empresas)")
            _hot_lines.append((_lbl_pd, fpct(_pulse["avg_30"], 1)))
        # 2) ICM Grandes Superficies última var_anual
        if not df_distrib.empty and "modo" in df_distrib.columns:
            _d = df_distrib[(df_distrib["tipus"] == "real") &
                            (df_distrib["indicador"] == "var_anual") &
                            (df_distrib["modo"] == "Grandes Superficies")].copy()
            _d["data"] = pd.to_datetime(_d["data"], errors="coerce")
            _d = _d.dropna(subset=["data", "valor"]).sort_values("data")
            if not _d.empty:
                _last = _d.iloc[-1]
                _lbl_gs = ("Grans superfícies · ICM YoY"
                           if _ca else "Grandes Superficies · ICM YoY")
                _hot_lines.append((_lbl_gs, fpct(float(_last["valor"]), 1)))
        # 3) Eurostat ES vs UE-27, última diferència
        if not df_eu_m.empty and "yoy" in df_eu_m.columns:
            _eu_last_mes = df_eu_m["periode"].max()
            _es = df_eu_m[(df_eu_m["pais_codi"] == "ES") &
                          (df_eu_m["periode"] == _eu_last_mes)]
            _ue = df_eu_m[(df_eu_m["pais_codi"] == "EU27_2020") &
                          (df_eu_m["periode"] == _eu_last_mes)]
            if not _es.empty and not _ue.empty:
                _es_v = float(_es.iloc[0]["yoy"]) if pd.notna(_es.iloc[0]["yoy"]) else None
                _ue_v = float(_ue.iloc[0]["yoy"]) if pd.notna(_ue.iloc[0]["yoy"]) else None
                if _es_v is not None and _ue_v is not None:
                    _diff = _es_v - _ue_v
                    _lbl_eu = ("ES vs UE-27 (Eurostat YoY)"
                               if _ca else "ES vs UE-27 (Eurostat YoY)")
                    _hot_lines.append((_lbl_eu,
                                        f"{fpct(_es_v, 1)} vs {fpct(_ue_v, 1)} ({fpct(_diff, 1)})"))

        if _hot_lines:
            _hot_html = "".join(
                f"<div style='display:flex; justify-content:space-between; "
                f"padding:6px 0; border-bottom:1px solid rgba(0,51,102,0.08); "
                f"font-size:12.5px;'>"
                f"<span style='color:#6a6a6a;'>{lbl}</span>"
                f"<span style='font-family:Archivo Narrow,sans-serif; font-weight:700; "
                f"color:#003366;'>{val}</span></div>"
                for lbl, val in _hot_lines
            )
        else:
            _hot_html = ""

        _pending_lbl = ("Pendent d'actualitzar" if _ca else "Pendiente de actualizar")
        _live_lbl = ("Mentrestant, dades del cache:" if _ca
                     else "Mientras tanto, datos del caché:")
        st.markdown(
            f"""
            <div style="background:rgba(0,51,102,0.02); border-top:3px solid #c0c0c0;
                        padding:16px 18px 12px 18px; margin-top:18px;
                        font-family:'Inter',sans-serif;">
                <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.82rem;
                            font-weight:700; text-transform:uppercase;
                            color:#6a6a6a; margin-bottom:4px;">
                    {_eyebrow_r}
                </div>
                <div style="color:#6a6a6a; font-size:12.5px; margin-bottom:12px;">
                    {_pending_lbl}
                </div>
                <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.72rem;
                            font-weight:700; text-transform:uppercase; color:#6a6a6a;
                            opacity:0.7; margin-bottom:6px;">
                    {_live_lbl}
                </div>
                {_hot_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/L_Lecturas.py",
            label=("Veure el Pulso de la setmana →" if _ca
                   else "Ver el Pulso de la semana →"),
        )

# Banner d'avís si el retard del Pols diari és superior al normal
if _pulse and _pulse["lag_days"] > 21:
    _notice = (
        f"L'INE publica el CDMGE un cop al mes amb retard de ~30-40 dies. "
        f"Última dada disponible: {_pulse['last_dt'].strftime('%d/%m/%Y')} "
        f"(fa {_pulse['lag_days']} dies)."
        if _ca else
        f"El INE publica el CDMGE una vez al mes con retraso de ~30-40 días. "
        f"Último dato disponible: {_pulse['last_dt'].strftime('%d/%m/%Y')} "
        f"(hace {_pulse['lag_days']} días)."
    )
    st.caption(_notice)

st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

# ─── KPIs ──────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_pib.empty and "vab_cnae47_corrents" in df_pib.columns:
        rows = df_pib.dropna(subset=["vab_cnae47_corrents"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["vab_cnae47_corrents"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["vab_cnae47_corrents"]) - 1) * 100)
        st.metric(t("kpi_pib"), f"{fnum(val)} {t('kpi_meur')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_pib"), "—")

with col2:
    if not df_empreses.empty:
        esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if not esp.empty:
            last = esp.iloc[-1]
            val = int(last["empreses"])
            any_ = int(last["any"])
            if len(esp) > 1:
                prev = esp.iloc[-2]
                any_prev = int(prev["any"])
                delta = fpct(((val / int(prev["empreses"])) - 1) * 100)
                st.metric(t("kpi_empreses"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
            else:
                st.metric(t("kpi_empreses"), fnum(val), help=f"{any_}")
    else:
        st.metric(t("kpi_empreses"), "—")

with col3:
    if not df_prod.empty and "personal_ocupat" in df_prod.columns:
        rows = df_prod.dropna(subset=["personal_ocupat"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["personal_ocupat"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["personal_ocupat"]) - 1) * 100)
        st.metric(t("kpi_ocupacio"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_ocupacio"), "—")

with col4:
    if not df_prod.empty and "productivitat_va_hora" in df_prod.columns:
        rows = df_prod.dropna(subset=["productivitat_va_hora"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["productivitat_va_hora"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["productivitat_va_hora"]) - 1) * 100)
        st.metric(t("kpi_productivitat"), f"{fnum(val, 1)} {t('kpi_eur_h')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_productivitat"), "—")

# ─── POLS DIARI · CHART 12 MESOS ───────────────────────────────

st.markdown("---")

if _pulse:
    _eyebrow_c = ("Pols diari · darrers 12 mesos (mitjana mòbil 30 dies)"
                  if _ca else
                  "Pulso diario · últimos 12 meses (media móvil 30 días)")
    st.markdown(
        f"""
        <div style="margin:6px 0 6px;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.82rem;
                        font-weight:700; text-transform:uppercase; color:#003366;">
                {_eyebrow_c}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _fig = go.Figure()
    _fig.add_trace(go.Scatter(
        x=_pulse["plot"]["data"], y=_pulse["plot"]["mm30"],
        mode="lines",
        line=dict(color="#003366", width=2.6),
        fill="tozeroy",
        fillcolor="rgba(245, 216, 0, 0.18)",
        hovertemplate="%{x|%d/%m/%Y}: %{y:+.1f}%<extra></extra>",
        showlegend=False,
    ))
    _fig.add_hline(y=0, line_dash="solid", line_color="#888", line_width=1)
    _fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=20),
        yaxis_title="",
        xaxis_title="",
        hovermode="x unified",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12, color="#1a1a1a"),
    )
    _fig.update_yaxes(gridcolor="#eee", zeroline=False, ticksuffix="%")
    _fig.update_xaxes(gridcolor="#f5f5f5")
    st.plotly_chart(_fig, use_container_width=True,
                    config={"displayModeBar": False})

    st.page_link(
        "pages/0a_Pols_diari.py",
        label=("Veure el detall del Pols diari →" if _ca
               else "Ver el detalle del Pulso diario →"),
        icon=None,
    )

# ─── CARDS DE NAVEGACIÓ (6 dimensions, grid 3x2) ───────────────

st.divider()

_cards_eyebrow = ("Explora les dimensions" if _ca
                  else "Explora las dimensiones")
_cards_sub = ("Sis radiografies del sector. Cada targeta porta a la pàgina amb el detall complet."
              if _ca else
              "Seis radiografías del sector. Cada tarjeta lleva a la página con el detalle completo.")
st.markdown(
    f"""
    <div style="margin:24px 0 18px;">
        <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.92rem;
                    font-weight:700; text-transform:uppercase; color:#003366;
                    margin-bottom:6px;">
            {_cards_eyebrow}
        </div>
        <div style="font-size:13px; color:#666;">{_cards_sub}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def _spark(values, color="#003366"):
    """Mini-sparkline Plotly per a les cards (sense eixos)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))), y=list(values),
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor="rgba(0,51,102,0.10)",
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=58,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _card_header(eyebrow, kpi, sub):
    return (
        f"<div style=\"border-top:2px solid #003366; padding:14px 0 2px 0;\">"
        f"<div style=\"font-family:'Archivo Narrow',sans-serif; font-size:0.78rem; "
        f"font-weight:700; text-transform:uppercase; color:#003366; opacity:0.7; "
        f"margin-bottom:6px;\">{eyebrow}</div>"
        f"<div style=\"font-family:'Archivo Narrow',sans-serif; font-size:1.55rem; "
        f"font-weight:700; line-height:1.05; color:#003366; letter-spacing:-0.5px;\">{kpi}</div>"
        f"<div style=\"font-size:11.5px; color:#6a6a6a; margin-top:4px;\">{sub}</div>"
        f"</div>"
    )


def _no_data_card(eyebrow):
    return (
        f"<div style=\"border-top:2px solid #c0c0c0; padding:14px 0;\">"
        f"<div style=\"font-family:'Archivo Narrow',sans-serif; font-size:0.78rem; "
        f"font-weight:700; text-transform:uppercase; color:#6a6a6a; opacity:0.7;\">{eyebrow}</div>"
        f"<div style=\"font-size:13px; color:#999; font-style:italic; margin-top:8px;\">—</div>"
        f"</div>"
    )


row1 = st.columns(3, gap="medium")
row2 = st.columns(3, gap="medium")

# ── Card 1: PIB i VAB ─────────────────────────────────────────
with row1[0]:
    _lbl = "PIB i VAB" if _ca else "PIB y VAB"
    if (not df_pib.empty
            and "vab_cnae47_corrents" in df_pib.columns):
        _rows = df_pib.dropna(subset=["vab_cnae47_corrents"]).sort_values("any")
        if len(_rows) >= 2:
            _last = _rows.iloc[-1]
            _kpi = f"{fnum(_last['vab_cnae47_corrents'])} M€"
            _sub = (f"VAB nominal {int(_last['any'])}" if not _ca
                    else f"VAB nominal {int(_last['any'])}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = (_rows["vab_cnae47_constants"].dropna().tolist()
                           if "vab_cnae47_constants" in _rows.columns
                           and _rows["vab_cnae47_constants"].notna().any()
                           else _rows["vab_cnae47_corrents"].tolist())
            if len(_spark_vals) >= 2:
                st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                                config={"displayModeBar": False})
            st.page_link("pages/1_PIB_i_VAB.py",
                         label=("Evolució i pes sobre PIB →" if _ca
                                else "Evolución y peso sobre PIB →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ── Card 2: Empreses ──────────────────────────────────────────
with row1[1]:
    _lbl = "Empreses" if _ca else "Empresas"
    if not df_empreses.empty:
        _esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if len(_esp) >= 2:
            _last = _esp.iloc[-1]
            _kpi = fnum(int(_last["empreses"]))
            _sub = (f"Empreses CNAE 47 · {int(_last['any'])}" if _ca
                    else f"Empresas CNAE 47 · {int(_last['any'])}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = _esp["empreses"].tolist()
            st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                            config={"displayModeBar": False})
            st.page_link("pages/2_Empreses.py",
                         label=("Densitat per CCAA →" if _ca
                                else "Densidad por CCAA →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ── Card 3: Productivitat ─────────────────────────────────────
with row1[2]:
    _lbl = "Productivitat" if _ca else "Productividad"
    if (not df_prod.empty
            and "productivitat_va_hora" in df_prod.columns):
        _rows = df_prod.dropna(subset=["productivitat_va_hora"]).sort_values("any")
        if len(_rows) >= 2:
            _last = _rows.iloc[-1]
            _kpi = f"{fnum(_last['productivitat_va_hora'], 1)} €/h"
            _sub = (f"VA per hora · {int(_last['any'])}" if _ca
                    else f"VA por hora · {int(_last['any'])}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = _rows["productivitat_va_hora"].tolist()
            st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                            config={"displayModeBar": False})
            st.page_link("pages/4_Productivitat.py",
                         label=("Quota salarial i costos →" if _ca
                                else "Cuota salarial y costes →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ── Card 4: E-commerce ────────────────────────────────────────
with row2[0]:
    _lbl = "E-commerce"
    if (not df_ecommerce.empty
            and "ecommerce_cnae47_eur" in df_ecommerce.columns):
        _rows = df_ecommerce.dropna(subset=["ecommerce_cnae47_eur"]).sort_values("any")
        if len(_rows) >= 2:
            _last = _rows.iloc[-1]
            _kpi = f"{fnum(_last['ecommerce_cnae47_eur']/1e9, 1)} Md€"
            _sub = (f"Volum CNAE 47 · {int(_last['any'])}" if _ca
                    else f"Volumen CNAE 47 · {int(_last['any'])}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = _rows["ecommerce_cnae47_eur"].tolist()
            st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                            config={"displayModeBar": False})
            st.page_link("pages/5_Ecommerce.py",
                         label=("Pes online sobre total →" if _ca
                                else "Peso online sobre total →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ── Card 5: Territori ─────────────────────────────────────────
with row2[1]:
    _lbl = "Territori" if _ca else "Territorio"
    if (not df_territori.empty
            and "pes_cnae47_pib" in df_territori.columns):
        _terr = df_territori[df_territori["territori"] != "espanya"].dropna(subset=["pes_cnae47_pib"])
        if not _terr.empty:
            _yr = int(_terr["any"].max())
            _yr_data = _terr[_terr["any"] == _yr]
            _top = _yr_data.nlargest(1, "pes_cnae47_pib").iloc[0]
            _bot = _yr_data.nsmallest(1, "pes_cnae47_pib").iloc[0]
            _kpi = f"{fpct(_top['pes_cnae47_pib']*100, 1, sign=False)} – {fpct(_bot['pes_cnae47_pib']*100, 1, sign=False)}"
            _sub = (f"Pes s/ PIB · rang CCAA · {_yr}" if _ca
                    else f"Peso s/ PIB · rango CCAA · {_yr}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = _yr_data.sort_values("pes_cnae47_pib")["pes_cnae47_pib"].tolist()
            st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                            config={"displayModeBar": False})
            st.page_link("pages/6_Territori.py",
                         label=("Mapa i estimació per CCAA →" if _ca
                                else "Mapa y estimación por CCAA →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ── Card 6: Europa ────────────────────────────────────────────
with row2[2]:
    _lbl = "Europa"
    if not df_europa.empty and "pes_cnae47" in df_europa.columns:
        _es = df_europa[df_europa["pais_codi"] == "ES"].sort_values("any")
        _eu = df_europa[df_europa["pais_codi"] == "EU27_2020"].sort_values("any")
        if not _es.empty and not _eu.empty:
            _es_last = _es.iloc[-1]
            _eu_last = _eu.iloc[-1]
            _delta = (_es_last["pes_cnae47"] - _eu_last["pes_cnae47"]) * 100
            _yr = int(_es_last["any"])
            _kpi = f"{fpct(_delta, 2)}"
            _sub = (f"ES vs UE-27 · pes s/ PIB · {_yr}" if _ca
                    else f"ES vs UE-27 · peso s/ PIB · {_yr}")
            st.markdown(_card_header(_lbl, _kpi, _sub), unsafe_allow_html=True)
            _spark_vals = [v*100 for v in _es["pes_cnae47"].tolist()]
            st.plotly_chart(_spark(_spark_vals), use_container_width=True,
                            config={"displayModeBar": False})
            st.page_link("pages/7_Comparativa_Europa.py",
                         label=("Comparativa amb la UE-27 →" if _ca
                                else "Comparativa con la UE-27 →"))
        else:
            st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)
    else:
        st.markdown(_no_data_card(_lbl), unsafe_allow_html=True)

# ─── SOBRE L'OBSERVATORI (expander discret) ───────────────────

st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

with highlight_expander(
    "Què és l'Observatori del Comerç" if _ca else "Qué es el Observatorio del Comercio",
    expanded=False,
):
    if _ca:
        st.markdown(
            "El **comerç al detall** (CNAE 47) és un dels pilars de l'economia "
            "espanyola: dona feina a més d'**1,7 milions** de persones, genera uns "
            "**70.000 M EUR** de valor afegit i articula el consum de les famílies "
            "a tot el territori. Aquest observatori ofereix una **radiografia "
            "actualitzada** del sector a partir de dades oficials (INE, Eurostat, "
            "CNMC), organitzada en sis dimensions: PIB i VAB, empreses, productivitat, "
            "e-commerce, territori i Europa. Les dades s'actualitzen de forma "
            "**trimestral automàtica** (gener, abril, juliol, octubre) i el Pols "
            "diari/mensual es refresca de continu."
        )
    else:
        st.markdown(
            "El **comercio minorista** (CNAE 47) es uno de los pilares de la economía "
            "española: da empleo a más de **1,7 millones** de personas, genera unos "
            "**70.000 M EUR** de valor añadido y articula el consumo de las familias "
            "en todo el territorio. Este observatorio ofrece una **radiografía "
            "actualizada** del sector a partir de datos oficiales (INE, Eurostat, "
            "CNMC), organizada en seis dimensiones: PIB y VAB, empresas, productividad, "
            "e-commerce, territorio y Europa. Los datos se actualizan de forma "
            "**trimestral automática** (enero, abril, julio, octubre) y el Pulso "
            "diario/mensual se refresca de continuo."
        )

# ─── CONCLUSIONS DINAMIQUES ───────────────────────────────────

_conclusions = []

# 1. PIB/VAB
if not df_pib.empty and "vab_cnae47_corrents" in df_pib.columns and "vab_cnae47_constants" in df_pib.columns:
    _pib_rows = df_pib.dropna(subset=["vab_cnae47_corrents", "vab_cnae47_constants"])
    if len(_pib_rows) >= 2:
        _pib_last = _pib_rows.iloc[-1]
        _pib_first = _pib_rows.iloc[0]
        _pib_yr = int(_pib_last["any"])
        _pib_n = _pib_yr - int(_pib_first["any"])
        _cagr_real = cagr(_pib_first["vab_cnae47_constants"], _pib_last["vab_cnae47_constants"], _pib_n)
        if _ca:
            _conclusions.append(
                f"El VAB nominal del CNAE 47 es de <strong>{fnum(_pib_last['vab_cnae47_corrents'])} M EUR</strong> ({_pib_yr}), "
                f"amb un creixement real anualitzat (CAGR) del <strong>{fpct(_cagr_real, 1)}</strong> des de {int(_pib_first['any'])}."
            )
        else:
            _conclusions.append(
                f"El VAB nominal del CNAE 47 es de <strong>{fnum(_pib_last['vab_cnae47_corrents'])} M EUR</strong> ({_pib_yr}), "
                f"con un crecimiento real anualizado (CAGR) del <strong>{fpct(_cagr_real, 1)}</strong> desde {int(_pib_first['any'])}."
            )

# 2. Empreses
if not df_empreses.empty:
    _emp_esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
    if len(_emp_esp) >= 2:
        _emp_last = _emp_esp.iloc[-1]
        _emp_prev = _emp_esp.iloc[-2]
        _emp_var = (int(_emp_last["empreses"]) / int(_emp_prev["empreses"]) - 1) * 100
        if _ca:
            _conclusions.append(
                f"El sector compta amb <strong>{fnum(int(_emp_last['empreses']))}</strong> empreses ({int(_emp_last['any'])}), "
                f"un <strong>{fpct(_emp_var)}</strong> respecte l'any anterior."
            )
        else:
            _conclusions.append(
                f"El sector cuenta con <strong>{fnum(int(_emp_last['empreses']))}</strong> empresas ({int(_emp_last['any'])}), "
                f"un <strong>{fpct(_emp_var)}</strong> respecto al ano anterior."
            )

# 3. Productivitat
if not df_prod.empty and "productivitat_va_hora" in df_prod.columns:
    _prod_rows = df_prod.dropna(subset=["productivitat_va_hora"])
    if len(_prod_rows) >= 2:
        _prod_last = _prod_rows.iloc[-1]
        _prod_first = _prod_rows.iloc[0]
        _prod_var = (_prod_last["productivitat_va_hora"] / _prod_first["productivitat_va_hora"] - 1) * 100
        if _ca:
            _conclusions.append(
                f"La productivitat (VA/hora) ha variat un <strong>{fpct(_prod_var, 1)}</strong> "
                f"entre {int(_prod_first['any'])} i {int(_prod_last['any'])}, situant-se en "
                f"<strong>{fnum(_prod_last['productivitat_va_hora'], 1)} EUR/hora</strong>."
            )
        else:
            _conclusions.append(
                f"La productividad (VA/hora) ha variado un <strong>{fpct(_prod_var, 1)}</strong> "
                f"entre {int(_prod_first['any'])} y {int(_prod_last['any'])}, situandose en "
                f"<strong>{fnum(_prod_last['productivitat_va_hora'], 1)} EUR/hora</strong>."
            )

# 4. E-commerce
if not df_ecommerce.empty and "ecommerce_cnae47_eur" in df_ecommerce.columns:
    _ec = df_ecommerce.dropna(subset=["ecommerce_cnae47_eur"]).sort_values("any")
    if len(_ec) >= 2:
        _ec_last = _ec.iloc[-1]
        _ec_first = _ec.iloc[0]
        _ec_mult = _ec_last["ecommerce_cnae47_eur"] / _ec_first["ecommerce_cnae47_eur"]
        if _ca:
            _conclusions.append(
                f"L'e-commerce del CNAE 47 ha multiplicat el seu volum per <strong>x{fnum(_ec_mult, 1)}</strong> "
                f"des de {int(_ec_first['any'])}, fins a <strong>{fnum(_ec_last['ecommerce_cnae47_eur']/1e9, 1)} Md EUR</strong> ({int(_ec_last['any'])})."
            )
        else:
            _conclusions.append(
                f"El e-commerce del CNAE 47 ha multiplicado su volumen por <strong>x{fnum(_ec_mult, 1)}</strong> "
                f"desde {int(_ec_first['any'])}, hasta <strong>{fnum(_ec_last['ecommerce_cnae47_eur']/1e9, 1)} Md EUR</strong> ({int(_ec_last['any'])})."
            )

# 5. Europa
if not df_europa.empty and "pes_cnae47" in df_europa.columns:
    _eu_es = df_europa[df_europa["pais_codi"] == "ES"].sort_values("any")
    _eu_avg = df_europa[df_europa["pais_codi"] == "EU27_2020"].sort_values("any")
    if not _eu_es.empty and not _eu_avg.empty:
        _eu_es_last = _eu_es.iloc[-1]
        _eu_avg_last = _eu_avg.iloc[-1]
        _es_pct = _eu_es_last["pes_cnae47"] * 100
        _eu_pct = _eu_avg_last["pes_cnae47"] * 100
        _diff = _es_pct - _eu_pct
        if _ca:
            _pos = "per sobre" if _diff > 0 else "per sota"
            _conclusions.append(
                f"Espanya destina un <strong>{fpct(_es_pct, 1, sign=False)}</strong> del seu PIB al comerç al detall, "
                f"<strong>{fpct(abs(_diff), 2, sign=False)} {_pos}</strong> de la mitjana UE-27 ({fpct(_eu_pct, 1, sign=False)})."
            )
        else:
            _pos = "por encima" if _diff > 0 else "por debajo"
            _conclusions.append(
                f"Espana destina un <strong>{fpct(_es_pct, 1, sign=False)}</strong> de su PIB al comercio minorista, "
                f"<strong>{fpct(abs(_diff), 2, sign=False)} {_pos}</strong> de la media UE-27 ({fpct(_eu_pct, 1, sign=False)})."
            )

# 6. Territori
if not df_territori.empty and "pes_cnae47_pib" in df_territori.columns:
    _terr = df_territori[df_territori["territori"] != "espanya"].dropna(subset=["pes_cnae47_pib"])
    if not _terr.empty:
        _terr_yr = _terr["any"].max()
        _terr_yr_data = _terr[_terr["any"] == _terr_yr]
        _t_top = _terr_yr_data.nlargest(1, "pes_cnae47_pib").iloc[0]
        _t_bot = _terr_yr_data.nsmallest(1, "pes_cnae47_pib").iloc[0]
        if _ca:
            _conclusions.append(
                f"El pes territorial del comerç al detall varia entre el <strong>{fpct(_t_top['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_top['territori']} i el <strong>{fpct(_t_bot['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_bot['territori']} ({int(_terr_yr)})."
            )
        else:
            _conclusions.append(
                f"El peso territorial del comercio minorista varía entre el <strong>{fpct(_t_top['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_top['territori']} y el <strong>{fpct(_t_bot['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_bot['territori']} ({int(_terr_yr)})."
            )

if _conclusions:
    _eyebrow = "Resum executiu" if _ca else "Resumen ejecutivo"
    _title = "Principals conclusions" if _ca else "Principales conclusiones"
    _upd_lbl = "Última actualització" if _ca else "Última actualización"

    _last_update_path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "last_update.txt")
    _upd_html = ""
    if os.path.exists(_last_update_path):
        with open(_last_update_path) as f:
            _upd = f.read().strip()
        _upd_html = f'<div class="conclusions-update">{_upd_lbl}: {_upd}</div>'

    _items_html = "".join(f"<li>{c}</li>" for c in _conclusions)

    st.markdown(
        f"""
        <div class="conclusions-block">
            <div class="conclusions-eyebrow">{_eyebrow}</div>
            <h3>{_title}</h3>
            {_upd_html}
            <ul>{_items_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── BUTLLETI ─────────────────────────────────────────────────

st.divider()
newsletter_form(st.session_state.lang)

# ─── BOTÓ DESCÀRREGA EXCEL (al peu) ───────────────────────────


def _build_excel():
    buf = BytesIO()
    wb = None
    try:
        import xlsxwriter
        wb = xlsxwriter.Workbook(buf, {"in_memory": True, "nan_inf_to_errors": True})
    except ImportError:
        return None

    hdr_fmt = wb.add_format({"bold": True, "bg_color": "#003366", "font_color": "white",
                              "border": 1, "font_name": "Calibri", "font_size": 11})
    cell_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11})
    num_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "#,##0"})
    pct_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "0.00%"})
    dec_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "#,##0.0"})

    def _write_header(ws, cols, row=0):
        for c, name in enumerate(cols):
            ws.write(row, c, name, hdr_fmt)

    # --- 1. PIB i VAB ---
    if not df_pib.empty:
        ws = wb.add_worksheet("PIB i VAB")
        cols = ["Any", "VAB nominal (M EUR)", "VAB real (M EUR)", "Pes s/ PIB"]
        _write_header(ws, cols)
        rows_pib = df_pib.sort_values("any")
        for i, (_, r) in enumerate(rows_pib.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("vab_cnae47_corrents"), num_fmt)
            ws.write(i, 2, r.get("vab_cnae47_constants"), num_fmt)
            ws.write(i, 3, r.get("pes_cnae47"), pct_fmt)
        n = len(rows_pib)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 2, 20)
        ws.set_column(3, 3, 14)

        chart = wb.add_chart({"type": "line"})
        chart.add_series({"name": "VAB nominal", "categories": ["PIB i VAB", 1, 0, n, 0],
                          "values": ["PIB i VAB", 1, 1, n, 1], "line": {"color": "#003366", "width": 2.5}})
        chart.add_series({"name": "VAB real", "categories": ["PIB i VAB", 1, 0, n, 0],
                          "values": ["PIB i VAB", 1, 2, n, 2], "line": {"color": "#c0392b", "width": 2.5}})
        chart.set_title({"name": "VAB CNAE 47 (M EUR)"})
        chart.set_x_axis({"name": "Any"})
        chart.set_y_axis({"name": "M EUR"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "bottom"})
        ws.insert_chart("F2", chart)

    # --- 2. Empreses ---
    if not df_empreses.empty:
        ws = wb.add_worksheet("Empreses")
        cols = ["Territori", "Any", "Empreses", "Poblacio", "Empreses/1.000 hab."]
        _write_header(ws, cols)
        rows_emp = df_empreses.sort_values(["territori", "any"])
        for i, (_, r) in enumerate(rows_emp.iterrows(), 1):
            ws.write(i, 0, r["territori"], cell_fmt)
            ws.write(i, 1, int(r["any"]), cell_fmt)
            ws.write(i, 2, int(r["empreses"]) if pd.notna(r["empreses"]) else None, num_fmt)
            ws.write(i, 3, int(r["poblacio"]) if pd.notna(r.get("poblacio")) else None, num_fmt)
            ws.write(i, 4, r.get("empreses_per_1000hab"), dec_fmt)
        ws.set_column(0, 0, 28)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 4, 18)

        esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if len(esp) >= 2:
            ws2_name = "Empreses_ES"
            ws2 = wb.add_worksheet(ws2_name)
            _write_header(ws2, ["Any", "Empreses"])
            for i, (_, r) in enumerate(esp.iterrows(), 1):
                ws2.write(i, 0, int(r["any"]), cell_fmt)
                ws2.write(i, 1, int(r["empreses"]), num_fmt)
            ne = len(esp)
            chart = wb.add_chart({"type": "line"})
            chart.add_series({"name": "Empreses Espanya", "categories": [ws2_name, 1, 0, ne, 0],
                              "values": [ws2_name, 1, 1, ne, 1], "line": {"color": "#003366", "width": 2.5}})
            chart.set_title({"name": "Empreses CNAE 47 - Espanya"})
            chart.set_size({"width": 620, "height": 380})
            chart.set_legend({"position": "none"})
            ws2.insert_chart("D2", chart)
            ws2.set_column(0, 0, 8)
            ws2.set_column(1, 1, 14)

    # --- 3. Productivitat ---
    if not df_prod.empty:
        ws = wb.add_worksheet("Productivitat")
        cols = ["Any", "Personal ocupat", "Hores treballades", "Productivitat (EUR/h)",
                "Quota salarial", "Cost laboral/ocupat"]
        _write_header(ws, cols)
        rows_p = df_prod.sort_values("any")
        for i, (_, r) in enumerate(rows_p.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("personal_ocupat"), num_fmt)
            ws.write(i, 2, r.get("hores_treballades"), num_fmt)
            ws.write(i, 3, r.get("productivitat_va_hora"), dec_fmt)
            ws.write(i, 4, r.get("quota_salarial"), pct_fmt)
            ws.write(i, 5, r.get("cost_laboral_per_ocupat"), num_fmt)
        np_ = len(rows_p)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 5, 22)

        chart = wb.add_chart({"type": "line"})
        chart.add_series({"name": "Productivitat (EUR/h)", "categories": ["Productivitat", 1, 0, np_, 0],
                          "values": ["Productivitat", 1, 3, np_, 3], "line": {"color": "#003366", "width": 2.5}})
        chart.set_title({"name": "Productivitat VA/hora (EUR)"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "none"})
        ws.insert_chart("H2", chart)

    # --- 4. E-commerce ---
    if not df_ecommerce.empty:
        ws = wb.add_worksheet("E-commerce")
        cols = ["Any", "E-commerce total (EUR)", "E-commerce CNAE 47 (EUR)", "Pes CNAE 47"]
        _write_header(ws, cols)
        rows_ec = df_ecommerce.sort_values("any")
        for i, (_, r) in enumerate(rows_ec.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("ecommerce_total_eur"), num_fmt)
            ws.write(i, 2, r.get("ecommerce_cnae47_eur"), num_fmt)
            ws.write(i, 3, r.get("pes_cnae47_ecommerce"), pct_fmt)
        nec = len(rows_ec)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 2, 24)
        ws.set_column(3, 3, 14)

        chart = wb.add_chart({"type": "column"})
        chart.add_series({"name": "E-commerce CNAE 47", "categories": ["E-commerce", 1, 0, nec, 0],
                          "values": ["E-commerce", 1, 2, nec, 2], "fill": {"color": "#003366"}})
        chart.set_title({"name": "E-commerce CNAE 47 (EUR)"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "none"})
        ws.insert_chart("F2", chart)

    # --- 5. Territori ---
    if not df_territori.empty:
        ws = wb.add_worksheet("Territori CCAA")
        cols = ["Territori", "Any", "Locals", "Personal ocupat", "VAB estimat (EUR)",
                "VAB Eurostat (EUR)", "Pes CNAE 47/PIB"]
        _write_header(ws, cols)
        rows_t = df_territori.sort_values(["territori", "any"])
        for i, (_, r) in enumerate(rows_t.iterrows(), 1):
            ws.write(i, 0, r["territori"], cell_fmt)
            ws.write(i, 1, int(r["any"]), cell_fmt)
            ws.write(i, 2, r.get("locals"), num_fmt)
            ws.write(i, 3, r.get("personal_ocupat"), num_fmt)
            ws.write(i, 4, r.get("vab_estimat"), num_fmt)
            ws.write(i, 5, r.get("vab_eurostat"), num_fmt)
            ws.write(i, 6, r.get("pes_cnae47_pib"), pct_fmt)
        ws.set_column(0, 0, 28)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 6, 20)

        terr_last = df_territori[
            (df_territori["territori"] != "espanya") &
            df_territori["pes_cnae47_pib"].notna()
        ]
        if not terr_last.empty:
            yr_max = terr_last["any"].max()
            tdata = terr_last[terr_last["any"] == yr_max].sort_values("pes_cnae47_pib", ascending=False)
            ws2_name = "Pes CCAA"
            ws2 = wb.add_worksheet(ws2_name)
            _write_header(ws2, ["CCAA", "Pes CNAE 47/PIB"])
            for i, (_, r) in enumerate(tdata.iterrows(), 1):
                ws2.write(i, 0, r["territori"], cell_fmt)
                ws2.write(i, 1, r["pes_cnae47_pib"], pct_fmt)
            nt = len(tdata)
            ws2.set_column(0, 0, 28)
            ws2.set_column(1, 1, 18)

            chart = wb.add_chart({"type": "bar"})
            chart.add_series({"name": f"Pes CNAE 47/PIB ({int(yr_max)})",
                              "categories": [ws2_name, 1, 0, nt, 0],
                              "values": [ws2_name, 1, 1, nt, 1],
                              "fill": {"color": "#003366"}})
            chart.set_title({"name": f"Pes del comerç al detall sobre el PIB ({int(yr_max)})"})
            chart.set_size({"width": 700, "height": 480})
            chart.set_legend({"position": "none"})
            chart.set_y_axis({"reverse": True})
            ws2.insert_chart("D2", chart)

    # --- 6. Europa ---
    if not df_europa.empty:
        ws = wb.add_worksheet("Europa")
        cols = ["Pais", "Codi", "Any", "VAB CNAE 47 (M EUR)", "VAB total (M EUR)", "Pes CNAE 47"]
        _write_header(ws, cols)
        rows_eu = df_europa.sort_values(["pais", "any"])
        for i, (_, r) in enumerate(rows_eu.iterrows(), 1):
            ws.write(i, 0, r.get("pais", ""), cell_fmt)
            ws.write(i, 1, r.get("pais_codi", ""), cell_fmt)
            ws.write(i, 2, int(r["any"]), cell_fmt)
            ws.write(i, 3, r.get("vab_meur"), num_fmt)
            ws.write(i, 4, r.get("vab_total_meur"), num_fmt)
            ws.write(i, 5, r.get("pes_cnae47"), pct_fmt)
        ws.set_column(0, 0, 18)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 2, 8)
        ws.set_column(3, 5, 22)

    wb.close()
    buf.seek(0)
    return buf


st.divider()
_excel_buf = _build_excel()
if _excel_buf:
    st.download_button(
        label=("Descarregar Excel amb totes les dades" if _ca
               else "Descargar Excel con todos los datos"),
        data=_excel_buf,
        file_name="observatori_comerc_detall.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("xlsxwriter no disponible" if _ca else "xlsxwriter no disponible")

# ─── SIGNATURA JBJ ─────────────────────────────────────────────

st.markdown(
    """
    <div style="text-align:right; color:#888; font-size:12px;
                font-family:'Inter',sans-serif; margin-top:12px;">
        Observatorio del Comercio · J3B3 Consulting
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── META ─────────────────────────────────────────────────────

page_meta("INE, Eurostat, CNMC", st.session_state.lang)

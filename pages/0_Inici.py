"""Pàgina d'inici: hero amb número-xoc + tesi vigent, KPIs, Pols diari, cards de
navegació per dimensió, conclusions executives, butlletí."""
import json
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, fnum, fpct,
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
def load_tesi(sig=None):
    # La tesi vigent de la home = titular de l'ÚLTIMA edició del Pulso, llegit
    # directament de l'arxiu mirall (data/newsletter/semana-*.md) — la MATEIXA
    # font que L_Lecturas. Així home i Pulso no poden divergir mai. Abans depenia
    # de tesi_vigent.json, que una recuperació manual d'edició (enviament via
    # Brevo que salta mirror.py) podia deixar enrere. `sig` = llista d'edicions:
    # quan n'entra una de nova, la caché es refresca a l'instant.
    ndir = os.path.join(os.path.dirname(__file__), "..", "data", "newsletter")
    try:
        mds = sorted(
            (f for f in os.listdir(ndir)
             if f.startswith("semana-") and f.endswith(".md")),
            reverse=True,
        )
    except OSError:
        return None
    for fname in mds:
        mdate = re.match(r"semana-(\d{4}-\d{2}-\d{2})\.md$", fname)
        if not mdate:
            continue
        try:
            with open(os.path.join(ndir, fname), "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        mt = re.search(r"(?m)^\*\*Titular:\*\*\s*(.+)$", text)
        if not mt:
            continue
        return {
            "titol": mt.group(1).strip(),
            "data_publicacio": mdate.group(1),
            "autor": "Observatorio del Comercio · J3B3 Consulting",
            "enllac_pulso": None,
        }
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
df_icm = load_data("icm")

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

# El Pols diari (CDMGE) és una estadística experimental de l'INE que
# s'actualitza de forma irregular. Si la darrera dada té més de 30 dies,
# deixa de ser representativa com a "darrers 30 dies" i la retirem de la
# home (es manté la pàgina pròpia al sidebar). El hero passa a l'ICM.
POLS_LAG_LLINDAR = 30
_pulse_fresc = _pulse is not None and _pulse["lag_days"] <= POLS_LAG_LLINDAR

# Fallback fresc per al hero quan el Pols diari és obsolet: variació anual
# real de l'ICM mensual (Pols mensual), branca general CNAE 47.
_icm_hero = None
if not _pulse_fresc and not df_icm.empty and "ambit" in df_icm.columns:
    _s = df_icm[(df_icm["ambit"] == "nacional") &
                (df_icm["tipus"] == "real") &
                (df_icm["indicador"] == "var_anual") &
                (df_icm["branca"] == "Comercio al por menor, excepto de vehículos de motor y motocicletas")].copy()
    _s = _s.dropna(subset=["valor"])
    if not _s.empty:
        _s["data"] = pd.to_datetime(_s["data"], errors="coerce")
        _s = _s.dropna(subset=["data"]).sort_values("data")
        if not _s.empty:
            _icm_hero = {"valor": float(_s.iloc[-1]["valor"]), "data": _s.iloc[-1]["data"]}

# ─── HERO: NÚMERO-XOC (esquerra) + TESI VIGENT (dreta) ─────────

_ndir = os.path.join(os.path.dirname(__file__), "..", "data", "newsletter")
try:
    _sig = tuple(sorted(f for f in os.listdir(_ndir)
                        if f.startswith("semana-") and f.endswith(".md")))
except OSError:
    _sig = ()
_tesi = load_tesi(_sig)
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
# Una tesi editorial datada no caduca als 10 dies: es mostra sempre l'última
# disponible amb la seva data (el lector jutja la vigència). Només es considera
# "absent" si no hi ha tesi o data vàlida; en aquest cas no s'omple amb soroll.
_tesi_obsoleta = (_tesi_data is None)

hero_l, hero_r = st.columns([3, 2], gap="large")

with hero_l:
    if _pulse_fresc:
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
    elif _icm_hero is not None:
        # Fallback: el Pols diari està obsolet (>30d). Mostrem l'ICM mensual,
        # que sí és fresc, com a número-xoc del hero.
        _sign_color = "#003366" if _icm_hero["valor"] >= 0 else "#c0392b"
        _sign_text = fpct(_icm_hero["valor"], 1)
        _eyebrow_l = ("Pols del consum · darrer mes (ICM)"
                      if _ca else
                      "Pulso del consumo · último mes (ICM)")
        _sub_l = ("Variació anual de la xifra de negoci real del comerç al detall"
                  if _ca else
                  "Variación anual de la cifra de negocio real del comercio minorista")
        _asof_l = "Darrera dada" if _ca else "Último dato"
        from style import format_mes_any as _fma
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
                    {_sub_l}
                </div>
                <div style="color:#6a6a6a; font-size:12px; margin-top:10px;">
                    {_asof_l}: {_fma(_icm_hero['data'], st.session_state.lang)} · INE, ICM
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
        # Sense tesi disponible (cas excepcional): bloc net amb l'enllaç al Pulso,
        # sense "pendent d'actualitzar" ni dades de cache (eren soroll).
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
                <div style="color:#003366; font-size:15px; font-weight:600;
                            line-height:1.35; font-family:'Archivo Narrow',sans-serif;">
                    {"La lectura de la setmana, al Pulso." if _ca
                     else "La lectura de la semana, en el Pulso."}
                </div>
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
if _pulse_fresc and _pulse["lag_days"] > 21:
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

# ─── NOVETATS (alertes d'actualització de dades) ───────────────

@st.cache_data(ttl=600)
def load_updates_log():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "updates_log.json")
    if not os.path.exists(p):
        return {"events": []}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"events": []}


def _fmt_marker(marker, lang):
    """Formata el marcador de data d'un event (any / mes-any / data)."""
    parts = str(marker).split("-")
    if len(parts) == 1:
        return parts[0]  # any
    try:
        if len(parts) == 2:  # YYYY-MM
            from style import format_mes_any as _fma
            return _fma(date(int(parts[0]), int(parts[1]), 1), lang)
        if len(parts) == 3:  # YYYY-MM-DD
            return f"{int(parts[2]):02d}/{int(parts[1]):02d}/{parts[0]}"
    except (ValueError, TypeError):
        return str(marker)
    return str(marker)


_upd_log = load_updates_log()
_NOVETATS_DIES = 14
_recents = []
for _ev in _upd_log.get("events", []):
    try:
        _det = date.fromisoformat(_ev.get("detected_at", ""))
    except (TypeError, ValueError):
        continue
    _ago = (_avui - _det).days
    if 0 <= _ago <= _NOVETATS_DIES:
        _recents.append((_ev, _ago))

if _recents:
    _nov_eyebrow = "Novetats" if _ca else "Novedades"
    _nov_sub = ("Actualitzacions de dades dels darrers 14 dies"
                if _ca else "Actualizaciones de datos de los últimos 14 días")
    _items_html = ""
    for _ev, _ago in _recents:
        _lbl = _ev.get("label_ca" if _ca else "label_es", _ev.get("dataset", ""))
        _marker_fmt = _fmt_marker(_ev.get("last_data", ""), st.session_state.lang)
        if _ago == 0:
            _when = "avui" if _ca else "hoy"
        elif _ago == 1:
            _when = "ahir" if _ca else "ayer"
        else:
            _when = (f"fa {_ago} dies" if _ca else f"hace {_ago} días")
        _verb = "actualitzat amb dades de" if _ca else "actualizado con datos de"
        _items_html += (
            f"<div style='display:flex; justify-content:space-between; align-items:baseline;"
            f" gap:12px; padding:7px 0; border-bottom:1px solid rgba(0,51,102,0.08);'>"
            f"<span style='font-size:13px; color:#1a1a1a;'>"
            f"<strong style='color:#003366;'>{_lbl}</strong> {_verb} {_marker_fmt}</span>"
            f"<span style='font-size:11.5px; color:#6a6a6a; white-space:nowrap;'>{_when}</span>"
            f"</div>"
        )
    st.markdown(
        f"""
        <div style="border-top:3px solid #f5d800; background:rgba(245,216,0,0.06);
                    padding:16px 18px 8px 18px; margin:6px 0 22px;
                    font-family:'Inter',sans-serif;">
            <div style="font-family:'Archivo Narrow',sans-serif; font-size:0.82rem;
                        font-weight:700; text-transform:uppercase; color:#003366;
                        margin-bottom:2px;">
                {_nov_eyebrow}
            </div>
            <div style="font-size:12px; color:#6a6a6a; margin-bottom:8px;">{_nov_sub}</div>
            {_items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── ORIENTACIÓ (primer cop) ───────────────────────────────────

_orient_ca = (
    "Primer cop aquí? Comença pel <strong>Pols diari</strong> per veure el termòmetre "
    "immediat del consum, o explora les sis radiografies de sota per entendre "
    "l'estructura del sector. El <strong>Pulso setmanal</strong> connecta les dades "
    "amb el cicle econòmic."
)
_orient_es = (
    "¿Primera visita? Empieza por el <strong>Pulso diario</strong> para ver el termómetro "
    "inmediato del consumo, o explora las seis radiografías de abajo para entender "
    "la estructura del sector. El <strong>Pulso semanal</strong> conecta los datos "
    "con el ciclo económico."
)
st.markdown(
    f"""
    <div style="background:rgba(0,51,102,0.04); border-left:3px solid #003366;
                padding:12px 16px; margin:0 0 4px 0;
                font-family:'Inter',sans-serif; font-size:13px; line-height:1.55;
                color:#1a1a1a;">
        {_orient_ca if _ca else _orient_es}
    </div>
    """,
    unsafe_allow_html=True,
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

# ─── BUTLLETI ─────────────────────────────────────────────────

st.divider()
newsletter_form(st.session_state.lang)

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

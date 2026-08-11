"""Pols mensual del comerç al detall espanyol (ICM, INE).

Sèrie mensual oficial de l'INE — Índices de Comercio al por Menor:
cifra de negoci a preus constants i corrents + ocupació, per branca
CNAE 47 i per Comunitat Autònoma. Base 2021=100.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, inject_premium_page_css, setup_lang, page_header,
                   insight, source, page_meta, fnum, fpct, apply_layout,
                   highlight_expander, format_mes_any,
                   kicker, action_title, deck, key_takeaways, exhibit_header,
                   NAVY, OCRE_DEEP, RED, G1_P, G2_P, GRAY_DARK,
                   freshness_badge)

inject_css()
inject_premium_page_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"


@st.cache_data(ttl=3600)
def load_icm():
    base = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
    pq = os.path.join(base, "icm.parquet")
    if os.path.exists(pq):
        df = pd.read_parquet(pq)
    else:
        csv = os.path.join(base, "icm.csv")
        if not os.path.exists(csv):
            return pd.DataFrame()
        df = pd.read_csv(csv)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df.dropna(subset=["data"])


@st.cache_data(ttl=3600)
def load_icm_distribucion():
    base = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
    pq = os.path.join(base, "icm_distribucion.parquet")
    if os.path.exists(pq):
        df = pd.read_parquet(pq)
    else:
        csv = os.path.join(base, "icm_distribucion.csv")
        if not os.path.exists(csv):
            return pd.DataFrame()
        df = pd.read_csv(csv)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df.dropna(subset=["data"])


df = load_icm()
df_distrib = load_icm_distribucion()

kicker("Pols mensual del consum · ICM (INE)" if _ca
       else "Pulso mensual del consumo · ICM (INE)")

if df.empty:
    st.warning(
        "No hi ha dades ICM disponibles. Executa el processador."
        if _ca else
        "No hay datos ICM disponibles. Ejecuta el procesador."
    )
    st.stop()

# Branca general CNAE 47 estricta (sense vehicles)
BRANCA_GENERAL_47 = "Comercio al por menor, excepto de vehículos de motor y motocicletas"
# Branca neta (sense estacions de servei)
BRANCA_NETA = "Comercio al por menor sin Estaciones de Servicio (47 sin 473)"

# Mapping codis CNAE → etiqueta editorial
BRANCA_LBL_CA = {
    BRANCA_GENERAL_47: "General CNAE 47",
    BRANCA_NETA: "Sense benzineres (47 sense 473)",
    "Alimentación (4711+472)": "Alimentació",
    "Resto (sin Alim. ni Est. Serv.)": "Resta (no alim., no benzineres)",
    "Equipo personal (4771+4772)": "Equipament personal",
    "Equipo del hogar": "Equipament de la llar",
    "Equipamiento del hogar (475)": "Equipament de la llar (475)",
    "Otros bienes para uso doméstico (475)": "Altres béns ús domèstic",
    "Comercio al por menor de combustible para la automoción en establecimientos especializados": "Estacions de servei",
    "Salud (4773+4774+4775)": "Salut i cura personal",
    "Establecimientos no especializados (471)": "Establiments no especialitzats (471)",
}
BRANCA_LBL_ES = {
    BRANCA_GENERAL_47: "General CNAE 47",
    BRANCA_NETA: "Sin gasolineras (47 sin 473)",
    "Alimentación (4711+472)": "Alimentación",
    "Resto (sin Alim. ni Est. Serv.)": "Resto (no alim., no gasolineras)",
    "Equipo personal (4771+4772)": "Equipo personal",
    "Equipo del hogar": "Equipo del hogar",
    "Equipamiento del hogar (475)": "Equipamiento del hogar (475)",
    "Otros bienes para uso doméstico (475)": "Otros bienes uso doméstico",
    "Comercio al por menor de combustible para la automoción en establecimientos especializados": "Estaciones de servicio",
    "Salud (4773+4774+4775)": "Salud y cuidado personal",
    "Establecimientos no especializados (471)": "Establecimientos no especializados (471)",
}
BRANCA_LBL = BRANCA_LBL_CA if _ca else BRANCA_LBL_ES

# ─── Selector d'àmbit (com l'INE: general o sense estacions de servei) ──
_branca_options = {
    BRANCA_GENERAL_47: ("General (amb estacions de servei)" if _ca
                        else "General (con estaciones de servicio)"),
    BRANCA_NETA: ("Sense estacions de servei (47 sense 473)" if _ca
                  else "Sin estaciones de servicio (47 sin 473)"),
}
BRANCA_SEL = st.radio(
    ("Àmbit del comerç" if _ca else "Ámbito del comercio"),
    list(_branca_options.keys()),
    format_func=lambda b: _branca_options[b],
    index=0, horizontal=True, key="icm_branca_sel",
)
_branca_font_lbl = BRANCA_LBL[BRANCA_SEL]

# ─── KPIs nacionals ────────────────────────────────────────────

df_nac_real = df[(df["ambit"] == "nacional") &
                 (df["tipus"] == "real") &
                 (df["branca"] == BRANCA_SEL)]
df_nac_nom = df[(df["ambit"] == "nacional") &
                (df["tipus"] == "nominal") &
                (df["branca"] == BRANCA_SEL)]
df_nac_ocu = df[(df["ambit"] == "nacional") &
                (df["tipus"] == "ocupacio") &
                (df["branca"] == BRANCA_SEL)]

# Última dada del general real (índex + variació anual)
_last_real_idx = df_nac_real[df_nac_real["indicador"] == "index"].sort_values("data")
_last_real_var = df_nac_real[df_nac_real["indicador"] == "var_anual"].sort_values("data")
_last_nom_var = df_nac_nom[df_nac_nom["indicador"] == "var_anual"].sort_values("data")
_last_ocu_var = df_nac_ocu[df_nac_ocu["indicador"] == "var_anual"].sort_values("data")

# ─── Tesi del titular: última variació real, mitjana 12m, efecte preu ──
_real_v = float(_last_real_var.iloc[-1]["valor"]) if not _last_real_var.empty else None
_nom_v = float(_last_nom_var.iloc[-1]["valor"]) if not _last_nom_var.empty else None
_real_dt = _last_real_var.iloc[-1]["data"] if not _last_real_var.empty else None
_avg12 = (df_nac_real[df_nac_real["indicador"] == "var_anual"]["valor"]
          .tail(12).mean())
_gap = (_nom_v - _real_v) if (_real_v is not None and _nom_v is not None) else None
_mes_titol = format_mes_any(_real_dt, st.session_state.lang) if _real_dt is not None else ""

if _real_v is not None:
    _puja = _real_v > 0
    if _ca:
        _verb = "creix" if _puja else ("cau" if _real_v < 0 else "s'estabilitza")
        action_title(
            f"El consum real {_verb} un {fnum(abs(_real_v), 1)}% interanual"
            if _real_v != 0 else "El consum real s'estabilitza")
        deck(f"Cifra de negoci del comerç al detall a preus constants, "
             f"{_mes_titol}. La bretxa amb el nominal és l'efecte preu.")
    else:
        _verb = "crece" if _puja else ("cae" if _real_v < 0 else "se estabiliza")
        action_title(
            f"El consumo real {_verb} un {fnum(abs(_real_v), 1)}% interanual"
            if _real_v != 0 else "El consumo real se estabiliza")
        deck(f"Cifra de negocio del comercio minorista a precios constantes, "
             f"{_mes_titol}. La brecha con el nominal es el efecto precio.")
else:
    action_title("Pols mensual del comerç" if _ca else "Pulso mensual del comercio")
    deck("Sèrie oficial mensual de l'INE (ICM), base 2021=100." if _ca
         else "Serie oficial mensual del INE (ICM), base 2021=100.")

if _real_v is not None:
    if _ca:
        _tk = [
            f"Al <b>{_mes_titol}</b>, la cifra de negoci real del comerç al "
            f"detall {'creix' if _puja else ('cau' if _real_v < 0 else 'es manté')} "
            f"un <b>{fpct(_real_v, 1)}</b> respecte al mateix mes de l'any anterior.",
            f"En els darrers 12 mesos, la variació anual mitjana s'ha situat al "
            f"<b>{fpct(_avg12, 1)}</b>.",
        ]
        if _gap is not None:
            _tk.append(
                f"El nominal varia un <b>{fpct(_nom_v, 1)}</b>: la bretxa de "
                f"<b>{fnum(abs(_gap), 1)} punts</b> amb el real és, essencialment, "
                f"l'efecte preu.")
        _tk_lbl = "Conclusions clau"
    else:
        _tk = [
            f"En <b>{_mes_titol}</b>, la cifra de negocio real del comercio "
            f"minorista {'crece' if _puja else ('cae' if _real_v < 0 else 'se estabiliza')} "
            f"un <b>{fpct(_real_v, 1)}</b> respecto al mismo mes del año anterior.",
            f"En los últimos 12 meses, la variación anual media se ha situado en "
            f"el <b>{fpct(_avg12, 1)}</b>.",
        ]
        if _gap is not None:
            _tk.append(
                f"El nominal varía un <b>{fpct(_nom_v, 1)}</b>: la brecha de "
                f"<b>{fnum(abs(_gap), 1)} puntos</b> con el real es, esencialmente, "
                f"el efecto precio.")
        _tk_lbl = "Conclusiones clave"
    key_takeaways(_tk, label=_tk_lbl)

freshness_badge(["icm", "icm_distribucion"], st.session_state.lang)

if not _last_real_idx.empty:
    last_data = _last_real_idx.iloc[-1]["data"]
    st.caption(
        ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
        + format_mes_any(last_data, st.session_state.lang)
    )

c1, c2, c3, c4 = st.columns(4)
with c1:
    if not _last_real_idx.empty:
        val = _last_real_idx.iloc[-1]["valor"]
        st.metric(
            ("Índex real (base 2021)" if _ca else "Índice real (base 2021)"),
            f"{fnum(val, 1)}",
        )
with c2:
    if not _last_real_var.empty:
        val = _last_real_var.iloc[-1]["valor"]
        st.metric(
            ("Variació anual (real)" if _ca else "Variación anual (real)"),
            fpct(val, 1),
        )
with c3:
    if not _last_nom_var.empty:
        val = _last_nom_var.iloc[-1]["valor"]
        st.metric(
            ("Variació anual (nominal)" if _ca else "Variación anual (nominal)"),
            fpct(val, 1),
        )
with c4:
    if not _last_ocu_var.empty:
        val = _last_ocu_var.iloc[-1]["valor"]
        st.metric(
            ("Variació ocupació" if _ca else "Variación empleo"),
            fpct(val, 1),
        )

tab1, tab2, tab3, tab4 = st.tabs([
    ("Nacional" if _ca else "Nacional"),
    ("Per branca" if _ca else "Por rama"),
    ("Per CCAA" if _ca else "Por CCAA"),
    ("Per format" if _ca else "Por formato"),
])

with tab1:
    if _ca:
        exhibit_header(
            1, "Real i nominal divergeixen quan els preus es mouen",
            note="Variació anual de la cifra de negoci. La distància entre "
                 "les dues línies és l'efecte preu.")
    else:
        exhibit_header(
            1, "Real y nominal divergen cuando los precios se mueven",
            note="Variación anual de la cifra de negocio. La distancia entre "
                 "las dos líneas es el efecto precio.")

    periodes = {
        ("12 mesos" if _ca else "12 meses"): 12,
        ("24 mesos" if _ca else "24 meses"): 24,
        ("60 mesos" if _ca else "60 meses"): 60,
        ("Des de 2020" if _ca else "Desde 2020"): 999,
    }
    per_lbl = st.radio(
        ("Període" if _ca else "Período"),
        list(periodes.keys()), index=1, horizontal=True, key="icm_per",
    )
    per_n = periodes[per_lbl]

    df_serie_real = df_nac_real[df_nac_real["indicador"] == "var_anual"].sort_values("data")
    df_serie_nom = df[(df["ambit"] == "nacional") & (df["tipus"] == "nominal") &
                      (df["branca"] == BRANCA_SEL) &
                      (df["indicador"] == "var_anual")].sort_values("data")

    if per_n < 999:
        df_serie_real = df_serie_real.tail(per_n)
        df_serie_nom = df_serie_nom.tail(per_n)
    else:
        df_serie_real = df_serie_real[df_serie_real["data"] >= "2020-01-01"]
        df_serie_nom = df_serie_nom[df_serie_nom["data"] >= "2020-01-01"]

    _lang = st.session_state.lang
    _lbl_real = [format_mes_any(d, _lang) for d in df_serie_real["data"]]
    _lbl_nom = [format_mes_any(d, _lang) for d in df_serie_nom["data"]]

    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x=df_serie_real["data"], y=df_serie_real["valor"],
        mode="lines+markers",
        name=("Real (preus constants)" if _ca else "Real (precios constantes)"),
        line=dict(color=NAVY, width=2.6),
        marker=dict(size=5),
        customdata=_lbl_real,
        hovertemplate="%{customdata}: <b>%{y:+.1f}%</b><extra></extra>",
    ))
    fig_evo.add_trace(go.Scatter(
        x=df_serie_nom["data"], y=df_serie_nom["valor"],
        mode="lines+markers",
        name=("Nominal (preus corrents)" if _ca else "Nominal (precios corrientes)"),
        line=dict(color=GRAY_DARK, width=2, dash="dot"),
        marker=dict(size=4),
        customdata=_lbl_nom,
        hovertemplate="%{customdata}: <b>%{y:+.1f}%</b><extra></extra>",
    ))
    fig_evo.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
    apply_layout(fig_evo,
        yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
        height=420,
    )
    # Format numèric a l'eix X per no dependre del locale del browser (que
    # podria mostrar "Mar 2026" en anglès). Ticks com 03/2026.
    fig_evo.update_xaxes(tickformat="%m/%Y")
    st.plotly_chart(fig_evo, use_container_width=True)
    source(f"INE, Índices de Comercio al por Menor (ICM). {_branca_font_lbl}")

    # Insight evolució
    if not df_serie_real.empty and len(df_serie_real) >= 2:
        _last_v = float(df_serie_real.iloc[-1]["valor"])
        _last_dt = df_serie_real.iloc[-1]["data"]
        _avg_12 = df_nac_real[df_nac_real["indicador"] == "var_anual"]["valor"].tail(12).mean()
        _signe = "creix" if _last_v > 0 else ("cau" if _last_v < 0 else "s'estabilitza")
        if _ca:
            insight(
                f"Al <strong>{format_mes_any(_last_dt, 'ca')}</strong>, la cifra de negoci real "
                f"del comerç al detall espanyol <strong>{_signe} un {abs(_last_v):.1f}%</strong> respecte "
                f"al mateix mes de l'any anterior. En els darrers 12 mesos, la variació anual mitjana s'ha "
                f"situat al <strong>{_avg_12:+.1f}%</strong>. "
                f"La diferència entre nominal i real és l'efecte preu: si el nominal creix més que el real, "
                f"part del creixement és simplement inflació."
            )
        else:
            _signe_es = "crece" if _last_v > 0 else ("cae" if _last_v < 0 else "se estabiliza")
            insight(
                f"En <strong>{format_mes_any(_last_dt, 'es')}</strong>, la cifra de negocio real "
                f"del comercio minorista español <strong>{_signe_es} un {abs(_last_v):.1f}%</strong> "
                f"respecto al mismo mes del año anterior. En los últimos 12 meses, la variación anual "
                f"media se ha situado en el <strong>{_avg_12:+.1f}%</strong>. "
                f"La diferencia entre nominal y real es el efecto precio: si el nominal crece más que "
                f"el real, parte del crecimiento es simplemente inflación."
            )

with tab2:
    # Última data disponible amb dades de branques
    _last_dt = df_nac_real["data"].max()
    df_branca = df[(df["ambit"] == "nacional") &
                   (df["tipus"] == "real") &
                   (df["indicador"] == "var_anual") &
                   (df["data"] == _last_dt)].copy()

    # Excloure les variants "Comercio al por menor sin Estaciones..." amb sub-variants
    df_branca = df_branca[~df_branca["branca"].str.contains("General", na=False, regex=False)]
    df_branca["label"] = df_branca["branca"].map(BRANCA_LBL).fillna(df_branca["branca"])
    df_branca = df_branca.drop_duplicates(subset=["branca"]).sort_values("valor", ascending=True)

    _n_pos = int((df_branca["valor"] >= 0).sum())
    _n_tot = len(df_branca)
    if _ca:
        exhibit_header(
            2, f"{_n_pos} de {_n_tot} branques creixen el darrer mes" if _n_tot
               else "Variació anual per branca",
            note="Variació interanual de la cifra de negoci real per branca "
                 "CNAE 47, últim mes disponible.")
    else:
        exhibit_header(
            2, f"{_n_pos} de {_n_tot} ramas crecen en el último mes" if _n_tot
               else "Variación anual por rama",
            note="Variación interanual de la cifra de negocio real por rama "
                 "CNAE 47, último mes disponible.")

    if not df_branca.empty:
        colors_br = [NAVY if v >= 0 else RED for v in df_branca["valor"]]
        fig_br = go.Figure()
        fig_br.add_trace(go.Bar(
            y=df_branca["label"], x=df_branca["valor"],
            orientation="h",
            marker_color=colors_br,
            text=[fpct(v, 1) for v in df_branca["valor"]],
            textposition="outside",
            textfont=dict(size=11),
            name="",
            hovertemplate="<b>%{y}</b>: %{x:+.1f}%<extra></extra>",
        ))
        fig_br.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        apply_layout(fig_br,
            xaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
            height=max(380, len(df_branca) * 32 + 100),
            margin=dict(l=240, r=80, t=30, b=50),
        )
        st.plotly_chart(fig_br, use_container_width=True)
        source(f"INE, ICM. Cifra de negoci a preus constants — {format_mes_any(_last_dt, 'ca')}"
               if _ca else
               f"INE, ICM. Cifra de negocio a precios constantes — {format_mes_any(_last_dt, 'es')}")

with tab3:
    df_ccaa = df[(df["ambit"] != "nacional") &
                 (df["tipus"] == "real") &
                 (df["indicador"] == "var_anual") &
                 (df["branca"] == BRANCA_SEL) &
                 (df["data"] == _last_dt)].copy()
    df_ccaa = df_ccaa.drop_duplicates(subset=["ambit"]).sort_values("valor", ascending=True)

    _n_pos_cc = int((df_ccaa["valor"] >= 0).sum())
    _n_tot_cc = len(df_ccaa)
    if _ca:
        exhibit_header(
            3, f"El consum real creix a {_n_pos_cc} de {_n_tot_cc} comunitats"
               if _n_tot_cc else "Variació anual per CCAA",
            note="Variació interanual de la cifra de negoci real per comunitat "
                 "autònoma, últim mes disponible.")
    else:
        exhibit_header(
            3, f"El consumo real crece en {_n_pos_cc} de {_n_tot_cc} comunidades"
               if _n_tot_cc else "Variación anual por CCAA",
            note="Variación interanual de la cifra de negocio real por comunidad "
                 "autónoma, último mes disponible.")

    if not df_ccaa.empty:
        colors_cc = [NAVY if v >= 0 else RED for v in df_ccaa["valor"]]
        fig_cc = go.Figure()
        fig_cc.add_trace(go.Bar(
            y=df_ccaa["ambit"], x=df_ccaa["valor"],
            orientation="h",
            marker_color=colors_cc,
            text=[fpct(v, 1) for v in df_ccaa["valor"]],
            textposition="outside",
            textfont=dict(size=11),
            name="",
            hovertemplate="<b>%{y}</b>: %{x:+.1f}%<extra></extra>",
        ))
        fig_cc.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        apply_layout(fig_cc,
            xaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
            height=max(450, len(df_ccaa) * 30 + 100),
            margin=dict(l=200, r=80, t=30, b=50),
        )
        st.plotly_chart(fig_cc, use_container_width=True)
        source(f"INE, ICM per CCAA. Cifra de negoci a preus constants ({_branca_font_lbl}) — {format_mes_any(_last_dt, 'ca')}"
               if _ca else
               f"INE, ICM por CCAA. Cifra de negocio a precios constantes ({_branca_font_lbl}) — {format_mes_any(_last_dt, 'es')}")

with tab4:
    if _ca:
        exhibit_header(
            4, "La bretxa entre formats marca el ritme de la concentració",
            note="Variació anual de la cifra de negoci real per modo de "
                 "distribució comercial.")
    else:
        exhibit_header(
            4, "La brecha entre formatos marca el ritmo de la concentración",
            note="Variación anual de la cifra de negocio real por modo de "
                 "distribución comercial.")

    if _ca:
        st.markdown(
            "Desglossament de l'ICM per **modo de distribució comercial**: "
            "*Empreses unilocalitzades* (un sol establiment), *Petites cadenes* "
            "(2 a 24 botigues), *Grans cadenes* (25 o més) i *Grans superfícies* "
            "(≥2.500 m² de venda). Substitueix la sèrie històrica IGS, "
            "descatalogada el desembre de 2023."
        )
    else:
        st.markdown(
            "Desglose del ICM por **modo de distribución comercial**: "
            "*Empresas unilocalizadas* (un solo establecimiento), *Pequeñas cadenas* "
            "(2 a 24 tiendas), *Grandes cadenas* (25 o más) y *Grandes Superficies* "
            "(≥2.500 m² de venta). Sustituye a la serie histórica IGS, "
            "descatalogada en diciembre de 2023."
        )

    if df_distrib.empty:
        st.info("Encara no hi ha dades de modos de distribució a la cache."
                if _ca else
                "Aún no hay datos de modos de distribución en la caché.")
    else:
        # Sèrie real (preus constants), variació anual, ordenada per modo
        _ds = df_distrib[(df_distrib["tipus"] == "real") &
                         (df_distrib["indicador"] == "var_anual")].copy()
        _ds = _ds.sort_values("data")

        _modo_lbl_ca = {
            "Empresas unilocalizadas": "Unilocalitzades",
            "Pequeñas cadenas": "Petites cadenes",
            "Grandes cadenas": "Grans cadenes",
            "Grandes Superficies": "Grans superfícies",
        }
        _modo_lbl_es = {
            "Empresas unilocalizadas": "Unilocalizadas",
            "Pequeñas cadenas": "Pequeñas cadenas",
            "Grandes cadenas": "Grandes cadenas",
            "Grandes Superficies": "Grandes Superficies",
        }
        _modo_lbl = _modo_lbl_ca if _ca else _modo_lbl_es

        # Mètriques: última variació anual de cada modo
        _last_dt_d = _ds["data"].max()
        _last = _ds[_ds["data"] == _last_dt_d]
        st.caption(
            ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
            + format_mes_any(_last_dt_d, st.session_state.lang)
        )
        _cols_m = st.columns(4)
        _modo_order = ["Empresas unilocalizadas", "Pequeñas cadenas",
                       "Grandes cadenas", "Grandes Superficies"]
        for i, m in enumerate(_modo_order):
            with _cols_m[i]:
                _row = _last[_last["modo"] == m]
                if not _row.empty:
                    _v = float(_row.iloc[0]["valor"])
                    st.metric(_modo_lbl[m], fpct(_v, 1))
                else:
                    st.metric(_modo_lbl[m], "—")

        # Sèrie 36 mesos amb 4 línies
        _cutoff = _last_dt_d - pd.Timedelta(days=365 * 3)
        _ds_plot = _ds[_ds["data"] >= _cutoff]

        fig_d = go.Figure()
        _colors_d = {
            "Empresas unilocalizadas": OCRE_DEEP,
            "Pequeñas cadenas": G1_P,
            "Grandes cadenas": NAVY,
            "Grandes Superficies": G2_P,
        }
        for m in _modo_order:
            _serie = _ds_plot[_ds_plot["modo"] == m].sort_values("data")
            if _serie.empty:
                continue
            _lbl_serie = [format_mes_any(d, st.session_state.lang) for d in _serie["data"]]
            fig_d.add_trace(go.Scatter(
                x=_serie["data"], y=_serie["valor"],
                mode="lines+markers",
                name=_modo_lbl[m],
                line=dict(color=_colors_d[m], width=2.4),
                marker=dict(size=4),
                customdata=_lbl_serie,
                hovertemplate=f"<b>{_modo_lbl[m]}</b><br>%{{customdata}}: %{{y:+.1f}}%<extra></extra>",
            ))
        fig_d.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
        apply_layout(fig_d,
            yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
            height=420,
        )
        fig_d.update_xaxes(tickformat="%m/%Y")
        st.plotly_chart(fig_d, use_container_width=True)
        source(("INE, ICM per modo de distribució (taula 75809). Preus constants, "
                "Comerç sense estacions de servei.") if _ca else
               ("INE, ICM por modo de distribución (tabla 75809). Precios constantes, "
                "Comercio sin estaciones de servicio."))

        # Insight curt
        if not _last.empty:
            _by_modo = {m: float(_last[_last["modo"] == m].iloc[0]["valor"])
                        for m in _modo_order if not _last[_last["modo"] == m].empty}
            if len(_by_modo) >= 2:
                _best = max(_by_modo, key=_by_modo.get)
                _worst = min(_by_modo, key=_by_modo.get)
                if _ca:
                    insight(
                        f"A <strong>{format_mes_any(_last_dt_d, 'ca')}</strong>, "
                        f"el format que millor evoluciona és <strong>{_modo_lbl[_best]}</strong> "
                        f"({fpct(_by_modo[_best], 1)}), i el que va més fluix és "
                        f"<strong>{_modo_lbl[_worst]}</strong> ({fpct(_by_modo[_worst], 1)}). "
                        f"La bretxa entre formats indica si la concentració del retail accelera "
                        f"o es modera."
                    )
                else:
                    insight(
                        f"En <strong>{format_mes_any(_last_dt_d, 'es')}</strong>, "
                        f"el formato con mejor evolución es <strong>{_modo_lbl[_best]}</strong> "
                        f"({fpct(_by_modo[_best], 1)}), y el más flojo es "
                        f"<strong>{_modo_lbl[_worst]}</strong> ({fpct(_by_modo[_worst], 1)}). "
                        f"La brecha entre formatos indica si la concentración del retail acelera "
                        f"o se modera."
                    )

        # ─── Ocupació per modo ──────────────────────────────
        st.markdown("---")
        if _ca:
            st.markdown(
                "**Ocupació** per modo de distribució (nombre de treballadors, "
                "variació anual). Mateixa font i desglossament que la cifra de negoci."
            )
        else:
            st.markdown(
                "**Ocupación** por modo de distribución (número de trabajadores, "
                "variación anual). Misma fuente y desglose que la cifra de negocio."
            )

        _do = df_distrib[(df_distrib["tipus"] == "ocupacio") &
                         (df_distrib["indicador"] == "var_anual")].copy()
        _do = _do.sort_values("data")

        if _do.empty:
            st.info("Encara no hi ha dades d'ocupació per modo a la cache."
                    if _ca else
                    "Aún no hay datos de empleo por modo en la caché.")
        else:
            _last_dt_o = _do["data"].max()
            _last_o = _do[_do["data"] == _last_dt_o]
            st.caption(
                ("Darrera dada disponible: " if _ca else "Último dato disponible: ")
                + format_mes_any(_last_dt_o, st.session_state.lang)
            )
            _cols_o = st.columns(4)
            for i, m in enumerate(_modo_order):
                with _cols_o[i]:
                    _row = _last_o[_last_o["modo"] == m]
                    if not _row.empty:
                        _v = float(_row.iloc[0]["valor"])
                        st.metric(_modo_lbl[m], fpct(_v, 1))
                    else:
                        st.metric(_modo_lbl[m], "—")

            _cutoff_o = _last_dt_o - pd.Timedelta(days=365 * 3)
            _do_plot = _do[_do["data"] >= _cutoff_o]

            fig_o = go.Figure()
            for m in _modo_order:
                _serie = _do_plot[_do_plot["modo"] == m].sort_values("data")
                if _serie.empty:
                    continue
                _lbl_serie = [format_mes_any(d, st.session_state.lang) for d in _serie["data"]]
                fig_o.add_trace(go.Scatter(
                    x=_serie["data"], y=_serie["valor"],
                    mode="lines+markers",
                    name=_modo_lbl[m],
                    line=dict(color=_colors_d[m], width=2.4),
                    marker=dict(size=4),
                    customdata=_lbl_serie,
                    hovertemplate=f"<b>{_modo_lbl[m]}</b><br>%{{customdata}}: %{{y:+.1f}}%<extra></extra>",
                ))
            fig_o.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
            apply_layout(fig_o,
                yaxis_title=("Variació anual ocupació (%)" if _ca else "Variación anual empleo (%)"),
                height=420,
            )
            fig_o.update_xaxes(tickformat="%m/%Y")
            st.plotly_chart(fig_o, use_container_width=True)
            source(("INE, ICM ocupació per modo de distribució (taula 60115).") if _ca else
                   ("INE, ICM empleo por modo de distribución (tabla 60115)."))

            if not _last_o.empty:
                _by_modo_o = {m: float(_last_o[_last_o["modo"] == m].iloc[0]["valor"])
                            for m in _modo_order if not _last_o[_last_o["modo"] == m].empty}
                if len(_by_modo_o) >= 2:
                    _best_o = max(_by_modo_o, key=_by_modo_o.get)
                    _worst_o = min(_by_modo_o, key=_by_modo_o.get)
                    if _ca:
                        insight(
                            f"A <strong>{format_mes_any(_last_dt_o, 'ca')}</strong>, "
                            f"l'ocupació creix més a <strong>{_modo_lbl[_best_o]}</strong> "
                            f"({fpct(_by_modo_o[_best_o], 1)}) i cau més a "
                            f"<strong>{_modo_lbl[_worst_o]}</strong> ({fpct(_by_modo_o[_worst_o], 1)}). "
                            f"Quan vendes i ocupació cauen alhora en un mateix format, "
                            f"la desacceleració és estructural, no només de preus."
                        )
                    else:
                        insight(
                            f"En <strong>{format_mes_any(_last_dt_o, 'es')}</strong>, "
                            f"el empleo crece más en <strong>{_modo_lbl[_best_o]}</strong> "
                            f"({fpct(_by_modo_o[_best_o], 1)}) y cae más en "
                            f"<strong>{_modo_lbl[_worst_o]}</strong> ({fpct(_by_modo_o[_worst_o], 1)}). "
                            f"Cuando ventas y empleo caen a la vez en un mismo formato, "
                            f"la desaceleración es estructural, no solo de precios."
                        )

# ─── Expander: evolució ocupació ──────────────────────────────

_lbl_ocu_exp = ("Veure evolució de l'ocupació mensual"
                if _ca else
                "Ver evolución del empleo mensual")
with highlight_expander(_lbl_ocu_exp, expanded=False):
    df_ocu_serie = df_nac_ocu[df_nac_ocu["indicador"] == "var_anual"].sort_values("data")
    if per_n < 999:
        df_ocu_serie = df_ocu_serie.tail(per_n)
    else:
        df_ocu_serie = df_ocu_serie[df_ocu_serie["data"] >= "2020-01-01"]

    _lbl_ocu = [format_mes_any(d, st.session_state.lang) for d in df_ocu_serie["data"]]
    fig_ocu = go.Figure()
    fig_ocu.add_trace(go.Scatter(
        x=df_ocu_serie["data"], y=df_ocu_serie["valor"],
        mode="lines+markers",
        line=dict(color=NAVY, width=2.6),
        marker=dict(size=5),
        name="",
        customdata=_lbl_ocu,
        hovertemplate="%{customdata}: <b>%{y:+.1f}%</b><extra></extra>",
    ))
    fig_ocu.add_hline(y=0, line_dash="solid", line_color="#999", line_width=1)
    apply_layout(fig_ocu,
        yaxis_title=("Variació anual ocupats (%)" if _ca else "Variación anual ocupados (%)"),
        height=380,
    )
    fig_ocu.update_xaxes(tickformat="%m/%Y")
    st.plotly_chart(fig_ocu, use_container_width=True)
    source("INE, ICM ocupació mensual" if _ca else "INE, ICM empleo mensual")

page_meta("INE, Índices de Comercio al por Menor (ICM)", st.session_state.lang)

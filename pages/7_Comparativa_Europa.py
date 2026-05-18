"""Pàgina Comparativa Europa — fusió Europa + Estructura UE (Fase 1).

Quatre blocs en aquest ordre:
  1. Posicionament estructural (pes CNAE 47/PIB per país, ES vermell)
  2. Evolució del posicionament (línies ES/DE/FR/IT/PT/UE-27)
  3. Dimensió estructural (4 gràfics Eurostat bd_size: mida, rotació, mida mitjana, supervivència)
  4. Pols mensual europeu (índex volum vendes sts_trtu_m)

Cada bloc inclou un placeholder LECTURA visible per a la redacció de Jordi.
Fonts: Eurostat nama_10_a64, sts_trtu_m, bd_size. CNAE G47 estricte.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, intro, source, page_meta,
                   fnum, fpct, apply_layout,
                   PURPLE, PURPLE_LIGHT, RED, BLUE, GREEN, ORANGE, GRAY)

inject_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"

# ─── Càrrega de dades ──────────────────────────────────────────

@st.cache_data(ttl=3600)
def _load_csv(name):
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", f"{name}.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

df_europa = _load_csv("europa_vab")              # anual: pes CNAE 47/PIB per país
df_mens = _load_csv("europa_retail_mensual")     # mensual: índex volum vendes
df_total = _load_csv("estructura_retail")        # anual: indicadors estructurals bd_size
df_mida = _load_csv("estructura_retail_mida")    # anual: per mida d'empresa
df_surv = _load_csv("estructura_retail_supervivencia")  # anual: supervivència Y1/Y2

# ─── Helper: caixa de placeholder LECTURA ──────────────────────

def lectura_placeholder():
    """Bloc visualment destacat per a una lectura interpretativa pendent."""
    txt = ("Pendent — text per redactar (Jordi)" if _ca
           else "Pendiente — texto por redactar (Jordi)")
    st.markdown(
        f"""
        <div style="background:#fff8e1; border-left:4px solid #f0a500;
                    padding:14px 18px; margin:8px 0 24px; border-radius:3px;
                    font-family:'DM Sans',sans-serif;">
            <div style="font-size:10px; font-weight:700; letter-spacing:1.5px;
                        text-transform:uppercase; color:#f0a500; margin-bottom:6px;">
                LECTURA · Jordi Bacaria · J3B3 Consulting
            </div>
            <div style="color:#555; font-size:14px; font-style:italic;">
                [{txt}]
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Capçalera ─────────────────────────────────────────────────

st.title("Comparativa Europa" if _ca else "Comparativa Europa")

if _ca:
    intro(
        "Aquesta pàgina situa el comerç al detall espanyol en el context europeu des de quatre angles: "
        "(1) <strong>posicionament estructural</strong> per pes sobre el PIB, "
        "(2) <strong>evolució</strong> del pes per principals economies, "
        "(3) <strong>dimensió estructural</strong> de la demografia empresarial i "
        "(4) <strong>pols mensual</strong> del volum de vendes. "
        "Espanya es destaca en vermell per facilitar la comparació."
    )
else:
    intro(
        "Esta página sitúa el comercio minorista español en el contexto europeo desde cuatro ángulos: "
        "(1) <strong>posicionamiento estructural</strong> por peso sobre el PIB, "
        "(2) <strong>evolución</strong> del peso por principales economías, "
        "(3) <strong>dimensión estructural</strong> de la demografía empresarial y "
        "(4) <strong>pulso mensual</strong> del volumen de ventas. "
        "España se destaca en rojo para facilitar la comparación."
    )

if df_europa.empty and df_mens.empty and df_total.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# BLOC 1 — POSICIONAMENT ESTRUCTURAL
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("1. " + ("Posicionament estructural" if _ca else "Posicionamiento estructural"))

if not df_europa.empty and "pes_cnae47" in df_europa.columns:
    anys_disp = sorted(df_europa["any"].dropna().unique(), reverse=True)
    any_sel = st.selectbox(
        ("Any de referència" if _ca else "Año de referencia"),
        anys_disp, index=0, key="cmp_any_sel",
    )

    df_year = df_europa[df_europa["any"] == any_sel].copy()
    exclude_agg = ["EU27_2020", "EA20", "EA19"]
    df_countries = df_year[~df_year["pais_codi"].isin(exclude_agg)].copy()
    es_data = df_year[df_year["pais_codi"] == "ES"]
    eu_data = df_year[df_year["pais_codi"] == "EU27_2020"]

    # KPIs
    if not es_data.empty:
        col1, col2, col3 = st.columns(3)
        es_pes = es_data.iloc[0]["pes_cnae47"] * 100
        col1.metric(
            f"{'Pes CNAE 47 Espanya' if _ca else 'Peso CNAE 47 España'} ({int(any_sel)})",
            fpct(es_pes, 2, sign=False),
        )
        if not eu_data.empty:
            eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100
            diff = es_pes - eu_pes
            col2.metric(
                "Mitjana UE-27" if _ca else "Media UE-27",
                fpct(eu_pes, 2, sign=False),
                f"{fpct(diff, 2)} vs UE",
            )
        if not df_countries.empty:
            ranking = df_countries.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=False)
            pos_es = list(ranking["pais_codi"]).index("ES") + 1 if "ES" in list(ranking["pais_codi"]) else "—"
            col3.metric(
                "Posició al rànquing" if _ca else "Posición en el ranking",
                f"#{pos_es} de {len(ranking)}",
            )

    # Gràfic horitzontal: pes/PIB per país
    df_sorted = df_year.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=True)
    colors = [RED if c == "ES" else PURPLE if c == "EU27_2020" else GRAY
              for c in df_sorted["pais_codi"]]

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=df_sorted["pais"], x=df_sorted["pes_cnae47"] * 100,
        orientation="h",
        marker_color=colors,
        text=[fpct(v, 2, sign=False) for v in df_sorted["pes_cnae47"] * 100],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig1,
        xaxis_title="% PIB",
        height=max(450, len(df_sorted) * 28),
        margin=dict(l=140, r=80, t=40, b=50),
    )
    st.plotly_chart(fig1, use_container_width=True)
    source("Eurostat, Comptes Nacionals (nama_10_a64)" if _ca
           else "Eurostat, Cuentas Nacionales (nama_10_a64)")

lectura_placeholder()

# ═══════════════════════════════════════════════════════════════
# BLOC 2 — EVOLUCIÓ DEL POSICIONAMENT
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("2. " + ("Evolució del posicionament" if _ca else "Evolución del posicionamiento"))

if not df_europa.empty and "pes_cnae47" in df_europa.columns:
    highlight = ["ES", "DE", "FR", "IT", "PT", "EU27_2020"]
    colors_map = {
        "ES": RED, "DE": BLUE, "FR": GREEN,
        "IT": ORANGE, "PT": "#8E44AD", "EU27_2020": PURPLE,
    }

    fig2 = go.Figure()
    for code in highlight:
        df_c = df_europa[df_europa["pais_codi"] == code].sort_values("any")
        if not df_c.empty:
            fig2.add_trace(go.Scatter(
                x=df_c["any"], y=df_c["pes_cnae47"] * 100,
                mode="lines+markers",
                name=df_c["pais"].iloc[0],
                line=dict(color=colors_map.get(code, "#999"), width=2.5),
                marker=dict(size=5),
            ))

    apply_layout(fig2, yaxis_title="% PIB", height=450)
    st.plotly_chart(fig2, use_container_width=True)
    source("Eurostat, Comptes Nacionals (nama_10_a64)" if _ca
           else "Eurostat, Cuentas Nacionales (nama_10_a64)")

lectura_placeholder()

# ═══════════════════════════════════════════════════════════════
# BLOC 3 — DIMENSIÓ ESTRUCTURAL (Eurostat bd_size)
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("3. " + ("Dimensió estructural" if _ca else "Dimensión estructural"))

if df_total.empty:
    st.info(
        ("Sense dades estructurals (Eurostat bd_size). Executa el processador per generar la cache."
         if _ca else
         "Sin datos estructurales (Eurostat bd_size). Ejecuta el procesador para generar la caché.")
    )
else:
    # Pivot a wide
    df_w = df_total.pivot_table(index=["pais", "pais_codi", "any"],
                                columns="indic_sbs", values="valor").reset_index()
    darrer_any = int(df_w["any"].max())
    df_lst = df_w[df_w["any"] == darrer_any].copy()
    es_row = df_lst[df_lst["pais_codi"] == "ES"]

    # KPIs Espanya darrer any
    if not es_row.empty:
        r = es_row.iloc[0]
        st.caption(
            f"{'Dades Eurostat bd_size, CNAE G47, any' if _ca else 'Datos Eurostat bd_size, CNAE G47, año'} "
            f"**{darrer_any}**. "
            + ("Sèrie disponible 2021-2023 per canvi de marc metodològic UE 2019/2152."
               if _ca else
               "Serie disponible 2021-2023 por cambio de marco metodológico UE 2019/2152.")
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            ("Empreses CNAE 47" if _ca else "Empresas CNAE 47"),
            fnum(r.get("ENT_NR", 0)),
        )
        c2.metric(
            ("Ocupació total" if _ca else "Ocupación total"),
            fnum(r.get("EMP_NR", 0)),
        )
        if r.get("ENT_NR") and r.get("SAL_NR") is not None and r.get("EMP_NR"):
            autonoms = r["EMP_NR"] - r["SAL_NR"]
            pct_auto = (autonoms / r["EMP_NR"]) * 100
            c3.metric(
                ("% no assalariats" if _ca else "% no asalariados"),
                fpct(pct_auto, 1, sign=False),
            )
        c4.metric(
            ("Taxa rotació" if _ca else "Tasa rotación"),
            fpct(r.get("ENT_BRTHR_DTHR_PC", 0), 2, sign=False),
        )

    # ── 3.1 Distribució per mida d'empresa ───────────────────
    st.subheader("3.1 " + ("Distribució per mida d'empresa" if _ca
                           else "Distribución por tamaño de empresa"))

    if not df_mida.empty:
        df_size = df_mida[(df_mida["any"] == darrer_any) & (df_mida["indic_sbs"] == "ENT_NR")].copy()
        if not df_size.empty:
            totals = df_size.groupby("pais_codi")["valor"].sum().to_dict()
            df_size["pct"] = df_size.apply(lambda r: r["valor"] / totals[r["pais_codi"]] * 100, axis=1)

            SIZE_ORDER = ["0", "1-4", "5-9", "GE10"]
            SIZE_LBL_CA = {"0": "Sense assalariats", "1-4": "1-4 assalariats",
                           "5-9": "5-9 assalariats", "GE10": "10 o més"}
            SIZE_LBL_ES = {"0": "Sin asalariados", "1-4": "1-4 asalariados",
                           "5-9": "5-9 asalariados", "GE10": "10 o más"}
            size_lbl = SIZE_LBL_CA if _ca else SIZE_LBL_ES
            SIZE_COLORS = {"0": "#a8c8e8", "1-4": "#5d4fff", "5-9": "#3320d4", "GE10": "#1a0d8e"}

            fig_size = go.Figure()
            for s in SIZE_ORDER:
                d_s = df_size[df_size["sizeclas"] == s]
                d_es = d_s[d_s["pais_codi"] == "ES"]["pct"].sum()
                d_ue = d_s[d_s["pais_codi"] == "EU27_2020"]["pct"].sum()
                fig_size.add_trace(go.Bar(
                    y=["Espanya" if _ca else "España", "UE-27"],
                    x=[d_es, d_ue],
                    name=size_lbl[s],
                    orientation="h",
                    marker_color=SIZE_COLORS[s],
                    text=[fpct(d_es, 1, sign=False), fpct(d_ue, 1, sign=False)],
                    textposition="inside",
                    textfont=dict(color="white", size=11),
                ))
            apply_layout(fig_size,
                barmode="stack",
                xaxis_title="%",
                height=280,
                margin=dict(l=80, r=20, t=30, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
            )
            fig_size.update_xaxes(range=[0, 100])
            st.plotly_chart(fig_size, use_container_width=True)
            source(f"Eurostat <i>bd_size</i> ({darrer_any})")
    lectura_placeholder()

    # ── 3.2 Naixement vs defunció per 8 països ───────────────
    st.subheader("3.2 " + ("Naixement vs defunció (8 països)" if _ca
                           else "Nacimiento vs defunción (8 países)"))

    if not df_lst.empty:
        PAIS_ORDER = ["EU27_2020", "ES", "DE", "FR", "IT", "PT", "NL", "PL"]
        df_disp = df_lst.set_index("pais_codi").reindex(PAIS_ORDER).reset_index()

        fig_br = go.Figure()
        fig_br.add_trace(go.Bar(
            x=df_disp["pais"], y=df_disp.get("ENT_BRTHR_PC", pd.Series()),
            name=("Taxa naixement" if _ca else "Tasa nacimiento"),
            marker_color=GREEN,
            text=[fpct(v, 1, sign=False) for v in df_disp.get("ENT_BRTHR_PC", pd.Series())],
            textposition="outside",
        ))
        fig_br.add_trace(go.Bar(
            x=df_disp["pais"], y=df_disp.get("ENT_DTHR_PC", pd.Series()),
            name=("Taxa defunció" if _ca else "Tasa defunción"),
            marker_color=RED,
            text=[fpct(v, 1, sign=False) for v in df_disp.get("ENT_DTHR_PC", pd.Series())],
            textposition="outside",
        ))
        apply_layout(fig_br,
            barmode="group",
            yaxis_title="%",
            height=400,
            margin=dict(l=50, r=20, t=30, b=80),
        )
        st.plotly_chart(fig_br, use_container_width=True)
        source(f"Eurostat <i>bd_size</i> ({darrer_any})")
    lectura_placeholder()

    # ── 3.3 Mida mitjana (ocupats/empresa) per país ──────────
    st.subheader("3.3 " + ("Mida mitjana d'empresa (ocupats per empresa)" if _ca
                           else "Tamaño medio de empresa (ocupados por empresa)"))

    if not df_lst.empty and "ENT_NR" in df_lst.columns and "EMP_NR" in df_lst.columns:
        df_lst2 = df_lst.copy()
        df_lst2["mida_mitjana"] = df_lst2["EMP_NR"] / df_lst2["ENT_NR"]
        PAIS_ORDER = ["EU27_2020", "ES", "DE", "FR", "IT", "PT", "NL", "PL"]
        df_mm = df_lst2.set_index("pais_codi").reindex(PAIS_ORDER).reset_index()
        df_mm = df_mm.dropna(subset=["mida_mitjana"]).sort_values("mida_mitjana", ascending=True)

        colors_mm = []
        for code in df_mm["pais_codi"]:
            if code == "ES":
                colors_mm.append(PURPLE)
            elif code == "EU27_2020":
                colors_mm.append(RED)
            else:
                colors_mm.append(PURPLE_LIGHT)

        fig_mm = go.Figure()
        fig_mm.add_trace(go.Bar(
            y=df_mm["pais"], x=df_mm["mida_mitjana"],
            orientation="h",
            marker_color=colors_mm,
            text=[f"{v:.1f}" for v in df_mm["mida_mitjana"]],
            textposition="outside",
        ))
        apply_layout(fig_mm,
            xaxis_title=("Ocupats / empresa" if _ca else "Ocupados / empresa"),
            height=350,
            margin=dict(l=130, r=80, t=30, b=50),
        )
        st.plotly_chart(fig_mm, use_container_width=True)
        source(f"Eurostat <i>bd_size</i> ({darrer_any})")
    lectura_placeholder()

    # ── 3.4 Supervivència Y1 / Y2 ES vs UE-27 ────────────────
    st.subheader("3.4 " + ("Supervivència empresarial Y1 / Y2" if _ca
                           else "Supervivencia empresarial Y1 / Y2"))

    if not df_surv.empty:
        AGE_LBL_CA = {"Y1": "1 any després del naixement", "Y2": "2 anys després del naixement"}
        AGE_LBL_ES = {"Y1": "1 año después del nacimiento", "Y2": "2 años después del nacimiento"}
        age_lbl = AGE_LBL_CA if _ca else AGE_LBL_ES

        surv_max_any = df_surv["any"].max()
        df_s_lst = df_surv[df_surv["any"] == surv_max_any].copy()
        if df_s_lst.empty:
            df_s_lst = df_surv.sort_values("any").groupby(["pais_codi", "age"]).tail(1)

        if not df_s_lst.empty:
            fig_s = go.Figure()
            for age in ["Y1", "Y2"]:
                d_age = df_s_lst[df_s_lst["age"] == age].sort_values("pais_codi")
                if d_age.empty:
                    continue
                fig_s.add_trace(go.Bar(
                    x=[d_age[d_age["pais_codi"] == "EU27_2020"]["survival_pc"].sum(),
                       d_age[d_age["pais_codi"] == "ES"]["survival_pc"].sum()],
                    y=["UE-27", "Espanya" if _ca else "España"],
                    name=age_lbl[age],
                    orientation="h",
                    marker_color=PURPLE if age == "Y1" else PURPLE_LIGHT,
                    text=[fpct(d_age[d_age["pais_codi"] == "EU27_2020"]["survival_pc"].sum(), 1, sign=False),
                          fpct(d_age[d_age["pais_codi"] == "ES"]["survival_pc"].sum(), 1, sign=False)],
                    textposition="outside",
                ))
            apply_layout(fig_s,
                barmode="group",
                xaxis_title="%",
                height=320,
                margin=dict(l=80, r=80, t=30, b=50),
            )
            st.plotly_chart(fig_s, use_container_width=True)
            source(f"Eurostat <i>bd_size</i> (cohort {int(surv_max_any)})")
    lectura_placeholder()

# ═══════════════════════════════════════════════════════════════
# BLOC 4 — POLS MENSUAL EUROPEU
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("4. " + ("Pols mensual del comerç a Europa" if _ca
                   else "Pulso mensual del comercio en Europa"))

if df_mens.empty:
    st.info(
        ("Sense dades mensuals (Eurostat sts_trtu_m)."
         if _ca else
         "Sin datos mensuales (Eurostat sts_trtu_m).")
    )
else:
    df_mens["periode"] = df_mens["periode"].astype(str)
    darrer = df_mens["periode"].max()
    df_last = df_mens[df_mens["periode"] == darrer]
    es_row = df_last[df_last["pais_codi"] == "ES"]
    ea_row = df_last[df_last["pais_codi"] == "EA20"]
    eu_row = df_last[df_last["pais_codi"] == "EU27_2020"]

    help_anual = (
        f"Variació del volum de vendes minoristes respecte al mateix mes de l'any anterior. Dada de {darrer}."
        if _ca else
        f"Variación del volumen de ventas minoristas respecto al mismo mes del año anterior. Dato de {darrer}."
    )

    c1, c2, c3, c4 = st.columns(4)
    if not es_row.empty:
        es_yoy = es_row.iloc[0].get("yoy")
        c1.metric(
            ("Espanya — vs. fa un any" if _ca else "España — vs. hace un año"),
            fpct(es_yoy, 1) if pd.notna(es_yoy) else "—",
            help=help_anual,
        )
    if not ea_row.empty:
        ea_yoy = ea_row.iloc[0].get("yoy")
        c2.metric(
            ("Eurozona — vs. fa un any" if _ca else "Eurozona — vs. hace un año"),
            fpct(ea_yoy, 1) if pd.notna(ea_yoy) else "—",
            help=help_anual,
        )
    if not eu_row.empty:
        eu_yoy = eu_row.iloc[0].get("yoy")
        c3.metric(
            ("UE-27 — vs. fa un any" if _ca else "UE-27 — vs. hace un año"),
            fpct(eu_yoy, 1) if pd.notna(eu_yoy) else "—",
            help=help_anual,
        )
    if not es_row.empty:
        es_idx = es_row.iloc[0]["index_volum"]
        c4.metric(
            (f"Índex Espanya ({darrer})" if _ca else f"Índice España ({darrer})"),
            fnum(es_idx, 1),
            help=("Volum de vendes amb base 2021=100, ajustat estacional."
                  if _ca else
                  "Volumen de ventas con base 2021=100, ajustado estacional."),
        )

    st.write("")

    # Controls del gràfic
    cc1, cc2 = st.columns([1, 2])
    finestres = {
        "24": ("Darrers 2 anys", "Últimos 2 años"),
        "60": ("Darrers 5 anys", "Últimos 5 años"),
        "120": ("Darrers 10 anys", "Últimos 10 años"),
        "all": ("Tota la sèrie", "Toda la serie"),
    }
    with cc1:
        finestra = st.selectbox(
            ("Període" if _ca else "Período"),
            options=list(finestres.keys()),
            index=1,
            format_func=lambda k: finestres[k][0 if _ca else 1],
            key="cmp_eu_finestra",
        )

    paisos_opcionals = ["DE", "FR", "IT", "PT", "NL", "BE"]
    pais_lbl = {
        "DE": "Alemanya" if _ca else "Alemania",
        "FR": "França" if _ca else "Francia",
        "IT": "Itàlia" if _ca else "Italia",
        "PT": "Portugal",
        "NL": "Països Baixos" if _ca else "Países Bajos",
        "BE": "Bèlgica" if _ca else "Bélgica",
    }
    with cc2:
        extra_sel = st.multiselect(
            ("Comparar amb altres països (opcional)" if _ca
             else "Comparar con otros países (opcional)"),
            options=paisos_opcionals,
            default=[],
            format_func=lambda c: pais_lbl.get(c, c),
            key="cmp_eu_paisos",
        )

    df_plot = df_mens.copy()
    df_plot["dt"] = pd.to_datetime(df_plot["periode"], format="%Y-%m", errors="coerce")
    if finestra != "all":
        cutoff = df_plot["dt"].max() - pd.DateOffset(months=int(finestra))
        df_plot = df_plot[df_plot["dt"] >= cutoff]

    color_m = {
        "ES": RED, "EA20": "#34495e", "EU27_2020": "#7f8c8d",
        "DE": BLUE, "FR": GREEN, "IT": ORANGE,
        "PT": "#8E44AD", "NL": "#16a085", "BE": "#95a5a6",
    }
    paisos_visibles = ["EA20", "EU27_2020"] + extra_sel + ["ES"]

    fig_m = go.Figure()
    for code in paisos_visibles:
        sub = df_plot[df_plot["pais_codi"] == code].sort_values("dt")
        if sub.empty:
            continue
        es_destacat = (code == "ES")
        fig_m.add_trace(go.Scatter(
            x=sub["dt"], y=sub["index_volum"],
            mode="lines", name=sub["pais"].iloc[0],
            line=dict(
                color=color_m.get(code, "#999"),
                width=3.4 if es_destacat else 2.0,
            ),
        ))
    fig_m.add_hline(y=100, line=dict(color="#bbb", width=1, dash="dot"),
                    annotation_text="Base 2021=100",
                    annotation_position="bottom right",
                    annotation_font_size=10)
    apply_layout(fig_m,
        yaxis_title=("Índex (2021=100)" if _ca else "Índice (2021=100)"),
        height=420,
    )
    st.plotly_chart(fig_m, use_container_width=True)
    source(
        f"Eurostat sts_trtu_m. Volum de vendes G47, ajustat estacional. Darrera dada: {darrer}."
        if _ca else
        f"Eurostat sts_trtu_m. Volumen de ventas G47, ajustado estacional. Último dato: {darrer}."
    )

lectura_placeholder()

# ─── Descàrrega + nota metodològica al peu ─────────────────────

st.markdown("---")
with st.expander(
    ("Descarregar dades brutes (CSV)" if _ca else "Descargar datos brutos (CSV)"),
    expanded=False,
):
    if not df_europa.empty:
        st.download_button(
            "europa_vab.csv",
            df_europa.to_csv(index=False).encode("utf-8"),
            "europa_vab.csv", "text/csv",
            key="dl_europa_vab",
        )
    if not df_mens.empty:
        st.download_button(
            "europa_retail_mensual.csv",
            df_mens.to_csv(index=False).encode("utf-8"),
            "europa_retail_mensual.csv", "text/csv",
            key="dl_europa_mens",
        )
    if not df_total.empty:
        st.download_button(
            "estructura_retail.csv",
            df_total.to_csv(index=False).encode("utf-8"),
            "estructura_retail.csv", "text/csv",
            key="dl_estructura",
        )

with st.expander(
    ("Nota metodològica" if _ca else "Nota metodológica"),
    expanded=False,
):
    if _ca:
        st.markdown(
            "**Fonts utilitzades:**\n"
            "- *Pes CNAE 47 / PIB i evolució*: Eurostat `nama_10_a64` (VAB del CNAE G47 i del total) per a tots els països UE + agregats UE-27 / EA-20.\n"
            "- *Dimensió estructural*: Eurostat `bd_size` (Business Demography by size class and NACE). Cobertura **2021-2023** pel nou marc estadístic UE 2019/2152. La sèrie històrica `bd_9bd_sz_cl_r2` (2008-2020) no s'integra aquí per evitar comparacions metodològicament discutibles.\n"
            "- *Pols mensual*: Eurostat `sts_trtu_m` (Volum de vendes, índex 2021=100, ajustat estacional). Publicació mensual amb retard ~45 dies.\n\n"
            "**CNAE G47 estricte** (sense barreja amb G45 vehicles ni majorista G46). "
            "Comparativa harmonitzada entre estats membres."
        )
    else:
        st.markdown(
            "**Fuentes utilizadas:**\n"
            "- *Peso CNAE 47 / PIB y evolución*: Eurostat `nama_10_a64` (VAB del CNAE G47 y del total) para todos los países UE + agregados UE-27 / EA-20.\n"
            "- *Dimensión estructural*: Eurostat `bd_size` (Business Demography by size class and NACE). Cobertura **2021-2023** por el nuevo marco estadístico UE 2019/2152. La serie histórica `bd_9bd_sz_cl_r2` (2008-2020) no se integra aquí para evitar comparaciones metodológicamente cuestionables.\n"
            "- *Pulso mensual*: Eurostat `sts_trtu_m` (Volumen de ventas, índice 2021=100, ajustado estacional). Publicación mensual con retraso ~45 días.\n\n"
            "**CNAE G47 estricto** (sin mezcla con G45 vehículos ni mayorista G46). "
            "Comparativa armonizada entre estados miembros."
        )

page_meta(
    ("Eurostat (nama_10_a64, sts_trtu_m, bd_size)" if _ca
     else "Eurostat (nama_10_a64, sts_trtu_m, bd_size)"),
    st.session_state.lang,
)

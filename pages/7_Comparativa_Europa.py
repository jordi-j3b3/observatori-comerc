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
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout, highlight_expander,
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

# ─── Helpers de presentació LECTURA ────────────────────────────

def firma_lectura():
    """Signatura corporativa discreta sota cada insight() de lectura real."""
    st.markdown(
        '<div style="text-align:right; color:#888; font-size:11px; '
        'font-style:italic; font-family:\'Inter\',sans-serif; '
        'margin-top:-8px; margin-bottom:24px;">'
        'Observatorio del Comercio · J3B3 Consulting'
        '</div>',
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

    # ─── Lectura: posicionament ES vs UE-27 ─────────────────
    # Nota: la part de tendència temporal (variació pes des de l'any inicial)
    # s'ha tret aquí — pertany conceptualment al Bloc 2 (Evolució del
    # posicionament), que de moment manté placeholder fins que Jordi redacti
    # lectura pròpia.
    if not es_data.empty and not eu_data.empty:
        _es_pes = es_data.iloc[0]["pes_cnae47"] * 100
        _eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100
        if _ca:
            _txt = (
                f"Espanya destina un <strong>{fpct(_es_pes, 2, sign=False)}</strong> "
                f"del seu PIB al comerç al detall, "
            )
            if _es_pes > _eu_pes:
                _txt += (
                    f"<strong>{fpct(_es_pes - _eu_pes, 2)} per sobre</strong> "
                    f"de la mitjana europea ({fpct(_eu_pes, 2, sign=False)}). "
                    "Això pot reflectir una estructura econòmica amb més pes del "
                    "consum final i una menor industrialització relativa comparada "
                    "amb països com Alemanya. El pes superior també s'explica per "
                    "la importància del turisme, que impulsa el consum al detall "
                    "especialment en zones costaneres i urbanes."
                )
            else:
                _txt += (
                    f"<strong>{fpct(_eu_pes - _es_pes, 2)} per sota</strong> "
                    f"de la mitjana europea ({fpct(_eu_pes, 2, sign=False)})."
                )
        else:
            _txt = (
                f"España destina un <strong>{fpct(_es_pes, 2, sign=False)}</strong> "
                f"de su PIB al comercio minorista, "
            )
            if _es_pes > _eu_pes:
                _txt += (
                    f"<strong>{fpct(_es_pes - _eu_pes, 2)} por encima</strong> "
                    f"de la media europea ({fpct(_eu_pes, 2, sign=False)}). "
                    "Esto puede reflejar una estructura económica con más peso "
                    "del consumo final y una menor industrialización relativa "
                    "comparada con países como Alemania. El peso superior también "
                    "se explica por la importancia del turismo, que impulsa el "
                    "consumo minorista especialmente en zonas costeras y urbanas."
                )
            else:
                _txt += (
                    f"<strong>{fpct(_eu_pes - _es_pes, 2)} por debajo</strong> "
                    f"de la media europea ({fpct(_eu_pes, 2, sign=False)})."
                )
        insight(_txt)
        firma_lectura()

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

            # ─── Lectura: atomització ES vs UE-27 ───────────
            pct_auto_es = df_size[(df_size["sizeclas"] == "0") &
                                  (df_size["pais_codi"] == "ES")]["pct"].sum()
            pct_auto_ue = df_size[(df_size["sizeclas"] == "0") &
                                  (df_size["pais_codi"] == "EU27_2020")]["pct"].sum()
            pct_ge10_es = df_size[(df_size["sizeclas"] == "GE10") &
                                  (df_size["pais_codi"] == "ES")]["pct"].sum()
            pct_ge10_ue = df_size[(df_size["sizeclas"] == "GE10") &
                                  (df_size["pais_codi"] == "EU27_2020")]["pct"].sum()
            es_mes_atom = pct_auto_es > pct_auto_ue
            if _ca:
                etiqueta = ("més atomitzat" if es_mes_atom else "menys atomitzat")
                implicacio = (
                    "Aquesta major atomització afecta la productivitat, la capacitat "
                    "d'inversió i l'eficiència negociadora amb proveïdors."
                    if es_mes_atom else
                    "Aquesta major concentració empresarial relativa pot afavorir "
                    "economies d'escala i poder negociador, però redueix la densitat "
                    "de comerç de proximitat respecte la mitjana europea."
                )
                _txt = (
                    f"El comerç al detall espanyol és <strong>{etiqueta}</strong> "
                    f"que la mitjana europea: un {fpct(pct_auto_es, 1, sign=False)} "
                    f"d'empreses sense assalariats a Espanya vs un "
                    f"{fpct(pct_auto_ue, 1, sign=False)} a la UE-27. "
                    f"Al tram alt, les empreses amb 10 o més assalariats "
                    f"representen el {fpct(pct_ge10_es, 1, sign=False)} a Espanya vs el "
                    f"{fpct(pct_ge10_ue, 1, sign=False)} europeu. {implicacio}"
                )
            else:
                etiqueta = ("más atomizado" if es_mes_atom else "menos atomizado")
                implicacio = (
                    "Esta mayor atomización afecta la productividad, la capacidad "
                    "de inversión y la eficiencia negociadora con proveedores."
                    if es_mes_atom else
                    "Esta mayor concentración empresarial relativa puede favorecer "
                    "economías de escala y poder negociador, pero reduce la densidad "
                    "de comercio de proximidad respecto a la media europea."
                )
                _txt = (
                    f"El comercio minorista español es <strong>{etiqueta}</strong> "
                    f"que la media europea: un {fpct(pct_auto_es, 1, sign=False)} "
                    f"de empresas sin asalariados en España vs un "
                    f"{fpct(pct_auto_ue, 1, sign=False)} en la UE-27. "
                    f"En el tramo alto, las empresas con 10 o más asalariados "
                    f"representan el {fpct(pct_ge10_es, 1, sign=False)} en España vs el "
                    f"{fpct(pct_ge10_ue, 1, sign=False)} europeo. {implicacio}"
                )
            insight(_txt)
            firma_lectura()

    # ── 3.2-3.4 Sub-blocs secundaris de dimensió estructural ──
    _lbl_estr_exp = ("Veure més anàlisi estructural (naixement, mida, supervivència)"
                     if _ca else
                     "Ver más análisis estructural (nacimiento, tamaño, supervivencia)")
    with highlight_expander(_lbl_estr_exp, expanded=False):
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

            # ─── Lectura: rotació ES vs UE-27 ───────────────────
            _es_brth = (df_disp[df_disp["pais_codi"] == "ES"]["ENT_BRTHR_PC"].iloc[0]
                        if "ENT_BRTHR_PC" in df_disp.columns else None)
            _es_dth = (df_disp[df_disp["pais_codi"] == "ES"]["ENT_DTHR_PC"].iloc[0]
                       if "ENT_DTHR_PC" in df_disp.columns else None)
            _ue_brth = (df_disp[df_disp["pais_codi"] == "EU27_2020"]["ENT_BRTHR_PC"].iloc[0]
                        if "ENT_BRTHR_PC" in df_disp.columns else None)
            _ue_dth = (df_disp[df_disp["pais_codi"] == "EU27_2020"]["ENT_DTHR_PC"].iloc[0]
                       if "ENT_DTHR_PC" in df_disp.columns else None)
            if _es_brth is not None and _es_dth is not None:
                _es_net = _es_brth - _es_dth
                if _ca:
                    _txt = (
                        f"A Espanya, la taxa de naixement empresarial al CNAE 47 "
                        f"({fpct(_es_brth, 1, sign=False)}) queda <strong>per sota</strong> "
                        f"de la taxa de defunció ({fpct(_es_dth, 1, sign=False)}), amb un "
                        f"saldo net negatiu de {fpct(_es_net, 1)} punts. "
                    )
                    if _ue_brth is not None and _ue_dth is not None:
                        _ue_net = _ue_brth - _ue_dth
                        _txt += (
                            f"A la UE-27, el saldo net és {fpct(_ue_net, 1)} punts "
                            f"(naixement {fpct(_ue_brth, 1, sign=False)} vs defunció "
                            f"{fpct(_ue_dth, 1, sign=False)}). "
                        )
                    _txt += (
                        "Una taxa de defunció superior a la de naixement de manera "
                        "sostinguda apunta cap a <strong>consolidació sectorial</strong>: "
                        "el sector està perdent empreses netament."
                    )
                else:
                    _txt = (
                        f"En España, la tasa de nacimiento empresarial del CNAE 47 "
                        f"({fpct(_es_brth, 1, sign=False)}) queda <strong>por debajo</strong> "
                        f"de la tasa de defunción ({fpct(_es_dth, 1, sign=False)}), con un "
                        f"saldo neto negativo de {fpct(_es_net, 1)} puntos. "
                    )
                    if _ue_brth is not None and _ue_dth is not None:
                        _ue_net = _ue_brth - _ue_dth
                        _txt += (
                            f"En la UE-27, el saldo neto es {fpct(_ue_net, 1)} puntos "
                            f"(nacimiento {fpct(_ue_brth, 1, sign=False)} vs defunción "
                            f"{fpct(_ue_dth, 1, sign=False)}). "
                        )
                    _txt += (
                        "Una tasa de defunción superior a la de nacimiento de manera "
                        "sostenida apunta a <strong>consolidación sectorial</strong>: "
                        "el sector está perdiendo empresas netamente."
                    )
                insight(_txt)
                firma_lectura()

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

            # ─── Lectura: mida mitjana ES vs UE-27 ──────────────
            _es_mm = df_mm[df_mm["pais_codi"] == "ES"]["mida_mitjana"]
            _ue_mm = df_mm[df_mm["pais_codi"] == "EU27_2020"]["mida_mitjana"]
            if not _es_mm.empty and not _ue_mm.empty:
                _es_v = _es_mm.iloc[0]
                _ue_v = _ue_mm.iloc[0]
                _diff_pct = (_es_v / _ue_v - 1) * 100
                if _ca:
                    _txt = (
                        f"Cada empresa retail espanyola dóna feina de mitjana a "
                        f"<strong>{fnum(_es_v, 1)} persones</strong>, davant les "
                        f"{fnum(_ue_v, 1)} de la mitjana UE-27 "
                        f"({fpct(_diff_pct, 1)} respecte a la UE). "
                        "Aquesta mètrica és un indicador agregat de la concentració "
                        "empresarial: valors més alts indiquen una estructura dominada "
                        "per grans cadenes."
                    )
                else:
                    _txt = (
                        f"Cada empresa retail española da trabajo en promedio a "
                        f"<strong>{fnum(_es_v, 1)} personas</strong>, frente a las "
                        f"{fnum(_ue_v, 1)} de la media UE-27 "
                        f"({fpct(_diff_pct, 1)} respecto a la UE). "
                        "Esta métrica es un indicador agregado de la concentración "
                        "empresarial: valores más altos indican una estructura dominada "
                        "por grandes cadenas."
                    )
                insight(_txt)
                firma_lectura()

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

                # ─── Lectura: supervivència Y1 ES vs UE-27 ──────
                _y1_es = df_s_lst[(df_s_lst["age"] == "Y1") &
                                  (df_s_lst["pais_codi"] == "ES")]["survival_pc"]
                _y1_ue = df_s_lst[(df_s_lst["age"] == "Y1") &
                                  (df_s_lst["pais_codi"] == "EU27_2020")]["survival_pc"]
                if not _y1_es.empty and not _y1_ue.empty:
                    _es_y1 = _y1_es.iloc[0]
                    _ue_y1 = _y1_ue.iloc[0]
                    _diff = _ue_y1 - _es_y1
                    _es_menys = _diff > 0
                    if _ca:
                        lectura = (
                            "Una taxa de supervivència més baixa pot reflectir un entorn "
                            "competitiu més dur, barreres d'entrada més baixes (més "
                            "empreses fràgils que ho proven) o suport menor al primer any."
                            if _es_menys else
                            "Una taxa de supervivència més alta indica un entorn d'entrada "
                            "més selectiu, projectes empresarials més robustos i, potser, "
                            "més suport institucional al primer any d'activitat."
                        )
                        _txt = (
                            f"De cada 100 noves empreses retail creades a Espanya, "
                            f"<strong>{fpct(_es_y1, 1, sign=False)} sobreviuen al primer "
                            f"any</strong>, davant les {fpct(_ue_y1, 1, sign=False)} de la "
                            f"mitjana UE-27 (diferencial de {fpct(_diff, 1)} punts). {lectura}"
                        )
                    else:
                        lectura = (
                            "Una tasa de supervivencia más baja puede reflejar un entorno "
                            "competitivo más duro, barreras de entrada más bajas (más "
                            "empresas frágiles que lo intentan) o menor apoyo al primer año."
                            if _es_menys else
                            "Una tasa de supervivencia más alta indica un entorno de entrada "
                            "más selectivo, proyectos empresariales más robustos y, "
                            "posiblemente, mayor apoyo institucional en el primer año."
                        )
                        _txt = (
                            f"De cada 100 nuevas empresas retail creadas en España, "
                            f"<strong>{fpct(_es_y1, 1, sign=False)} sobreviven al primer "
                            f"año</strong>, frente a las {fpct(_ue_y1, 1, sign=False)} de "
                            f"la media UE-27 (diferencial de {fpct(_diff, 1)} puntos). {lectura}"
                        )
                    insight(_txt)
                    firma_lectura()

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

    # ─── Lectura: cicle de consum ES vs Eurozona ────────────
    if not es_row.empty and not ea_row.empty:
        _es_yoy = es_row.iloc[0].get("yoy")
        _ea_yoy = ea_row.iloc[0].get("yoy")
        if pd.notna(_es_yoy) and pd.notna(_ea_yoy):
            _spread = _es_yoy - _ea_yoy
            _es_hist = (df_mens[df_mens["pais_codi"] == "ES"]
                        .sort_values("periode")
                        .tail(6))
            _avg_6m = _es_hist["yoy"].dropna().mean()
            _trend = _es_hist["yoy"].dropna().tolist()
            _accel = (_trend[-1] - _trend[0]) if len(_trend) >= 2 else 0

            if _ca:
                _verb = "creixen" if _es_yoy >= 0 else "cauen"
                _txt = (
                    f"Al <strong>{darrer}</strong>, les vendes minoristes a Espanya "
                    f"<strong>{_verb} un {abs(_es_yoy):.1f} %</strong> respecte al "
                    f"mateix mes de l'any anterior. "
                )
                if _spread >= 0.5:
                    _txt += (
                        f"Espanya supera la mitjana de l'eurozona ({_ea_yoy:+.1f} %) "
                        f"en <strong>{_spread:+.1f} punts</strong>, senyal d'un cicle "
                        "de consum més dinàmic. "
                    )
                elif _spread <= -0.5:
                    _txt += (
                        f"Espanya queda <strong>{abs(_spread):.1f} punts</strong> per "
                        f"sota de l'eurozona ({_ea_yoy:+.1f} %). "
                    )
                else:
                    _txt += (
                        f"En línia amb la mitjana de l'eurozona ({_ea_yoy:+.1f} %). "
                    )
                _txt += (
                    f"En els darrers 6 mesos, la variació interanual mitjana s'ha "
                    f"situat al <strong>{_avg_6m:+.1f} %</strong>"
                )
                if _accel > 0.5:
                    _txt += " amb tendència accelerant."
                elif _accel < -0.5:
                    _txt += " amb tendència desaccelerant."
                else:
                    _txt += " sense canvis de ritme significatius."
            else:
                _verb = "crecen" if _es_yoy >= 0 else "caen"
                _txt = (
                    f"En <strong>{darrer}</strong>, las ventas minoristas en España "
                    f"<strong>{_verb} un {abs(_es_yoy):.1f} %</strong> respecto al "
                    f"mismo mes del año anterior. "
                )
                if _spread >= 0.5:
                    _txt += (
                        f"España supera la media de la eurozona ({_ea_yoy:+.1f} %) "
                        f"en <strong>{_spread:+.1f} puntos</strong>, señal de un "
                        "ciclo de consumo más dinámico. "
                    )
                elif _spread <= -0.5:
                    _txt += (
                        f"España queda <strong>{abs(_spread):.1f} puntos</strong> por "
                        f"debajo de la eurozona ({_ea_yoy:+.1f} %). "
                    )
                else:
                    _txt += (
                        f"En línea con la media de la eurozona ({_ea_yoy:+.1f} %). "
                    )
                _txt += (
                    f"En los últimos 6 meses, la variación interanual media se ha "
                    f"situado en el <strong>{_avg_6m:+.1f} %</strong>"
                )
                if _accel > 0.5:
                    _txt += " con tendencia acelerándose."
                elif _accel < -0.5:
                    _txt += " con tendencia desacelerándose."
                else:
                    _txt += " sin cambios de ritmo significativos."
            insight(_txt)
            firma_lectura()

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

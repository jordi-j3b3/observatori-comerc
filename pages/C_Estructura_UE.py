"""Pàgina C: Estructura del retail espanyol en context UE.

Font única: Eurostat Business Demography (bd_size), CNAE G47 estricte.
Cobertura temporal: 2021-2023 (nou marc metodològic Reglament UE 2019/2152).
Sèrie històrica 2008-2020 disponible al dataset bd_9bd_sz_cl_r2 (no comparable directament).
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout, highlight_expander,
                   PURPLE, PURPLE_LIGHT, RED, GREEN, PALETTE)

inject_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"

st.title("Estructura del retail en context UE" if _ca else "Estructura del retail en contexto UE")

if _ca:
    intro(
        "Aquesta pàgina utilitza la <strong>Demografia Empresarial d'Eurostat</strong> "
        "(<i>bd_size</i>) per situar l'estructura del comerç al detall espanyol davant la <strong>UE-27</strong> "
        "i les principals economies del comerç al detall europeu. "
        "Es tracta de l'única font censal pública que cobreix el <strong>CNAE G47 estricte</strong> "
        "amb metodologia harmonitzada entre estats membres. "
        "Coberta 2021-2023 (nou marc metodològic UE 2019/2152). "
        "Permet contestar preguntes que les fonts INE soles no responen: "
        "el retail espanyol té més o menys rotació empresarial que la mitjana europea? "
        "Quina és la supervivència de les noves empreses comparada amb la UE? "
        "Quin és el pes dels autònoms (empreses sense assalariats) vs altres països?"
    )
else:
    intro(
        "Esta página utiliza la <strong>Demografía Empresarial de Eurostat</strong> "
        "(<i>bd_size</i>) para situar la estructura del comercio minorista español frente a la <strong>UE-27</strong> "
        "y las principales economías del comercio minorista europeo. "
        "Es la única fuente censal pública que cubre el <strong>CNAE G47 estricto</strong> "
        "con metodología armonizada entre estados miembros. "
        "Cobertura 2021-2023 (nuevo marco metodológico UE 2019/2152). "
        "Permite responder preguntas que las fuentes INE solas no responden: "
        "¿el retail español tiene más o menos rotación empresarial que la media europea? "
        "¿Cuál es la supervivencia de las nuevas empresas comparada con la UE? "
        "¿Cuál es el peso de los autónomos (empresas sin asalariados) vs otros países?"
    )

# ─── Carrega dades ──────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_total():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "estructura_retail.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_mida():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "estructura_retail_mida.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_supervivencia():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "estructura_retail_supervivencia.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

df_total = load_total()
df_mida = load_mida()
df_surv = load_supervivencia()

if df_total.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

# Pivotar a wide per facilitar mètriques
df_w = df_total.pivot_table(index=["pais", "pais_codi", "any"],
                            columns="indic_sbs", values="valor").reset_index()

darrer_any = int(df_w["any"].max())
df_lst = df_w[df_w["any"] == darrer_any].copy()
es_row = df_lst[df_lst["pais_codi"] == "ES"]
ue_row = df_lst[df_lst["pais_codi"] == "EU27_2020"]

# ─── TABS ────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    ("Espanya" if _ca else "España"),
    ("Comparativa UE" if _ca else "Comparativa UE"),
    ("Supervivència" if _ca else "Supervivencia"),
])

# ============================================================
# TAB 1: ESPANYA
# ============================================================
with tab1:
    # ─── KPIs Espanya darrer any ────────────────────────────────

    st.subheader(f"{'Espanya' if _ca else 'España'} — {darrer_any}")

    if not es_row.empty:
        r = es_row.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Empreses CNAE 47" if _ca else "Empresas CNAE 47",
            fnum(r.get("ENT_NR", 0)),
        )
        c2.metric(
            "Ocupació total" if _ca else "Ocupación total",
            fnum(r.get("EMP_NR", 0)),
        )
        if r.get("ENT_NR") and r.get("SAL_NR") is not None and r.get("EMP_NR"):
            autonoms = r["EMP_NR"] - r["SAL_NR"]
            pct_auto = (autonoms / r["EMP_NR"]) * 100
            c3.metric(
                "% no assalariats" if _ca else "% no asalariados",
                fpct(pct_auto, 1, sign=False),
            )
        c4.metric(
            "Taxa rotació" if _ca else "Tasa rotación",
            fpct(r.get("ENT_BRTHR_DTHR_PC", 0), 2, sign=False),
        )

    # ─── Distribució per mida d'empresa ─────────────────────────

    st.subheader("Distribució per mida d'empresa" if _ca else "Distribución por tamaño de empresa")

    if not df_mida.empty:
        df_size = df_mida[(df_mida["any"] == darrer_any) & (df_mida["indic_sbs"] == "ENT_NR")].copy()
        if not df_size.empty:
            # Calcular % per país
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
            source(f"Eurostat <i>bd_size</i> ({darrer_any}). Càlcul propi" if _ca
                   else f"Eurostat <i>bd_size</i> ({darrer_any}). Cálculo propio")

            # Insight distribució
            pct_auto_es = df_size[(df_size["sizeclas"] == "0") & (df_size["pais_codi"] == "ES")]["pct"].sum()
            pct_auto_ue = df_size[(df_size["sizeclas"] == "0") & (df_size["pais_codi"] == "EU27_2020")]["pct"].sum()
            pct_ge10_es = df_size[(df_size["sizeclas"] == "GE10") & (df_size["pais_codi"] == "ES")]["pct"].sum()
            pct_ge10_ue = df_size[(df_size["sizeclas"] == "GE10") & (df_size["pais_codi"] == "EU27_2020")]["pct"].sum()

            # Determinar dinàmicament si Espanya està més o menys atomitzada
            es_mes_atom = pct_auto_es > pct_auto_ue
            if _ca:
                etiqueta = ("més atomitzat" if es_mes_atom else "menys atomitzat")
                preposicio_comparat = ("a Espanya vs" if es_mes_atom else "a Espanya vs")
                implicacio = (
                    "Aquesta major atomització afecta la productivitat, la capacitat "
                    "d'inversió i l'eficiència negociadora amb proveïdors."
                    if es_mes_atom else
                    "Aquesta major concentració empresarial relativa pot afavorir "
                    "economies d'escala i poder negociador, però redueix la densitat "
                    "de comerç de proximitat respecte la mitjana europea."
                )
                txt = (
                    f"El comerç al detall espanyol és <strong>{etiqueta}</strong> que la mitjana europea: "
                    f"un {fpct(pct_auto_es, 1, sign=False)} d'empreses sense assalariats {preposicio_comparat} "
                    f"un {fpct(pct_auto_ue, 1, sign=False)} a la UE-27. "
                    f"Al tram alt, les empreses amb 10 o més assalariats representen el "
                    f"{fpct(pct_ge10_es, 1, sign=False)} a Espanya vs el {fpct(pct_ge10_ue, 1, sign=False)} europeu. "
                    f"{implicacio}"
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
                txt = (
                    f"El comercio minorista español es <strong>{etiqueta}</strong> que la media europea: "
                    f"un {fpct(pct_auto_es, 1, sign=False)} de empresas sin asalariados en España vs "
                    f"un {fpct(pct_auto_ue, 1, sign=False)} en la UE-27. "
                    f"En el tramo alto, las empresas con 10 o más asalariados representan el "
                    f"{fpct(pct_ge10_es, 1, sign=False)} en España vs el {fpct(pct_ge10_ue, 1, sign=False)} europeo. "
                    f"{implicacio}"
                )
            insight(txt)

# ============================================================
# TAB 2: COMPARATIVA UE
# ============================================================
with tab2:
    # ─── Comparativa entre països (any darrer) ──────────────────

    st.subheader(f"{'Comparativa europea' if _ca else 'Comparativa europea'} — {darrer_any}")

    if not df_lst.empty:
        PAIS_ORDER = ["EU27_2020", "ES", "DE", "FR", "IT", "PT", "NL", "PL"]
        df_disp = df_lst.set_index("pais_codi").reindex(PAIS_ORDER).reset_index()
        df_disp["pais_lbl"] = df_disp["pais"]

        # Taxa naixement vs defunció (barres aparellades)
        fig_br = go.Figure()
        fig_br.add_trace(go.Bar(
            x=df_disp["pais_lbl"], y=df_disp.get("ENT_BRTHR_PC", pd.Series()),
            name="Taxa naixement" if _ca else "Tasa nacimiento",
            marker_color=GREEN,
            text=[fpct(v, 1, sign=False) for v in df_disp.get("ENT_BRTHR_PC", pd.Series())],
            textposition="outside",
        ))
        fig_br.add_trace(go.Bar(
            x=df_disp["pais_lbl"], y=df_disp.get("ENT_DTHR_PC", pd.Series()),
            name="Taxa defunció" if _ca else "Tasa defunción",
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
        source(f"Eurostat <i>bd_size</i> ({darrer_any}). Càlcul propi" if _ca
               else f"Eurostat <i>bd_size</i> ({darrer_any}). Cálculo propio")

        # Insight rotació
        es_brth = df_disp[df_disp["pais_codi"] == "ES"]["ENT_BRTHR_PC"].iloc[0] if "ENT_BRTHR_PC" in df_disp.columns else None
        es_dth = df_disp[df_disp["pais_codi"] == "ES"]["ENT_DTHR_PC"].iloc[0] if "ENT_DTHR_PC" in df_disp.columns else None
        ue_brth = df_disp[df_disp["pais_codi"] == "EU27_2020"]["ENT_BRTHR_PC"].iloc[0] if "ENT_BRTHR_PC" in df_disp.columns else None
        ue_dth = df_disp[df_disp["pais_codi"] == "EU27_2020"]["ENT_DTHR_PC"].iloc[0] if "ENT_DTHR_PC" in df_disp.columns else None

        if es_brth is not None and es_dth is not None:
            es_net = es_brth - es_dth
            if _ca:
                txt = (
                    f"A Espanya, la taxa de naixement empresarial al CNAE 47 ({fpct(es_brth, 1, sign=False)}) "
                    f"queda <strong>per sota</strong> de la taxa de defunció ({fpct(es_dth, 1, sign=False)}), "
                    f"amb un saldo net negatiu de {fpct(es_net, 1)} punts. "
                )
                if ue_brth is not None and ue_dth is not None:
                    ue_net = ue_brth - ue_dth
                    txt += (
                        f"A la UE-27, el saldo net és {fpct(ue_net, 1)} punts "
                        f"(naixement {fpct(ue_brth, 1, sign=False)} vs defunció {fpct(ue_dth, 1, sign=False)}). "
                    )
                txt += (
                    "Una taxa de defunció superior a la de naixement de manera sostinguda apunta cap a "
                    "<strong>consolidació sectorial</strong>: el sector està perdent empreses netament."
                )
            else:
                txt = (
                    f"En España, la tasa de nacimiento empresarial del CNAE 47 ({fpct(es_brth, 1, sign=False)}) "
                    f"queda <strong>por debajo</strong> de la tasa de defunción ({fpct(es_dth, 1, sign=False)}), "
                    f"con un saldo neto negativo de {fpct(es_net, 1)} puntos. "
                )
                if ue_brth is not None and ue_dth is not None:
                    ue_net = ue_brth - ue_dth
                    txt += (
                        f"En la UE-27, el saldo neto es {fpct(ue_net, 1)} puntos "
                        f"(nacimiento {fpct(ue_brth, 1, sign=False)} vs defunción {fpct(ue_dth, 1, sign=False)}). "
                    )
                txt += (
                    "Una tasa de defunción superior a la de nacimiento de manera sostenida apunta a "
                    "<strong>consolidación sectorial</strong>: el sector está perdiendo empresas netamente."
                )
            insight(txt)

    # ─── Productivitat aparent: ocupació / empresa ───────────────

    st.subheader("Mida mitjana d'empresa (ocupats per empresa)" if _ca
                 else "Tamaño medio de empresa (ocupados por empresa)")

    if not df_lst.empty and "ENT_NR" in df_lst.columns and "EMP_NR" in df_lst.columns:
        df_lst["mida_mitjana"] = df_lst["EMP_NR"] / df_lst["ENT_NR"]
        PAIS_ORDER = ["EU27_2020", "ES", "DE", "FR", "IT", "PT", "NL", "PL"]
        df_mm = df_lst.set_index("pais_codi").reindex(PAIS_ORDER).reset_index()
        df_mm = df_mm.dropna(subset=["mida_mitjana"])
        df_mm = df_mm.sort_values("mida_mitjana", ascending=True)

        # Color: ES destaca, UE27 mig, resta gris
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
            xaxis_title="Ocupats / empresa" if _ca else "Ocupados / empresa",
            height=350,
            margin=dict(l=130, r=80, t=30, b=50),
        )
        st.plotly_chart(fig_mm, use_container_width=True)
        source(f"Eurostat <i>bd_size</i> ({darrer_any}). Càlcul propi" if _ca
               else f"Eurostat <i>bd_size</i> ({darrer_any}). Cálculo propio")

        # Insight mida mitjana
        es_mm = df_mm[df_mm["pais_codi"] == "ES"]["mida_mitjana"]
        ue_mm = df_mm[df_mm["pais_codi"] == "EU27_2020"]["mida_mitjana"]
        if not es_mm.empty and not ue_mm.empty:
            es_v = es_mm.iloc[0]
            ue_v = ue_mm.iloc[0]
            diff_pct = (es_v / ue_v - 1) * 100
            if _ca:
                txt = (
                    f"Cada empresa retail espanyola dóna feina de mitjana a <strong>{fnum(es_v, 1)} persones</strong>, "
                    f"davant les {fnum(ue_v, 1)} de la mitjana UE-27 ({fpct(diff_pct, 1)} respecte a la UE). "
                    "Aquesta mètrica és un indicador agregat de la concentració empresarial: "
                    "valors més alts indiquen una estructura dominada per grans cadenes."
                )
            else:
                txt = (
                    f"Cada empresa retail española da trabajo en promedio a <strong>{fnum(es_v, 1)} personas</strong>, "
                    f"frente a las {fnum(ue_v, 1)} de la media UE-27 ({fpct(diff_pct, 1)} respecto a la UE). "
                    "Esta métrica es un indicador agregado de la concentración empresarial: "
                    "valores más altos indican una estructura dominada por grandes cadenas."
                )
            insight(txt)

# ============================================================
# TAB 3: SUPERVIVÈNCIA
# ============================================================
with tab3:
    # ─── Supervivència (secundari, dins expander) ──────────────

    _lbl_surv_exp = ("Veure supervivència empresarial Y1 / Y2"
                     if _ca else
                     "Ver supervivencia empresarial Y1 / Y2")
    with highlight_expander(_lbl_surv_exp, expanded=False):

        if not df_surv.empty:
            st.subheader("Supervivència empresarial" if _ca else "Supervivencia empresarial")

            AGE_LBL_CA = {"Y1": "1 any després del naixement", "Y2": "2 anys després del naixement"}
            AGE_LBL_ES = {"Y1": "1 año después del nacimiento", "Y2": "2 años después del nacimiento"}
            age_lbl = AGE_LBL_CA if _ca else AGE_LBL_ES

            # Usar el darrer any disponible per cada age
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
                source(f"Eurostat <i>bd_size</i> (cohort {int(surv_max_any)}). Càlcul propi" if _ca
                       else f"Eurostat <i>bd_size</i> (cohort {int(surv_max_any)}). Cálculo propio")

                # Insight supervivència
                y1_es = df_s_lst[(df_s_lst["age"] == "Y1") & (df_s_lst["pais_codi"] == "ES")]["survival_pc"]
                y1_ue = df_s_lst[(df_s_lst["age"] == "Y1") & (df_s_lst["pais_codi"] == "EU27_2020")]["survival_pc"]
                if not y1_es.empty and not y1_ue.empty:
                    es_y1 = y1_es.iloc[0]
                    ue_y1 = y1_ue.iloc[0]
                    diff = ue_y1 - es_y1  # > 0 si Espanya sobreviu MENYS que la UE
                    _es_sobreviu_menys = diff > 0
                    if _ca:
                        if _es_sobreviu_menys:
                            lectura = (
                                "Una taxa de supervivència més baixa pot reflectir un entorn "
                                "competitiu més dur, barreres d'entrada més baixes (més empreses "
                                "fràgils que ho proven) o suport menor al primer any."
                            )
                        else:
                            lectura = (
                                "Una taxa de supervivència més alta indica un entorn d'entrada "
                                "més selectiu o un teixit empresarial amb projectes més robustos "
                                "des de l'inici. També pot reflectir més suport institucional "
                                "i finançament al primer any d'activitat."
                            )
                        txt = (
                            f"De cada 100 noves empreses retail creades a Espanya, <strong>{fpct(es_y1, 1, sign=False)} "
                            f"sobreviuen al primer any</strong>, davant les {fpct(ue_y1, 1, sign=False)} de la mitjana UE-27 "
                            f"(diferencial de {fpct(diff, 1)} punts). {lectura}"
                        )
                    else:
                        if _es_sobreviu_menys:
                            lectura = (
                                "Una tasa de supervivencia más baja puede reflejar un entorno "
                                "competitivo más duro, barreras de entrada más bajas (más empresas "
                                "frágiles que lo intentan) o menor apoyo al primer año."
                            )
                        else:
                            lectura = (
                                "Una tasa de supervivencia más alta indica un entorno de entrada "
                                "más selectivo o un tejido empresarial con proyectos más robustos "
                                "desde el inicio. También puede reflejar mayor apoyo institucional "
                                "y financiación en el primer año de actividad."
                            )
                        txt = (
                            f"De cada 100 nuevas empresas retail creadas en España, <strong>{fpct(es_y1, 1, sign=False)} "
                            f"sobreviven al primer año</strong>, frente a las {fpct(ue_y1, 1, sign=False)} de la media UE-27 "
                            f"(diferencial de {fpct(diff, 1)} puntos). {lectura}"
                        )
                    insight(txt)

# ─── Taula completa descarregable ──────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_total, use_container_width=True)
    st.download_button("CSV", df_total.to_csv(index=False).encode("utf-8"),
                       "estructura_retail_ue.csv", "text/csv")

if _ca:
    st.caption(
        "**Nota metodològica:** Les dades de 2021 endavant segueixen el nou marc estadístic europeu "
        "(Reglament UE 2019/2152). Per a sèries anteriors a 2021, el dataset Eurostat històric "
        "<i>bd_9bd_sz_cl_r2</i> cobreix 2008-2020 amb metodologia anterior; no s'inclou en aquesta pàgina "
        "per evitar comparacions metodològicament discutibles."
    )
else:
    st.caption(
        "**Nota metodológica:** Los datos desde 2021 siguen el nuevo marco estadístico europeo "
        "(Reglamento UE 2019/2152). Para series anteriores a 2021, el dataset Eurostat histórico "
        "<i>bd_9bd_sz_cl_r2</i> cubre 2008-2020 con metodología anterior; no se incluye en esta página "
        "para evitar comparaciones metodológicamente cuestionables."
    )

page_meta("Eurostat <i>bd_size</i> (Business Demography by size class and NACE)" if _ca
          else "Eurostat <i>bd_size</i> (Business Demography by size class and NACE)",
          st.session_state.lang)

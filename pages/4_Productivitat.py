"""Pàgina 4: Productivitat (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, BLUE, ORANGE)

st.set_page_config(page_title="Productivitat", page_icon="⚡", layout="wide")
inject_css()
t = setup_lang()

@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "productivitat.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

st.title(t("prod_title"))

_ca = st.session_state.lang == "ca"

# Noms complets (sense abreviatures)
_lbl_va = "Valor Afegit/hora" if _ca else "Valor Añadido/hora"
_lbl_xn = "Xifra de Negoci/hora" if _ca else "Cifra de Negocio/hora"
_lbl_va_short = "VA/hora"
_lbl_xn_short = "Xifra Negoci/hora" if _ca else "Cifra Negocio/hora"

if _ca:
    intro(
        "La <strong>productivitat</strong> mesura l'eficiència del sector dividint el resultat econòmic "
        "entre les hores treballades. Es presenten dues mètriques complementàries:<br>"
        f"• <strong>{_lbl_va}</strong>: quant valor net genera cada hora de treball, "
        "descomptant els costos intermedis (compres, subministraments). És la mesura d'eficiència pura.<br>"
        f"• <strong>{_lbl_xn}</strong>: quant factura cada hora de treball. "
        "Inclou tant el valor afegit com els costos intermedis.<br>"
        f"Si el {_lbl_va_short} creix més que el {_lbl_xn_short}, els <strong>marges milloren</strong> (el sector reté "
        "més valor de cada euro facturat). Si passa al revés, hi ha <strong>compressió de marges</strong>. "
        "Totes les dades són a preus constants (deflactats amb IPC general, base primer any disponible)."
    )
else:
    intro(
        "La <strong>productividad</strong> mide la eficiencia del sector dividiendo el resultado económico "
        "entre las horas trabajadas. Se presentan dos métricas complementarias:<br>"
        f"• <strong>{_lbl_va}</strong>: cuánto valor neto genera cada hora de trabajo, "
        "descontando los costes intermedios (compras, suministros). Es la medida de eficiencia pura.<br>"
        f"• <strong>{_lbl_xn}</strong>: cuánto factura cada hora de trabajo. "
        "Incluye tanto el valor añadido como los costes intermedios.<br>"
        f"Si el {_lbl_va_short} crece más que el {_lbl_xn_short}, los <strong>márgenes mejoran</strong> (el sector retiene "
        "más valor de cada euro facturado). Si ocurre al revés, hay <strong>compresión de márgenes</strong>. "
        "Todos los datos son a precios constantes (deflactados con IPC general, base primer año disponible)."
    )

if df.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

df = df.sort_values("any")

# ─── KPIs superiors ──────────────────────────────────────────

if "productivitat_va_hora" in df.columns:
    first = df.dropna(subset=["productivitat_va_hora"]).iloc[0]
    last = df.dropna(subset=["productivitat_va_hora"]).iloc[-1]
    var = ((last["productivitat_va_hora"] / first["productivitat_va_hora"]) - 1) * 100
    cagr_prod = cagr(first["productivitat_va_hora"], last["productivitat_va_hora"],
                     int(last["any"]) - int(first["any"]))

    any_first = int(first["any"])
    any_last = int(last["any"])
    n_anys = any_last - any_first

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{_lbl_va_short} ({any_last})",
                f"{fnum(last['productivitat_va_hora'], 2)} {t('prod_eur_h')}")
    col2.metric(f"{_lbl_va_short} ({any_first})",
                f"{fnum(first['productivitat_va_hora'], 2)} {t('prod_eur_h')}")
    col3.metric(f"{'Variació' if _ca else 'Variación'} {any_first}–{any_last}",
                fpct(var))
    with col4:
        st.metric(f"CAGR {any_first}–{any_last}", fpct(cagr_prod, 2))
        with st.popover("Què és el CAGR?" if _ca else "¿Qué es el CAGR?"):
            if _ca:
                st.markdown(
                    f"**CAGR** (*Compound Annual Growth Rate*) és la taxa de creixement anual compost.\n\n"
                    f"Indica quant ha crescut la productivitat **cada any de mitjana** si el creixement "
                    f"hagués estat constant entre {any_first} i {any_last} ({n_anys} anys).\n\n"
                    f"Un CAGR del **{fpct(cagr_prod, 2)}** vol dir que, de mitjana, la productivitat "
                    f"ha augmentat un {fpct(cagr_prod, 2)} cada any durant aquest període."
                )
            else:
                st.markdown(
                    f"**CAGR** (*Compound Annual Growth Rate*) es la tasa de crecimiento anual compuesto.\n\n"
                    f"Indica cuánto ha crecido la productividad **cada año de media** si el crecimiento "
                    f"hubiese sido constante entre {any_first} y {any_last} ({n_anys} años).\n\n"
                    f"Un CAGR del **{fpct(cagr_prod, 2)}** significa que, de media, la productividad "
                    f"ha aumentado un {fpct(cagr_prod, 2)} cada año durante este período."
                )

# ─── Gràfic 2: Índex base 100 ──────────��────────────────────

st.subheader("Evolució relativa (índex base 100)" if _ca
             else "Evolución relativa (índice base 100)")

df_idx = df.copy()
cols_idx = []
labels_idx = {}
colors_idx = {}

if "productivitat_va_hora" in df_idx.columns:
    base = df_idx["productivitat_va_hora"].dropna().iloc[0]
    df_idx["idx_va_hora"] = (df_idx["productivitat_va_hora"] / base) * 100
    cols_idx.append("idx_va_hora")
    labels_idx["idx_va_hora"] = _lbl_va_short
    colors_idx["idx_va_hora"] = PURPLE

if "productivitat_xn_hora" in df_idx.columns:
    base = df_idx["productivitat_xn_hora"].dropna().iloc[0]
    df_idx["idx_xn_hora"] = (df_idx["productivitat_xn_hora"] / base) * 100
    cols_idx.append("idx_xn_hora")
    labels_idx["idx_xn_hora"] = _lbl_xn_short
    colors_idx["idx_xn_hora"] = RED

if "personal_ocupat" in df_idx.columns:
    base = df_idx["personal_ocupat"].dropna().iloc[0]
    df_idx["idx_personal"] = (df_idx["personal_ocupat"] / base) * 100
    cols_idx.append("idx_personal")
    labels_idx["idx_personal"] = "Personal ocupat" if _ca else "Personal ocupado"
    colors_idx["idx_personal"] = BLUE

if "hores_treballades" in df_idx.columns:
    base = df_idx["hores_treballades"].dropna().iloc[0]
    df_idx["idx_hores"] = (df_idx["hores_treballades"] / base) * 100
    cols_idx.append("idx_hores")
    labels_idx["idx_hores"] = "Hores treballades" if _ca else "Horas trabajadas"
    colors_idx["idx_hores"] = ORANGE

fig_idx = go.Figure()
for col in cols_idx:
    fig_idx.add_trace(go.Scatter(
        x=df_idx["any"], y=df_idx[col],
        mode="lines+markers",
        name=labels_idx[col],
        line=dict(color=colors_idx[col], width=2.5),
        marker=dict(size=5),
    ))

fig_idx.add_hline(y=100, line_dash="dash", line_color="rgba(0,0,0,0.15)")
apply_layout(fig_idx,
    yaxis_title=f"{'Índex' if _ca else 'Índice'} (base 100 = {int(df_idx['any'].min())})",
    height=450,
)
st.plotly_chart(fig_idx, use_container_width=True)
source("INE, EEE. Càlcul propi" if _ca else "INE, EEE. Cálculo propio")

# ─── Insight productivitat ────────────────────────────────────

if "productivitat_va_hora" in df.columns and len(df) >= 4:
    df_i = df.dropna(subset=["personal_ocupat", "hores_treballades", "valor_afegit_constants", "xifra_negoci_constants"])
    if len(df_i) >= 4:
        # Calcular marge VA/XN per any
        df_i = df_i.copy()
        df_i["marge"] = df_i["valor_afegit_constants"] / df_i["xifra_negoci_constants"] * 100

        # Índexs base primer any
        base_yr = df_i.iloc[0]
        idx_pers = (df_i["personal_ocupat"].iloc[-1] / base_yr["personal_ocupat"] - 1) * 100
        idx_hores = (df_i["hores_treballades"].iloc[-1] / base_yr["hores_treballades"] - 1) * 100
        any_first = int(df_i["any"].iloc[0])
        any_last = int(df_i["any"].iloc[-1])

        if _ca:
            txt = (
                f"<strong>Més hores, no més contractació.</strong> "
                f"Entre {any_first} i {any_last}, el personal ocupat ha variat un {fpct(idx_pers)}, "
                f"mentre que les hores treballades han crescut un {fpct(idx_hores)}. "
                f"El sector ha optat per <strong>intensificar la jornada</strong> de la plantilla existent "
                f"abans que crear nous llocs de treball. La reforma laboral de 2022 — que va limitar la "
                f"temporalitat i va impulsar la conversió a contractes indefinits — ha contribuït a aquest patró: "
                f"menys rotació i més hores per treballador."
                f"<br><br>"
                f"<strong>La contractació segueix el valor afegit, no la facturació.</strong> "
                f"A partir de 2022, el valor afegit i el personal ocupat mostren trajectòries paral·leles, "
                f"mentre que la xifra de negoci creix a un ritme diferent. "
                f"Això suggereix que les decisions de contractació responen al <strong>valor net generat</strong> "
                f"(descomptant costos intermedis), no al volum de vendes brut."
                f"<br><br>"
                f"<strong>Marges volàtils.</strong> "
                f"El 2021 va ser excepcional: els ERTOs van reduir costos laborals mentre el consum "
                f"post-confinament disparava el valor afegit, generant marges artificials "
                f"({fnum(df_i[df_i['any']==2021]['marge'].iloc[0], 1)}% de valor afegit sobre xifra de negoci). "
                f"El 2022, la inflació va comprimir marges fins al {fnum(df_i[df_i['any']==2022]['marge'].iloc[0], 1)}%. "
                f"El 2023 es va estancar, i el 2024 els recupera ({fnum(df_i[df_i['any']==2024]['marge'].iloc[0], 1)}%). "
                f"Aquesta <strong>volatilitat dels marges</strong> explica la cautela del sector a l'hora de contractar "
                f"durant 2022-23: sense certesa de marges estables, les empreses van preferir augmentar hores "
                f"abans que assumir nous costos fixos de personal."
            )
        else:
            txt = (
                f"<strong>Más horas, no más contratación.</strong> "
                f"Entre {any_first} y {any_last}, el personal ocupado ha variado un {fpct(idx_pers)}, "
                f"mientras que las horas trabajadas han crecido un {fpct(idx_hores)}. "
                f"El sector ha optado por <strong>intensificar la jornada</strong> de la plantilla existente "
                f"antes que crear nuevos puestos de trabajo. La reforma laboral de 2022 — que limitó la "
                f"temporalidad e impulsó la conversión a contratos indefinidos — ha contribuido a este patrón: "
                f"menos rotación y más horas por trabajador."
                f"<br><br>"
                f"<strong>La contratación sigue al valor añadido, no a la facturación.</strong> "
                f"A partir de 2022, el valor añadido y el personal ocupado muestran trayectorias paralelas, "
                f"mientras que la cifra de negocio crece a un ritmo diferente. "
                f"Esto sugiere que las decisiones de contratación responden al <strong>valor neto generado</strong> "
                f"(descontando costes intermedios), no al volumen de ventas bruto."
                f"<br><br>"
                f"<strong>Márgenes volátiles.</strong> "
                f"2021 fue excepcional: los ERTEs redujeron costes laborales mientras el consumo "
                f"post-confinamiento disparaba el valor añadido, generando márgenes artificiales "
                f"({fnum(df_i[df_i['any']==2021]['marge'].iloc[0], 1)}% de valor añadido sobre cifra de negocio). "
                f"En 2022, la inflación comprimió márgenes hasta el {fnum(df_i[df_i['any']==2022]['marge'].iloc[0], 1)}%. "
                f"2023 se estancó, y 2024 los recupera ({fnum(df_i[df_i['any']==2024]['marge'].iloc[0], 1)}%). "
                f"Esta <strong>volatilidad de márgenes</strong> explica la cautela del sector al contratar "
                f"durante 2022-23: sin certeza de márgenes estables, las empresas prefirieron aumentar horas "
                f"antes que asumir nuevos costes fijos de personal."
            )
        insight(txt)

# ─── Secció: Distribució del VAB ────────��────────────────────

if "quota_salarial" in df.columns and "excedent_brut" in df.columns:
    st.markdown("---")
    st.subheader("Distribució del Valor Afegit" if _ca
                 else "Distribución del Valor Añadido")

    if _ca:
        intro(
            "El Valor Afegit que genera el sector es reparteix entre dos grans components: "
            "la <strong>remuneració dels treballadors</strong> (gastos de personal) i "
            "l'<strong>excedent brut d'explotació</strong> (beneficis empresarials, amortitzacions i impostos). "
            "La <strong>quota salarial</strong> (% del VA destinat a salaris) és un indicador clau de com "
            "es distribueix la riquesa generada.<br>"
            "El <strong>cost laboral per ocupat</strong> mostra l'evolució de la remuneració mitjana, "
            "a preus constants per eliminar l'efecte de la inflació."
        )
    else:
        intro(
            "El Valor Añadido que genera el sector se reparte entre dos grandes componentes: "
            "la <strong>remuneración de los trabajadores</strong> (gastos de personal) y "
            "el <strong>excedente bruto de explotaci��n</strong> (beneficios empresariales, amortizaciones e impuestos). "
            "La <strong>cuota salarial</strong> (% del VA destinado a salarios) es un indicador clave de cómo "
            "se distribuye la riqueza generada.<br>"
            "El <strong>coste laboral por ocupado</strong> muestra la evolución de la remuneración media, "
            "a precios constantes para eliminar el efecto de la inflación."
        )

    df_dist = df.dropna(subset=["gastos_personal_constants", "excedent_brut"])

    if not df_dist.empty:
        # Gràfic: Composició del VAB (àrea apilada)
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Scatter(
            x=df_dist["any"], y=df_dist["gastos_personal_constants"] / 1e9,
            mode="lines",
            name=("Remuneració treballadors" if _ca else "Remuneración trabajadores"),
            line=dict(width=0), fillcolor="rgba(46,134,193,0.5)",
            stackgroup="one",
        ))
        fig_dist.add_trace(go.Scatter(
            x=df_dist["any"], y=df_dist["excedent_brut"] / 1e9,
            mode="lines",
            name=("Excedent brut" if _ca else "Excedente bruto"),
            line=dict(width=0), fillcolor="rgba(93,79,255,0.5)",
            stackgroup="one",
        ))
        apply_layout(fig_dist,
            yaxis_title=("Milers M EUR" if _ca else "Miles M EUR"),
            height=400,
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        source("INE, EEE. Preus constants. Càlcul propi" if _ca
               else "INE, EEE. Precios constantes. Cálculo propio")

    # Gràfic: Quota salarial
    df_qs = df.dropna(subset=["quota_salarial"])
    if not df_qs.empty:
        st.subheader("Quota salarial" if _ca else "Cuota salarial")
        fig_qs = go.Figure()
        fig_qs.add_trace(go.Scatter(
            x=df_qs["any"], y=df_qs["quota_salarial"] * 100,
            mode="lines+markers",
            name=("Quota salarial" if _ca else "Cuota salarial"),
            line=dict(color=BLUE, width=3),
            marker=dict(size=8),
            text=[f"{v:.1f}%".replace(".", ",") for v in df_qs["quota_salarial"] * 100],
            textposition="top center",
            textfont=dict(size=10),
        ))
        apply_layout(fig_qs,
            yaxis_title=("% del Valor Afegit" if _ca else "% del Valor Añadido"),
            height=380,
        )
        st.plotly_chart(fig_qs, use_container_width=True)
        source("INE, EEE. Càlcul propi" if _ca else "INE, EEE. Cálculo propio")

    # Gràfic: Cost laboral per ocupat
    if "cost_laboral_per_ocupat" in df.columns:
        df_cl = df.dropna(subset=["cost_laboral_per_ocupat"])
        if not df_cl.empty:
            st.subheader("Cost laboral per ocupat (preus constants)" if _ca
                         else "Coste laboral por ocupado (precios constantes)")

            fig_cl = go.Figure()
            fig_cl.add_trace(go.Bar(
                x=df_cl["any"], y=df_cl["cost_laboral_per_ocupat"],
                marker_color=PURPLE,
                text=[f"{fnum(v, 0)} EUR" for v in df_cl["cost_laboral_per_ocupat"]],
                textposition="outside",
                textfont=dict(size=11),
            ))
            apply_layout(fig_cl,
                yaxis_title=("EUR / ocupat" if _ca else "EUR / ocupado"),
                height=380,
            )
            st.plotly_chart(fig_cl, use_container_width=True)
            source("INE, EEE. Preus constants. Càlcul propi" if _ca
                   else "INE, EEE. Precios constantes. Cálculo propio")

    # Insight distribució
    if not df_qs.empty:
        qs_first = df_qs.iloc[0]
        qs_last = df_qs.iloc[-1]
        var_qs = (qs_last["quota_salarial"] - qs_first["quota_salarial"]) * 100

        if _ca:
            txt_dist = (
                f"La quota salarial del comerç al detall ha passat del "
                f"<strong>{fpct(qs_first['quota_salarial'] * 100, 1, sign=False)}</strong> "
                f"({int(qs_first['any'])}) al "
                f"<strong>{fpct(qs_last['quota_salarial'] * 100, 1, sign=False)}</strong> "
                f"({int(qs_last['any'])}). "
            )
            if var_qs < -2:
                txt_dist += (
                    f"La caiguda de <strong>{fpct(abs(var_qs), 1, sign=False)} punts</strong> indica que "
                    f"l'excedent brut (beneficis + amortitzacions) ha crescut més que la remuneració: "
                    f"el sector <strong>reté més valor per als propietaris</strong> en detriment dels salaris relatius. "
                    f"Això és coherent amb la concentració empresarial: les grans cadenes generen més excedent "
                    f"per les economies d'escala i el seu poder de negociació amb proveïdors."
                )
            elif var_qs > 2:
                txt_dist += (
                    f"L'augment de <strong>{fpct(abs(var_qs), 1, sign=False)} punts</strong> indica que "
                    f"els salaris han absorbit una proporció creixent del valor generat: "
                    f"els <strong>treballadors capten més valor</strong>, cosa que pot reflectir millores salarials "
                    f"o reducció de marges empresarials."
                )
            else:
                txt_dist += (
                    "La distribució entre salaris i excedent brut s'ha mantingut <strong>relativament estable</strong>, "
                    "cosa que suggereix un equilibri entre la pressió salarial i la capacitat del sector "
                    "de mantenir els seus marges."
                )
        else:
            txt_dist = (
                f"La cuota salarial del comercio minorista ha pasado del "
                f"<strong>{fpct(qs_first['quota_salarial'] * 100, 1, sign=False)}</strong> "
                f"({int(qs_first['any'])}) al "
                f"<strong>{fpct(qs_last['quota_salarial'] * 100, 1, sign=False)}</strong> "
                f"({int(qs_last['any'])}). "
            )
            if var_qs < -2:
                txt_dist += (
                    f"La caída de <strong>{fpct(abs(var_qs), 1, sign=False)} puntos</strong> indica que "
                    f"el excedente bruto (beneficios + amortizaciones) ha crecido más que la remuneración: "
                    f"el sector <strong>retiene más valor para los propietarios</strong> en detrimento de los salarios relativos. "
                    f"Esto es coherente con la concentración empresarial: las grandes cadenas generan más excedente "
                    f"por las economías de escala y su poder de negociación con proveedores."
                )
            elif var_qs > 2:
                txt_dist += (
                    f"El aumento de <strong>{fpct(abs(var_qs), 1, sign=False)} puntos</strong> indica que "
                    f"los salarios han absorbido una proporción creciente del valor generado: "
                    f"los <strong>trabajadores captan más valor</strong>, lo que puede reflejar mejoras salariales "
                    f"o reducción de márgenes empresariales."
                )
            else:
                txt_dist += (
                    "La distribución entre salarios y excedente bruto se ha mantenido <strong>relativamente estable</strong>, "
                    "lo que sugiere un equilibrio entre la presión salarial y la capacidad del sector "
                    "de mantener sus márgenes."
                )
        insight(txt_dist)

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "productivitat_cnae47.csv", "text/csv")

page_meta("INE, Estadística Estructural d'Empreses (EEE)" if _ca
          else "INE, Estadística Estructural de Empresas (EEE)", st.session_state.lang)

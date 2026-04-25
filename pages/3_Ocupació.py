"""Pàgina 3: Ocupació (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, BLUE, ORANGE)

inject_css()
t = setup_lang(show_selector=False)
page_header()

@st.cache_data(ttl=3600)
def load_prod():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "productivitat.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_empreses():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "empreses.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df_prod = load_prod()
df_emp = load_empreses()

st.title(t("ocu_title"))

_ca = st.session_state.lang == "ca"

if _ca:
    intro(
        "L'<strong>ocupació</strong> del comerç al detall es mesura en dues dimensions complementàries: "
        "el <strong>personal ocupat</strong> (nombre de persones que treballen al sector) i les "
        "<strong>hores treballades</strong> (volum total de treball efectiu). La relació entre ambdues "
        "revela la <strong>intensitat laboral</strong>: si l'ocupació creix més que les hores, "
        "augmenta la parcialitat; si les hores creixen més, s'intensifiquen les jornades. "
        "La ràtio de <strong>treballadors per empresa</strong> connecta l'ocupació amb l'estructura "
        "empresarial i permet detectar tendències de concentració."
    )
else:
    intro(
        "El <strong>empleo</strong> del comercio minorista se mide en dos dimensiones complementarias: "
        "el <strong>personal ocupado</strong> (número de personas que trabajan en el sector) y las "
        "<strong>horas trabajadas</strong> (volumen total de trabajo efectivo). La relación entre ambas "
        "revela la <strong>intensidad laboral</strong>: si el empleo crece más que las horas, "
        "aumenta la parcialidad; si las horas crecen más, se intensifican las jornadas. "
        "La ratio de <strong>trabajadores por empresa</strong> conecta el empleo con la estructura "
        "empresarial y permite detectar tendencias de concentración."
    )

# ─── Ocupats i hores treballades ───────────────────────────────

if not df_prod.empty and "personal_ocupat" in df_prod.columns:
    df = df_prod.sort_values("any")

    # KPIs
    first = df.dropna(subset=["personal_ocupat"]).iloc[0]
    last = df.dropna(subset=["personal_ocupat"]).iloc[-1]
    var_ocu = ((last["personal_ocupat"] / first["personal_ocupat"]) - 1) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric(f"{'Personal ocupat' if _ca else 'Personal ocupado'} ({int(last['any'])})",
                fnum(last['personal_ocupat']))
    col2.metric(f"{'Variació' if _ca else 'Variación'} {int(first['any'])}-{int(last['any'])}",
                fpct(var_ocu))

    if "hores_treballades" in df.columns:
        last_h = df.dropna(subset=["hores_treballades"]).iloc[-1]
        col3.metric(f"{'Hores' if _ca else 'Horas'} ({int(last_h['any'])})",
                    f"{fnum(last_h['hores_treballades'] / 1e6)}M h")

    # Gràfic ocupats
    st.subheader(t("ocu_evolution"))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["any"], y=df["personal_ocupat"],
        mode="lines+markers", name=t("kpi_ocupacio"),
        line=dict(color=PURPLE, width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(93,79,255,0.08)",
    ))
    apply_layout(fig,
        yaxis_title=("Persones" if _ca else "Personas"),
        height=400, yaxis_range=[1500000, 2000000])
    st.plotly_chart(fig, use_container_width=True)
    source("INE, Estadística Estructural d'Empreses (EEE)" if _ca
           else "INE, Estadística Estructural de Empresas (EEE)")

    # Hores treballades
    if "hores_treballades" in df.columns:
        st.subheader(t("ocu_hours"))
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df["any"], y=df["hores_treballades"] / 1e6,
            marker_color=BLUE,
            text=[f"{fnum(v / 1e6)}M" for v in df["hores_treballades"]],
            textposition="outside",
            textfont=dict(size=10),
        ))
        apply_layout(fig2,
            yaxis_title=("Milions d'hores" if _ca else "Millones de horas"),
            height=400)
        st.plotly_chart(fig2, use_container_width=True)
        source("INE, EEE")

    # Hores per treballador
    if "hores_treballades" in df.columns and "personal_ocupat" in df.columns:
        df["hores_per_treballador"] = df["hores_treballades"] / df["personal_ocupat"]

        st.subheader("Hores anuals per treballador" if _ca else "Horas anuales por trabajador")
        fig_hpt = go.Figure()
        fig_hpt.add_trace(go.Scatter(
            x=df["any"], y=df["hores_per_treballador"],
            mode="lines+markers",
            line=dict(color=ORANGE, width=2.5),
            marker=dict(size=6),
        ))
        apply_layout(fig_hpt,
            yaxis_title=("Hores/any per treballador" if _ca else "Horas/año por trabajador"),
            height=380)
        st.plotly_chart(fig_hpt, use_container_width=True)
        source("INE, EEE. Càlcul propi" if _ca else "INE, EEE. Cálculo propio")

    # Insight
    if "hores_treballades" in df.columns and "valor_afegit_constants" in df.columns and "xifra_negoci_constants" in df.columns:
        first_h = df.dropna(subset=["hores_treballades"]).iloc[0]
        last_h = df.dropna(subset=["hores_treballades"]).iloc[-1]
        var_h = ((last_h["hores_treballades"] / first_h["hores_treballades"]) - 1) * 100

        hpt_first = df.dropna(subset=["hores_per_treballador"]).iloc[0]["hores_per_treballador"]
        hpt_last = df.dropna(subset=["hores_per_treballador"]).iloc[-1]["hores_per_treballador"]

        any_f = int(first["any"])
        any_l = int(last["any"])

        if _ca:
            txt = (
                f"<strong>Més hores, no més contractació.</strong> "
                f"Entre {any_f} i {any_l}, el personal ocupat ha variat un {fpct(var_ocu)}, "
                f"mentre que les hores treballades han crescut un {fpct(var_h)}. "
                f"El sector ha optat per <strong>intensificar la jornada</strong> de la plantilla existent "
                f"abans que crear nous llocs de treball. La reforma laboral de 2022 — que va limitar la "
                f"temporalitat i va impulsar la conversió a contractes indefinits — ha contribuït a aquest patró: "
                f"menys rotació i més hores per treballador. "
                f"La ràtio d'hores per treballador ha passat de {fnum(hpt_first)} a {fnum(hpt_last)} h/any."
                f"<br><br>"
                f"<strong>La contractació segueix el valor afegit, no la facturació.</strong> "
                f"A partir de 2022, el valor afegit i el personal ocupat mostren trajectòries paral·leles, "
                f"mentre que la xifra de negoci creix a un ritme diferent. "
                f"Això suggereix que les decisions de contractació responen al <strong>valor net generat</strong> "
                f"(descomptant costos intermedis), no al volum de vendes brut."
            )
        else:
            txt = (
                f"<strong>Más horas, no más contratación.</strong> "
                f"Entre {any_f} y {any_l}, el personal ocupado ha variado un {fpct(var_ocu)}, "
                f"mientras que las horas trabajadas han crecido un {fpct(var_h)}. "
                f"El sector ha optado por <strong>intensificar la jornada</strong> de la plantilla existente "
                f"antes que crear nuevos puestos de trabajo. La reforma laboral de 2022 — que limitó la "
                f"temporalidad e impulsó la conversión a contratos indefinidos — ha contribuido a este patrón: "
                f"menos rotación y más horas por trabajador. "
                f"La ratio de horas por trabajador ha pasado de {fnum(hpt_first)} a {fnum(hpt_last)} h/año."
                f"<br><br>"
                f"<strong>La contratación sigue al valor añadido, no a la facturación.</strong> "
                f"A partir de 2022, el valor añadido y el personal ocupado muestran trayectorias paralelas, "
                f"mientras que la cifra de negocio crece a un ritmo diferente. "
                f"Esto sugiere que las decisiones de contratación responden al <strong>valor neto generado</strong> "
                f"(descontando costes intermedios), no al volumen de ventas bruto."
            )
        insight(txt)

# ─── Treballadors per empresa ──────────────────────────────────

st.subheader(t("ocu_per_company"))

df_esp = df_emp[df_emp["territori"] == "espanya"].sort_values("any") if not df_emp.empty else pd.DataFrame()

if not df_prod.empty and not df_esp.empty and "personal_ocupat" in df_prod.columns:
    merged = df_prod[["any", "personal_ocupat"]].merge(df_esp[["any", "empreses"]], on="any")
    merged["treb_per_empresa"] = merged["personal_ocupat"] / merged["empreses"]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=merged["any"], y=merged["treb_per_empresa"],
        mode="lines+markers",
        line=dict(color=ORANGE, width=2.5),
        marker=dict(size=6),
    ))
    apply_layout(fig3,
        yaxis_title=("Treballadors / empresa" if _ca else "Trabajadores / empresa"),
        height=400)
    st.plotly_chart(fig3, use_container_width=True)
    source("INE, EEE i DIRCE. Càlcul propi" if _ca else "INE, EEE y DIRCE. Cálculo propio")

    if len(merged) > 1:
        te_first = merged.iloc[0]["treb_per_empresa"]
        te_last = merged.iloc[-1]["treb_per_empresa"]
        if _ca:
            insight(
                f"La ràtio de treballadors per empresa ha passat de <strong>{fnum(te_first, 1)}</strong> "
                f"({int(merged.iloc[0]['any'])}) a <strong>{fnum(te_last, 1)}</strong> ({int(merged.iloc[-1]['any'])}). "
                f"Que pugi indica que les empreses supervivents són més grans: la concentració empresarial "
                f"elimina petits comerços i deixa al sector empreses amb plantilles més àmplies. "
                f"Això té implicacions per a la <strong>qualitat de l'ocupació</strong>: les empreses més grans "
                f"solen oferir millors condicions laborals, convenis col·lectius més favorables "
                f"i més oportunitats de promoció interna."
            )
        else:
            insight(
                f"La ratio de trabajadores por empresa ha pasado de <strong>{fnum(te_first, 1)}</strong> "
                f"({int(merged.iloc[0]['any'])}) a <strong>{fnum(te_last, 1)}</strong> ({int(merged.iloc[-1]['any'])}). "
                f"Que suba indica que las empresas supervivientes son más grandes: la concentración empresarial "
                f"elimina pequeños comercios y deja al sector empresas con plantillas más amplias. "
                f"Esto tiene implicaciones para la <strong>calidad del empleo</strong>: las empresas más grandes "
                f"suelen ofrecer mejores condiciones laborales, convenios colectivos más favorables "
                f"y más oportunidades de promoción interna."
            )
else:
    st.info("Dades insuficients per calcular treballadors per empresa." if _ca
            else "Datos insuficientes para calcular trabajadores por empresa.")

with st.expander(t("download_data")):
    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
        st.download_button("CSV", df_prod.to_csv(index=False).encode("utf-8"), "ocupacio_cnae47.csv", "text/csv")

page_meta("INE, Estadística Estructural d'Empreses (EEE)" if _ca
          else "INE, Estadística Estructural de Empresas (EEE)", st.session_state.lang)

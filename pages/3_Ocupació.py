"""Pàgina 3: Ocupació (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, BLUE, ORANGE)

st.set_page_config(page_title="Ocupació", page_icon="👥", layout="wide")
inject_css()
t = setup_lang()

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
    if "hores_treballades" in df.columns:
        first_h = df.dropna(subset=["hores_treballades"]).iloc[0]
        last_h = df.dropna(subset=["hores_treballades"]).iloc[-1]
        var_h = ((last_h["hores_treballades"] / first_h["hores_treballades"]) - 1) * 100

        hpt_first = df.dropna(subset=["hores_per_treballador"]).iloc[0]["hores_per_treballador"]
        hpt_last = df.dropna(subset=["hores_per_treballador"]).iloc[-1]["hores_per_treballador"]

        gap_ocu_hores = var_ocu - var_h

        if _ca:
            txt = ""
            if gap_ocu_hores > 3:
                txt += (
                    f"L'ocupació creix ({fpct(var_ocu)}) més que les hores ({fpct(var_h)}): "
                    f"el sector <strong>crea llocs de treball però amb menys hores per persona</strong>, "
                    f"suggerint un augment de la parcialitat i la flexibilització laboral. "
                )
            elif gap_ocu_hores < -3:
                txt += (
                    f"Les hores creixen ({fpct(var_h)}) més que l'ocupació ({fpct(var_ocu)}): "
                    f"el sector <strong>intensifica les jornades dels treballadors existents</strong> "
                    f"en lloc de crear noves places. "
                )
            else:
                txt += (
                    f"Ocupació i hores evolucionen de forma similar ({fpct(var_ocu)} vs {fpct(var_h)}), "
                    f"indicant <strong>estabilitat en la jornada mitjana</strong> del sector. "
                )
            txt += (
                f"La ràtio d'hores per treballador ha passat de {fnum(hpt_first)} a {fnum(hpt_last)} h/any. "
                f"El comerç al detall es caracteritza per una <strong>alta incidència de treball parcial</strong> "
                f"(caps de setmana, campanyes estacionals), cosa que fa que les hores per treballador "
                f"siguin inferiors a la mitjana de l'economia."
            )
        else:
            txt = ""
            if gap_ocu_hores > 3:
                txt += (
                    f"El empleo crece ({fpct(var_ocu)}) más que las horas ({fpct(var_h)}): "
                    f"el sector <strong>crea puestos de trabajo pero con menos horas por persona</strong>, "
                    f"sugiriendo un aumento de la parcialidad y la flexibilización laboral. "
                )
            elif gap_ocu_hores < -3:
                txt += (
                    f"Las horas crecen ({fpct(var_h)}) más que el empleo ({fpct(var_ocu)}): "
                    f"el sector <strong>intensifica las jornadas de los trabajadores existentes</strong> "
                    f"en lugar de crear nuevas plazas. "
                )
            else:
                txt += (
                    f"Empleo y horas evolucionan de forma similar ({fpct(var_ocu)} vs {fpct(var_h)}), "
                    f"indicando <strong>estabilidad en la jornada media</strong> del sector. "
                )
            txt += (
                f"La ratio de horas por trabajador ha pasado de {fnum(hpt_first)} a {fnum(hpt_last)} h/año. "
                f"El comercio minorista se caracteriza por una <strong>alta incidencia de trabajo parcial</strong> "
                f"(fines de semana, campañas estacionales), lo que hace que las horas por trabajador "
                f"sean inferiores a la media de la economía."
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

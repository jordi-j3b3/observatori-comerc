"""Pàgina 6: Comparativa Europea (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout,
                   PURPLE, RED, BLUE, GREEN, ORANGE, GRAY)

inject_css()
t = setup_lang(show_selector=False)
page_header()

@st.cache_data(ttl=3600)
def load_europa():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "europa_vab.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_retail_mensual():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "europa_retail_mensual.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


df = load_europa()
df_m = load_retail_mensual()

st.title(t("eu_title"))

_ca = st.session_state.lang == "ca"

if _ca:
    intro(
        "Aquesta secció posiciona el comerç al detall espanyol en el context europeu "
        "des de dues mirades complementàries. "
        "A dalt, el <strong>pols mensual</strong> del volum de vendes (Eurostat, base 2021=100, "
        "ajustat estacional) permet seguir el cicle de consum gairebé en temps real i comparar "
        "Espanya amb la mitjana de l'eurozona i la UE-27. "
        "A continuació, la mirada <strong>estructural anual</strong> mostra el pes del CNAE 47 "
        "sobre el PIB de cada país —indicador de l'orientació econòmica cap al consum final— "
        "i el VAB absolut com a dimensió del sector. "
        "Espanya es destaca en vermell per facilitar la comparació."
    )
else:
    intro(
        "Esta sección posiciona el comercio minorista español en el contexto europeo "
        "desde dos miradas complementarias. "
        "Arriba, el <strong>pulso mensual</strong> del volumen de ventas (Eurostat, base 2021=100, "
        "ajustado estacional) permite seguir el ciclo de consumo casi en tiempo real y comparar "
        "España con la media de la eurozona y la UE-27. "
        "A continuación, la mirada <strong>estructural anual</strong> muestra el peso del CNAE 47 "
        "sobre el PIB de cada país —indicador de la orientación económica hacia el consumo final— "
        "y el VAB absoluto como dimensión del sector. "
        "España se destaca en rojo para facilitar la comparación."
    )

# ─── SECCIÓ MENSUAL: volum de vendes (Eurostat sts_trtu_m) ──────

if not df_m.empty:
    st.subheader("Pols mensual del comerç a Europa" if _ca
                 else "Pulso mensual del comercio en Europa")

    df_m["periode"] = df_m["periode"].astype(str)
    darrer = df_m["periode"].max()
    df_last = df_m[df_m["periode"] == darrer]

    es_row = df_last[df_last["pais_codi"] == "ES"]
    ea_row = df_last[df_last["pais_codi"] == "EA20"]
    eu_row = df_last[df_last["pais_codi"] == "EU27_2020"]

    c1, c2, c3, c4 = st.columns(4)
    help_anual = (
        f"Variació del volum de vendes minoristes respecte al mateix mes de l'any "
        f"anterior. Dada de {darrer}."
        if _ca else
        f"Variación del volumen de ventas minoristas respecto al mismo mes del "
        f"año anterior. Dato de {darrer}."
    )
    lbl_es = "Espanya — vs. fa un any" if _ca else "España — vs. hace un año"
    lbl_ea = "Eurozona — vs. fa un any" if _ca else "Eurozona — vs. hace un año"
    lbl_eu = "UE-27 — vs. fa un any" if _ca else "UE-27 — vs. hace un año"
    lbl_idx = f"Índex Espanya ({darrer})" if _ca else f"Índice España ({darrer})"

    if not es_row.empty:
        es_yoy = es_row.iloc[0].get("yoy")
        c1.metric(lbl_es, fpct(es_yoy, 1) if pd.notna(es_yoy) else "—",
                  help=help_anual)
    if not ea_row.empty:
        ea_yoy = ea_row.iloc[0].get("yoy")
        c2.metric(lbl_ea, fpct(ea_yoy, 1) if pd.notna(ea_yoy) else "—",
                  help=help_anual)
    if not eu_row.empty:
        eu_yoy = eu_row.iloc[0].get("yoy")
        c3.metric(lbl_eu, fpct(eu_yoy, 1) if pd.notna(eu_yoy) else "—",
                  help=help_anual)
    if not es_row.empty:
        es_idx = es_row.iloc[0]["index_volum"]
        c4.metric(lbl_idx, fnum(es_idx, 1),
                  help="Volum de vendes amb base 2021=100, ajustat estacional. "
                       "Si supera 100, les vendes són superiors a la mitjana de 2021."
                  if _ca else
                  "Volumen de ventas con base 2021=100, ajustado estacional. "
                  "Si supera 100, las ventas son superiores a la media de 2021.")

    st.write("")

    # ─── Controls del gràfic ────────────────────────────────
    cc1, cc2 = st.columns([1, 2])

    finestres = {
        "24": ("Darrers 2 anys", "Últimos 2 años"),
        "60": ("Darrers 5 anys", "Últimos 5 años"),
        "120": ("Darrers 10 anys", "Últimos 10 años"),
        "all": ("Tota la sèrie", "Toda la serie"),
    }
    with cc1:
        finestra = st.selectbox(
            "Període" if _ca else "Período",
            options=list(finestres.keys()),
            index=1,
            format_func=lambda k: finestres[k][0 if _ca else 1],
            key="europa_retail_finestra",
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
            "Comparar amb altres països (opcional)" if _ca
            else "Comparar con otros países (opcional)",
            options=paisos_opcionals,
            default=[],
            format_func=lambda c: pais_lbl.get(c, c),
            key="europa_retail_paisos",
        )

    df_plot = df_m.copy()
    df_plot["dt"] = pd.to_datetime(df_plot["periode"], format="%Y-%m", errors="coerce")
    if finestra != "all":
        cutoff = df_plot["dt"].max() - pd.DateOffset(months=int(finestra))
        df_plot = df_plot[df_plot["dt"] >= cutoff]

    color_m = {
        "ES": RED, "EA20": "#34495e", "EU27_2020": "#7f8c8d",
        "DE": BLUE, "FR": GREEN, "IT": ORANGE,
        "PT": "#8E44AD", "NL": "#16a085", "BE": "#95a5a6",
    }
    # Per defecte només 3 línies (ES + dues referències agregades)
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
        yaxis_title="Índex (2021=100)" if _ca else "Índice (2021=100)",
        height=420,
    )
    st.plotly_chart(fig_m, use_container_width=True)

    # ─── Insight dinàmic ────────────────────────────────────
    if not es_row.empty and not ea_row.empty:
        _es_yoy = es_row.iloc[0].get("yoy")
        _ea_yoy = ea_row.iloc[0].get("yoy")
        if pd.notna(_es_yoy) and pd.notna(_ea_yoy):
            _spread = _es_yoy - _ea_yoy
            _es_hist = (df_m[df_m["pais_codi"] == "ES"]
                        .sort_values("periode")
                        .tail(6))
            _avg_6m = _es_hist["yoy"].dropna().mean()
            _trend = _es_hist["yoy"].dropna().tolist()
            _accel = (_trend[-1] - _trend[0]) if len(_trend) >= 2 else 0

            if _ca:
                verb = "creixen" if _es_yoy >= 0 else "cauen"
                txt = (
                    f"Al <strong>{darrer}</strong>, les vendes minoristes a Espanya "
                    f"<strong>{verb} un {abs(_es_yoy):.1f} %</strong> respecte al mateix "
                    f"mes de l'any anterior. "
                )
                if _spread >= 0.5:
                    txt += (
                        f"Espanya supera la mitjana de l'eurozona ({_ea_yoy:+.1f} %) "
                        f"en <strong>{_spread:+.1f} punts</strong>, "
                        "senyal d'un cicle de consum més dinàmic. "
                    )
                elif _spread <= -0.5:
                    txt += (
                        f"Espanya queda <strong>{abs(_spread):.1f} punts</strong> per sota "
                        f"de l'eurozona ({_ea_yoy:+.1f} %). "
                    )
                else:
                    txt += (
                        f"En línia amb la mitjana de l'eurozona ({_ea_yoy:+.1f} %). "
                    )
                txt += (
                    f"En els darrers 6 mesos, la variació interanual mitjana s'ha situat "
                    f"al <strong>{_avg_6m:+.1f} %</strong>"
                )
                if _accel > 0.5:
                    txt += " amb tendència accelerant."
                elif _accel < -0.5:
                    txt += " amb tendència desaccelerant."
                else:
                    txt += " sense canvis de ritme significatius."
            else:
                verb = "crecen" if _es_yoy >= 0 else "caen"
                txt = (
                    f"En <strong>{darrer}</strong>, las ventas minoristas en España "
                    f"<strong>{verb} un {abs(_es_yoy):.1f} %</strong> respecto al mismo "
                    f"mes del año anterior. "
                )
                if _spread >= 0.5:
                    txt += (
                        f"España supera la media de la eurozona ({_ea_yoy:+.1f} %) "
                        f"en <strong>{_spread:+.1f} puntos</strong>, "
                        "señal de un ciclo de consumo más dinámico. "
                    )
                elif _spread <= -0.5:
                    txt += (
                        f"España queda <strong>{abs(_spread):.1f} puntos</strong> por debajo "
                        f"de la eurozona ({_ea_yoy:+.1f} %). "
                    )
                else:
                    txt += (
                        f"En línea con la media de la eurozona ({_ea_yoy:+.1f} %). "
                    )
                txt += (
                    f"En los últimos 6 meses, la variación interanual media se ha situado "
                    f"en el <strong>{_avg_6m:+.1f} %</strong>"
                )
                if _accel > 0.5:
                    txt += " con tendencia acelerándose."
                elif _accel < -0.5:
                    txt += " con tendencia desacelerándose."
                else:
                    txt += " sin cambios de ritmo significativos."
            insight(txt)

    # Barres horitzontals: variació anual per país, mes actual
    st.markdown(
        f"**Comparativa per país — vendes vs. fa un any ({darrer})**"
        if _ca else
        f"**Comparativa por país — ventas vs. hace un año ({darrer})**"
    )

    df_yoy = df_last.dropna(subset=["yoy"]).copy()
    ordre_grup = {"ES": 0, "EA20": 1, "EU27_2020": 2}
    df_yoy["_ord"] = df_yoy["pais_codi"].map(ordre_grup).fillna(3)
    df_yoy = df_yoy.sort_values(["_ord", "yoy"], ascending=[True, True])

    colors_yoy = [RED if c == "ES" else PURPLE if c in ("EA20", "EU27_2020") else BLUE
                  for c in df_yoy["pais_codi"]]
    fig_yoy = go.Figure()
    fig_yoy.add_trace(go.Bar(
        y=df_yoy["pais"], x=df_yoy["yoy"],
        orientation="h",
        marker_color=colors_yoy,
        text=[fpct(v, 1) for v in df_yoy["yoy"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    fig_yoy.add_vline(x=0, line=dict(color="#999", width=1))
    apply_layout(fig_yoy,
        xaxis_title="% variació respecte fa un any" if _ca
                    else "% variación respecto hace un año",
        height=max(300, len(df_yoy) * 32),
        margin=dict(l=140, r=80, t=20, b=50),
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    source(
        f"Eurostat, sts_trtu_m. Volum de vendes G47, ajustat estacional. Darrera dada: {darrer}."
        if _ca else
        f"Eurostat, sts_trtu_m. Volumen de ventas G47, ajustado estacional. Último dato: {darrer}."
    )

    st.divider()

# ─── SECCIÓ ANUAL: VAB i pes sobre PIB ──────────────────────

if df.empty:
    st.warning("No hi ha dades europees anuals disponibles." if _ca
               else "No hay datos europeos anuales disponibles.")
    st.stop()

# ─── Selector d'any ─────────────────────────��──────────────────

anys = sorted(df["any"].dropna().unique(), reverse=True)
any_sel = st.selectbox(t("year"), anys, index=0)

df_year = df[df["any"] == any_sel].copy()

# ─── KPIs posició Espanya ────────────────────────────────────

exclude_agg = ["EU27_2020", "EA20", "EA19"]
df_countries = df_year[~df_year["pais_codi"].isin(exclude_agg)].copy()
es_data = df_year[df_year["pais_codi"] == "ES"]
eu_data = df_year[df_year["pais_codi"] == "EU27_2020"]

if not es_data.empty and "pes_cnae47" in es_data.columns:
    col1, col2, col3 = st.columns(3)

    es_pes = es_data.iloc[0]["pes_cnae47"] * 100
    lbl_pes = "Pes CNAE 47 Espanya" if _ca else "Peso CNAE 47 España"
    col1.metric(f"{lbl_pes} ({int(any_sel)})", fpct(es_pes, 2, sign=False))

    if not eu_data.empty:
        eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100
        diff = es_pes - eu_pes
        col2.metric("Mitjana UE-27" if _ca else "Media UE-27",
                    fpct(eu_pes, 2, sign=False), f"{fpct(diff, 2)} vs UE")

    if not df_countries.empty:
        ranking = df_countries.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=False)
        pos_es = list(ranking["pais_codi"]).index("ES") + 1 if "ES" in list(ranking["pais_codi"]) else "—"
        col3.metric("Posició al rànquing" if _ca else "Posición en el ranking",
                    f"#{pos_es} de {len(ranking)}")

# ─── Gràfic 1: Pes CNAE 47 sobre PIB ─────────────────────────

st.subheader(t("eu_weight"))

if "pes_cnae47" in df_year.columns:
    df_sorted = df_year.dropna(subset=["pes_cnae47"]).sort_values("pes_cnae47", ascending=True)

    colors = [RED if code == "ES" else PURPLE if code == "EU27_2020" else GRAY
              for code in df_sorted["pais_codi"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["pais"], x=df_sorted["pes_cnae47"] * 100,
        orientation="h",
        marker_color=colors,
        text=[fpct(v, 2, sign=False) for v in df_sorted["pes_cnae47"] * 100],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig,
        xaxis_title="% PIB",
        height=max(450, len(df_sorted) * 28),
        margin=dict(l=140, r=80, t=40, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Gràfic 2: VAB absolut ──────────────────────────────────

st.subheader(f"VAB CNAE 47 ({int(any_sel)}) — {t('pib_meur')}")

if "vab_meur" in df_year.columns:
    df_abs = df_countries.dropna(subset=["vab_meur"])
    df_abs = df_abs.sort_values("vab_meur", ascending=True).tail(15)

    colors2 = [RED if code == "ES" else BLUE for code in df_abs["pais_codi"]]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=df_abs["pais"], x=df_abs["vab_meur"],
        orientation="h",
        marker_color=colors2,
        text=[fnum(v) for v in df_abs["vab_meur"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig2,
        xaxis_title=t("pib_meur"),
        height=500,
        margin=dict(l=140, r=80, t=40, b=50),
    )
    st.plotly_chart(fig2, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Gràfic 3: Evolució temporal ─────────────────────────────

st.subheader("Evolució pes CNAE 47 — principals països" if _ca
             else "Evolución peso CNAE 47 — principales países")

highlight = ["ES", "DE", "FR", "IT", "PT", "EU27_2020"]
colors_map = {
    "ES": RED, "DE": BLUE, "FR": GREEN,
    "IT": ORANGE, "PT": "#8E44AD", "EU27_2020": PURPLE,
}

if "pes_cnae47" in df.columns:
    fig3 = go.Figure()
    for code in highlight:
        df_c = df[df["pais_codi"] == code].sort_values("any")
        if not df_c.empty:
            fig3.add_trace(go.Scatter(
                x=df_c["any"], y=df_c["pes_cnae47"] * 100,
                mode="lines+markers",
                name=df_c["pais"].iloc[0],
                line=dict(color=colors_map.get(code, "#999"), width=2.5),
                marker=dict(size=5),
            ))

    apply_layout(fig3, yaxis_title="% PIB", height=450)
    st.plotly_chart(fig3, use_container_width=True)
    source("Eurostat, Comptes Nacionals" if _ca else "Eurostat, Cuentas Nacionales")

# ─── Insight Europa ──────────────────────────────────────────

if not es_data.empty and not eu_data.empty and "pes_cnae47" in es_data.columns:
    es_pes = es_data.iloc[0]["pes_cnae47"] * 100
    eu_pes = eu_data.iloc[0]["pes_cnae47"] * 100

    es_hist = df[df["pais_codi"] == "ES"].sort_values("any")
    if len(es_hist) > 1:
        es_first = es_hist.iloc[0]["pes_cnae47"] * 100
        es_last = es_hist.iloc[-1]["pes_cnae47"] * 100
        es_trend = es_last - es_first

        if _ca:
            txt = (
                f"Espanya destina un <strong>{fpct(es_pes, 2, sign=False)}</strong> del seu PIB al comerç al detall, "
            )
            if es_pes > eu_pes:
                txt += (
                    f"<strong>{fpct(es_pes - eu_pes, 2)} per sobre</strong> de la mitjana europea ({fpct(eu_pes, 2, sign=False)}). "
                    "Això pot reflectir una estructura econòmica amb més pes del consum final "
                    "i una menor industrialització relativa comparada amb països com Alemanya. "
                    "El pes superior també s'explica per la importància del turisme, que impulsa "
                    "el consum al detall especialment en zones costaneres i urbanes. "
                )
            else:
                txt += (
                    f"<strong>{fpct(eu_pes - es_pes, 2)} per sota</strong> de la mitjana europea ({fpct(eu_pes, 2, sign=False)}). "
                )
            txt += (
                f"La tendència mostra una variació de <strong>{fpct(es_trend, 2)}</strong> des de "
                f"{int(es_hist.iloc[0]['any'])}. "
            )
            if es_trend < -0.2:
                txt += (
                    "La pèrdua de pes és consistent amb la transformació digital i la concentració empresarial: "
                    "menys empreses, però més grans i eficients, generant menys VAB relatiu però amb major productivitat."
                )
        else:
            txt = (
                f"España destina un <strong>{fpct(es_pes, 2, sign=False)}</strong> de su PIB al comercio minorista, "
            )
            if es_pes > eu_pes:
                txt += (
                    f"<strong>{fpct(es_pes - eu_pes, 2)} por encima</strong> de la media europea ({fpct(eu_pes, 2, sign=False)}). "
                    "Esto puede reflejar una estructura económica con más peso del consumo final "
                    "y una menor industrialización relativa comparada con países como Alemania. "
                    "El peso superior también se explica por la importancia del turismo, que impulsa "
                    "el consumo minorista especialmente en zonas costeras y urbanas. "
                )
            else:
                txt += (
                    f"<strong>{fpct(eu_pes - es_pes, 2)} por debajo</strong> de la media europea ({fpct(eu_pes, 2, sign=False)}). "
                )
            txt += (
                f"La tendencia muestra una variación de <strong>{fpct(es_trend, 2)}</strong> desde "
                f"{int(es_hist.iloc[0]['any'])}. "
            )
            if es_trend < -0.2:
                txt += (
                    "La pérdida de peso es consistente con la transformación digital y la concentración empresarial: "
                    "menos empresas, pero más grandes y eficientes, generando menos VAB relativo pero con mayor productividad."
                )
        insight(txt)

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "europa_cnae47.csv", "text/csv")

page_meta("Eurostat, Comptes Nacionals d'Europa" if _ca
          else "Eurostat, Cuentas Nacionales de Europa", st.session_state.lang)

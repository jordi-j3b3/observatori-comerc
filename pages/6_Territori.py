"""Pàgina 6: Territori — Magnituds del CNAE 47 per CCAA"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   load_geojson_spain_ccaa, canaries_inset_layers,
                   fnum, fpct, apply_layout, highlight_expander,
                   PURPLE, PURPLE_LIGHT, RED, PALETTE,
                   BRAND, BRAND_DEEP, YELLOW, GRAY_DARK)

inject_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"

st.title("Territori" if _ca else "Territorio")

if _ca:
    intro(
        "La Comptabilitat Regional de l'INE no desglossa el CNAE 47 per comunitats autonomes. "
        "Per estimar el VAB del comerç al detall per CCAA, combinem dues fonts: "
        "la <strong>comptabilitat regional d'Eurostat</strong> (VAB de la secció G-I: comerç, transport i hostaleria) "
        "i la <strong>xifra de negoci per CCAA</strong> de l'Enquesta Estructural d'Empreses de l'INE. "
        "El metode hibrid distribueix el VAB nacional del CNAE 47 entre CCAA ponderant "
        "les quotes regionals de G-I (top-down) amb les quotes de facturacio (bottom-up), "
        "garantint que la suma coincideixi amb el total nacional d'Eurostat."
    )
else:
    intro(
        "La Contabilidad Regional del INE no desglosa el CNAE 47 por comunidades autonomas. "
        "Para estimar el VAB del comercio minorista por CCAA, combinamos dos fuentes: "
        "la <strong>contabilidad regional de Eurostat</strong> (VAB de la sección G-I: comercio, transporte y hosteleria) "
        "y la <strong>cifra de negocio por CCAA</strong> de la Encuesta Estructural de Empresas del INE. "
        "El metodo hibrido distribuye el VAB nacional del CNAE 47 entre CCAA ponderando "
        "las cuotas regionales de G-I (top-down) con las cuotas de facturacion (bottom-up), "
        "garantizando que la suma coincida con el total nacional de Eurostat."
    )

@st.cache_data(ttl=3600)
def load_data():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "eee_ccaa.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data
def load_geojson():
    return load_geojson_spain_ccaa(with_canaries_inset=True)

df_eee = load_data()

if df_eee.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

geojson = load_geojson()
df_ccaa = df_eee[df_eee["territori"] != "espanya"].copy()
df_esp = df_eee[df_eee["territori"] == "espanya"].copy()
_tots_anys = sorted(df_ccaa["any"].dropna().unique())
if "pes_cnae47_pib" in df_ccaa.columns:
    anys = sorted(df_ccaa.dropna(subset=["pes_cnae47_pib"])["any"].unique())
else:
    anys = _tots_anys
if not anys:
    anys = _tots_anys

# ─── Selector d'any ──────────────────────────────────────────

any_sel = st.select_slider(
    t("emp_ccaa_year"),
    options=anys,
    value=max(anys),
)

# ─── KPIs ────────────────────────────────────────────────────

VAB_COL = "vab_eurostat" if "vab_eurostat" in df_eee.columns else "vab_estimat"

d_yr_esp = df_esp[df_esp["any"] == any_sel]
if not d_yr_esp.empty:
    row = d_yr_esp.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    if pd.notna(row.get("pes_cnae47_pib")):
        c1.metric(
            f"{'Pes CNAE 47 / PIB' if _ca else 'Peso CNAE 47 / PIB'} ({int(any_sel)})",
            fpct(row["pes_cnae47_pib"] * 100, 1, sign=False))
    if "xifra_negoci" in row and pd.notna(row.get("xifra_negoci")):
        c2.metric(t("eee_ccaa_xn") + " (M EUR)", fnum(row["xifra_negoci"] / 1e6))
    if "personal_ocupat" in row and pd.notna(row.get("personal_ocupat")):
        c3.metric(t("eee_ccaa_personal"), fnum(row["personal_ocupat"]))
    if "locals" in row and pd.notna(row.get("locals")):
        c4.metric("Locals" if _ca else "Locales", fnum(row["locals"]))

# ─── Pes del CNAE 47 sobre el PIB per CCAA ──────────────────

_lbl_pes = ("Pes del comerç al detall sobre el PIB de cada CCAA" if _ca
            else "Peso del comercio minorista sobre el PIB de cada CCAA")
st.subheader(f"{_lbl_pes} ({int(any_sel)})")

if "pes_cnae47_pib" in df_ccaa.columns:
    d_pes = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["pes_cnae47_pib"]).copy()
    d_pes = d_pes.sort_values("pes_cnae47_pib", ascending=True)

    if not d_pes.empty:
        d_pes["_pct"] = d_pes["pes_cnae47_pib"] * 100

        esp_pes_row = df_esp[df_esp["any"] == any_sel]
        esp_pes = None
        if not esp_pes_row.empty and pd.notna(esp_pes_row.iloc[0].get("pes_cnae47_pib")):
            esp_pes = esp_pes_row.iloc[0]["pes_cnae47_pib"] * 100

        colors_pes = []
        for _, r in d_pes.iterrows():
            if esp_pes is not None and r["_pct"] >= esp_pes:
                colors_pes.append(PURPLE)
            else:
                colors_pes.append(PURPLE_LIGHT)

        fig_pes = go.Figure()
        fig_pes.add_trace(go.Bar(
            y=d_pes["territori"], x=d_pes["_pct"],
            orientation="h",
            marker_color=colors_pes,
            text=[fpct(v, 1, sign=False) for v in d_pes["_pct"]],
            textposition="outside",
            textfont=dict(size=11),
        ))

        if esp_pes is not None:
            fig_pes.add_vline(
                x=esp_pes, line_dash="dash", line_color=RED, line_width=2,
                annotation_text=f"{'Espanya' if _ca else 'Espana'}: {fpct(esp_pes, 1, sign=False)}",
                annotation_position="top right",
            )

        apply_layout(fig_pes,
            xaxis_title="% PIB",
            height=max(450, len(d_pes) * 32 + 100),
            margin=dict(l=200, r=100, t=50, b=50),
        )
        st.plotly_chart(fig_pes, use_container_width=True)
        if _ca:
            source(
                "Eurostat (comptabilitat regional G-I, <i>nama_10r_3gva</i> + VAB G47 nacional, <i>nama_10_a64</i>) "
                "i INE (xifra de negoci CNAE 47 per CCAA, taula 76817). "
                "Mètode: distribució proporcional híbrida (mitjana de quotes G-I i XN) "
                "restringida al total nacional Eurostat"
            )
        else:
            source(
                "Eurostat (contabilidad regional G-I, <i>nama_10r_3gva</i> + VAB G47 nacional, <i>nama_10_a64</i>) "
                "e INE (cifra de negocio CNAE 47 por CCAA, tabla 76817). "
                "Método: distribución proporcional híbrida (media de cuotas G-I y XN) "
                "restringida al total nacional Eurostat"
            )

        # Insight pes/PIB
        _top1 = d_pes.iloc[-1]
        _bot1 = d_pes.iloc[0]
        _above = d_pes[d_pes["_pct"] >= esp_pes] if esp_pes else d_pes
        _below = d_pes[d_pes["_pct"] < esp_pes] if esp_pes else pd.DataFrame()
        _spread = _top1["_pct"] - _bot1["_pct"]
        if _ca:
            _txt_pes = (
                f"<strong>{_top1['territori']}</strong> lidera amb un {fpct(_top1['_pct'], 1, sign=False)} del seu PIB "
                f"dedicat al comerç al detall, gairebé el doble que <strong>{_bot1['territori']}</strong> "
                f"({fpct(_bot1['_pct'], 1, sign=False)}). "
            )
            if esp_pes:
                _txt_pes += (
                    f"<strong>{len(_above)}</strong> comunitats superen la mitjana nacional ({fpct(esp_pes, 1, sign=False)}) "
                    f"i <strong>{len(_below)}</strong> queden per sota. "
                )
            _txt_pes += (
                "Les CCAA amb més pes del retail solen tenir economies orientades al consum final i al turisme, "
                "mentre que les de menor pes tenen estructures més industrials o de serveis avancats."
            )
        else:
            _txt_pes = (
                f"<strong>{_top1['territori']}</strong> lidera con un {fpct(_top1['_pct'], 1, sign=False)} de su PIB "
                f"dedicado al comercio minorista, casi el doble que <strong>{_bot1['territori']}</strong> "
                f"({fpct(_bot1['_pct'], 1, sign=False)}). "
            )
            if esp_pes:
                _txt_pes += (
                    f"<strong>{len(_above)}</strong> comunidades superan la media nacional ({fpct(esp_pes, 1, sign=False)}) "
                    f"y <strong>{len(_below)}</strong> quedan por debajo. "
                )
            _txt_pes += (
                "Las CCAA con mas peso del retail suelen tener economias orientadas al consumo final y al turismo, "
                "mientras que las de menor peso tienen estructuras mas industriales o de servicios avanzados."
            )
        insight(_txt_pes)

    # ── Mapa del pes ──
    d_map = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["pes_cnae47_pib"]).copy()
    d_map["_pct"] = d_map["pes_cnae47_pib"] * 100

    if not d_map.empty:
        fig_map = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=d_map["territori"],
            featureidkey="properties.territori",
            z=d_map["_pct"],
            zmin=d_map["_pct"].min() * 0.9,
            zmax=d_map["_pct"].max() * 1.05,
            colorscale=[
                [0, "#ffffff"], [0.25, "#dde7f0"], [0.5, "#6985a8"],
                [0.75, "#1f487a"], [1, "#003366"],
            ],
            colorbar=dict(title="% PIB", thickness=15),
            marker=dict(line=dict(width=1.5, color="white")),
            text=d_map["territori"],
            hovertemplate="<b>%{text}</b><br>Pes CNAE 47: %{z:.1f}%<extra></extra>",
        ))
        fig_map.update_layout(
            map=dict(
                style="white-bg",
                center=dict(lat=38.7, lon=-4.0),
                zoom=4.55,
                layers=canaries_inset_layers(),
            ),
            height=700, margin=dict(l=0, r=0, t=10, b=10),
            dragmode=False,
            annotations=[dict(
                text="<b>CANÀRIES</b>" if _ca else "<b>CANARIAS</b>",
                xref="paper", yref="paper",
                x=0.18, y=0.18,
                showarrow=False,
                font=dict(size=10, color="#003366", family="Inter, sans-serif"),
            )],
        )
        st.plotly_chart(fig_map, use_container_width=True,
                        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False})

# ─── Productivitat per CCAA ──────────────────────────────────

d_derived = df_ccaa[df_ccaa["any"] == any_sel].copy()
if "xifra_negoci" in d_derived.columns and "personal_ocupat" in d_derived.columns:
    d_derived["prod_xn_ocupat"] = d_derived["xifra_negoci"] / d_derived["personal_ocupat"]

    st.subheader(f"{t('eee_ccaa_prod')} ({int(any_sel)})")
    d_prod = d_derived.dropna(subset=["prod_xn_ocupat"]).sort_values("prod_xn_ocupat", ascending=True)

    fig_prod = go.Figure()
    fig_prod.add_trace(go.Bar(
        y=d_prod["territori"], x=d_prod["prod_xn_ocupat"] / 1000,
        orientation="h", marker_color=PURPLE_LIGHT,
        text=[f"{fnum(v/1000, 1)} k" for v in d_prod["prod_xn_ocupat"]],
        textposition="outside", textfont=dict(size=11),
    ))

    esp_row = df_esp[df_esp["any"] == any_sel]
    if not esp_row.empty and "xifra_negoci" in esp_row.columns:
        esp_p = esp_row["xifra_negoci"].values[0] / esp_row["personal_ocupat"].values[0]
        fig_prod.add_vline(
            x=esp_p / 1000, line_dash="dash", line_color=RED, line_width=2,
            annotation_text=f"{'Espanya' if _ca else 'España'}: {fnum(esp_p/1000, 1)} k",
            annotation_position="top right",
        )

    apply_layout(fig_prod,
        xaxis_title=("Milers EUR / ocupat" if _ca else "Miles EUR / ocupado"),
        height=max(450, len(d_prod) * 32 + 100),
        margin=dict(l=200, r=100, t=50, b=50),
    )
    st.plotly_chart(fig_prod, use_container_width=True)
    source("INE, Enquesta Estructural d'Empreses. Calcul propi" if _ca
           else "INE, Encuesta Estructural de Empresas. Calculo propio")

    # Insight productivitat
    if not d_prod.empty:
        _p_top = d_prod.iloc[-1]
        _p_bot = d_prod.iloc[0]
        _p_ratio = _p_top["prod_xn_ocupat"] / _p_bot["prod_xn_ocupat"]
        if _ca:
            _txt_prod = (
                f"La productivitat per ocupat varia un <strong>x{fnum(_p_ratio, 1)}</strong> entre "
                f"<strong>{_p_top['territori']}</strong> ({fnum(_p_top['prod_xn_ocupat']/1000, 1)} k EUR) "
                f"i <strong>{_p_bot['territori']}</strong> ({fnum(_p_bot['prod_xn_ocupat']/1000, 1)} k EUR). "
                "Aquesta diferència reflecteix el tiquet mitja (producte de més o menys valor), "
                "la presencia de grans cadenes (mes eficients en facturacio per treballador) "
                "i el cost de vida de cada regio."
            )
        else:
            _txt_prod = (
                f"La productividad por ocupado varia un <strong>x{fnum(_p_ratio, 1)}</strong> entre "
                f"<strong>{_p_top['territori']}</strong> ({fnum(_p_top['prod_xn_ocupat']/1000, 1)} k EUR) "
                f"y <strong>{_p_bot['territori']}</strong> ({fnum(_p_bot['prod_xn_ocupat']/1000, 1)} k EUR). "
                "Esta diferencia refleja el ticket medio (producto de mas o menos valor), "
                "la presencia de grandes cadenas (mas eficientes en facturacion por trabajador) "
                "y el coste de vida de cada region."
            )
        insight(_txt_prod)

# ─── Salari mitjà per CCAA ───────────────────────────────────

if "sous_salaris" in d_derived.columns and "personal_ocupat" in d_derived.columns:
    _lbl_sal_exp = ("Veure salari mitjà del comerç al detall per CCAA"
                    if _ca else
                    "Ver salario medio del comercio minorista por CCAA")
    with highlight_expander(_lbl_sal_exp, expanded=False):
        d_derived["sal_med"] = d_derived["sous_salaris"] / d_derived["personal_ocupat"]

        st.subheader(f"{t('eee_ccaa_sal_med')} ({int(any_sel)})")
        d_sal = d_derived.dropna(subset=["sal_med"]).sort_values("sal_med", ascending=True)

        # Gradient blau marí: més intens com més alt el salari. La CCAA
        # de baix és més clara, la de dalt el blau marca pur. Així el
        # rànquing es llegeix d'un cop d'ull sense necessitat d'ordre.
        _vmin = float(d_sal["sal_med"].min())
        _vmax = float(d_sal["sal_med"].max())
        _span = max(_vmax - _vmin, 1.0)
        def _color_sal(v):
            t_ = (v - _vmin) / _span  # 0..1
            # Interpolació entre #b9c9da (clar) i #003366 (BRAND)
            r = int(round(185 - 185 * t_ + 0 * t_))   # 185 -> 0
            g = int(round(201 - 201 * t_ + 51 * t_))  # 201 -> 51
            b = int(round(218 - 218 * t_ + 102 * t_)) # 218 -> 102
            return f"rgb({r},{g},{b})"
        _bar_colors = [_color_sal(v) for v in d_sal["sal_med"]]

        fig_sal = go.Figure()
        fig_sal.add_trace(go.Bar(
            y=d_sal["territori"], x=d_sal["sal_med"],
            orientation="h",
            marker=dict(
                color=_bar_colors,
                line=dict(color=BRAND_DEEP, width=0.5),
            ),
            text=[f"{fnum(v)} EUR" for v in d_sal["sal_med"]],
            textposition="outside", textfont=dict(size=11, color=BRAND_DEEP),
            hovertemplate="<b>%{y}</b>: %{x:,.0f} EUR<extra></extra>",
        ))

        esp_s = df_esp[df_esp["any"] == any_sel]
        if not esp_s.empty and "sous_salaris" in esp_s.columns:
            sal_esp = esp_s["sous_salaris"].values[0] / esp_s["personal_ocupat"].values[0]
            # Mitjana sectorial Espanya: línia groga marca per destacar
            # contrast amb el blau de les barres.
            fig_sal.add_vline(
                x=sal_esp, line_dash="dash", line_color=YELLOW, line_width=3,
                annotation_text=f"{'Espanya' if _ca else 'España'} (sector): {fnum(sal_esp)} EUR",
                annotation_position="top right",
                annotation=dict(font=dict(color=BRAND_DEEP, size=12)),
            )

        apply_layout(fig_sal,
            xaxis_title="EUR / ocupat" if _ca else "EUR / ocupado",
            height=max(450, len(d_sal) * 32 + 100),
            margin=dict(l=200, r=100, t=50, b=50),
        )
        st.plotly_chart(fig_sal, use_container_width=True)

        if _ca:
            st.caption(
                "**Nota:** Aquesta xifra divideix la massa total de sous i salaris entre el nombre de persones "
                "ocupades (incloent-hi temps parcial). El comerç al detall té una elevada taxa de parcialitat "
                "(~30% dels ocupats), de manera que la mitjana per persona pot quedar per sota de l'SMI a jornada "
                "completa sense que això impliqui cap incompliment legal. "
                "A més, \"sous i salaris\" exclou les cotitzacions socials a càrrec de l'empresa (~23% del cost "
                "laboral total). Vegeu l'apartat 4 de Metodologia per a una explicació detallada."
            )
        else:
            st.caption(
                "**Nota:** Esta cifra divide la masa total de sueldos y salarios entre el número de personas "
                "ocupadas (incluyendo tiempo parcial). El comercio minorista tiene una elevada tasa de parcialidad "
                "(~30% de los ocupados), de modo que la media por persona puede quedar por debajo del SMI a jornada "
                "completa sin que ello implique ningún incumplimiento legal. "
                "Además, \"sueldos y salarios\" excluye las cotizaciones sociales a cargo de la empresa (~23% del coste "
                "laboral total). Véase el apartado 4 de Metodología para una explicación detallada."
            )

    source("INE, Enquesta Estructural d'Empreses. Càlcul propi" if _ca
           else "INE, Encuesta Estructural de Empresas. Cálculo propio")

    # Insight salari
    if not d_sal.empty:
        _s_top = d_sal.iloc[-1]
        _s_bot = d_sal.iloc[0]
        _s_diff = _s_top["sal_med"] - _s_bot["sal_med"]
        if _ca:
            _txt_sal = (
                f"El salari mitjà del sector varia entre <strong>{fnum(_s_bot['sal_med'])} EUR</strong> "
                f"({_s_bot['territori']}) i <strong>{fnum(_s_top['sal_med'])} EUR</strong> "
                f"({_s_top['territori']}), una diferència de <strong>{fnum(_s_diff)} EUR</strong>. "
                "Les CCAA amb salaris més alts coincideixen generalment amb les de major cost de vida "
                "i concentració de grans empreses."
            )
        else:
            _txt_sal = (
                f"El salario medio del sector varía entre <strong>{fnum(_s_bot['sal_med'])} EUR</strong> "
                f"({_s_bot['territori']}) y <strong>{fnum(_s_top['sal_med'])} EUR</strong> "
                f"({_s_top['territori']}), una diferencia de <strong>{fnum(_s_diff)} EUR</strong>. "
                "Las CCAA con salarios más altos coinciden generalmente con las de mayor coste de vida "
                "y concentración de grandes empresas."
            )
        insight(_txt_sal)


# ─── Comparativa salarial vs total Espanya (EAES) ─────────────

@st.cache_data(ttl=3600)
def load_eaes():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "eaes.csv")
    if not os.path.exists(p):
        return pd.DataFrame()
    return pd.read_csv(p)


df_eaes = load_eaes()
if not df_eaes.empty:
    st.markdown("---")
    st.header(("Comparativa salarial vs total Espanya"
                if _ca else "Comparativa salarial vs total España"))

    if _ca:
        st.markdown(
            "El gràfic anterior mostra el salari mitjà del comerç al detall **calculat amb "
            "l'Enquesta Estructural d'Empreses (EEE)**: massa de sous dividida entre el total "
            "d'ocupats. Per comparar amb la mitjana de l'economia espanyola, fem servir una "
            "font diferent però **consistent entre sectors**: l'**Enquesta Anual d'Estructura "
            "Salarial (EAES, taula INE 28185)**, que mesura el salari brut anual per "
            "treballador a jornada equivalent."
        )
    else:
        st.markdown(
            "El gráfico anterior muestra el salario medio del comercio minorista **calculado "
            "con la Encuesta Estructural de Empresas (EEE)**: masa de sueldos dividida entre "
            "el total de ocupados. Para comparar con la media de la economía española, usamos "
            "una fuente distinta pero **consistente entre sectores**: la **Encuesta Anual de "
            "Estructura Salarial (EAES, tabla INE 28185)**, que mide el salario bruto anual "
            "por trabajador a jornada equivalente."
        )

    # Any més recent + valors clau
    _yr_eaes = int(df_eaes["any"].max())
    _eaes_last = df_eaes[df_eaes["any"] == _yr_eaes]
    SECTOR_TOTAL = "Industria, construcción y servicios (excepto actividades de los hogares como empleadores y de organizaciones y organismos extraterritoriales)"
    SECTOR_COMERCIO = "Comercio al por mayor y al por menor; reparación de vehículos de motor y motocicletas"

    _total = _eaes_last[_eaes_last["sector"] == SECTOR_TOTAL]
    _comer = _eaes_last[_eaes_last["sector"] == SECTOR_COMERCIO]

    if not _total.empty and not _comer.empty:
        _v_total = float(_total["valor"].iloc[0])
        _v_comer = float(_comer["valor"].iloc[0])
        _diff = _v_comer - _v_total
        _diff_pct = (_diff / _v_total) * 100

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(("Mitjana economia espanyola" if _ca
                        else "Media economía española"),
                       f"{fnum(_v_total)} EUR",
                       help=f"EAES {_yr_eaes} · jornada equivalent")
        with c2:
            st.metric(("Sector comerç (G45+G46+G47)" if _ca
                        else "Sector comercio (G45+G46+G47)"),
                       f"{fnum(_v_comer)} EUR",
                       help=f"EAES {_yr_eaes} · inclou majorista")
        with c3:
            _label_diff = ("Diferència sobre la mitjana" if _ca
                            else "Diferencia sobre la media")
            st.metric(_label_diff,
                       fpct(_diff_pct, 1),
                       delta=f"{fnum(_diff)} EUR",
                       delta_color="inverse")

        # Gràfic barres horitzontals comparativa per a l'any seleccionat
        _lbl_total = "Total economia espanyola" if _ca else "Total economía española"
        _lbl_comer = "Sector comerç (G)" if _ca else "Sector comercio (G)"
        _comp = pd.DataFrame({
            "Categoria": [_lbl_total, _lbl_comer],
            "Valor": [_v_total, _v_comer],
            "Color": [BRAND_DEEP, BRAND],
        })

        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(
            y=_comp["Categoria"], x=_comp["Valor"],
            orientation="h",
            marker=dict(color=_comp["Color"], line=dict(color=BRAND_DEEP, width=0.5)),
            text=[f"{fnum(v)} EUR" for v in _comp["Valor"]],
            textposition="outside", textfont=dict(size=13, color=BRAND_DEEP),
            hovertemplate="<b>%{y}</b>: %{x:,.0f} EUR<extra></extra>",
            width=0.5,
        ))
        apply_layout(fig_c,
            xaxis_title="EUR / treballador / any" if _ca else "EUR / trabajador / año",
            height=240, margin=dict(l=220, r=120, t=20, b=50),
        )
        st.plotly_chart(fig_c, use_container_width=True)
        source(f"INE, Encuesta Anual de Estructura Salarial (EAES), taula 28185 · {_yr_eaes}")

        # Evolució temporal (10 anys disponibles)
        _serie_total = df_eaes[df_eaes["sector"] == SECTOR_TOTAL].sort_values("any")
        _serie_comer = df_eaes[df_eaes["sector"] == SECTOR_COMERCIO].sort_values("any")

        if len(_serie_total) >= 3 and len(_serie_comer) >= 3:
            _lbl_evo = ("Veure evolució 2014-{:d}".format(_yr_eaes) if _ca
                        else "Ver evolución 2014-{:d}".format(_yr_eaes))
            with highlight_expander(_lbl_evo, expanded=False):
                fig_evo = go.Figure()
                fig_evo.add_trace(go.Scatter(
                    x=_serie_total["any"], y=_serie_total["valor"],
                    mode="lines+markers",
                    name=_lbl_total,
                    line=dict(color=BRAND_DEEP, width=2.8),
                    marker=dict(size=7),
                    hovertemplate="<b>%{x}</b>: %{y:,.0f} EUR<extra></extra>",
                ))
                fig_evo.add_trace(go.Scatter(
                    x=_serie_comer["any"], y=_serie_comer["valor"],
                    mode="lines+markers",
                    name=_lbl_comer,
                    line=dict(color=YELLOW, width=2.8),
                    marker=dict(size=7, line=dict(color=BRAND_DEEP, width=1)),
                    hovertemplate="<b>%{x}</b>: %{y:,.0f} EUR<extra></extra>",
                ))
                apply_layout(fig_evo,
                    yaxis_title="EUR / treballador / any" if _ca
                                else "EUR / trabajador / año",
                    height=380, margin=dict(l=70, r=20, t=40, b=50),
                )
                st.plotly_chart(fig_evo, use_container_width=True)
                source(f"INE, EAES (taula 28185) · sèrie 2014-{_yr_eaes}")

        # Insight + nota metodològica
        if _ca:
            insight(
                f"Segons l'EAES de l'any {_yr_eaes}, el sector comerç (G45+G46+G47) paga "
                f"un <strong>{fpct(abs(_diff_pct), 1, sign=False)} menys</strong> que la "
                f"mitjana de l'economia espanyola: <strong>{fnum(_v_comer)} EUR vs "
                f"{fnum(_v_total)} EUR</strong>. Aquesta diferència reflecteix el pes elevat "
                f"d'ocupacions de menor qualificació i la presència de jornades parcials, "
                f"especialment al comerç al detall G47. "
                f"<br><br><em>Nota: l'EAES només publica el sector G complet (que inclou "
                f"comerç majorista G45+G46 i venda i reparació de vehicles G45), no "
                f"el CNAE 47 aïllat. La xifra del sector comerç de l'EAES tendeix a "
                f"sobreestimar lleugerament el salari del retail estrictament G47 "
                f"perquè el majorista paga més de mitjana.</em>"
            )
        else:
            insight(
                f"Según la EAES del año {_yr_eaes}, el sector comercio (G45+G46+G47) paga "
                f"un <strong>{fpct(abs(_diff_pct), 1, sign=False)} menos</strong> que la "
                f"media de la economía española: <strong>{fnum(_v_comer)} EUR vs "
                f"{fnum(_v_total)} EUR</strong>. Esta diferencia refleja el peso elevado "
                f"de ocupaciones de menor cualificación y la presencia de jornadas parciales, "
                f"especialmente en el comercio minorista G47. "
                f"<br><br><em>Nota: la EAES solo publica el sector G completo (que incluye "
                f"comercio mayorista G45+G46 y venta y reparación de vehículos G45), no "
                f"el CNAE 47 aislado. La cifra del sector comercio de la EAES tiende a "
                f"sobreestimar ligeramente el salario del retail estrictamente G47 "
                f"porque el mayorista paga más de media.</em>"
            )


# ─── Taula ────────────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_eee, use_container_width=True)
    st.download_button("CSV", df_eee.to_csv(index=False).encode("utf-8"),
                       "territori_cnae47.csv", "text/csv")

page_meta("INE + Eurostat. Estimació híbrida propia" if _ca
          else "INE + Eurostat. Estimacion híbrida pròpia", st.session_state.lang)

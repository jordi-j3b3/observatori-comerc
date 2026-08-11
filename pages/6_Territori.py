"""Pàgina 6: Territori — Magnituds del CNAE 47 per CCAA (disseny premium)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (
    inject_css, inject_premium_page_css, setup_lang, page_header,
    insight, source, page_meta,
    fnum, fpct, apply_layout, highlight_expander,
    kicker, action_title, deck, key_takeaways, exhibit_header,
    freshness_badge,
    NAVY, OCRE, G1_P, G2_P,
    load_geojson_spain_ccaa, canaries_inset_layers,
)

inject_css()
inject_premium_page_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"


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

kicker("Anàlisi territorial · Comerç al detall per CCAA" if _ca
       else "Análisis territorial · Comercio minorista por CCAA")

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

# ─── Càlculs per a header i takeaways (últim any disponible) ──
_ly = int(max(anys))

_d_hdr = df_ccaa[df_ccaa["any"] == _ly].dropna(subset=["pes_cnae47_pib"]).copy()
_d_hdr["_pct"] = _d_hdr["pes_cnae47_pib"] * 100
_d_hdr = _d_hdr.sort_values("_pct")
_hdr_top = _d_hdr.iloc[-1]
_hdr_bot = _d_hdr.iloc[0]
_hdr_ratio = _hdr_top["_pct"] / _hdr_bot["_pct"] if _hdr_bot["_pct"] else 0

_esp_hdr = df_esp[df_esp["any"] == _ly]
_esp_pes_hdr = None
if not _esp_hdr.empty and pd.notna(_esp_hdr.iloc[0].get("pes_cnae47_pib")):
    _esp_pes_hdr = _esp_hdr.iloc[0]["pes_cnae47_pib"] * 100

# Productivitat per al takeaway
_dp_hdr = df_ccaa[df_ccaa["any"] == _ly].copy()
_prod_top = _prod_bot = _prod_ratio = None
if "xifra_negoci" in _dp_hdr.columns and "personal_ocupat" in _dp_hdr.columns:
    _dp_hdr["_prod"] = _dp_hdr["xifra_negoci"] / _dp_hdr["personal_ocupat"]
    _dp_hdr = _dp_hdr.dropna(subset=["_prod"]).sort_values("_prod")
    if not _dp_hdr.empty:
        _prod_top = _dp_hdr.iloc[-1]
        _prod_bot = _dp_hdr.iloc[0]
        _prod_ratio = _prod_top["_prod"] / _prod_bot["_prod"]

# ─── HEADER ──────────────────────────────────────────────────
if _ca:
    action_title(
        f"El pes del comerç sobre el PIB regional oscil·la entre el "
        f"{fpct(_hdr_top['_pct'], 1, sign=False)} i el {fpct(_hdr_bot['_pct'], 1, sign=False)}")
    deck("El comerç al detall pesa molt més a les economies orientades al consum "
         "i al turisme que a les industrials o de serveis avançats.")
else:
    action_title(
        f"El peso del comercio sobre el PIB regional oscila entre el "
        f"{fpct(_hdr_top['_pct'], 1, sign=False)} y el {fpct(_hdr_bot['_pct'], 1, sign=False)}")
    deck("El comercio minorista pesa mucho más en las economías orientadas al "
         "consumo y al turismo que en las industriales o de servicios avanzados.")

if _ca:
    _takeaways = [
        f"El {_ly}, <b>{_hdr_top['territori']}</b> destina el "
        f"<b>{fpct(_hdr_top['_pct'], 1, sign=False)}</b> del seu PIB al comerç al detall, "
        f"<b>{fnum(_hdr_ratio, 1)}</b> vegades el de <b>{_hdr_bot['territori']}</b> "
        f"({fpct(_hdr_bot['_pct'], 1, sign=False)}).",
    ]
    if _esp_pes_hdr is not None:
        _above = int((_d_hdr["_pct"] >= _esp_pes_hdr).sum())
        _below = int((_d_hdr["_pct"] < _esp_pes_hdr).sum())
        _takeaways.append(
            f"<b>{_above}</b> comunitats superen la mitjana espanyola "
            f"(<b>{fpct(_esp_pes_hdr, 1, sign=False)}</b> del PIB) i <b>{_below}</b> hi queden per sota.")
    if _prod_ratio is not None:
        _takeaways.append(
            f"La facturació per ocupat varia <b>{fnum(_prod_ratio, 1)}</b> vegades entre "
            f"<b>{_prod_top['territori']}</b> ({fnum(_prod_top['_prod']/1000, 0)} k EUR) "
            f"i <b>{_prod_bot['territori']}</b> ({fnum(_prod_bot['_prod']/1000, 0)} k EUR).")
    _tk_label = "Conclusions clau"
else:
    _takeaways = [
        f"En {_ly}, <b>{_hdr_top['territori']}</b> destina el "
        f"<b>{fpct(_hdr_top['_pct'], 1, sign=False)}</b> de su PIB al comercio minorista, "
        f"<b>{fnum(_hdr_ratio, 1)}</b> veces el de <b>{_hdr_bot['territori']}</b> "
        f"({fpct(_hdr_bot['_pct'], 1, sign=False)}).",
    ]
    if _esp_pes_hdr is not None:
        _above = int((_d_hdr["_pct"] >= _esp_pes_hdr).sum())
        _below = int((_d_hdr["_pct"] < _esp_pes_hdr).sum())
        _takeaways.append(
            f"<b>{_above}</b> comunidades superan la media española "
            f"(<b>{fpct(_esp_pes_hdr, 1, sign=False)}</b> del PIB) y <b>{_below}</b> quedan por debajo.")
    if _prod_ratio is not None:
        _takeaways.append(
            f"La facturación por ocupado varía <b>{fnum(_prod_ratio, 1)}</b> veces entre "
            f"<b>{_prod_top['territori']}</b> ({fnum(_prod_top['_prod']/1000, 0)} k EUR) "
            f"y <b>{_prod_bot['territori']}</b> ({fnum(_prod_bot['_prod']/1000, 0)} k EUR).")
    _tk_label = "Conclusiones clave"

key_takeaways(_takeaways, label=_tk_label)
freshness_badge("eee_ccaa", st.session_state.lang)

# ─── Nota metodològica (mètode híbrid top-down + bottom-up) ──
_lbl_metode = ("Nota metodològica: com s'estima el VAB del comerç per CCAA"
               if _ca else "Nota metodológica: cómo se estima el VAB del comercio por CCAA")
with highlight_expander(_lbl_metode, expanded=False):
    if _ca:
        st.markdown(
            "La Comptabilitat Regional de l'INE no desglossa el CNAE 47 per comunitats autònomes. "
            "Per estimar el VAB del comerç al detall per CCAA combinem dues fonts: "
            "la **comptabilitat regional d'Eurostat** (VAB de la secció G-I: comerç, transport i hostaleria) "
            "i la **xifra de negoci per CCAA** de l'Enquesta Estructural d'Empreses de l'INE. "
            "El mètode híbrid distribueix el VAB nacional del CNAE 47 entre CCAA ponderant "
            "les quotes regionals de G-I (top-down) amb les quotes de facturació (bottom-up), "
            "garantint que la suma coincideixi amb el total nacional d'Eurostat.")
    else:
        st.markdown(
            "La Contabilidad Regional del INE no desglosa el CNAE 47 por comunidades autónomas. "
            "Para estimar el VAB del comercio minorista por CCAA combinamos dos fuentes: "
            "la **contabilidad regional de Eurostat** (VAB de la sección G-I: comercio, transporte y hostelería) "
            "y la **cifra de negocio por CCAA** de la Encuesta Estructural de Empresas del INE. "
            "El método híbrido distribuye el VAB nacional del CNAE 47 entre CCAA ponderando "
            "las cuotas regionales de G-I (top-down) con las cuotas de facturación (bottom-up), "
            "garantizando que la suma coincida con el total nacional de Eurostat.")

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

# ─── Exhibit 1: pes del CNAE 47 sobre el PIB per CCAA ────────

if "pes_cnae47_pib" in df_ccaa.columns:
    d_pes = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["pes_cnae47_pib"]).copy()
    d_pes = d_pes.sort_values("pes_cnae47_pib", ascending=True)

    if not d_pes.empty:
        d_pes["_pct"] = d_pes["pes_cnae47_pib"] * 100

        esp_pes_row = df_esp[df_esp["any"] == any_sel]
        esp_pes = None
        if not esp_pes_row.empty and pd.notna(esp_pes_row.iloc[0].get("pes_cnae47_pib")):
            esp_pes = esp_pes_row.iloc[0]["pes_cnae47_pib"] * 100

        _ex1_top = d_pes.iloc[-1]
        if _ca:
            exhibit_header(
                1, f"{_ex1_top['territori']} encapçala el pes del comerç sobre el PIB "
                   f"({fpct(_ex1_top['_pct'], 1, sign=False)}) el {int(any_sel)}",
                note="Les barres navy marquen comunitats per sobre de la mitjana espanyola; "
                     "les clares, per sota.",
            )
        else:
            exhibit_header(
                1, f"{_ex1_top['territori']} encabeza el peso del comercio sobre el PIB "
                   f"({fpct(_ex1_top['_pct'], 1, sign=False)}) en {int(any_sel)}",
                note="Las barras navy marcan comunidades por encima de la media española; "
                     "las claras, por debajo.",
            )

        colors_pes = []
        for _, r in d_pes.iterrows():
            if esp_pes is not None and r["_pct"] >= esp_pes:
                colors_pes.append(NAVY)
            else:
                colors_pes.append(G2_P)

        fig_pes = go.Figure()
        fig_pes.add_trace(go.Bar(
            y=d_pes["territori"], x=d_pes["_pct"],
            orientation="h",
            marker_color=colors_pes,
            text=[fpct(v, 1, sign=False) for v in d_pes["_pct"]],
            textposition="outside",
            textfont=dict(size=11, color=G1_P),
        ))

        if esp_pes is not None:
            fig_pes.add_vline(
                x=esp_pes, line_dash="dash", line_color=OCRE, line_width=2,
                annotation_text=f"{'Espanya' if _ca else 'España'}: {fpct(esp_pes, 1, sign=False)}",
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
        if _ca:
            exhibit_header(2, f"Mapa del pes del comerç sobre el PIB per comunitat ({int(any_sel)})")
        else:
            exhibit_header(2, f"Mapa del peso del comercio sobre el PIB por comunidad ({int(any_sel)})")
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

# ─── Exhibit 3: productivitat per CCAA ───────────────────────

d_derived = df_ccaa[df_ccaa["any"] == any_sel].copy()
if "xifra_negoci" in d_derived.columns and "personal_ocupat" in d_derived.columns:
    d_derived["prod_xn_ocupat"] = d_derived["xifra_negoci"] / d_derived["personal_ocupat"]
    d_prod = d_derived.dropna(subset=["prod_xn_ocupat"]).sort_values("prod_xn_ocupat", ascending=True)

    if not d_prod.empty:
        _pr_top = d_prod.iloc[-1]
        if _ca:
            exhibit_header(
                3, f"{_pr_top['territori']} lidera la facturació per ocupat "
                   f"({fnum(_pr_top['prod_xn_ocupat']/1000, 0)} k EUR) el {int(any_sel)}",
                note="La línia ocre marca la mitjana espanyola.",
            )
        else:
            exhibit_header(
                3, f"{_pr_top['territori']} lidera la facturación por ocupado "
                   f"({fnum(_pr_top['prod_xn_ocupat']/1000, 0)} k EUR) en {int(any_sel)}",
                note="La línea ocre marca la media española.",
            )

        fig_prod = go.Figure()
        fig_prod.add_trace(go.Bar(
            y=d_prod["territori"], x=d_prod["prod_xn_ocupat"] / 1000,
            orientation="h", marker_color=NAVY,
            text=[f"{fnum(v/1000, 1)} k" for v in d_prod["prod_xn_ocupat"]],
            textposition="outside", textfont=dict(size=11, color=G1_P),
        ))

        esp_row = df_esp[df_esp["any"] == any_sel]
        if not esp_row.empty and "xifra_negoci" in esp_row.columns:
            esp_p = esp_row["xifra_negoci"].values[0] / esp_row["personal_ocupat"].values[0]
            fig_prod.add_vline(
                x=esp_p / 1000, line_dash="dash", line_color=OCRE, line_width=2,
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

# ─── Taula ────────────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_eee, use_container_width=True)
    st.download_button("CSV", df_eee.to_csv(index=False).encode("utf-8"),
                       "territori_cnae47.csv", "text/csv")

page_meta("INE + Eurostat. Estimació híbrida propia" if _ca
          else "INE + Eurostat. Estimacion híbrida pròpia", st.session_state.lang)

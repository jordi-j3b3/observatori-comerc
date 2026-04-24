"""Pàgina 1: PIB i Valor Afegit Brut (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, PURPLE_LIGHT, RED, BLUE, PALETTE)

inject_css()
t = setup_lang(show_selector=False)

# Dades
@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "pib_vab.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

st.title(t("pib_title"))

if st.session_state.lang == "ca":
    intro(
        "El <strong>Valor Afegit Brut (VAB)</strong> mesura la riquesa que genera el comerç al detall (CNAE 47) "
        "dins l'economia espanyola. Es presenta en termes <strong>nominals</strong> (preus corrents, el que es paga en cada moment) "
        "i <strong>reals</strong> (preus constants de 2002, eliminant l'efecte de la inflació amb l'IPC general). "
        "Aquesta distinció és important: un sector pot semblar que creix en termes nominals quan en realitat només reflecteix "
        "la pujada de preus. El <strong>CAGR</strong> (taxa de creixement anual compost) permet resumir la tendència "
        "de tot el període en una sola xifra anualitzada.<br><br>"
        "<strong>Nota:</strong> Els valors reals prenen com a base l'any 2002 (primer any amb dades d'IPC disponibles). "
        "Per tant, el 2002 el valor real coincideix amb el nominal, i a partir d'aquí la inflació "
        "fa que el nominal creixi per sobre del real."
    )
else:
    intro(
        "El <strong>Valor Añadido Bruto (VAB)</strong> mide la riqueza que genera el comercio minorista (CNAE 47) "
        "dentro de la economía española. Se presenta en términos <strong>nominales</strong> (precios corrientes, lo que se paga en cada momento) "
        "y <strong>reales</strong> (precios constantes de 2002, eliminando el efecto de la inflación con el IPC general). "
        "Esta distinción es importante: un sector puede parecer que crece en términos nominales cuando en realidad solo refleja "
        "la subida de precios. El <strong>CAGR</strong> (tasa de crecimiento anual compuesto) permite resumir la tendencia "
        "de todo el período en una sola cifra anualizada.<br><br>"
        "<strong>Nota:</strong> Los valores reales toman como base el año 2002 (primer año con datos de IPC disponibles). "
        "Por tanto, en 2002 el valor real coincide con el nominal, y a partir de ahí la inflación "
        "hace que el nominal crezca por encima del real."
    )

if df.empty:
    st.warning("No hi ha dades disponibles." if st.session_state.lang == "ca"
               else "No hay datos disponibles.")
    st.stop()

df = df.sort_values("any")

# ─── KPIs superiors ──────────────────────────────────────────

last = df.dropna(subset=["vab_cnae47_corrents"]).iloc[-1]
first = df.dropna(subset=["vab_cnae47_corrents"]).iloc[0]
any_last = int(last["any"])
any_first = int(first["any"])
n_years = any_last - any_first

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(f"VAB nominal ({any_last})", f"{fnum(last['vab_cnae47_corrents'])} M EUR")
with col2:
    if "vab_cnae47_constants" in df.columns:
        last_real = df.dropna(subset=["vab_cnae47_constants"]).iloc[-1]
        st.metric(f"VAB real ({int(last_real['any'])})", f"{fnum(last_real['vab_cnae47_constants'])} M EUR")
with col3:
    if "pes_cnae47" in df.columns:
        pes = df.dropna(subset=["pes_cnae47"]).iloc[-1]
        lbl_pes = "Pes sobre PIB" if st.session_state.lang == "ca" else "Peso sobre PIB"
        st.metric(f"{lbl_pes} ({int(pes['any'])})", fpct(pes['pes_cnae47'] * 100, 2, sign=False))
with col4:
    if n_years > 0:
        cagr_val = cagr(first["vab_cnae47_corrents"], last["vab_cnae47_corrents"], n_years)
        st.metric(f"CAGR {any_first}-{any_last}", fpct(cagr_val, 2))

# ─── Gràfic 1: VAB nominal vs real ────────────────────────────

st.subheader(t("pib_nominal_vs_real"))

fig1 = go.Figure()

if "vab_cnae47_corrents" in df.columns:
    fig1.add_trace(go.Scatter(
        x=df["any"], y=df["vab_cnae47_corrents"],
        mode="lines+markers", name=t("pib_nominal"),
        line=dict(color=RED, width=2.5),
        marker=dict(size=5),
    ))

if "vab_cnae47_constants" in df.columns:
    fig1.add_trace(go.Scatter(
        x=df["any"], y=df["vab_cnae47_constants"],
        mode="lines+markers", name=t("pib_real"),
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=5),
    ))

apply_layout(fig1, yaxis_title=t("pib_meur"), height=450)
st.plotly_chart(fig1, use_container_width=True)
source("INE, Comptabilitat Nacional. Deflactor: IPC general, base 2002. Càlcul propi"
       if st.session_state.lang == "ca" else
       "INE, Contabilidad Nacional. Deflactor: IPC general, base 2002. Cálculo propio")

# ─── Insight PIB ──────────────────────────────────────────────

if "vab_cnae47_constants" in df.columns and "vab_cnae47_corrents" in df.columns:
    df_clean = df.dropna(subset=["vab_cnae47_corrents", "vab_cnae47_constants"])
    if len(df_clean) > 2:
        first_r = df_clean.iloc[0]
        last_r = df_clean.iloc[-1]
        n = int(last_r["any"]) - int(first_r["any"])

        # Variació acumulada total del període
        var_nom_total = ((last_r["vab_cnae47_corrents"] / first_r["vab_cnae47_corrents"]) - 1) * 100
        var_real_total = ((last_r["vab_cnae47_constants"] / first_r["vab_cnae47_constants"]) - 1) * 100
        cagr_nom = cagr(first_r["vab_cnae47_corrents"], last_r["vab_cnae47_corrents"], n)
        cagr_real = cagr(first_r["vab_cnae47_constants"], last_r["vab_cnae47_constants"], n)

        gap = var_nom_total - var_real_total

        if st.session_state.lang == "ca":
            txt = (
                f"Entre {int(first_r['any'])} i {int(last_r['any'])}, el VAB nominal del comerç al detall ha crescut "
                f"un <strong>{fpct(var_nom_total, 1, sign=False)}</strong> (CAGR {fpct(cagr_nom, 2)}), "
                f"però en termes reals la variació ha estat del <strong>{fpct(var_real_total, 1, sign=False)}</strong> "
                f"(CAGR {fpct(cagr_real, 2)}). "
            )
            if gap > 10:
                txt += (
                    f"La diferència de <strong>{fpct(gap, 1, sign=False)}</strong> punts entre ambdues xifres "
                    f"és l'<strong>efecte acumulat de la inflació</strong>: una part important del creixement aparent "
                    f"és simplement pujada de preus. "
                )
            txt += (
                f"Amb un CAGR real del {fpct(cagr_real, 2)}, el sector creix per sota del PIB general espanyol (~2% real), "
                f"confirmant la <strong>pèrdua estructural de pes</strong> del sector en l'economia. "
                f"Factors explicatius: concentració empresarial, digitalització i canvi en patrons de consum."
            )
        else:
            txt = (
                f"Entre {int(first_r['any'])} y {int(last_r['any'])}, el VAB nominal del comercio minorista ha crecido "
                f"un <strong>{fpct(var_nom_total, 1, sign=False)}</strong> (CAGR {fpct(cagr_nom, 2)}), "
                f"pero en términos reales la variación ha sido del <strong>{fpct(var_real_total, 1, sign=False)}</strong> "
                f"(CAGR {fpct(cagr_real, 2)}). "
            )
            if gap > 10:
                txt += (
                    f"La diferencia de <strong>{fpct(gap, 1, sign=False)}</strong> puntos entre ambas cifras "
                    f"es el <strong>efecto acumulado de la inflación</strong>: una parte importante del crecimiento aparente "
                    f"es simplemente subida de precios. "
                )
            txt += (
                f"Con un CAGR real del {fpct(cagr_real, 2)}, el sector crece por debajo del PIB general español (~2% real), "
                f"confirmando la <strong>pérdida estructural de peso</strong> del sector en la economía. "
                f"Factores explicativos: concentración empresarial, digitalización y cambio en patrones de consumo."
            )
        insight(txt)

# ─── Gràfic 2: Pes CNAE 47 sobre PIB ─────────────────────────

if "pes_cnae47" in df.columns:
    st.subheader(t("pib_weight"))

    df_pes = df.dropna(subset=["pes_cnae47"])

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_pes["any"], y=df_pes["pes_cnae47"] * 100,
        marker_color=PURPLE,
        text=[fpct(v, 2, sign=False) for v in df_pes["pes_cnae47"] * 100],
        textposition="outside",
        textfont=dict(size=10),
    ))
    apply_layout(fig2,
        yaxis_title="%",
        yaxis_range=[0, max(df_pes["pes_cnae47"] * 100) * 1.25],
        height=400,
    )
    st.plotly_chart(fig2, use_container_width=True)
    source("INE, Comptabilitat Nacional. Càlcul propi"
           if st.session_state.lang == "ca" else
           "INE, Contabilidad Nacional. Cálculo propio")

# ─── Gràfic 3: Variació anual ─────────────────────────────────

var_cols = [c for c in df.columns if c.startswith("var_")]
if var_cols:
    st.subheader(t("pib_annual_var"))

    fig3 = go.Figure()
    colors = {"var_vab_cnae47_corrents": RED, "var_vab_cnae47_constants": BLUE}
    names = {"var_vab_cnae47_corrents": t("pib_nominal"), "var_vab_cnae47_constants": t("pib_real")}

    for col in var_cols:
        df_var = df.dropna(subset=[col])
        fig3.add_trace(go.Bar(
            x=df_var["any"], y=df_var[col] * 100,
            name=names.get(col, col),
            marker_color=colors.get(col, "#999"),
        ))

    apply_layout(fig3,
        yaxis_title=t("annual_variation") + " (%)",
        barmode="group",
        height=400,
    )
    fig3.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    st.plotly_chart(fig3, use_container_width=True)
    source("INE, Comptabilitat Nacional. Càlcul propi"
           if st.session_state.lang == "ca" else
           "INE, Contabilidad Nacional. Cálculo propio")

# ─── VAB CNAE 47 per CCAA (EEE taula 76817) ─────────────────

_ca = st.session_state.lang == "ca"

st.markdown("---")
st.subheader(t("eee_ccaa_title"))

@st.cache_data(ttl=3600)
def load_eee_ccaa():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "eee_ccaa.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data
def load_geojson():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "geo", "spain_ccaa.geojson")
    with open(p, "r") as f:
        return json.load(f)

df_eee = load_eee_ccaa()

if not df_eee.empty:
    geojson = load_geojson()
    df_eee_ccaa = df_eee[df_eee["territori"] != "espanya"].copy()
    df_eee_esp = df_eee[df_eee["territori"] == "espanya"].copy()

    eee_anys = sorted(df_eee_ccaa["any"].dropna().unique())
    eee_any = st.select_slider(
        t("emp_ccaa_year") + " (EEE)",
        options=eee_anys,
        value=max(eee_anys),
        key="eee_any",
    )

    METRICS_EEE = {
        "vab_estimat": (t("eee_ccaa_vab"), "M EUR"),
        "xifra_negoci": (t("eee_ccaa_xn"), "M EUR"),
        "personal_ocupat": (t("eee_ccaa_personal"), ""),
        "sous_salaris": (t("eee_ccaa_sous"), "M EUR"),
    }

    available = {k: v for k, v in METRICS_EEE.items() if k in df_eee_ccaa.columns}
    sel_metric = st.radio(
        t("eee_ccaa_metric"),
        list(available.keys()),
        format_func=lambda x: available[x][0],
        horizontal=True,
    )

    d_yr = df_eee_ccaa[df_eee_ccaa["any"] == eee_any].dropna(subset=[sel_metric]).copy()

    if not d_yr.empty:
        d_yr = d_yr.sort_values(sel_metric, ascending=True)
        lbl, unit = available[sel_metric]

        if unit == "M EUR":
            d_yr["_display"] = d_yr[sel_metric] / 1e6
            txt_vals = [f"{fnum(v / 1e6)} M" for v in d_yr[sel_metric]]
            ax_title = f"{lbl} (M EUR)"
        else:
            d_yr["_display"] = d_yr[sel_metric]
            txt_vals = [fnum(v) for v in d_yr[sel_metric]]
            ax_title = lbl

        fig_eee = go.Figure()
        fig_eee.add_trace(go.Bar(
            y=d_yr["territori"], x=d_yr["_display"],
            orientation="h",
            marker_color=PURPLE_LIGHT,
            text=txt_vals,
            textposition="outside",
            textfont=dict(size=11),
        ))

        esp_val = df_eee_esp[df_eee_esp["any"] == eee_any][sel_metric].values
        if len(esp_val) > 0:
            n_ccaa_eee = len(d_yr)
            if n_ccaa_eee > 0:
                avg_val = esp_val[0] / n_ccaa_eee
                if unit == "M EUR":
                    avg_disp = avg_val / 1e6
                    avg_txt = f"{'Mitjana' if _ca else 'Media'}: {fnum(avg_val / 1e6)} M"
                else:
                    avg_disp = avg_val
                    avg_txt = f"{'Mitjana' if _ca else 'Media'}: {fnum(avg_val)}"
                fig_eee.add_vline(
                    x=avg_disp, line_dash="dash", line_color=RED, line_width=2,
                    annotation_text=avg_txt,
                    annotation_position="top right",
                )

        apply_layout(fig_eee,
            title=f"{lbl} ({int(eee_any)})",
            xaxis_title=ax_title,
            height=max(450, len(d_yr) * 32 + 100),
            margin=dict(l=200, r=120, t=50, b=50),
        )
        st.plotly_chart(fig_eee, use_container_width=True)
        source("INE, Estadística Estructural d'Empreses (EEE). Càlcul propi" if _ca
               else "INE, Estadística Estructural de Empresas (EEE). Cálculo propio")

    # Mapa coroplet VAB estimat
    if "vab_estimat" in df_eee_ccaa.columns:
        st.subheader(t("eee_ccaa_vab") + f" ({int(eee_any)})")
        d_map_eee = df_eee_ccaa[df_eee_ccaa["any"] == eee_any].dropna(subset=["vab_estimat"]).copy()
        d_map_eee["vab_meur"] = d_map_eee["vab_estimat"] / 1e6

        if not d_map_eee.empty:
            zmin_eee = df_eee_ccaa["vab_estimat"].min() / 1e6
            zmax_eee = df_eee_ccaa["vab_estimat"].max() / 1e6

            fig_vab_map = go.Figure(go.Choroplethmap(
                geojson=geojson,
                locations=d_map_eee["territori"],
                featureidkey="properties.territori",
                z=d_map_eee["vab_meur"],
                zmin=zmin_eee,
                zmax=zmax_eee,
                colorscale=[
                    [0, "#e8f0fe"],
                    [0.15, "#a8c8e8"],
                    [0.35, "#5a9fd4"],
                    [0.55, "#0055a4"],
                    [0.75, "#003d7a"],
                    [1, "#001d3d"],
                ],
                colorbar=dict(title="M EUR", thickness=15),
                marker=dict(line=dict(width=1.5, color="white")),
                text=d_map_eee["territori"],
                hovertemplate="<b>%{text}</b><br>VAB: %{z:,.0f} M EUR<extra></extra>",
            ))
            fig_vab_map.update_layout(
                map=dict(style="white-bg", center=dict(lat=39.5, lon=-3.5), zoom=4.8),
                height=700,
                margin=dict(l=0, r=0, t=10, b=10),
            )
            st.plotly_chart(fig_vab_map, use_container_width=True)
            source("INE, EEE Sector Comercio (taula 76817) i EEE CNAE 47 (taula 36194). Càlcul propi" if _ca
                   else "INE, EEE Sector Comercio (tabla 76817) y EEE CNAE 47 (tabla 36194). Cálculo propio")

    # Productivitat per CCAA
    d_derived = df_eee_ccaa[df_eee_ccaa["any"] == eee_any].copy()
    if "xifra_negoci" in d_derived.columns and "personal_ocupat" in d_derived.columns:
        d_derived["prod_xn_ocupat"] = d_derived["xifra_negoci"] / d_derived["personal_ocupat"]

        st.subheader(t("eee_ccaa_prod") + f" ({int(eee_any)})")
        d_prod = d_derived.dropna(subset=["prod_xn_ocupat"]).sort_values("prod_xn_ocupat", ascending=True)

        fig_prod = go.Figure()
        fig_prod.add_trace(go.Bar(
            y=d_prod["territori"], x=d_prod["prod_xn_ocupat"] / 1000,
            orientation="h",
            marker_color=PURPLE_LIGHT,
            text=[f"{fnum(v/1000, 1)} k" for v in d_prod["prod_xn_ocupat"]],
            textposition="outside",
            textfont=dict(size=11),
        ))

        esp_prod = df_eee_esp[df_eee_esp["any"] == eee_any]
        if not esp_prod.empty and "xifra_negoci" in esp_prod.columns and "personal_ocupat" in esp_prod.columns:
            esp_p = esp_prod["xifra_negoci"].values[0] / esp_prod["personal_ocupat"].values[0]
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
        source("INE, EEE Sector Comercio. Càlcul propi" if _ca
               else "INE, EEE Sector Comercio. Cálculo propio")

    # Salari mitjà per CCAA
    if "sous_salaris" in d_derived.columns and "personal_ocupat" in d_derived.columns:
        d_derived["sal_med"] = d_derived["sous_salaris"] / d_derived["personal_ocupat"]

        st.subheader(t("eee_ccaa_sal_med") + f" ({int(eee_any)})")
        d_sal = d_derived.dropna(subset=["sal_med"]).sort_values("sal_med", ascending=True)

        fig_sal = go.Figure()
        fig_sal.add_trace(go.Bar(
            y=d_sal["territori"], x=d_sal["sal_med"],
            orientation="h",
            marker_color=PURPLE_LIGHT,
            text=[f"{fnum(v)} EUR" for v in d_sal["sal_med"]],
            textposition="outside",
            textfont=dict(size=11),
        ))

        esp_s = df_eee_esp[df_eee_esp["any"] == eee_any]
        if not esp_s.empty and "sous_salaris" in esp_s.columns and "personal_ocupat" in esp_s.columns:
            sal_esp = esp_s["sous_salaris"].values[0] / esp_s["personal_ocupat"].values[0]
            fig_sal.add_vline(
                x=sal_esp, line_dash="dash", line_color=RED, line_width=2,
                annotation_text=f"{'Espanya' if _ca else 'España'}: {fnum(sal_esp)} EUR",
                annotation_position="top right",
            )

        apply_layout(fig_sal,
            xaxis_title="EUR / ocupat" if _ca else "EUR / ocupado",
            height=max(450, len(d_sal) * 32 + 100),
            margin=dict(l=200, r=100, t=50, b=50),
        )
        st.plotly_chart(fig_sal, use_container_width=True)
        source("INE, EEE Sector Comercio. Càlcul propi" if _ca
               else "INE, EEE Sector Comercio. Cálculo propio")

    # Insight EEE CCAA
    if "vab_estimat" in df_eee_ccaa.columns:
        d_last = df_eee_ccaa[df_eee_ccaa["any"] == max(eee_anys)].dropna(subset=["vab_estimat"])
        if not d_last.empty:
            top3 = d_last.nlargest(3, "vab_estimat")
            top_names = ", ".join(top3["territori"].values[:2]) + f" {'i' if _ca else 'y'} " + top3["territori"].values[2]
            top_pct = top3["vab_estimat"].sum() / d_last["vab_estimat"].sum() * 100
            if _ca:
                insight(
                    f"Les tres CCAA amb més VAB estimat del CNAE 47 ({int(max(eee_anys))}) són "
                    f"<strong>{top_names}</strong>, que concentren el <strong>{fpct(top_pct, 1, sign=False)}</strong> "
                    f"del total. "
                    f"Les diferències en productivitat per ocupat i salari mitjà entre comunitats reflecteixen "
                    f"l'heterogeneïtat del sector: cost de vida, estructura comercial (gran superfície vs. petit comerç) "
                    f"i especialització territorial condicionen els resultats."
                )
            else:
                insight(
                    f"Las tres CCAA con mayor VAB estimado del CNAE 47 ({int(max(eee_anys))}) son "
                    f"<strong>{top_names}</strong>, que concentran el <strong>{fpct(top_pct, 1, sign=False)}</strong> "
                    f"del total. "
                    f"Las diferencias en productividad por ocupado y salario medio entre comunidades reflejan "
                    f"la heterogeneidad del sector: coste de vida, estructura comercial (gran superficie vs. pequeño comercio) "
                    f"y especialización territorial condicionan los resultados."
                )

else:
    st.info("No hi ha dades EEE per CCAA disponibles." if _ca
            else "No hay datos EEE por CCAA disponibles.")

# ─── Taula descarregable ──────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "pib_vab_cnae47.csv", "text/csv")

    if not df_eee.empty:
        st.markdown("---")
        st.markdown("**EEE CNAE 47 per CCAA**" if _ca else "**EEE CNAE 47 por CCAA**")
        st.dataframe(df_eee, use_container_width=True)
        st.download_button("CSV (EEE CCAA)", df_eee.to_csv(index=False).encode("utf-8"),
                           "eee_cnae47_ccaa.csv", "text/csv")

page_meta("INE, Comptabilitat Nacional d'Espanya" if st.session_state.lang == "ca"
         else "INE, Contabilidad Nacional de España", st.session_state.lang)

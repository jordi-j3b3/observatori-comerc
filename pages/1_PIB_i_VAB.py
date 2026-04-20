"""Pàgina 1: PIB i Valor Afegit Brut (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, BLUE)

st.set_page_config(page_title="PIB i VAB", page_icon="📊", layout="wide")
inject_css()
t = setup_lang()

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

# ─── Taula descarregable ──────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "pib_vab_cnae47.csv", "text/csv")

page_meta("INE, Comptabilitat Nacional d'Espanya" if st.session_state.lang == "ca"
         else "INE, Contabilidad Nacional de España", st.session_state.lang)

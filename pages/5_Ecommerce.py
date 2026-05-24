"""Pàgina 5: Digitalització del comerç (CNAE 47) — e-commerce (CNMC) + adopció TIC (Eurostat)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, RED, GREEN, GRAY, BRAND, ORANGE)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"

_DIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "digitalitzacio_comerc.csv")


@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "ecommerce.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_dig(sig):  # 'sig' (mida+data del CSV) trenca la cache quan canvien les dades
    if os.path.exists(_DIG_PATH):
        return pd.read_csv(_DIG_PATH)
    return pd.DataFrame()


df = load_data()
_dig_sig = ((os.path.getsize(_DIG_PATH), int(os.path.getmtime(_DIG_PATH)))
            if os.path.exists(_DIG_PATH) else (0, 0))
df_dig = load_dig(_dig_sig)

st.title("Digitalització del comerç" if _ca else "Digitalización del comercio")
intro(
    ("La <strong>digitalització</strong> del comerç al detall, en dues mirades: el "
     "<strong>comerç electrònic</strong> (volum de negoci online del sector, dades CNMC) i "
     "l'<strong>adopció de tecnologies digitals</strong> per les empreses del sector "
     "—e-commerce, intel·ligència artificial i núvol— comparada amb la UE-27 (Eurostat)."
     if _ca else
     "La <strong>digitalización</strong> del comercio minorista, en dos miradas: el "
     "<strong>comercio electrónico</strong> (volumen de negocio online del sector, datos CNMC) y "
     "la <strong>adopción de tecnologías digitales</strong> por las empresas del sector "
     "—e-commerce, inteligencia artificial y nube— comparada con la UE-27 (Eurostat).")
)

tab_ec, tab_dig = st.tabs([
    "E-commerce",
    ("Digitalització" if _ca else "Digitalización"),
])

# ════════════════════════════════════════════════════════════
# TAB 1: E-COMMERCE (volum de negoci online, CNMC)
# ════════════════════════════════════════════════════════════
with tab_ec:
    if df.empty:
        st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    else:
        df = df.sort_values("any")

        if _ca:
            intro(
                "El <strong>comerç electrònic</strong> és el canal de venda amb major creixement del sector del detall. "
                "Analitzem el volum de negoci online de les empreses CNAE 47 i el comparem amb el total a Espanya. "
                "El <strong>pes sobre el total</strong> indica quina proporció de l'e-commerce correspon al comerç "
                "al detall — si baixa, vol dir que altres sectors (serveis, turisme, continguts) creixen encara més ràpid."
            )
        else:
            intro(
                "El <strong>comercio electrónico</strong> es el canal de venta con mayor crecimiento del sector minorista. "
                "Analizamos el volumen de negocio online de las empresas CNAE 47 y lo comparamos con el total en España. "
                "El <strong>peso sobre el total</strong> indica qué proporción del e-commerce corresponde al comercio "
                "minorista — si baja, significa que otros sectores (servicios, turismo, contenidos) crecen aún más rápido."
            )

        # ─── KPIs ────────────────────────────────────────────
        if "ecommerce_cnae47_eur" in df.columns:
            first = df.dropna(subset=["ecommerce_cnae47_eur"]).iloc[0]
            last = df.dropna(subset=["ecommerce_cnae47_eur"]).iloc[-1]
            n_years = int(last["any"]) - int(first["any"])
            multiplicador = last["ecommerce_cnae47_eur"] / first["ecommerce_cnae47_eur"]
            cagr_ec = cagr(first["ecommerce_cnae47_eur"], last["ecommerce_cnae47_eur"], n_years)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"E-commerce CNAE 47 ({int(last['any'])})",
                        f"{fnum(last['ecommerce_cnae47_eur'] / 1e9, 1)} Md EUR")
            col2.metric(f"Multiplicador {int(first['any'])}-{int(last['any'])}",
                        f"x{fnum(multiplicador)}")
            col3.metric("CAGR", fpct(cagr_ec))
            if "pes_cnae47_ecommerce" in df.columns:
                col4.metric(f"{'Pes sobre total' if _ca else 'Peso sobre total'} ({int(last['any'])})",
                            fpct(last['pes_cnae47_ecommerce'] * 100, 1, sign=False))

        # ─── Nota metodològica any parcial ───────────────────
        if len(df) >= 2:
            _last_yr = df.iloc[-1]
            _prev_yr = df.iloc[-2]
            if "ecommerce_total_eur" in df.columns:
                _ratio = _last_yr["ecommerce_total_eur"] / _prev_yr["ecommerce_total_eur"]
                if _ratio < 0.85:
                    _any_parcial = int(_last_yr["any"])
                    if _ca:
                        st.warning(
                            f"**Nota metodològica:** Les dades de {_any_parcial} són provisionals i corresponen "
                            f"a un any incomplet (dades publicades fins al moment per la CNMC). "
                            f"La caiguda aparent respecte a {_any_parcial - 1} reflecteix la manca de dades dels últims trimestres, "
                            f"no una reducció real del volum de negoci."
                        )
                    else:
                        st.warning(
                            f"**Nota metodológica:** Los datos de {_any_parcial} son provisionales y corresponden "
                            f"a un año incompleto (datos publicados hasta el momento por la CNMC). "
                            f"La caída aparente respecto a {_any_parcial - 1} refleja la falta de datos de los últimos trimestres, "
                            f"no una reducción real del volumen de negocio."
                        )

        # ─── Gràfic 1: Volum e-commerce ──────────────────────
        st.subheader(t("ec_volume"))
        fig = go.Figure()
        if "ecommerce_total_eur" in df.columns:
            fig.add_trace(go.Bar(
                x=df["any"], y=df["ecommerce_total_eur"] / 1e9,
                name=t("ec_total"), marker_color=GRAY))
        if "ecommerce_cnae47_eur" in df.columns:
            fig.add_trace(go.Bar(
                x=df["any"], y=df["ecommerce_cnae47_eur"] / 1e9,
                name=t("ec_cnae47"), marker_color=PURPLE))
        apply_layout(fig,
            yaxis_title=("Milers de milions EUR" if _ca else "Miles de millones EUR"),
            barmode="group", height=450)
        st.plotly_chart(fig, use_container_width=True)
        source("CNMC, Comerç electrònic a Espanya" if _ca
               else "CNMC, Comercio electrónico en España")

        # ─── Gràfic 2: Pes CNAE 47 sobre total ───────────────
        if "pes_cnae47_ecommerce" in df.columns:
            st.subheader(t("ec_weight"))
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df["any"], y=df["pes_cnae47_ecommerce"] * 100,
                mode="lines+markers",
                line=dict(color=PURPLE, width=3), marker=dict(size=8),
                fill="tozeroy", fillcolor="rgba(93,79,255,0.08)"))
            apply_layout(fig2,
                yaxis_title=("% sobre total e-commerce" if _ca else "% sobre total e-commerce"),
                height=400)
            st.plotly_chart(fig2, use_container_width=True)
            source("CNMC. Càlcul propi" if _ca else "CNMC. Cálculo propio")

        # ─── Gràfic 3: Creixement interanual ─────────────────
        if "ecommerce_cnae47_eur" in df.columns and len(df) > 1:
            df["creix_ec"] = df["ecommerce_cnae47_eur"].pct_change() * 100
            st.subheader("Creixement interanual e-commerce CNAE 47" if _ca
                         else "Crecimiento interanual e-commerce CNAE 47")
            fig3 = go.Figure()
            df_creix = df.dropna(subset=["creix_ec"])
            colors = [GREEN if v >= 0 else RED for v in df_creix["creix_ec"]]
            fig3.add_trace(go.Bar(
                x=df_creix["any"], y=df_creix["creix_ec"],
                marker_color=colors,
                text=[fpct(v) for v in df_creix["creix_ec"]],
                textposition="outside", textfont=dict(size=11)))
            apply_layout(fig3,
                yaxis_title=("Variació interanual (%)" if _ca else "Variación interanual (%)"),
                height=400)
            fig3.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
            st.plotly_chart(fig3, use_container_width=True)
            source("CNMC. Càlcul propi" if _ca else "CNMC. Cálculo propio")

        # ─── Insight e-commerce ──────────────────────────────
        if "ecommerce_cnae47_eur" in df.columns and "pes_cnae47_ecommerce" in df.columns:
            pes_first = df.dropna(subset=["pes_cnae47_ecommerce"]).iloc[0]["pes_cnae47_ecommerce"] * 100
            pes_last = df.dropna(subset=["pes_cnae47_ecommerce"]).iloc[-1]["pes_cnae47_ecommerce"] * 100
            pes_var = pes_last - pes_first
            if _ca:
                txt = (
                    f"El comerç electrònic del CNAE 47 ha multiplicat el seu volum per <strong>x{fnum(multiplicador)}</strong> "
                    f"en {n_years} anys, amb un CAGR del <strong>{fpct(cagr_ec)}</strong>. "
                    f"El pes del detall sobre el total d'e-commerce "
                    f"ha passat del {fpct(pes_first, 1, sign=False)} al {fpct(pes_last, 1, sign=False)} ({fpct(pes_var)})."
                )
                if pes_var < 0:
                    txt += (
                        "Això indica que <strong>altres sectors han crescut encara més ràpidament</strong> en el canal digital. "
                        "El comerç al detall, tot i ser un adoptant significatiu, "
                        "perd quota relativa davant serveis, turisme i sectors amb major marge digital. "
                        "La digitalització del sector ha estat reactiva (accelerada per la pandèmia) "
                        "més que proactiva, cosa que explica la pèrdua de quota relativa."
                    )
                else:
                    txt += (
                        "Això indica que <strong>el comerç al detall guanya quota en el canal digital</strong> "
                        "per sobre d'altres sectors, consolidant la seva posició en l'ecosistema d'e-commerce."
                    )
            else:
                txt = (
                    f"El comercio electrónico del CNAE 47 ha multiplicado su volumen por <strong>x{fnum(multiplicador)}</strong> "
                    f"en {n_years} años, con un CAGR del <strong>{fpct(cagr_ec)}</strong>. "
                    f"El peso del minorista sobre el total de e-commerce "
                    f"ha pasado del {fpct(pes_first, 1, sign=False)} al {fpct(pes_last, 1, sign=False)} ({fpct(pes_var)})."
                )
                if pes_var < 0:
                    txt += (
                        "Esto indica que <strong>otros sectores han crecido aún más rápidamente</strong> en el canal digital. "
                        "El comercio minorista, aun siendo un adoptante significativo, "
                        "pierde cuota relativa frente a servicios, turismo y sectores con mayor margen digital. "
                        "La digitalización del sector ha sido reactiva (acelerada por la pandemia) "
                        "más que proactiva, lo que explica la pérdida de cuota relativa."
                    )
                else:
                    txt += (
                        "Esto indica que <strong>el minorista gana cuota en el canal digital</strong> "
                        "por encima de otros sectores, consolidando su posición en el ecosistema de e-commerce."
                    )
            insight(txt)

        with st.expander(t("download_data")):
            st.dataframe(df, use_container_width=True)
            st.download_button("CSV", df.to_csv(index=False).encode("utf-8"),
                               "ecommerce_cnae47.csv", "text/csv")

# ════════════════════════════════════════════════════════════
# TAB 2: DIGITALITZACIÓ (adopció TIC: e-commerce, IA, núvol — Eurostat)
# ════════════════════════════════════════════════════════════
with tab_dig:
    if df_dig.empty:
        st.info("Sense dades de digitalització disponibles." if _ca
                else "Sin datos de digitalización disponibles.")
    else:
        # (tech_ca, tech_es, color) en ordre de presentació
        _TECHS = [
            ("Venda electrònica", "Venta electrónica", BRAND),
            ("Intel·ligència artificial", "Inteligencia artificial", ORANGE),
            ("Núvol (cloud)", "Nube (cloud)", GREEN),
        ]

        def _last(tech_ca, p):
            s = df_dig[(df_dig["tech"] == tech_ca) & (df_dig["pais_codi"] == p)].sort_values("any")
            return (None, None) if s.empty else (int(s.iloc[-1]["any"]), float(s.iloc[-1]["pct"]))

        intro(
            ("Quina part de les <strong>empreses de comerç</strong> (CNAE 47) adopta cada tecnologia digital "
             "—venda electrònica, <strong>intel·ligència artificial</strong> i <strong>núvol</strong>— "
             "segons l'enquesta TIC d'Eurostat, comparat amb la UE-27. És la cara de l'<strong>oferta</strong>: "
             "no quant es ven online, sinó quantes empreses tenen la capacitat digital. "
             "<em>Nota: IA i núvol cobreixen empreses de 10 o més ocupats (exclou micro i autònoms).</em>"
             if _ca else
             "Qué parte de las <strong>empresas de comercio</strong> (CNAE 47) adopta cada tecnología digital "
             "—venta electrónica, <strong>inteligencia artificial</strong> y <strong>nube</strong>— "
             "según la encuesta TIC de Eurostat, comparado con la UE-27. Es la cara de la <strong>oferta</strong>: "
             "no cuánto se vende online, sino cuántas empresas tienen la capacidad digital. "
             "<em>Nota: IA y nube cubren empresas de 10 o más ocupados (excluye micro y autónomos).</em>")
        )

        dc1, dc2, dc3 = st.columns(3)
        for _col_box, (_tca, _tes, _) in zip([dc1, dc2, dc3], _TECHS):
            _yr, _v = _last(_tca, "ES")
            _, _vu = _last(_tca, "EU27_2020")
            _col_box.metric((_tca if _ca else _tes), fpct(_v, 1, sign=False),
                            help=f"ES {_yr} · UE-27 {fpct(_vu, 1, sign=False)}")

        _sub_comp, _sub_evo = st.tabs([
            ("Comparativa ES vs UE-27" if _ca else "Comparativa ES vs UE-27"),
            ("Evolució a Espanya" if _ca else "Evolución en España"),
        ])

        with _sub_comp:
            _labels = [(_tca if _ca else _tes) for _tca, _tes, _ in _TECHS]
            figb = go.Figure()
            figb.add_trace(go.Bar(x=_labels, y=[_last(t2[0], "ES")[1] for t2 in _TECHS],
                                  name=("Espanya" if _ca else "España"), marker_color=BRAND))
            figb.add_trace(go.Bar(x=_labels, y=[_last(t2[0], "EU27_2020")[1] for t2 in _TECHS],
                                  name="UE-27", marker_color=GRAY))
            apply_layout(figb, yaxis_title="% d'empreses" if _ca else "% de empresas",
                         height=380, barmode="group")
            st.plotly_chart(figb, use_container_width=True)
            source("Eurostat, enquesta TIC (isoc_ec_eseln2 · isoc_eb_ain2 · isoc_cicce_usen2), CNAE G47")

        with _sub_evo:
            figl = go.Figure()
            for _tca, _tes, _c in _TECHS:
                _d = df_dig[(df_dig["tech"] == _tca) & (df_dig["pais_codi"] == "ES")].sort_values("any")
                figl.add_trace(go.Scatter(
                    x=_d["any"], y=_d["pct"], mode="lines+markers", name=(_tca if _ca else _tes),
                    line=dict(color=_c, width=2.5), marker=dict(size=4)))
            apply_layout(figl, yaxis_title="% d'empreses" if _ca else "% de empresas", height=380)
            st.plotly_chart(figl, use_container_width=True)
            source("Eurostat, enquesta TIC, CNAE G47")

        _ec_es, _ec_ue = _last("Venda electrònica", "ES")[1], _last("Venda electrònica", "EU27_2020")[1]
        _ai_es, _ai_ue = _last("Intel·ligència artificial", "ES")[1], _last("Intel·ligència artificial", "EU27_2020")[1]
        _ai_0 = df_dig[(df_dig["tech"] == "Intel·ligència artificial") & (df_dig["pais_codi"] == "ES")].sort_values("any")
        _ai_first = (None, None) if _ai_0.empty else (int(_ai_0.iloc[0]["any"]), float(_ai_0.iloc[0]["pct"]))
        _cl_es, _cl_ue = _last("Núvol (cloud)", "ES")[1], _last("Núvol (cloud)", "EU27_2020")[1]
        insight(
            (f"La digitalització del comerç espanyol és <strong>desigual</strong>. En <strong>venda electrònica</strong> "
             f"Espanya supera la UE ({fpct(_ec_es, 1, sign=False)} vs {fpct(_ec_ue, 1, sign=False)}): el canal de venda "
             f"es va digitalitzar aviat. Però en la <strong>infraestructura</strong> queda enrere: el "
             f"<strong>núvol</strong> ({fpct(_cl_es, 1, sign=False)}) està molt per sota de la UE ({fpct(_cl_ue, 1, sign=False)}). "
             f"La <strong>IA</strong> irromp de pressa —del {fpct(_ai_first[1], 1, sign=False)} ({_ai_first[0]}) al "
             f"{fpct(_ai_es, 1, sign=False)} ({_last('Intel·ligència artificial', 'ES')[0]})—, encara just per sota de la UE "
             f"({fpct(_ai_ue, 1, sign=False)}). Lectura: el comerç espanyol sap <em>vendre</em> online, però va més lent "
             f"a adoptar la <em>tecnologia de fons</em> que decideix qui competeix en els canals nous."
             if _ca else
             f"La digitalización del comercio español es <strong>desigual</strong>. En <strong>venta electrónica</strong> "
             f"España supera a la UE ({fpct(_ec_es, 1, sign=False)} vs {fpct(_ec_ue, 1, sign=False)}): el canal de venta "
             f"se digitalizó pronto. Pero en la <strong>infraestructura</strong> se queda atrás: la "
             f"<strong>nube</strong> ({fpct(_cl_es, 1, sign=False)}) está muy por debajo de la UE ({fpct(_cl_ue, 1, sign=False)}). "
             f"La <strong>IA</strong> irrumpe rápido —del {fpct(_ai_first[1], 1, sign=False)} ({_ai_first[0]}) al "
             f"{fpct(_ai_es, 1, sign=False)} ({_last('Intel·ligència artificial', 'ES')[0]})—, aún justo por debajo de la UE "
             f"({fpct(_ai_ue, 1, sign=False)}). Lectura: el comercio español sabe <em>vender</em> online, pero va más lento "
             f"en adoptar la <em>tecnología de fondo</em> que decide quién compite en los canales nuevos.")
        )

        with st.expander(t("download_data")):
            st.dataframe(df_dig, use_container_width=True)
            st.download_button("CSV", df_dig.to_csv(index=False).encode("utf-8"),
                               "digitalitzacio_comerc.csv", "text/csv", key="dl_dig")

page_meta("CNMC + Eurostat (enquesta TIC)" if _ca
          else "CNMC + Eurostat (encuesta TIC)", st.session_state.lang)

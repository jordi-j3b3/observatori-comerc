"""Pàgina 3: Ocupació (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout, highlight_expander,
                   PURPLE, RED, BLUE, ORANGE,
                   BRAND, BRAND_DEEP, YELLOW)

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

        _lbl_hpt_exp = ("Veure hores anuals per treballador"
                        if _ca else
                        "Ver horas anuales por trabajador")
        with highlight_expander(_lbl_hpt_exp, expanded=False):
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

        # Detecció dinàmica: intensificació (hores creixen més que ocupació)
        # vs extensificació (ocupació creix més que hores).
        _intensifica = var_h > var_ocu
        _hpt_creix = hpt_last > hpt_first
        if _ca:
            if _intensifica:
                titol_bloc = "<strong>Més hores, no més contractació.</strong>"
                lectura = (
                    f"El sector ha optat per <strong>intensificar la jornada</strong> de la plantilla "
                    f"existent abans que crear nous llocs de treball. La reforma laboral de 2022 — que va "
                    f"limitar la temporalitat i va impulsar la conversió a contractes indefinits — ha "
                    f"contribuït a aquest patró: menys rotació i més hores per treballador."
                )
            else:
                titol_bloc = "<strong>Més contractació, menys intensitat.</strong>"
                lectura = (
                    f"El sector ha optat per <strong>ampliar la plantilla</strong> més que intensificar "
                    f"la jornada existent: la creació de nous llocs de treball ha anat per davant de "
                    f"l'augment d'hores per treballador."
                )
            verb_hpt = "ha passat" if _hpt_creix else "ha passat (a la baixa)"
            txt = (
                f"{titol_bloc} "
                f"Entre {any_f} i {any_l}, el personal ocupat ha variat un {fpct(var_ocu)}, "
                f"mentre que les hores treballades han variat un {fpct(var_h)}. "
                f"{lectura} "
                f"La ràtio d'hores per treballador {verb_hpt} de {fnum(hpt_first)} a {fnum(hpt_last)} h/any."
                f"<br><br>"
                f"<strong>La contractació segueix el valor afegit, no la facturació.</strong> "
                f"El valor afegit i el personal ocupat mostren trajectòries paral·leles, "
                f"mentre que la xifra de negoci creix a un ritme diferent. "
                f"Això suggereix que les decisions de contractació responen al <strong>valor net generat</strong> "
                f"(descomptant costos intermedis), no al volum de vendes brut."
            )
        else:
            if _intensifica:
                titol_bloc = "<strong>Más horas, no más contratación.</strong>"
                lectura = (
                    f"El sector ha optado por <strong>intensificar la jornada</strong> de la plantilla "
                    f"existente antes que crear nuevos puestos de trabajo. La reforma laboral de 2022 — "
                    f"que limitó la temporalidad e impulsó la conversión a contratos indefinidos — ha "
                    f"contribuido a este patrón: menos rotación y más horas por trabajador."
                )
            else:
                titol_bloc = "<strong>Más contratación, menos intensidad.</strong>"
                lectura = (
                    f"El sector ha optado por <strong>ampliar la plantilla</strong> más que intensificar "
                    f"la jornada existente: la creación de nuevos puestos ha ido por delante del "
                    f"aumento de horas por trabajador."
                )
            verb_hpt = "ha pasado" if _hpt_creix else "ha pasado (a la baja)"
            txt = (
                f"{titol_bloc} "
                f"Entre {any_f} y {any_l}, el personal ocupado ha variado un {fpct(var_ocu)}, "
                f"mientras que las horas trabajadas han variado un {fpct(var_h)}. "
                f"{lectura} "
                f"La ratio de horas por trabajador {verb_hpt} de {fnum(hpt_first)} a {fnum(hpt_last)} h/año."
                f"<br><br>"
                f"<strong>La contratación sigue al valor añadido, no a la facturación.</strong> "
                f"El valor añadido y el personal ocupado muestran trayectorias paralelas, "
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
        _te_puja = te_last > te_first
        if _ca:
            if _te_puja:
                lectura_te = (
                    "<strong>Que pugi indica que les empreses supervivents són més grans</strong>: "
                    "la concentració empresarial elimina petits comerços i deixa al sector "
                    "empreses amb plantilles més àmplies. Això té implicacions per a la "
                    "<strong>qualitat de l'ocupació</strong>: les empreses més grans solen "
                    "oferir millors condicions laborals, convenis col·lectius més favorables "
                    "i més oportunitats de promoció interna."
                )
            else:
                lectura_te = (
                    "<strong>Que baixi indica una atomització creixent</strong>: el sector guanya "
                    "empreses més que treballadors, reflectint l'entrada de microempreses, autònoms "
                    "i nous formats sense plantilla. Aquesta dinàmica pot indicar dinamisme "
                    "emprenedor però redueix l'escala mitjana i el poder negociador."
                )
            insight(
                f"La ràtio de treballadors per empresa ha passat de <strong>{fnum(te_first, 1)}</strong> "
                f"({int(merged.iloc[0]['any'])}) a <strong>{fnum(te_last, 1)}</strong> "
                f"({int(merged.iloc[-1]['any'])}). {lectura_te}"
            )
        else:
            if _te_puja:
                lectura_te = (
                    "<strong>Que suba indica que las empresas supervivientes son más grandes</strong>: "
                    "la concentración empresarial elimina pequeños comercios y deja al sector "
                    "empresas con plantillas más amplias. Esto tiene implicaciones para la "
                    "<strong>calidad del empleo</strong>: las empresas más grandes suelen ofrecer "
                    "mejores condiciones laborales, convenios colectivos más favorables y más "
                    "oportunidades de promoción interna."
                )
            else:
                lectura_te = (
                    "<strong>Que baje indica una atomización creciente</strong>: el sector gana "
                    "empresas más que trabajadores, reflejando la entrada de microempresas, "
                    "autónomos y nuevos formatos sin plantilla. Esta dinámica puede indicar "
                    "dinamismo emprendedor, pero reduce la escala media y el poder negociador."
                )
            insight(
                f"La ratio de trabajadores por empresa ha pasado de <strong>{fnum(te_first, 1)}</strong> "
                f"({int(merged.iloc[0]['any'])}) a <strong>{fnum(te_last, 1)}</strong> "
                f"({int(merged.iloc[-1]['any'])}). {lectura_te}"
            )
else:
    st.info("Dades insuficients per calcular treballadors per empresa." if _ca
            else "Datos insuficientes para calcular trabajadores por empresa.")

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
    st.header(("Salaris: comerç vs total economia espanyola"
                if _ca else "Salarios: comercio vs total economía española"))

    if _ca:
        st.markdown(
            "Per situar el sector en el conjunt de l'economia, fem servir l'**Enquesta Anual "
            "d'Estructura Salarial (EAES, taula INE 28185)**, que mesura el salari brut anual "
            "per treballador a jornada equivalent i és **consistent entre sectors**. "
            "Permet comparar el comerç amb la mitjana de l'economia espanyola."
        )
    else:
        st.markdown(
            "Para situar el sector en el conjunto de la economía, usamos la **Encuesta Anual "
            "de Estructura Salarial (EAES, tabla INE 28185)**, que mide el salario bruto anual "
            "por trabajador a jornada equivalente y es **consistente entre sectores**. "
            "Permite comparar el comercio con la media de la economía española."
        )

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

# ─── Qui treballa al comerç: sexe i edat (Eurostat EU-LFS) ───

_OCU_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "ocupacio_comerc.csv")

@st.cache_data(ttl=3600)
def load_ocu_sx(sig):  # 'sig' (mida+data del CSV) trenca la cache quan canvien les dades
    if os.path.exists(_OCU_PATH):
        return pd.read_csv(_OCU_PATH)
    return pd.DataFrame()

_ocu_sig = ((os.path.getsize(_OCU_PATH), int(os.path.getmtime(_OCU_PATH)))
            if os.path.exists(_OCU_PATH) else (0, 0))
df_ocu = load_ocu_sx(_ocu_sig)

if not df_ocu.empty:
    st.markdown("---")
    st.header("Qui treballa al comerç: sexe i edat" if _ca
              else "Quién trabaja en el comercio: sexo y edad")
    intro(
        ("Més enllà de quantes persones treballen al comerç, importa <strong>qui</strong> ho fa. "
         "Amb l'Enquesta de Població Activa europea (Eurostat, CNAE 47) radiografiem el sector per "
         "<strong>sexe</strong> i <strong>edat</strong>, i el comparem amb la UE-27. Dues preguntes: "
         "és un sector feminitzat? I es renova generacionalment o envelleix?"
         if _ca else
         "Más allá de cuántas personas trabajan en el comercio, importa <strong>quién</strong> lo hace. "
         "Con la Encuesta de Población Activa europea (Eurostat, CNAE 47) radiografiamos el sector por "
         "<strong>sexo</strong> y <strong>edad</strong>, y lo comparamos con la UE-27. Dos preguntas: "
         "¿es un sector feminizado? ¿Y se renueva generacionalmente o envejece?")
    )

    _ages = ["15-24", "25-39", "40-49", "50-59", "60-64", "65+"]
    # Rampa seqüencial jove (clar) -> gran (fosc), família navy de marca
    _RAMP = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]
    _ult = int(df_ocu["any"].max())
    _first = int(df_ocu["any"].min())

    def _wshare(p, y):
        b = df_ocu[(df_ocu["pais_codi"] == p) & (df_ocu["any"] == y)]
        tot = b[b["sexe"] == "Total"]["ocupats_milers"].sum()
        don = b[b["sexe"] == "Dones"]["ocupats_milers"].sum()
        return (don / tot * 100) if tot else None

    def _ageshare(p, y, band):
        a = df_ocu[(df_ocu["sexe"] == "Total") & (df_ocu["pais_codi"] == p) & (df_ocu["any"] == y)]
        s = a.groupby("edat")["ocupats_milers"].sum()
        return (s.get(band, 0) / s.sum() * 100) if s.sum() else None

    def _senshare(p, y):  # 50 anys o més
        a = df_ocu[(df_ocu["sexe"] == "Total") & (df_ocu["pais_codi"] == p) & (df_ocu["any"] == y)]
        s = a.groupby("edat")["ocupats_milers"].sum()
        if not s.sum():
            return None
        return (s.get("50-59", 0) + s.get("60-64", 0) + s.get("65+", 0)) / s.sum() * 100

    w_es, w_ue = _wshare("ES", _ult), _wshare("EU27_2020", _ult)
    jove_es, jove_ue = _ageshare("ES", _ult, "15-24"), _ageshare("EU27_2020", _ult, "15-24")
    sen_es, sen_first = _senshare("ES", _ult), _senshare("ES", _first)

    k1, k2, k3 = st.columns(3)
    k1.metric(("Dones al comerç" if _ca else "Mujeres en el comercio"),
              fpct(w_es, 1, sign=False), help=(f"UE-27: {fpct(w_ue, 1, sign=False)}"))
    k2.metric(("Joves 15-24" if _ca else "Jóvenes 15-24"),
              fpct(jove_es, 1, sign=False),
              delta=fpct(jove_es - _ageshare("ES", _first, "15-24"), 1),
              delta_color="normal",
              help=(f"vs {_first}; UE-27 avui: {fpct(jove_ue, 1, sign=False)}"))
    k3.metric(("50 anys o més" if _ca else "50 años o más"),
              fpct(sen_es, 1, sign=False),
              delta=fpct(sen_es - sen_first, 1),
              delta_color="off", help=(f"vs {_first}"))

    _tab_sexe, _tab_edat = st.tabs([
        ("Sexe" if _ca else "Sexo"),
        ("Edat: relleu generacional" if _ca else "Edad: relevo generacional"),
    ])

    # --- Sexe: quota de dones al llarg del temps, ES vs UE ---
    with _tab_sexe:
        st.markdown("**Un sector majoritàriament femení**" if _ca
                    else "**Un sector mayoritariamente femenino**")
        _piv = df_ocu.pivot_table(index=["pais_codi", "any"], columns="sexe",
                                  values="ocupats_milers", aggfunc="sum").reset_index()
        _piv["quota_dones"] = _piv["Dones"] / _piv["Total"] * 100
        figg = go.Figure()
        for _p, _col, _nm in [("ES", BRAND, ("Espanya" if _ca else "España")),
                              ("EU27_2020", ORANGE, "UE-27")]:
            _d = _piv[_piv["pais_codi"] == _p].sort_values("any")
            figg.add_trace(go.Scatter(
                x=_d["any"], y=_d["quota_dones"], mode="lines+markers", name=_nm,
                line=dict(color=_col, width=2.5), marker=dict(size=5)))
        apply_layout(figg, yaxis_title="% dones" if _ca else "% mujeres", height=380)
        st.plotly_chart(figg, use_container_width=True)
        source("Eurostat lfsa_egan22d (EU-LFS), CNAE G47")

    # --- Edat: relleu generacional ---
    with _tab_edat:
        # (a) Evolució longitudinal de l'estructura d'edat a Espanya (àrea apilada 100%)
        st.markdown(("**Com evoluciona l'estructura d'edat a Espanya** "
                     f"({_first}–{_ult})" if _ca else
                     "**Cómo evoluciona la estructura de edad en España** "
                     f"({_first}–{_ult})"))
        _es = df_ocu[(df_ocu["sexe"] == "Total") & (df_ocu["pais_codi"] == "ES")]
        _pv = _es.pivot_table(index="any", columns="edat",
                              values="ocupats_milers", aggfunc="sum")
        _pv = _pv.reindex(columns=_ages)
        _pvs = _pv.div(_pv.sum(axis=1), axis=0) * 100
        figL = go.Figure()
        for _b, _colr in zip(_ages, _RAMP):
            figL.add_trace(go.Scatter(
                x=_pvs.index, y=_pvs[_b], mode="lines", name=_b,
                stackgroup="one", line=dict(width=0.5, color=_colr), fillcolor=_colr))
        apply_layout(figL, yaxis_title="% dels ocupats" if _ca else "% de los ocupados",
                     height=400, yaxis_range=[0, 100])
        st.plotly_chart(figL, use_container_width=True)
        source("Eurostat lfsa_egan22d (EU-LFS), CNAE G47")

        # (b) Foto actual: Espanya vs UE-27 per franja
        st.markdown((f"**Foto actual: Espanya vs UE-27** ({_ult})" if _ca
                     else f"**Foto actual: España vs UE-27** ({_ult})"))
        figa = go.Figure()
        for _p, _col, _nm in [("ES", BRAND, ("Espanya" if _ca else "España")),
                              ("EU27_2020", ORANGE, "UE-27")]:
            _ys = [_ageshare(_p, _ult, b) for b in _ages]
            figa.add_trace(go.Bar(x=_ages, y=_ys, name=_nm, marker_color=_col))
        apply_layout(figa, yaxis_title="% dels ocupats" if _ca else "% de los ocupados",
                     height=360, barmode="group")
        st.plotly_chart(figa, use_container_width=True)
        source("Eurostat lfsa_egan22d (EU-LFS), CNAE G47")

    insight(
        (f"El comerç és un <strong>sector feminitzat</strong> ({fpct(w_es, 1, sign=False)} de dones a Espanya, "
         f"lleugerament per sota de la UE-27, {fpct(w_ue, 1, sign=False)}), però <strong>envelleix de pressa</strong>. "
         f"El pes dels joves 15-24 ha caigut del {fpct(_ageshare('ES', _first, '15-24'), 1, sign=False)} ({_first}) "
         f"al {fpct(jove_es, 1, sign=False)} ({_ult}) —ara per sota de la UE-27 ({fpct(jove_ue, 1, sign=False)})—, "
         f"mentre el pes dels 50 anys o més ha pujat del {fpct(sen_first, 1, sign=False)} al {fpct(sen_es, 1, sign=False)}. "
         f"El <strong>relleu generacional és feble</strong>: cada cop entren menys joves i la plantilla es fa gran."
         if _ca else
         f"El comercio es un <strong>sector feminizado</strong> ({fpct(w_es, 1, sign=False)} de mujeres en España, "
         f"ligeramente por debajo de la UE-27, {fpct(w_ue, 1, sign=False)}), pero <strong>envejece rápido</strong>. "
         f"El peso de los jóvenes 15-24 ha caído del {fpct(_ageshare('ES', _first, '15-24'), 1, sign=False)} ({_first}) "
         f"al {fpct(jove_es, 1, sign=False)} ({_ult}) —ahora por debajo de la UE-27 ({fpct(jove_ue, 1, sign=False)})—, "
         f"mientras el peso de los 50 años o más ha subido del {fpct(sen_first, 1, sign=False)} al {fpct(sen_es, 1, sign=False)}. "
         f"El <strong>relevo generacional es débil</strong>: entran cada vez menos jóvenes y la plantilla envejece.")
    )

# ─── Descàrrega de dades ─────────────────────────────────────

with st.expander(t("download_data")):
    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
        st.download_button("CSV", df_prod.to_csv(index=False).encode("utf-8"), "ocupacio_cnae47.csv", "text/csv")

page_meta("INE, Estadística Estructural d'Empreses (EEE)" if _ca
          else "INE, Estadística Estructural de Empresas (EEE)", st.session_state.lang)

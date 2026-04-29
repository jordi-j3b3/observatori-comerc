"""Pàgina d'inici: KPIs, introducció i conclusions dinàmiques."""
import streamlit as st
import pandas as pd
import os, sys
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header, insight, fnum, fpct, cagr, page_meta

inject_css()
t = setup_lang(show_selector=False)

# ─── DADES ─────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data(name):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df_pib = load_data("pib_vab")
df_empreses = load_data("empreses")
df_prod = load_data("productivitat")
df_ecommerce = load_data("ecommerce")
df_europa = load_data("europa_vab")
df_territori = load_data("eee_ccaa")

# ─── HEADER ────────────────────────────────────────────────────

page_header()
st.title(t("app_title"))
st.markdown(f"*{t('app_subtitle')}*")

# ─── KPIs ──────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_pib.empty and "vab_cnae47_corrents" in df_pib.columns:
        rows = df_pib.dropna(subset=["vab_cnae47_corrents"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["vab_cnae47_corrents"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["vab_cnae47_corrents"]) - 1) * 100)
        st.metric(t("kpi_pib"), f"{fnum(val)} {t('kpi_meur')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_pib"), "—")

with col2:
    if not df_empreses.empty:
        esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if not esp.empty:
            last = esp.iloc[-1]
            val = int(last["empreses"])
            any_ = int(last["any"])
            if len(esp) > 1:
                prev = esp.iloc[-2]
                any_prev = int(prev["any"])
                delta = fpct(((val / int(prev["empreses"])) - 1) * 100)
                st.metric(t("kpi_empreses"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
            else:
                st.metric(t("kpi_empreses"), fnum(val), help=f"{any_}")
    else:
        st.metric(t("kpi_empreses"), "—")

with col3:
    if not df_prod.empty and "personal_ocupat" in df_prod.columns:
        rows = df_prod.dropna(subset=["personal_ocupat"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["personal_ocupat"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["personal_ocupat"]) - 1) * 100)
        st.metric(t("kpi_ocupacio"), fnum(val), delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_ocupacio"), "—")

with col4:
    if not df_prod.empty and "productivitat_va_hora" in df_prod.columns:
        rows = df_prod.dropna(subset=["productivitat_va_hora"])
        last = rows.iloc[-1]
        prev = rows.iloc[-2]
        val = last["productivitat_va_hora"]
        any_ = int(last["any"])
        any_prev = int(prev["any"])
        delta = fpct(((val / prev["productivitat_va_hora"]) - 1) * 100)
        st.metric(t("kpi_productivitat"), f"{fnum(val, 1)} {t('kpi_eur_h')}", delta, help=f"{any_} (var. {any_prev}–{any_})")
    else:
        st.metric(t("kpi_productivitat"), "—")

# ─── INTRODUCCIO ──────────────────────────────────────────────

st.divider()

_ca = st.session_state.lang == "ca"

if _ca:
    st.markdown("""
### Sobre l'Observatori

El **comerç al detall** (CNAE 47) és un dels pilars de l'economia espanyola: dona feina a més
d'**1,7 milions** de persones, genera uns **70.000 M EUR** de valor afegit i articula el consum
de les families a tot el territori. Tot i el seu pes, el sector afronta transformacions
profundes: digitalització, concentració empresarial, canvi de patrons de consum i pressió
sobre marges.

Aquest observatori ofereix una **radiografia actualitzada** del sector a partir de dades
oficials (INE, Eurostat, CNMC), organitzada en sis dimensions:

- **PIB i VAB:** evolució del valor afegit nominal i real, pes sobre el PIB
- **Empreses:** teixit empresarial, densitat comercial per CCAA
- **Treball i productivitat:** ocupació, hores, productivitat, distribució del valor afegit
- **E-commerce:** volum del canal online i pes sobre el total
- **Territori:** estimació del VAB per CCAA i diferències regionals
- **Europa:** posició d'Espanya en el context de la UE-27

Les dades s'actualitzen de forma **trimestral automàtica** (gener, abril, juliol, octubre).
    """)
else:
    st.markdown("""
### Sobre el Observatorio

El **comercio minorista** (CNAE 47) es uno de los pilares de la economia espanola: da empleo a mas
de **1,7 millones** de personas, genera unos **70.000 M EUR** de valor anadido y articula el consumo
de las familias en todo el territorio. A pesar de su peso, el sector afronta transformaciones
profundas: digitalizacion, concentracion empresarial, cambio de patrones de consumo y presion
sobre margenes.

Este observatorio ofrece una **radiografia actualizada** del sector a partir de datos
oficiales (INE, Eurostat, CNMC), organizada en seis dimensiones:

- **PIB y VAB:** evolución del valor anadido nominal y real, peso sobre el PIB
- **Empresas:** tejido empresarial, densidad comercial por CCAA
- **Trabajo y productividad:** empleo, horas, productividad, distribución del valor anadido
- **E-commerce:** volumen del canal online y peso sobre el total
- **Territorio:** estimación del VAB por CCAA y diferencias regionales
- **Europa:** posición de Espana en el contexto de la UE-27

Los datos se actualizan de forma **trimestral automatica** (enero, abril, julio, octubre).
    """)

# ─── CONCLUSIONS DINAMIQUES ───────────────────────────────────

_conclusions = []

# 1. PIB/VAB
if not df_pib.empty and "vab_cnae47_corrents" in df_pib.columns and "vab_cnae47_constants" in df_pib.columns:
    _pib_rows = df_pib.dropna(subset=["vab_cnae47_corrents", "vab_cnae47_constants"])
    if len(_pib_rows) >= 2:
        _pib_last = _pib_rows.iloc[-1]
        _pib_first = _pib_rows.iloc[0]
        _pib_yr = int(_pib_last["any"])
        _pib_n = _pib_yr - int(_pib_first["any"])
        _cagr_real = cagr(_pib_first["vab_cnae47_constants"], _pib_last["vab_cnae47_constants"], _pib_n)
        _var_last = ((_pib_last["vab_cnae47_corrents"] / _pib_rows.iloc[-2]["vab_cnae47_corrents"]) - 1) * 100
        if _ca:
            _conclusions.append(
                f"El VAB nominal del CNAE 47 es de <strong>{fnum(_pib_last['vab_cnae47_corrents'])} M EUR</strong> ({_pib_yr}), "
                f"amb un creixement real anualitzat (CAGR) del <strong>{fpct(_cagr_real, 2)}</strong> des de {int(_pib_first['any'])}."
            )
        else:
            _conclusions.append(
                f"El VAB nominal del CNAE 47 es de <strong>{fnum(_pib_last['vab_cnae47_corrents'])} M EUR</strong> ({_pib_yr}), "
                f"con un crecimiento real anualizado (CAGR) del <strong>{fpct(_cagr_real, 2)}</strong> desde {int(_pib_first['any'])}."
            )

# 2. Empreses
if not df_empreses.empty:
    _emp_esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
    if len(_emp_esp) >= 2:
        _emp_last = _emp_esp.iloc[-1]
        _emp_prev = _emp_esp.iloc[-2]
        _emp_var = (int(_emp_last["empreses"]) / int(_emp_prev["empreses"]) - 1) * 100
        if _ca:
            _conclusions.append(
                f"El sector compta amb <strong>{fnum(int(_emp_last['empreses']))}</strong> empreses ({int(_emp_last['any'])}), "
                f"un <strong>{fpct(_emp_var)}</strong> respecte l'any anterior."
            )
        else:
            _conclusions.append(
                f"El sector cuenta con <strong>{fnum(int(_emp_last['empreses']))}</strong> empresas ({int(_emp_last['any'])}), "
                f"un <strong>{fpct(_emp_var)}</strong> respecto al ano anterior."
            )

# 3. Productivitat
if not df_prod.empty and "productivitat_va_hora" in df_prod.columns:
    _prod_rows = df_prod.dropna(subset=["productivitat_va_hora"])
    if len(_prod_rows) >= 2:
        _prod_last = _prod_rows.iloc[-1]
        _prod_first = _prod_rows.iloc[0]
        _prod_var = (_prod_last["productivitat_va_hora"] / _prod_first["productivitat_va_hora"] - 1) * 100
        if _ca:
            _conclusions.append(
                f"La productivitat (VA/hora) ha variat un <strong>{fpct(_prod_var, 1)}</strong> "
                f"entre {int(_prod_first['any'])} i {int(_prod_last['any'])}, situant-se en "
                f"<strong>{fnum(_prod_last['productivitat_va_hora'], 1)} EUR/hora</strong>."
            )
        else:
            _conclusions.append(
                f"La productividad (VA/hora) ha variado un <strong>{fpct(_prod_var, 1)}</strong> "
                f"entre {int(_prod_first['any'])} y {int(_prod_last['any'])}, situandose en "
                f"<strong>{fnum(_prod_last['productivitat_va_hora'], 1)} EUR/hora</strong>."
            )

# 4. E-commerce
if not df_ecommerce.empty and "ecommerce_cnae47_eur" in df_ecommerce.columns:
    _ec = df_ecommerce.dropna(subset=["ecommerce_cnae47_eur"]).sort_values("any")
    if len(_ec) >= 2:
        _ec_last = _ec.iloc[-1]
        _ec_first = _ec.iloc[0]
        _ec_mult = _ec_last["ecommerce_cnae47_eur"] / _ec_first["ecommerce_cnae47_eur"]
        if _ca:
            _conclusions.append(
                f"L'e-commerce del CNAE 47 ha multiplicat el seu volum per <strong>x{fnum(_ec_mult, 1)}</strong> "
                f"des de {int(_ec_first['any'])}, fins a <strong>{fnum(_ec_last['ecommerce_cnae47_eur']/1e9, 1)} Md EUR</strong> ({int(_ec_last['any'])})."
            )
        else:
            _conclusions.append(
                f"El e-commerce del CNAE 47 ha multiplicado su volumen por <strong>x{fnum(_ec_mult, 1)}</strong> "
                f"desde {int(_ec_first['any'])}, hasta <strong>{fnum(_ec_last['ecommerce_cnae47_eur']/1e9, 1)} Md EUR</strong> ({int(_ec_last['any'])})."
            )

# 5. Europa
if not df_europa.empty and "pes_cnae47" in df_europa.columns:
    _eu_es = df_europa[df_europa["pais_codi"] == "ES"].sort_values("any")
    _eu_avg = df_europa[df_europa["pais_codi"] == "EU27_2020"].sort_values("any")
    if not _eu_es.empty and not _eu_avg.empty:
        _eu_es_last = _eu_es.iloc[-1]
        _eu_avg_last = _eu_avg.iloc[-1]
        _es_pct = _eu_es_last["pes_cnae47"] * 100
        _eu_pct = _eu_avg_last["pes_cnae47"] * 100
        _diff = _es_pct - _eu_pct
        if _ca:
            _pos = "per sobre" if _diff > 0 else "per sota"
            _conclusions.append(
                f"Espanya destina un <strong>{fpct(_es_pct, 2, sign=False)}</strong> del seu PIB al comerç al detall, "
                f"<strong>{fpct(abs(_diff), 2, sign=False)} {_pos}</strong> de la mitjana UE-27 ({fpct(_eu_pct, 2, sign=False)})."
            )
        else:
            _pos = "por encima" if _diff > 0 else "por debajo"
            _conclusions.append(
                f"Espana destina un <strong>{fpct(_es_pct, 2, sign=False)}</strong> de su PIB al comercio minorista, "
                f"<strong>{fpct(abs(_diff), 2, sign=False)} {_pos}</strong> de la media UE-27 ({fpct(_eu_pct, 2, sign=False)})."
            )

# 6. Territori
if not df_territori.empty and "pes_cnae47_pib" in df_territori.columns:
    _terr = df_territori[df_territori["territori"] != "espanya"].dropna(subset=["pes_cnae47_pib"])
    if not _terr.empty:
        _terr_yr = _terr["any"].max()
        _terr_yr_data = _terr[_terr["any"] == _terr_yr]
        _t_top = _terr_yr_data.nlargest(1, "pes_cnae47_pib").iloc[0]
        _t_bot = _terr_yr_data.nsmallest(1, "pes_cnae47_pib").iloc[0]
        if _ca:
            _conclusions.append(
                f"El pes territorial del comerç al detall varia entre el <strong>{fpct(_t_top['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_top['territori']} i el <strong>{fpct(_t_bot['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_bot['territori']} ({int(_terr_yr)})."
            )
        else:
            _conclusions.append(
                f"El peso territorial del comercio minorista varía entre el <strong>{fpct(_t_top['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_top['territori']} y el <strong>{fpct(_t_bot['pes_cnae47_pib']*100, 1, sign=False)}</strong> "
                f"de {_t_bot['territori']} ({int(_terr_yr)})."
            )

if _conclusions:
    _eyebrow = "Resum executiu" if _ca else "Resumen ejecutivo"
    _title = "Principals conclusions" if _ca else "Principales conclusiones"
    _upd_lbl = "Última actualització" if _ca else "Última actualización"

    _last_update_path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "last_update.txt")
    _upd_html = ""
    if os.path.exists(_last_update_path):
        with open(_last_update_path) as f:
            _upd = f.read().strip()
        _upd_html = f'<div class="conclusions-update">{_upd_lbl}: {_upd}</div>'

    _items_html = "".join(f"<li>{c}</li>" for c in _conclusions)

    st.markdown(
        f"""
        <div class="conclusions-block">
            <div class="conclusions-eyebrow">{_eyebrow}</div>
            <h3>{_title}</h3>
            {_upd_html}
            <ul>{_items_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── DESCARREGA EXCEL ─────────────────────────────────────────

st.divider()
st.subheader("Descàrrega de dades" if _ca else "Descarga de datos")
st.markdown(
    ("Descarrega un fitxer Excel amb totes les dades i grafics de l'observatori."
     if _ca else
     "Descarga un archivo Excel con todos los datos y graficos del observatorio.")
)


def _build_excel():
    buf = BytesIO()
    wb = None
    try:
        import xlsxwriter
        wb = xlsxwriter.Workbook(buf, {"in_memory": True, "nan_inf_to_errors": True})
    except ImportError:
        return None

    hdr_fmt = wb.add_format({"bold": True, "bg_color": "#0055a4", "font_color": "white",
                              "border": 1, "font_name": "Calibri", "font_size": 11})
    cell_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11})
    num_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "#,##0"})
    pct_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "0.00%"})
    dec_fmt = wb.add_format({"border": 1, "font_name": "Calibri", "font_size": 11, "num_format": "#,##0.0"})

    def _write_header(ws, cols, row=0):
        for c, name in enumerate(cols):
            ws.write(row, c, name, hdr_fmt)

    # --- 1. PIB i VAB ---
    if not df_pib.empty:
        ws = wb.add_worksheet("PIB i VAB")
        cols = ["Any", "VAB nominal (M EUR)", "VAB real (M EUR)", "Pes s/ PIB"]
        _write_header(ws, cols)
        rows_pib = df_pib.sort_values("any")
        for i, (_, r) in enumerate(rows_pib.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("vab_cnae47_corrents"), num_fmt)
            ws.write(i, 2, r.get("vab_cnae47_constants"), num_fmt)
            ws.write(i, 3, r.get("pes_cnae47"), pct_fmt)
        n = len(rows_pib)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 2, 20)
        ws.set_column(3, 3, 14)

        chart = wb.add_chart({"type": "line"})
        chart.add_series({"name": "VAB nominal", "categories": ["PIB i VAB", 1, 0, n, 0],
                          "values": ["PIB i VAB", 1, 1, n, 1], "line": {"color": "#0055a4", "width": 2.5}})
        chart.add_series({"name": "VAB real", "categories": ["PIB i VAB", 1, 0, n, 0],
                          "values": ["PIB i VAB", 1, 2, n, 2], "line": {"color": "#c0392b", "width": 2.5}})
        chart.set_title({"name": "VAB CNAE 47 (M EUR)"})
        chart.set_x_axis({"name": "Any"})
        chart.set_y_axis({"name": "M EUR"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "bottom"})
        ws.insert_chart("F2", chart)

    # --- 2. Empreses ---
    if not df_empreses.empty:
        ws = wb.add_worksheet("Empreses")
        cols = ["Territori", "Any", "Empreses", "Poblacio", "Empreses/1.000 hab."]
        _write_header(ws, cols)
        rows_emp = df_empreses.sort_values(["territori", "any"])
        for i, (_, r) in enumerate(rows_emp.iterrows(), 1):
            ws.write(i, 0, r["territori"], cell_fmt)
            ws.write(i, 1, int(r["any"]), cell_fmt)
            ws.write(i, 2, int(r["empreses"]) if pd.notna(r["empreses"]) else None, num_fmt)
            ws.write(i, 3, int(r["poblacio"]) if pd.notna(r.get("poblacio")) else None, num_fmt)
            ws.write(i, 4, r.get("empreses_per_1000hab"), dec_fmt)
        ws.set_column(0, 0, 28)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 4, 18)

        esp = df_empreses[df_empreses["territori"] == "espanya"].sort_values("any")
        if len(esp) >= 2:
            ws2_name = "Empreses_ES"
            ws2 = wb.add_worksheet(ws2_name)
            _write_header(ws2, ["Any", "Empreses"])
            for i, (_, r) in enumerate(esp.iterrows(), 1):
                ws2.write(i, 0, int(r["any"]), cell_fmt)
                ws2.write(i, 1, int(r["empreses"]), num_fmt)
            ne = len(esp)
            chart = wb.add_chart({"type": "line"})
            chart.add_series({"name": "Empreses Espanya", "categories": [ws2_name, 1, 0, ne, 0],
                              "values": [ws2_name, 1, 1, ne, 1], "line": {"color": "#0055a4", "width": 2.5}})
            chart.set_title({"name": "Empreses CNAE 47 - Espanya"})
            chart.set_size({"width": 620, "height": 380})
            chart.set_legend({"position": "none"})
            ws2.insert_chart("D2", chart)
            ws2.set_column(0, 0, 8)
            ws2.set_column(1, 1, 14)

    # --- 3. Productivitat ---
    if not df_prod.empty:
        ws = wb.add_worksheet("Productivitat")
        cols = ["Any", "Personal ocupat", "Hores treballades", "Productivitat (EUR/h)",
                "Quota salarial", "Cost laboral/ocupat"]
        _write_header(ws, cols)
        rows_p = df_prod.sort_values("any")
        for i, (_, r) in enumerate(rows_p.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("personal_ocupat"), num_fmt)
            ws.write(i, 2, r.get("hores_treballades"), num_fmt)
            ws.write(i, 3, r.get("productivitat_va_hora"), dec_fmt)
            ws.write(i, 4, r.get("quota_salarial"), pct_fmt)
            ws.write(i, 5, r.get("cost_laboral_per_ocupat"), num_fmt)
        np_ = len(rows_p)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 5, 22)

        chart = wb.add_chart({"type": "line"})
        chart.add_series({"name": "Productivitat (EUR/h)", "categories": ["Productivitat", 1, 0, np_, 0],
                          "values": ["Productivitat", 1, 3, np_, 3], "line": {"color": "#0055a4", "width": 2.5}})
        chart.set_title({"name": "Productivitat VA/hora (EUR)"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "none"})
        ws.insert_chart("H2", chart)

    # --- 4. E-commerce ---
    if not df_ecommerce.empty:
        ws = wb.add_worksheet("E-commerce")
        cols = ["Any", "E-commerce total (EUR)", "E-commerce CNAE 47 (EUR)", "Pes CNAE 47"]
        _write_header(ws, cols)
        rows_ec = df_ecommerce.sort_values("any")
        for i, (_, r) in enumerate(rows_ec.iterrows(), 1):
            ws.write(i, 0, int(r["any"]), cell_fmt)
            ws.write(i, 1, r.get("ecommerce_total_eur"), num_fmt)
            ws.write(i, 2, r.get("ecommerce_cnae47_eur"), num_fmt)
            ws.write(i, 3, r.get("pes_cnae47_ecommerce"), pct_fmt)
        nec = len(rows_ec)
        ws.set_column(0, 0, 8)
        ws.set_column(1, 2, 24)
        ws.set_column(3, 3, 14)

        chart = wb.add_chart({"type": "column"})
        chart.add_series({"name": "E-commerce CNAE 47", "categories": ["E-commerce", 1, 0, nec, 0],
                          "values": ["E-commerce", 1, 2, nec, 2], "fill": {"color": "#0055a4"}})
        chart.set_title({"name": "E-commerce CNAE 47 (EUR)"})
        chart.set_size({"width": 620, "height": 380})
        chart.set_legend({"position": "none"})
        ws.insert_chart("F2", chart)

    # --- 5. Territori ---
    if not df_territori.empty:
        ws = wb.add_worksheet("Territori CCAA")
        cols = ["Territori", "Any", "Locals", "Personal ocupat", "VAB estimat (EUR)",
                "VAB Eurostat (EUR)", "Pes CNAE 47/PIB"]
        _write_header(ws, cols)
        rows_t = df_territori.sort_values(["territori", "any"])
        for i, (_, r) in enumerate(rows_t.iterrows(), 1):
            ws.write(i, 0, r["territori"], cell_fmt)
            ws.write(i, 1, int(r["any"]), cell_fmt)
            ws.write(i, 2, r.get("locals"), num_fmt)
            ws.write(i, 3, r.get("personal_ocupat"), num_fmt)
            ws.write(i, 4, r.get("vab_estimat"), num_fmt)
            ws.write(i, 5, r.get("vab_eurostat"), num_fmt)
            ws.write(i, 6, r.get("pes_cnae47_pib"), pct_fmt)
        ws.set_column(0, 0, 28)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 6, 20)

        terr_last = df_territori[
            (df_territori["territori"] != "espanya") &
            df_territori["pes_cnae47_pib"].notna()
        ]
        if not terr_last.empty:
            yr_max = terr_last["any"].max()
            tdata = terr_last[terr_last["any"] == yr_max].sort_values("pes_cnae47_pib", ascending=False)
            ws2_name = "Pes CCAA"
            ws2 = wb.add_worksheet(ws2_name)
            _write_header(ws2, ["CCAA", "Pes CNAE 47/PIB"])
            for i, (_, r) in enumerate(tdata.iterrows(), 1):
                ws2.write(i, 0, r["territori"], cell_fmt)
                ws2.write(i, 1, r["pes_cnae47_pib"], pct_fmt)
            nt = len(tdata)
            ws2.set_column(0, 0, 28)
            ws2.set_column(1, 1, 18)

            chart = wb.add_chart({"type": "bar"})
            chart.add_series({"name": f"Pes CNAE 47/PIB ({int(yr_max)})",
                              "categories": [ws2_name, 1, 0, nt, 0],
                              "values": [ws2_name, 1, 1, nt, 1],
                              "fill": {"color": "#0055a4"}})
            chart.set_title({"name": f"Pes del comerç al detall sobre el PIB ({int(yr_max)})"})
            chart.set_size({"width": 700, "height": 480})
            chart.set_legend({"position": "none"})
            chart.set_y_axis({"reverse": True})
            ws2.insert_chart("D2", chart)

    # --- 6. Europa ---
    if not df_europa.empty:
        ws = wb.add_worksheet("Europa")
        cols = ["Pais", "Codi", "Any", "VAB CNAE 47 (M EUR)", "VAB total (M EUR)", "Pes CNAE 47"]
        _write_header(ws, cols)
        rows_eu = df_europa.sort_values(["pais", "any"])
        for i, (_, r) in enumerate(rows_eu.iterrows(), 1):
            ws.write(i, 0, r.get("pais", ""), cell_fmt)
            ws.write(i, 1, r.get("pais_codi", ""), cell_fmt)
            ws.write(i, 2, int(r["any"]), cell_fmt)
            ws.write(i, 3, r.get("vab_meur"), num_fmt)
            ws.write(i, 4, r.get("vab_total_meur"), num_fmt)
            ws.write(i, 5, r.get("pes_cnae47"), pct_fmt)
        ws.set_column(0, 0, 18)
        ws.set_column(1, 1, 8)
        ws.set_column(2, 2, 8)
        ws.set_column(3, 5, 22)

    wb.close()
    buf.seek(0)
    return buf


col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    _excel_buf = _build_excel()
    if _excel_buf:
        st.download_button(
            label=("Descarregar Excel (totes les dades)" if _ca
                   else "Descargar Excel (todos los datos)"),
            data=_excel_buf,
            file_name="observatori_comerc_detall.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("xlsxwriter no disponible" if _ca else "xlsxwriter no disponible")

with col_dl2:
    _info_path = os.path.join(os.path.dirname(__file__), "..", "data", "static", "infografia_q1_2026.html")
    if os.path.exists(_info_path):
        with open(_info_path, "rb") as f:
            _info_bytes = f.read()
        st.download_button(
            label=("Descarregar infografia Q1 2026 (HTML)" if _ca
                   else "Descargar infografía Q1 2026 (HTML)"),
            data=_info_bytes,
            file_name="comerc_minorista_espana_Q1_2026.html",
            mime="text/html",
        )

# ─── META ─────────────────────────────────────────────────────

page_meta("INE, Eurostat, CNMC", st.session_state.lang)

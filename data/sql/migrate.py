"""
Migració completa del pipeline CSV -> DuckDB pel chatbot de retail.
Esquema (format llarg/tidy) definit a schema.sql: observations + series_metadata.

Convenció (confirmada 2026-08-03 després del pilot amb icm/epa_retail/ipc_coicop):
  - Magnituds/unitats diferents (encara que vinguin en un mateix CSV, ample o
    llarg) -> serie_id propi.
  - Categories DINS la mateixa magnitud (territori, sexe, branca CNAE, grup
    ECOICOP, tecnologia...) -> dimensió (dim_1/dim_2/dim_3), no serie propi.

30 caches -> 3 exclusions:
  - municipal: exclòs del chatbot públic (decisió explícita).
  - lideres_empreses, prediccions_estructura: NO són series temporals
    (entitat-atribut / registre d'esdeveniments amb múltiples dates per fila)
    — no encaixen amb l'esquema observations. Vegeu SKIPPED avall.

Execució: python3 data/sql/migrate.py
"""
import os
import duckdb
import pandas as pd

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "observatori.duckdb")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def _load(name):
    return pd.read_csv(os.path.join(CACHE_DIR, f"{name}.csv"))


# ─── Helpers genèrics de data ────────────────────────────────────────────────

def _annual_date(df):
    return pd.to_datetime(dict(year=df["any"], month=1, day=1)).dt.date


def _monthly_date(df, any_col="any", mes_col="mes"):
    return pd.to_datetime(dict(year=df[any_col], month=df[mes_col], day=1)).dt.date


def _periode_monthly_date(df, col="periode"):
    return pd.to_datetime(df[col] + "-01").dt.date


def _asis_date(df, col="data"):
    return pd.to_datetime(df[col]).dt.date


# ─── Helper genèric: cache CSV (ample o llarg) -> tidy (date,value,dim_1..3) ─
# Cobreix TOTS els casos: extreure una columna d'un CSV ample (split per
# mètrica) i extreure la columna "valor" d'un CSV ja llarg (nomes cal
# renombrar dims) són la mateixa operació.

def _series_builder(cache_name, metric_col, date_fn, dim_cols=(), row_filter=None):
    def _build():
        df = _load(cache_name).copy()
        if row_filter is not None:
            df = df[row_filter(df)].copy()
        out = pd.DataFrame({"date": date_fn(df), "value": df[metric_col].values})
        for i, dc in enumerate(dim_cols, start=1):
            out[f"dim_{i}"] = df[dc].values
        return out
    return _build


# ─── Transformacions: CSV cache (ample o llarg) -> tidy (date,value,dim_1,dim_2,dim_3) ───

def _build_icm(tipus):
    df = _load("icm")
    df = df[df["tipus"] == tipus].copy()
    df["date"] = pd.to_datetime(df["data"]).dt.date
    return df.rename(columns={"valor": "value", "branca": "dim_1", "ambit": "dim_2",
                               "indicador": "dim_3"})[["date", "value", "dim_1", "dim_2", "dim_3"]]


def _build_epa_retail(metric_col):
    df = _load("epa_retail").copy()
    mes_inici = (df["trimestre"] - 1) * 3 + 1
    df["date"] = pd.to_datetime(dict(year=df["any"], month=mes_inici, day=1)).dt.date
    df["value"] = df[metric_col]
    df["dim_1"] = df["sexe"]
    return df[["date", "value", "dim_1"]]


def _build_ipc_coicop():
    df = _load("ipc_coicop").copy()
    df["date"] = pd.to_datetime(dict(year=df["any"], month=df["mes"], day=1)).dt.date
    df["value"] = df["ipc"]
    df["dim_1"] = df["grup"]
    return df[["date", "value", "dim_1"]]


# ─── Registre de sèries pilot ────────────────────────────────────────────────
# "tipus" de l'ICM (nominal/real/ocupació) esdevé serie_id perquè són magnituds
# i unitats diferents (€ corrents / € constants / persones), no una dimensió
# dins la mateixa magnitud — a diferència de "branca" o "grup", que sí ho són.

SERIES = [
    dict(serie_id="icm_nominal", name="ICM — cifra de negoci nominal",
         description="Índex de comerç al detall (cifra de negoci a preus corrents), "
                      "per branca CNAE 47 i CCAA. Base 2021=100.",
         source="INE", source_table="T=59787+60110",
         frequency="monthly", unit="índex / % variació",
         is_critical=True, is_derived=False, is_public=True,
         build=lambda: _build_icm("nominal")),
    dict(serie_id="icm_real", name="ICM — cifra de negoci real",
         description="Índex de comerç al detall (cifra de negoci a preus constants, "
                      "deflactat), per branca CNAE 47 i CCAA. Base 2021=100.",
         source="INE", source_table="T=60096+60111",
         frequency="monthly", unit="índex / % variació",
         is_critical=True, is_derived=False, is_public=True,
         build=lambda: _build_icm("real")),
    dict(serie_id="icm_ocupacio", name="ICM — ocupació",
         description="Índex d'ocupació mensual del comerç al detall, per branca "
                      "CNAE 47. Base 2021=100.",
         source="INE", source_table="T=60114+60115",
         frequency="monthly", unit="índex / % variació",
         is_critical=True, is_derived=False, is_public=True,
         build=lambda: _build_icm("ocupacio")),
    dict(serie_id="epa_retail_ocupats", name="EPA — ocupats al comerç al detall",
         description="Ocupats CNAE 47 net (comerç al detall, excepte vehicles de "
                      "motor i motocicletes), per sexe. Font: Encuesta de Población "
                      "Activa (EPA).",
         source="INE", source_table="T=65123",
         frequency="quarterly", unit="milers de persones",
         is_critical=False, is_derived=False, is_public=True,
         build=lambda: _build_epa_retail("ocupats_cnae47_milers")),
    dict(serie_id="epa_retail_aturats", name="EPA — aturats (secció G)",
         description="Aturats de la secció G (comerç a l'engròs + al detall + "
                      "reparació de vehicles), per sexe. L'INE NO desglossa els "
                      "aturats a nivell CNAE 47 — aquesta xifra inclou també "
                      "l'engròs i la reparació de vehicles, no només comerç al "
                      "detall.",
         source="INE", source_table="T=65249",
         frequency="quarterly", unit="milers de persones",
         is_critical=False, is_derived=False, is_public=True,
         build=lambda: _build_epa_retail("aturats_seccio_g_milers")),
    dict(serie_id="epa_retail_hores", name="EPA — hores setmanals (secció G)",
         description="Mitjana d'hores efectives setmanals treballades a la "
                      "secció G (comerç a l'engròs + al detall + reparació de "
                      "vehicles), per sexe. L'INE NO desglossa aquesta magnitud "
                      "a nivell CNAE 47.",
         source="INE", source_table="T=65159",
         frequency="quarterly", unit="hores/setmana (mitjana)",
         is_critical=False, is_derived=False, is_public=True,
         build=lambda: _build_epa_retail("hores_setmana_seccio_g")),
    dict(serie_id="ipc_coicop", name="IPC per grups (alimentació, vestit, llar)",
         description="Índex de Preus de Consum mensual per grups ECOICOP "
                      "rellevants pel comerç al detall (alimentació, vestit i "
                      "calçat, parament de la llar) + índex general de referència. "
                      "Base 2021=100.",
         source="INE", source_table="T=76125",
         frequency="monthly", unit="índex (base 2021=100)",
         is_critical=False, is_derived=False, is_public=True,
         build=_build_ipc_coicop),
]


# ─── Sèries restants (26 caches -> ~90 sèries) ───────────────────────────────
# is_critical s'hereta de CRITICAL_SOURCES a processor.py: totes les sub-series
# d'un cache crític (pib_vab, empreses, productivitat, europa_vab,
# europa_retail_mensual) hereten is_critical=True; la resta, False.
# is_derived=True nomes per estructura_comerc (model propi J3B3).

def _icm_distribucio_build(tipus):
    return _series_builder(
        "icm_distribucion", "valor",
        lambda df: _asis_date(df),
        dim_cols=["modo", "indicador"],
        row_filter=lambda df, t=tipus: df["tipus"] == t,
    )()


SERIES_EXTRA = []


def _add(serie_id, name, description, source, source_table, frequency, unit,
         is_critical, is_derived, cache_name, metric_col, date_fn, dim_cols=(),
         row_filter=None):
    SERIES_EXTRA.append(dict(
        serie_id=serie_id, name=name, description=description, source=source,
        source_table=source_table, frequency=frequency, unit=unit,
        is_critical=is_critical, is_derived=is_derived, is_public=True,
        build=_series_builder(cache_name, metric_col, date_fn, dim_cols, row_filter),
    ))


# --- pib_vab (INE T=69070) — CRITICAL — sense dimensió (agregat nacional) ---
for col, unit, desc in [
    ("vab_total_corrents", "M EUR (preus corrents)", "VAB total de l'economia espanyola, preus corrents."),
    ("vab_cnae47_corrents", "M EUR (preus corrents)", "VAB del comerç al detall (CNAE 47), preus corrents."),
    ("vab_cnae47_constants", "M EUR (preus constants)", "VAB del comerç al detall (CNAE 47), preus constants (volum encadenat)."),
    ("vab_total_constants", "M EUR (preus constants)", "VAB total de l'economia espanyola, preus constants."),
    ("pes_cnae47", "ràtio (0-1)", "Pes del VAB del comerç al detall sobre el VAB total (preus corrents)."),
    ("var_vab_cnae47_corrents", "% variació anual", "Variació interanual del VAB CNAE 47 a preus corrents."),
    ("var_vab_cnae47_constants", "% variació anual", "Variació interanual del VAB CNAE 47 a preus constants."),
]:
    _add(f"pib_vab_{col}", f"PIB/VAB — {col}", desc, "INE", "T=69070",
         "annual", unit, True, False, "pib_vab", col, _annual_date)

# --- empreses (INE T=39372+3954+298 DIRCE + T=2915+56934 Padró) — CRITICAL ---
_add("empreses_count", "Empreses actives CNAE 47", "Nombre d'empreses actives del comerç al detall (CNAE 47), per territori.",
     "INE", "T=39372+3954+298", "annual", "nombre d'empreses", True, False,
     "empreses", "empreses", _annual_date, dim_cols=["territori"])
_add("empreses_poblacio", "Població (per territori)", "Població per territori, usada com a denominador de densitat comercial.",
     "INE", "T=2915+56934", "annual", "persones", True, False,
     "empreses", "poblacio", _annual_date, dim_cols=["territori"])
_add("empreses_per_1000hab", "Densitat comercial", "Empreses actives CNAE 47 per cada 1.000 habitants, per territori.",
     "INE", "T=39372+3954+298 / T=2915+56934 (ràtio derivada)", "annual", "empreses / 1.000 hab.", True, False,
     "empreses", "empreses_per_1000hab", _annual_date, dim_cols=["territori"])

# --- productivitat (INE T=36194 EEE Comercio + T=36199 P&L + T=50902 IPC) — CRITICAL ---
_PROD = [
    ("xifra_negoci_constants", "M EUR (preus constants)", "T=36194 (deflactat amb T=50902)", "Xifra de negoci del comerç al detall, preus constants."),
    ("valor_afegit_constants", "M EUR (preus constants)", "T=36194 (deflactat amb T=50902)", "Valor afegit del comerç al detall, preus constants."),
    ("personal_ocupat", "persones", "T=36194", "Personal ocupat al comerç al detall."),
    ("hores_treballades", "milers d'hores", "T=36194", "Hores treballades pel personal remunerat, comerç al detall."),
    ("productivitat_va_hora", "EUR/hora", "T=36194 (ràtio derivada)", "Productivitat: valor afegit constant per hora treballada."),
    ("productivitat_xn_hora", "EUR/hora", "T=36194 (ràtio derivada)", "Productivitat: xifra de negoci constant per hora treballada."),
    ("gastos_personal", "M EUR (preus corrents)", "T=36194", "Despeses de personal, comerç al detall."),
    ("gastos_personal_constants", "M EUR (preus constants)", "T=36194 (deflactat amb T=50902)", "Despeses de personal, preus constants."),
    ("quota_salarial", "ràtio (0-1)", "T=36194 (ràtio derivada)", "Despeses de personal sobre valor afegit."),
    ("excedent_brut", "M EUR (preus corrents)", "T=36194 (ràtio derivada)", "Excedent brut d'explotació (valor afegit - despeses de personal)."),
    ("cost_laboral_per_ocupat", "EUR/persona", "T=36194 (ràtio derivada)", "Cost laboral mitjà per ocupat."),
    ("cost_laboral_hora", "EUR/hora", "T=36194+50902 (ràtio derivada)", "Cost laboral per hora treballada, preus constants."),
    ("cogs", "M EUR (preus corrents)", "T=36199", "Consum de béns i serveis per a revenda (cost de mercaderia venuda)."),
    ("cogs_constants", "M EUR (preus constants)", "T=36199 (deflactat amb T=50902)", "COGS, preus constants."),
    ("serveis_exteriors", "M EUR (preus corrents)", "T=36199", "Despeses en serveis exteriors (lloguers, energia, serveis externs)."),
    ("serveis_exteriors_constants", "M EUR (preus constants)", "T=36199 (deflactat amb T=50902)", "Serveis exteriors, preus constants."),
    ("marge_brut", "ràtio (0-1)", "T=36194+36199 (ràtio derivada)", "Marge brut comptable: (vendes - COGS) / vendes."),
]
for col, unit, tbl, desc in _PROD:
    _add(f"productivitat_{col}", f"Productivitat — {col}", desc, "INE", tbl,
         "annual", unit, True, False, "productivitat", col, _annual_date)

# --- europa_vab (Eurostat nama_10_a64) — CRITICAL — dim: pais ---
for col, unit, desc in [
    ("vab_meur", "M EUR", "VAB del comerç al detall (G47), per país."),
    ("vab_total_meur", "M EUR", "VAB total de l'economia, per país."),
    ("pes_cnae47", "ràtio (0-1)", "Pes del G47 sobre el VAB total, per país."),
]:
    _add(f"europa_vab_{col}", f"Europa VAB — {col}", desc, "Eurostat", "nama_10_a64",
         "annual", unit, True, False, "europa_vab", col, _annual_date, dim_cols=["pais"])

# --- europa_retail_mensual (Eurostat sts_trtu_m) — CRITICAL — dim: pais ---
_add("europa_retail_mensual_index", "Europa — volum de vendes retail (índex)",
     "Índex de volum de vendes del comerç al detall (G47), ajustat estacional, base 2021=100, per país.",
     "Eurostat", "sts_trtu_m", "monthly", "índex (base 2021=100)", True, False,
     "europa_retail_mensual", "index_volum", _periode_monthly_date, dim_cols=["pais"])
_add("europa_retail_mensual_yoy", "Europa — volum de vendes retail (variació interanual)",
     "Variació interanual de l'índex de volum de vendes retail, per país.",
     "Eurostat", "sts_trtu_m", "monthly", "% variació anual", True, False,
     "europa_retail_mensual", "yoy", _periode_monthly_date, dim_cols=["pais"])

# --- icm_distribucion (INE T=60105 nominal / T=75809 real / T=60115 ocupació) — CRITICAL ---
for tipus, tid, label in [
    ("nominal", "T=60105", "cifra de negoci nominal"),
    ("real", "T=75809", "cifra de negoci real"),
    ("ocupacio", "T=60115", "ocupació"),
]:
    SERIES_EXTRA.append(dict(
        serie_id=f"icm_distribucio_{tipus}", name=f"ICM per modo distribució — {label}",
        description=f"Índex de {label} del comerç al detall per modo de distribució "
                     "(Empresas unilocalizadas / Pequeñas cadenas / Grandes cadenas / "
                     "Grandes Superficies). Base 2021=100.",
        source="INE", source_table=tid, frequency="monthly", unit="índex / % variació",
        is_critical=True, is_derived=False, is_public=True,
        build=(lambda t=tipus: _icm_distribucio_build(t)),
    ))

# --- ipc (INE T=50902) — no crítica — sense dimensió ---
_add("ipc", "IPC general", "Índex de Preus de Consum general nacional, base 2021=100.",
     "INE", "T=50902", "monthly", "índex (base 2021=100)", False, False,
     "ipc", "ipc", _monthly_date)

# --- confianza_consumidor (Eurostat ei_bsco_m) — no crítica — sense dimensió ---
for col, label, desc in [
    ("index_confianca", "índex compost", "Indicador compost de confiança del consumidor (mitjana de 4 components a 12 mesos vista)."),
    ("situacio_actual_financera", "situació actual — financera", "Balanç d'opinió sobre la situació financera de la llar, últims 12 mesos."),
    ("situacio_actual_economica", "situació actual — econòmica", "Balanç d'opinió sobre la situació econòmica general, últims 12 mesos."),
    ("expectatives_financera", "expectatives — financera", "Balanç d'opinió sobre la situació financera de la llar, propers 12 mesos."),
    ("expectatives_economica", "expectatives — econòmica", "Balanç d'opinió sobre la situació econòmica general, propers 12 mesos."),
]:
    _add(f"confianza_consumidor_{col}", f"Confiança consumidor — {label}", desc,
         "Eurostat", "ei_bsco_m", "monthly", "balanç de respostes (-100..100)", False, False,
         "confianza_consumidor", col, _monthly_date)

# --- digitalitzacio_comerc (Eurostat isoc_*) — no crítica — dims: tech, pais ---
_add("digitalitzacio_comerc", "Digitalització del comerç (TIC)",
     "Percentatge d'empreses del comerç (G47) que adopten venda electrònica, IA o núvol.",
     "Eurostat", "isoc_* (múltiples datasets TIC)", "annual", "% empreses", False, False,
     "digitalitzacio_comerc", "pct", _annual_date, dim_cols=["tech", "pais"])

# --- ocupacio_comerc (Eurostat lfsa_egan22d) — no crítica — dims: pais, sexe, edat ---
_add("ocupacio_comerc", "Ocupació al comerç per sexe i edat",
     "Persones ocupades al comerç al detall (G47), per país, sexe i franja d'edat.",
     "Eurostat", "lfsa_egan22d", "annual", "milers de persones", False, False,
     "ocupacio_comerc", "ocupats_milers", _annual_date, dim_cols=["pais", "sexe", "edat"])

# --- eaes (INE T=28185) — no crítica — dim: sector ---
_add("eaes", "Salari brut anual per sector", "Salari brut anual mitjà, per sector d'activitat (comparativa amb el comerç).",
     "INE", "T=28185", "annual", "EUR/any", False, False,
     "eaes", "valor", _annual_date, dim_cols=["sector"])

# --- ecommerce (CNMC) — no crítica (exclosa expressament) — sense dimensió ---
for sid, col, unit, desc in [
    ("ecommerce_total", "ecommerce_total_eur", "EUR", "Facturació total del comerç electrònic a Espanya (tots els sectors)."),
    ("ecommerce_cnae47", "ecommerce_cnae47_eur", "EUR", "Facturació del comerç electrònic del CNAE 47 (comerç al detall)."),
    ("ecommerce_pes_cnae47", "pes_cnae47_ecommerce", "ràtio (0-1)", "Pes del CNAE 47 sobre el total de comerç electrònic."),
]:
    _add(sid, f"E-commerce — {col}", desc, "CNMC", "Panel CNMC comercio electrónico",
         "annual", unit, False, False, "ecommerce", col, _annual_date)

# --- eee_ccaa (INE T=76817 + Eurostat nama_10r_3gva/nama_10_a64 per vab_eurostat) — no crítica ---
_EEE_CCAA = [
    ("locals", "nombre de locals", "T=76817", "Nombre de locals del comerç al detall, per CCAA."),
    ("xifra_negoci", "M EUR", "T=76817", "Xifra de negoci del comerç al detall, per CCAA."),
    ("sous_salaris", "M EUR", "T=76817", "Sous i salaris del comerç al detall, per CCAA."),
    ("inversio", "M EUR", "T=76817", "Inversió en actius materials, per CCAA."),
    ("personal_ocupat", "persones", "T=76817", "Personal ocupat del comerç al detall, per CCAA."),
    ("vab_estimat", "M EUR", "T=76817 (estimació via ràtio VA/XN)", "VAB estimat per CCAA (mètode ràtio nacional, preus constants)."),
    ("vab_estimat_nominal", "M EUR", "T=76817 (estimació via ràtio VAB corrents/XN)", "VAB estimat per CCAA (mètode ràtio nacional, preus corrents)."),
    ("vab_eurostat", "M EUR", "Eurostat nama_10r_3gva+nama_10_a64 (mètode híbrid)", "VAB estimat per CCAA (mètode híbrid comptabilitat regional)."),
    ("pes_cnae47_pib", "ràtio (0-1)", "Eurostat nama_10r_3gva+nama_10_a64", "Pes del CNAE 47 sobre el PIB de cada CCAA."),
]
for col, unit, tbl, desc in _EEE_CCAA:
    _add(f"eee_ccaa_{col}", f"EEE CCAA — {col}", desc, "INE/Eurostat", tbl,
         "annual", unit, False, False, "eee_ccaa", col, _annual_date, dim_cols=["territori"])

# --- subsectors_dirce (INE T=73019) — no crítica — dim: nom (subsector) ---
_add("subsectors_dirce_empreses", "Subsectors CNAE 47 — empreses (DIRCE)",
     "Nombre d'empreses per subsector CNAE 47 (471-479).",
     "INE", "T=73019", "annual", "nombre d'empreses", False, False,
     "subsectors_dirce", "empreses", _annual_date, dim_cols=["nom"])

# --- subsectors_eas (INE T=76818) — no crítica — dim: nom (subsector) ---
for col, unit, desc in [
    ("n_empreses_eas", "nombre d'empreses", "Empreses per subsector CNAE 47 (font EAS)."),
    ("xifra_negoci", "M EUR", "Xifra de negoci per subsector CNAE 47."),
    ("valor_afegit", "M EUR", "Valor afegit per subsector CNAE 47."),
    ("inversio", "M EUR", "Inversió per subsector CNAE 47."),
    ("personal_ocupat", "persones", "Personal ocupat per subsector CNAE 47."),
]:
    _add(f"subsectors_eas_{col}", f"Subsectors EAS — {col}", desc, "INE", "T=76818",
         "annual", unit, False, False, "subsectors_eas", col, _annual_date, dim_cols=["nom"])

# --- subsectors_472 (INE T=76818, detall alimentació) — no crítica — dim: nom ---
for col, unit, desc in [
    ("n_empreses_eas", "nombre d'empreses", "Empreses per categoria d'alimentació (472)."),
    ("xifra_negoci", "M EUR (preus corrents)", "Xifra de negoci per categoria d'alimentació."),
    ("xifra_negoci_constants", "M EUR (preus constants)", "Xifra de negoci per categoria d'alimentació, preus constants."),
    ("valor_afegit", "M EUR", "Valor afegit per categoria d'alimentació."),
    ("inversio", "M EUR", "Inversió per categoria d'alimentació."),
    ("personal_ocupat", "persones", "Personal ocupat per categoria d'alimentació."),
]:
    _add(f"subsectors_472_{col}", f"Subsectors 472 — {col}", desc, "INE", "T=76818",
         "annual", unit, False, False, "subsectors_472", col, _annual_date, dim_cols=["nom"])

# --- subsectors_epf (INE T=75003) — no crítica — dim: nom (categoria COICOP) ---
_add("subsectors_epf_despesa", "Despesa per llar (EPF, COICOP)",
     "Despesa mitjana per llar, per categoria de consum COICOP.",
     "INE", "T=75003", "annual", "EUR/llar/any", False, False,
     "subsectors_epf", "despesa_per_llar", _annual_date, dim_cols=["nom"])

# --- marges_branca_ine (INE T=76818) — no crítica — dim: branca ---
_add("marges_branca_ine", "Marge sobre vendes per branca",
     "Marge (EBE / xifra de negoci) per branca CNAE 47 a 3 dígits.",
     "INE", "T=76818", "annual", "% sobre vendes", False, False,
     "marges_branca_ine", "marge_vendes_pct", _annual_date, dim_cols=["branca"])

# --- cdmge (INE T=37808) — CRITICAL — dim: indicador (totes les variacions %) ---
_add("cdmge", "Comerç diari grans empreses (CDMGE)",
     "Variacions de vendes diàries de grans empreses del comerç al detall "
     "(diverses finestres de comparació: mensual/anual, vs. mes/any anterior).",
     "INE", "T=37808", "daily", "% variació", True, False,
     "cdmge", "valor", _asis_date, dim_cols=["indicador"])

# --- estructura_retail (Eurostat bd_size) — no crítica — dim: pais ---
_ER_INDIC = {
    "EMP_NR": ("estructura_retail_emp_nr", "persones", "Persones ocupades al comerç al detall (G47), per país."),
    "ENT_NR": ("estructura_retail_ent_nr", "nombre d'empreses", "Nombre d'empreses del comerç al detall (G47), per país."),
    "SAL_NR": ("estructura_retail_sal_nr", "persones", "Nombre d'assalariats al comerç al detall (G47), per país."),
    "ENT_BRTHR_PC": ("estructura_retail_ent_brthr_pc", "% anual", "Taxa de naixement d'empreses (G47), per país."),
    "ENT_DTHR_PC": ("estructura_retail_ent_dthr_pc", "% anual", "Taxa de mort d'empreses (G47), per país."),
    "ENT_BRTHR_DTHR_PC": ("estructura_retail_ent_brthr_dthr_pc", "% anual", "Taxa combinada naixement+mort d'empreses (G47), per país."),
    "GRW_ENT_PC": ("estructura_retail_grw_ent_pc", "% anual", "Taxa de creixement net d'empreses (G47), per país."),
}
for code, (sid, unit, desc) in _ER_INDIC.items():
    SERIES_EXTRA.append(dict(
        serie_id=sid, name=f"Estructura retail UE — {code}", description=desc,
        source="Eurostat", source_table="bd_size", frequency="annual", unit=unit,
        is_critical=False, is_derived=False, is_public=True,
        build=_series_builder("estructura_retail", "valor", _annual_date, dim_cols=["pais"],
                               row_filter=(lambda df, c=code: df["indic_sbs"] == c)),
    ))

# --- estructura_retail_mida (Eurostat bd_size, per mida d'empresa) — no crítica ---
_ERM_INDIC = {
    "EMP_NR": ("estructura_retail_mida_emp_nr", "persones", "Persones ocupades al comerç al detall (G47), per país i mida d'empresa."),
    "ENT_NR": ("estructura_retail_mida_ent_nr", "nombre d'empreses", "Nombre d'empreses del comerç al detall (G47), per país i mida d'empresa."),
}
for code, (sid, unit, desc) in _ERM_INDIC.items():
    SERIES_EXTRA.append(dict(
        serie_id=sid, name=f"Estructura retail UE per mida — {code}", description=desc,
        source="Eurostat", source_table="bd_size", frequency="annual", unit=unit,
        is_critical=False, is_derived=False, is_public=True,
        build=_series_builder("estructura_retail_mida", "valor", _annual_date,
                               dim_cols=["pais", "sizeclas"],
                               row_filter=(lambda df, c=code: df["indic_sbs"] == c)),
    ))

# --- estructura_retail_supervivencia (Eurostat bd_size) — no crítica — dims: pais, age ---
_add("estructura_retail_supervivencia", "Supervivència d'empreses (G47)",
     "Percentatge d'empreses del comerç al detall que sobreviuen N anys després de néixer.",
     "Eurostat", "bd_size", "annual", "% supervivència", False, False,
     "estructura_retail_supervivencia", "survival_pc", _annual_date, dim_cols=["pais", "age"])

# --- estructura_consum (Eurostat nama_10_fcs) — no crítica — dim: pais ---
for col, unit, desc in [
    ("bens_meur", "M EUR", "Consum de les llars en béns, per país."),
    ("serveis_meur", "M EUR", "Consum de les llars en serveis, per país."),
    ("bens_share", "%", "Quota de béns sobre el consum total de les llars, per país."),
    ("serveis_share", "%", "Quota de serveis sobre el consum total de les llars, per país."),
]:
    _add(f"estructura_consum_{col}", f"Estructura consum — {col}", desc, "Eurostat", "nama_10_fcs",
         "annual", unit, False, False, "estructura_consum", col, _annual_date, dim_cols=["pais"])

# --- estructura_comerc (DERIVAT: model propi J3B3) — is_derived=True — dim: tipus ---
for col, unit, desc in [
    ("bens_share", "%", "Quota de béns sobre el consum de les llars (històric + projecció lineal/logit)."),
    ("serveis_share", "%", "Quota de serveis sobre el consum de les llars (històric + projecció)."),
    ("online_pen", "%", "Penetració del canal online sobre el consum de béns (històric + projecció)."),
    ("comerc_fisic_share", "%", "Quota estimada del comerç físic (béns × (1 - penetració online))."),
    ("comerc_fisic_logodds", "%", "Quota estimada del comerç físic, variant log-odds (banda de projecció)."),
]:
    SERIES_EXTRA.append(dict(
        serie_id=f"estructura_comerc_{col}", name=f"Trajectòria estructural — {col}",
        description=f"{desc} MODEL PROPI DE J3B3 (no és font externa): combina Eurostat "
                     "nama_10_fcs (quota béns) i CNMC (penetració online), amb projecció "
                     "lineal + log-odds fins 2035. Citar sempre com a model propi, mai com "
                     "a dada oficial.",
        source="J3B3 (model propi)", source_table="derivat de Eurostat nama_10_fcs + CNMC",
        frequency="annual", unit=unit, is_critical=False, is_derived=True, is_public=True,
        build=_series_builder("estructura_comerc", col, _annual_date, dim_cols=["tipus"]),
    ))


# ─── Exclosos: no encaixen amb l'esquema observations (series temporals) ────
SKIPPED = [
    dict(cache="municipal", reason="Exclòs del chatbot públic (decisió explícita 2026-08-03). "
                                    "Segueix vivint al repo/CSV, no a l'esquema SQL."),
    dict(cache="lideres_empreses", reason="Taula entitat-atribut (63 empreses x mètriques "
                                           "financeres d'un any concret), no una sèrie temporal: "
                                           "no té columna de data per fila (nomes snapshot_any "
                                           "constant), i cada fila és una empresa, no una "
                                           "observació temporal. Necessitaria una taula pròpia "
                                           "(dimensió 'companies'), no observations."),
    dict(cache="prediccions_estructura", reason="Registre d'esdeveniments de predicció, no una "
                                                 "sèrie mesurada: cada fila té 3 dates diferents "
                                                 "(data_prediccio/horitzo/data_resolucio) i "
                                                 "4 valors relacionats (valor/banda/benchmark_flat/"
                                                 "valor_real) que pertanyen a UNA predicció, no a "
                                                 "una seqüència d'observacions. No encaixa amb "
                                                 "'una fila = una observació d'una mètrica'."),
]


def migrate(db_path=DB_PATH, series=None):
    if series is None:
        series = SERIES + SERIES_EXTRA

    con = duckdb.connect(db_path)
    with open(SCHEMA_PATH) as f:
        con.execute(f.read())

    for s in series:
        print(f"  Migrant {s['serie_id']}...")
        tidy = s["build"]()
        tidy = tidy.dropna(subset=["date", "value"]).copy()
        for col in ["dim_1", "dim_2", "dim_3"]:
            if col not in tidy.columns:
                tidy[col] = None
        tidy["serie_id"] = s["serie_id"]
        tidy["frequency"] = s["frequency"]
        tidy["unit"] = s["unit"]
        tidy["source_table"] = s["source_table"]
        tidy["is_critical"] = s["is_critical"]
        tidy["is_derived"] = s["is_derived"]
        tidy["is_public"] = s["is_public"]

        cols = ["serie_id", "date", "frequency", "value", "unit", "dim_1", "dim_2",
                "dim_3", "source_table", "is_critical", "is_derived", "is_public"]
        date_start, date_end = tidy["date"].min(), tidy["date"].max()

        # Ordre: esborrar filles (observations) abans que el pare (series_metadata);
        # inserir pare abans que filles (restriccio FOREIGN KEY).
        con.execute("DELETE FROM observations WHERE serie_id = ?", [s["serie_id"]])
        con.execute("DELETE FROM series_metadata WHERE serie_id = ?", [s["serie_id"]])
        con.execute("""
            INSERT INTO series_metadata
            (serie_id, name, description, source, frequency, date_start, date_end,
             is_critical, is_derived, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [s["serie_id"], s["name"], s["description"], s["source"], s["frequency"],
              date_start, date_end, s["is_critical"], s["is_derived"], s["is_public"]])

        con.register("tidy_df", tidy[cols])
        con.execute("INSERT INTO observations SELECT * FROM tidy_df")
        con.unregister("tidy_df")

        print(f"    {len(tidy)} files, {date_start} .. {date_end}")

    n_series = con.execute("SELECT count(*) FROM series_metadata").fetchone()[0]
    n_obs = con.execute("SELECT count(*) FROM observations").fetchone()[0]
    n_critical = con.execute("SELECT count(*) FROM series_metadata WHERE is_critical").fetchone()[0]
    n_derived = con.execute("SELECT count(*) FROM series_metadata WHERE is_derived").fetchone()[0]
    con.close()

    print(f"\nMigracio completa: {db_path}")
    print(f"  series_metadata: {n_series} sèries ({n_critical} crítiques, {n_derived} derivades)")
    print(f"  observations:    {n_obs} files")
    if SKIPPED:
        print(f"\n  Exclosos ({len(SKIPPED)}):")
        for sk in SKIPPED:
            print(f"    - {sk['cache']}: {sk['reason']}")


if __name__ == "__main__":
    migrate()

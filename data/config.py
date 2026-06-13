"""Codis de taula INE i Eurostat.

Punt únic de referència: quan INE retiri una taula, el canvi és aquí.
Convenci: anotar el codi de taula al missatge de commit quan es modifica un fetcher.
"""

# ─── INE ─────────────────────────────────────────────────────────
INE_TABLES = {
    # PIB / VAB
    69070: "VAB per branques d'activitat (CNR, preus corrents + índex volum)",

    # Empreses (DIRCE / EAS)
    39372: "DIRCE — Empreses CNAE 47 per CCAA + Nacional (sèrie 2008–actual)",
    3954:  "DIRCE — Empreses CNAE 47 Nacional (sèrie llarga)",
    298:   "DIRCE — Empreses CNAE 47 per CCAA (sèrie històrica fins ~2020)",
    73019: "DIRCE — Subsectors CNAE 471–479",
    76818: "EAS — Subsectors CNAE 47",
    4721:  "DIRCE — Empreses municipals (CNAE G+I agregat)",

    # Ocupació
    65123: "EPA — Ocupats per branca d'activitat i sexe (CNAE 47)",

    # Preus
    50902: "IPC general mensual (base 2021=100) — per al deflactor",

    # Estructura empresarial (EEE)
    36194: "EEE Comercio — cifra de negoci nacional per CNAE 47",
    36199: "EEE PyL — compte de pèrdues i guanys",
    76817: "EEE Comercio — per CCAA i branca general",

    # ICM — Índices de Comercio al por Menor (6 taules wstempus)
    60096: "ICM — cifra negoci preus constants, Total Nacional × branca CNAE",
    59787: "ICM — cifra negoci preus corrents, Total Nacional × especials agregats",
    60110: "ICM — cifra negoci preus corrents, CCAA × branca general",
    60111: "ICM — cifra negoci preus constants, CCAA × branca general",
    60114: "ICM — ocupació mensual, Total Nacional × general",
    60115: "ICM — ocupació mensual, Total Nacional × especials agregats",

    # CDMGE — Comptador de Moviments de Grans Empreses
    37808: "CDMGE — variació vendes diàries grans empreses retail",

    # Renda i territori
    30896: "Atlas distribució renda — renda neta municipal",

    # Població
    2915:  "Padró — Població per municipis (sèrie llarga)",
    56934: "Padró — Població per municipis (nova sèrie des de 2002)",

    # Indicadors addicionals
    36499: "ICC — Índex de Confiança del Consumidor mensual",
    75003: "EPF COICOP — despesa llars en alimentació i vestuari",
    28185: "EAES — Enquesta Anual d'Estructura Salarial",
}

# ─── Eurostat ─────────────────────────────────────────────────────
EUROSTAT_DATASETS = {
    "nama_10_a64":   "Comptes nacionals per 64 branques — VAB per país (CNAE G47)",
    "nama_10r_3gva": "Comptes nacionals regionals — VAB per NUTS-3",
    "prc_ppp_ind":   "Paritats de poder adquisitiu (PPP)",
    "bd_size":       "Demografía empresarial per mida (empreses, assalariats, VAB, supervivència)",
    "sts_trtu_m":    "Estadística conjuntural — volum vendes retail mensual (base 2021=100)",
    "lfsa_egan22d":  "EPA europea — Ocupació per activitat NACE (CNAE 47)",
}
# Codis isoc_* (digitalització): múltiples datasets, veure fetchers/eurostat.py fetch_digitalitzacio_comerc()

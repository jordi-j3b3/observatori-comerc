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
    301:   "DIRCE — Locals per província, divisió CNAE 47 (sèrie 2010–actual)",
    294:   "DIRCE — Locals per CCAA, grups CNAE 471–479 (sèrie 2010–actual)",

    # Ocupació (EPA — ocupats CNAE 47 net; aturats/hores nomes a seccio G)
    65123: "EPA — Ocupats per branca d'activitat i sexe (CNAE 47 net)",
    65249: "EPA — Aturats per branca d'activitat i sexe (nomes secció G, no arriba a CNAE 47)",
    65159: "EPA — Mitjana d'hores efectives setmanals per branca i sexe (nomes secció G)",

    # Preus
    50902: "IPC general mensual (base 2021=100) — per al deflactor",
    76125: "IPC per grups ECOICOP ver.2, nacional, mensual (alimentació/vestit/llar/general)",

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
    29005: "Padró — Xifres oficials per municipi (1996–actual), sumades per província",

    # Indicadors addicionals
    # (Índex de Confiança del Consumidor: cap taula INE — la taula 36499 antiga
    # ja no existeix (404). Font real: Eurostat ei_bsco_m, vegeu EUROSTAT_DATASETS.)
    75003: "EPF COICOP — despesa llars en alimentació i vestuari",
    28185: "EAES — Enquesta Anual d'Estructura Salarial",
}

# ─── Trencaments de sèrie del DIRCE ─────────────────────────────────
# Primer any (foto a 1 de gener) d'una base nova. Una comparació entre dos anys
# travessa el trencament si l'any base és anterior i l'any final és igual o
# posterior. Punt únic per a tots els consumidors: processor (columnes
# travessa_trencament / nota_trencament dels CSV), corpus DuckDB i pàgines.
#   2023: el cens de CNAE 47 cau d'un any per l'altre molt més que qualsevol
#         altre any de la sèrie (empreses −35.318; locals −6,6%). Canvi
#         metodològic no verificat.
# Quan arribi l'edició en CNAE-2025 (prevista el desembre de 2026), afegir-hi
# l'any de referència corresponent.
TRENCAMENTS_DIRCE = [2023]


def trencaments_travessats(any_base, any_final, trencaments=TRENCAMENTS_DIRCE):
    """Anys de trencament que queden entre any_base (exclòs) i any_final (inclòs)."""
    lo, hi = sorted((int(any_base), int(any_final)))
    return [t for t in trencaments if lo < t <= hi]


def nota_trencament_dirce(trencaments=TRENCAMENTS_DIRCE):
    """Text d'avís per a sèries del DIRCE, o None si no n'hi ha cap."""
    if not trencaments:
        return None
    anys = ", ".join(str(t) for t in trencaments)
    return (f"Trencament de sèrie DIRCE a {anys}: les xifres d'abans i d'après no "
            f"són comparables. Cap variació que travessi aquest any es pot "
            f"presentar sense avís.")

# ─── Eurostat ─────────────────────────────────────────────────────
EUROSTAT_DATASETS = {
    "nama_10_a64":   "Comptes nacionals per 64 branques — VAB per país (CNAE G47)",
    "nama_10r_3gva": "Comptes nacionals regionals — VAB per NUTS-3",
    "prc_ppp_ind":   "Paritats de poder adquisitiu (PPP)",
    "bd_size":       "Demografía empresarial per mida (empreses, assalariats, VAB, supervivència)",
    "sts_trtu_m":    "Estadística conjuntural — volum vendes retail mensual (base 2021=100)",
    "lfsa_egan22d":  "EPA europea — Ocupació per activitat NACE (CNAE 47)",
    "ei_bsco_m":     "Índex de confiança del consumidor (Business and Consumer Surveys, ES)",
}
# Codis isoc_* (digitalització): múltiples datasets, veure fetchers/eurostat.py fetch_digitalitzacio_comerc()

"""
Client API per Eurostat.
Documentació: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access
"""
import requests
import pandas as pd

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

COUNTRIES = [
    "EU27_2020", "EA20", "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL",
    "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT",
    "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE",
]

COUNTRY_NAMES = {
    "EU27_2020": "UE-27", "EA20": "Eurozona", "BE": "Belgica", "BG": "Bulgaria",
    "CZ": "Txequia", "DK": "Dinamarca", "DE": "Alemanya", "EE": "Estonia",
    "IE": "Irlanda", "EL": "Grecia", "ES": "Espanya", "FR": "Franca",
    "HR": "Croacia", "IT": "Italia", "CY": "Xipre", "LV": "Letonia",
    "LT": "Lituania", "LU": "Luxemburg", "HU": "Hongria", "MT": "Malta",
    "NL": "Paisos Baixos", "AT": "Austria", "PL": "Polonia", "PT": "Portugal",
    "RO": "Romania", "SI": "Eslovenia", "SK": "Eslovaquia", "FI": "Finlandia",
    "SE": "Suecia",
}


def _fetch_eurostat(dataset, params):
    """Descarrega dades de l'API REST d'Eurostat.
    params pot ser un dict o una llista de tuples (per parametres repetits com geo).
    """
    url = f"{BASE_URL}/{dataset}"

    # Convertir a llista de tuples per suportar parametres repetits
    if isinstance(params, dict):
        # Si geo es una llista, expandir-la
        param_list = []
        for k, v in params.items():
            if isinstance(v, list):
                for item in v:
                    param_list.append((k, item))
            else:
                param_list.append((k, v))
        params = param_list

    params.append(("format", "JSON"))
    params.append(("lang", "en"))

    resp = requests.get(url, params=params, timeout=120)
    if resp.status_code != 200:
        print(f"Eurostat error {resp.status_code}: {resp.text[:200]}")
        return None
    return resp.json()


def _parse_eurostat_json(data):
    """
    Parseja el format JSON-stat d'Eurostat a un DataFrame.
    """
    if not data or "value" not in data:
        return pd.DataFrame()

    dims = data.get("dimension", {})
    sizes = data.get("size", [])
    dim_ids = data.get("id", [])
    values = data.get("value", {})

    # Construir mapeig d'índex a combinació de dimensions
    dim_labels = {}
    for dim_id in dim_ids:
        dim_info = dims.get(dim_id, {})
        cat = dim_info.get("category", {})
        idx = cat.get("index", {})
        label = cat.get("label", {})
        # Ordenar per índex
        sorted_keys = sorted(idx.items(), key=lambda x: x[1])
        dim_labels[dim_id] = [k for k, v in sorted_keys]

    rows = []
    total = 1
    for s in sizes:
        total *= s

    for flat_idx_str, val in values.items():
        flat_idx = int(flat_idx_str)
        row = {}
        remainder = flat_idx
        for i in range(len(dim_ids) - 1, -1, -1):
            dim_size = len(dim_labels[dim_ids[i]])
            pos = remainder % dim_size
            remainder //= dim_size
            row[dim_ids[i]] = dim_labels[dim_ids[i]][pos]
        row["valor"] = val
        rows.append(row)

    return pd.DataFrame(rows)


def fetch_vab_cnae47():
    """
    Dataset nama_10_a64: VAB del CNAE 47 per país (preus corrents i encadenats).
    """
    params = {
        "nace_r2": "G47",
        "na_item": "B1G",  # Value added, gross
        "unit": "CP_MEUR",  # Current prices, million euro
        "geo": COUNTRIES,  # Llista -> parametres repetits
    }

    data = _fetch_eurostat("nama_10_a64", params)
    df = _parse_eurostat_json(data)
    if df.empty:
        return df

    df = df.rename(columns={"time": "any", "TIME_PERIOD": "any", "geo": "pais_codi"})
    df["pais"] = df["pais_codi"].map(COUNTRY_NAMES)
    df["any"] = pd.to_numeric(df["any"], errors="coerce")
    df["vab_meur"] = pd.to_numeric(df["valor"], errors="coerce")

    return df[["pais", "pais_codi", "any", "vab_meur"]].dropna()


def fetch_vab_total():
    """
    Dataset nama_10_a64: VAB total per país (per calcular pes CNAE 47).
    """
    params = {
        "nace_r2": "TOTAL",
        "na_item": "B1G",
        "unit": "CP_MEUR",
        "geo": COUNTRIES,
    }

    data = _fetch_eurostat("nama_10_a64", params)
    df = _parse_eurostat_json(data)
    if df.empty:
        return df

    df = df.rename(columns={"time": "any", "TIME_PERIOD": "any", "geo": "pais_codi"})
    df["pais"] = df["pais_codi"].map(COUNTRY_NAMES)
    df["any"] = pd.to_numeric(df["any"], errors="coerce")
    df["vab_total_meur"] = pd.to_numeric(df["valor"], errors="coerce")

    return df[["pais", "pais_codi", "any", "vab_total_meur"]].dropna()


def fetch_ppp():
    """
    Dataset prc_ppp_ind: Paritats de poder adquisitiu i índexs de preus.
    """
    params = {
        "na_item": "PLI_EU27_2020",  # Price level indices
        "ppp_cat": "A0101",  # Actual individual consumption
        "geo": COUNTRIES,
    }

    data = _fetch_eurostat("prc_ppp_ind", params)
    df = _parse_eurostat_json(data)
    if df.empty:
        return df

    df = df.rename(columns={"time": "any", "TIME_PERIOD": "any", "geo": "pais_codi"})
    df["pais"] = df["pais_codi"].map(COUNTRY_NAMES)
    df["any"] = pd.to_numeric(df["any"], errors="coerce")
    df["index_preus"] = pd.to_numeric(df["valor"], errors="coerce")

    return df[["pais", "pais_codi", "any", "index_preus"]].dropna()


def fetch_empreses_ue():
    """
    Dataset bd_size: Nombre d'empreses CNAE 47 per país.
    """
    params = {
        "nace_r2": "G47",
        "indic_sb": "V11910",  # Number of enterprises
        "sizeclas": "TOTAL",
        "geo": COUNTRIES,
    }

    data = _fetch_eurostat("bd_size", params)
    df = _parse_eurostat_json(data)
    if df.empty:
        return df

    df = df.rename(columns={"time": "any", "TIME_PERIOD": "any", "geo": "pais_codi"})
    df["pais"] = df["pais_codi"].map(COUNTRY_NAMES)
    df["any"] = pd.to_numeric(df["any"], errors="coerce")
    df["empreses"] = pd.to_numeric(df["valor"], errors="coerce")

    return df[["pais", "pais_codi", "any", "empreses"]].dropna()


if __name__ == "__main__":
    print("Testejant API Eurostat...")

    print("\n1. VAB CNAE 47 per país:")
    df = fetch_vab_cnae47()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df[df["pais_codi"] == "ES"].head())

    print("\n2. PPP:")
    df = fetch_ppp()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df[df["pais_codi"] == "ES"].head())

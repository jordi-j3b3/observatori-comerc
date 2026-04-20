"""
Client API per l'OCDE (OECD Data Explorer).
Dades de digitalització d'empreses (ICT Usage).
"""
import requests
import pandas as pd
import io

BASE_URL = "https://sdmx.oecd.org/public/rest/data"


def fetch_ict_businesses():
    """
    Descarrega dades d'ús de TIC per empreses del comerç (CNAE 47).
    Empreses amb web i amb venda online, Espanya.
    """
    # Dataset: ICT Business usage
    url = (
        f"{BASE_URL}/OECD.STI.DEP/DSD_ICT_B@DF_BUSINESSES/1.0/"
        "ESP.A.B2_B+B1_B..G47+_T.S_GE10"
    )
    params = {
        "format": "csvfilewithlabels",
        "startPeriod": "2005",
    }

    resp = requests.get(url, params=params, timeout=60)
    if resp.status_code != 200:
        print(f"OCDE error {resp.status_code}: {resp.text[:200]}")
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(resp.text))
    if df.empty:
        return df

    # Simplificar columnes
    col_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if "time" in col_lower and "period" in col_lower:
            col_map[col] = "any"
        elif "obs_value" in col_lower or "obs" == col_lower:
            col_map[col] = "valor"
        elif "measure" in col_lower and "label" in col_lower:
            col_map[col] = "indicador"
        elif "activity" in col_lower and "label" in col_lower:
            col_map[col] = "activitat"

    df = df.rename(columns=col_map)

    cols_to_keep = [c for c in ["any", "valor", "indicador", "activitat"] if c in df.columns]
    if not cols_to_keep:
        return df

    df = df[cols_to_keep].copy()
    df["any"] = pd.to_numeric(df.get("any"), errors="coerce")
    df["valor"] = pd.to_numeric(df.get("valor"), errors="coerce")

    return df.dropna(subset=["any", "valor"])


if __name__ == "__main__":
    print("Testejant API OCDE...")

    print("\n1. ICT Businesses (Espanya):")
    df = fetch_ict_businesses()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df.head(10))

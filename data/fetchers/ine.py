"""
Client API per l'Instituto Nacional de Estadística (INE).
Documentació: https://www.ine.es/dyngs/DAB/en/index.htm?cid=1102
"""
import requests
import pandas as pd
import time
import os

BASE_URL = "https://servicios.ine.es/wstempus/js/ES"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")


def _fetch_table(table_id, nult=None, retries=3):
    """Descarrega una taula de l'INE amb reintentos per peticions en cua."""
    url = f"{BASE_URL}/DATOS_TABLA/{table_id}"
    params = {}
    if nult:
        params["nult"] = nult

    for attempt in range(retries):
        resp = requests.get(url, params=params, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and data.get("Status") == "En proceso":
                time.sleep(10)
                continue
            return data
        elif resp.status_code == 429:
            time.sleep(30)
        else:
            resp.raise_for_status()

    raise Exception(f"No s'han pogut obtenir dades de la taula {table_id} després de {retries} intents")


def _parse_ine_series(data):
    """Converteix la resposta JSON de l'INE a un DataFrame."""
    rows = []
    if not isinstance(data, list):
        return pd.DataFrame()

    for serie in data:
        nombre = serie.get("Nombre", "")
        for obs in serie.get("Data", []):
            rows.append({
                "serie": nombre,
                "any": obs.get("Anyo"),
                "periode": obs.get("FK_Periodo"),
                "valor": obs.get("Valor"),
            })

    return pd.DataFrame(rows)


def fetch_vab_ramas():
    """
    Taula 69070: VAB per branques d'activitat.
    Retorna Total CNAE i CNAE 47 en:
      - Preus corrents (Dato base, M EUR)
      - Index volum encadenat (per calcular preus constants)
    IMPORTANT: cal nult=30 per obtenir la serie completa (1995-2023).
    """
    data = _fetch_table(69070, nult=30)
    if not isinstance(data, list):
        return pd.DataFrame()

    results = []
    for serie in data:
        nombre = serie.get("Nombre", "")

        # ── VAB Preus corrents (Dato base, M EUR) ──
        if "Dato base" in nombre and "Precios corrientes" in nombre:
            if nombre.startswith("Total Nacional. Valor añadido bruto. Total CNAE"):
                indicador = "vab_total_corrents"
            elif "Comercio al por menor, excepto" in nombre and nombre.startswith("Total Nacional"):
                indicador = "vab_cnae47_corrents"
            else:
                continue

        # ── Index volum encadenat (per preus constants) ──
        elif "volumen encadenados" in nombre and "Índice." in nombre:
            if "Total CNAE" in nombre:
                indicador = "idx_volum_total"
            elif "Comercio al por menor, excepto" in nombre:
                indicador = "idx_volum_cnae47"
            else:
                continue
        else:
            continue

        for obs in serie.get("Data", []):
            val = obs.get("Valor")
            if val is not None:
                results.append({
                    "indicador": indicador,
                    "any": obs.get("Anyo"),
                    "valor": val,
                })

    return pd.DataFrame(results)


def fetch_empreses(ccaa=None):
    """
    Empreses actives CNAE 47 per territori.
    Combina dues fonts per obtenir la sèrie més completa (fins 2025):

    1. Taula 3954 (Nacional): "Total Nacional. Comercio al por menor...Todas las edades. Empresas."
       Dóna la sèrie nacional amb dades fins a l'any actual.

    2. Taula 39372 (CCAA + Nacional, 3 dígits CNAE): "{CCAA}. Total. 47 Comercio al por menor..."
       Dóna Nacional + totes les CCAA amb dades fins a l'any actual.

    Fallback: Taula 298 (històrica, fins ~2020).
    """
    results = []

    # ── Font principal: Taula 39372 (CCAA + Nacional fins 2025) ──
    print("    Intentant taula 39372 (CCAA + Nacional)...")
    try:
        data_ccaa = _fetch_table(39372, nult=20)
        if isinstance(data_ccaa, list):
            for serie in data_ccaa:
                nombre = serie.get("Nombre", "")
                # Nacional: "Nacional. Total. Total. 47 Comercio al por menor..."
                if "Nacional. Total. Total. 47 Comercio al por menor" in nombre:
                    for obs in serie.get("Data", []):
                        results.append({"territori": "espanya", "any": obs.get("Anyo"), "empreses": obs.get("Valor")})
                # CCAA: "{CCAA}. Total. 47 Comercio al por menor..." (sense "Total. Total.")
                elif ". Total. 47 Comercio al por menor" in nombre and ". Total. Total." not in nombre and "Nacional" not in nombre:
                    terr = nombre.split(".")[0].strip()
                    for obs in serie.get("Data", []):
                        results.append({"territori": terr, "any": obs.get("Anyo"), "empreses": obs.get("Valor")})
            print(f"    Taula 39372: {len(results)} registres")
    except Exception as e:
        print(f"    Error taula 39372: {e}")

    # ── Complementar Nacional amb Taula 3954 (sèrie més llarga) ──
    print("    Intentant taula 3954 (Nacional històric)...")
    try:
        data_nac = _fetch_table(3954, nult=30)
        if isinstance(data_nac, list):
            # Anys que ja tenim de la taula 39372 per evitar duplicats
            anys_existents = {r["any"] for r in results if r["territori"] == "espanya"}
            count_new = 0
            for serie in data_nac:
                nombre = serie.get("Nombre", "")
                if "Comercio al por menor" in nombre and "Todas las edades" in nombre:
                    for obs in serie.get("Data", []):
                        any_ = obs.get("Anyo")
                        if any_ not in anys_existents:
                            results.append({"territori": "espanya", "any": any_, "empreses": obs.get("Valor")})
                            count_new += 1
                    break
            print(f"    Taula 3954: {count_new} anys addicionals")
    except Exception as e:
        print(f"    Error taula 3954: {e}")

    # ── Complement: Taula 298 (històrica, CCAA fins ~2020) ──
    print("    Complementant amb taula 298 (CCAA històric)...")
    try:
        data_old = _fetch_table(298, nult=20)
        if isinstance(data_old, list):
            anys_existents_all = {(r["territori"], r["any"]) for r in results}
            count_298 = 0
            for serie in data_old:
                nombre = serie.get("Nombre", "")
                if ". Total. Total. 47 Comercio" in nombre and nombre.startswith("Nacional"):
                    terr = "espanya"
                elif ". Total. 47 Comercio" in nombre and ". Total. Total." not in nombre and not nombre.startswith("Nacional"):
                    terr = nombre.split(".")[0].strip()
                else:
                    continue
                for obs in serie.get("Data", []):
                    key = (terr, obs.get("Anyo"))
                    if key not in anys_existents_all:
                        results.append({"territori": terr, "any": obs.get("Anyo"), "empreses": obs.get("Valor")})
                        count_298 += 1
            print(f"    Taula 298: {count_298} registres addicionals")
    except Exception as e:
        print(f"    Error taula 298: {e}")

    return pd.DataFrame(results)


def fetch_ocupacio():
    """
    Taula 65123: Ocupats per sexe i branca d'activitat.
    Retorna ocupats CNAE 47 trimestral.
    """
    data = _fetch_table(65123, nult=20)

    results = []
    if not isinstance(data, list):
        return pd.DataFrame()

    for serie in data:
        nombre = serie.get("Nombre", "")
        if "47" not in nombre:
            continue
        if "Ambos sexos" not in nombre and "Total" not in nombre:
            continue

        for obs in serie.get("Data", []):
            results.append({
                "any": obs.get("Anyo"),
                "trimestre": obs.get("FK_Periodo"),
                "ocupats_milers": obs.get("Valor"),
            })

    return pd.DataFrame(results)


def fetch_ipc():
    """
    Taula 50902: IPC general, mensual. Base 2021 = 100.
    Retorna index IPC mensual per calcular deflactor.
    IMPORTANT: nult=400 per obtenir serie completa (1995-2025, ~360 mesos).
    Filtra nomes la serie "Total Nacional. Indice general. Indice."
    """
    data = _fetch_table(50902, nult=400)

    results = []
    if not isinstance(data, list):
        return pd.DataFrame()

    for serie in data:
        nombre = serie.get("Nombre", "")
        if "ndice general" not in nombre or "ndice." not in nombre.split("general")[-1]:
            continue
        if "Variaci" in nombre:
            continue

        for obs in serie.get("Data", []):
            val = obs.get("Valor")
            if val is not None:
                results.append({
                    "any": obs.get("Anyo"),
                    "mes": obs.get("FK_Periodo"),
                    "ipc": val,
                })
        break  # Nomes una serie

    return pd.DataFrame(results)


def fetch_eee_comercio():
    """
    Taula 36194: Estadistica Estructural d'Empreses - Sector Comercio.
    Principals magnituds CNAE 47 (Comercio al por menor).
    Retorna: xifra negoci, valor afegit, personal ocupat, hores treballades.
    Unitats: milers EUR (xifra/va), persones, milers hores.
    """
    data = _fetch_table(36194, nult=10)
    if not isinstance(data, list):
        return pd.DataFrame()

    # Mapeig de noms de serie a columnes
    MAGNITUDS = {
        "Cifra de negocios": "xifra_negoci",
        "Valor añadido a coste de los factores": "valor_afegit",
        "Personal ocupado": "personal_ocupat",
        "Horas trabajadas por el personal remunerado": "hores_treballades",
        "Gastos de personal": "gastos_personal",
    }

    results = {}
    for serie in data:
        nombre = serie.get("Nombre", "")
        if "Comercio al por menor, excepto" not in nombre:
            continue

        # Identificar magnitud
        col_name = None
        for key, col in MAGNITUDS.items():
            if key in nombre:
                col_name = col
                break
        if not col_name:
            continue

        for obs in serie.get("Data", []):
            val = obs.get("Valor")
            any_ = obs.get("Anyo")
            if val is not None and any_ is not None:
                if any_ not in results:
                    results[any_] = {"any": any_}
                results[any_][col_name] = val

    df = pd.DataFrame(list(results.values()))
    if not df.empty:
        df = df.sort_values("any").reset_index(drop=True)
        # Convertir unitats: milers EUR -> EUR per xifra, va i gastos
        for col in ["xifra_negoci", "valor_afegit", "gastos_personal"]:
            if col in df.columns:
                df[col] = df[col] * 1000  # milers EUR -> EUR
        # Hores: milers hores -> hores
        if "hores_treballades" in df.columns:
            df["hores_treballades"] = df["hores_treballades"] * 1000

    return df


def fetch_poblacio():
    """
    Població per CCAA i Nacional.
    Combina dues fonts:
      - Taula 2915 (Padrón): Nacional + CCAA (1996-2021)
      - Taula 56934 (Cifras de Población): Nacional (2022-2025)
    Per CCAA 2022-2025 s'estima amb la proporció del 2021 aplicada
    sobre el total nacional dels anys recents (error < 0.5%).
    """
    results = []

    # ── Taula 2915: Padrón (CCAA + Nacional fins 2021) ──
    data = _fetch_table(2915, nult=30)
    if isinstance(data, list):
        for serie in data:
            nombre = serie.get("Nombre", "")
            if "Total Nacional. Total municipios. Personas. Total" in nombre:
                terr = "espanya"
            elif "Personas. Total. Total municipios." in nombre:
                terr = nombre.split("Total municipios.")[-1].strip().rstrip(".")
            else:
                continue
            for obs in serie.get("Data", []):
                results.append({"territori": terr, "any": obs.get("Anyo"), "poblacio": obs.get("Valor")})

    # ── Taula 56934: Cifras de Población Nacional (2022-2025) ──
    anys_nac = {r["any"] for r in results if r["territori"] == "espanya"}
    try:
        data2 = _fetch_table(56934, nult=20)
        if isinstance(data2, list):
            for serie in data2:
                nombre = serie.get("Nombre", "")
                if "Total Nacional. Todas las edades. Total. Población. Número" in nombre:
                    by_year = {}
                    for o in serie.get("Data", []):
                        y = o.get("Anyo")
                        p = o.get("FK_Periodo", 0)
                        if y and (y not in by_year or p > by_year[y][1]):
                            by_year[y] = (o.get("Valor"), p)
                    for y, (v, _) in by_year.items():
                        if y not in anys_nac:
                            results.append({"territori": "espanya", "any": y, "poblacio": v})
                    break
    except Exception:
        pass

    df = pd.DataFrame(results)
    if df.empty:
        return df

    # ── Estimar CCAA per anys recents amb proporció 2021 ──
    ccaa_names = [t for t in df["territori"].unique() if t != "espanya"]
    last_padron_year = df[df["territori"].isin(ccaa_names)]["any"].max()
    esp_series = df[df["territori"] == "espanya"].set_index("any")["poblacio"]
    anys_nous = [y for y in esp_series.index if y > last_padron_year]

    if anys_nous and last_padron_year in esp_series.index:
        total_ref = esp_series[last_padron_year]
        for ccaa in ccaa_names:
            pob_ref = df[(df["territori"] == ccaa) & (df["any"] == last_padron_year)]["poblacio"].values
            if len(pob_ref) > 0:
                prop = pob_ref[0] / total_ref
                for y in anys_nous:
                    results.append({"territori": ccaa, "any": y, "poblacio": round(esp_series[y] * prop)})

    return pd.DataFrame(results)


def fetch_confianza():
    """
    Taula 36499: Índex de confiança del consumidor.
    """
    data = _fetch_table(36499, nult=20)

    results = []
    if not isinstance(data, list):
        return pd.DataFrame()

    for serie in data:
        nombre = serie.get("Nombre", "")
        if "confianza" not in nombre.lower() and "global" not in nombre.lower():
            continue

        for obs in serie.get("Data", []):
            results.append({
                "any": obs.get("Anyo"),
                "mes": obs.get("FK_Periodo"),
                "index_confianza": obs.get("Valor"),
            })

    return pd.DataFrame(results)


def fetch_eee_comercio_ccaa():
    """
    Taula 76817: EEE Sector Comercio — magnituds regionalitzades.
    CNAE 47 per CCAA (2018-2024).
    Retorna: xifra_negoci, personal_ocupat, sous_salaris, inversio, locals
    per cada CCAA i Total Nacional.
    Unitats: milers EUR (xifra/sous/inversio), persones, unitats.
    """
    data = _fetch_table(76817, nult=10)
    if not isinstance(data, list):
        return pd.DataFrame()

    MAGNITUDS = {
        "Cifra de negocios": "xifra_negoci",
        "Sueldos y salarios": "sous_salaris",
        "Personal ocupado": "personal_ocupat",
        "Inversión en activos materiales": "inversio",
        "Número de locales": "locals",
    }

    TERR_NORM = {
        "Asturias, Principado de": "Asturias (Principado de)",
        "Balears, Illes": "Balears (Illes)",
        "Madrid, Comunidad de": "Madrid (Comunidad de)",
        "Murcia, Región de": "Murcia (Región de)",
        "Navarra, Comunidad Foral de": "Navarra (Comunidad Foral de)",
        "Rioja, La": "Rioja (La)",
        "Total Nacional": "espanya",
    }

    results = {}
    for serie in data:
        nombre = serie.get("Nombre", "")
        if "Comercio al por menor, excepto" not in nombre:
            continue

        terr_raw = nombre.split(".")[0].strip()
        if terr_raw in ("Ceuta", "Melilla"):
            continue
        terr = TERR_NORM.get(terr_raw, terr_raw)

        col_name = None
        for key, col in MAGNITUDS.items():
            if key in nombre:
                col_name = col
                break
        if not col_name:
            continue

        for obs in serie.get("Data", []):
            val = obs.get("Valor")
            any_ = obs.get("Anyo")
            if val is not None and any_ is not None:
                key = (terr, any_)
                if key not in results:
                    results[key] = {"territori": terr, "any": any_}
                results[key][col_name] = val

    df = pd.DataFrame(list(results.values()))
    if not df.empty:
        df = df.sort_values(["territori", "any"]).reset_index(drop=True)
        for col in ["xifra_negoci", "sous_salaris", "inversio"]:
            if col in df.columns:
                df[col] = df[col] * 1000

    return df


if __name__ == "__main__":
    print("Testejant API INE...")

    print("\n1. VAB per branques:")
    df = fetch_vab_ramas()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df.head())

    print("\n2. Empreses:")
    df = fetch_empreses()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df.head())

    print("\n3. Ocupació:")
    df = fetch_ocupacio()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df.head())

    print("\n4. EEE Comercio CCAA:")
    df = fetch_eee_comercio_ccaa()
    print(f"   {len(df)} registres")
    if not df.empty:
        print(df.head(10))

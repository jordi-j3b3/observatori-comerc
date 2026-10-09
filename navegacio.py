"""Enllaços de les novetats de la portada cap a la pàgina i la pestanya on es veu cada dataset.

La portada desa la destinació a st.session_state i fa st.switch_page; la pàgina
de destí crida tab_destinacio() per obrir directament la pestanya bona. Es fa
per sessió i no per URL perquè una URL nova recarregaria l'app i perdria l'idioma.
"""
import streamlit as st

# dataset de updates_log.json -> (fitxer de la pàgina, índex de la pestanya o None)
DESTINS = {
    "cdmge":                           ("pages/0a_Pols_diari.py", None),
    "icm":                             ("pages/0b_ICM.py", 0),
    "icm_distribucion":                ("pages/0b_ICM.py", 3),
    "confianza_consumidor":            ("pages/0b_ICM.py", 4),
    "ipc_coicop":                      ("pages/0b_ICM.py", 5),
    "targetes_tpv":                    ("pages/0b_ICM.py", 6),
    "pib_vab":                         ("pages/1_PIB_i_VAB.py", 0),
    "empreses":                        ("pages/2_Empreses.py", 0),
    "ocupacio_comerc":                 ("pages/3_Ocupació.py", 2),
    "eaes":                            ("pages/3_Ocupació.py", 1),
    "epa_retail":                      ("pages/3_Ocupació.py", 3),
    "productivitat":                   ("pages/4_Productivitat.py", 0),
    "marges_branca_ine":               ("pages/4_Productivitat.py", 2),
    "ecommerce":                       ("pages/5_Ecommerce.py", 0),
    "digitalitzacio_comerc":           ("pages/5_Ecommerce.py", 1),
    "eee_ccaa":                        ("pages/6_Territori.py", 0),
    "europa_vab":                      ("pages/7_Comparativa_Europa.py", 0),
    "estructura_retail":               ("pages/7_Comparativa_Europa.py", 2),
    "estructura_retail_mida":          ("pages/7_Comparativa_Europa.py", 2),
    "estructura_retail_supervivencia": ("pages/7_Comparativa_Europa.py", 2),
    "europa_retail_mensual":           ("pages/7_Comparativa_Europa.py", 3),
    "subsectors_dirce":                ("pages/9_Subsectors.py", 0),
    "subsectors_eas":                  ("pages/9_Subsectors.py", 1),
    "subsectors_epf":                  ("pages/9_Subsectors.py", 2),
    "subsectors_472":                  ("pages/9_Subsectors.py", 3),
    "estructura_consum":               ("pages/E_Estructura.py", 1),
    # "ipc" (deflactor anual) no té pàgina pròpia: la novetat surt sense enllaç
}

_CLAU = "_nav_destinacio"


def anar_a(dataset):
    """Desa la pestanya de destí i canvia de pàgina. Cridar quan es clica la novetat."""
    pagina, tab = DESTINS[dataset]
    st.session_state[_CLAU] = (pagina, tab)
    st.switch_page(pagina)


def oblidar_destinacio():
    """La portada l'esborra a cada càrrega: la pestanya forçada només val per a un salt."""
    st.session_state.pop(_CLAU, None)


def tab_destinacio(pagina, labels):
    """Etiqueta de la pestanya que s'ha d'obrir, o None si no s'hi arriba des d'una novetat.

    No s'esborra en llegir-la: si el valor de default canviés entre reruns de la
    mateixa pàgina, Streamlit podria tornar a la primera pestanya.
    """
    desti = st.session_state.get(_CLAU)
    if not desti or desti[0] != pagina or desti[1] is None:
        return None
    return labels[desti[1]] if desti[1] < len(labels) else None

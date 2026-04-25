"""Pàgina 7: Aspectes Metodològics"""
import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header, page_meta, PURPLE

inject_css()
t = setup_lang(show_selector=False)
page_header()

if st.session_state.lang == "ca":
    st.title("Aspectes metodològics")
    st.markdown("""
    Aquesta secció detalla els criteris de càlcul i les decisions metodològiques
    adoptades en l'elaboració dels indicadors de l'Observatori. L'objectiu és garantir
    la **transparència** i la **reproductibilitat** de tots els resultats presentats.
    """)

    st.markdown("---")

    # ── Deflactor IPC ──
    st.subheader("1. Deflació amb IPC: conversió a preus constants")
    st.markdown("""
    **Objectiu:** Eliminar l'efecte de la inflació per comparar magnituds econòmiques al llarg del temps.

    **Font del deflactor:** IPC general mensual publicat per l'INE (Taula 50902), base oficial 2021 = 100.

    **Procediment:**
    1. Es calcula la **mitjana anual** de l'IPC mensual per a cada any.
    2. Es defineix com a **any base** el primer any amb dades disponibles (2002 per al VAB; 2018 per a la productivitat).
    3. El deflactor es calcula com: `IPC_any / IPC_any_base`.
    4. El valor real es calcula com: `Valor_nominal / Deflactor`.

    **Resultat:** Amb aquesta base, el valor real coincideix amb el nominal l'any base,
    i els valors reals sempre són iguals o inferiors als nominals (ja que la inflació acumulada
    des de l'any base és positiva). Això evita la confusió visual que generaria un any base posterior
    (com 2021) on els valors reals pre-base superarien els nominals.

    **Nota:** El deflactor utilitzat és l'IPC general, no un deflactor sectorial específic.
    Això és una simplificació habitual en anàlisis sectorials quan no es disposa d'un deflactor
    específic per al CNAE 47. L'IPC general és una aproximació raonable atès que el comerç al
    detall és un dels principals components de la cistella de l'IPC.
    """)

    # ── Productivitat ──
    st.subheader("2. Càlcul de la productivitat")
    st.markdown("""
    **Font:** Estadística Estructural d'Empreses (EEE) de l'INE, Taula 36194 — Sector Comerç.

    **Indicadors:**
    - **VA/hora** (Valor Afegit per hora) = `Valor Afegit a cost de factors (preus constants) / Hores treballades`
    - **Xifra de Negoci/hora** = `Xifra de Negoci (preus constants) / Hores treballades`

    El Valor Afegit i la Xifra de Negoci es deflacten amb l'IPC (base 2018, primer any EEE disponible)
    abans de dividir per les hores treballades. Així es mesura la productivitat **real**,
    no l'aparent creixement per pujada de preus.

    **Interpretació de la divergència:**
    - Si VA/hora creix més que Xifra de Negoci/hora → **millora de marges** (el sector reté més valor net).
    - Si Xifra de Negoci/hora creix més → **compressió de marges** (més facturació però menys valor retingut).
    """)

    # ── Distribució VAB ──
    st.subheader("3. Distribució del Valor Afegit: quota salarial i excedent brut")
    st.markdown("""
    **Font:** EEE de l'INE, Taula 36194 — magnituds "Valor añadido a coste de los factores"
    i "Gastos de personal" per al CNAE 47.

    **Indicadors:**
    - **Quota salarial** = `Gastos de personal / Valor Afegit` (proporció del VA destinada a remunerar treballadors).
    - **Excedent brut d'explotació** = `Valor Afegit − Gastos de personal` (beneficis empresarials + amortitzacions + impostos).
    - **Cost laboral per ocupat** = `Gastos de personal (preus constants) / Personal ocupat`.
    - **Cost laboral per hora** = `Gastos de personal (preus constants) / Hores treballades`.

    **Nota:** L'EEE mesura "Gastos de personal" que inclou salaris bruts, cotitzacions socials
    a càrrec de l'empresa i altres costos laborals. No equival al salari net del treballador.
    """)

    # ── Empreses i densitat ──
    st.subheader("4. Empreses i densitat comercial")
    st.markdown("""
    **Fonts d'empreses (combinació de 3 taules INE):**
    - **Taula 39372:** CCAA + Nacional, CNAE a 3 dígits (2020-últim any). Font principal per a dades recents.
    - **Taula 3954:** Nacional, CNAE detallat (2013-últim any). Complementa la sèrie nacional.
    - **Taula 298:** CCAA + Nacional, històrica (2008-2020). Complementa anys anteriors.

    La combinació garanteix la sèrie més llarga possible sense duplicar anys.

    **Població (per calcular densitat):**
    - **Taula 2915 (Padrón Municipal):** Nacional + CCAA, 1996-2021.
    - **Taula 56934 (Cifras de Población):** Nacional, 2022-últim any.
    - **Estimació CCAA 2022-2025:** S'aplica la proporció de cada CCAA sobre el total nacional
      de l'últim any del Padrón (2021) a la població nacional dels anys recents.
      L'error estimat és inferior al 0,5% (les proporcions poblacionals entre CCAA varien molt lentament).

    **Densitat comercial** = `(Empreses / Població) × 1.000` = empreses per cada 1.000 habitants.

    **Nota sobre 2022-2023:** Es pot observar una caiguda brusca d'empreses entre 2022 i 2023
    en algunes CCAA. Això pot reflectir canvis metodològics en el DIRCE de l'INE (actualització
    del directori d'empreses) més que una destrucció real de teixit empresarial.
    """)

    # ── Territori ──
    st.subheader("5. Estimacio del VAB CNAE 47 per CCAA (metode hibrid)")
    st.markdown("""
    **Problema:** La Comptabilitat Regional de l'INE no desglossa el VAB al nivell del CNAE 47
    (comerc al detall). Per tant, cal estimar-lo.

    **Fonts:**
    - **Eurostat `nama_10r_3gva`:** VAB de la seccio G-I (comerc, transport i hostaleria) per CCAA (NUTS2).
      Dades de comptabilitat regional real, no estimacions.
    - **Eurostat `nama_10_a64`:** VAB del CNAE G47 a nivell nacional espanyol.
    - **INE, taula 76817 (EEE Sector Comerc):** Xifra de negoci del CNAE 47 per CCAA.

    **Metode hibrid (proporcional ponderat):**
    1. Es calcula la **ratio nacional** `G47/GI = VAB_G47_Espanya / VAB_GI_Espanya` (~22-26% segons l'any).
    2. Per a cada CCAA es calculen dues quotes: la **quota G-I** (pes del VAB G-I de la CCAA sobre el total G-I nacional)
       i la **quota de xifra de negoci** (pes de la XN CNAE 47 de la CCAA sobre el total nacional).
    3. La **quota hibrida** es la mitjana de les dues quotes. Aixo combina la informacio top-down
       (comptabilitat regional) amb la bottom-up (enquesta d'empreses).
    4. El VAB G47 nacional d'Eurostat es distribueix entre CCAA segons les quotes hibrides.

    **Per que la mitjana?** La quota G-I captura l'escala economica real de cada regio pero inclou
    transport i hostaleria (on CCAA turistiques com Balears pesen mes del que correspondria al retail).
    La quota de XN reflexa directament l'activitat del comerc al detall pero prove d'una enquesta
    (no de comptabilitat regional). La mitjana equilibra ambdos biaixos.

    **Restriccio:** La suma del VAB estimat de totes les CCAA es exactament igual al VAB G47 nacional
    d'Eurostat, garantint coherencia amb els comptes nacionals.

    **Limitacio:** L'estimacio assumeix que la ratio G47/GI es homogenia dins cada CCAA. En realitat,
    CCAA turistiques tenen un pes relatiu mes gran de la H (hostaleria) dins G-I. La ponderacio amb XN
    corregeix parcialment aquest biaix.
    """)

    # ── Ecommerce ──
    st.subheader("6. Comerc electronic")
    st.markdown("""
    **Font:** CNMC (Comissio Nacional dels Mercats i la Competencia), dades trimestrals de comerc electronic.

    **Agregacio:** Les dades trimestrals s'agreguen a nivell anual (suma dels 4 trimestres).

    **Any parcial:** Si l'ultim any disponible mostra un volum total inferior al 85% de l'any anterior,
    es considera que les dades son d'un any incomplet (la CNMC publica amb retard)
    i es mostra una nota d'advertencia.

    **Pes CNAE 47** = `Volum e-commerce CNAE 47 / Volum total e-commerce x 100`.
    """)

    # ── Europa ──
    st.subheader("7. Comparativa europea")
    st.markdown("""
    **Font:** Eurostat, Comptes Nacionals (taula `nama_10_a64`).

    **Pes CNAE 47 sobre PIB** = `VAB CNAE G47 / PIB total x 100` per a cada pais.

    **Paisos inclosos:** Tots els disponibles a Eurostat amb dades per al CNAE G47, incloent
    l'agregat UE-27 com a referencia. Espanya es destaca visualment per facilitar la comparacio.
    """)

    # ── Periodicitat ──
    st.subheader("8. Periodicitat d'actualitzacio")
    st.markdown("""
    L'Observatori s'actualitza de forma **trimestral** (gener, abril, juliol i octubre) mitjançant
    un procés automatitzat (GitHub Actions) que:
    1. Descarrega les dades actualitzades de les APIs de l'INE, Eurostat i CNMC.
    2. Processa i deflacta les dades.
    3. Genera els fitxers CSV actualitzats.
    4. Redesplega automàticament el dashboard.
    """)

else:
    st.title("Aspectos metodológicos")
    st.markdown("""
    Esta sección detalla los criterios de cálculo y las decisiones metodológicas
    adoptadas en la elaboración de los indicadores del Observatorio. El objetivo es garantizar
    la **transparencia** y la **reproducibilidad** de todos los resultados presentados.
    """)

    st.markdown("---")

    st.subheader("1. Deflación con IPC: conversión a precios constantes")
    st.markdown("""
    **Objetivo:** Eliminar el efecto de la inflación para comparar magnitudes económicas a lo largo del tiempo.

    **Fuente del deflactor:** IPC general mensual publicado por el INE (Tabla 50902), base oficial 2021 = 100.

    **Procedimiento:**
    1. Se calcula la **media anual** del IPC mensual para cada año.
    2. Se define como **año base** el primer año con datos disponibles (2002 para el VAB; 2018 para la productividad).
    3. El deflactor se calcula como: `IPC_año / IPC_año_base`.
    4. El valor real se calcula como: `Valor_nominal / Deflactor`.

    **Resultado:** Con esta base, el valor real coincide con el nominal en el año base,
    y los valores reales siempre son iguales o inferiores a los nominales (ya que la inflación acumulada
    desde el año base es positiva). Esto evita la confusión visual que generaría un año base posterior
    (como 2021) donde los valores reales pre-base superarían los nominales.

    **Nota:** El deflactor utilizado es el IPC general, no un deflactor sectorial específico.
    Esta es una simplificación habitual en análisis sectoriales cuando no se dispone de un deflactor
    específico para el CNAE 47. El IPC general es una aproximación razonable dado que el comercio
    minorista es uno de los principales componentes de la cesta del IPC.
    """)

    st.subheader("2. Cálculo de la productividad")
    st.markdown("""
    **Fuente:** Estadística Estructural de Empresas (EEE) del INE, Tabla 36194 — Sector Comercio.

    **Indicadores:**
    - **VA/hora** (Valor Añadido por hora) = `Valor Añadido a coste de factores (precios constantes) / Horas trabajadas`
    - **Cifra de Negocio/hora** = `Cifra de Negocio (precios constantes) / Horas trabajadas`

    El Valor Añadido y la Cifra de Negocio se deflactan con el IPC (base 2018, primer año EEE disponible)
    antes de dividir por las horas trabajadas. Así se mide la productividad **real**,
    no el aparente crecimiento por subida de precios.

    **Interpretación de la divergencia:**
    - Si VA/hora crece más que Cifra de Negocio/hora → **mejora de márgenes** (el sector retiene más valor neto).
    - Si Cifra de Negocio/hora crece más → **compresión de márgenes** (más facturación pero menos valor retenido).
    """)

    st.subheader("3. Distribución del Valor Añadido: cuota salarial y excedente bruto")
    st.markdown("""
    **Fuente:** EEE del INE, Tabla 36194 — magnitudes "Valor añadido a coste de los factores"
    y "Gastos de personal" para el CNAE 47.

    **Indicadores:**
    - **Cuota salarial** = `Gastos de personal / Valor Añadido` (proporción del VA destinada a remunerar trabajadores).
    - **Excedente bruto de explotación** = `Valor Añadido − Gastos de personal` (beneficios empresariales + amortizaciones + impuestos).
    - **Coste laboral por ocupado** = `Gastos de personal (precios constantes) / Personal ocupado`.
    - **Coste laboral por hora** = `Gastos de personal (precios constantes) / Horas trabajadas`.

    **Nota:** La EEE mide "Gastos de personal" que incluye salarios brutos, cotizaciones sociales
    a cargo de la empresa y otros costes laborales. No equivale al salario neto del trabajador.
    """)

    st.subheader("4. Empresas y densidad comercial")
    st.markdown("""
    **Fuentes de empresas (combinación de 3 tablas INE):**
    - **Tabla 39372:** CCAA + Nacional, CNAE a 3 dígitos (2020-último año). Fuente principal para datos recientes.
    - **Tabla 3954:** Nacional, CNAE detallado (2013-último año). Complementa la serie nacional.
    - **Tabla 298:** CCAA + Nacional, histórica (2008-2020). Complementa años anteriores.

    La combinación garantiza la serie más larga posible sin duplicar años.

    **Población (para calcular densidad):**
    - **Tabla 2915 (Padrón Municipal):** Nacional + CCAA, 1996-2021.
    - **Tabla 56934 (Cifras de Población):** Nacional, 2022-último año.
    - **Estimación CCAA 2022-2025:** Se aplica la proporción de cada CCAA sobre el total nacional
      del último año del Padrón (2021) a la población nacional de los años recientes.
      El error estimado es inferior al 0,5% (las proporciones poblacionales entre CCAA varían muy lentamente).

    **Densidad comercial** = `(Empresas / Población) × 1.000` = empresas por cada 1.000 habitantes.

    **Nota sobre 2022-2023:** Se puede observar una caída brusca de empresas entre 2022 y 2023
    en algunas CCAA. Esto puede reflejar cambios metodológicos en el DIRCE del INE (actualización
    del directorio de empresas) más que una destrucción real de tejido empresarial.
    """)

    st.subheader("5. Estimacion del VAB CNAE 47 por CCAA (metodo hibrido)")
    st.markdown("""
    **Problema:** La Contabilidad Regional del INE no desglosa el VAB al nivel del CNAE 47
    (comercio minorista). Por tanto, es necesario estimarlo.

    **Fuentes:**
    - **Eurostat `nama_10r_3gva`:** VAB de la seccion G-I (comercio, transporte y hosteleria) por CCAA (NUTS2).
      Datos de contabilidad regional real, no estimaciones.
    - **Eurostat `nama_10_a64`:** VAB del CNAE G47 a nivel nacional espanol.
    - **INE, tabla 76817 (EEE Sector Comercio):** Cifra de negocio del CNAE 47 por CCAA.

    **Metodo hibrido (proporcional ponderado):**
    1. Se calcula la **ratio nacional** `G47/GI = VAB_G47_Espana / VAB_GI_Espana` (~22-26% segun el ano).
    2. Para cada CCAA se calculan dos cuotas: la **cuota G-I** (peso del VAB G-I de la CCAA sobre el total G-I nacional)
       y la **cuota de cifra de negocio** (peso de la XN CNAE 47 de la CCAA sobre el total nacional).
    3. La **cuota hibrida** es la media de las dos cuotas. Esto combina la informacion top-down
       (contabilidad regional) con la bottom-up (encuesta de empresas).
    4. El VAB G47 nacional de Eurostat se distribuye entre CCAA segun las cuotas hibridas.

    **Por que la media?** La cuota G-I captura la escala economica real de cada region pero incluye
    transporte y hosteleria (donde CCAA turisticas como Baleares pesan mas de lo que corresponderia al retail).
    La cuota de XN refleja directamente la actividad del comercio minorista pero proviene de una encuesta
    (no de contabilidad regional). La media equilibra ambos sesgos.

    **Restriccion:** La suma del VAB estimado de todas las CCAA es exactamente igual al VAB G47 nacional
    de Eurostat, garantizando coherencia con las cuentas nacionales.

    **Limitacion:** La estimacion asume que la ratio G47/GI es homogenea dentro de cada CCAA. En realidad,
    CCAA turisticas tienen un peso relativo mayor de la H (hosteleria) dentro de G-I. La ponderacion con XN
    corrige parcialmente este sesgo.
    """)

    st.subheader("6. Comercio electronico")
    st.markdown("""
    **Fuente:** CNMC (Comision Nacional de los Mercados y la Competencia), datos trimestrales de comercio electronico.

    **Agregacion:** Los datos trimestrales se agregan a nivel anual (suma de los 4 trimestres).

    **Ano parcial:** Si el ultimo ano disponible muestra un volumen total inferior al 85% del ano anterior,
    se considera que los datos son de un ano incompleto (la CNMC publica con retraso)
    y se muestra una nota de advertencia.

    **Peso CNAE 47** = `Volumen e-commerce CNAE 47 / Volumen total e-commerce x 100`.
    """)

    st.subheader("7. Comparativa europea")
    st.markdown("""
    **Fuente:** Eurostat, Cuentas Nacionales (tabla `nama_10_a64`).

    **Peso CNAE 47 sobre PIB** = `VAB CNAE G47 / PIB total x 100` para cada pais.

    **Paises incluidos:** Todos los disponibles en Eurostat con datos para el CNAE G47, incluyendo
    el agregado UE-27 como referencia. Espana se destaca visualmente para facilitar la comparacion.
    """)

    st.subheader("8. Periodicidad de actualizacion")
    st.markdown("""
    El Observatorio se actualiza de forma **trimestral** (enero, abril, julio y octubre) mediante
    un proceso automatizado (GitHub Actions) que:
    1. Descarga los datos actualizados de las APIs del INE, Eurostat y CNMC.
    2. Procesa y deflacta los datos.
    3. Genera los archivos CSV actualizados.
    4. Redespliega automáticamente el dashboard.
    """)

page_meta("Elaboració pròpia", st.session_state.lang)

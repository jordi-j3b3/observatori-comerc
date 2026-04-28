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

    # ── Salari mitjà per ocupat ──
    st.subheader("4. Salari mitjà per ocupat per CCAA: interpretació i limitacions")
    st.markdown("""
    **Indicador:** `Sous i salaris / Personal ocupat` per a cada CCAA.

    **Font:** INE, Estadística Estructural d'Empreses (EEE), Taula 76817 — Sector Comerç, CNAE 47.

    **Què mesura:** La despesa mitjana en sous i salaris per cada persona ocupada al sector del comerç
    al detall, desglossada per comunitat autònoma.

    **Per què algunes CCAA mostren valors inferiors a l'SMI?**

    Aquesta xifra **no és comparable directament amb el Salari Mínim Interprofessional (SMI)**
    per tres raons:

    1. **Inclou treballadors a temps parcial.** El comerç al detall té una de les taxes de parcialitat
       més altes de l'economia (~30% dels ocupats segons l'EPA). El denominador (`personal ocupat`)
       compta caps, no equivalents a jornada completa (EJC). Un treballador a mitja jornada compta
       com a 1 persona però cobra proporcionalment a les seves hores. L'SMI s'aplica pro rata
       al temps parcial, de manera que un treballador a mitja jornada pot cobrar legalment la meitat de l'SMI anual.

    2. **"Sous i salaris" exclou les cotitzacions socials a càrrec de l'empresa.** La variable
       `Sueldos y salarios` de l'EEE recull exclusivament la retribució bruta. Les cotitzacions
       a la Seguretat Social, formació professional i altres càrregues patronals (~23% del cost
       laboral total) queden fora. La variable que les inclou és `Gastos de personal`, disponible
       a nivell nacional però no regionalitzada per CCAA.

    3. **Efecte composició per CCAA.** Les comunitats amb menor cost de vida tendeixen a tenir
       una proporció més alta de contractes a temps parcial i de comerç de proximitat (menys
       grans superfícies), cosa que empeny la mitjana per persona a la baixa.

    **Verificació amb dades nacionals:**

    A nivell nacional, on disposem d'hores treballades (EEE Taula 36194), podem calcular el salari per hora:

    | Indicador (2023) | Valor |
    |---|---|
    | Sous i salaris / Hores treballades | **13,26 EUR/hora** |
    | SMI per hora (ref. 1.756 h/any jornada completa) | **8,61 EUR/hora** |
    | Salari equivalent a jornada completa (13,26 × 1.756) | **~23.285 EUR/any** |
    | Hores mitjanes per treballador al sector | **1.240 h/any** (70,6% d'una jornada completa) |

    El salari per hora del sector és un **54% superior a l'SMI per hora**. La mitjana per persona
    és baixa perquè reflecteix jornades reduïdes, no salaris insuficients.

    **Fonts complementàries per contrastar:**
    - **INE, Enquesta Anual d'Estructura Salarial (EAES):** Salari mitjà brut del sector Comerç (secció G):
      24.137 EUR/any (2023). Jornada completa: 32.168 EUR; temps parcial: 13.775 EUR.
    - **INE, EPA:** Taxa de parcialitat al sector Comerç (secció G): ~15% (2023). Al detall (CNAE 47)
      la xifra és superior per la prevalença de contractes de cap de setmana i mitja jornada.
    - **SEPE, Observatorio de las Ocupaciones:** Informes sectorials anuals sobre contractació
      al comerç minorista per tipus de jornada i CCAA.

    **Limitació important:** La Taula 76817 de l'EEE no publica hores treballades per CCAA,
    de manera que no és possible calcular un salari per hora regionalitzat. L'indicador
    `sous/ocupat` és la millor aproximació disponible, però cal interpretar-lo amb les precaucions
    descrites.
    """)

    # ── Empreses i densitat ──
    st.subheader("5. Empreses i densitat comercial")
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
    st.subheader("6. Estimació del VAB CNAE 47 per CCAA (mètode híbrid)")
    st.markdown("""
    **Problema:** La Comptabilitat Regional de l'INE no desglossa el VAB al nivell del CNAE 47
    (comerç al detall). Per tant, cal estimar-lo.

    **Fonts:**
    - **Eurostat `nama_10r_3gva`:** VAB de la secció G-I (comerç, transport i hostaleria) per CCAA (NUTS2).
      Dades de comptabilitat regional real, no estimacions.
    - **Eurostat `nama_10_a64`:** VAB del CNAE G47 a nivell nacional espanyol.
    - **INE, taula 76817 (EEE Sector Comerc):** Xifra de negoci del CNAE 47 per CCAA.

    **Mètode híbrid (proporcional ponderat):**
    1. Es calcula la **ratio nacional** `G47/GI = VAB_G47_Espanya / VAB_GI_Espanya` (~22-26% segons l'any).
    2. Per a cada CCAA es calculen dues quotes: la **quota G-I** (pes del VAB G-I de la CCAA sobre el total G-I nacional)
       i la **quota de xifra de negoci** (pes de la XN CNAE 47 de la CCAA sobre el total nacional).
    3. La **quota híbrida** és la mitjana de les dues quotes. Això combina la informació top-down
       (comptabilitat regional) amb la bottom-up (enquesta d'empreses).
    4. El VAB G47 nacional d'Eurostat es distribueix entre CCAA segons les quotes híbrides.

    **Per què la mitjana?** La quota G-I captura l'escala econòmica real de cada regió però inclou
    transport i hostaleria (on CCAA turístiques com Balears pesen més del que correspondria al retail).
    La quota de XN reflecteix directament l'activitat del comerç al detall però prové d'una enquesta
    (no de comptabilitat regional). La mitjana equilibra ambdós biaixos.

    **Restricció:** La suma del VAB estimat de totes les CCAA és exactament igual al VAB G47 nacional
    d'Eurostat, garantint coherència amb els comptes nacionals.

    **Limitació:** L'estimació assumeix que la ratio G47/GI es homogènia dins cada CCAA. En realitat,
    CCAA turístiques tenen un pes relatiu més gran de la H (hostaleria) dins G-I. La ponderació amb XN
    corregeix parcialment aquest biaix.
    """)

    # ── Ecommerce ──
    st.subheader("7. Comerç electrònic")
    st.markdown("""
    **Font:** CNMC (Comissió Nacional dels Mercats i la Competència), dades trimestrals de comerç electrònic.

    **Agregació:** Les dades trimestrals s'agreguen a nivell anual (suma dels 4 trimestres).

    **Any parcial:** Si l'últim any disponible mostra un volum total inferior al 85% de l'any anterior,
    es considera que les dades són d'un any incomplet (la CNMC publica amb retard)
    i es mostra una nota d'advertència.

    **Pes CNAE 47** = `Volum e-commerce CNAE 47 / Volum total e-commerce x 100`.
    """)

    # ── Europa ──
    st.subheader("8. Comparativa europea")
    st.markdown("""
    **Font:** Eurostat, Comptes Nacionals (taula `nama_10_a64`).

    **Pes CNAE 47 sobre PIB** = `VAB CNAE G47 / PIB total x 100` per a cada país.

    **Països inclosos:** Tots els disponibles a Eurostat amb dades per al CNAE G47, incloent
    l'agregat UE-27 com a referència. Espanya es destaca visualment per facilitar la comparació.
    """)

    # ── Subsectors i mapeig COICOP ↔ CNAE ──
    st.subheader("9. Subsectors CNAE 47 i mapeig demanda ↔ oferta")
    st.markdown("""
    **Fonts utilitzades a la pàgina Subsectors:**
    - **DIRCE (Taula 73019):** nombre d'empreses per subsector CNAE 47 a 3 dígits.
    - **EAS Comerç (Taula 76818):** xifra de negoci, valor afegit, personal ocupat i inversió per subsector. Inclou totes les empreses CNAE 47 (e-commerce pur de CNAE 479 i vendes online d'establiments tradicionals classificades al subsector principal de l'empresa).
    - **EPF (Taula 75003):** despesa mitjana per llar a preus constants, per categoria COICOP-2 dígits.

    **Exclusió del CNAE 473 (Combustibles per a l'automoció):**
    Aquest subsector té una dinàmica atípica dins del comerç al detall (preus regulats per components fiscals,
    volatilitat lligada al mercat energètic global, marges reduïts i estables). S'exclou de l'anàlisi
    per no distorsionar les comparacions entre subsectors retail genuïns. La suma agregada dels subsectors
    mostrats no és exactament igual al total CNAE 47 oficial, ni per aquesta exclusió ni per els
    arrodoniments estadístics que aplica l'INE entre nivells de la jerarquia CNAE (gap habitual del 0,5–1%).

    **Mapeig COICOP (demanda) ↔ CNAE 47 (oferta):**

    Permet llegir conjuntament què compren les famílies (EPF) i a través de quins subsectors
    de comerç es canalitza aquesta despesa (EAS/DIRCE). El mapeig és **orientatiu**: alguns béns
    es venen també per canals fora del comerç al detall (majorista, importació directa, etc.).

    | COICOP (demanda) | CNAE 47 (oferta) |
    |---|---|
    | 01 Aliments i begudes no alc. | 471 (no especialitzats) + 472 (especialitzada alim.) |
    | 02 Begudes alc., tabac | 472 (estancs i begudes) |
    | 03 Vestit i calçat | 477 (4771 vestit + 4772 calçat) |
    | 05 Mobles i articles llar | 475 (electrodomèstics, parament) |
    | 06 Sanitat | 477 (4773 farmàcies, dins 477) |
    | 08 Informació i comunicacions | 474 (equips TIC) |
    | 09 Oci, cultura i esport | 476 (llibreries, jugueteries, esports) |
    | 12 Cura personal | 477 (4775 cosmètics, dins 477) |

    **Categories COICOP no incloses al retail:**
    - 04 Habitatge i energia (subministraments)
    - 07 Transport (carburant està a 473, exclòs; resta no és retail)
    - 10 Educació
    - 11 Restauració i allotjament

    **Coincidència amb altres apartats:**
    - El **Personal ocupat** del CNAE 47 a la pàgina Subsectors (T=76818) coincideix exactament
      amb el de la pàgina Productivitat (T=36194), perquè ambdues taules surten de l'EAS Comerç.
    - La **Xifra de negoci** i el **VA** a la pàgina Subsectors es mostren a **preus corrents**
      (no deflactats), mentre que la pàgina Productivitat treballa a **preus constants**. Per
      comparar, cal aplicar el deflactor IPC.

    **Per què el CNAE 479 NO coincideix amb el volum d'e-commerce (CNMC)?**

    Són **dues mètriques diferents que no s'haurien de comparar literalment**. Mesuren coses
    diferents amb metodologies independents:

    | Concepte | CNMC (pàgina E-commerce) | CNAE 479 (pàgina Subsectors) |
    |---|---|---|
    | Font primària | Processadors de pagament espanyols | Enquesta INE a empreses |
    | Què mesura | Volum de transaccions online | Facturació d'empreses "no establertes" |
    | Inclou compres a plataformes estrangeres | Sí (Amazon DE, AliExpress, Temu...) | No (només empreses fiscalment a Espanya) |
    | Inclou vendes online de tradicionals | Sí (Carrefour, El Corte Inglés, Decathlon online) | No (van al subsector principal: 471, 476...) |
    | Classificació | Per sector del comerciant (CNMC) | Per CNAE oficial (INE) |
    | Cobertura | Pure-play + tradicionals + estrangers | Només pure-play + venda directa + vending |

    **Comparativa numèrica (M EUR):**

    | Any | CNMC CNAE 47 | EAS CNAE 479 | Ratio |
    |---|---|---|---|
    | 2018 | 9.735 | 8.178 | 84% |
    | 2020 | 17.958 | 11.545 | 64% |
    | 2022 | 20.356 | 15.182 | 75% |
    | 2024 | 25.739 | 17.181 | 67% |

    La bretxa creix amb el temps perquè els grans retailers tradicionals han desenvolupat
    canals online importants (que CNMC capta però CNAE 479 no), i perquè el comerç internacional
    online (marketplaces estrangers) creix a un ritme superior.

    **Lectura conjunta:** la CNMC capta el volum **total de comerç electrònic des del costat
    del consumidor**; el CNAE 479 capta el segment d'empreses **purament digitals des del
    costat oferta empresarial**. Cap és "millor": són lents complementàries del mateix fenomen.
    """)

    # ── Periodicitat ──
    st.subheader("10. Periodicitat d'actualització")
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

    # ── Salario medio por ocupado ──
    st.subheader("4. Salario medio por ocupado por CCAA: interpretación y limitaciones")
    st.markdown("""
    **Indicador:** `Sueldos y salarios / Personal ocupado` para cada CCAA.

    **Fuente:** INE, Estadística Estructural de Empresas (EEE), Tabla 76817 — Sector Comercio, CNAE 47.

    **Qué mide:** El gasto medio en sueldos y salarios por cada persona ocupada en el sector del comercio
    minorista, desglosado por comunidad autónoma.

    **¿Por qué algunas CCAA muestran valores inferiores al SMI?**

    Esta cifra **no es comparable directamente con el Salario Mínimo Interprofesional (SMI)**
    por tres razones:

    1. **Incluye trabajadores a tiempo parcial.** El comercio minorista tiene una de las tasas de parcialidad
       más altas de la economía (~30% de los ocupados según la EPA). El denominador (`personal ocupado`)
       cuenta personas, no equivalentes a jornada completa (EJC). Un trabajador a media jornada cuenta
       como 1 persona pero cobra proporcionalmente a sus horas. El SMI se aplica pro rata
       al tiempo parcial, de modo que un trabajador a media jornada puede cobrar legalmente la mitad del SMI anual.

    2. **"Sueldos y salarios" excluye las cotizaciones sociales a cargo de la empresa.** La variable
       `Sueldos y salarios` de la EEE recoge exclusivamente la retribución bruta. Las cotizaciones
       a la Seguridad Social, formación profesional y otras cargas patronales (~23% del coste
       laboral total) quedan fuera. La variable que las incluye es `Gastos de personal`, disponible
       a nivel nacional pero no regionalizada por CCAA.

    3. **Efecto composición por CCAA.** Las comunidades con menor coste de vida tienden a tener
       una proporción más alta de contratos a tiempo parcial y de comercio de proximidad (menos
       grandes superficies), lo que empuja la media por persona a la baja.

    **Verificación con datos nacionales:**

    A nivel nacional, donde disponemos de horas trabajadas (EEE Tabla 36194), podemos calcular el salario por hora:

    | Indicador (2023) | Valor |
    |---|---|
    | Sueldos y salarios / Horas trabajadas | **13,26 EUR/hora** |
    | SMI por hora (ref. 1.756 h/año jornada completa) | **8,61 EUR/hora** |
    | Salario equivalente a jornada completa (13,26 x 1.756) | **~23.285 EUR/año** |
    | Horas medias por trabajador en el sector | **1.240 h/año** (70,6% de una jornada completa) |

    El salario por hora del sector es un **54% superior al SMI por hora**. La media por persona
    es baja porque refleja jornadas reducidas, no salarios insuficientes.

    **Fuentes complementarias para contrastar:**
    - **INE, Encuesta Anual de Estructura Salarial (EAES):** Salario medio bruto del sector Comercio (sección G):
      24.137 EUR/año (2023). Jornada completa: 32.168 EUR; tiempo parcial: 13.775 EUR.
    - **INE, EPA:** Tasa de parcialidad en el sector Comercio (sección G): ~15% (2023). En el minorista (CNAE 47)
      la cifra es superior por la prevalencia de contratos de fin de semana y media jornada.
    - **SEPE, Observatorio de las Ocupaciones:** Informes sectoriales anuales sobre contratación
      en el comercio minorista por tipo de jornada y CCAA.

    **Limitación importante:** La Tabla 76817 de la EEE no publica horas trabajadas por CCAA,
    de modo que no es posible calcular un salario por hora regionalizado. El indicador
    `sueldos/ocupado` es la mejor aproximación disponible, pero debe interpretarse con las precauciones
    descritas.
    """)

    st.subheader("5. Empresas y densidad comercial")
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

    st.subheader("6. Estimación del VAB CNAE 47 por CCAA (método híbrido)")
    st.markdown("""
    **Problema:** La Contabilidad Regional del INE no desglosa el VAB al nivel del CNAE 47
    (comercio minorista). Por tanto, es necesario estimarlo.

    **Fuentes:**
    - **Eurostat `nama_10r_3gva`:** VAB de la sección G-I (comercio, transporte y hosteleria) por CCAA (NUTS2).
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

    **Limitación:** La estimacion asume que la ratio G47/GI es homogenea dentro de cada CCAA. En realidad,
    CCAA turisticas tienen un peso relativo mayor de la H (hosteleria) dentro de G-I. La ponderacion con XN
    corrige parcialmente este sesgo.
    """)

    st.subheader("7. Comercio electrónico")
    st.markdown("""
    **Fuente:** CNMC (Comision Nacional de los Mercados y la Competencia), datos trimestrales de comercio electronico.

    **Agregacion:** Los datos trimestrales se agregan a nivel anual (suma de los 4 trimestres).

    **Ano parcial:** Si el ultimo ano disponible muestra un volumen total inferior al 85% del ano anterior,
    se considera que los datos son de un ano incompleto (la CNMC publica con retraso)
    y se muestra una nota de advertencia.

    **Peso CNAE 47** = `Volumen e-commerce CNAE 47 / Volumen total e-commerce x 100`.
    """)

    st.subheader("8. Comparativa europea")
    st.markdown("""
    **Fuente:** Eurostat, Cuentas Nacionales (tabla `nama_10_a64`).

    **Peso CNAE 47 sobre PIB** = `VAB CNAE G47 / PIB total x 100` para cada país.

    **Países incluidos:** Todos los disponibles en Eurostat con datos para el CNAE G47, incluyendo
    el agregado UE-27 como referencia. España se destaca visualmente para facilitar la comparación.
    """)

    st.subheader("9. Subsectores CNAE 47 y mapeo demanda ↔ oferta")
    st.markdown("""
    **Fuentes utilizadas en la página Subsectores:**
    - **DIRCE (Tabla 73019):** número de empresas por subsector CNAE 47 a 3 dígitos.
    - **EAS Comercio (Tabla 76818):** cifra de negocios, valor añadido, personal ocupado e inversión por subsector. Incluye todas las empresas CNAE 47 (e-commerce puro de CNAE 479 y ventas online de establecimientos tradicionales clasificadas en el subsector principal de la empresa).
    - **EPF (Tabla 75003):** gasto medio por hogar a precios constantes, por categoría COICOP-2 dígitos.

    **Exclusión del CNAE 473 (Combustibles para automoción):**
    Este subsector tiene una dinámica atípica dentro del comercio minorista (precios regulados por
    componentes fiscales, volatilidad ligada al mercado energético global, márgenes reducidos y
    estables). Se excluye del análisis para no distorsionar las comparaciones entre subsectores
    retail genuinos. La suma agregada de los subsectores mostrados no es exactamente igual al total
    CNAE 47 oficial, ni por esta exclusión ni por los redondeos estadísticos que aplica el INE entre
    niveles de la jerarquía CNAE (gap habitual del 0,5–1%).

    **Mapeo COICOP (demanda) ↔ CNAE 47 (oferta):**

    Permite leer conjuntamente qué compran las familias (EPF) y a través de qué subsectores de
    comercio se canaliza ese gasto (EAS/DIRCE). El mapeo es **orientativo**: algunos bienes se
    venden también por canales fuera del comercio minorista (mayorista, importación directa, etc.).

    | COICOP (demanda) | CNAE 47 (oferta) |
    |---|---|
    | 01 Alimentos y bebidas no alc. | 471 (no especializados) + 472 (especializada alim.) |
    | 02 Bebidas alc., tabaco | 472 (estancos y bebidas) |
    | 03 Vestido y calzado | 477 (4771 vestido + 4772 calzado) |
    | 05 Muebles y artículos hogar | 475 (electrodomésticos, menaje) |
    | 06 Sanidad | 477 (4773 farmacias, dentro de 477) |
    | 08 Información y comunicaciones | 474 (equipos TIC) |
    | 09 Ocio, cultura y deporte | 476 (librerías, jugueterías, deportes) |
    | 12 Cuidado personal | 477 (4775 cosméticos, dentro de 477) |

    **Categorías COICOP no incluidas en el retail:**
    - 04 Vivienda y energía (suministros)
    - 07 Transporte (carburante está en 473, excluido; el resto no es retail)
    - 10 Educación
    - 11 Restauración y alojamiento

    **Coincidencia con otros apartados:**
    - El **Personal ocupado** del CNAE 47 en la página Subsectores (T=76818) coincide exactamente
      con el de la página Productividad (T=36194), porque ambas tablas provienen de la EAS Comercio.
    - La **Cifra de negocios** y el **VA** en la página Subsectores se muestran a **precios
      corrientes** (sin deflactar), mientras que la página Productividad trabaja a **precios
      constantes**. Para comparar, aplicar el deflactor IPC.

    **¿Por qué el CNAE 479 NO coincide con el volumen de e-commerce (CNMC)?**

    Son **dos métricas diferentes que no deberían compararse literalmente**. Miden cosas
    distintas con metodologías independientes:

    | Concepto | CNMC (página E-commerce) | CNAE 479 (página Subsectores) |
    |---|---|---|
    | Fuente primaria | Procesadores de pago españoles | Encuesta INE a empresas |
    | Qué mide | Volumen de transacciones online | Facturación de empresas "no establecidas" |
    | Incluye compras en plataformas extranjeras | Sí (Amazon DE, AliExpress, Temu...) | No (solo empresas fiscalmente en España) |
    | Incluye ventas online de tradicionales | Sí (Carrefour, El Corte Inglés, Decathlon online) | No (van al subsector principal: 471, 476...) |
    | Clasificación | Por sector del comerciante (CNMC) | Por CNAE oficial (INE) |
    | Cobertura | Pure-play + tradicionales + extranjeros | Solo pure-play + venta directa + vending |

    **Comparativa numérica (M EUR):**

    | Año | CNMC CNAE 47 | EAS CNAE 479 | Ratio |
    |---|---|---|---|
    | 2018 | 9.735 | 8.178 | 84% |
    | 2020 | 17.958 | 11.545 | 64% |
    | 2022 | 20.356 | 15.182 | 75% |
    | 2024 | 25.739 | 17.181 | 67% |

    La brecha crece con el tiempo porque los grandes retailers tradicionales han desarrollado
    canales online importantes (que CNMC capta pero CNAE 479 no), y porque el comercio
    internacional online (marketplaces extranjeros) crece a un ritmo superior.

    **Lectura conjunta:** la CNMC capta el volumen **total de comercio electrónico desde el
    lado del consumidor**; el CNAE 479 capta el segmento de empresas **puramente digitales
    desde el lado oferta empresarial**. Ninguna es "mejor": son lentes complementarias del
    mismo fenómeno.
    """)

    st.subheader("10. Periodicidad de actualización")
    st.markdown("""
    El Observatorio se actualiza de forma **trimestral** (enero, abril, julio y octubre) mediante
    un proceso automatizado (GitHub Actions) que:
    1. Descarga los datos actualizados de las APIs del INE, Eurostat y CNMC.
    2. Procesa y deflacta los datos.
    3. Genera los archivos CSV actualizados.
    4. Redespliega automáticamente el dashboard.
    """)

page_meta("Elaboració pròpia", st.session_state.lang)

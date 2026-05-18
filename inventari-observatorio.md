# Inventari Observatori del Comerç

Sessió d'arquitectura — generat 2026-05-18.

Ruta arrel del projecte: `/Users/j3b3/Desktop/ESTUDI PIB/observatori-comerc/`. Pestanyes declarades explícitament a `app.py` via `st.navigation()`. L'ordre del sidebar segueix la llista d'aquell fitxer; aquesta inventari respecta l'ordre demanat.

---

## Inici

- **Ruta del fitxer**: `pages/0_Inici.py`
- **Propòsit declarat**: Títol traduït via `t("app_title")` ("Observatori del Comerç al detall a Espanya — CNAE 47"). Subtítol via `t("app_subtitle")`. Apartat literal "Sobre l'Observatori": "El comerç al detall (CNAE 47) és un dels pilars de l'economia espanyola: dona feina a més d'1,7 milions de persones, genera uns 70.000 M EUR de valor afegit i articula el consum de les famílies a tot el territori. […] Aquest observatori ofereix una radiografia actualitzada del sector a partir de dades oficials (INE, Eurostat, CNMC), organitzada en sis dimensions: PIB i VAB / Empreses / Treball i productivitat / E-commerce / Territori / Europa".
- **Components visuals**:
  - 4 KPIs superiors (st.metric): VAB CNAE 47 nominal, Empreses CNAE 47, Personal ocupat, Productivitat VA/hora — cadascun amb variació delta.
  - Bloc HTML "Resum executiu / Principals conclusions" amb fins a 6 conclusions dinàmiques generades a partir dels CSVs (PIB, Empreses, Productivitat, E-commerce, Europa, Territori). Mostra "Última actualització" llegint `last_update.txt`.
  - Botó de descàrrega: "Excel observatori_comerc_detall.xlsx" amb 6 fulls (PIB i VAB, Empreses + Empreses_ES, Productivitat, E-commerce, Territori CCAA + Pes CCAA, Europa) generats amb `xlsxwriter`, cada full amb gràfic Plotly nadiu equivalent (line, column, bar).
  - Botó-link: "Obrir infografia Q1 2026" — enllaç HTML estàtic a `static/infografia_q1_2026.html`.
  - Formulari de butlletí trimestral (component `newsletter_form` de `style.py`).
- **Fonts de dades**: agregació de tots els CSVs principals — `pib_vab.csv`, `empreses.csv`, `productivitat.csv`, `ecommerce.csv`, `europa_vab.csv`, `eee_ccaa.csv` (no crida APIs en viu; només llegeix la cache).
- **Freqüència d'actualització**: trimestral (gener, abril, juliol, octubre) segons el text declarat. Process automatitzat via GitHub Actions descrit a Metodologia §10.
- **Text explicatiu/interpretatiu**: abundant. Inclou un text introductori bilingüe d'unes 8 línies + conclusions dinàmiques amb fins a 6 ítems narratius generats a runtime.
- **Filtres o interactivitat**: cap selector. Únic input interactiu = botons de descàrrega.
- **Dependències tècniques rellevants**:
  - `style.py`: `inject_css`, `setup_lang`, `page_header`, `insight`, `fnum`, `fpct`, `cagr`, `page_meta`, `newsletter_form`.
  - `xlsxwriter` (opcional; degrada amb missatge si no està disponible).
  - Llegeix `static/infografia_q1_2026.html` si existeix (publicat via Streamlit static serving).
  - Llegeix `data/cache/last_update.txt`.

---

## Pols diari

- **Ruta del fitxer**: `pages/0a_Pols_diari.py`
- **Propòsit declarat**: Etiqueta "GRANULARITAT DIÀRIA · PUBLICACIÓ MENSUAL". Títol "Pols diari del consum". Subtítol literal: "Sèrie diària de vendes acumulades de grans empreses del comerç al detall, comparades amb el mateix període de l'any anterior. L'INE publica aquesta sèrie un cop al mes: cada dia està disponible, però amb el retard típic de la publicació."
- **Components visuals**:
  - Capçalera HTML amb "Darrera dada disponible" (retard vs avui) i "Propera actualització estimada".
  - 4 KPIs: Darrera dada (taxa anual), Mitjana 7 dies, Mitjana 30 dies, Mitjana 90 dies — amb delta entre finestres.
  - 1 gràfic Plotly: línia (taxa anual interanual) amb mitjana mòbil + sèrie diària fina puntejada quan se suavitza, línia base 0%, ombrejat del període COVID 2020-03-14 a 2020-06-21.
  - 2 expanders desplegables: "Anàlisi — què diuen les dades ara mateix" (text dinàmic basat en mitjanes), "Metodologia — com es calcula i què mesura".
- **Fonts de dades**: INE — Mesura del Comerç Diari al per Menor de Grans Empreses (CDMGE), taula 37808. Cache: `data/cache/cdmge.csv` (indicador `tasa_anual`).
- **Freqüència d'actualització**: dada amb granularitat diària, **publicació mensual** per l'INE amb retard típic de 25-55 dies. La cache local s'actualitza amb el processament trimestral del pipeline.
- **Text explicatiu/interpretatiu**: abundant. Bloc "Lectura del moment" generat dinàmicament + expander metodològic exhaustiu (font, càlcul, suavitzat, limitacions, calendari de publicació).
- **Filtres o interactivitat**: `st.radio` "Període" (3, 6, 12, 24 mesos, Des de 2020) i `st.radio` "Suavitzat" (sense, MM7, MM30, MM90). Tots horitzontals.
- **Dependències tècniques rellevants**:
  - Només `style.py` (mínim: `inject_css`, `setup_lang`, `page_header`).
  - Llegeix exclusivament `data/cache/cdmge.csv`.
  - Càlculs de retard amb `datetime` i `pd.offsets.MonthEnd`.

---

## PIB i VAB

- **Ruta del fitxer**: `pages/1_PIB_i_VAB.py`
- **Propòsit declarat**: Títol "PIB i VAB" (via `t`). Intro literal: "El Valor Afegit Brut (VAB) mesura la riquesa que genera el comerç al detall (CNAE 47) dins l'economia espanyola. Es presenta en termes nominals (preus corrents) i reals (preus constants de 2002, eliminant l'efecte de la inflació amb l'IPC general). […] El CAGR (taxa de creixement anual compost) permet resumir la tendència de tot el període en una sola xifra anualitzada."
- **Components visuals**:
  - 4 KPIs: VAB nominal (darrer any), VAB real (darrer any), Pes sobre PIB, CAGR del període complet.
  - Gràfic 1 (línies): VAB nominal vs real anys complets.
  - Gràfic 2 (barres): Pes CNAE 47 sobre PIB anual (% PIB).
  - Gràfic 3 (barres agrupades): Variació anual nominal vs real, amb línia 0.
  - Gràfic 4 (línies múltiples): VAB nominal vs real per CCAA seleccionades (multiselect).
  - 2 blocs `insight()` dinàmics amb interpretació narrativa.
  - Expander de descàrrega de CSV.
- **Fonts de dades**: INE Comptabilitat Nacional (`pib_vab.csv`); a la secció CCAA es creua amb Eurostat + INE EAS 76817 (`eee_ccaa.csv`, columnes `vab_eurostat`, `vab_estimat`). Deflactor IPC general base 2002 (INE T=50902).
- **Freqüència d'actualització**: anual (publicació INE Comptabilitat Nacional). Refresh al pipeline trimestral.
- **Text explicatiu/interpretatiu**: abundant. Intro + 2 insights dinàmics + sources amb explicació metodològica del deflactor.
- **Filtres o interactivitat**: `st.multiselect` per CCAA al gràfic 4 (default: Cataluña, Madrid, Andalucía, Comunitat Valenciana).
- **Dependències tècniques rellevants**:
  - `style.py`: helpers complets + paleta (PURPLE, PURPLE_LIGHT, RED, BLUE, PALETTE).
  - Carrega `pib_vab.csv` i `eee_ccaa.csv` (font compartida amb la pestanya Territori).

---

## Empreses

- **Ruta del fitxer**: `pages/2_Empreses.py`
- **Propòsit declarat**: Títol via `t("emp_title")`. Intro literal: "El nombre d'empreses actives del comerç al detall (CNAE 47) reflecteix la salut i la dinàmica del teixit empresarial del sector. Una caiguda sostinguda no sempre és negativa: pot indicar concentració (menys empreses, però més grans i eficients) o bé destrucció neta per pressió competitiva i digitalització. La comparativa per comunitats autònomes permet identificar quins territoris perden o guanyen pes relatiu en el comerç al detall."
- **Components visuals**:
  - 4 KPIs: Empreses darrer any, Variació total, Empreses perdudes, CAGR.
  - Gràfic 1 (línia + àrea): Evolució empreses Espanya, range fixat 350.000-600.000.
  - Gràfic 2 (barres bicolor): Taxa variació anual amb codis GREEN/RED.
  - Gràfic 3 (línia + àrea): Densitat comercial nacional (empreses/1.000 hab).
  - Mapa choropleth interactiu CCAA dins `st.tabs(["Mapa", "Rànquing"])` amb inset de Canàries; mètrica seleccionable amb `st.radio` (densitat vs absolut).
  - Tab Rànquing: barres horitzontals per nombre d'empreses CCAA + barres horitzontals per densitat CCAA, amb línia de referència Espanya.
  - Barres horitzontals: variació acumulada per CCAA del primer al darrer any.
  - Gràfic línies múltiples: evolució temporal per CCAA seleccionades (multiselect).
  - 3 blocs `insight()` (Espanya general, densitat, contextualització CCAA).
  - Expander de descàrrega.
- **Fonts de dades**: INE DIRCE — Directori Central d'Empreses. Cache: `data/cache/empreses.csv` (territori, any, empreses, poblacio, empreses_per_1000hab). Suporta Espanya + 17 CCAA. Combina T=39372 + T=3954 + T=298 (segons Metodologia §5).
- **Freqüència d'actualització**: anual (DIRCE INE).
- **Text explicatiu/interpretatiu**: abundant. Intro extensa, 3 insights narratius, captions a fonts.
- **Filtres o interactivitat**: `st.select_slider` selector d'any; `st.tabs` Mapa/Rànquing; `st.radio` mètrica del mapa; `st.multiselect` CCAA per evolució temporal.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers complets + paleta + `load_geojson_spain_ccaa`, `canaries_inset_layers`.
  - Carrega `data/cache/empreses.csv`.

---

## Ocupació

- **Ruta del fitxer**: `pages/3_Ocupació.py`
- **Propòsit declarat**: Títol via `t("ocu_title")`. Intro literal: "L'ocupació del comerç al detall es mesura en dues dimensions complementàries: el personal ocupat (nombre de persones que treballen al sector) i les hores treballades (volum total de treball efectiu). La relació entre ambdues revela la intensitat laboral […]. La ràtio de treballadors per empresa connecta l'ocupació amb l'estructura empresarial."
- **Components visuals**:
  - 3 KPIs: Personal ocupat (darrer any), Variació del període complet, Hores treballades (en milions).
  - Gràfic 1 (línia + àrea): Evolució del personal ocupat, range fixat 1,5M-2M.
  - Gràfic 2 (barres): Hores treballades anuals en milions.
  - Gràfic 3 (línia): Hores anuals per treballador.
  - Gràfic 4 (línia): Treballadors per empresa (ràtio ocupació/empreses).
  - 2 blocs `insight()` dinàmics ("Més hores, no més contractació" + interpretació ràtio).
  - Expander de descàrrega CSV.
- **Fonts de dades**: INE Estadística Estructural d'Empreses (EEE) — Taula 36194 (cache: `productivitat.csv`). Cruza amb DIRCE (`empreses.csv`) per la ràtio treballadors/empresa.
- **Freqüència d'actualització**: anual (EAS Comerç INE).
- **Text explicatiu/interpretatiu**: abundant. Intro + 2 insights narratius detallats que mencionen la reforma laboral 2022.
- **Filtres o interactivitat**: cap.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta (PURPLE, RED, BLUE, ORANGE).
  - Llegeix 2 caches: `productivitat.csv` i `empreses.csv` (font compartida amb Inici, PIB i VAB).

---

## Productivitat

- **Ruta del fitxer**: `pages/4_Productivitat.py`
- **Propòsit declarat**: Títol via `t("prod_title")`. Intro literal: "Aquesta pàgina analitza el rendiment econòmic del comerç al detall des de tres perspectives complementàries: la productivitat (eficiència en l'ús del treball), la distribució del Valor Afegit entre treball i capital, i els marges i rendibilitat del sector. Totes les dades són a preus constants (deflactats amb IPC general, base primer any disponible)."
- **Components visuals**: organitzats en `st.tabs(["Productivitat", "Distribució del Valor Afegit", "Marges i rendibilitat"])`:
  - **Tab 1 (Productivitat)**: 4 KPIs (VA/hora darrer any, primer any, variació, CAGR), `st.popover` informatiu sobre CAGR, gràfic d'evolució relativa amb índex base 100 (VA/hora vs Xifra de Negoci/hora).
  - **Tab 2 (Distribució VAB)**: subseccions "Composició del Valor Afegit" (gràfic apilat), "Quota salarial" (gràfic), "Cost laboral per ocupat (preus constants)".
  - **Tab 3 (Marges)**: "Evolució dels marges sobre vendes" (gràfic), "Descomposició de la xifra de negoci" (apilat), explicacions amb `st.caption` de la fórmula "(Vendes − Cost de mercaderia venuda) / Vendes".
  - Diversos blocs `insight()` interpretatius dins de cada tab.
  - Expander de descàrrega CSV al final.
- **Fonts de dades**: INE EAS Sector Comerç (taules 36194 + 36199). Cache: `data/cache/productivitat.csv` amb columnes `personal_ocupat`, `hores_treballades`, `productivitat_va_hora`, `productivitat_xn_hora`, `quota_salarial`, `cost_laboral_per_ocupat`, sèries de marges. Deflactor IPC base 2018 (primer any EAS disponible).
- **Freqüència d'actualització**: anual (EAS Comerç INE).
- **Text explicatiu/interpretatiu**: abundant. La pàgina és la més llarga de l'observatori després de Subsectors (873 línies). Tres intros per tab + múltiples insights narratius + captions explicatius.
- **Filtres o interactivitat**: navegació entre `st.tabs` i `st.popover` informatiu del CAGR. Sense filtres de dades.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers complets + paleta.
  - Llegeix `productivitat.csv` (font compartida amb Inici i Ocupació).

---

## E-commerce

- **Ruta del fitxer**: `pages/5_Ecommerce.py`
- **Propòsit declarat**: Títol via `t("ec_title")`. Intro literal: "El comerç electrònic és el canal de venda amb major creixement del sector del detall. Aquesta secció analitza el volum de negoci online generat per les empreses CNAE 47 i el compara amb el total del comerç electrònic a Espanya. El pes sobre el total indica quina proporció de l'e-commerce correspon al comerç al detall — si baixa, vol dir que altres sectors (serveis, turisme, continguts digitals) creixen encara més ràpid en el canal online. El CAGR permet comparar el ritme de creixement amb el del comerç físic."
- **Components visuals**:
  - 4 KPIs: E-commerce CNAE 47 (Md EUR), Multiplicador del període, CAGR, Pes sobre total e-commerce.
  - `st.warning` automàtic si l'últim any sembla parcial (< 85% del previ).
  - Gràfic 1 (barres agrupades): Volum total vs CNAE 47.
  - Gràfic 2 (línia + àrea): Pes CNAE 47 sobre total e-commerce (%).
  - Gràfic 3 (barres bicolor): Creixement interanual.
  - Bloc `insight()` dinàmic que canvia el text segons el signe del trend del pes.
  - Expander de descàrrega CSV.
- **Fonts de dades**: CNMC — Comerç electrònic a Espanya. Cache: `data/cache/ecommerce.csv` amb `ecommerce_total_eur`, `ecommerce_cnae47_eur`, `pes_cnae47_ecommerce`. Trimestral agregat a anual al processador.
- **Freqüència d'actualització**: trimestral (CNMC). Refresh al pipeline trimestral.
- **Text explicatiu/interpretatiu**: moderat. Intro + nota metodològica per any parcial + 1 insight dinàmic.
- **Filtres o interactivitat**: cap.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta (PURPLE, RED, GREEN, GRAY).
  - Llegeix `ecommerce.csv`.

---

## Territori

- **Ruta del fitxer**: `pages/6_Territori.py`
- **Propòsit declarat**: Títol "Territori". Intro literal: "La Comptabilitat Regional de l'INE no desglossa el CNAE 47 per comunitats autonomes. Per estimar el VAB del comerç al detall per CCAA, combinem dues fonts: la comptabilitat regional d'Eurostat (VAB de la secció G-I: comerç, transport i hostaleria) i la xifra de negoci per CCAA de l'Enquesta Estructural d'Empreses de l'INE. El metode hibrid distribueix el VAB nacional del CNAE 47 entre CCAA ponderant les quotes regionals de G-I (top-down) amb les quotes de facturacio (bottom-up), garantint que la suma coincideixi amb el total nacional d'Eurostat."
- **Components visuals**:
  - 4 KPIs Espanya (segons selector d'any): Pes CNAE 47/PIB, Xifra de negoci, Personal ocupat, Locals.
  - Gràfic horitzontal de barres: Pes CNAE 47/PIB per CCAA, amb línia de referència Espanya en vermell. Colors PURPLE/PURPLE_LIGHT segons supera la mitjana.
  - Mapa choropleth Espanya amb inset Canàries: Pes CNAE 47/PIB per CCAA.
  - Gràfic horitzontal: Productivitat (xifra negoci/ocupat) per CCAA en milers EUR, amb línia Espanya.
  - Gràfic horitzontal: Salari mitjà (sous_salaris/ocupat) per CCAA, amb línia Espanya i `st.caption` amb les limitacions (parcialitat, exclusió cotitzacions).
  - 3 blocs `insight()` (pes/PIB, productivitat, salari).
  - Expander de descàrrega CSV.
- **Fonts de dades**: Eurostat `nama_10r_3gva` (G-I regional) + `nama_10_a64` (G47 nacional) + INE EAS taula 76817 (xifra de negoci CNAE 47 per CCAA). Cache: `data/cache/eee_ccaa.csv` (territori, any, vab_eurostat, vab_estimat, xifra_negoci, personal_ocupat, sous_salaris, locals, pes_cnae47_pib).
- **Freqüència d'actualització**: anual.
- **Text explicatiu/interpretatiu**: abundant. Intro metodològica explícita + 3 insights narratius + caption llarga sobre interpretació salari mitjà.
- **Filtres o interactivitat**: `st.select_slider` d'any.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta + `load_geojson_spain_ccaa`, `canaries_inset_layers` (compartit amb Empreses).
  - Llegeix `eee_ccaa.csv`.

---

## Europa

- **Ruta del fitxer**: `pages/7_Europa.py`
- **Propòsit declarat**: Títol via `t("eu_title")`. Intro literal: "Aquesta secció posiciona el comerç al detall espanyol en el context europeu des de dues mirades complementàries. A dalt, el pols mensual del volum de vendes (Eurostat, base 2021=100, ajustat estacional) permet seguir el cicle de consum gairebé en temps real i comparar Espanya amb la mitjana de l'eurozona i la UE-27. A continuació, la mirada estructural anual mostra el pes del CNAE 47 sobre el PIB de cada país […]. Espanya es destaca en vermell per facilitar la comparació."
- **Components visuals**: dues seccions clarament separades amb `st.divider`:
  - **Secció mensual (Eurostat `sts_trtu_m`)**:
    - 4 KPIs: variació interanual vendes ES, Eurozona, UE-27 i índex Espanya (2021=100).
    - Gràfic de línies multipaís: índex de volum de vendes (línia destacada ES, línies EA20/EU27 i altres seleccionables).
    - Gràfic addicional secundari (línies YoY) amb anàlisi automàtica de trend i spread vs Eurozona.
    - Bloc `insight()` dinàmic interpretant accel/desaccel.
  - **Secció anual (Eurostat `nama_10_a64`)**:
    - 3 KPIs: pes ES, mitjana UE-27, posició al rànquing.
    - Gràfic horitzontal: pes CNAE 47/PIB per país (ES destacada en vermell, UE-27 en lila).
    - Gràfic horitzontal: VAB CNAE 47 absolut per país (top 15).
    - Gràfic de línies: evolució del pes CNAE 47 per principals països (ES, DE, FR, IT, PT, UE-27).
    - Bloc `insight()` interpretant la posició i tendència d'Espanya.
  - Expander de descàrrega CSV.
- **Fonts de dades**: Eurostat — `nama_10_a64` (cache `europa_vab.csv`) + `sts_trtu_m` (cache `europa_retail_mensual.csv`). Calcul propi de YoY (`pct_change(periods=12)`).
- **Freqüència d'actualització**: secció anual = anual (publicació Eurostat ~T-1 amb retard). Secció mensual = mensual (cron diari del pipeline; la sèrie es publica amb retard ~45 dies).
- **Text explicatiu/interpretatiu**: abundant. Intro + 2 insights llargs + 2 sources explícits.
- **Filtres o interactivitat**: `st.selectbox` "Període" (24/60/120/all) i `st.multiselect` "Comparar amb altres països" (DE, FR, IT, PT, NL, BE) per a la secció mensual; `st.selectbox` "Any" per a la secció anual.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta.
  - Llegeix 2 caches: `europa_vab.csv` i `europa_retail_mensual.csv`.

---

## Subsectors

- **Ruta del fitxer**: `pages/9_Subsectors.py`
- **Propòsit declarat**: Títol "Subsectors del comerç al detall". Intro literal: "El CNAE 47 agrupa diversos subsectors a tres dígits amb dinàmiques molt diferents: des dels establiments no especialitzats (supermercats, hipermercats) fins al comerç electrònic (CNAE 479) o la venda en mercadillos. S'exclou el CNAE 473 (combustibles per a l'automoció) per la seva naturalesa atípica dins del comerç al detall (preus regulats, dinàmica energètica). Aquesta pàgina creua tres fonts oficials de l'INE per oferir una radiografia tridimensional: Directori d'Empreses (estructura empresarial), Enquesta Estructural d'Empreses (oferta: xifra de negoci, valor afegit, ocupació) i Enquesta de Pressupostos Familiars (demanda: despesa de les llars per tipus de béns)."
- **Components visuals**: és la pàgina més extensa del dashboard (1.057 línies). Organitzada en `st.tabs(["Estructura empresarial", "Activitat i productivitat", "Demanda (despesa famílies)"])`:
  - **KPIs superiors comuns**: 4 mètriques DIRCE — nombre subsectors, total empreses CNAE 47, subsector líder, % del total.
  - **Tab 1 — Estructura (DIRCE T=73019)**: barres horitzontals empreses per subsector amb exemples al hover, captions detallades sobre CNAE 471 i 479; gràfic de variació acumulada per subsector; `insight()` extens sobre concentració top-3, dinàmica creixement/destrucció.
  - **Tab 2 — Activitat (EAS T=76818)**: 3 gràfics horitzontals (xifra de negoci, productivitat VA/persona ocupada, persones ocupades) per subsector, més captions metodològiques.
  - **Tab 3 — Demanda (EPF T=75003 + mapeig COICOP→CNAE)**: gràfic apilat de despesa per categoria COICOP amb mapeig al subsector CNAE; gràfic d'evolució temporal amb multiselect de categories.
  - Expander de descàrrega amb 3 botons separats (DIRCE, EAS, EPF).
- **Fonts de dades**: 3 caches INE: `subsectors_dirce.csv` (T=73019), `subsectors_eas.csv` (T=76818), `subsectors_epf.csv` (T=75003 amb codis COICOP zero-padded). Exclusió explícita del CNAE 473 (combustibles).
- **Freqüència d'actualització**: anual (les 3 fonts són anuals).
- **Text explicatiu/interpretatiu**: abundant. Múltiples intros per tab + 1-2 insights per tab + captions extenses sobre cada subsector (significat, exemples reals com Mercadona/Inditex, divergència CNAE 479 vs CNMC).
- **Filtres o interactivitat**: navegació entre `st.tabs`; `st.multiselect` "sel_codis" a la tab Demanda per filtrar categories COICOP a la sèrie temporal.
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta (incloent ORANGE i PALETTE per categories múltiples).
  - 3 CSVs de cache. Helper local `wrap_text` per formatar hovers Plotly llargs.
  - Diccionaris constants extensos: `SUBSECTOR_LABELS`, `SUBSECTOR_EXAMPLES`, `COICOP_LABELS`, `DEMAND_CNAE_LABELS`, `DEMAND_EXAMPLES`, `COICOP_TO_CNAE`.

---

## Recull de premsa

- **Ruta del fitxer**: `pages/B_Premsa.py`
- **Propòsit declarat**: Títol "Recull de premsa". Subtítol literal: "Notícies seleccionades de fonts sectorials, generalistes i institucionals sobre comerç al detall, distribució i consum a Espanya."
- **Components visuals**:
  - Llista HTML personalitzada amb CSS inline (`.press-item`, `.press-meta`, `.press-titol`, `.press-snippet`) amb límit de MAX_ITEMS=100. Cada element: font (color marca), data formatada relativa ("fa N h", "fa N min", o data absoluta), badge del tipus, títol enllaçat al `link` original, snippet.
  - `st.caption` amb comptador "N notícies · actualitzat cada hora".
  - Sense gràfics ni KPIs.
- **Fonts de dades**: 12 feeds RSS via `modules/press.py::fetch_press()`. Distribución Actualidad, Alimarket (5 categories), Cinco Días (filtrat), Modaes (via Google News `site:`), El Economista (via Google News), INE notes de premsa, Idescat notes de premsa. Cache TTL=3600 (1h).
- **Freqüència d'actualització**: cada hora (cache TTL = 3600 s); els feeds RSS originals s'actualitzen segons cada font.
- **Text explicatiu/interpretatiu**: poc. Subtítol breu + caption del comptador + page_meta amb les fonts.
- **Filtres o interactivitat**: `st.pills` "Tipus de font" (sectorial, generalista, institucional, agregador, multi-selecció); `st.selectbox` "Període" (7/15/30/90/tot); `st.multiselect` "Àrea" (multisector, moda, alimentació, institucional); `st.text_input` "Cerca" lliure; `st.expander` "Fonts específiques (avançat)" amb `st.multiselect` per font individual.
- **Dependències tècniques rellevants**:
  - `style.py`: minimal (`inject_css`, `setup_lang`, `page_header`, `page_meta`).
  - `modules/press.py` (mòdul local, requereix `feedparser`).
  - Sense cache CSV — depèn d'API en viu via RSS.

---

## Estructura UE

- **Ruta del fitxer**: `pages/C_Estructura_UE.py`
- **Propòsit declarat**: Títol "Estructura del retail en context UE". Intro literal: "Aquesta pàgina utilitza la Demografia Empresarial d'Eurostat (bd_size) per situar l'estructura del comerç al detall espanyol davant la UE-27 i les principals economies del comerç al detall europeu. Es tracta de l'única font censal pública que cobreix el CNAE G47 estricte amb metodologia harmonitzada entre estats membres. Coberta 2021-2023 (nou marc metodològic UE 2019/2152). Permet contestar preguntes que les fonts INE soles no responen: el retail espanyol té més o menys rotació empresarial que la mitjana europea? Quina és la supervivència de les noves empreses comparada amb la UE? Quin és el pes dels autònoms (empreses sense assalariats) vs altres països?"
- **Components visuals**:
  - 4 KPIs Espanya darrer any: nombre empreses CNAE 47, ocupació total, % no assalariats (autònoms), taxa rotació BRTH+DTH.
  - Gràfic apilat horitzontal: distribució per mida d'empresa (0, 1-4, 5-9, ≥10 assalariats) — ES vs UE-27 com a percentatges.
  - Gràfic barres agrupades: taxes naixement vs defunció per 8 països (UE27, ES, DE, FR, IT, PT, NL, PL).
  - Gràfic barres horitzontals: mida mitjana (ocupats/empresa) per país, ES destacada PURPLE, UE-27 RED.
  - Gràfic barres apilades: supervivència Y1 i Y2 ES vs UE-27.
  - 4 blocs `insight()` (mida, rotació, mida mitjana, supervivència).
  - Expander de descàrrega CSV + `st.caption` amb nota metodològica sobre canvi de marc UE 2019/2152.
- **Fonts de dades**: Eurostat `bd_size` (Business Demography by Size Class and NACE). Caches: `data/cache/estructura_retail.csv` (indicadors totals), `estructura_retail_mida.csv` (per sizeclas), `estructura_retail_supervivencia.csv` (Y1/Y2).
- **Freqüència d'actualització**: anual. Cobertura temporal **limitada a 2021-2023** per canvi de metodologia UE.
- **Text explicatiu/interpretatiu**: abundant. Intro extensa + 4 insights narratius + caption metodològic explícit sobre la sèrie discontínua respecte al dataset històric `bd_9bd_sz_cl_r2`.
- **Filtres o interactivitat**: cap (només navegació estàtica).
- **Dependències tècniques rellevants**:
  - `style.py`: helpers + paleta.
  - Llegeix 3 caches especialitzats (`estructura_retail*.csv`).

---

## Metodologia

- **Ruta del fitxer**: `pages/8_Metodologia.py`
- **Propòsit declarat**: Títol "Aspectes metodològics". Subtítol literal: "Aquesta secció detalla els criteris de càlcul i les decisions metodològiques adoptades en l'elaboració dels indicadors de l'Observatori. L'objectiu és garantir la transparència i la reproductibilitat de tots els resultats presentats."
- **Components visuals**: text pur via `st.markdown`. 10 subseccions numerades:
  1. Deflació amb IPC: conversió a preus constants.
  2. Càlcul de la productivitat.
  3. Distribució del Valor Afegit: quota salarial i excedent brut.
  4. Salari mitjà per ocupat per CCAA: interpretació i limitacions (inclou taula amb 4 indicadors 2023).
  5. Empreses i densitat comercial.
  6. Estimació del VAB CNAE 47 per CCAA (mètode híbrid).
  7. Comerç electrònic.
  8. Comparativa europea.
  9. Subsectors CNAE 47 i mapeig demanda ↔ oferta (inclou taula COICOP↔CNAE i taula comparativa CNMC vs CNAE 479 anys 2018-2024).
  10. Periodicitat d'actualització.
  - Cap KPI, gràfic, mapa ni filtre. Inclou 2 taules markdown.
- **Fonts de dades**: cap dada llegida. Document estàtic que descriu les fonts utilitzades per les altres pàgines (INE T=50902, 36194, 36199, 76817, 39372, 3954, 298, 73019, 76818, 75003, 2915, 56934; Eurostat nama_10_a64, nama_10r_3gva; CNMC).
- **Freqüència d'actualització**: ad-hoc (editat manualment quan canvia un mètode).
- **Text explicatiu/interpretatiu**: abundant. Tota la pàgina és text. La pàgina té 599 línies entre ca i es.
- **Filtres o interactivitat**: cap.
- **Dependències tècniques rellevants**:
  - `style.py`: minimal (`inject_css`, `setup_lang`, `page_header`, `page_meta`, `PURPLE`).
  - No carrega cap CSV.

---

## Notes transversals

### Components/blocs de codi reutilitzats entre pestanyes

- `style.py` és el mòdul transversal central. Helpers utilitzats per gairebé totes les pàgines:
  - **Estil i estructura**: `inject_css`, `setup_lang`, `page_header`, `page_meta`.
  - **Format de text**: `intro(text)`, `insight(text)`, `source(text)` — blocs HTML estilitzats amb classe pròpia.
  - **Formatatge numèric**: `fnum`, `fpct`, `cagr`.
  - **Plotly**: `apply_layout(fig, **overrides)` aplica un layout estàndard.
  - **Paleta de colors**: `PURPLE`, `PURPLE_LIGHT`, `RED`, `BLUE`, `GREEN`, `ORANGE`, `GRAY`, `PALETTE`.
- **Helpers GeoJSON**: `load_geojson_spain_ccaa(with_canaries_inset=True)` i `canaries_inset_layers()` — utilitzats explícitament per **Empreses** i **Territori** (els dos únics mapes choropleth).
- **Patró bilingüe**: cada pàgina té al començament `_ca = st.session_state.lang == "ca"` seguit d'`if _ca` o expressions ternàries inline. No hi ha sistema de translation keys robust — la pàgina **Inici** sí que fa servir un `t()` per a títols/labels generals (via `translations.json`), però la resta de text utilitza el patró inline.
- **Patró de càrrega de dades**: `@st.cache_data(ttl=3600)` + funció `load_data()` que llegeix `data/cache/<name>.csv` amb fallback a DataFrame buit. Idèntic en pràcticament totes les pàgines.

### Pestanyes que comparteixen fonts de dades

| Cache CSV | Pestanyes que el llegeixen |
|---|---|
| `pib_vab.csv` | Inici, PIB i VAB |
| `empreses.csv` | Inici, Empreses, Ocupació (ràtio treb/empresa) |
| `productivitat.csv` | Inici, Ocupació, Productivitat |
| `ecommerce.csv` | Inici, E-commerce |
| `europa_vab.csv` | Inici, Europa |
| `europa_retail_mensual.csv` | Europa |
| `eee_ccaa.csv` | Inici, PIB i VAB (gràfic CCAA), Territori |
| `cdmge.csv` | Pols diari |
| `subsectors_dirce.csv`, `subsectors_eas.csv`, `subsectors_epf.csv` | Subsectors |
| `estructura_retail.csv`, `estructura_retail_mida.csv`, `estructura_retail_supervivencia.csv` | Estructura UE |
| `ipc.csv` | Cap (deflactor intern del pipeline, no es llegeix a cap pàgina) |
| `municipal.csv` | Només `A_Municipis.py` (no exposat al sidebar públic) |

- `eee_ccaa.csv` és el cache amb més pestanyes consumidores (3): és la sortida de la pàgina Territori però es reutilitza a PIB i VAB (gràfic VAB CCAA nominal vs real) i a Inici (KPIs i conclusions).
- Inici depèn d'**absolutament totes les caches anuals principals** per generar les seves conclusions dinàmiques i el botó d'Excel.

### Inconsistències i duplicats detectats

- **Numeració del fitxer Metodologia vs ordre al sidebar**: el fitxer és `8_Metodologia.py` però apareix com a **última pestanya** al sidebar (després de "Estructura UE"). L'ordre està hardcoded a `app.py` amb `_pages.append(st.Page("pages/8_Metodologia.py", ...))` al final. La numeració del fitxer ja no reflecteix l'ordre real.
- **Salt en la numeració al disc**: existeix `pages/8_Metodologia.py` i `pages/9_Subsectors.py`, però l'ordre al sidebar invertit (Subsectors apareix abans de Metodologia). Convivència de prefixos numèrics + alfabètics (A_, B_, C_) que reflecteix l'ordre d'afegit, no un esquema estable.
- **`A_Municipis.py` no està al sidebar públic**: està registrat a `app.py` darrere de la flag `LOCAL_ONLY = os.environ.get("OBSERVATORI_LOCAL", "0") == "1"`. La pàgina existeix i és funcional però només es publica si la variable d'entorn està activa. No forma part de les 13 pestanyes inventariades.
- **Càlculs duplicats**: el CAGR, les variacions YoY i les ràtios habituals es calculen inline dins de cada pàgina, sense un `analytics.py` o similar. Quan canvia la mètrica conceptual, cal modificar a múltiples llocs.
- **Conclusions dinàmiques d'Inici dupliquen lectures de pestanyes individuals**: la pàgina Inici recalcula les xifres clau (var. empreses, CAGR productivitat, pes UE-27, etc.) que ja es calculen i mostren a les pàgines respectives. No comparteix codi amb elles, només la font CSV.
- **Generació de l'Excel a Inici és gran (200+ línies de `xlsxwriter`)**: tot el codi de construcció de fulls Excel viu dins de `_build_excel()` al fitxer d'Inici. Si es vol mantenir, suggeriria un `modules/excel_export.py`.
- **`fetch_confianza` (taula INE 36499)** té un fetcher a `data/fetchers/ine.py` però **no hi ha cap `process_confianza()`** al processor ni cap CSV a `data/cache/`. Implementació parcial.
- **Pestanya `A_Municipis.py` carrega `municipal.csv` (329 KB)** que segueix al pipeline i es genera periòdicament tot i no ser visible.
- **Mapeig de fonts a la doc**: la pàgina Metodologia §5 menciona "Taula 39372 + Taula 3954 + Taula 298" per empreses, però `pages/2_Empreses.py` no detalla l'orquestració d'aquestes 3 taules (es fa al processor). Aquesta complexitat queda invisible a les pàgines de presentació.

### Pestanyes que sembla que estan a mig fer o desactualitzades

- **Estructura UE**: tècnicament completa però **limitada a 3 anys de dades (2021-2023)** pel canvi metodològic d'Eurostat amb el Reglament UE 2019/2152. La sèrie històrica `bd_9bd_sz_cl_r2` (2008-2020) existeix però no està integrada. Documentat al footer de la pàgina.
- **Pols diari**: és la pàgina amb la dada més recent (granularitat diària) però depèn de l'**estadística experimental CDMGE** de l'INE. Si l'INE deixés de publicar-la o canviés el format, la pàgina deixaria de funcionar. No hi ha fallback definit.
- **E-commerce**: la lògica de detecció d'any parcial (`< 85% del previ`) és heurística i pot fallar en anys de fort decreixement real. La pàgina no té detall per subsector ni per format (B2C vs C2C, marketplaces).
- **Ocupació**: l'únic gràfic té un eix Y range fixat (`yaxis_range=[1500000, 2000000]`); si la sèrie surt d'aquest interval (creixement o caiguda forta) el gràfic clipa la visualització.
- **Empreses**: similar problema al gràfic Espanya (`yaxis_range=[350000, 600000]` fixat). Resta de gràfics CCAA són dinàmics.
- **Productivitat (Tab 3 Marges)**: cita "(Vendes − Cost de mercaderia venuda) / Vendes" a `st.caption` però la implementació depèn de columnes EAS T=36199. Si aquesta taula canvia, els marges trenquen.
- **Recull de premsa**: és la pestanya més recent (commit 2026-05-12). 12 feeds operatius però alguns (Modaes Feedburner, El Economista directe) van haver de redirigir-se via Google News `site:` filter per anti-bot. Risc de fragilitat depenent de canvis a Google News o Modaes.
- **`A_Municipis.py` (fora de l'inventari oficial)**: declarada explícitament com a "(local)" al sidebar quan s'activa la flag. La memòria del projecte la marca com a roadmap pendent amb T=4721 (només G-I agregat). NO és pública.

### Notes finals

- L'ordre real de les 13 pestanyes al sidebar (segons `app.py` actual) és: Inici, Pols diari, PIB i VAB, Empreses, Ocupació, Productivitat, E-commerce, Territori, Europa, Subsectors, Recull de premsa, Estructura UE, Metodologia. Coincideix amb l'ordre demanat.
- Cap pestanya crida una API en viu durant la renderització, excepte **Recull de premsa** (RSS via feedparser amb cache 1h). La resta llegeix CSVs pre-generats per `data/processor.py::process_all()` (cron trimestral via GitHub Actions segons Metodologia §10).
- Bilinguisme: ca/es. No suporta eu/gl ni en (descartat 2026-05-04 per coherència de marca).

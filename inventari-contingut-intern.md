# Inventari de contingut intern — pàgines de dades

Auditoria descriptiva de tots els elements visibles a cada pàgina de dades de l'Observatori. **Sense judici ni recomanacions** — només descripció factual per a decisió posterior.

Codi referenciat: branca `main` local, commit més recent `953291d` (recuperació LECTURA Comparativa Europa).

Pàgines incloses: Inici · Pols diari · PIB i VAB · Empreses · Ocupació · Productivitat · E-commerce · Territori · Subsectors.

Pàgines excloses per acord: Comparativa Europa, Lecturas, Metodologia, Recull de premsa.

---

## Inici (`pages/0_Inici.py`)

### Capçalera de pàgina
- **Títol**: `t("app_title")` → "Observatori del Comerç al detall a Espanya — CNAE 47" (via translations.json)
- **Subtítol**: `t("app_subtitle")` (italica, sota el títol)
- **Nombre total d'elements visibles**: 14

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | Caixa Tesi vigent | `tesi_vigent.json` | Caixa blava destacada amb titol + signatura corporativa + data. Fallback neutre si >10 dies. | No |
| 2 | KPI | VAB CNAE 47 | `pib_vab.csv` | Valor nominal darrer any + delta interanual. | No |
| 3 | KPI | Empreses CNAE 47 | `empreses.csv` | Total Espanya + delta interanual. | No |
| 4 | KPI | Personal ocupat | `productivitat.csv` | Total Espanya + delta interanual. | No |
| 5 | KPI | Productivitat VA/hora | `productivitat.csv` | EUR/hora darrer any + delta. | No |
| 6 | Bloc text | Eyebrow "Pols diari · darrers 12 mesos" + subtítol | — | Capçalera HTML del bloc condensat. | — |
| 7 | Gràfic | Pols diari condensat (línia MM30) | `cdmge.csv` | Variació anual de vendes diàries grans empreses, mitjana mòbil 30 dies, finestra 12 mesos, sense modeBar. | No (lectura curta independent al següent ítem) |
| 8 | Lectura | Lectura curta Pols | `cdmge.csv` | 3-4 línies dinàmiques: signe (creixement/contracció), mitjana 30d, accel vs trimestre anterior. NO usa helper `insight()`, és text directe via `st.markdown`. | Sí (és la lectura) |
| 9 | Altres | Botó "veure detall del Pols diari" | — | `st.page_link` cap a `pages/0a_Pols_diari.py`. | No |
| 10 | Bloc text | "Sobre l'Observatori" | — | Paràgraf + 6 bullets (dimensions del dashboard). Estàtic bilingüe. | No |
| 11 | Lectura | Resum executiu / Principals conclusions | `pib_vab.csv`, `empreses.csv`, `productivitat.csv`, `ecommerce.csv`, `europa_vab.csv`, `eee_ccaa.csv` | Bloc HTML amb fins a 6 conclusions dinàmiques agregades (1 ítem per dimensió). Mostra "Última actualització" llegint `last_update.txt`. | Sí (és lectura agregada) |
| 12 | Altres | Formulari butlletí | — | Helper `newsletter_form()` — caixa MailerLite embed. | No |
| 13 | Altres | Botó descàrrega Excel | `pib_vab`, `empreses`, `productivitat`, `ecommerce`, `eee_ccaa`, `europa_vab` | `st.download_button` amb Excel generat per `_build_excel()` (6 fulls + gràfics XlsxWriter nadius). | No |
| 14 | Bloc text | Signatura corporativa "Observatorio del Comercio · J3B3 Consulting" | — | Caption discret alineat a la dreta. | — |

### Observacions finals
- Llegeix **7 CSVs + 1 JSON** (els 6 principals del dashboard + `cdmge.csv` + `tesi_vigent.json`). Cap altra pàgina llegeix tantes fonts.
- El "Resum executiu" duplica conceptualment les xifres dels KPIs (mateixa dada vista 2 cops) i a més afegeix mètriques de dimensions que els KPIs no toquen (e-commerce, Europa, Territori).
- Estructura: flux continu sense seccions explícites (sense `st.tabs`), però seqüència visual clara (Tesi → KPIs → Pols → Sobre → Conclusions → Butlletí → Excel).
- Sense codis tècnics visibles al cos.

---

## Pols diari (`pages/0a_Pols_diari.py`)

### Capçalera de pàgina
- **Títol**: "Pols diari del consum" / "Pulso diario del consumo"
- **Subtítol/eyebrow**: HTML personalitzat amb eyebrow "GRANULARITAT DIÀRIA · PUBLICACIÓ MENSUAL" + paràgraf descriptiu + bloc `asof` (darrera dada disponible, retard vs avui, propera publicació estimada)
- **Nombre total d'elements visibles**: 11

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | Capçalera HTML completa (eyebrow + sub + asof) | `cdmge.csv` (per `_last_dt`, `_lag_days`, `_next_pub_est`) | Bloc destacat amb metadades de la publicació. | — |
| 2 | KPI | Darrera dada | `cdmge.csv` | Taxa anual del darrer dia publicat amb data. | No |
| 3 | KPI | Mitjana 7 dies | `cdmge.csv` | + delta vs MM30. | No |
| 4 | KPI | Mitjana 30 dies | `cdmge.csv` | + delta vs MM90. | No |
| 5 | KPI | Mitjana 90 dies | `cdmge.csv` | + delta vs MM365 (si disponible). | No |
| 6 | Selector | "Període" (st.radio horitzontal) | — | 3m / 6m / 12m / 24m / Des de 2020. | — |
| 7 | Selector | "Suavitzat" (st.radio horitzontal) | — | Sense / MM7 / MM30 / MM90. | — |
| 8 | Gràfic | Taxa anual diària (línia) | `cdmge.csv` (indicador `tasa_anual`) | Línia amb àrea sota, línia base 0%, vrect ombrejat 2020-03-14 a 2020-06-21 (COVID). | No (anàlisi al següent ítem) |
| 9 | Lectura | Expander "Anàlisi — què diuen les dades ara mateix" (expanded=True) | `cdmge.csv` | Lectura dinàmica narrativa amb signe, accel/desaccel, vs ritme anual, màxim/mínim 90d, com llegir-ho i avís interpretatiu. NO usa helper `insight()`, és `st.markdown` directe dins expander. | Sí (és la lectura) |
| 10 | Bloc text | Expander "Metodologia" (expanded=False) | — | Paràgraf llarg sobre font, què mesura, com es calcula la taxa anual, suavitzat, limitacions, calendari de publicació, raó d'inclusió. Estàtic. | No |
| 11 | Bloc text | `st.caption` final amb font CDMGE | — | Línia única. | — |

### Observacions finals
- 1 sol CSV (`cdmge.csv`).
- 4 KPIs i 1 gràfic alimenten-se de la **mateixa columna** (`valor` del `tasa_anual`), agregada amb diferents finestres. La dada subjacent es presenta en 5 perspectives temporals (1 dia + 4 mitjanes mòbils).
- Estructura: flux continu sense seccions. La metodologia està al cos (dins d'expander col·lapsat), no a la pàgina Metodologia general.
- El bloc d'anàlisi (`expanded=True` per defecte) té contingut narratiu llarg amb subseccions ("Lectura del moment", "Punts singulars dels darrers 90 dies", "Com llegir-ho", "Avis interpretatiu").

---

## PIB i VAB (`pages/1_PIB_i_VAB.py`)

### Capçalera de pàgina
- **Títol**: `t("pib_title")`
- **Subtítol**: `intro()` (caixa estilitzada amb paràgraf bilingüe + nota sobre any base 2002)
- **Nombre total d'elements visibles**: 12

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` metodològic | — | Caixa amb 2 paràgrafs: definició VAB nominal/real, deflactor IPC base 2002, nota sobre any base. | No |
| 2 | KPI | VAB nominal (darrer any) | `pib_vab.csv` | M EUR. | No |
| 3 | KPI | VAB real (darrer any) | `pib_vab.csv` | M EUR. | No |
| 4 | KPI | Pes sobre PIB | `pib_vab.csv` | % darrer any. | No |
| 5 | KPI | CAGR període complet | `pib_vab.csv` | Anys primer-últim. | No |
| 6 | Gràfic | VAB nominal vs real | `pib_vab.csv` | Dues línies (corrents/constants) amb markers. | No (lectura al ítem 7) |
| 7 | Lectura | `insight()` VAB i inflació | `pib_vab.csv` | Variació total, CAGR nominal vs real, efecte inflació, comparativa amb PIB general. | Sí |
| 8 | Gràfic | Pes CNAE 47 sobre PIB | `pib_vab.csv` | Barres anuals amb valors. | No |
| 9 | Gràfic | Variació anual nominal vs real | `pib_vab.csv` | Barres agrupades amb hline 0. | No |
| 10 | Selector | Multiselect CCAA | `eee_ccaa.csv` | Default: Cataluña, Madrid, Andalucía, Comunitat Valenciana. | — |
| 11 | Gràfic | VAB nominal vs real per CCAA seleccionades | `eee_ccaa.csv` (cols `vab_eurostat`, `vab_estimat`) | Línies múltiples (sòlid nominal + dash real). | No |
| 12 | Taula | Expander descàrrega CSV | `pib_vab.csv` | `st.dataframe` + `st.download_button`. | — |

### Observacions finals
- **2 CSVs** (`pib_vab.csv` principal + `eee_ccaa.csv` per gràfic CCAA).
- El gràfic 11 reutilitza `eee_ccaa.csv` que també alimenta tota la pàgina **Territori** — mateixa font, vista diferent (sèrie temporal vs foto d'un any).
- Sense codis tècnics visibles al cos, però la intro menciona "IPC base 2002" i "CAGR".
- Estructura: flux continu (sense tabs), seqüència KPIs → 3 gràfics nacionals → selector CCAA + 1 gràfic regional → descàrrega.

---

## Empreses (`pages/2_Empreses.py`)

### Capçalera de pàgina
- **Títol**: `t("emp_title")`
- **Subtítol**: `intro()` (paràgraf bilingüe sobre interpretació de la caiguda d'empreses)
- **Nombre total d'elements visibles**: 19

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` | — | Definició teixit empresarial + interpretació (concentració vs destrucció). | No |
| 2 | KPI | Empreses darrer any | `empreses.csv` | Total Espanya. | No |
| 3 | KPI | Variació total període | `empreses.csv` | % entre primer i últim any. | No |
| 4 | KPI | Empreses perdudes | `empreses.csv` | Diferència absoluta. | No |
| 5 | KPI | CAGR | `empreses.csv` | Anual compost. | No |
| 6 | Gràfic | Evolució empreses Espanya | `empreses.csv` | Línia + àrea, `yaxis_range=[350000, 600000]` fixat. | No |
| 7 | Gràfic | Taxa variació anual | `empreses.csv` | Barres bicolor verd/vermell amb hline 0. | No |
| 8 | Lectura | `insight()` empreses | `empreses.csv` | Total actual, diferència vs inici, any pic, CAGR, interpretació concentració. | Sí |
| 9 | Gràfic | Densitat comercial Espanya | `empreses.csv` (col `empreses_per_1000hab`) | Línia + àrea. | No |
| 10 | Lectura | `insight()` densitat | `empreses.csv` | Variació densitat, doble efecte població/empreses. | Sí |
| 11 | Selector | Select slider "any" | `empreses.csv` (anys disponibles) | — | — |
| 12 | Altres | Tabs Mapa / Rànquing | — | Navegació interna. | — |
| 13 | Selector | Radio "Mètrica" (dins tab Mapa) | — | Densitat vs absolut. | — |
| 14 | Gràfic | Mapa choropleth CCAA | `empreses.csv` + GeoJSON | Inset Canàries, color escala blava. | No |
| 15 | Gràfic | Rànquing empreses CCAA (barres horitzontals) | `empreses.csv` | Amb línia mitjana vermella + text % sobre total. | No |
| 16 | Gràfic | Rànquing densitat CCAA (barres horitzontals) | `empreses.csv` | Amb línia referència Espanya en vermell. | No |
| 17 | Gràfic | Variació acumulada per CCAA | `empreses.csv` | Barres horitzontals bicolor verd/vermell. | No |
| 18 | Selector | Multiselect CCAA | `empreses.csv` | Default: 4 grans. | — |
| 19 | Gràfic | Evolució CCAA seleccionades | `empreses.csv` | Línies múltiples. | No |

(Final): Expander descàrrega → no comptat com a element narratiu però present.

### Observacions finals
- **1 sol CSV** (`empreses.csv`) alimenta tota la pàgina.
- El mateix concepte (empreses CCAA) es presenta de **4 maneres**: mapa choropleth + rànquing barres + variació acumulada + evolució multilínia.
- Densitat comercial es presenta tant a **nivell nacional** (gràfic 9) com **per CCAA** (gràfic 16) — mateixa mètrica, dues vistes.
- Sense codis tècnics visibles. La densitat menciona "Padrón Municipal" a les fonts.
- Estructura: 3 blocs separats per `st.markdown("---")`: nacional, CCAA dins tabs, evolució CCAA. No són `st.tabs` excepte Mapa/Rànquing.

---

## Ocupació (`pages/3_Ocupació.py`)

### Capçalera de pàgina
- **Títol**: `t("ocu_title")`
- **Subtítol**: `intro()` (paràgraf bilingüe sobre intensitat laboral i ràtio treballadors/empresa)
- **Nombre total d'elements visibles**: 11

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` | — | Definició dimensions ocupats vs hores, parcialitat, ràtio per empresa. | No |
| 2 | KPI | Personal ocupat (darrer any) | `productivitat.csv` | Persones. | No |
| 3 | KPI | Variació període complet | `productivitat.csv` | % primer-últim any. | No |
| 4 | KPI | Hores totals (darrer any) | `productivitat.csv` | En milions. | No |
| 5 | Gràfic | Evolució personal ocupat | `productivitat.csv` | Línia + àrea, `yaxis_range=[1500000, 2000000]` fixat. | No |
| 6 | Gràfic | Hores treballades | `productivitat.csv` | Barres amb valors en M. | No |
| 7 | Gràfic | Hores anuals per treballador | `productivitat.csv` (derivat) | Línia amb markers. | No |
| 8 | Lectura | `insight()` "Més hores, no més contractació" | `productivitat.csv` | Variació personal vs variació hores, reforma laboral 2022, ràtio hores/treballador, contractació vs VA vs xifra negoci. | Sí |
| 9 | Gràfic | Treballadors per empresa | `productivitat.csv` + `empreses.csv` (merged) | Línia amb markers. | No |
| 10 | Lectura | `insight()` ràtio treballadors | `productivitat.csv` + `empreses.csv` | Variació ràtio, interpretació concentració empresarial, qualitat ocupació. | Sí |
| 11 | Taula | Expander descàrrega CSV | `productivitat.csv` | — | — |

### Observacions finals
- **2 CSVs** (`productivitat.csv` principal + `empreses.csv` per ràtio).
- Comparteix `productivitat.csv` amb la pàgina **Productivitat** — mateix CSV, presentació diferent (Ocupació explota persones+hores; Productivitat explota VA/hora + distribució VA + marges).
- Comparteix `empreses.csv` amb la pàgina **Empreses** — mateix CSV, dues pàgines.
- Sense codis tècnics visibles. La intro 2 menciona "reforma laboral 2022" com a hipòtesi explicativa.
- Estructura: flux continu, 2 sub-blocs (ocupats i hores nacionals → ràtio per empresa).

---

## Productivitat (`pages/4_Productivitat.py`)

### Capçalera de pàgina
- **Títol**: `t("prod_title")`
- **Subtítol**: `intro()` (3 perspectives: productivitat, distribució VA, marges)
- **Nombre total d'elements visibles**: 20 (organitzats en 3 tabs)

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` global | — | Introducció als 3 angles. | No |
| 2 | Altres | Tabs Productivitat / Distribució VA / Marges | — | Navegació principal. | — |
| **— Tab 1: Productivitat —** ||||||
| 3 | Bloc text | Intro tab 1 (HTML directe) | — | Explicació VA/hora vs Xifra Negoci/hora i interpretació de marges. | No |
| 4 | KPI | VA/hora darrer any | `productivitat.csv` | EUR/hora. | No |
| 5 | KPI | VA/hora primer any | `productivitat.csv` | EUR/hora. | No |
| 6 | KPI | Variació total | `productivitat.csv` | % primer-últim. | No |
| 7 | KPI | CAGR | `productivitat.csv` | + popover explicatiu sobre el CAGR. | No |
| 8 | Gràfic | Evolució relativa índex base 100 | `productivitat.csv` | Línies VA/hora + Xifra Negoci/hora. | No |
| 9 | Lectura | `insight()` tab 1 | `productivitat.csv` | Productivitat sectorial vs PIB general, marges. | Sí |
| **— Tab 2: Distribució VA —** ||||||
| 10 | Bloc text | Intro tab 2 | — | Quota salarial vs excedent brut, cost laboral. | No |
| 11 | Gràfic | Composició del Valor Afegit | `productivitat.csv` | Apilat: quota salarial vs excedent. | No |
| 12 | Gràfic | Quota salarial | `productivitat.csv` | Línia o barres % VA. | No |
| 13 | Gràfic | Cost laboral per ocupat (preus constants) | `productivitat.csv` | Línia o barres EUR. | No |
| 14 | Lectura | `insight()` tab 2 | `productivitat.csv` | Distribució salarial vs benefici, tendència marges. | Sí |
| **— Tab 3: Marges —** ||||||
| 15 | Bloc text | Intro tab 3 | — | Explicació marges sobre vendes i descomposició xifra negoci. | No |
| 16 | Gràfic | Evolució dels marges sobre vendes | `productivitat.csv` (cols T=36194 + 36199) | Línia(es) amb caption explicatiu "(Vendes - Cost mercaderia) / Vendes". | No |
| 17 | Bloc text | Caption metodològic dins tab 3 | — | `st.caption` amb fórmula del marge. | No |
| 18 | Gràfic | Descomposició de la xifra de negoci | `productivitat.csv` | Apilat: cost mercaderia + altres compres + VA. | No |
| 19 | Lectura | `insight()` tab 3 (×2 segons recompte línies 783 i 843) | `productivitat.csv` | Lectures dinàmiques sobre marges i descomposició. | Sí |
| 20 | Taula | Expander descàrrega CSV | `productivitat.csv` | — | — |

### Observacions finals
- **1 sol CSV** (`productivitat.csv`) alimenta tota la pàgina.
- És la pàgina amb **més blocs text introductoris** (1 global + 1 per tab = 4 totals).
- Codis tècnics visibles: les `source()` mencionen "taula 36194" i "taula 36199" (EAS); el caption del marge mostra una fórmula matemàtica.
- Estructura: organitzada en **3 tabs** (única pàgina, juntament amb Subsectors, que usa tabs com a navegació principal).
- 3 insights al total (1 per tab), més 2-3 captions metodològiques.

---

## E-commerce (`pages/5_Ecommerce.py`)

### Capçalera de pàgina
- **Títol**: `t("ec_title")`
- **Subtítol**: `intro()` (bilingüe sobre canal de venda online)
- **Nombre total d'elements visibles**: 11

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` | — | Definició canal online, pes sobre total, CAGR. | No |
| 2 | KPI | E-commerce CNAE 47 darrer any | `ecommerce.csv` | Md EUR. | No |
| 3 | KPI | Multiplicador primer-últim | `ecommerce.csv` | Factor. | No |
| 4 | KPI | CAGR | `ecommerce.csv` | %. | No |
| 5 | KPI | Pes sobre total e-commerce | `ecommerce.csv` | %. | No |
| 6 | Bloc text | `st.warning` "Nota metodològica" condicional | `ecommerce.csv` | Apareix si l'últim any sembla parcial (volum < 85% previ). | No |
| 7 | Gràfic | Volum e-commerce | `ecommerce.csv` | Barres agrupades total vs CNAE 47. | No |
| 8 | Gràfic | Pes CNAE 47 sobre total | `ecommerce.csv` | Línia + àrea %. | No |
| 9 | Gràfic | Creixement interanual CNAE 47 | `ecommerce.csv` | Barres bicolor verd/vermell. | No |
| 10 | Lectura | `insight()` e-commerce | `ecommerce.csv` | Multiplicador, CAGR, pes evolució, interpretació quota relativa. | Sí |
| 11 | Taula | Expander descàrrega CSV | `ecommerce.csv` | — | — |

### Observacions finals
- **1 sol CSV** (`ecommerce.csv`).
- 3 KPIs (multiplicador, CAGR, pes) i 2 dels 3 gràfics (volum + pes) descriuen aspectes molt pròxims de la mateixa sèrie.
- Sense codis tècnics al cos. Font CNMC mencionada a `source()`.
- Estructura: flux continu, sense tabs ni seccions explícites.
- El `st.warning` és informatiu sobre any parcial — pot aparèixer o no segons les dades del moment.

---

## Territori (`pages/6_Territori.py`)

### Capçalera de pàgina
- **Títol**: "Territori" / "Territorio"
- **Subtítol**: `intro()` (metodologia híbrida Eurostat G-I + INE EAS XN)
- **Nombre total d'elements visibles**: 15

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` metodològica | — | Explicació de l'estimació híbrida + restricció a Eurostat total nacional. | No |
| 2 | Selector | Select slider "any" | `eee_ccaa.csv` (anys amb `pes_cnae47_pib` no nul) | — | — |
| 3 | KPI | Pes CNAE 47 / PIB Espanya | `eee_ccaa.csv` | % darrer any. | No |
| 4 | KPI | Xifra de negoci Espanya | `eee_ccaa.csv` | M EUR. | No |
| 5 | KPI | Personal ocupat Espanya | `eee_ccaa.csv` | Persones. | No |
| 6 | KPI | Locals Espanya | `eee_ccaa.csv` | Unitats. | No |
| 7 | Gràfic | Pes CNAE 47 / PIB per CCAA | `eee_ccaa.csv` | Barres horitzontals, color condicional (sobre/sota mitjana), vline Espanya. | No |
| 8 | Lectura | `insight()` pes/PIB | `eee_ccaa.csv` | Líder vs cua, comptatge CCAA sobre/sota mitjana, interpretació consum vs industrial. | Sí |
| 9 | Gràfic | Mapa choropleth CCAA pes/PIB | `eee_ccaa.csv` + GeoJSON | Inset Canàries, escala blava. | No |
| 10 | Gràfic | Productivitat per CCAA (xifra/ocupat) | `eee_ccaa.csv` (derivat) | Barres horitzontals milers EUR + vline Espanya. | No |
| 11 | Lectura | `insight()` productivitat | `eee_ccaa.csv` | Ràtio top-bottom, factors explicatius (tiquet mig, cadenes, cost de vida). | Sí |
| 12 | Gràfic | Salari mitjà per CCAA (sous/ocupat) | `eee_ccaa.csv` (derivat) | Barres horitzontals EUR + vline Espanya. | No |
| 13 | Bloc text | `st.caption` metodològic sota gràfic salaris | — | 4 línies explicant per què xifra <SMI: parcialitat + exclusió cotitzacions + apartat Metodologia §4. | No |
| 14 | Lectura | `insight()` salari | `eee_ccaa.csv` | Diferencial top-bottom, comparativa cost de vida i cadenes. | Sí |
| 15 | Taula | Expander descàrrega CSV | `eee_ccaa.csv` | — | — |

### Observacions finals
- **1 sol CSV** (`eee_ccaa.csv`) compartit amb pàgina **Inici** (per a 1 conclusió) i **PIB i VAB** (gràfic CCAA).
- 3 indicadors agregats Espanya als KPIs (3, 4, 5) i els mateixos 3 indicadors per CCAA als gràfics 7, 10 i 12 — mateixa dada vista en agregat i desglossada.
- Codis tècnics visibles a les `source()`: "nama_10r_3gva", "nama_10_a64", "taula 76817". El caption del salari té un avís metodològic llarg.
- Estructura: flux continu vertical (selector any → KPIs → 4 gràfics seqüencials cadascun amb lectura → descàrrega).
- Pàgina amb 3 `insight()` consecutius — el major nombre per pàgina (juntament amb Subsectors i Comparativa Europa, aquest últim ja revisat).

---

## Subsectors (`pages/9_Subsectors.py`)

### Capçalera de pàgina
- **Títol**: "Subsectors del comerç al detall" / "Subsectores del comercio minorista"
- **Subtítol**: `intro()` (3 fonts INE: DIRCE estructura + EAS oferta + EPF demanda; exclusió CNAE 473)
- **Nombre total d'elements visibles**: 22 (organitzats en 3 tabs)

### Llista d'elements

| # | Tipus | Títol | Dades font (CSV) | Descripció breu | Té lectura associada? |
|---|---|---|---|---|---|
| 1 | Bloc text | `intro()` global | — | Definició subsectors 3 dígits, exclusió 473 (combustibles), 3 fonts oficials. | No |
| 2 | KPI | Nombre subsectors | `subsectors_dirce.csv` | Comptatge. | No |
| 3 | KPI | Empreses CNAE 47 totals | `subsectors_dirce.csv` | Total agregat. | No |
| 4 | KPI | Subsector amb més empreses | `subsectors_dirce.csv` | Etiqueta + help text. | No |
| 5 | KPI | % del total empreses (líder) | `subsectors_dirce.csv` | %. | No |
| 6 | Altres | Tabs Estructura / Activitat / Demanda | — | Navegació principal. | — |
| **— Tab 1: Estructura empresarial —** ||||||
| 7 | Gràfic | Empreses per subsector (barres horitzontals) | `subsectors_dirce.csv` | Hover amb exemples reals de cadenes (Mercadona, Inditex…). | No |
| 8 | Bloc text | Caption explicatiu CNAE 471 + 479 | — | Paràgraf llarg amb exemples + nota sobre divergència CNMC vs 479. | No |
| 9 | Gràfic | Variació per subsector | `subsectors_dirce.csv` | Barres horitzontals bicolor primer-últim any. | No |
| 10 | Lectura | `insight()` estructura | `subsectors_dirce.csv` | Total empreses, líder, runner-up, concentració top-3, asimetria créixer/perdre, winner/loser, lectura conjunta amb altres tabs. | Sí |
| **— Tab 2: Activitat i productivitat —** ||||||
| 11 | Bloc text | Caption(s) introductoris | — | Captions explicatius sobre EAS T=76818 + interpretació. | No |
| 12 | Gràfic | Xifra de negoci per subsector | `subsectors_eas.csv` | Barres horitzontals darrer any. | No |
| 13 | Gràfic | Productivitat (VA/persona ocupada) | `subsectors_eas.csv` | Barres horitzontals. | No |
| 14 | Gràfic | Persones ocupades per subsector | `subsectors_eas.csv` | Barres horitzontals. | No |
| 15 | Lectura | `insight()` activitat | `subsectors_eas.csv` | Lectures sobre xifra negoci, productivitat i ocupació per subsector. | Sí |
| **— Tab 3: Demanda (despesa famílies) —** ||||||
| 16 | Bloc text | Caption(s) explicatius mapeig COICOP↔CNAE | — | Paràgrafs sobre Encuesta Presupuestos Familiars + categories mapejades. | No |
| 17 | Gràfic | Despesa per categoria COICOP | `subsectors_epf.csv` | Barres horitzontals amb subsector CNAE equivalent al hover. | No |
| 18 | Selector | Multiselect codis COICOP | `subsectors_epf.csv` | Per seleccionar categories a la sèrie temporal. | — |
| 19 | Gràfic | Evolució despesa al llarg del temps | `subsectors_epf.csv` (preus constants) | Línies múltiples categories seleccionades. | No |
| 20 | Lectura | `insight()` demanda | `subsectors_epf.csv` | Lectura sobre canvis de despesa familiar i mapeig amb subsectors retail. | Sí (×2 segons línies 944 i 983) |
| 21 | Taula | Expander descàrrega 3 CSVs (botons separats) | `subsectors_dirce.csv`, `subsectors_eas.csv`, `subsectors_epf.csv` | DataFrame de cadascun + 3 download_buttons. | — |

### Observacions finals
- **3 CSVs** (`subsectors_dirce`, `subsectors_eas`, `subsectors_epf`) — única pàgina amb 3 fonts independents.
- 4 KPIs superiors derivats només de DIRCE (visibles a totes les tabs en mantenir-se al cap). La resta de fonts (EAS i EPF) només apareixen dins de les seves tabs.
- Codis tècnics visibles al cos: "taula 73019" (DIRCE), "taula 76818" (EAS), "taula 75003" (EPF) a `source()`; captions amb "CNAE 471", "CNAE 479", comparativa numèrica CNMC vs CNAE 479 amb taula d'anys 2018-2024.
- Estructura: organitzada en **3 tabs** (única pàgina, juntament amb Productivitat). És la pàgina amb major volum de codi (1063 línies).
- Conté el major nombre de **captions metodològiques al cos** (línies 325, 344, 506, 517, 777, 786 — 6 captions independents), incloent una taula markdown comparativa CNMC vs CNAE 479.

---

## Notes tècniques pel camí

Anotacions factuals trobades durant la inventari, sense interpretar:

1. **CSV `productivitat.csv` consumit per 3 pàgines** amb dimensions diferents: Inici (KPIs agregats), Ocupació (persones + hores + ràtio), Productivitat (VA/hora + distribució VA + marges). El mateix fitxer alimenta presentacions molt diferents.

2. **CSV `empreses.csv` consumit per 3 pàgines**: Inici (1 KPI), Empreses (tota la pàgina), Ocupació (ràtio treballadors/empresa).

3. **CSV `eee_ccaa.csv` consumit per 3 pàgines**: Inici (conclusió Territori), PIB i VAB (gràfic CCAA), Territori (tota la pàgina).

4. **CSV `cdmge.csv` consumit per 2 pàgines**: Inici (gràfic condensat + lectura curta) i Pols diari (pàgina completa).

5. **Total CSVs únics que alimenten les 9 pàgines**: 11 + 1 JSON (`tesi_vigent.json`).
   Llista: `pib_vab`, `empreses`, `productivitat`, `ecommerce`, `europa_vab`, `eee_ccaa`, `cdmge`, `subsectors_dirce`, `subsectors_eas`, `subsectors_epf`, `last_update.txt` (metadata).
   (Comparativa Europa, fora d'aquest inventari, afegiria `europa_retail_mensual.csv` + 3 `estructura_retail*.csv`.)

6. **Patrons de presentació duplicats**: tres pàgines (Empreses, Territori, Comparativa Europa) usen el helper `load_geojson_spain_ccaa` + `canaries_inset_layers` per renderitzar mapes choropleth amb la mateixa lògica d'inset Canàries.

7. **Helper `insight()` usat 13 vegades al conjunt de pàgines inventariades**:
   - PIB i VAB: 1 · Empreses: 2 · Ocupació: 2 · Productivitat: 3 · E-commerce: 1 · Territori: 3 · Subsectors: 2 (potser 3, hi ha dos `insight()` a línies 944 i 983 dins la mateixa branca).

8. **Pàgines amb `yaxis_range` hardcoded** (potencial clipping si la sèrie sobresurt): `2_Empreses.py` (350.000–600.000) i `3_Ocupació.py` (1.500.000–2.000.000). Documentat a `inventari-observatorio.md` (Fase 1) i `verificacio-fase1.md`.

9. **Pàgines amb tabs com a navegació principal**: només `4_Productivitat.py` (3 tabs) i `9_Subsectors.py` (3 tabs). La resta són flux vertical continu.

10. **Lectures dinàmiques fora del helper `insight()`**: 2 casos:
    - `0_Inici.py` línies 282-313 — lectura curta del Pols condensat (text via `st.markdown` directe).
    - `0a_Pols_diari.py` línies 242-279 — lectura dinàmica dins d'expander "Anàlisi" (text via `st.markdown` directe).
    En aquests 2 casos no s'usa la caixa estilitzada `.insight-box` sinó renderització nativa de Streamlit/Markdown.

11. **Captions metodològics al cos (no a la pàgina Metodologia)** repartits:
    - `4_Productivitat.py`: caption amb fórmula del marge ("Vendes − Cost mercaderia / Vendes") al tab 3.
    - `6_Territori.py`: caption llarg (10 línies) sota el gràfic de salari mitjà explicant per què la xifra pot ser inferior a l'SMI.
    - `9_Subsectors.py`: 6 captions independents en diferents tabs amb context CNAE i comparatives numèriques.

12. **`st.warning` usats com a missatge informatiu condicional** (no com a alerta d'error):
    - `5_Ecommerce.py`: avís sobre any parcial si volum < 85% previ.
    - Diverses pàgines: `st.warning("No hi ha dades disponibles…")` com a fallback general (no funcional si tot funciona).

13. **Pàgina `0_Inici.py` és l'única que genera output multi-pàgina** (`_build_excel` amb 6 fulls i gràfics XlsxWriter nadius equivalents als de Plotly). Aquest codi (~200 línies) viu dins del fitxer d'Inici i NO és reaprofitable per altres pàgines en la forma actual.

---

*Fi de l'inventari. Sense propostes de canvi; només descripció.*

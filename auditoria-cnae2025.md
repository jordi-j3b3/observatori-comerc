# Auditoria d'impacte CNAE-2025 / NACE Rev. 2.1 sobre l'observatori

Data: 2026-06-26. Abast: tot el pipeline de dades (CNAE 47, CNAE-2009).

## Resum executiu

L'observatori està construït 100% sobre la divisió 47 de CNAE-2009. La nova **CNAE-2025** (Reial decret 10/2025; data operativa 1 de gener de 2025) i la seva matriu europea **NACE Rev. 2.1** canvien el perímetre i l'estructura interna del comerç al detall. Lectures:

1. **No és una emergència, però el rellotge ja corre per Europa.** Les fonts Eurostat que fem servir (vendes mensuals, demografia empresarial, estructura SBS) ja publiquen en NACE Rev. 2.1 per a l'any de referència 2025. Les pàgines **Comparativa Europa** i **Trajectòria estructural** són les primeres exposades, ja el 2026.

2. **La pedra angular —PIB/VAB de Comptabilitat Nacional— és l'última a moure's: publicació prevista el setembre de 2029, però amb retropolació fins al 1995.** Això és bona notícia: aquella sèrie arribarà enllaçada, sense trencament.

3. **El canvi conceptual que més ens afecta és la desaparició del canal de venda dins el 47.** La nostra lectura de "venda no establerta / online" i el perímetre "47 sin 473" deixen de tenir el mateix significat. Subsectors i el mapeig COICOP→CNAE s'hauran de refer.

4. **El total del 47 deixa de ser comparable abans i després**, perquè la dissolució de la divisió 45 hi afegeix el comerç minorista de vehicles (nou grup 47.8). Caldrà advertir-ho a Metodologia i decidir si enllacem amb correspondència o trenquem la sèrie.

5. **Hallazgo immediat, independent del CNAE: l'EPF ja fa servir COICOP 2018.** El cache `subsectors_epf` ja porta l'estructura nova (13 entrades: total + 12 grups). El fetch no es trenca, però els continguts d'alguns grups han canviat —el grup 8 passa de "Comunicaciones" a "Información y comunicaciones"— i el nostre mapeig COICOP→CNAE 47 (`pages/9_Subsectors.py`) es va construir amb la semàntica antiga. Cal revalidar-lo ara, no és un tema futur.

## El canvi, amb precisió

Tres modificacions toquen la divisió 47:

- **Es dissol la divisió 45** (vehicles): es reparteix entre 46 (engròs), 47 (detall) i 95/secció T (reparació). El comerç minorista de vehicles entra al 47 com a **nou grup 47.8** (47.81 vehicles, 47.82 recanvis, 47.83 motocicletes).
- **S'elimina el canal de venda com a criteri.** L'estructura del 47 passa a ordenar-se per producte; la venda per internet, correu o parada es classifica dins la classe de producte que correspongui.
- **Matís sobre el codi 4791** (per als lliurables): no és exacte dir "desapareix el 4791". El que desapareix és el *concepte de canal*. El codi **47.9 es reutilitza amb significat nou** ("serveis d'intermediació per al comerç al detall": 47.91 / 47.92), i el **47.8** s'ha reassignat a vehicles. Dir "el 4791 desapareix" és rebatible; el correcte és "el comerç electrònic deixa de ser una categoria pròpia i es reparteix per producte".

Fonts: [CNAE-2025 (INE, PDF)](https://www.ine.es/daco/daco42/clasificaciones/cnae25/CNAE_2025.pdf) · [RD 10/2025 (BOE)](https://www.boe.es/buscar/act.php?id=BOE-A-2025-587) · [Nota implantació CNAE-2025 a l'INE](https://www.ine.es/clasifi/nota_informativa_CNAE2025.pdf) · [CCAE-2025, Decret 99/2025 (Idescat)](https://www.idescat.cat/novetats/?id=5214)

## Calendari de migració per font (el disparador)

Ordenat pel moment en què la font comença a publicar en CNAE-2025 / NACE 2.1. Aquest és el moment en què ens toca actuar a cada pàgina.

| Font (cache) | Origen | Primera publicació CNAE-2025 / NACE 2.1 | Sèrie enllaçada enrere? |
|---|---|---|---|
| Vendes retail mensual (`europa_retail_mensual`) | Eurostat `sts_trtu_m` | Ja: períodes des de gen-2025 (doble report fins 2027) | Backcasting + correspondència previstos |
| Demografia/mida UE (`estructura_retail`, `_mida`, `_supervivencia`) | Eurostat `bd_size` | Ref. 2025 | Doble report ref. 2025 |
| VAB i ocupació UE (`europa_vab`, `ocupacio_comerc`, `digitalitzacio_comerc`) | Eurostat `nama_10_a64`, `lfsa_*`, `isoc_*` | NACE 2.1 progressiu des de ref. 2025 | Política de backcasting; detall no confirmat |
| Empreses i subsectors (`empreses`, `subsectors_dirce`) | INE DIRCE | Edició publicada el **2026** (ref. 2025); l'edició 2025 encara és CNAE-2009 | Només taula de correspondència |
| Estructura empresarial (`subsectors_eas`, `subsectors_472`, `productivitat`, `eee_ccaa`) | INE EEE-Comerç | **2027** (ref. 2025) | No compromès |
| Índex de comerç al detall (`icm`, `icm_distribucion`) | INE ICM | **mar-2028** (ref. gen-2028) | No compromès |
| Salaris (`eaes`) | INE EAES | **2028** (ref. 2026) | No confirmat |
| Despesa de les llars (`subsectors_epf`) | INE EPF (75003) | CNAE: ~2028. **COICOP 2018: JA aplicat (EPF 2024)** | COICOP: sèrie homogènia 2016-2024 |
| PIB i VAB (`pib_vab`) | INE Comptabilitat Nacional | **set-2029** (canvi de base; ref. 1995-2028) | **Sí, retropolació a 1995** |
| Pols diari (`cdmge`) | INE (taula 37808) | Per confirmar (vegeu incerteses) | — |
| IPC (`ipc`, deflactor) | INE IPC | **No afectat per CNAE** (és ECOICOP; canvi de base 2025 independent) | n/a |

## Impacte i acció per àmbit

| Àmbit / pàgina | Impacte | Acció recomanada |
|---|---|---|
| Comparativa Europa, Trajectòria estructural | **Primer exposat** (Eurostat ja en NACE 2.1) | Verificar que el filtre `G47` segueix retornant dades; aprofitar el doble report 2025-2027 per validar el salt |
| Empreses, Subsectors (oferta) | Alt: estructura 471-479 i 4721-4729 pot canviar; +vehicles al total 47 | Re-mapejar diccionaris de subsectors amb la correspondència oficial quan surti DIRCE 2026 |
| Subsectors (demanda, EPF) i mapeig COICOP→CNAE | Alt i en part **ja actiu** (COICOP 2018) | Verificar ara el nombre de grups COICOP que retorna la 75003; refer el mapeig "01"-"12" si calen 13 grups |
| ICM i "47 sin 473" | Mig: el perímetre i els modes de venda canvien de significat | Replantejar la lectura de modes de venda quan ICM passi a CNAE-2025 (2028) |
| PIB i VAB | Baix a curt termini (no migra fins 2029) i amb sèrie enllaçada | Cap acció fins 2029; documentar a Metodologia que arribarà retropolat |
| Líders (SABI) | Mig: 13 codis CNAE-2009 hardcodejats | Re-mapejar els codis SABI en el pròxim export manual |
| Total 47 (perímetre global) | Trencament de comparabilitat (+vehicles) | Decisió de mètode: enllaçar amb correspondència o trencar sèrie i explicar-ho |

## Decisió de fons pendent (de mètode, teva)

Per a cada font, quan flipi a CNAE-2025, dues opcions: **(a) enllaçar** la sèrie nova amb l'antiga via taula de correspondència oficial CNAE-2009↔2025 (continuïtat, però amb una nota de ruptura), o **(b) trencar** la sèrie i mostrar 2009 i 2025 com a dos trams, explicat a Metodologia. La recomanació natural: enllaçar on hi ha retropolació oficial (PIB/VAB), trencar i advertir on no n'hi ha (ICM, EEE).

## Annex: punts del codi a tocar (hotspots)

Literals de codi CNAE sensibles, per fitxer (de l'inventari del pipeline):

- `data/fetchers/ine.py`: filtres `"47"` (línies 224, 784), `"47 sin 473"` (1175); diccionaris de subsectors 471-479 (699-722) i 4721-4729 (727-741).
- `data/fetchers/cnmc.py` (e-commerce): set de ~23 codis de 4 dígits i combinacions (18-27), inclosos codis mixtos engròs+detall que la nova estructura recompondrà.
- `data/fetchers/eurostat.py`: paràmetre `nace_r2="G47"` (104, 175, 267, 298, 339, 387, 461, 489, 518) i `"G-I"` (218, 242).
- `data/processor.py`: diccionari de subsectors SABI (1427-1431); desglossament 472 (1160-1167).
- `pages/9_Subsectors.py`: diccionaris `SUBSECTORS_*` (41-60), `SUBSECTORS_ALIM_472` (1135-1146), `EXCLUDE_CODES=["473"]` (65), mapeig COICOP→CNAE (181-188).

## Incerteses (no resoltes encara)

- **Retropolació** d'ICM, DIRCE, EEE-Comerç i EAES: la nota de l'INE dona dates de publicació però no compromet sèrie enrere. Cal esperar la nota metodològica de cada operació.
- **`cdmge`**: l'inventari del codi l'identifica com a taula INE 37808 amb perímetre 47; la recerca externa va apuntar a una estadística de targetes del Banc d'Espanya (classificada per MCC, no CNAE). Discrepància a resoldre: confirmar l'origen real i si li aplica la migració CNAE.
- **EPF i COICOP 2018**: verificat que la 75003 ja retorna l'estructura nova (13 entrades, total inclòs); cap grup queda sense carregar. Pendent: revalidar la correspondència COICOP→CNAE 47 contra els continguts COICOP 2018 (atenció al grup 8, "Información y comunicaciones" → CNAE 474).
- Data "3 de març de 2025" que es va esmentar com a entrada en vigor: **no verificada** al BOE (el RD entra en vigor el 16 de gener de 2025; la data operativa és l'1 de gener de 2025). No usar el "3 de març" sense confirmar-ne la font.

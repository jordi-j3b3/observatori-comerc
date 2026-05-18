# Arquitectura de l'Observatori del Comerç — Pla d'execució per fases

**Sessió**: 18 de maig de 2026 (avançada respecte al calendari original del 20)
**Validat per**: Jordi Bacaria (J3B3 Consulting)
**Destinatari**: Claude Code, com a instrucció executable per a la Fase 1

---

## 0. Marc estratègic acordat

- L'Observatori segueix un model de creixement orgànic (**Opció A**): no hi ha llançament campanya, el web creix amb el contingut.
- L'1 de juny **no és un deadline d'acabament**. És una vitrina dins d'una jornada del Col·legi d'Economistes de Catalunya (30 presencials + 60 online, perfil economistes). L'Observatori apareix 5-7 minuts dins d'una intervenció de 30' sobre PIB del comerç + comparativa Europa. Es prioritza el polit de 2 pantalles per damunt de tenir-ho tot.
- **Arquitectura dual**: capa visible (frontend) + motor backend (mitjà de producció, invisible a l'usuari). El motor no és producte d'usuari final. Es construeix a la Fase 2 amb tranquil·litat.
- **Filosofia rectora**: fer fàcil el difícil. Tot el que no ho fa, fora o s'amaga.
- **Frontera de monetització**: es decideix en sessió posterior. La Fase 1 no la implementa.
- **Idioma per defecte**: castellà. Català disponible com a opció via selector. La presentació del Col·legi pot ensenyar-se en català activant el selector.

---

## 1. Personas i preguntes prioritàries

### Persona zero — Economista del Col·legi (audiència 1 de juny)

1. ¿Quines fonts integra i fins on arriba? (¿és rigorós o és casolà?)
2. ¿Què hi ha aquí que no pugui obtenir jo mateix d'altres llocs? (¿quin és el diferencial real?)
3. ¿Qui hi ha al darrere i quin punt de vista té? (¿hi ha veu signada o és un dashboard anònim?)

### Persona 1 — Director estratègic retail (Tipus 1)
*[Per omplir a la sessió posterior — no és bloquejant per a Fase 1]*

### Persona 2 — Periodista/analista sectorial (Tipus 2)
*[Per omplir a la sessió posterior]*

### Persona 3 — Inversor amb exposició retail (Tipus 3)
*[Per omplir a la sessió posterior]*

### Persona 4 — Institucional sectorial (Tipus 4)
*[Per omplir a la sessió posterior]*

---

## 2. Mapa A — Capa visible (frontend)

### Estructura jeràrquica acordada

```
HOME (Inici reformulada)
├── Tesi vigent signada (redacció manual setmanal)
├── 3-4 xifres-cop del moment del consum
├── Bloc condensat del Pols diari (1 gràfic + lectura curta)
├── Botó "veure Pulso complet de la setmana"
├── Formulari butlletí (CTA principal)
└── Botó descàrrega Excel (al peu)

SECCIÓ 1 — LECTURAS
├── Pulso de la setmana (entrada principal)
├── Arxiu de pulsos
└── Track record de prediccions

SECCIÓ 2 — RADIOGRAFIA
├── PIB i VAB
├── Empreses
├── Treball i productivitat       ← fusió Ocupació + Productivitat (Fase 2)
├── E-commerce
└── Comparativa Europa            ← fusió Europa + Estructura UE (Fase 1)

SECCIÓ 3 — DETALL
├── Subsectors
└── Territori

PEU
├── Metodologia
└── Recull de premsa              ← rebaixada de pestanya a auxiliar
```

**Reducció efectiva**: de 13 pestanyes planes a 8 elements de navegació principal (home + 3 seccions amb 9 pàgines + 2 elements de peu). Sense pèrdua de contingut.

### Pantalles del nucli polit per a l'1 de juny

**Pantalla 1 — Home reformulada**

- **Què mostra**: tesi vigent signada + 3-4 KPIs estructurals + bloc condensat del Pols diari + botó al Pulso complet + formulari butlletí + Excel al peu.
- **Per què aquesta**: és el primer cop d'ull. Contesta les tres preguntes de la persona zero en una sola pantalla — rigor de fonts (KPIs amb font visible), diferencial (lectura signada), veu (signatura JBJ visible).
- **Què cal fer per polir-la**:
  - Eliminar el botó-link a la infografia Q1 2026 i tot el codi associat (`static/infografia_q1_2026.html` queda al projecte però sense enllaç visible).
  - Afegir bloc tesi vigent al cap de la home (redacció manual, vegi §3 Pipeline editorial).
  - Condensar el Pols diari a 1 gràfic + lectura curta (extreta de la versió completa que ara és pestanya).
  - Mantenir Excel al peu, no al cap.
  - Tipografia neta consultora-grade (referència: V3 del Pla de Comunicació).
  - Verificar que la signatura "Jordi Bacaria · J3B3 Consulting" apareix de manera clara però discreta.

**Pantalla 2 — Comparativa Europa unificada**

- **Què mostra**: fusió de l'actual Europa + Estructura UE. Quatre blocs integrats:
  1. **Posicionament estructural** (gràfic principal del teu estudi): Pes CNAE 47/PIB per país, ES destacada en vermell.
  2. **Evolució del posicionament**: Pes per principals països (ES, DE, FR, IT, PT, UE-27) en sèrie temporal.
  3. **Dimensió estructural** (de l'actual Estructura UE): mida d'empresa, rotació, supervivència ES vs UE-27.
  4. **Pols mensual europeu**: índex de volum de vendes multipaís.
- **Per què aquesta**: és la pàgina que sustenta literalment la teva intervenció. El moment de la presentació on dius "el que us he ensenyat en slide està viu i comparat aquí" cau sobre aquesta pantalla.
- **Què cal fer per polir-la**:
  - Fusionar `pages/7_Europa.py` i `pages/C_Estructura_UE.py` en una sola pàgina.
  - Ordre intern: primer els dos gràfics estructurals del PIB/VAB (els que reflecteixen la teva slide), després la dimensió estructural com a tercer bloc, després el pols mensual com a quart bloc.
  - Mantenir coherència visual amb les slides de la presentació (validar a la fase de Claude Code).
  - Lectura interpretativa damunt de cada bloc (estil "LECTURA" de la V3 del Pla de Comunicació).
  - Nota metodològica accessible amb un clic (no exposada).

### Pàgines que no es toquen a la Fase 1

PIB i VAB, Empreses, E-commerce, Subsectors, Territori, Metodologia, Recull de premsa, Productivitat i Ocupació. Continuen funcionant tal com estan. La reorganització del sidebar les reagrupa però no en modifica el contingut intern. La fusió Ocupació+Productivitat és Fase 2.

---

## 3. Mapa B — Motor backend (principis)

Es fixen els principis. Implementació detallada a la Fase 2.

- **Què entra al corpus**: totes les sèries actualment al pipeline (`pib_vab`, `empreses`, `productivitat`, `ecommerce`, `europa_vab`, `europa_retail_mensual`, `eee_ccaa`, `cdmge`, `subsectors_dirce/eas/epf`, `estructura_retail*`).
- **Com s'estructuren les sèries**: model entitats-temps-variable (cada observació té entitat geogràfica, dimensió sectorial, unitat temporal, font, indicador). Unitat mínima reutilitzable = una sèrie identificada per (entitat × dimensió × indicador × periodicitat).
- **Què queda fora explícitament**: dades que no provenen de fonts oficials (INE, Eurostat, CNMC). No s'integren reports privats, dades de proveïdors comercials, ni estimacions de tercers.
- **Fonts integrades a la Fase 1**: les actuals. Sense canvis.
- **Fonts diferides a la Fase 2**: datasets Eurostat addicionals esmentats al briefing original (bd_size redissenyant Estructura Empresarial, bd_hgnace_r per a empreses d'alt creixement provincial).
- **Tecnologia preliminar**: a decidir a la Fase 2. Hipòtesi raonable: DuckDB + parquet per a corpus consolidat, mantenint els CSVs de cache actuals com a sortida pública.

---

## 4. Mapa C — Frontera de monetització (marcatge, no implementació)

Es deixa explícitament diferit. La sessió de monetització és posterior.

- **Capa pública gratuïta (per defecte avui)**: tot el que hi ha actualment.
- **Capa premium hipotètica**: descàrregues de sèries completes via motor, alertes sobre indicadors, arxiu complet de tesis i prediccions, informes a mida.
- **Decisions diferides**: preu, gateway de pagament, autenticació, segmentació institucional vs individual.

---

## 5. Pla d'execució — Fase 1 (fins a l'1 de juny)

**Instruccions executables per a Claude Code**, en ordre de prioritat:

### 5.1 — Reorganització del sidebar (`app.py`)

Reestructurar `st.navigation()` per agrupar les pàgines segons l'estructura del §2:

```
HOME
└── Inici

LECTURAS
└── (placeholder — Pulso de la setmana, en construcció Fase 2)

RADIOGRAFIA
├── PIB i VAB
├── Empreses
├── Ocupació          (mantenir separada — fusió Fase 2)
├── Productivitat     (mantenir separada — fusió Fase 2)
├── E-commerce
└── Comparativa Europa  (fusió Europa + Estructura UE, vegi §5.3)

DETALL
├── Subsectors
└── Territori

RECURSOS
├── Metodologia
└── Recull de premsa
```

**Nota**: el Pols diari deixa de tenir entrada al sidebar principal. La pàgina queda al codi com a `pages/0a_Pols_diari.py` però sense aparèixer al sidebar. S'hi accedeix només des de la home via botó "veure Pols diari complet".

### 5.2 — Home reformulada (`pages/0_Inici.py`)

Modificacions concretes:

1. **Afegir bloc "Tesi vigent" al cap de la pàgina**, immediatament després del títol i abans dels KPIs:
   - Container amb estil destacat
   - Camp llegit des de `data/cache/tesi_vigent.json` (vegi §5.5 per a la generació)
   - Mostra: títol curt de la tesi (15-20 paraules), peu amb signatura "Jordi Bacaria · J3B3 Consulting" i data de publicació.
   - Si el fitxer no existeix o és antic (>10 dies), mostrar placeholder neutre sense trencar la pàgina.

2. **Afegir bloc condensat del Pols diari** després dels 4 KPIs i abans del resum executiu:
   - 1 gràfic (taxa anual interanual amb MM30 per defecte, finestra 12 mesos)
   - Lectura curta (3-4 línies) generada amb la mateixa lògica que la pàgina completa
   - Botó/enllaç "veure el detall del Pols diari" que porti a `pages/0a_Pols_diari.py`

3. **Eliminar el botó-link a la infografia Q1 2026**:
   - Treure el botó visible de la home
   - Mantenir el fitxer `static/infografia_q1_2026.html` al projecte (per si es vol recuperar)
   - Eliminar qualsevol referència al text de la home

4. **Reordenar elements**:
   - Cap: títol + Tesi vigent + KPIs
   - Cos: Pols diari condensat + Resum executiu / Conclusions
   - Peu: Formulari butlletí + Botó Excel

5. **Mantenir intactes**: KPIs actuals, conclusions dinàmiques, generador d'Excel.

### 5.3 — Fusió Europa + Estructura UE

Crear nova pàgina `pages/7_Comparativa_Europa.py` que substitueix les dues actuals:

- Renombrar/eliminar `pages/7_Europa.py` i `pages/C_Estructura_UE.py`
- Nova pàgina amb estructura interna en 4 blocs (en aquest ordre):

  **Bloc 1 — Posicionament estructural (gràfic principal del teu estudi)**
  - Gràfic horitzontal: Pes CNAE 47/PIB per país, ES destacada vermell, UE-27 lila
  - 3 KPIs damunt: pes ES, mitjana UE-27, posició al rànquing
  - Bloc LECTURA interpretativa

  **Bloc 2 — Evolució del posicionament**
  - Gràfic de línies: evolució del pes per principals països (ES, DE, FR, IT, PT, UE-27)
  - Bloc LECTURA interpretativa

  **Bloc 3 — Dimensió estructural (de l'actual Estructura UE)**
  - Gràfic apilat horitzontal: distribució per mida d'empresa ES vs UE-27
  - Gràfic barres agrupades: naixement vs defunció per 8 països
  - Gràfic barres horitzontals: mida mitjana per país
  - Gràfic barres apilades: supervivència Y1 i Y2 ES vs UE-27
  - 4 blocs LECTURA (un per gràfic, breus)

  **Bloc 4 — Pols mensual europeu**
  - Gràfic línies multipaís (índex volum vendes)
  - Bloc LECTURA dinàmica accel/desaccel

- Mantenir totes les fonts de dades actuals (`europa_vab.csv`, `europa_retail_mensual.csv`, `estructura_retail*.csv`)
- Nota metodològica al peu (no exposada): canvi de marc Eurostat 2019/2152 que limita la sèrie demogràfica a 2021-2023.

### 5.4 — Reorganització de Recull de premsa i Metodologia com a Recursos

A `app.py`, agrupar Metodologia i Recull de premsa en una secció "Recursos" del sidebar. No cal modificar el contingut de les pàgines.

### 5.5 — Pipeline de tesi vigent (Opció B: redacció manual)

Crear infraestructura mínima per a publicar la tesi setmanal:

- Fitxer `data/cache/tesi_vigent.json` amb estructura:
  ```json
  {
    "titol": "Frase de 15-20 paraules",
    "data_publicacio": "2026-05-25",
    "autor": "Jordi Bacaria",
    "enllac_pulso": "URL al Pulso complet (opcional)"
  }
  ```
- Procediment d'actualització manual: Jordi edita el JSON cada dilluns després del Pulso. No cal interfície d'edició a la Fase 1.
- Per a la presentació de l'1 de juny: tenir la tesi del 25 de maig (Prova 2) i la de l'1 de juny (Prova 3) preparades amb anticipació.

### 5.6 — Selector d'idioma visible

L'idioma per defecte passa a ser **castellà** (actualment ca/es bilingüe sense default explícit).

- Modificar `style.py::setup_lang()` perquè per defecte sigui `es` quan no hi ha selecció prèvia.
- Mantenir el selector ca/es visible al header (ja existeix, només cal verificar que funciona).
- Per a la presentació al Col·legi: activar manualment català abans de començar.

### Criteri d'acabat Fase 1

Les 2 pantalles del nucli polit (Home + Comparativa Europa) estan en l'estat que Jordi valida com a presentable al Col·legi. La resta del web pot estar tal com queda després de §5.1 a §5.6, però no ha d'estar trencat ni semblar abandonat. Cap regressió funcional en pàgines no modificades.

---

## 6. Pla d'execució — Fase 2 (juny-setembre)

Backlog ordenat per prioritat, sense data exacta:

1. **Motor backend (Mapa B)**: model entitats-temps-variable amb DuckDB o equivalent, sobre el corpus actual. Pipeline de regeneració dels CSVs des del motor (no des de scripts independents).
2. **Fusió Ocupació + Productivitat** en una sola pàgina "Treball i productivitat", organitzada en tabs lògics.
3. **Pulso de la setmana com a pàgina principal** dins de Lecturas (avui placeholder). Llegit des del pipeline editorial del Pulso.
4. **Arxiu de pulsos i Track record de prediccions** a Lecturas. Implementació de tracking d'estats (pendent / encertada / fallida) sobre les prediccions condicionades.
5. **Pols diari refinat**: si la pestanya ha quedat fora del sidebar, decidir si es manté com a pàgina interior o s'integra del tot a la pàgina del Pulso setmanal.
6. **Datasets Eurostat addicionals**: bd_size redissenyant Estructura Empresarial, bd_hgnace_r per a empreses d'alt creixement provincial.
7. **Refinament dels eixos hardcoded** (yaxis_range fix a Empreses i Ocupació): convertir-los a dinàmics per evitar clipping.
8. **Mòdul d'analítica compartida** (`analytics.py`): centralitzar càlculs de CAGR, YoY i ràtios duplicats inline avui.

---

## 7. Pla d'execució — Fase 3 (tardor)

A vista, sense detallar:

- Definició i implementació de la frontera premium (Mapa C)
- Comunicació activa (primera campanya LinkedIn de l'Observatori)
- Possibles primers leads convertits a clients via consulta o informe a mida
- Avaluació de track record acumulat de prediccions com a peça pública

---

## 8. Decisions explícitament diferides

Coses que NO es decideixen en aquesta sessió i que es treballen més endavant:

- Frontera concreta de monetització (preus, modalitats, gateway)
- Personas 1-4 amb les seves 3 preguntes prioritàries (Tipus 1, 2, 3, 4)
- Tecnologia exacta del motor backend
- Sistema de translation keys robust (avui patró inline a la majoria de pàgines)
- Decisió definitiva sobre `A_Municipis.py` (mantenir local, exposar, eliminar)
- Tractament de subscriptors institucionals vs individuals
- Calendari de campanya post-llançament orgànic

---

*Fitxer generat el 18 de maig de 2026 a partir de la conversa estratègica entre Jordi i Claude. Passa a Claude Code com a instrucció única per a la Fase 1.*

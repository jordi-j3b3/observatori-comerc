# TODO

Llistat de tasques pendents al projecte. No incloure aquí l'estat operatiu del dia a dia (això va a les memòries del repo Claude).

## Multi-idioma per subdomini

**Estat**: opció validada, implementació pendent.

**Objectiu**: quan un usuari entra per `observatorio-comercio.j3b3.com`, el dashboard ha de carregar en castellà; quan entra per `observatori-comerc.j3b3.com` (o `observatori-comerc.streamlit.app`), en català.

**Solució acordada — Opció A (query param al redirect 301):**

1. Configuració al hosting WordPress (htaccess o panel de redirects):
   - `observatorio-comercio.j3b3.com` → `301 https://observatori-comerc.streamlit.app/?lang=es`
   - `observatori-comerc.j3b3.com` → `301 https://observatori-comerc.streamlit.app/?lang=ca`

2. Canvi a `style.py:setup_lang()`: al primer load llegir `st.query_params.get("lang")` i, si val `ca` o `es`, escriure-ho a `st.session_state.lang` abans del selector manual. Esquema indicatiu:
   ```python
   if "lang" not in st.session_state:
       param = st.query_params.get("lang")
       st.session_state.lang = param if param in ("ca", "es") else "ca"
   ```

3. Validació local:
   - `streamlit run app.py` amb `?lang=es` → carregar pestanyes en castellà
   - `streamlit run app.py` amb `?lang=ca` → carregar pestanyes en català
   - Sense param → default `ca`

**Opcionals després del primer release**:
- Netejar el query param de la URL després del primer load amb `st.query_params.clear()` per UX més neta. Risc: si l'usuari recarrega dur perd la decisió i cau al default.
- Sincronitzar amb el selector manual perquè el canvi d'idioma manual actualitzi també el query param.

**Alternatives descartades**:
- Cookie al redirect via JS — cookies cross-domain entre `j3b3.com` i `streamlit.app` no funcionen.
- Dos deploys separats — Streamlit Cloud free plan permet només una app per repo public.
- CNAME directe amb Host header — Streamlit Cloud free no accepta custom domains.
- `document.referrer` — referrer-policy modern el suprimeix sovint, no fiable.

**Implementació**: 5-10 min canvis codi + verificació local + canvi a redirects WP. Commit separat (no barrejar amb feines de dades o UI).

---

## Racionalitzar la navegació

**Origen**: diagnosi UX 2026-06-12.

- Fusionar `7_Europa.py` i `7_Comparativa_Europa.py` (solapament de contingut significatiu).
- Agrupar el sidebar en 4–5 blocs (ex: Pols · Radiografia · Europa · Anàlisi · Sobre nosaltres) amb capçaleres de secció.
- Afegir bloc d'orientació a `0_Inici.py` per a visitants nous ("si véns per primer cop, comença aquí").
- Eliminar el formulari de newsletter duplicat (apareix al sidebar i al footer).
- Completar el micro-copy en castellà que queda hardcoded fora del sistema i18n.

**Estimació**: 1 dia.

---

## Capa comuna de dades (`data/loader.py`)

**Origen**: diagnosi arquitectura 2026-06-12.

Avui cada pàgina llegeix els CSV directament amb `pd.read_csv`. Crear `data/loader.py` amb una funció `load_dataset(name)` que totes les pàgines usin. Beneficis:
- Facilita reutilitzar el codi a l'Observatori Catalunya sense duplicar lògica.
- Punt únic per aplicar @st.cache_resource persistent (en lloc dels @st.cache_data per sessió actuals).
- Preparació per a una futura API de dades (canvi de `source="csv"` a `source="api"` sense tocar cap pàgina).

**Estimació**: mig dia.

---

## Neteja tècnica

**Origen**: diagnosi motor intern i arquitectura 2026-06-12.

- **Dependències mortes**: `streamlit-authenticator`, `bcrypt` i `pyyaml` estan a `requirements.txt` però no s'usen (vestigi d'un pla d'autenticació antic). Treure.
- **`icm.csv` a Parquet**: 13 MB → ~1 MB, càrrega inicial de sessió molt més ràpida. `pandas.read_parquet` és un canvi de dues línies.
- **Centralitzar codis de taula INE/Eurostat**: crear `DATA_SOURCES = {…}` a `data/config.py` amb tots els codis (ara dispersos per `fetchers/ine.py`, `processor.py` i pàgines). Quan INE retiri una taula, el canvi és en un sol lloc.
- **Codis de taula al commit message**: quan es canviï una taula, anotar-ho explícitament al missatge de commit per auditar l'historial.

**Estimació**: mig dia.

---

## Millores CSS per a mòbil (incremental)

**Origen**: diagnosi UX 2026-06-12.

Streamlit posa un sostre dur a la responsivitat. Millores realistes sense canviar de plataforma:
- Augmentar mida de font base a mòbil (`@media (max-width: 768px)`).
- Ocultar elements secundaris (subtítols de secció, notes metodològiques) a pantalles petites.
- Revisar que els gràfics Plotly tinguin `config={"responsive": True}` i alçada mínima adequada.

**Decisió prèvia necessària**: revisar l'analítica Plausible (quan estigui activa) per saber quant tràfic mòbil hi ha realment abans d'invertir-hi temps.

**Estimació**: mig dia, un cop hi hagi dades d'ús.

---

## Logo professional (decisió ajornada post-llançament)

**Estat**: bloquejat fins post 1 juny.

L'intent de logo "Observatorio del Comercio Minorista" del 2026-05-15 es va revertir tant al dashboard com al newsletter. Els assets generats (commit `b573c3b`) queden a `brand/` com a referència, però el producte no els usa ara mateix. La marca és tipogràfica fins que es prengui decisió posterior al llançament. No reactivar res relacionat amb el logo sense decisió explícita.

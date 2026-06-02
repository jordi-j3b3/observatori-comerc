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

## Logo professional (decisió ajornada post-llançament)

**Estat**: bloquejat fins post 1 juny.

L'intent de logo "Observatorio del Comercio Minorista" del 2026-05-15 es va revertir tant al dashboard com al newsletter. Els assets generats (commit `b573c3b`) queden a `brand/` com a referència, però el producte no els usa ara mateix. La marca és tipogràfica fins que es prengui decisió posterior al llançament. No reactivar res relacionat amb el logo sense decisió explícita.

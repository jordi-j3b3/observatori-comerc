-- Esquema DuckDB per al chatbot de retail (base de dades de sèries temporals).
-- Format llarg/tidy: una fila per observació. Veure data/sql/series_registry.py
-- per la definició de cada sèrie i data/sql/migrate.py pel procés de migració.

CREATE TABLE IF NOT EXISTS series_metadata (
    serie_id     VARCHAR PRIMARY KEY,
    name         VARCHAR NOT NULL,
    description  VARCHAR NOT NULL,
    source       VARCHAR NOT NULL,   -- p.ex. "INE T=60096+59787+60110+60111" o "Eurostat ei_bsco_m"
    frequency    VARCHAR NOT NULL,   -- 'daily' | 'monthly' | 'quarterly' | 'annual'
    date_start   DATE,
    date_end     DATE,
    is_critical  BOOLEAN NOT NULL DEFAULT FALSE,
    is_derived   BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE = model propi J3B3, no font externa
    is_public    BOOLEAN NOT NULL DEFAULT TRUE,   -- FALSE = no citable pel chatbot públic
    nota_trencament VARCHAR                       -- trencament de sèrie (p.ex. DIRCE 2023); NULL si no n'hi ha
);

-- Bases creades abans d'afegir nota_trencament (la de CI es regenera sencera).
ALTER TABLE series_metadata ADD COLUMN IF NOT EXISTS nota_trencament VARCHAR;

CREATE TABLE IF NOT EXISTS observations (
    serie_id      VARCHAR NOT NULL REFERENCES series_metadata(serie_id),
    date          DATE NOT NULL,
    frequency     VARCHAR NOT NULL,
    value         DOUBLE,
    unit          VARCHAR,
    dim_1         VARCHAR,           -- significat depen de serie_id (veure series_registry.py)
    dim_2         VARCHAR,
    dim_3         VARCHAR,           -- nomes ocupada per series amb 3 dimensions (p.ex. icm_*)
    source_table  VARCHAR,
    is_critical   BOOLEAN NOT NULL DEFAULT FALSE,
    is_derived    BOOLEAN NOT NULL DEFAULT FALSE,
    is_public     BOOLEAN NOT NULL DEFAULT TRUE,
    geo_codi      VARCHAR,           -- clau canònica de territori (dim_territori); veure data/sql/dimensions.py
    cnae_codi     VARCHAR            -- clau canònica de branca (dim_branca); NULL si la sèrie no és d'una branca
);

ALTER TABLE observations ADD COLUMN IF NOT EXISTS geo_codi VARCHAR;
ALTER TABLE observations ADD COLUMN IF NOT EXISTS cnae_codi VARCHAR;

CREATE INDEX IF NOT EXISTS idx_obs_serie_date ON observations(serie_id, date);

-- Claus comunes per creuar fonts (contingut a data/sql/dimensions.py).
CREATE TABLE IF NOT EXISTS dim_territori (
    geo_codi      VARCHAR PRIMARY KEY,   -- pais:ES, agr:EU27_2020, ccaa:09, prov:08
    nivell        VARCHAR NOT NULL,      -- 'pais' | 'agregat' | 'ccaa' | 'provincia'
    nom           VARCHAR NOT NULL,
    geo_pare      VARCHAR,               -- província -> CCAA -> pais:ES
    codi_ine      VARCHAR,
    codi_eurostat VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_branca (
    cnae_codi     VARCHAR PRIMARY KEY,   -- G, 47, 471, 4711, 47_ALIM...
    nivell        VARCHAR NOT NULL,      -- 'seccio' | 'divisio' | 'grup' | 'classe' | 'agregat_icm'
    nom           VARCHAR NOT NULL,
    cnae_pare     VARCHAR
);

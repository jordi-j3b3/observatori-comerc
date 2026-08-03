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
    is_public    BOOLEAN NOT NULL DEFAULT TRUE    -- FALSE = no citable pel chatbot públic
);

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
    is_public     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_obs_serie_date ON observations(serie_id, date);

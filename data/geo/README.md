# data/geo

## spain_provincies.geojson i spain_provincies_inset.geojson

- Font: IGN/CNIG, servei WFS INSPIRE d'unitats administratives
  (`https://www.ign.es/wfs-inspire/unidades-administrativas`), capa `au:AdministrativeUnit`
  filtrada per `nationalLevelName = Provincia`. Llicència CC BY 4.0: cal citar
  "© Instituto Geográfico Nacional" a la font del mapa.
- Descarregat el 2026-09-27. 53 recintes; es descarta el codi 54 (territoris no associats).
- `codi_prov` = caràcters 5-6 del `nationalCode`; `provincia` i `codi_ccaa` surten de `provincies.csv`.
- Simplificat amb mapshaper: `-simplify 1.5% visvalingam weighted keep-shapes -clean`,
  precisió de 5 decimals. Fronteres compartides sense forats ni solapaments.
- Versió `_inset`: Las Palmas (35) i Santa Cruz de Tenerife (38) traslladades +5,7 de longitud
  i +6,5 de latitud, el mateix desplaçament que `spain_ccaa_inset.geojson`
  (requadre a `CANARIES_INSET_BOUNDS` de `style.py`).

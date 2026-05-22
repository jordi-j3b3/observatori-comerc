# Registro de predicciones — Observatorio del Comercio

Track record verificable de las predicciones del Observatorio. Es un **activo de
credibilidad**: con el tiempo permite publicar "qué predijimos y qué pasó"
(transparencia = autoridad), alimenta un futuro servicio premium de predicción y
sirve de corpus para el asistente IA.

## Regla de oro
Toda predicción se registra **fechada y ANTES de conocer el resultado**, y debe
ser **falsable**: métrica + valor + horizonte concretos. Una predicción que no se
puede puntuar no entra.

## Esquema (`registro.csv`)
| Columna | Qué es |
|---|---|
| `id` | Identificador (P001, P002…) |
| `fecha_prediccion` | Fecha en que se hace la predicción (ISO) |
| `horizonte` | Fecha/periodo en que se resuelve (p.ej. `2026-04` o `2026-12-31`) |
| `metrica` | Qué se predice |
| `ambito` | Territorio / sector / canal |
| `prediccion` | El valor o afirmación predicha |
| `tipo` | `cuantitativa` o `cualitativa` |
| `supuestos` | Supuestos clave (qué tendría que cumplirse) |
| `fuente` | Serie/dato en que se basa |
| `publicada` | Dónde (Pulso Núm.X / interna) |
| `estado` | `pendiente` · `acertada` · `fallada` · `parcial` |
| `valor_real` | Valor observado (se rellena al resolver) |
| `fecha_resolucion` | Cuándo se resolvió |
| `evaluacion` | Nota de puntuación (margen de error, contexto) |

## Cadencia recomendada (volumen rápido)
La frecuencia del registro **no** está atada a la newsletter:
- **Newsletter (Pulso)**: ~1 predicción/semana, pulida y publicada.
- **Ciclo corto (volumen)**: cada mes, antes de la publicación oficial, predecir
  el dato del mes siguiente sobre series frecuentes —Eurostat retail mensual
  (`europa_retail_mensual.csv`), ICM INE, CDMGE diario (`cdmge.csv`)—. Resuelven
  en 4-6 semanas. Con 5-8/mes sobre varias métricas/países → 30-50 resueltas en
  6 meses.
- **Largo plazo**: predicciones sectoriales a 1-3 años (las premium); pocas, lentas
  de verificar, alto valor.

Ejemplos de entradas de ciclo corto (plantilla, NO datos reales):
- `Ventas minoristas YoY · España · abril 2026 · "+3,8% ±0,5"` → resuelve al publicar Eurostat.
- `ICM general YoY · España · abril 2026 · "+4,0%"` → resuelve al publicar INE.

## Puntuación
Cuando llega el dato real: rellenar `valor_real`, `fecha_resolucion`, fijar
`estado` y anotar en `evaluacion` el margen de error. Mantener **las fallidas**:
un historial honesto (con errores) es más creíble que uno seleccionado.

## Doble uso
Cuando exista la herramienta `forecast(metrica, horizonte)` (modelo cuantitativo),
este registro será también su **backtest**: validación del modelo + track record
editorial en un solo sitio.

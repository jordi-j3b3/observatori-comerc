# Marges sobre vendes per branca comercial (`marges_branca.csv`)

## Què és

Marge sobre vendes (%) de les branques del comerç minorista espanyol (agregació
CNAE 47 per grup de dos dígits), anys 2019, 2022, 2023, 2024 i 2025.

## Font

- **PATECO — Informe de la Distribución Comercial en la Comunitat Valenciana.
  Perspectivas 2026/2027 (IDC 26/27)**, taula de la pàgina 31.
- Editat per PATECO (Oficina Comercio y Territorio) per a la Dirección General de
  Comercio, Artesanía y Consumo de la Generalitat Valenciana. Publicat 06/07/2026.
- URL de presentació: https://pateco.org/informe-de-la-distribucion-comercial-en-la-comunitat-valenciana-perspectivas-2026-2027/

## ⚠ Estat de verificació

Els valors actuals provenen d'una **lectura aproximada d'una captura de pantalla**
de la taula de la pàgina 31, no del PDF original. Per això:

- La columna `verificat` val `False` a totes les files.
- Els percentatges són aproximats (marcats amb "~" a la font d'origen) i poden
  tenir errors de lectura.

**Pendent:** obtenir el PDF original (contacte `pateco@camarascv.org`), contrastar
cada valor amb la taula real i, un cop confirmats, canviar `verificat` a `True`.

Fins que no estigui verificat, qualsevol ús en publicacions (dashboard, newsletter)
ha d'anar acompanyat de la cautela "estimació PATECO IDC 26/27, pendent verificació".

## Esquema

| Camp | Tipus | Descripció |
|------|-------|------------|
| `any` | int | Any de referència (2019, 2022, 2023, 2024, 2025) |
| `cnae` | str | Codi de branca (N470–N479, agregació de PATECO sobre CNAE 47) |
| `branca` | str | Nom de la branca |
| `marge_vendes_pct` | float | Marge sobre vendes en % |
| `font` | str | Font de la dada (`PATECO IDC 26/27`) |
| `verificat` | bool | `True` només si s'ha contrastat amb el PDF original |

## Branques

| Codi | Branca |
|------|--------|
| N470 | Supermercats i grans superfícies alimentàries |
| N471 | Especialistes en alimentació, begudes i tabac |
| N472 | Gasolineres |
| N474 | Tecnologia |
| N475 | Equipament de la llar |
| N476 | Productes culturals, esportius i joguines |
| N477 | Moda, calçat, articles personals |
| N478 | Punts de venda i mercadillos |
| N479 | Comerç per internet / sense establiment |

Nota: no hi ha N473 a la taula d'origen. Els anys 2020 i 2021 no consten a la font.

# Revisión 2: limpieza y enriquecimiento ENIGH

## Geografía

- Se pudo hacer el merge geográfico con `ubica_geo = Clave de AGEE + Clave de AGEM`.
- El catálogo original está a nivel localidad: `Mapa = AGEE + AGEM + localidad`.
- Catálogo municipal deduplicado: 2,478 municipios; duplicados por `ubica_geo`: 0; conflictos de nombre/clave: 0.
- Cobertura del merge: 100% en `concentradohogar` y `viviendas` para 2018, 2020, 2022 y 2024; claves sin match: 0.
- Columnas añadidas: `cve_ent`, `entidad`, `cve_mun`, `municipio`.
- No se añadieron localidad, latitud ni longitud porque el catálogo las reporta a nivel localidad.

### Archivos geográficos inspeccionados

| archivo | filas | columnas | nivel_aparente | posibles_llaves |
| --- | --- | --- | --- | --- |
| AGEEML_20268131444460_utf.csv | 360473 | 21 | localidad | Mapa; Clave de AGEE + Clave de AGEM + Clave Localidad |
| AGEEML_20268131456832_utf.txt | 360473 | 21 | localidad | Mapa; Clave de AGEE + Clave de AGEM + Clave Localidad |
| AGEEML_20268131556800.dbf | 360473 | 20 | localidad | Campos truncados de AGEE/AGEM/Mapa |
| AGEEML_2026813173099.xlsx | 360477 | 20 | localidad | Mapa; Clave de AGEE + Clave de AGEM + Clave Localidad |
| AGEEML_20268131742140.csv | 360473 | 21 | localidad | Mapa; Clave de AGEE + Clave de AGEM + Clave Localidad |
| AGEEML_20268131754722.txt | 360473 | 21 | localidad | Mapa; Clave de AGEE + Clave de AGEM + Clave Localidad |
| AGEEML_202681494756.kml | 360473 |  | localidad/geometría | Placemark/Mapa |

### Cobertura del merge

| tabla | anio | registros | ubica_geo_unicos | pct_match | pct_sin_match |
| --- | --- | --- | --- | --- | --- |
| concentradohogar | 2018 | 74647 | 996 | 100.0 | 0.0 |
| concentradohogar | 2020 | 89006 | 1090 | 100.0 | 0.0 |
| concentradohogar | 2022 | 90102 | 1132 | 100.0 | 0.0 |
| concentradohogar | 2024 | 91414 | 1112 | 100.0 | 0.0 |
| viviendas | 2018 | 73405 | 996 | 100.0 | 0.0 |
| viviendas | 2020 | 87754 | 1090 | 100.0 | 0.0 |
| viviendas | 2022 | 88823 | 1132 | 100.0 | 0.0 |
| viviendas | 2024 | 90324 | 1112 | 100.0 | 0.0 |

### Validación de filas

| tabla | filas_antes | filas_despues | diferencia | estado |
| --- | --- | --- | --- | --- |
| concentradohogar | 345169 | 345169 | 0 | OK |
| hogares | 345169 | 345169 | 0 | Sin ubica_geo; no aplica merge geografico |
| ingresos | 1532144 | 1532144 | 0 | Sin ubica_geo; no aplica merge geografico |
| poblacion | 1203231 | 1203231 | 0 | Sin ubica_geo; no aplica merge geografico |
| trabajos | 634140 | 634140 | 0 | Sin ubica_geo; no aplica merge geografico |
| viviendas | 340306 | 340306 | 0 | OK |

### Observaciones por municipio

| tabla | anio | municipios_observados | min | p10 | p25 | mediana | p75 | p90 | max | lt_5 | lt_10 | lt_20 | lt_30 | lt_50 | lt_100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| concentradohogar | 2018 | 996 | 4 | 19.0 | 22.0 | 34.0 | 69.25 | 146.5 | 1384 | 1 | 21 | 124 | 485 | 655 | 823 |
| concentradohogar | 2020 | 1090 | 4 | 18.0 | 21.0 | 39.0 | 70.0 | 171.1 | 1500 | 3 | 21 | 180 | 471 | 699 | 904 |
| concentradohogar | 2022 | 1132 | 3 | 18.0 | 20.0 | 35.5 | 66.25 | 169.5 | 1544 | 3 | 25 | 212 | 534 | 740 | 924 |
| concentradohogar | 2024 | 1112 | 2 | 19.0 | 22.0 | 40.0 | 79.0 | 177.9 | 1689 | 8 | 41 | 126 | 525 | 719 | 904 |
| viviendas | 2018 | 996 | 4 | 19.0 | 22.0 | 34.0 | 68.0 | 144.0 | 1358 | 1 | 22 | 131 | 487 | 662 | 828 |
| viviendas | 2020 | 1090 | 4 | 18.0 | 21.0 | 39.0 | 69.75 | 168.1 | 1477 | 3 | 21 | 192 | 473 | 705 | 905 |
| viviendas | 2022 | 1132 | 3 | 18.0 | 20.0 | 35.0 | 65.0 | 166.6 | 1525 | 3 | 26 | 228 | 534 | 741 | 927 |
| viviendas | 2024 | 1112 | 2 | 19.0 | 22.0 | 40.0 | 79.0 | 176.9 | 1670 | 8 | 42 | 132 | 525 | 720 | 906 |

## Tipos

- Fuente: `docs/enigh_variable_metadata.csv`.
- Variables `C (...)`: texto/código; se corrigieron artefactos `1.0` y se respetó el ancho documentado cuando era estable.
- Variables `N (...)`: numéricas sólo si todos los valores observados eran convertibles; si no, se conservaron como texto y se reportaron.
- Variables `C` con artefacto decimal antes: 208; celdas afectadas: 11,875,227.
- Variables `C` con artefacto decimal después: 0.
- Variables `N` convertidas: 219; variables `N` con valores no numéricos pendientes: 0.
- No quedaron variables `N` con valores no numéricos pendientes.

## Categóricas

- Variables categóricas codificadas detectadas en las tablas actuales: 304.
- Decodificaciones ENIGH aplicadas: 0.
- La documentación versionada describe variables y tipos, pero no trae catálogos código-descripción por año; por eso no se generaron `*_desc` para variables ENIGH.
- Sí se agregaron nombres geográficos (`entidad`, `municipio`) desde el catálogo validado.
- Quedó `inventario_categoricas.csv` con las variables que requieren catálogo/diccionario.

## Archivos generados

| tabla | filas | columnas_antes | columnas_despues | columnas_agregadas |
| --- | --- | --- | --- | --- |
| concentradohogar | 345169 | 125 | 129 | cve_ent, entidad, cve_mun, municipio |
| hogares | 345169 | 125 | 125 |  |
| ingresos | 1532144 | 18 | 18 |  |
| poblacion | 1203231 | 164 | 164 |  |
| trabajos | 634140 | 57 | 57 |  |
| viviendas | 340306 | 61 | 65 | cve_ent, entidad, cve_mun, municipio |

También quedan en `data/interim/revision_2/`: `catalogo_municipal.csv`, `validacion_*`, `observaciones_por_municipio.csv`, `validacion_tipos.csv`, `inventario_categoricas.csv` y `resumen_revision_2.json`.

## Pendientes

- Añadir catálogos oficiales código-descripción por año para decodificar variables categóricas ENIGH.
- Validar si `est_dis` y `upm` se usarán sólo como diseño muestral; por ahora no se interpretan como geografía.
- Para inferencia municipal, revisar la tabla de observaciones por municipio: identificar municipio no garantiza muestra suficiente.
- Añadir catálogos SINCO/SCIAN si se quieren descripciones en `trabajos`.

# Revisión 3: decodificación de variables categóricas ENIGH

## Decodificación de variables categóricas

### Documentación

Se usaron los cuatro PDFs oficiales locales. La ruta real del proyecto es `data/raw/EINGH/`, aunque la instrucción mencionaba `ENIGH`.
| año | pdf |
| --- | --- |
| 2018 | data/raw/EINGH/2018/doc_2018.pdf |
| 2020 | data/raw/EINGH/2020/doc_2020.pdf |
| 2022 | data/raw/EINGH/2022/doc_2022.pdf |
| 2024 | data/raw/EINGH/2024/doc_2024.pdf |

### Catálogo

- Variables con mapping extraído: 431.
- Filas código-etiqueta extraídas: 4,406.
- Fuente principal: fichas de variables de la sección 2.3 (`Valor` -> `Etiqueta`).
- Catálogos externos enlazados cuando la ficha remite explícitamente a ellos: parentesco, residencia, lengua indígena e ingresos.

### Prueba inicial en `poblacion`

La prueba prioritaria incluyó variables disponibles en la base actual: `sexo`, `hablaind`, `etnia`, `alfabetism`, `asis_esc`, `nivelaprob`, `edo_conyug`, `parentesco`, `lenguaind` y `residencia`. No se incluyó discapacidad porque las variables `disc_*` no están en la base derivada común actual.
| anio | tabla | variable | observados | documentados | mapeados | sin_mapping | normalizaciones_para_mapping |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | poblacion | alfabetism | 2 | 2 | 2 | 0 |  |
| 2018 | poblacion | asis_esc | 2 | 2 | 2 | 0 |  |
| 2018 | poblacion | edo_conyug | 6 | 6 | 6 | 0 |  |
| 2018 | poblacion | etnia | 2 | 2 | 2 | 0 |  |
| 2018 | poblacion | hablaind | 2 | 2 | 2 | 0 |  |
| 2018 | poblacion | lenguaind | 84 | 0 | 0 | 84 |  |
| 2018 | poblacion | nivelaprob | 10 | 10 | 10 | 0 |  |
| 2018 | poblacion | parentesco | 34 | 63 | 34 | 0 |  |
| 2018 | poblacion | residencia | 34 | 34 | 34 | 0 |  |
| 2018 | poblacion | sexo | 2 | 2 | 2 | 0 |  |
| 2020 | poblacion | alfabetism | 2 | 2 | 2 | 0 |  |
| 2020 | poblacion | asis_esc | 2 | 2 | 2 | 0 |  |
| 2020 | poblacion | edo_conyug | 6 | 6 | 6 | 0 |  |
| 2020 | poblacion | etnia | 2 | 2 | 2 | 0 |  |
| 2020 | poblacion | hablaind | 2 | 2 | 2 | 0 |  |
| 2020 | poblacion | lenguaind | 89 | 98 | 89 | 0 |  |
| 2020 | poblacion | nivelaprob | 10 | 10 | 10 | 0 |  |
| 2020 | poblacion | parentesco | 33 | 63 | 33 | 0 |  |
| 2020 | poblacion | residencia | 34 | 34 | 34 | 0 |  |
| 2020 | poblacion | sexo | 2 | 2 | 2 | 0 |  |
| 2022 | poblacion | alfabetism | 2 | 2 | 2 | 0 |  |
| 2022 | poblacion | asis_esc | 2 | 2 | 2 | 0 |  |
| 2022 | poblacion | edo_conyug | 6 | 6 | 6 | 0 |  |
| 2022 | poblacion | etnia | 2 | 2 | 2 | 0 |  |
| 2022 | poblacion | hablaind | 2 | 2 | 2 | 0 |  |
| 2022 | poblacion | lenguaind | 90 | 90 | 90 | 0 |  |
| 2022 | poblacion | nivelaprob | 10 | 10 | 10 | 0 |  |
| 2022 | poblacion | parentesco | 40 | 62 | 40 | 0 |  |
| 2022 | poblacion | residencia | 34 | 34 | 34 | 0 |  |
| 2022 | poblacion | sexo | 2 | 2 | 2 | 0 |  |
| 2024 | poblacion | alfabetism | 2 | 2 | 2 | 0 |  |
| 2024 | poblacion | asis_esc | 2 | 2 | 2 | 0 |  |
| 2024 | poblacion | edo_conyug | 8 | 8 | 8 | 0 |  |
| 2024 | poblacion | etnia | 2 | 2 | 2 | 0 |  |
| 2024 | poblacion | hablaind | 2 | 2 | 2 | 0 |  |
| 2024 | poblacion | lenguaind | 85 | 85 | 85 | 0 |  |
| 2024 | poblacion | nivelaprob | 11 | 11 | 11 | 0 | 0->00; 1->01; 2->02; 3->03; 4->04; 5->05; 6->06; 7->07; 8->08; 9->09 |
| 2024 | poblacion | parentesco | 42 | 62 | 42 | 0 |  |
| 2024 | poblacion | residencia | 34 | 34 | 34 | 0 |  |
| 2024 | poblacion | sexo | 2 | 2 | 2 | 0 |  |

### Estabilidad

| estado | variables |
| --- | --- |
| no disponible en todos los años | 395 |
| estable | 207 |
| categorías diferentes | 86 |
- Variables con cambio de codificación detectado: 0.
- Variables con cambio de definición marcadas automáticamente: 0; las diferencias de definición textual se dejan para revisión manual si son sustantivas.

### Decodificación

- Variables decodificadas: 263.
- Columnas `_desc` creadas: 263.
- Códigos observados sin mapping dentro de variables decodificadas: 0.
| tabla | columnas_desc_creadas |
| --- | --- |
| concentradohogar | 5 |
| hogares | 43 |
| ingresos | 7 |
| poblacion | 127 |
| trabajos | 47 |
| viviendas | 34 |

### Problemas

- Códigos observados sin mapping en variables no decodificadas o pendientes: 6,393.
| anio | tabla | variable | sin_mapping | codigos_sin_mapping |
| --- | --- | --- | --- | --- |
| 2018 | hogares | anio_aspir | 37 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 67; 78; 80; 83; 84; 85; 87; 88; 89; 90; 92; 93; 94; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_auto | 51 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 59; 66; 67; 68; 70; 71; 73; 74; 76; 77; 78; 79; 80; 81; 82; 83; 84; 85; 86; 87; 88 |
| 2018 | hogares | anio_bici | 56 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 52; 55; 58; 60; 62; 63; 65; 67; 68; 69; 70; 71; 73; 75; 76; 78; 79; 80; 81; 82; 83 |
| 2018 | hogares | anio_canoa | 32 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 70; 78; 80; 83; 85; 86; 88; 89; 93; 95; 96; 98; 99 |
| 2018 | hogares | anio_carret | 35 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 51; 60; 72; 78; 80; 82; 83; 86; 88; 89; 90; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_compu | 28 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 88; 90; 93; 94; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_dvd | 32 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 80; 85; 87; 88; 90; 92; 93; 94; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_ester | 48 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 58; 60; 63; 65; 70; 73; 75; 78; 79; 80; 81; 82; 83; 84; 85; 86; 87; 88; 89; 90; 91 |
| 2018 | hogares | anio_estuf | 65 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 53; 54; 55; 56; 57; 58; 59; 60; 62; 63; 64; 65; 66; 67; 68; 69; 70; 71; 72; 73; 74 |
| 2018 | hogares | anio_impre | 27 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 86; 88; 90; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_juego | 25 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 88; 91; 95; 96; 97; 98 |
| 2018 | hogares | anio_lavad | 49 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 51; 60; 68; 69; 70; 72; 73; 75; 76; 78; 79; 80; 82; 83; 84; 85; 86; 87; 88; 89; 90 |
| 2018 | hogares | anio_licua | 58 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 52; 53; 58; 60; 62; 63; 65; 67; 68; 70; 71; 72; 73; 74; 75; 76; 77; 78; 79; 80; 81 |
| 2018 | hogares | anio_maqui | 68 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 51; 52; 53; 54; 55; 56; 57; 58; 59; 60; 61; 62; 63; 64; 65; 66; 67; 68; 69; 70; 71 |
| 2018 | hogares | anio_micro | 38 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 77; 80; 83; 84; 85; 86; 87; 88; 89; 90; 91; 92; 93; 94; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_moto | 37 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 62; 68; 70; 77; 78; 80; 84; 86; 88; 90; 91; 93; 94; 95; 96; 97; 98; 99 |
| 2018 | hogares | anio_otro | 25 | 00; 01; 03; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 80; 83; 86; 87; 88; 91; 93; 94; 98 |
| 2018 | hogares | anio_pickup | 48 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 64; 65; 70; 72; 74; 75; 76; 77; 78; 79; 80; 82; 83; 84; 85; 86; 87; 88; 89; 90; 91 |
| 2018 | hogares | anio_planc | 55 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 60; 61; 62; 65; 66; 68; 69; 70; 71; 72; 73; 74; 75; 76; 78; 79; 80; 81; 82; 83; 84 |
| 2018 | hogares | anio_radio | 52 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 58; 60; 63; 64; 65; 68; 70; 72; 73; 75; 76; 78; 79; 80; 81; 82; 83; 84; 85; 86; 87 |
| 2018 | hogares | anio_refri | 55 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 54; 58; 60; 64; 65; 66; 68; 69; 70; 72; 73; 75; 76; 77; 78; 79; 80; 81; 82; 83; 84 |
| 2018 | hogares | anio_tosta | 43 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 70; 72; 73; 78; 80; 81; 82; 83; 84; 85; 86; 87; 88; 89; 90; 91; 92; 93; 94; 95; 96 |
| 2018 | hogares | anio_trici | 32 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 78; 83; 85; 86; 88; 89; 90; 91; 92; 93; 95; 98; 99 |
| 2018 | hogares | anio_tva | 51 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 60; 62; 65; 68; 70; 72; 73; 74; 75; 77; 78; 79; 80; 81; 82; 83; 84; 85; 86; 87; 88 |
| 2018 | hogares | anio_tvd | 26 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 82; 90; 93; 96; 97; 98; 99 |
| 2018 | hogares | anio_van | 46 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 60; 68; 72; 75; 76; 77; 78; 79; 80; 81; 82; 83; 84; 85; 86; 88; 89; 90; 91; 92; 93 |
| 2018 | hogares | anio_venti | 50 | 00; 01; 02; 03; 04; 05; 06; 07; 08; 09; 10; 11; 12; 13; 14; 15; 16; 17; 18; 60; 61; 63; 68; 70; 72; 73; 74; 75; 76; 77; 78; 80; 82; 83; 84; 85; 86; 87; 88; 89 |
| 2018 | hogares | diconsa | 1 | 9 |
| 2018 | hogares | frec_dicon | 3 | 1; 2; 3 |
| 2018 | hogares | num_aspir | 6 | 0; 1; 2; 3; 4; 6 |
| 2018 | hogares | num_compu | 12 | 0; 1; 10; 18; 2; 3; 4; 5; 6; 7; 8; 9 |
| 2018 | hogares | num_dvd | 7 | 0; 1; 10; 2; 3; 4; 5 |
| 2018 | hogares | num_ester | 10 | 0; 1; 10; 15; 2; 3; 4; 5; 7; 8 |
| 2018 | hogares | num_estuf | 12 | 0; 1; 10; 15; 2; 3; 35; 4; 5; 6; 7; 9 |
| 2018 | hogares | num_impre | 8 | 0; 1; 2; 3; 4; 41; 5; 8 |
| 2018 | hogares | num_juego | 11 | 0; 1; 12; 2; 3; 4; 5; 6; 7; 8; 9 |
| 2018 | hogares | num_lavad | 11 | 0; 1; 11; 15; 2; 3; 4; 5; 6; 7; 9 |
| 2018 | hogares | num_licua | 15 | 0; 1; 10; 11; 14; 18; 2; 20; 3; 4; 5; 6; 7; 8; 9 |
| 2018 | hogares | num_maqui | 11 | 0; 1; 10; 11; 2; 3; 4; 42; 5; 6; 7 |
| 2018 | hogares | num_micro | 8 | 0; 1; 2; 20; 3; 4; 7; 8 |

### Variables para revisión manual

| tabla | variable | tipo_conceptual | observacion |
| --- | --- | --- | --- |
| hogares | anio_auto | categórica nominal | Mapping extraído, pero no se decodifica por 213 códigos sin mapping. |
| hogares | anio_van | categórica nominal | Mapping extraído, pero no se decodifica por 193 códigos sin mapping. |
| hogares | anio_pickup | categórica nominal | Mapping extraído, pero no se decodifica por 215 códigos sin mapping. |
| hogares | anio_moto | categórica nominal | Mapping extraído, pero no se decodifica por 152 códigos sin mapping. |
| hogares | anio_bici | categórica nominal | Mapping extraído, pero no se decodifica por 230 códigos sin mapping. |
| hogares | anio_trici | categórica nominal | Mapping extraído, pero no se decodifica por 143 códigos sin mapping. |
| hogares | anio_carret | categórica nominal | Mapping extraído, pero no se decodifica por 140 códigos sin mapping. |
| hogares | anio_canoa | categórica nominal | Mapping extraído, pero no se decodifica por 116 códigos sin mapping. |
| hogares | anio_otro | categórica nominal | Mapping extraído, pero no se decodifica por 106 códigos sin mapping. |
| hogares | num_ester | categórica nominal | Mapping extraído, pero no se decodifica por 40 códigos sin mapping. |
| hogares | anio_ester | categórica nominal | Mapping extraído, pero no se decodifica por 201 códigos sin mapping. |
| hogares | num_radio | categórica nominal | Mapping extraído, pero no se decodifica por 49 códigos sin mapping. |
| hogares | anio_radio | categórica nominal | Mapping extraído, pero no se decodifica por 226 códigos sin mapping. |
| hogares | num_tva | categórica nominal | Mapping extraído, pero no se decodifica por 36 códigos sin mapping. |
| hogares | anio_tva | categórica nominal | Mapping extraído, pero no se decodifica por 210 códigos sin mapping. |
| hogares | num_tvd | categórica nominal | Mapping extraído, pero no se decodifica por 51 códigos sin mapping. |
| hogares | anio_tvd | categórica nominal | Mapping extraído, pero no se decodifica por 139 códigos sin mapping. |
| hogares | num_dvd | categórica nominal | Mapping extraído, pero no se decodifica por 31 códigos sin mapping. |
| hogares | anio_dvd | categórica nominal | Mapping extraído, pero no se decodifica por 146 códigos sin mapping. |
| hogares | num_licua | categórica nominal | Mapping extraído, pero no se decodifica por 47 códigos sin mapping. |
| hogares | anio_licua | categórica nominal | Mapping extraído, pero no se decodifica por 232 códigos sin mapping. |
| hogares | num_tosta | categórica nominal | Mapping extraído, pero no se decodifica por 23 códigos sin mapping. |
| hogares | anio_tosta | categórica nominal | Mapping extraído, pero no se decodifica por 180 códigos sin mapping. |
| hogares | num_micro | categórica nominal | Mapping extraído, pero no se decodifica por 32 códigos sin mapping. |
| hogares | anio_micro | categórica nominal | Mapping extraído, pero no se decodifica por 166 códigos sin mapping. |
| hogares | num_refri | categórica nominal | Mapping extraído, pero no se decodifica por 45 códigos sin mapping. |
| hogares | anio_refri | categórica nominal | Mapping extraído, pero no se decodifica por 234 códigos sin mapping. |
| hogares | num_estuf | categórica nominal | Mapping extraído, pero no se decodifica por 47 códigos sin mapping. |
| hogares | anio_estuf | categórica nominal | Mapping extraído, pero no se decodifica por 263 códigos sin mapping. |
| hogares | num_lavad | categórica nominal | Mapping extraído, pero no se decodifica por 45 códigos sin mapping. |
| hogares | anio_lavad | categórica nominal | Mapping extraído, pero no se decodifica por 210 códigos sin mapping. |
| hogares | num_planc | categórica nominal | Mapping extraído, pero no se decodifica por 52 códigos sin mapping. |
| hogares | anio_planc | categórica nominal | Mapping extraído, pero no se decodifica por 225 códigos sin mapping. |
| hogares | num_maqui | categórica nominal | Mapping extraído, pero no se decodifica por 40 códigos sin mapping. |
| hogares | anio_maqui | categórica nominal | Mapping extraído, pero no se decodifica por 280 códigos sin mapping. |
| hogares | num_venti | categórica nominal | Mapping extraído, pero no se decodifica por 65 códigos sin mapping. |
| hogares | anio_venti | categórica nominal | Mapping extraído, pero no se decodifica por 202 códigos sin mapping. |
| hogares | num_aspir | categórica nominal | Mapping extraído, pero no se decodifica por 27 códigos sin mapping. |
| hogares | anio_aspir | categórica nominal | Mapping extraído, pero no se decodifica por 156 códigos sin mapping. |
| hogares | num_compu | categórica nominal | Mapping extraído, pero no se decodifica por 42 códigos sin mapping. |
| hogares | anio_compu | categórica nominal | Mapping extraído, pero no se decodifica por 125 códigos sin mapping. |
| hogares | num_impre | categórica nominal | Mapping extraído, pero no se decodifica por 30 códigos sin mapping. |
| hogares | anio_impre | categórica nominal | Mapping extraído, pero no se decodifica por 113 códigos sin mapping. |
| hogares | num_juego | categórica nominal | Mapping extraído, pero no se decodifica por 46 códigos sin mapping. |
| hogares | anio_juego | categórica nominal | Mapping extraído, pero no se decodifica por 119 códigos sin mapping. |
| hogares | diconsa | categórica nominal | Mapping extraído, pero no se decodifica por 3 códigos sin mapping. |
| hogares | frec_dicon | categórica ordinal | Mapping extraído, pero no se decodifica por 3 códigos sin mapping. |
| poblacion | madre_id | identificador | Mapping extraído, pero no se decodifica por 67 códigos sin mapping. |
| poblacion | padre_id | identificador | Mapping extraído, pero no se decodifica por 64 códigos sin mapping. |
| poblacion | lenguaind | código de catálogo | Mapping extraído, pero no se decodifica por 84 códigos sin mapping. |

## Archivos generados

- `data/interim/revision_3/catalogo_categoricas_enigh.csv`
- `data/interim/revision_3/matriz_estabilidad_categoricas.csv`
- `data/interim/revision_3/validacion_mappings_categoricas.csv`
- `data/interim/revision_3/inventario_variables_revision_3.csv`
- `data/interim/revision_3/variables_revision_manual.csv`
- `data/interim/revision_3/*_decodificada_2018_2024.csv.gz`

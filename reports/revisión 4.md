# Revisión 4: relaciones, marts y dashboard exploratorio

## Reparación de `02_limpieza_enriquecimiento`

Se ejecutó `notebooks/02_limpieza_enriquecimiento.ipynb` desde un entorno limpio y se encontraron dos fallas:

| Celda | Error | Causa | Corrección |
| --- | --- | --- | --- |
| 3 | `FileNotFoundError` al leer `validacion_archivos_geografia.csv` | La celda 2 usaba `ROOT = Path('..').resolve()`, que sólo funciona si el kernel arranca desde `notebooks/`. Desde la raíz del proyecto apuntaba a la carpeta padre. | Se agregó detección robusta de raíz buscando `README.md` y `data/`. |
| 7 | `KeyError: ['storage_2024_antes', 'storage_2024_despues'] not in index` | `validacion_tipos.csv` ya usa columnas `artefactos_decimal_*`. | Se actualizó la selección de columnas para usar la nomenclatura real. |

Validación posterior:

- `02_limpieza_enriquecimiento.ipynb` corre completo con kernel limpio.
- La revisión 2 conserva 100% de cobertura geográfica en `concentradohogar` y `viviendas`.
- No hay multiplicación de filas en merges de limpieza.
- Los artefactos decimales en variables categóricas quedan en 0 después de la limpieza.
- La nota metodológica final del notebook 02 se actualizó para aclarar que la decodificación `*_desc` corresponde al notebook 03.

## Relaciones entre tablas

Se creó `notebooks/04_relaciones_entre_bases.ipynb`.

La ruta local real de los datos crudos es `data/raw/EINGH/`. Los PDFs oficiales locales usados como referencia son:

- `data/raw/EINGH/2018/doc_2018.pdf`
- `data/raw/EINGH/2020/doc_2020.pdf`
- `data/raw/EINGH/2022/doc_2022.pdf`
- `data/raw/EINGH/2024/doc_2024.pdf`

Mapa relacional validado:

| Tabla | Nivel | Llave | Relación principal |
| --- | --- | --- | --- |
| `viviendas` | vivienda | `folioviv` | 1:N hogares |
| `hogares` | hogar | `folioviv + foliohog` | N:1 vivienda; 1:N población; 1:1 concentradohogar |
| `concentradohogar` | hogar agregado INEGI | `folioviv + foliohog` | 1:1 hogares |
| `poblacion` | persona | `folioviv + foliohog + numren` | N:1 hogar; 1:N trabajos; 1:N ingresos |
| `trabajos` | trabajo de una persona | `folioviv + foliohog + numren + id_trabajo` | N:1 persona |
| `ingresos` | registro persona-clave de ingreso | `folioviv + foliohog + numren + clave` | N:1 persona |

Resultados empíricos:

- Las llaves propuestas tienen 0 duplicados en 2018, 2020, 2022 y 2024.
- Todas las unidades hijas tienen padre en las relaciones validadas.
- `hogares -> poblacion`: máximo observado de 25 personas por hogar.
- `poblacion -> trabajos`: máximo observado de 2 trabajos por persona.
- `poblacion -> ingresos`: máximo observado de 14 registros de ingreso por persona.

Riesgo principal: no hacer merges directos `poblacion.merge(trabajos).merge(ingresos)`, porque trabajos e ingresos son 1:N respecto a persona y pueden multiplicar observaciones.

## Ingresos

`ingresos.csv` se interpreta como tabla persona-clave de ingreso:

- llave: `folioviv + foliohog + numren + clave`;
- `clave`: concepto de ingreso;
- `mes_1` a `mes_6`: meses reportados;
- `ing_1` a `ing_6`: importes mensuales;
- `ing_tri`: ingreso trimestral.

Para esta etapa se construyeron agregados a nivel persona:

- `registros_ingreso`;
- `claves_ingreso_distintas`;
- `ingreso_persona_total_registros_tri`;
- `ingreso_persona_laboral_negocio_tri`;
- `ingreso_persona_transferencias_tri`;
- `ingreso_persona_rentas_propiedad_tri`;
- `ingreso_persona_financiero_capital_tri`;
- `ingreso_persona_no_clasificado_tri`.

Estos agregados se documentan como derivados de `ingresos.csv`. Para targets de hogar se priorizan las variables oficiales de `concentradohogar`, como `ing_cor` e `ingtrab`, porque no todas las sumas desde `ingresos.csv` reproducen automáticamente los agregados oficiales del hogar.

## Trabajos

`trabajos.csv` se interpreta como tabla de trabajos de una persona:

- llave: `folioviv + foliohog + numren + id_trabajo`;
- máximo observado: 2 trabajos por persona;
- se toma el trabajo con menor `id_trabajo` como trabajo principal para conservar características principales;
- se agregan a persona `n_trabajos`, `horas_trabajos_total` y `horas_trabajo_principal`.

No se construyó una variable definitiva de formalidad. Se conservaron insumos interpretables como pago, contrato, subordinación, independencia, sueldo y tamaño de empresa para análisis posterior.

## Construcción de `mart_persona`

Se creó `notebooks/05_bases_analiticas.ipynb` y el archivo:

`data/interim/revision_4/mart_persona_2018_2024.csv.gz`

Unidad: una persona por año.

Llave:

`anio + folioviv + foliohog + numren`

Resultado:

- filas: 1,203,231;
- columnas: 140;
- duplicados de llave final: 0.

Auditoría de joins:

| Paso | Filas antes | Filas después | % match | Tipo |
| --- | ---: | ---: | ---: | --- |
| Agregar ingresos a nivel persona | 1,203,231 | 1,203,231 | 66.0118 | opcional |
| Agregar trabajos a nivel persona | 1,203,231 | 1,203,231 | 48.0447 | opcional |
| Agregar hogar/concentrado/geografía | 1,203,231 | 1,203,231 | 100.0000 | esperado |
| Agregar variables de hogares | 1,203,231 | 1,203,231 | 100.0000 | esperado |
| Agregar vivienda | 1,203,231 | 1,203,231 | 100.0000 | esperado |

La geografía se incorpora desde hogar/vivienda mediante las relaciones validadas. No se agrega localidad, latitud ni longitud. En esta actualización también se conserva `region_banxico`, construida desde `cve_ent` con la clasificación de cuatro regiones revisada en el estado del arte.

## Construcción de `mart_hogar`

Archivo creado:

`data/interim/revision_4/mart_hogar_2018_2024.csv.gz`

Unidad: un hogar por año.

Llave:

`anio + folioviv + foliohog`

Resultado:

- filas: 345,169;
- columnas: 92;
- duplicados de llave final: 0.

Auditoría de joins:

| Paso | Filas antes | Filas después | % match | Tipo |
| --- | ---: | ---: | ---: | --- |
| Agregar variables de hogares | 345,169 | 345,169 | 100.0000 | esperado |
| Agregar vivienda | 345,169 | 345,169 | 100.0000 | esperado |
| Agregar agregados de población | 345,169 | 345,169 | 100.0000 | esperado |
| Agregar ingresos derivados de `ingresos.csv` | 345,169 | 345,169 | 99.9276 | opcional |

Comparaciones contra variables oficiales:

| Comparación | Filas | % exacto | Máxima diferencia absoluta |
| --- | ---: | ---: | ---: |
| `tot_integ` vs conteo en `poblacion` | 345,169 | 99.8734 | 6 |
| `edad_jefe` vs jefe identificado en `poblacion` | 345,169 | 100.0000 | 0 |

Cuando exista una variable oficial de INEGI y una reconstrucción propia, se conserva la variable oficial como referencia principal y la reconstrucción se usa como auditoría o insumo secundario.

## Factor de expansión y diseño muestral

La metadata muestra que `factor`, `est_dis` y `upm` están disponibles longitudinalmente en `concentradohogar` y `viviendas`. En otras tablas aparecen directamente desde 2022.

Decisión de esta etapa:

- `mart_hogar` conserva `factor_hogar`, `est_dis` y `upm` desde `concentradohogar`;
- ambos marts exponen `factor` como alias operativo de `factor_hogar` para resúmenes descriptivos ponderados;
- `mart_persona` hereda estas columnas desde el hogar para mantener consistencia 2018-2024;
- todavía no se implementa inferencia con diseño muestral complejo;
- el dashboard distingue análisis muestral y deja ponderación como pendiente metodológico.

## Auditoría geográfica y análisis regional

Esta actualización responde a la necesidad de revisar si las bases analíticas ya estaban alineadas con las variables geográficas y de estratificación documentadas. Se tomó como referencia `reports/estado_del_arte_geografia_ingresos_ENIGH.md`, especialmente la clasificación Banxico de cuatro regiones: Norte, Centro Norte, Centro y Sur.

Cambios mínimos en los marts:

| Mart | Filas antes | Filas después | Columnas antes | Columnas después | Duplicados llave | Faltantes `region_banxico` | Faltantes `factor` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mart_persona` | 1,203,231 | 1,203,231 | 138 | 140 | 0 | 0 | 0 |
| `mart_hogar` | 345,169 | 345,169 | 90 | 92 | 0 | 0 | 0 |

Variables incorporadas o normalizadas:

- `region_banxico`, construida desde `cve_ent`;
- `factor`, como alias documentado de `factor_hogar`;
- `est_socio_desc`, normalizada por código 1-4 para corregir una etiqueta dañada en 2022 sin cambiar `est_socio`.

Validaciones:

- las 32 entidades aparecen exactamente una vez en el mapa entidad-región;
- no hay faltantes en `cve_ent`, `entidad`, `cve_mun`, `municipio`, `tam_loc_desc`, `est_socio_desc`, `region_banxico`, `factor`, `est_dis` ni `upm`;
- no cambió la granularidad de `mart_persona` ni de `mart_hogar`;
- no se modificó `data/raw/`.

Se creó `notebooks/07_analisis_regional_ingresos.ipynb`. El target principal es `ingreso_persona_laboral_negocio_tri`; las tablas centrales usan la submuestra con ingreso laboral positivo para evitar medianas en cero al incluir población sin ingreso laboral. El ingreso corriente per cápita del hogar se conserva como contraste territorial. La libreta ejecutó sus 17 celdas de código sin error desde un proceso limpio de Python.

Hallazgos descriptivos preliminares:

- la muestra central tiene 574,462 personas con ingreso laboral positivo, 47.7% del mart persona;
- la mediana trimestral de ingreso laboral es mayor en Norte ($22,131) y menor en Sur ($11,739);
- el mismo orden territorial aparece en ingreso corriente per cápita del hogar: Norte tiene la mediana más alta ($16,713) y Sur la más baja ($10,477);
- el tamaño de localidad muestra un gradiente urbano-rural: localidades de 100,000 o más habitantes tienen mediana de $22,500 frente a $13,011 en localidades menores de 2,500 habitantes;
- el estrato socioeconómico separa fuertemente la distribución: Alto registra $33,359 y Bajo $10,125;
- la educación presenta un gradiente amplio: licenciatura o ingeniería alcanza $36,685 de mediana y maestría $50,967, frente a $11,331 en primaria y $6,722 en ningún nivel aprobado;
- la brecha por sexo aparece sin controles: hombres $19,392 y mujeres $12,984;
- tener contrato se asocia con una mediana mayor ($28,124) que no tenerlo ($14,478);
- entre 2018 y 2024 la mediana sube en todas las regiones, con el mayor aumento absoluto en Norte.

Estos hallazgos no son causales y todavía no separan composición educativa, edad, sexo, ocupación, estructura del hogar ni diferencias nominales/reales entre años.

## Calidad de las bases analíticas

Se creó `notebooks/08_calidad_bases_analiticas.ipynb` para auditar las bases antes de avanzar a desigualdad territorial, Gini, deflactación o modelos. La libreta usa la terminología visible:

- `mart_persona`: base analítica de personas;
- `mart_hogar`: base analítica de hogares;
- data mart: nombre técnico de una tabla preparada para análisis a una granularidad específica.

La libreta no reconstruye bases, no modifica datos crudos, no imputa y no elimina filas. Reutiliza los artefactos actuales de `data/interim/revision_4`.

Acumulación temporal:

| Base analítica | 2018 | 2020 | 2022 | 2024 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Personas | 269,206 | 315,743 | 309,684 | 308,598 | 1,203,231 |
| Hogares | 74,647 | 89,006 | 90,102 | 91,414 | 345,169 |

Estas bases concatenan levantamientos independientes. No son un panel: una persona u hogar de 2018 y una persona u hogar de 2024 son observaciones independientes.

Faltantes principales:

- geografía, estratos y diseño muestral están completos en variables prioritarias: `region_banxico`, `entidad`, `tam_loc_desc`, `est_socio_desc`, `factor`, `est_dis` y `upm`;
- los targets monetarios principales no tienen faltantes: `ingreso_persona_laboral_negocio_tri`, `ingreso_persona_total_registros_tri`, `ing_cor_hogar_pc_oficial_tri`, `ing_cor_hogar_oficial_tri` e `ing_cor_pc_oficial_tri`;
- `edo_conyug_desc` tiene 233,128 faltantes, 19.38% de la base de personas, explicados por menores de 12 años; dentro de personas de 12 años o más el faltante es 0%;
- `nivelaprob_desc` tiene 47,209 faltantes, 3.92%, concentrados en edades 0-5; desde 6 años prácticamente desaparecen;
- `nivel_desc` tiene 869,288 faltantes, 72.25%, porque describe nivel educativo actual y solo aplica cuando la persona asiste a la escuela;
- variables laborales como `subor_principal_desc` y `tam_emp_principal_desc` faltan en 51.96% de la base completa, pero dentro de personas con trabajo reportado están completas;
- `contrato_principal_desc` falta en 65.56% de la base completa, pero está completa dentro de trabajadores que reciben pago;
- `personas_con_registros_ingreso` tenía 250 faltantes en la base de hogares, 0.07%, por el merge opcional de ingresos agregados a hogar; al validar contra `mart_persona`, todos esos hogares tenían integrantes pero 0 personas con registros en `ingresos.csv`, por lo que el contador se corrigió a 0.

Clasificación provisional de mecanismos:

| Grupo | Variables | Interpretación |
| --- | --- | --- |
| Sin faltantes | edad, sexo, ingresos principales, geografía, estratos, factor, `est_dis`, `upm`, variables centrales de hogar | Usar directamente, documentando universo y ponderación cuando aplique. |
| Estructural / no aplica | estado conyugal en menores de 12, educación aprobada en edades 0-5, nivel educativo actual fuera de asistencia escolar, variables laborales fuera de trabajadores o fuera de su ruta de cuestionario | Restringir universo antes de analizar. |
| Compatible con MCAR | Ninguna variable central se clasifica así como conclusión fuerte | No afirmar MCAR sin supuestos adicionales. |
| Compatible con MAR | Ninguna variable central se clasifica así después de aplicar universos | Las asociaciones brutas con edad o trabajo reflejan principalmente saltos lógicos. |
| Posible MNAR | Ninguna variable central identificada | MNAR no puede demostrarse con datos observados; requeriría supuestos adicionales. |
| Cambio metodológico | No se detecta desaparición de variables prioritarias entre 2018-2024 | Mantener vigilancia si se incorporan variables nuevas. |
| Problema potencial de datos | Sin variables centrales pendientes después de la corrección acotada de `asis_esc_desc` y `personas_con_registros_ingreso` | Mantener vigilancia si estas variables se vuelven centrales. |

Análisis de ceros:

- `ingreso_persona_laboral_negocio_tri` no tiene faltantes ni negativos; tiene 628,769 ceros y 574,462 positivos;
- por año, personas con ingreso laboral positivo: 2018 = 127,846; 2020 = 148,082; 2022 = 149,569; 2024 = 148,965;
- por año, personas con ingreso laboral cero: 2018 = 141,360; 2020 = 167,661; 2022 = 160,115; 2024 = 159,633;
- 94.71% de las personas sin trabajo reportado tiene ingreso laboral cero; esto respalda tratar el cero como legítimo/estructural, no como faltante;
- `registros_ingreso = 0` representa ausencia de registros en `ingresos.csv`;
- `n_trabajos = 0` y `horas_trabajo_principal = 0` representan ausencia de trabajo reportado;
- 36 hogares tienen ingreso corriente oficial cero; se conservan, pero conviene revisarlos si se vuelven sustantivos;
- ceros en códigos o identificadores, como `trabajo_mp`, `grado`, `gradoaprob`, `est_dis` o `upm`, no se interpretan como cantidades.

Poblaciones analíticas propuestas:

| Universo | 2018 | 2020 | 2022 | 2024 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base completa de personas | 269,206 | 315,743 | 309,684 | 308,598 | 1,203,231 |
| Personas con trabajo reportado | 127,638 | 149,387 | 150,682 | 150,382 | 578,089 |
| Personas con ingreso laboral positivo | 127,846 | 148,082 | 149,569 | 148,965 | 574,462 |
| Hogares | 74,647 | 89,006 | 90,102 | 91,414 | 345,169 |

Decisión metodológica provisional: para ingreso laboral conviene separar dos análisis posteriores. Primero, probabilidad de tener ingreso laboral positivo. Segundo, monto del ingreso condicionado a `ingreso_persona_laboral_negocio_tri > 0`. Todavía no se construyen esos modelos.

Variables que requieren decisión antes de usarse:

- `asis_esc_desc`: las etiquetas dañadas para "No" en 2020/2022 se corrigieron por código oficial `asis_esc` (`1 = Sí`, `2 = No`); el faltante restante corresponde a edades 0-5;
- `personas_con_registros_ingreso`: los 250 `NaN` se validaron contra `mart_persona` y se rellenaron con 0 porque representan ausencia de registros individuales en `ingresos.csv`, no pérdida de llave;
- `nivel_desc`: no mide escolaridad general, sino nivel educativo actual de quienes asisten a la escuela;
- `contrato_principal_desc`: debe usarse en el universo de trabajadores que reciben pago, no en toda la población.

La libreta ejecutó sus 14 celdas de código sin error desde un proceso limpio de Python.

## Dashboard exploratorio

Se creó `notebooks/06_dashboard_exploratorio.ipynb`.

Permite explorar:

- nivel de análisis: persona u hogar;
- variable objetivo de ingreso;
- año;
- entidad;
- municipio;
- tamaño de localidad;
- estrato socioeconómico;
- variable explicativa;
- distribución de ingresos;
- relación X vs ingreso;
- evolución temporal;
- comparación geográfica.

Validaciones realizadas:

- el notebook carga `mart_persona` y `mart_hogar`;
- el dashboard inicializa con `ipywidgets`;
- cambiar nivel persona/hogar funciona;
- cambiar año funciona;
- cambiar variable objetivo funciona;
- cambiar variable explicativa funciona;
- cambiar vista funciona;
- filtro y comparación por municipio funcionan con mínimo de observaciones;
- no se detectaron errores con filtros que devuelven pocas observaciones durante la simulación de interacciones.

Se instalaron en el runtime de Codex las dependencias necesarias para validar el dashboard: `matplotlib`, `seaborn` e `ipywidgets`.

## Archivos principales generados

Notebooks:

- `notebooks/04_relaciones_entre_bases.ipynb`
- `notebooks/05_bases_analiticas.ipynb`
- `notebooks/06_dashboard_exploratorio.ipynb`
- `notebooks/07_analisis_regional_ingresos.ipynb`
- `notebooks/08_calidad_bases_analiticas.ipynb`

Datos intermedios:

- `data/interim/revision_4/mapa_relacional.csv`
- `data/interim/revision_4/validacion_cardinalidades.csv`
- `data/interim/revision_4/validacion_relaciones.csv`
- `data/interim/revision_4/ingresos_agregados_persona.csv.gz`
- `data/interim/revision_4/trabajos_agregados_persona.csv.gz`
- `data/interim/revision_4/poblacion_agregada_hogar.csv.gz`
- `data/interim/revision_4/mart_persona_2018_2024.csv.gz`
- `data/interim/revision_4/mart_hogar_2018_2024.csv.gz`
- `data/interim/revision_4/validacion_mart_persona.csv`
- `data/interim/revision_4/validacion_mart_hogar.csv`
- `data/interim/revision_4/comparacion_variables_hogar.csv`
- `data/interim/revision_4/diccionario_marts.csv`
- `data/interim/revision_4/resumen_revision_4_marts.json`

## Pendientes

- Revisar con más detalle las claves de ingreso si se quiere convertir los agregados persona en definiciones finales publicables.
- Definir tratamiento de ingresos nominales vs reales antes de comparación temporal sustantiva.
- Definir formalmente cómo se reportará el diseño muestral si los resultados pasan de descriptivos a inferenciales.
- Mantener documentada la corrección de `asis_esc_desc` si asistencia escolar se usa como variable explicativa.
- Mantener documentada la decisión de tratar como 0 los 250 casos previos de `personas_con_registros_ingreso`.
- Revisar las diferencias entre `tot_integ` oficial y conteo reconstruido desde `poblacion`.
- No interpretar municipios como representativos sin revisar diseño muestral y tamaños de muestra.
- Construir variables de formalidad sólo después de revisar definiciones sustantivas y documentación.

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
- columnas: 138;
- duplicados de llave final: 0.

Auditoría de joins:

| Paso | Filas antes | Filas después | % match | Tipo |
| --- | ---: | ---: | ---: | --- |
| Agregar ingresos a nivel persona | 1,203,231 | 1,203,231 | 66.0118 | opcional |
| Agregar trabajos a nivel persona | 1,203,231 | 1,203,231 | 48.0447 | opcional |
| Agregar hogar/concentrado/geografía | 1,203,231 | 1,203,231 | 100.0000 | esperado |
| Agregar variables de hogares | 1,203,231 | 1,203,231 | 100.0000 | esperado |
| Agregar vivienda | 1,203,231 | 1,203,231 | 100.0000 | esperado |

La geografía se incorpora desde hogar/vivienda mediante las relaciones validadas. No se agrega localidad, latitud ni longitud.

## Construcción de `mart_hogar`

Archivo creado:

`data/interim/revision_4/mart_hogar_2018_2024.csv.gz`

Unidad: un hogar por año.

Llave:

`anio + folioviv + foliohog`

Resultado:

- filas: 345,169;
- columnas: 90;
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
- `mart_persona` hereda estas columnas desde el hogar para mantener consistencia 2018-2024;
- todavía no se implementa inferencia con diseño muestral complejo;
- el dashboard distingue análisis muestral y deja ponderación como pendiente metodológico.

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
- Decidir formalmente si el análisis usará ponderadores y cómo se reportará el diseño muestral.
- Revisar las diferencias entre `tot_integ` oficial y conteo reconstruido desde `poblacion`.
- No interpretar municipios como representativos sin revisar diseño muestral y tamaños de muestra.
- Construir variables de formalidad sólo después de revisar definiciones sustantivas y documentación.

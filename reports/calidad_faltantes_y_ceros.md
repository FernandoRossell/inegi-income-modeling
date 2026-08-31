# Calidad, faltantes y ceros

**Proyecto:** ENIGH, ingresos y territorio en México  
**Base:** `data/interim/revision_4/`  
**Notebook base:** `notebooks/08_calidad_bases_analiticas.ipynb`

Este documento técnico resume el criterio usado para interpretar faltantes y ceros en las bases analíticas de personas y hogares. No reemplaza el notebook: deja por escrito las decisiones que deben sostener el análisis posterior.

## 1. Taxonomía de faltantes

Se usa la siguiente clasificación práctica:

| Tipo | Interpretación | Acción |
| --- | --- | --- |
| Sin faltantes | La variable está completa en su universo relevante. | Usar directamente. |
| Estructural / no aplica | El faltante se explica por edad, condición laboral o salto de cuestionario. | Restringir universo antes de interpretar. |
| Compatible con MCAR | No se detecta patrón observable relevante. | No afirmar sin evidencia adicional. |
| Compatible con MAR | El faltante se asocia con variables observadas. | Documentar controles y universo. |
| Posible MNAR | La ausencia puede depender del valor no observado. | No se concluye con datos observados solamente. |
| Cambio metodológico | La variable cambia entre años o deja de estar disponible. | Documentar comparabilidad antes de usar. |
| Problema potencial de datos | Etiquetas, merges o codificación requieren revisión. | Validar antes de usar o corregir de forma acotada. |

En esta etapa no se clasifica ninguna variable central como MCAR, MAR o MNAR de forma definitiva. Primero se revisan universos de aplicación y lógica de cuestionario.

## 2. Indicadores de missing

Para cada variable prioritaria se calcula:

- `missing_n`: número de observaciones faltantes;
- `missing_pct`: porcentaje de faltantes;
- `cero_n`: número de ceros cuando la variable es numérica;
- `cero_pct`: porcentaje de ceros;
- `n_unicos`: número de valores únicos observados;
- universo aplicable definido antes de interpretar.

También se usa un indicador conceptual:

```text
M_X = 1 si X falta
M_X = 0 si X está observada
```

Este indicador permite revisar si la ausencia de una variable se concentra por edad, sexo, año, región, tamaño de localidad, estrato socioeconómico o condición laboral.

## 3. Chi-cuadrada y Cramér's V

Para variables categóricas se construyen tablas de contingencia entre `M_X` y controles observados. A partir de esas tablas se calcula una estadística tipo chi-cuadrada descriptiva:

```text
chi2 = sum((observado - esperado)^2 / esperado)
```

Después se resume la magnitud con Cramér's V:

```text
V = sqrt(chi2 / (n * (min(r, c) - 1)))
```

No se usan p-values en esta etapa. Con bases grandes, diferencias pequeñas pueden salir significativas sin ser sustantivamente importantes para la tesina.

## 4. Diferencia estandarizada de medias

Para controles numéricos se compara el promedio del control entre observaciones con y sin faltante:

```text
SMD = (media_missing - media_observado) / desviación_estándar_combinada
```

Se usa como medida de magnitud descriptiva. En notebook 08, las asociaciones fuertes con edad o trabajo reportado confirman principalmente saltos lógicos del cuestionario.

## 5. Flujo diagnóstico

El flujo aplicado es:

1. Revisar faltantes brutos.
2. Definir universo aplicable.
3. Recalcular faltantes dentro del universo.
4. Separar missing de ceros.
5. Validar si el cero es cantidad, código o ausencia estructural.
6. Revisar asociaciones de `M_X` con controles observados.
7. Decidir si se usa, restringe, corrige o deja pendiente.
8. Documentar la decisión antes de avanzar.

## 6. Resultados actuales de faltantes

Variables completas o tratables directamente:

- geografía: `region_banxico`, `entidad`, `cve_ent`, `tam_loc_desc`, `est_socio_desc`;
- diseño: `factor`, `factor_hogar`, `est_dis`, `upm`;
- ingresos principales: `ingreso_persona_laboral_negocio_tri`, `ingreso_persona_total_registros_tri`, `ing_cor_hogar_oficial_tri`, `ing_cor_pc_oficial_tri`;
- estructura básica del hogar: `tot_integ`, `ocupados`, `sexo_jefe_desc`, `nivelaprob_jefe_desc`.

Faltantes estructurales importantes:

| Variable | Faltantes | % | Interpretación |
| --- | ---: | ---: | --- |
| `edo_conyug_desc` | 233,128 | 19.38 | Falta en edades 0-11; en 12+ queda completo. |
| `nivelaprob_desc` | 47,209 | 3.92 | Concentrado en edades 0-5; desde 6+ prácticamente desaparece. |
| `nivel_desc` | 869,288 | 72.25 | Solo aplica a quienes asisten a la escuela; no mide escolaridad general. |
| `segsoc_desc` | 233,650 | 19.42 | Explicado casi totalmente por edades 0-11; revisar residual si se vuelve central. |
| `subor_principal_desc` | 625,142 | 51.96 | Falta para no trabajadores; completo entre trabajadores. |
| `tam_emp_principal_desc` | 625,142 | 51.96 | Falta para no trabajadores; completo entre trabajadores. |
| `contrato_principal_desc` | 788,877 | 65.56 | Completo dentro de trabajadores que reciben pago. |

## 7. Análisis de ceros

Los ceros se tratan por separado de los faltantes.

### Ingreso laboral individual

`ingreso_persona_laboral_negocio_tri`:

- faltantes: 0;
- negativos: 0;
- ceros: 628,769;
- positivos: 574,462.

Por año:

| Año | Cero | Positivo |
| --- | ---: | ---: |
| 2018 | 141,360 | 127,846 |
| 2020 | 167,661 | 148,082 |
| 2022 | 160,115 | 149,569 |
| 2024 | 159,633 | 148,965 |

El 94.71% de las personas sin trabajo reportado tiene ingreso laboral cero. Esto respalda tratar el cero como legítimo o estructural, no como faltante.

### Hogares

- `ing_cor_hogar_oficial_tri`: 36 ceros, sin faltantes ni negativos.
- `ing_cor_pc_oficial_tri`: 36 ceros, sin faltantes ni negativos.
- `ingtrab_hogar_oficial_tri`: 40,139 ceros, compatible con hogares sin ingreso laboral.
- `personas_con_registros_ingreso`: 250 `NaN` previos ya corregidos a 0 después de validación.

### Ceros que no son cantidades

Variables como `trabajo_mp`, `grado`, `gradoaprob`, `est_dis` o `upm` pueden tener código 0 o valores numéricos que no representan montos ni ausencia económica. No se interpretan como ceros sustantivos.

## 8. Conteos de ingreso laboral

La población analítica de ingreso laboral queda:

| Universo | 2018 | 2020 | 2022 | 2024 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Personas con trabajo reportado | 127,638 | 149,387 | 150,682 | 150,382 | 578,089 |
| Personas con ingreso laboral positivo | 127,846 | 148,082 | 149,569 | 148,965 | 574,462 |
| Trabajo reportado e ingreso laboral positivo | 541,418 total | | | | |

Decisión: para análisis posteriores separar probabilidad de ingreso laboral positivo y monto condicionado a ingreso laboral positivo.

## 9. Corrección de `asis_esc_desc`

Problema detectado:

- 2020 y 2022 tenían etiquetas dañadas para la categoría "No".
- Los códigos observados eran consistentes: `1` para asistencia y `2` para no asistencia.
- `nivel_desc` estaba observado cuando `asis_esc_desc` era "Sí" y faltante cuando era "No", lo que respaldó la lectura del código.

Acción:

```text
asis_esc = 1 -> Sí
asis_esc = 2 -> No
```

Resultado:

- los códigos 1 y 2 quedaron con etiquetas limpias;
- el faltante restante de `asis_esc_desc` corresponde a edades 0-5;
- asistencia escolar puede usarse en el universo de 6 años o más.

## 10. Corrección de `personas_con_registros_ingreso`

Problema detectado:

- 250 hogares tenían `NaN` en `personas_con_registros_ingreso`;
- distribución: 2018 = 50, 2020 = 80, 2022 = 58, 2024 = 62;
- el origen era el merge opcional de ingresos agregados a hogar.

Validación:

- los 250 hogares sí tenían integrantes en `mart_persona`;
- al reagrupar personas por `anio + folioviv + foliohog`, el contador reconstruido fue 0 en los 250 casos;
- la suma reconstruida de ingreso total individual y de ingreso laboral/negocio fue 0;
- en hogares no faltantes, el contador original coincidió con el cálculo reconstruido.

Decisión:

```text
NaN en personas_con_registros_ingreso -> 0
```

Interpretación: el cero significa ausencia de registros individuales en `ingresos.csv`, no pérdida de llave hogar-persona. Esta decisión no altera las variables oficiales de ingreso del hogar en `concentradohogar`.

## 11. Decisión sobre imputación

No se imputa en esta etapa.

Razones:

- los targets monetarios principales están completos;
- muchos faltantes se explican por universo de aplicación;
- variables laborales deben analizarse en subpoblaciones correctas;
- imputar antes de definir modelos podría introducir supuestos innecesarios;
- el objetivo inmediato es EDA interpretable y reproducible.

## 12. Pendientes de calidad

Pendientes reales después de la corrección acotada:

- revisar residual de `segsoc_desc` en personas de 12 años o más si seguridad social se vuelve variable central;
- revisar diferencias entre `tot_integ` oficial y conteo reconstruido desde `poblacion`;
- definir formalmente tratamiento de los 36 hogares con ingreso corriente oficial cero si afectan análisis de desigualdad;
- documentar universos cada vez que se usen variables laborales;
- no usar `nivel_desc` como escolaridad general;
- no usar `contrato_principal_desc` fuera de trabajadores que reciben pago.

## 13. Regla de uso para siguientes notebooks

Antes de usar una variable con faltantes:

```text
variable -> universo aplicable -> faltante dentro del universo -> decisión documentada
```

Antes de convertir un faltante a cero:

```text
faltante -> verificar llave/origen -> verificar universo -> verificar conteo reconstruido -> documentar
```

Esta regla queda como principio para las siguientes etapas del proyecto.

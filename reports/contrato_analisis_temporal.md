# Contrato para el analisis temporal de determinantes

**Estado:** infraestructura de notebook preparada; ejecucion manual y validacion de resultados pendientes. ENIGH 2018, 2020, 2022 y 2024 son cuatro cortes transversales independientes, no un panel.

## Fuente y unidad

- Una fila de la base analitica equivale a una persona adulta con `ingreso_persona_laboral_negocio_tri > 0`.
- El unico mart de microdatos del notebook 12 es `data/interim/revision_4/mart_persona_2018_2024.csv.gz` (`mart_persona_revision_4`). No se lee ni se une `mart_hogar`.
- Llave de persona: `anio`, `folioviv`, `foliohog`, `numren`. Los tres primeros campos identifican hogar para particiones sin fuga; ninguna llave es predictor.
- La misma definicion nominal trimestral del ingreso laboral/de negocio se mantiene como target en los cuatro años. Se conservan target nominal, `log1p` nominal, target real aproximado de 2024 y `log1p` real.
- `factor`, `est_dis` y `upm` se conservan para un futuro tratamiento del diseño muestral; no entran como predictores.

## Ajuste monetario

El notebook 12 lee la tabla versionada `docs/deflactores_precios_2024.csv` como referencia de precios. Usa un factor anual comun por edicion: 2018 = 1.3504040596; 2020 = 1.2602040463; 2022 = 1.1051180464; 2024 = 1. El target real se calcula como `target_nominal * deflactor_2024` y el logaritmico como `log1p(target_real)`.

Estos factores fueron calibrados en un intento metodologico anterior contra el benchmark INEGI del ingreso corriente promedio trimestral **del hogar**. Son una aproximacion anual aplicada ahora al ingreso laboral **de personas**; no son deflactores mensuales ni por componente. No se usan microdatos de hogares en esta preparacion. Antes de interpretar tendencias reales, revisar y aprobar la adecuacion de esta conversion para el target individual. Los marts `revision_4` permanecen intactos.

## Variables y comparabilidad

Conjunto comun **propuesto**, sujeto a auditoria manual: `edad`, `sexo_desc`, `hablaind_desc`, `n_trabajos`, `horas_trabajos_total`, `segsoc_desc`, `subor_principal_desc`, `contrato_principal_desc`, `region_banxico`, `tam_loc_desc`.

`nivelaprob_desc` y `parentesco_desc` se conservan en las bases anuales y en la especificacion exploratoria de cada año, pero no entran en el conjunto comun hasta documentar equivalencias de codigos y etiquetas. La referencia `No` de `segsoc_desc` se reconstruye con una regla exacta y visible para la etiqueta contaminada del codigo 2 en 2020/2022; el notebook comprueba ese codigo y conserva `segsoc_desc_original`. Esta regla y cualquier categoria inesperada deben revisarse al ejecutar. `tam_emp_principal_desc` y `est_socio_desc` siguen pendientes. `tot_integ`, `menores`, `p65mas`, `sexo_jefe_desc` y `educa_jefe_desc` son contexto del hogar y quedan fuera del modelo individual principal.

`significativas_2024` es un antecedente exploratorio por variable original de la corrida local de 2024. No constituye filtro para otro año ni reemplaza el modelo completo comun. El futuro trabajo contrastara un modelo completo armonizado con exploraciones elegidas independientemente por año.

## Bases por año

| Año | Salida individual esperada | Estado de esta tarea |
| --- | --- | --- |
| 2018 | `data/processed/determinantes_2018/base_interpretable_personas_2018.csv.gz` | Ejecucion manual pendiente |
| 2020 | `data/processed/determinantes_2020/base_interpretable_personas_2020.csv.gz` | Ejecucion manual y revision de `segsoc_desc` pendientes |
| 2022 | `data/processed/determinantes_2022/base_interpretable_personas_2022.csv.gz` | Ejecucion manual y revision de `segsoc_desc` pendientes |
| 2024 | `data/processed/determinantes_2024/base_interpretable_personas_2024.csv.gz` | Reejecucion manual del codigo temporal pendiente; archivos locales anteriores no se atribuyen a esta tarea |

Cada salida contiene año, llave personal y de hogar, targets nominal y real, predictores, `region_banxico`, `entidad`, `cve_ent`, metadata y variables del diseño. La tabla de comparabilidad del notebook 12 tendra una fila por variable con disponibilidad por año, tipos, categorias y referencias; las tablas anexas conservaran faltantes, valores unicos y frecuencias. El mismo nombre de columna solo permite una comparabilidad provisional hasta revisar metadatos y codigos ENIGH.

## Alternativas geograficas

- Regional: `region_banxico`, referencia propuesta `Centro`.
- Estatal: `entidad`, con `cve_ent` para verificar codigos; la referencia estatal se decidira despues de comprobar cobertura y consistencia de las 32 entidades.
- Las dos geografias se modelaran por separado. Un coeficiente geografico desplaza el intercepto respecto de su referencia; diferencias de pendientes requieren interacciones posteriores.

## Salida exigida al futuro notebook de modelos

Por cada año y especificacion geografica: OLS completo en nivel monetario y en `log1p` del target real, seleccion exploratoria independiente, coeficientes, errores estandar, intervalos, p-values, indicador de significancia, metricas train/validacion, diagnosticos, VIF/GVIF, PCA y arbol diagnostico. En el roadmap, "modelo nominal" se refiere a la escala lineal del ingreso; para comparar años, sus unidades seran pesos aproximados de 2024. El preprocesamiento se ajustara solo con entrenamiento y la particion se agrupara por hogar. No se implementa nada de ello en esta tarea.

La tabla normalizada de coeficientes debera contener:

| Columna | Significado |
| --- | --- |
| `anio`, `escala_target`, `especificacion` | Corte, escala y modelo completo/exploratorio/geografico |
| `variable`, `categoria`, `referencia` | Predictor original y contraste categorico |
| `coeficiente`, `error_estandar` | Estimacion e incertidumbre; indicar tipo de EE en metadata |
| `intervalo_inferior`, `intervalo_superior`, `p_value`, `significativa` | Inferencia condicionada a la especificacion |
| `n_personas`, `n_hogares` | Tamaño del universo modelado |

No se calcula esta tabla ahora. Comparar coeficientes entre años requerira igual definicion, escala y codificacion; una categoria ausente no se rellenara con columnas constantes artificiales. La inferencia formal con diseño muestral y la correccion por pruebas multiples siguen pendientes.

## Roadmap

1. Auditar y armonizar variables 2018-2024, incluida la conversion monetaria anual y las categorias pendientes.
2. Ejecutar manualmente el notebook 12 para cada año y revisar las cuatro bases.
3. Estimar modelos nominales y logaritmicos completos separados por año.
4. Realizar seleccion exploratoria independiente por año.
5. Comparar años con la especificacion completa comun.
6. Estimar modelos geograficos separados para regiones Banxico y entidades federativas.
7. Plantear un modelo pooled con efectos de año.
8. Evaluar interacciones `año × predictor`.
9. Aplicar pruebas Wald de cambio temporal y revisar pruebas multiples.
10. Incorporar y validar el diseño muestral.
11. Interpretar cambios entre cortes transversales, sin tratarlos como panel.

Permanecen pendientes la ejecucion manual, revision de categorias y referencias estatales, modelos por año, pooled, interacciones, Wald, correccion por pruebas multiples e inferencia de diseño.

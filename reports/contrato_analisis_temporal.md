# Contrato para el analisis temporal de determinantes

**Estado (24-09-2026):** las cuatro bases individuales exportadas por Fernando estan disponibles y su esquema se inspecciono sin ejecutar notebooks. El notebook 14 de comparacion temporal esta preparado, sin outputs ni modelos ejecutados por Codex. ENIGH 2018, 2020, 2022 y 2024 son cortes transversales independientes, no un panel.

## Fuente y unidad

- Una fila de la base analitica equivale a una persona adulta con `ingreso_persona_laboral_negocio_tri > 0`.
- El notebook 12 parte de `data/interim/revision_4/mart_persona_2018_2024.csv.gz` (`mart_persona_revision_4`). El notebook 14 lee exclusivamente las cuatro bases individuales ya exportadas por el 12. No se lee ni se une `mart_hogar`.
- Llave de persona: `anio`, `folioviv`, `foliohog`, `numren`. Los tres primeros campos identifican hogar para particiones sin fuga; ninguna llave es predictor.
- La misma definicion nominal trimestral del ingreso laboral/de negocio se mantiene como target en los cuatro años. Se conservan target nominal, `log1p` nominal, target real aproximado de 2024 y `log1p` real.
- `factor`, `est_dis` y `upm` se conservan para un futuro tratamiento del diseño muestral; no entran como predictores.

## Ajuste monetario

El notebook 12 lee la tabla versionada `docs/deflactores_precios_2024.csv` como referencia de precios. Usa un factor anual comun por edicion: 2018 = 1.3504040596; 2020 = 1.2602040463; 2022 = 1.1051180464; 2024 = 1. El target real se calcula como `target_nominal * deflactor_2024` y el logaritmico como `log1p(target_real)`.

Estos factores fueron calibrados en un intento metodologico anterior contra el benchmark INEGI del ingreso corriente promedio trimestral **del hogar**. Son una aproximacion anual aplicada ahora al ingreso laboral **de personas**; no son deflactores mensuales ni por componente. No se usan microdatos de hogares en esta preparacion. Antes de interpretar tendencias reales, revisar y aprobar la adecuacion de esta conversion para el target individual. Los marts `revision_4` permanecen intactos.

## Variables y comparabilidad

Conjunto comun **propuesto**, sujeto a auditoria manual: `edad`, `sexo_desc`, `hablaind_desc`, `n_trabajos`, `horas_trabajos_total`, `segsoc_desc`, `subor_principal_desc`, `contrato_principal_desc`, `region_banxico`, `tam_loc_desc`.

La inspeccion de las bases confirma que el nucleo conserva las mismas categorias observadas en los cuatro años, tras etiquetar los faltantes estructurales de `subor_principal_desc` y `contrato_principal_desc` como en el notebook 13. Los archivos conservan `segsoc_desc_original`: en 2020/2022 se verifica la correccion exacta a `No`, y el 14 detiene la ejecucion ante etiquetas inesperadas. Los codigos originales de escolaridad y seguridad social no fueron exportados en estas bases; el 14 verifica las parejas de etiquetas de seguridad social y se apoya en la validacion por codigo que ya hizo el 12, sin atribuirse una nueva validacion del codigo.

`nivelaprob_desc` sigue fuera: 2018/2020/2022 tienen diez etiquetas observadas y 2024 once; aparecen `Especialidad` y cambios de nombres como `Profesional` frente a `Licenciatura o Ingenieria (profesional)`. No se inventan equivalencias; la especificacion ampliada se detiene sin frenar el nucleo. `parentesco_desc` es sensibilidad futura por categorias distintas. `tam_emp_principal_desc` y `est_socio_desc` siguen pendientes por dependencia laboral y nivel conceptual. `tot_integ`, `menores`, `p65mas`, `sexo_jefe_desc` y `educa_jefe_desc` son contexto del hogar y quedan fuera del modelo individual principal.

`significativas_2024` es un antecedente exploratorio por variable original de la corrida local de 2024. No constituye filtro para otro año ni reemplaza el modelo completo comun. El notebook 14 reconstruira una tabla descriptiva por termino de su propia especificacion, sin trasladar una seleccion del 13 ni repetir PCA o arbol.

## Bases por año

| Año | Archivo individual | Estado de esta tarea |
| --- | --- | --- |
| 2018 | `data/processed/determinantes_2018/base_interpretable_personas_2018.csv.gz` | Disponible; esquema inspeccionado, 120054 personas |
| 2020 | `data/processed/determinantes_2020/base_interpretable_personas_2020.csv.gz` | Disponible; esquema y `segsoc_desc` inspeccionados, 139394 personas |
| 2022 | `data/processed/determinantes_2022/base_interpretable_personas_2022.csv.gz` | Disponible; esquema y `segsoc_desc` inspeccionados, 141514 personas |
| 2024 | `data/processed/determinantes_2024/base_interpretable_personas_2024.csv.gz` | Disponible; esquema inspeccionado, 141579 personas |

Cada salida contiene año, llave personal y de hogar, targets nominal y real, predictores, `region_banxico`, `entidad`, `cve_ent`, metadata y variables del diseño. El notebook 14 prepara una fila de comparabilidad por variable con disponibilidad, faltantes, categorias, frecuencias minimas y referencia por año. El mismo nombre de columna solo permite comparabilidad provisional hasta revisar metadatos y codigos ENIGH.

## Alternativas geograficas

- Regional: `region_banxico`, referencia propuesta `Centro`.
- Estatal: `entidad`, referencia explicita `Ciudad de Mexico` por su papel de capital federal, no por ser un extremo estadistico. La inspeccion confirmo su presencia, las mismas 32 etiquetas y relacion uno-a-uno con `cve_ent` en los cuatro archivos; el notebook valida de nuevo antes de ajustar.
- Las dos geografias se modelaran por separado. Un coeficiente geografico desplaza el intercepto respecto de su referencia; diferencias de pendientes requieren interacciones posteriores.

## Notebook 14 preparado, pendiente de ejecucion manual

`notebooks/14_comparacion_temporal_determinantes.ipynb` contiene auditoria de las cuatro bases, especificacion comun, OLS anuales de `log1p` real aproximado como analisis principal y de niveles nominales como secundario, errores convencionales/HC3/agrupados por hogar, pruebas conjuntas, figuras, pooled con 2024 como referencia, interacciones por bloques y Wald. La especificacion estatal sustituye a la regional; la WLS anual y pooled es solo sensibilidad cuando `factor`, `est_dis` y `upm` son validos. La prediccion con holdout agrupado por hogar queda como evaluacion opcional posterior, separada de la inferencia con muestra completa. No se repiten PCA/arbol ni se filtra por `significativas_2024`.

La tabla normalizada de coeficientes se producira al ejecutar y debera contener:

| Columna | Significado |
| --- | --- |
| `anio`, `escala_target`, `especificacion`, `estimador`, `tipo_covarianza` | Corte, escala, modelo y tratamiento de incertidumbre |
| `variable`, `categoria`, `referencia` | Predictor original y contraste categorico |
| `coeficiente`, `error_estandar` | Estimacion e incertidumbre; indicar tipo de EE en metadata |
| `intervalo_inferior`, `intervalo_superior`, `p_value`, `significativa_descriptiva` | Inferencia condicionada a la especificacion |
| `n_personas`, `n_hogares` | Tamaño del universo modelado |

No se calcula esta tabla ahora. Las salidas previstas estan en `outputs/comparacion_temporal_determinantes/`: auditoria, comparabilidad, referencias, metricas/coeficientes/pruebas anuales, coeficientes pooled, efectos totales, Wald, geografia, figuras y manifest. Comparar coeficientes entre años requiere igual definicion, escala y codificacion; una categoria ausente detiene el modelo, no se rellena con una constante artificial. Diferencia de p-values no es prueba de cambio; la prueba apropiada es la interaccion. La inferencia formal con diseño muestral y la correccion por pruebas multiples siguen pendientes. El factor anual real, calibrado con ingreso del hogar, no esta aprobado para concluir tendencias del ingreso laboral individual.

## Roadmap

1. Bases de 2018, 2020, 2022 y 2024 disponibles; inspeccion de esquema y categorias realizada sin ejecutar notebooks en esta tarea.
2. Notebook 14 preparado para auditoria, modelos anuales comparables, sensibilidad estatal, pooled, interacciones, Wald y exportaciones; ejecucion manual pendiente.
3. Revisar outputs de la ejecucion, especialmente categorias, matrices, IC y pruebas, antes de escribir conclusiones temporales.
4. Resolver homologacion de escolaridad y posible sensibilidad de parentesco; no incluirlas por significancia 2024.
5. Aprobar o reemplazar el ajuste monetario anual para ingreso laboral individual y definir correccion por pruebas multiples.
6. Evaluar predictivamente en un flujo separado, si aporta a la pregunta; considerar diseño muestral formal y heterogeneidad territorial de pendientes en etapas posteriores.

Permanecen pendientes la ejecucion y revision manual del 14, la aprobacion del factor real, la ampliacion educativa y la inferencia formal del diseño. Ningun resultado de modelado temporal se atribuye a esta preparacion.

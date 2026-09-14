# Preparación de base para determinantes 2024

Esta etapa prepara una base analítica de personas para estudiar asociaciones entre características personales, laborales, del hogar y territoriales e ingreso. No entrena modelos, no crea particiones y no reactiva las etapas históricas de homologación monetaria o JKn.

Método de ejecución registrado: notebook_12_parametrizado_proceso_python_limpio_sin_nbclient.

## Alcance aprobado

- Unidad: persona.
- Año: 2024.
- Universo: edad >= 18 e ingreso laboral/de negocio positivo.
- Cobertura: todas las regiones Banxico.
- Target: `ingreso_persona_laboral_negocio_tri`.
- Montos: nominales trimestrales.
- Fuente: `data/interim/revision_4/mart_persona_2018_2024.csv.gz`.

Los resultados futuros con esta base corresponderán a adultos con ingreso laboral/de negocio positivo. No explican directamente quién obtiene ingreso positivo ni corrigen sesgos de selección.

## Flujo del universo

| paso | criterio | filas_antes | excluidas | filas_despues | hogares_unicos_despues |
| --- | --- | --- | --- | --- | --- |
| anio_2024 | anio == 2024 | 1,203,231 | 894,633 | 308,598 | 91,414 |
| edad_valida | edad valida y finita | 308,598 | 0 | 308,598 | 91,414 |
| adultos | edad >= 18 | 308,598 | 89,770 | 218,828 | 91,389 |
| target_valido | target valido y finito | 218,828 | 0 | 218,828 | 91,389 |
| target_positivo | target > 0 | 218,828 | 77,249 | 141,579 | 80,872 |

## Target

Resumen no ponderado:

| n | media | mediana | desv_std | p01 | p05 | p25 | p50 | p75 | p95 | p99 | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 141,579 | 31,171.87 | 24,245.89 | 64,171.35 | 295.08 | 1,516.30 | 12,433.44 | 24,245.89 | 38,225.27 | 79,239.13 | 154,663.03 | 17,021,739.12 |

Contraste descriptivo ponderado con `factor`:

| n_muestral | suma_factor | media_ponderada | mediana_ponderada | p25 | p75 | p95 | p99 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 141,579 | 61,105,085.00 | 33,133.23 | 25,081.95 | 13,694.12 | 39,836.04 | 87,540.96 | 169,472.55 |

La cola derecha es muy larga: el máximo supera ampliamente P99. Por eso se crea `log_ingreso_persona_laboral_negocio_tri` solo como diagnóstico visual, sin sustituir el target activo.

## Predictores iniciales

| variable | tipo | papel | transformacion | referencia_o_tratamiento |
| --- | --- | --- | --- | --- |
| edad | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| n_trabajos | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| horas_trabajos_total | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| tot_integ | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| menores | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| p65mas | continua | predictor inicial | sin escalar; estandarizada solo en matriz diagnostica |  |
| sexo_desc | categorica | predictor inicial | one-hot k-1 | Hombre |
| nivelaprob_desc | categorica | predictor inicial | one-hot k-1 | Ninguno |
| region_banxico | categorica | predictor inicial | one-hot k-1 | Centro |
| tam_loc_desc | categorica | predictor inicial | one-hot k-1 | Localidades con 100 000 y más habitantes |
| parentesco_desc | categorica | predictor inicial | one-hot k-1 | Jefe(a) |
| hablaind_desc | categorica | predictor inicial | one-hot k-1 | No |
| segsoc_desc | categorica | predictor inicial | one-hot k-1 | No |
| subor_principal_desc | categorica | predictor inicial | one-hot k-1 | No |
| contrato_principal_desc | categorica | predictor inicial | one-hot k-1 | No |
| sexo_jefe_desc | categorica | predictor inicial | one-hot k-1 | Hombre |
| educa_jefe_desc | categorica | predictor inicial | one-hot k-1 | Sin instrucción |

`est_socio` se conserva como diagnóstico contextual y queda fuera de la matriz inicial. `entidad` también se conserva como metadata diagnóstica porque `region_banxico` ya está determinada por entidad. `tam_emp_principal_desc` queda pendiente: su categoría estructural "sin trabajo principal reportado" duplicaba exactamente una dummy de subordinación, por lo que se conserva en la base interpretable pero no entra a `X` inicial.

## Faltantes

| variable | faltantes | faltantes_pct | decision |
| --- | --- | --- | --- |
| edad | 0 | 0.0000 | usar sin imputacion |
| n_trabajos | 0 | 0.0000 | usar sin imputacion |
| horas_trabajos_total | 0 | 0.0000 | usar sin imputacion |
| tot_integ | 0 | 0.0000 | usar sin imputacion |
| menores | 0 | 0.0000 | usar sin imputacion |
| p65mas | 0 | 0.0000 | usar sin imputacion |
| sexo_desc | 0 | 0.0000 | usar sin imputacion |
| nivelaprob_desc | 0 | 0.0000 | usar sin imputacion |
| region_banxico | 0 | 0.0000 | usar sin imputacion |
| tam_loc_desc | 0 | 0.0000 | usar sin imputacion |
| parentesco_desc | 0 | 0.0000 | usar sin imputacion |
| hablaind_desc | 0 | 0.0000 | usar sin imputacion |
| segsoc_desc | 0 | 0.0000 | usar sin imputacion |
| subor_principal_desc | 5,205 | 0.0368 | faltante estructural convertido solo en categoria de matriz; original se conserva |
| contrato_principal_desc | 37,124 | 0.2622 | faltante estructural convertido solo en categoria de matriz; original se conserva |
| sexo_jefe_desc | 0 | 0.0000 | usar sin imputacion |
| educa_jefe_desc | 0 | 0.0000 | usar sin imputacion |

No se aplicó complete-case global. Las continuas seleccionadas no tienen faltantes. En variables laborales del trabajo principal, los faltantes se tratan como categorías estructurales solo cuando el origen permite distinguir ausencia de trabajo principal o contrato no documentado.

## One-hot encoding

Se usa k-1 por variable, pensando en un intercepto futuro. Las referencias no se eligieron por conveniencia estadística sino por interpretación:

| variable | referencia | n_referencia |
| --- | --- | --- |
| sexo_desc | Hombre | 82,304 |
| nivelaprob_desc | Ninguno | 4,145 |
| region_banxico | Centro | 35,628 |
| tam_loc_desc | Localidades con 100 000 y más habitantes | 54,544 |
| parentesco_desc | Jefe(a) | 68,035 |
| hablaind_desc | No | 130,582 |
| segsoc_desc | No | 58,278 |
| subor_principal_desc | No | 31,445 |
| contrato_principal_desc | No | 52,696 |
| sexo_jefe_desc | Hombre | 100,575 |
| educa_jefe_desc | Sin instrucción | 7,153 |

Los indicadores son 0/1 y el intercepto no se guarda como predictor.

## Asociaciones exploratorias

Continuas, Spearman con ingreso original:

| variable | n_valido | spearman_ingreso_original |
| --- | --- | --- |
| horas_trabajos_total | 141,579 | 0.3434 |
| p65mas | 141,579 | -0.1394 |
| n_trabajos | 141,579 | 0.0853 |
| tot_integ | 141,579 | -0.0534 |
| edad | 141,579 | -0.0446 |
| menores | 141,579 | -0.0076 |

Dummies, punto biserial con ingreso original:

| dummy | variable_original | categoria_vs_resto | frecuencia_1 | punto_biserial_ingreso_original |
| --- | --- | --- | --- | --- |
| contrato_principal_desc__si | contrato_principal_desc | Sí | 51,759 | 0.1553 |
| segsoc_desc__si | segsoc_desc | Sí | 83,301 | 0.1375 |
| educa_jefe_desc__profesional_completa | educa_jefe_desc | Profesional completa | 15,615 | 0.1330 |
| nivelaprob_desc__licenciatura_o_ingenieria_profesional | nivelaprob_desc | Licenciatura o Ingeniería (profesional) | 27,905 | 0.1247 |
| educa_jefe_desc__posgrado | educa_jefe_desc | Posgrado | 3,037 | 0.0999 |
| nivelaprob_desc__maestria | nivelaprob_desc | Maestría | 2,243 | 0.0905 |
| tam_loc_desc__localidades_con_menos_de_2_500_habitantes | tam_loc_desc | Localidades con menos de 2 500 habitantes | 53,072 | -0.0897 |
| sexo_desc__mujer | sexo_desc | Mujer | 59,275 | -0.0860 |
| nivelaprob_desc__primaria | nivelaprob_desc | Primaria | 28,255 | -0.0832 |
| region_banxico__norte | region_banxico | Norte | 32,110 | 0.0691 |
| educa_jefe_desc__primaria_incompleta | educa_jefe_desc | Primaria incompleta | 18,167 | -0.0687 |
| subor_principal_desc__no_aplica_sin_trabajo_principal_reportado | subor_principal_desc | No aplica: sin trabajo principal reportado | 5,205 | -0.0687 |

Estas correlaciones son exploratorias, no ponderadas, sin p-values y no son criterio automático de descarte. Una dummy compara su categoría contra todas las demás, no únicamente contra la referencia.

## Dependencia entre predictores

| filas | columnas_X | columnas_con_intercepto | rango_con_intercepto | deficiencia_rango | estado |
| --- | --- | --- | --- | --- | --- |
| 141,579 | 67 | 68 | 68 | 0 | rango_completo |

VIF más altos:

| columna | vif | estado |
| --- | --- | --- |
| contrato_principal_desc__no_aplica_sin_contrato_principal_documentado | 36.50 | ok |
| subor_principal_desc__si | 36.39 | ok |
| nivelaprob_desc__secundaria | 12.60 | ok |
| nivelaprob_desc__preparatoria_o_bachillerato | 11.84 | ok |
| nivelaprob_desc__licenciatura_o_ingenieria_profesional | 11.78 | ok |
| nivelaprob_desc__primaria | 9.16 | ok |
| educa_jefe_desc__secundaria_completa | 7.90 | ok |
| educa_jefe_desc__preparatoria_completa | 5.80 | ok |
| educa_jefe_desc__profesional_completa | 5.53 | ok |
| educa_jefe_desc__primaria_completa | 5.17 | ok |
| educa_jefe_desc__primaria_incompleta | 4.26 | ok |
| educa_jefe_desc__posgrado | 2.77 | ok |

`VIF_j = 1 / (1 - R_j^2)`. En dummies individuales depende de la codificación k-1 y no equivale a importancia causal ni a un diagnóstico global de la variable categórica original.

## Figuras

- `reports/figures/preparacion_determinantes/2024/target_hist_original_log.png`: El panel original limita el eje x a P99 solo para lectura visual; no recorta datos.
- `reports/figures/preparacion_determinantes/2024/target_log_por_region.png`: Boxplot descriptivo no ponderado; outliers ocultos solo en la figura para legibilidad.
- `reports/figures/preparacion_determinantes/2024/target_log_por_sexo.png`: Boxplot descriptivo no ponderado; outliers ocultos solo en la figura para legibilidad.
- `reports/figures/preparacion_determinantes/2024/target_log_por_escolaridad.png`: Boxplot descriptivo no ponderado; outliers ocultos solo en la figura para legibilidad.

## Archivos locales

Las bases y matrices se escribieron en `data/processed/determinantes_2024/` y quedan fuera de Git por contener microdatos/identificadores. Las tablas agregadas pequeñas se escribieron en `reports/tables/preparacion_determinantes/2024/`.

Manifest: `reports/tables/preparacion_determinantes/2024/manifest_preparacion_determinantes.json`.

## Parametrización anual

Para cambiar el año debe modificarse `ANIO_ANALISIS` al inicio del notebook. Los años válidos son (2018, 2020, 2022, 2024) y la edad mínima configurada es 18. Esta ejecución generó bases, matrices, tablas y figuras solo para 2024; los años (2018, 2020, 2022) quedan inspeccionados en esquema cuando el notebook se ejecuta con compatibilidad activa.

Estado vigente posterior a la auditoría: la implementación está ejecutada para 2024, pero la revisión metodológica sigue pendiente antes de modelar. La auditoría diagnóstica queda documentada en `reports/auditoria_preparacion_determinantes.md` y sus tablas agregadas en `reports/tables/auditoria_preparacion_determinantes/`.

Las salidas por año quedan separadas:

- Base y matrices: `data/processed/determinantes_<anio>/`.
- Tablas: `reports/tables/preparacion_determinantes/<anio>/`.
- Figuras: `reports/figures/preparacion_determinantes/<anio>/`.

Resumen de compatibilidad inspeccionada:

| anio | estado | filas_anio | filas_universo | hogares_unicos | referencias_ohe_faltantes | categorias_nuevas_vs_anio_base | categorias_ausentes_vs_anio_base |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | compatibilidad inspeccionada; ejecución pendiente | 269,206 | 120,054 | 67,807 |  | 5 | 9 |
| 2020 | revisar antes de generar base | 315,743 | 139,394 | 79,365 | segsoc_desc | 7 | 10 |
| 2022 | revisar antes de generar base | 309,684 | 141,514 | 80,217 | segsoc_desc | 5 | 8 |
| 2024 | ejecutado, validado y auditado | 308,598 | 141,579 | 80,872 |  | 0 | 0 |

La auditoría muestra que en 2020/2022 el código original `2` de `segsoc` sí aparece en el universo de determinantes, pero la etiqueta fue extraída como texto contaminado (`No ... Descripción ...` invertido), por lo que la referencia exacta `No` no se encuentra. La corrección propuesta `código 2 -> No` no fue aplicada y requiere aprobación antes de generar bases de esos años.

La comparabilidad de coeficientes entre años no queda resuelta por esta preparación: dependerá de una especificación común posterior y de preprocesadores ajustados dentro de entrenamiento cuando se defina una evaluación predictiva.

## Limitaciones y pendientes

- La base es nominal trimestral y corresponde solo a 2024.
- No se usa `deflactor_2024`, columnas `_real_2024` ni JKn.
- No se preparó train/test ni validación cruzada.
- Una futura partición debe considerar hogares para evitar compartir información familiar entre conjuntos.
- La estrategia inferencial de los modelos todavía está pendiente.
- No existe identificación causal aprobada; las lecturas son asociativas.
- Antes de cambiar `X`, deben aprobarse: mapeo de `segsoc_desc` 2020/2022, tratamiento de faltantes laborales del trabajo principal, decisión sobre `tam_emp_principal_desc`, tratamiento de la cola derecha y uso de variables de jefatura como contexto del hogar.

# Diseño muestral formal e inferencia descriptiva

Etapa 11 del proyecto ENIGH. Esta revisión incorpora inferencia descriptiva aproximada con el diseño observable en los marts: ponderador `factor`, estrato de diseño `est_dis` y UPM `upm`. El trabajo se mantiene en variables nominales trimestrales y no modifica datos crudos, marts ni la etapa 10 de homologación monetaria.

## Alcance

- Fuente operativa: `data/interim/revision_4/mart_hogar_2018_2024.csv.gz` y `data/interim/revision_4/mart_persona_2018_2024.csv.gz`.
- Unidad hogar: media nominal trimestral de `ing_cor_hogar_oficial_tri`.
- Unidad persona: proporción con `ingreso_persona_laboral_negocio_tri > 0`, incluyendo personas menores en el denominador.
- Unidad persona condicionada: media nominal trimestral de `ingreso_persona_laboral_negocio_tri` solo entre personas con ingreso positivo.
- Contraste: diferencia Norte menos Sur de la media condicionada anterior.

## Fórmulas

Para un dominio descriptivo D:

`N_hat_D = sum_i w_i d_i`

`Y_hat_D = sum_i w_i d_i y_i`

`mu_hat_D = Y_hat_D / N_hat_D`

`p_hat_D = sum_i w_i d_i I(y_i > 0) / sum_i w_i d_i`

La media condicionada usa `d_i = I(y_i > 0)` dentro del dominio geográfico. El contraste se define como:

`Delta_hat = mu_hat_Norte - mu_hat_Sur`

## Varianza JKn

Se usa JKn estratificado por UPM como aproximación. Para cada estrato h con `m_h` UPMs, la réplica que elimina la UPM j asigna peso 0 a la UPM eliminada y multiplica los pesos de las demás UPM del mismo estrato por `m_h / (m_h - 1)`. Los demás estratos permanecen sin cambio.

La varianza se centra en la estimación completa:

`V_JK = sum_h ((m_h - 1) / m_h) sum_j (theta_(h,j) - theta_hat)^2`

`SE_JK = sqrt(V_JK)`

Los dominios se calculan sobre el diseño completo de cada año y unidad: las UPM fuera del dominio conservan contribución cero. El contraste Norte-Sur recalcula ambas medias dentro de la misma réplica, por lo que la covarianza queda incorporada naturalmente.

## Referencia t

El intervalo reportado es `estimación ± t(0.975, nu) * SE_JK`. Esta t es una referencia finita aproximada para la distribución muestral studentizada, no una t exacta clásica. La t exacta clásica requeriría una razón `Z / sqrt(U / nu)` con normalidad, chi-cuadrada e independencia, condiciones que no se demuestran aquí.

Regla usada:

- Diseño completo: `nu_design = M - H`.
- Dominio: `nu_D = M_D - H_D`, donde `M_D` y `H_D` son UPMs y estratos con soporte del dominio.
- Contraste Norte-Sur: soporte unido de Norte y Sur.
- Si `nu <= 0` o el dominio no tiene soporte suficiente, se bloquea el IC. Las proporciones usan Wald-t aproximado y no se recortan a `[0, 1]`.

## Auditoría de diseño

| anio | unidad | filas | estratos | upm | estratos_singleton | upm_raw_en_multiples_estratos | estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | hogar | 74647 | 543 | 8377 | 0 | 0 | ok |
| 2018 | persona | 269206 | 543 | 8377 | 0 | 0 | ok |
| 2020 | hogar | 89006 | 558 | 10118 | 0 | 0 | ok |
| 2020 | persona | 315743 | 558 | 10118 | 0 | 0 | ok |
| 2022 | hogar | 90102 | 560 | 10211 | 0 | 0 | ok |
| 2022 | persona | 309684 | 560 | 10211 | 0 | 0 | ok |
| 2024 | hogar | 91414 | 681 | 10569 | 0 | 0 | ok |
| 2024 | persona | 308598 | 681 | 10569 | 0 | 0 | ok |

Los códigos 0 en `est_dis` o `upm` se auditan, pero no se tratan como faltantes ni como inválidos por sí mismos. Cuando el mismo código crudo de UPM aparece en más de un estrato, el cálculo usa identificadores compuestos por año, estrato y UPM; no se interpreta como seguimiento longitudinal.

## Estimaciones nacionales

Media nominal trimestral del ingreso corriente del hogar:

| anio | estimacion | se_jkn | nu | ic95_inf | ic95_sup | estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | 49,851 | 455 | 7834 | 48,959 | 50,743 | ok |
| 2020 | 50,309 | 400 | 9560 | 49,524 | 51,094 | ok |
| 2022 | 63,695 | 440 | 9651 | 62,832 | 64,559 | ok |
| 2024 | 77,864 | 606 | 9888 | 76,677 | 79,051 | ok |

Proporción de personas con ingreso laboral/negocio positivo:

| anio | estimacion | se_jkn | nu | ic95_inf | ic95_sup | estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | 0.4783 | 0.0015 | 7834 | 0.4754 | 0.4813 | ok |
| 2020 | 0.4679 | 0.0014 | 9560 | 0.4652 | 0.4705 | ok |
| 2022 | 0.4843 | 0.0014 | 9651 | 0.4815 | 0.4870 | ok |
| 2024 | 0.4902 | 0.0015 | 9888 | 0.4872 | 0.4931 | ok |

Media nominal trimestral entre personas con ingreso laboral/negocio positivo:

| anio | estimacion | se_jkn | nu | ic95_inf | ic95_sup | estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | 20,275 | 220 | 7817 | 19,845 | 20,705 | ok |
| 2020 | 20,055 | 197 | 9527 | 19,669 | 20,442 | ok |
| 2022 | 26,083 | 208 | 9616 | 25,675 | 26,492 | ok |
| 2024 | 31,977 | 314 | 9868 | 31,362 | 32,592 | ok |

## Contraste Norte-Sur

| anio | estimacion | se_jkn | nu | ic95_inf | ic95_sup | estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | 12,339 | 595 | 3619 | 11,173 | 13,505 | ok |
| 2020 | 13,649 | 608 | 4408 | 12,457 | 14,840 | ok |
| 2022 | 15,986 | 542 | 4455 | 14,923 | 17,049 | ok |
| 2024 | 20,730 | 1,388 | 4506 | 18,009 | 23,450 | ok |

## Validaciones

| validacion | resultado | diferencia_maxima | tolerancia |
| --- | --- | --- | --- |
| estimacion_vs_calculo_directo_ponderado | ok | 0.000000000007 | 0.000000100000 |
| jkn_agregado_vs_replicas_explicitas_media_toy | ok | 0.000000000000 | 0.000000000100 |
| jkn_dominio_con_upm_cero_vs_replicas_explicitas_toy | ok | 0.000000000000 | 0.000000000100 |
| jkn_agregado_vs_replicas_explicitas_contraste_toy | ok | 0.000000000000 | 0.000000000100 |
| invariancia_medias_se_al_escalar_pesos | ok | 0.000000000000 | 0.000000000100 |
| invariancia_proporciones_se_al_escalar_pesos | ok | 0.000000000000 | 0.000000000100 |
| respuesta_constante_varianza_cero | ok | 0.000000000000 | 0.000000000001 |
| comparacion_R_survey_JKn | pendiente_entorno | NA | NA |

La comparación especializada con R `survey` queda preparada en `reports/tables/diseno_muestral/validacion_r_survey_jkn.R`, pero no ejecutada porque `Rscript` no está disponible en el entorno local.

## Figuras

- `C:/Users/lucia/OneDrive/Escritorio/Fer/inegi-income-modeling/reports/figures_documentacion/diseno_muestral_ingreso_hogar_ic95.svg` (svg_fallback)
- `C:/Users/lucia/OneDrive/Escritorio/Fer/inegi-income-modeling/reports/figures_documentacion/diseno_muestral_contraste_norte_sur_ic95.svg` (svg_fallback)

## Decisiones metodológicas

- Problema: incorporar diseño muestral antes de modelar. Opción tomada: JKn estratificado por UPM con `factor`, `est_dis` y `upm`. Alternativas no usadas: Taylor linearization, bootstrap, FPC o réplicas oficiales no disponibles. Razón: reproduce una inferencia descriptiva transparente con variables observables.
- Problema: dominios geográficos. Opción tomada: construir réplicas sobre el diseño completo y asignar contribución cero fuera del dominio. Alternativa descartada: filtrar antes de definir diseño. Razón: evita perder UPMs/estratos necesarios para la varianza de dominio.
- Problema: contraste Norte-Sur. Opción tomada: recalcular ambas medias dentro de cada réplica. Alternativa descartada: sumar varianzas regionales. Razón: el método conserva la covarianza implícita.
- Problema: temporalidad monetaria. Opción tomada: mantener estimandos nominales en esta etapa. Razón: la revisión de poder adquisitivo y deflactores queda como complemento metodológico posterior; no se reabre la discrepancia con Banxico.

## Limitaciones

- Los pesos replicados son construidos por el proyecto; no son pesos replicados oficiales de INEGI.
- No se reconstruyen calibración, no respuesta, FPC ni detalles no observables del diseño original.
- La referencia t no prueba cobertura exacta de 95%.
- El notebook 00 se conserva como histórico y no se usa como referencia vigente.
- La validación contra R `survey` queda pendiente por entorno, no por lógica de implementación.

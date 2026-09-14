# Auditoria de preparacion de determinantes

## Estado

- Rama de trabajo: `codex/auditoria-preparacion-determinantes`.
- Commit base auditado: `6aec7782a395d49bfb45a6d314a3feda54dc84fd`.
- Alcance: revision diagnostica de la etapa 12, sin entrenar modelos, sin particiones, sin reactivar deflactores/JKn y sin modificar matrices ni marts.
- Universo activo 2024: personas con edad >= 18 e ingreso laboral/de negocio positivo, montos nominales trimestrales.

## Archivos revisados

| archivo | tipo | uso |
| --- | --- | --- |
| src/features/preparacion_determinantes.py | codigo etapa 12 | reglas de universo, transformaciones, OHE y VIF |
| notebooks/12_preparacion_base_determinantes.ipynb | notebook etapa 12 | ejecucion narrativa parametrizada |
| reports/preparacion_base_determinantes.md | reporte etapa 12 | resumen vigente de preparacion |
| reports/tables/preparacion_determinantes/2024/*.csv | tablas etapa 12 | faltantes, OHE, VIF, reproduccion y validaciones |
| reports/tables/preparacion_determinantes/compatibilidad_*.csv | tablas etapa 12 | compatibilidad por ano |
| data/interim/revision_3/catalogo_categoricas_enigh.csv | catalogo local | codigos y etiquetas extraidas de documentacion |
| data/interim/revision_4/mart_persona_2018_2024.csv.gz | mart nominal | base fuente de la etapa 12 |
| data/interim/revision_4/ingresos_agregados_persona.csv.gz | agregado persona | trazabilidad del target |
| data/raw/EINGH/2024/ingresos.csv | fuente cruda | trazabilidad agregada del maximo sin guardar folios |

## Hallazgos por tipo

Tipos usados: A = hecho observado; B = explicacion respaldada por evidencia; C = hipotesis pendiente; D = decision que requiere aprobacion.

| tipo | asunto | evidencia | causa | accion |
| --- | --- | --- | --- | --- |
| A_hecho | 2024 reproducido | La reproduccion previa registra 141579 personas, 80872 hogares, 67 columnas X, rango 68/68 y maximo 17021739.12. | Ejecucion parametrizada de etapa 12 para ANIO_ANALISIS=2024. | Mantener 2024 como base ejecutada y marcar revision pendiente. |
| B_explicacion | segsoc_desc 2020/2022 sin referencia No | El catalogo local contiene codigo 2 con etiquetas contaminadas por texto invertido en 2020/2022; el universo si contiene codigo 2. | Problema de etiqueta extraida/decodificada, no ausencia de la categoria en el universo. | Proponer correccion codigo 2 -> No en 2020/2022, sin aplicarla hasta aprobacion. |
| A_hecho | faltantes laborales 2024 | subor_principal_desc faltante=5205; contrato_principal_desc faltante=37124. | subor falta cuando no hay trabajo principal reportado; contrato falta fuera de la ruta de trabajador con pago. | Conservar base intacta y pedir decision antes de cambiar especificacion laboral. |
| C_hipotesis | ingreso positivo sin trabajo principal reportado | Hay 5205 personas del universo 2024 con target positivo, sin trabajo principal reportado y sin id_trabajo_principal. | Puede corresponder a ingresos registrados sin fila de trabajos en la ventana observada o a una integracion a revisar; no se demuestra error con esta auditoria. | Mantener clasificacion estructural y revisar documentacion/ruta laboral si se decide modelar detalles del trabajo principal. |
| B_explicacion | maximo y cola derecha | Maximo=17021739.12; top 0.1% aporta 3.0333%; media total=31171.87, media sin top 0.1%=30256.69. | Suma nominal trimestral de claves laborales/de negocio; cola derecha extrema. | Documentar cola y evaluar transformacion/modelo robusto en etapa posterior. |
| A_hecho | tam_emp_principal_desc duplicaria una dummy | La categoria estructural sin trabajo principal de tam_emp coincide exactamente con la dummy estructural de subor. | Ambas variables comparten el mismo estado no aplica cuando no existe trabajo principal reportado. | Aprobar si se mantiene fuera, se recodifica solo entre trabajadores o se usa especificacion laboral separada. |
| B_explicacion | variables propias y de jefatura | Jefes/as=68035 (48.0544%); sexo propio y de jefatura coincide en jefes/as. | sexo_jefe es derivado del jefe del hogar; para no jefes/as funciona como contexto del hogar. | Mantener como hallazgo contextual; decidir especificacion de contexto del hogar antes de modelar. |
| A_hecho | VIF alto en bloque laboral/educativo | Mayor VIF=36.4987 en contrato_principal_desc__no_aplica_sin_contrato_principal_documentado; rango con intercepto completo. | Asociacion mecanica/semantica entre contrato, subordinacion y categorias educativas codificadas k-1. | Usar tabla VIF detallada como insumo para decisiones de especificacion. |
| D_decision | preparacion no cerrada | 2018 solo inspeccionado; 2020/2022 requieren correccion de segsoc_desc; 2024 auditado con pendientes. | La comparabilidad anual de coeficientes exige especificacion comun posterior. | Aprobar mapeos, tratamiento de laborales, tam_emp, cola y contexto de jefatura antes de cambiar X. |

## Seguridad social 2020/2022

La referencia OHE esperada para `segsoc_desc` es la etiqueta exacta `No`. En 2020 y 2022 la categoria no esta ausente del universo: aparece el codigo original `2`, pero su etiqueta local queda contaminada como texto invertido de la extraccion documental. No es un problema de espacios, mayusculas/minusculas o acentos.

| anio | segsoc_codigo | segsoc_etiqueta | n | pct_en_anio_ambito |
| --- | --- | --- | --- | --- |
| 2018 | 1 | Sí | 68625 | 0.5716177720025988 |
| 2018 | 2 | No | 51429 | 0.42838222799740117 |
| 2020 | 1 | Sí | 81436 | 0.5842145286023789 |
| 2020 | 2 | No nóicpircseD .0202 y | 57958 | 0.4157854713976211 |
| 2022 | 1 | Sí | 83518 | 0.5901748236923555 |
| 2022 | 2 | No nóicpircseD .2202 y | 57996 | 0.4098251763076445 |
| 2024 | 1 | Sí | 83301 | 0.5883711567393469 |
| 2024 | 2 | No | 58278 | 0.4116288432606531 |

Mapeo propuesto, no aplicado:

| anio | variable | codigo_original | etiqueta_observada | etiqueta_propuesta | base_evidencia | estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2020 | segsoc_desc | 2 | No nóicpircseD .0202 y | No | Catalogo local: misma variable con rango binario; codigo 2 contaminado por texto invertido de extraccion en 2020/2022; codigo 2 aparece con etiqueta limpia No en 2018/2024. | propuesta_no_aplicada_requiere_aprobacion |
| 2022 | segsoc_desc | 2 | No nóicpircseD .2202 y | No | Catalogo local: misma variable con rango binario; codigo 2 contaminado por texto invertido de extraccion en 2020/2022; codigo 2 aparece con etiqueta limpia No en 2018/2024. | propuesta_no_aplicada_requiere_aprobacion |

## Faltantes laborales 2024

Los faltantes de `subor_principal_desc` se concentran en personas con ingreso laboral/de negocio positivo pero sin trabajo principal reportado en `trabajos`. Los de `contrato_principal_desc` se concentran fuera de la ruta de trabajador con pago; la regla actual los convierte en categoria estructural en la matriz, no en imputacion.

| variable | clasificacion | n | pct_universo | con_trabajo_reportado | con_id_trabajo_principal |
| --- | --- | --- | --- | --- | --- |
| subor_principal_desc | no_aplica_sin_trabajo_principal_reportado | 5205 | 0.03676392685355879 | 0 | 0 |
| subor_principal_desc | observado | 136374 | 0.9632360731464412 | 136374 | 136374 |
| contrato_principal_desc | no_aplica_pago_principal_no_documentado | 31267 | 0.22084489931416382 | 31267 | 31267 |
| contrato_principal_desc | no_aplica_sin_trabajo_principal_reportado | 5205 | 0.03676392685355879 | 0 | 0 |
| contrato_principal_desc | no_aplica_trabajador_sin_pago | 652 | 0.004605202748995261 | 652 | 652 |
| contrato_principal_desc | observado | 104455 | 0.7377859710832821 | 104455 | 104455 |

Frecuencias de la categoria usada actualmente en matriz:

| variable | categoria_matriz | n | pct_universo |
| --- | --- | --- | --- |
| subor_principal_desc | Sí | 104929 | 0.7411339252290241 |
| subor_principal_desc | No | 31445 | 0.22210214791741714 |
| subor_principal_desc | No aplica: sin trabajo principal reportado | 5205 | 0.03676392685355879 |
| contrato_principal_desc | No | 52696 | 0.3722020921181814 |
| contrato_principal_desc | Sí | 51759 | 0.36558387896510075 |
| contrato_principal_desc | No aplica: sin contrato principal documentado | 37124 | 0.26221402891671786 |

## Maximo y cola derecha

La trazabilidad del maximo se verifico contra el agregado de ingresos por persona y contra `ingresos.csv` 2024 usando claves 1-22 y 67-81, que son las claves del target documentadas en el notebook de construccion de marts. La tabla de componentes no incluye folios ni llaves personales.

| validacion | valor_mart | valor_fuente | diferencia | estado |
| --- | --- | --- | --- | --- |
| mart_vs_ingresos_agregados | 17021739.119999997 | 17021739.119999997 | 0.0 | ok |
| mart_vs_ingresos_raw_claves_1_22_67_81 | 17021739.119999997 | 17021739.119999997 | 0.0 | ok |
| raw_total_persona_todas_claves | 17373913.029999997 | 17373913.029999997 | 0.0 | ok |

Metricas de cola:

| metrica | valor |
| --- | --- |
| n | 141579.0 |
| sum | 4413282142.37 |
| mean | 31171.869714929475 |
| median | 24245.89 |
| p95 | 79239.13 |
| p99 | 154663.03 |
| p99_9 | 425676.6289399673 |
| max | 17021739.119999997 |
| mean_excluyendo_top_0_1pct | 30256.689971223936 |
| n_excluyendo_top_0_1pct | 141437.0 |

Participacion de la cola:

| grupo | pct_solicitado | n_incluido | criterio_empates | valor_corte | empates_totales_en_corte | empates_incluidos_en_corte | ingreso_sum | share_ingreso_muestral |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_1.000% | 0.01 | 1416 | orden descendente estable; no se expande el corte por empates | 154663.03 | 2 | 1 | 414173494.07000005 | 0.09384704641783509 |
| top_0.100% | 0.001 | 142 | orden descendente estable; no se expande el corte por empates | 427868.85 | 1 | 1 | 133866682.91 | 0.03033268179815749 |

## Tamano de empresa

`tam_emp_principal_desc` conserva informacion sustantiva de tamano de empresa para quienes tienen trabajo principal. El problema detectado es acotado: si entrara a OHE, su categoria estructural `No aplica: sin trabajo principal reportado` duplicaria exactamente la dummy estructural ya creada por `subor_principal_desc`.

| columna_a_si_tam_emp_entrara_a_x | columna_b_existente_en_x | categoria | n_columna_a | n_columna_b | duplicada_exacta | ambito_duplicacion | informacion_no_duplicada_perdida_en_x_actual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tam_emp_principal_desc__no_aplica_sin_trabajo_principal_reportado | subor_principal_desc__no_aplica_sin_trabajo_principal_reportado | No aplica: sin trabajo principal reportado | 5205 | 5205 | True | solo_categoria_estructural_sin_trabajo_principal_reportado | tamano de empresa observado en 12 categorias para quienes si tienen trabajo principal reportado |

## Variables propias y de jefatura

Para personas que son jefe(a), `sexo_desc` y `sexo_jefe_desc` coinciden como se espera. Para no jefes/as, `sexo_jefe_desc` es contexto del hogar, no copia de la persona. En educacion, `nivelaprob_desc` y `educa_jefe_desc` no son escalas textuales identicas: `educa_jefe_desc` separa completo/incompleto y profesional, por lo que la no coincidencia textual exacta no implica error de construccion.

| metrica | valor | pct_universo | nota |
| --- | --- | --- | --- |
| personas_universo | 141579 | 1.0 | Universo 2024 de determinantes. |
| personas_jefe_a | 68035 | 0.4805444310243751 | parentesco_desc == Jefe(a). |
| jefes_sexo_desc_coincide | 68035 | 1.0 | Entre jefes/as, sexo_desc y sexo_jefe_desc coinciden. |
| jefes_sexo_codigo_coincide | 68035 | 1.0 | Entre jefes/as, sexo y sexo_jefe coinciden por codigo. |
| jefes_nivelaprob_educa_jefe_match_texto_exacta | 0 | 0.0 | Comparacion textual exacta; no debe esperarse 100% porque educa_jefe clasifica completo/incompleto y profesional. |

## VIF y dependencias

La X guardada de 2024 tiene 67 columnas; el rango con intercepto es completo. El intercepto se agrega solo para diagnostico de rango y no esta dentro de X. Los VIF guardados usan la inversa de la matriz de correlaciones, equivalente al VIF de regresiones auxiliares con intercepto sobre variables no constantes; la verificacion auxiliar reproduce los 15 VIF mas altos.

| columna_matriz | variable_original | categoria | referencia_variable | frecuencia_categoria | vif |
| --- | --- | --- | --- | --- | --- |
| contrato_principal_desc__no_aplica_sin_contrato_principal_documentado | contrato_principal_desc | No aplica: sin contrato principal documentado | No | 37124 | 36.49869571627536 |
| subor_principal_desc__si | subor_principal_desc | Sí | No | 104929 | 36.38905748568494 |
| nivelaprob_desc__secundaria | nivelaprob_desc | Secundaria | Ninguno | 42046 | 12.597583006845536 |
| nivelaprob_desc__preparatoria_o_bachillerato | nivelaprob_desc | Preparatoria o bachillerato | Ninguno | 32230 | 11.835690175922837 |
| nivelaprob_desc__licenciatura_o_ingenieria_profesional | nivelaprob_desc | Licenciatura o Ingeniería (profesional) | Ninguno | 27905 | 11.778720190870906 |
| nivelaprob_desc__primaria | nivelaprob_desc | Primaria | Ninguno | 28255 | 9.158746050715028 |
| educa_jefe_desc__secundaria_completa | educa_jefe_desc | Secundaria completa | Sin instrucción | 40850 | 7.900242961796901 |
| educa_jefe_desc__preparatoria_completa | educa_jefe_desc | Preparatoria completa | Sin instrucción | 20179 | 5.803011553497795 |
| educa_jefe_desc__profesional_completa | educa_jefe_desc | Profesional completa | Sin instrucción | 15615 | 5.533420501073588 |
| educa_jefe_desc__primaria_completa | educa_jefe_desc | Primaria completa | Sin instrucción | 23550 | 5.17407351133238 |
| educa_jefe_desc__primaria_incompleta | educa_jefe_desc | Primaria incompleta | Sin instrucción | 18167 | 4.25761620812779 |
| educa_jefe_desc__posgrado | educa_jefe_desc | Posgrado | Sin instrucción | 3037 | 2.770515014946937 |
| parentesco_desc__hijo_a_hijo_a_consanguineo_hijo_a_reconocido | parentesco_desc | Hijo(a), hijo(a) consanguíneo, hijo(a) reconocido | Jefe(a) | 34115 | 2.736523385581707 |
| nivelaprob_desc__maestria | nivelaprob_desc | Maestría | Ninguno | 2243 | 2.6810010216014257 |
| edad | edad |  |  | 141579 | 2.5342776923448502 |

## Decisiones pendientes antes de cambiar X

- Aprobar correccion explicita de `segsoc_desc` codigo 2 a `No` en 2020 y 2022, sin cambiar semantica de otros codigos.
- Definir si las variables laborales del trabajo principal deben modelarse en todo el universo activo o en una especificacion separada para trabajadores con trabajo reportado/con pago.
- Definir si `tam_emp_principal_desc` queda fuera, se recodifica para evitar la dummy estructural duplicada o se usa solo en una submuestra laboral.
- Definir tratamiento de cola derecha: sin recorte actual; cualquier log-transformacion, robustez, winsorizacion o exclusion requiere aprobacion.
- Definir como entraran variables de contexto del hogar, especialmente sexo y educacion de jefatura, dada la redundancia esperada para jefes/as.
- Definir especificacion comun posterior si se quieren comparar coeficientes entre anos.

## Estado documental

La etapa 12 debe leerse como implementacion ejecutada para 2024, con revision metodologica pendiente. 2018 esta inspeccionado como compatible; 2020 y 2022 requieren resolver `segsoc_desc` antes de generar bases; 2024 esta reproducido y ahora auditado con pendientes abiertos.

## Salidas

Las tablas agregadas de esta auditoria estan en `reports/tables/auditoria_preparacion_determinantes/`. No se generaron matrices nuevas, no se modificaron marts, no se crearon modelos y no se realizo push ni merge.

# Regresion diagnostica de determinantes

## Estado

- Notebook: `notebooks/13_regresion_diagnostico_determinantes.ipynb`.
- Configuracion: `ANIO_ANALISIS=2024`, `EDAD_MINIMA=18`, `TARGET=ingreso_persona_laboral_negocio_tri`, `CRITERIO_STEPWISE=None`, `EJECUTAR_SELECCION=False`.
- Alcance: primera ejecucion diagnostica con todas las variables candidatas admisibles de la etapa 12. No hay seleccion automatica, regresion reducida ni regresion por componentes.
- La validacion es diagnostica; no es prueba final independiente.

## Dependencias

| paquete | disponible | version |
| --- | --- | --- |
| numpy | True | 2.4.6 |
| pandas | True | 3.0.5 |
| sklearn | True | 1.9.0 |
| matplotlib | True | 3.10.9 |
| scipy | True | 1.17.1 |
| statsmodels | False |  |
| nbformat | False |  |
| nbclient | False |  |

## Variables

Incluidas inicialmente:

| variable | estado | tipo |
| --- | --- | --- |
| edad | incluida | continua |
| n_trabajos | incluida | continua |
| horas_trabajos_total | incluida | continua |
| tot_integ | incluida | continua |
| menores | incluida | continua |
| p65mas | incluida | continua |
| sexo_desc | incluida | categorica |
| nivelaprob_desc | incluida | categorica |
| region_banxico | incluida | categorica |
| tam_loc_desc | incluida | categorica |
| parentesco_desc | incluida | categorica |
| hablaind_desc | incluida | categorica |
| segsoc_desc | incluida | categorica |
| subor_principal_desc | incluida | categorica |
| contrato_principal_desc | incluida | categorica |
| sexo_jefe_desc | incluida | categorica |
| educa_jefe_desc | incluida | categorica |

Pendientes:

| variable | motivo | estado |
| --- | --- | --- |
| tam_emp_principal_desc | Pendiente de parametrizacion: conserva informacion de tamano, pero su categoria estructural duplicaria una dummy de subor si entrara sin recodificar. | pendiente_no_incluida_en_matriz_identificable |
| est_socio_desc | Diagnostico contextual; requiere aprobacion para entrar al modelo. | pendiente_no_incluida_en_matriz_identificable |

Exclusiones tecnicas:

| grupo | criterio |
| --- | --- |
| target_derivados | Excluir target, log(target), componentes y agregados que contienen el ingreso objetivo. |
| identificadores | Excluir llaves de persona/hogar, entidad, municipio e identificadores. |
| pesos_diseno | Conservar factor, factor_hogar, est_dis y upm como metadata; no predictores. |
| deflactores_reales | Etapas 10/11 deprecadas; no usar deflactores, variables reales ni JKn. |
| constantes_duplicados | Excluir columnas constantes o duplicados exactos si aparecen en la matriz identificable. |
| representaciones_redundantes | Usar una representacion interpretable por variable; no incluir simultaneamente codigo y etiqueta. |

## Compatibilidad anual previa

Esta etapa ejecuta diagnosticos solo para el año seleccionado. Los demas años quedan solo como compatibilidad inspeccionada desde la etapa 12; no se generan matrices ni modelos anuales adicionales.

| anio | estado_preparacion | filas_universo | hogares_unicos | referencias_ohe_faltantes | estado_en_regresion_diagnostica | nota_regresion |
| --- | --- | --- | --- | --- | --- | --- |
| 2018 | compatible_para_generar_base | 120054 | 67807 |  | solo_compatibilidad_inspeccionada_previa | No se genero matriz ni modelo para este anio en esta etapa. |
| 2020 | revisar_antes_de_generar_base | 139394 | 79365 | segsoc_desc | solo_inspeccion_previa_con_pendientes | No se genero matriz; resolver referencias OHE antes de ejecutar. |
| 2022 | revisar_antes_de_generar_base | 141514 | 80217 | segsoc_desc | solo_inspeccion_previa_con_pendientes | No se genero matriz; resolver referencias OHE antes de ejecutar. |
| 2024 | compatible_para_generar_base | 141579 | 80872 |  | ejecutado_y_validado_en_esta_etapa | Se genero diagnostico de regresion, PCA y arbol para este anio. |

Categorias no vistas al aplicar referencias y categorias aprendidas en entrenamiento:

| variable_original | categoria_no_vista_en_entrenamiento | n | particion |
| --- | --- | --- | --- |
| parentesco_desc | Hijo(a) de crianza | 1 | validacion |

## Particion

Particion 80/20 por hogares con semilla `20240914`. La pertenencia se guardo localmente fuera de Git en `data/processed/regresion_diagnostico/2024/diagnostico_inicial/`.

| particion | personas | hogares | pct_personas | pct_hogares |
| --- | --- | --- | --- | --- |
| entrenamiento | 113173 | 64697 | 0.799362899865093 | 0.799992580868533 |
| validacion | 28406 | 16175 | 0.200637100134907 | 0.200007419131467 |

## Reproduccion 2024

La ejecucion 2024 reproduce el universo y resumen del target de la etapa 12 dentro de tolerancias explicitas. La matriz de esta etapa no se compara columna a columna con la matriz de preparacion porque aqui se ajusta solo sobre entrenamiento y se excluyen variables pendientes.

| metrica | esperado | observado | tolerancia | diferencia_abs | resultado | nota |
| --- | --- | --- | --- | --- | --- | --- |
| universo_filas | 141579.0 | 141579.0 | 0.0 | 0.0 | ok | Comparacion contra etapa 12. |
| hogares_unicos | 80872.0 | 80872.0 | 0.0 | 0.0 | ok | Comparacion contra etapa 12. |
| media_target | 31171.869714929475 | 31171.869714929475 | 0.01 | 0.0 | ok | Comparacion contra etapa 12. |
| mediana_target | 24245.89 | 24245.89 | 0.01 | 0.0 | ok | Comparacion contra etapa 12. |
| p99_target | 154663.03 | 154663.03 | 0.01 | 0.0 | ok | Comparacion contra etapa 12. |
| max_target | 17021739.12 | 17021739.119999997 | 0.01 | 3.725290298461914e-09 | ok | Comparacion contra etapa 12. |
| columnas_matriz_diagnostica |  | 66.0 |  |  | documentado | No se compara contra X_columnas de etapa 12: esta matriz excluye pendientes y se ajusta solo con entrenamiento. |

## Regresiones diagnosticas

OLS no ponderado con intercepto. No es estimacion de diseno poblacional. Los p-values convencionales no se destacan como evidencia inferencial.

| escala | n_entrenamiento | parametros_con_intercepto | rango_con_intercepto | r2_entrenamiento | r2_ajustado_entrenamiento | aic_entrenamiento_misma_escala | bic_entrenamiento_misma_escala | nota |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ingreso_nominal | 113173 | 67 | 67 | 0.06996756366513956 | 0.06942486795670588 | 2511093.797483678 | 2511739.4545680047 | AIC/BIC solo comparables dentro de la misma escala de respuesta. |
| log_ingreso | 113173 | 67 | 67 | 0.4599805666846475 | 0.45966545269777837 | -27309.210765558815 | -26663.553681231966 | AIC/BIC solo comparables dentro de la misma escala de respuesta. |

| escala | particion | n | mae | rmse |
| --- | --- | --- | --- | --- |
| ingreso_nominal | entrenamiento | 113173 | 15781.40146393741 | 65739.66769857414 |
| ingreso_nominal | validacion | 28406 | 15827.766090646921 | 41410.43241381606 |
| log_ingreso | entrenamiento | 113173 | 0.6191864958611608 | 0.8858173383709359 |
| log_ingreso | validacion | 28406 | 0.6310463427055871 | 0.9032703807913339 |

La version logaritmica usa las mismas filas, variables y particion. Sus AIC/R2 se reportan dentro de su escala y no se comparan directamente con ingreso nominal. No se aplica retransfomacion exponencial.

## VIF/GVIF

La matriz de entrenamiento se reviso por rango, constantes y duplicados exactos antes de VIF/GVIF.

| metrica | valor |
| --- | --- |
| filas | 113173 |
| columnas | 66 |
| rango_sin_intercepto | 66 |
| rango_con_intercepto | 67 |
| constantes | 0 |
| duplicados_exactos | 0 |

VIF por columna mas altos:

| columna_matriz | variable_original | categoria | referencia_variable | vif |
| --- | --- | --- | --- | --- |
| contrato_principal_desc__no_aplica_sin_contrato_principal_documentado | contrato_principal_desc | No aplica: sin contrato principal documentado | No | 35.70218285738494 |
| subor_principal_desc__si | subor_principal_desc | Sí | No | 35.59837300656483 |
| nivelaprob_desc__secundaria | nivelaprob_desc | Secundaria | Ninguno | 12.71174961500345 |
| nivelaprob_desc__licenciatura_o_ingenieria_profesional | nivelaprob_desc | Licenciatura o Ingeniería (profesional) | Ninguno | 11.90422430396421 |
| nivelaprob_desc__preparatoria_o_bachillerato | nivelaprob_desc | Preparatoria o bachillerato | Ninguno | 11.903264618003515 |
| nivelaprob_desc__primaria | nivelaprob_desc | Primaria | Ninguno | 9.21060245169005 |
| educa_jefe_desc__secundaria_completa | educa_jefe_desc | Secundaria completa | Sin instrucción | 7.999994753561717 |
| educa_jefe_desc__preparatoria_completa | educa_jefe_desc | Preparatoria completa | Sin instrucción | 5.856483388294256 |
| educa_jefe_desc__profesional_completa | educa_jefe_desc | Profesional completa | Sin instrucción | 5.624710825058043 |
| educa_jefe_desc__primaria_completa | educa_jefe_desc | Primaria completa | Sin instrucción | 5.224384640017018 |

GVIF por bloque mas altos:

| variable_original | df_bloque | gvif | gvif_ajustado | estado |
| --- | --- | --- | --- | --- |
| subor_principal_desc | 2 | 57.105250466107 | 2.7489637325607035 | ok |
| contrato_principal_desc | 2 | 49.486862391104374 | 2.652298989286199 | ok |
| edad | 1 | 2.529876616438462 | 1.5905585862955385 | ok |
| tot_integ | 1 | 2.1384252292807373 | 1.462335539225091 | ok |
| menores | 1 | 2.0144272500492244 | 1.41930519975417 | ok |
| n_trabajos | 1 | 1.6980794055410673 | 1.3031037585476712 | ok |
| segsoc_desc | 1 | 1.5603579426482037 | 1.2491428831995977 | ok |
| p65mas | 1 | 1.5275421766077797 | 1.2359377721421818 | ok |
| sexo_desc | 1 | 1.4692558552123425 | 1.2121286463128995 | ok |
| horas_trabajos_total | 1 | 1.4549417033887562 | 1.206209643216616 | ok |

## PCA exploratorio

PCA se ajusto solo con entrenamiento. Continuas estandarizadas con parametros de entrenamiento; categoricas con OHE completo centrado y sin escalado por desviacion. Esta geometria no es neutral y puede asignar distinta inercia a bloques categoricos. Componentes no nulos: 66; componentes nulos: 11. No se selecciono numero de componentes ni se ajusto PCR.

| componente | valor_propio | varianza_explicada | varianza_acumulada | componente_nulo |
| --- | --- | --- | --- | --- |
| PC1 | 1.861991576272746 | 0.15141370650688157 | 0.15141370650688157 | False |
| PC2 | 1.5082177377129597 | 0.1226454731571202 | 0.2740591796640018 | False |
| PC3 | 1.3382675687976622 | 0.10882544017477633 | 0.3828846198387781 | False |
| PC4 | 0.9129853353726025 | 0.07424227659069968 | 0.4571268964294778 | False |
| PC5 | 0.8095418025393362 | 0.06583044008185564 | 0.5229573365113335 | False |
| PC6 | 0.6399683771735019 | 0.05204104318721146 | 0.574998379698545 | False |
| PC7 | 0.48527105898103945 | 0.039461343776818356 | 0.6144597234753633 | False |
| PC8 | 0.47634182659417007 | 0.03873523513637887 | 0.6531949586117421 | False |
| PC9 | 0.38671622169468356 | 0.03144704693580843 | 0.6846420055475506 | False |
| PC10 | 0.37133704741268797 | 0.030196440965982518 | 0.7148384465135331 | False |
| PC11 | 0.33945804940157714 | 0.02760409988877415 | 0.7424425464023072 | False |
| PC12 | 0.3019453394563302 | 0.024553635790919712 | 0.766996182193227 | False |
| PC13 | 0.275273715227452 | 0.02238474870543827 | 0.7893809308986652 | False |
| PC14 | 0.25939775442695084 | 0.02109374497599405 | 0.8104746758746593 | False |
| PC15 | 0.24729699718834305 | 0.020109733808389714 | 0.830584409683049 | False |

## Arbol exploratorio

DecisionTreeRegressor diagnostico con `max_depth=5`, `min_samples_leaf=0.01`, semilla fija. No hubo busqueda de hiperparametros. Las importancias no son causalidad ni colinealidad; la importancia por impureza puede tener sesgo de cardinalidad y la permutacion por bloques conserva dummies categoricas conjuntas.

| escala | particion | n | mae | rmse |
| --- | --- | --- | --- | --- |
| arbol_ingreso_nominal | entrenamiento | 113173 | 16097.544661003501 | 66159.91737325829 |
| arbol_ingreso_nominal | validacion | 28406 | 15977.2235888836 | 41997.04236959743 |

Importancia por impureza:

| variable_original | importancia_impureza |
| --- | --- |
| contrato_principal_desc | 0.37413968519801793 |
| educa_jefe_desc | 0.2925109893915524 |
| horas_trabajos_total | 0.15667810523508185 |
| subor_principal_desc | 0.056977893972763725 |
| sexo_desc | 0.03998739956679373 |
| segsoc_desc | 0.0365889732528032 |
| edad | 0.0222627665513576 |
| region_banxico | 0.011685707275872571 |
| nivelaprob_desc | 0.009168479555756972 |
| p65mas | 0.0 |
| n_trabajos | 0.0 |
| menores | 0.0 |

Importancia por permutacion:

| variable_original | delta_rmse_media | delta_rmse_sd | delta_rmse_min | delta_rmse_max | delta_mae_media | delta_mae_sd | delta_mae_min | delta_mae_max | repeticiones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| educa_jefe_desc | 1708.2330596431107 | 40.84415333668653 | 1637.8230994013065 | 1767.8422085239945 | 1228.4175196161214 | 32.76776121837801 | 1191.8291968226185 | 1277.2882327529187 | 10 |
| contrato_principal_desc | 1663.9230807940207 | 58.75897264856076 | 1526.7717046937105 | 1752.612498159724 | 2510.8480677635453 | 35.999088777074995 | 2425.4777760699253 | 2553.2137905966592 | 10 |
| horas_trabajos_total | 1217.6210372185524 | 73.62541410503786 | 1140.1723962665856 | 1366.1453740286015 | 2141.5616286185636 | 38.19651305473557 | 2093.652001607883 | 2202.365014164676 | 10 |
| subor_principal_desc | 306.87991380252936 | 70.0647366389024 | 185.76920816178608 | 404.85168896415416 | 46.91544094372311 | 22.301995429660767 | 10.39494630619447 | 79.83989116984412 | 10 |
| segsoc_desc | 290.1940839249161 | 22.815498241922676 | 244.55224675038335 | 326.4511033085 | 882.2074593876048 | 21.53658384118274 | 848.3433284703533 | 920.8387503232152 | 10 |
| sexo_desc | 264.6428338890968 | 19.506131881102867 | 236.74006712545815 | 297.2212283794797 | 449.30933360093 | 11.562511505305492 | 432.0720389299022 | 475.3215239286037 | 10 |
| edad | 141.08930583917973 | 10.261309641941505 | 119.73508012993989 | 154.05535438727384 | 149.993414787473 | 9.75915525359444 | 133.07463644473683 | 161.48252989668254 | 10 |
| region_banxico | 128.71265086523417 | 22.495373141965377 | 96.88219824346743 | 156.32907359997625 | 248.57684009821224 | 11.684867288552349 | 233.4466393916773 | 271.69472826837773 | 10 |
| nivelaprob_desc | 54.778615766255825 | 5.129239751591746 | 47.44447699745797 | 65.61209133532975 | 82.86289443761925 | 9.62043363891662 | 73.85305466516729 | 103.2264131955344 | 10 |
| p65mas | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10 |
| n_trabajos | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10 |
| menores | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10 |

## Tabla de revision

| variable | VIF_GVIF | evidencia_pca | importancia_arbol | problema_interpretativo | accion_propuesta | estado_aprobacion |
| --- | --- | --- | --- | --- | --- | --- |
| edad | GVIF=2.5299; df=1; adj=1.5906 | max \|carga\| 0.4775 en PC1 (edad) | impureza=0.022263; perm_delta_rmse=141.0893 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| n_trabajos | GVIF=1.6981; df=1; adj=1.3031 | max \|carga\| 0.5967 en PC2 (n_trabajos) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| horas_trabajos_total | GVIF=1.4549; df=1; adj=1.2062 | max \|carga\| 0.6734 en PC2 (horas_trabajos_total) | impureza=0.156678; perm_delta_rmse=1217.6210 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| tot_integ | GVIF=2.1384; df=1; adj=1.4623 | max \|carga\| 0.5638 en PC1 (tot_integ) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| menores | GVIF=2.0144; df=1; adj=1.4193 | max \|carga\| 0.5714 en PC1 (menores) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| p65mas | GVIF=1.5275; df=1; adj=1.2359 | max \|carga\| 0.6922 en PC4 (p65mas) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| sexo_desc | GVIF=1.4693; df=1; adj=1.2121 | max \|carga\| 0.3988 en PC6 (sexo_desc__mujer) | impureza=0.039987; perm_delta_rmse=264.6428 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| nivelaprob_desc | GVIF=19.6840; df=10; adj=1.1607 | max \|carga\| 0.5505 en PC10 (nivelaprob_desc__secundaria) | impureza=0.009168; perm_delta_rmse=54.7786 | bloque educativo con dependencia esperable | revisar GVIF/VIF y estabilidad de betas en fases futuras | pendiente_aprobacion |
| region_banxico | GVIF=1.2209; df=3; adj=1.0338 | max \|carga\| 0.0874 en PC8 (region_banxico__centro) | impureza=0.011686; perm_delta_rmse=128.7127 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| tam_loc_desc | GVIF=1.3725; df=3; adj=1.0542 | max \|carga\| 0.1929 en PC6 (tam_loc_desc__localidades_con_100_000_y_mas_habitantes) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| parentesco_desc | GVIF=4.1855; df=26; adj=1.0279 | max \|carga\| 0.2765 en PC9 (parentesco_desc__jefe_a) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| hablaind_desc | GVIF=1.1821; df=1; adj=1.0873 | max \|carga\| 0.0514 en PC3 (hablaind_desc__no) | impureza=0.000000; perm_delta_rmse=0.0000 | sin decision automatica en esta ejecucion | mantener hasta revision conjunta | pendiente_aprobacion |
| segsoc_desc | GVIF=1.5604; df=1; adj=1.2491 | max \|carga\| 0.3036 en PC5 (segsoc_desc__no) | impureza=0.036589; perm_delta_rmse=290.1941 | 2020/2022 tienen mapeo pendiente; 2024 si ejecutado | aprobar mapeo anual antes de comparaciones | pendiente_aprobacion |
| subor_principal_desc | GVIF=57.1053; df=2; adj=2.7490 | max \|carga\| 0.4134 en PC7 (subor_principal_desc__si) | impureza=0.056978; perm_delta_rmse=306.8799 | variable laboral depende de ruta de trabajo principal/pago | revisar especificacion laboral antes de eliminar | pendiente_aprobacion |
| contrato_principal_desc | GVIF=49.4869; df=2; adj=2.6523 | max \|carga\| 0.4958 en PC7 (contrato_principal_desc__no) | impureza=0.374140; perm_delta_rmse=1663.9231 | variable laboral depende de ruta de trabajo principal/pago | revisar especificacion laboral antes de eliminar | pendiente_aprobacion |
| sexo_jefe_desc | GVIF=1.2178; df=1; adj=1.1035 | max \|carga\| 0.3543 en PC9 (sexo_jefe_desc__hombre) | impureza=0.000000; perm_delta_rmse=0.0000 | variable de jefatura mezcla contexto del hogar y redundancia para jefes/as | definir si entra como contexto familiar | pendiente_aprobacion |
| educa_jefe_desc | GVIF=18.6547; df=10; adj=1.1575 | max \|carga\| 0.5203 en PC10 (educa_jefe_desc__secundaria_completa) | impureza=0.292511; perm_delta_rmse=1708.2331 | variable de jefatura mezcla contexto del hogar y redundancia para jefes/as; bloque educativo con dependencia esperable | definir si entra como contexto familiar; revisar GVIF/VIF y estabilidad de betas en fases futuras | pendiente_aprobacion |

## Roadmap: Plan de regresion y diagnostico

A. Preparacion y auditoria de base parametrizada. Estado: avances existentes; pendientes documentados.

B. Regresion completa y diagnosticos VIF/GVIF, PCA y arbol. Estado: primera ejecucion diagnostica implementada en esta etapa.

C. Revision conjunta de diagnosticos. Estado: pendiente de aprobacion del usuario.

D. Seleccion iterativa supervisada. Estado: pendiente; criterio stepwise y eliminaciones por acordar.

E. Regresion reducida y regresion por componentes. Estado: pendiente; escala principal y componentes por acordar.

F. Comparacion, estabilidad, interpretacion y documentacion final. Estado: pendiente.

Pausas metodologicas: ninguna eliminacion se adopta sin revision; stepwise y eliminacion por multicolinealidad son rutas distintas; no se avanza automaticamente de B a D/E.

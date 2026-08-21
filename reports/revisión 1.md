# Revision 1

## 1. Bases por año

Se identificaron las tablas centrales definidas en el README para los cuatro levantamientos ENIGH 2018, 2020, 2022 y 2024. Para cada tabla se genero una version apilada con la interseccion de columnas comunes, una columna temporal `anio` y la homologacion explicita de renombres 2024 validados.

| tabla | 2018 | 2020 | 2022 | 2024 | columnas_comunes | archivo_apilado |
| --- | --- | --- | --- | --- | --- | --- |
| concentradohogar.csv | 74647 | 89006 | 90102 | 91414 | 124 | data\interim\revision_1\concentradohogar_common_2018_2024.csv.gz |
| hogares.csv | 74647 | 89006 | 90102 | 91414 | 124 | data\interim\revision_1\hogares_common_2018_2024.csv.gz |
| ingresos.csv | 348487 | 394912 | 397182 | 391563 | 17 | data\interim\revision_1\ingresos_common_2018_2024.csv.gz |
| poblacion.csv | 269206 | 315743 | 309684 | 308598 | 163 | data\interim\revision_1\poblacion_common_2018_2024.csv.gz |
| trabajos.csv | 139933 | 164876 | 165006 | 164325 | 56 | data\interim\revision_1\trabajos_common_2018_2024.csv.gz |
| viviendas.csv | 73405 | 87754 | 88823 | 90324 | 60 | data\interim\revision_1\viviendas_common_2018_2024.csv.gz |

## 2. Codificacion de variables de interes

Las variables de interes se revisaron solo cuando existen dentro de las columnas comunes 2018-2024. La revision compara tipo y etiqueta en `docs/enigh_variable_metadata.csv`, y tambien los codigos observados por año para variables categoricas.

Variables con alerta de metadata disponible:

| tabla | variable | mismo_tipo | misma_etiqueta | tipos |
| --- | --- | --- | --- | --- |
| poblacion.csv | nivel | False | True | C (1)\|C (2) |
| poblacion.csv | nivelaprob | False | True | C (1)\|C (2) |
| trabajos.csv | trapais | True | False | C (1) |
| trabajos.csv | pago | True | False | C (1) |
| concentradohogar.csv | est_dis | False | True | C (3)\|C (7) |
| concentradohogar.csv | upm | False | True | C (5)\|C (7) |
| concentradohogar.csv | edad_jefe | False | True | N (2)\|N (3) |
| concentradohogar.csv | smg | False | True | N (6,2)\|N (8,2) |
| viviendas.csv | renta | False | True | N (6)\|N (9) |

Cambios estructurales a cuidar antes de modelar: `poblacion.csv` cambio variables de discapacidad entre 2018 y los años posteriores; `ingresos.csv`, `poblacion.csv` y `trabajos.csv` incorporan `entidad`, `est_dis`, `upm` y `factor` desde 2022; y en 2024 hay renombres en variables de salud, hogares y vivienda. Por eso el apilado usa columnas comunes despues de aplicar solo las homologaciones validadas.

## 3. Valores faltantes

La revision de faltantes se recalculo despues de homologar 2024 y de aplicar limpieza minima de cadenas vacias/espacios. Los codigos validos de no aplica, no especificado o saltos de cuestionario no se reclasificaron todavia como faltantes si el diccionario no lo confirma.

| tabla | faltantes globales 2024 | variables 2024 con mayor alerta |
| --- | ---: | --- |
| concentradohogar.csv | 0.00% | Sin faltantes en columnas comunes homologadas |
| hogares.csv | 29.52% | `nr_viv` 100.00%, `anio_canoa` 99.83%, `anio_carret` 99.80%, `anio_otro` 99.75% |
| ingresos.csv | 0.00% | Sin faltantes en columnas comunes homologadas |
| poblacion.csv | 59.42% | `norecib_10`, `razon_2`, `norecib_6`, `norecib_7` y otras variables de salud con 100.00% |
| trabajos.csv | 53.69% | `medtrab_5` 99.96%, `no_ing` 99.90%, `medtrab_4` 99.70%, `pres_19` 99.33% |
| viviendas.csv | 9.36% | `num_dueno2` 96.53%, `hog_dueno2` 96.53%, `antigua_ne` 86.41%, `viv_usada` 80.23% |

Conclusion operativa sobre 2024: habia perdida de informacion por nombres no homologados en variables especificas, y ya fue corregida. Los faltantes extremos que permanecen no se deben al `concat`, `reindex` o apilado, sino a columnas que en la fuente 2024 vienen vacias o casi vacias, o a universos condicionados que deben verificarse con catalogo antes de usarse longitudinalmente.

## 4. Resumen descriptivo

Resumen acotado de variables centrales para el primer avance. `ing_tri` resume importes por clave en `ingresos.csv`; el ingreso laboral comparable a nivel hogar se revisa con `ingtrab` en `concentradohogar.csv`.

| indicador | year | n_valid | mean | p25 | median | p75 | max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Edad de integrantes | 2018 | 269206 | 31.53 | 14.00 | 28.00 | 47.00 | 110.00 |
| Edad de integrantes | 2020 | 315743 | 32.78 | 15.00 | 30.00 | 49.00 | 110.00 |
| Edad de integrantes | 2022 | 309684 | 33.27 | 15.00 | 30.00 | 50.00 | 109.00 |
| Edad de integrantes | 2024 | 308598 | 33.88 | 15.00 | 32.00 | 50.00 | 106.00 |
| Horas trabajadas | 2018 | 139933 | 40.93 | 25.00 | 45.00 | 50.00 | 168.00 |
| Horas trabajadas | 2020 | 164876 | 39.58 | 24.00 | 42.00 | 50.00 | 168.00 |
| Horas trabajadas | 2022 | 165006 | 41.11 | 28.00 | 45.00 | 50.00 | 168.00 |
| Horas trabajadas | 2024 | 164325 | 40.44 | 28.00 | 43.00 | 48.00 | 168.00 |
| Ingreso corriente trimestral del hogar | 2018 | 74647 | 46,043.88 | 20,345.39 | 33,573.48 | 55,196.46 | 4,501,830.28 |
| Ingreso corriente trimestral del hogar | 2020 | 89006 | 47,838.49 | 21,391.95 | 35,172.01 | 57,640.04 | 10,702,107.40 |
| Ingreso corriente trimestral del hogar | 2022 | 90102 | 61,489.96 | 28,385.69 | 46,073.68 | 74,343.65 | 7,153,770.46 |
| Ingreso corriente trimestral del hogar | 2024 | 91414 | 72,273.59 | 34,520.87 | 55,666.18 | 88,840.73 | 17,431,977.54 |
| Ingreso trimestral por trabajo del hogar | 2018 | 74647 | 30,839.53 | 9,387.29 | 22,293.42 | 40,940.19 | 1,841,188.51 |
| Ingreso trimestral por trabajo del hogar | 2020 | 89006 | 30,728.75 | 8,200.38 | 22,131.14 | 41,365.22 | 3,950,804.34 |
| Ingreso trimestral por trabajo del hogar | 2022 | 90102 | 40,359.54 | 12,170.67 | 29,899.11 | 54,327.95 | 5,891,913.57 |
| Ingreso trimestral por trabajo del hogar | 2024 | 91414 | 47,446.01 | 14,582.93 | 36,410.86 | 65,009.62 | 2,347,826.08 |
| Integrantes del hogar | 2018 | 74647 | 3.60 | 2.00 | 3.00 | 5.00 | 22.00 |
| Integrantes del hogar | 2020 | 89006 | 3.55 | 2.00 | 3.00 | 5.00 | 25.00 |
| Integrantes del hogar | 2022 | 90102 | 3.44 | 2.00 | 3.00 | 4.00 | 19.00 |
| Integrantes del hogar | 2024 | 91414 | 3.37 | 2.00 | 3.00 | 4.00 | 20.00 |
| Ingreso trimestral por clave | 2018 | 348487 | 8,681.05 | 880.43 | 2,459.01 | 10,760.86 | 16,906,077.34 |
| Ingreso trimestral por clave | 2020 | 394912 | 9,448.52 | 989.01 | 3,239.99 | 11,739.13 | 10,688,918.47 |
| Ingreso trimestral por clave | 2022 | 397182 | 12,233.88 | 1,439.26 | 4,891.30 | 15,513.81 | 6,854,754.09 |
| Ingreso trimestral por clave | 2024 | 391563 | 14,646.97 | 1,760.86 | 5,901.63 | 19,918.03 | 14,673,913.04 |

# Exploratory Data Analysis

## Resumen de revisión longitudinal

Después de homologar los cambios de nomenclatura entre levantamientos, me quedé con 544 variables que puedo comparar entre 2018, 2020, 2022 y 2024. Para llegar a ese conjunto conservé únicamente columnas presentes en los cuatro años después de aplicar mappings validados, por ejemplo `aten_hosp` a `hospital`, `anio_carre` a `anio_carret`, `num_carre` a `num_carret`, `anio_pick` a `anio_pickup`, `num_pick` a `num_pickup`, `combus` a `combustible` y `medid_luz` a `medidor_luz`.

### Variables que puedo comparar en los cuatro años

| Tabla | Variables comparables en los 4 años | Número |
| --- | --- | ---: |
| concentradohogar | Lista completa debajo | 124 |
| hogares | Lista completa debajo | 124 |
| ingresos | `folioviv`, `foliohog`, `numren`, `clave`, `mes_1`, `mes_2`, `mes_3`, `mes_4`, `mes_5`, `mes_6`, `ing_1`, `ing_2`, `ing_3`, `ing_4`, `ing_5`, `ing_6`, `ing_tri` | 17 |
| poblacion | Lista completa debajo | 163 |
| trabajos | Lista completa debajo | 56 |
| viviendas | Lista completa debajo | 60 |
| **Total** |  | **544** |

**Lista completa por tabla**

`concentradohogar` (124): `folioviv`, `foliohog`, `ubica_geo`, `tam_loc`, `est_socio`, `est_dis`, `upm`, `factor`, `clase_hog`, `sexo_jefe`, `edad_jefe`, `educa_jefe`, `tot_integ`, `hombres`, `mujeres`, `mayores`, `menores`, `p12_64`, `p65mas`, `ocupados`, `percep_ing`, `perc_ocupa`, `ing_cor`, `ingtrab`, `trabajo`, `sueldos`, `horas_extr`, `comisiones`, `aguinaldo`, `indemtrab`, `otra_rem`, `remu_espec`, `negocio`, `noagrop`, `industria`, `comercio`, `servicios`, `agrope`, `agricolas`, `pecuarios`, `reproducc`, `pesca`, `otros_trab`, `rentas`, `utilidad`, `arrenda`, `transfer`, `jubilacion`, `becas`, `donativos`, `remesas`, `bene_gob`, `transf_hog`, `trans_inst`, `estim_alqu`, `otros_ing`, `gasto_mon`, `alimentos`, `ali_dentro`, `cereales`, `carnes`, `pescado`, `leche`, `huevo`, `aceites`, `tuberculo`, `verduras`, `frutas`, `azucar`, `cafe`, `especias`, `otros_alim`, `bebidas`, `ali_fuera`, `tabaco`, `vesti_calz`, `vestido`, `calzado`, `vivienda`, `alquiler`, `pred_cons`, `agua`, `energia`, `limpieza`, `cuidados`, `utensilios`, `enseres`, `salud`, `hospital`, `transporte`, `publico`, `foraneo`, `adqui_vehi`, `mantenim`, `refaccion`, `combus`, `comunica`, `educa_espa`, `educacion`, `esparci`, `paq_turist`, `personales`, `cuida_pers`, `acces_pers`, `otros_gas`, `transf_gas`, `percep_tot`, `retiro_inv`, `prestamos`, `otras_perc`, `ero_nm_viv`, `ero_nm_hog`, `erogac_tot`, `cuota_viv`, `mater_serv`, `material`, `servicio`, `deposito`, `prest_terc`, `pago_tarje`, `deudas`, `balance`, `otras_erog`, `smg`.

`hogares` (124): `folioviv`, `foliohog`, `huespedes`, `huesp_come`, `num_trab_d`, `trab_come`, `acc_alim1`, `acc_alim2`, `acc_alim3`, `acc_alim4`, `acc_alim5`, `acc_alim6`, `acc_alim7`, `acc_alim8`, `acc_alim9`, `acc_alim10`, `acc_alim11`, `acc_alim12`, `acc_alim13`, `acc_alim14`, `acc_alim15`, `acc_alim16`, `alim17_1`, `alim17_2`, `alim17_3`, `alim17_4`, `alim17_5`, `alim17_6`, `alim17_7`, `alim17_8`, `alim17_9`, `alim17_10`, `alim17_11`, `alim17_12`, `acc_alim18`, `telefono`, `celular`, `tv_paga`, `conex_inte`, `num_auto`, `anio_auto`, `num_van`, `anio_van`, `num_pickup`, `anio_pickup`, `num_moto`, `anio_moto`, `num_bici`, `anio_bici`, `num_trici`, `anio_trici`, `num_carret`, `anio_carret`, `num_canoa`, `anio_canoa`, `num_otro`, `anio_otro`, `num_ester`, `anio_ester`, `num_radio`, `anio_radio`, `num_tva`, `anio_tva`, `num_tvd`, `anio_tvd`, `num_dvd`, `anio_dvd`, `num_licua`, `anio_licua`, `num_tosta`, `anio_tosta`, `num_micro`, `anio_micro`, `num_refri`, `anio_refri`, `num_estuf`, `anio_estuf`, `num_lavad`, `anio_lavad`, `num_planc`, `anio_planc`, `num_maqui`, `anio_maqui`, `num_venti`, `anio_venti`, `num_aspir`, `anio_aspir`, `num_compu`, `anio_compu`, `num_impre`, `anio_impre`, `num_juego`, `anio_juego`, `tsalud1_h`, `tsalud1_m`, `habito_1`, `habito_2`, `habito_3`, `habito_4`, `habito_5`, `habito_6`, `consumo`, `nr_viv`, `tarjeta`, `pagotarjet`, `regalotar`, `regalodado`, `autocons`, `regalos`, `remunera`, `transferen`, `parto_g`, `negcua`, `est_alim`, `est_trans`, `bene_licon`, `cond_licon`, `lts_licon`, `otros_lts`, `diconsa`, `frec_dicon`, `cond_dicon`, `pago_dicon`, `otro_pago`.

`poblacion` (163): `folioviv`, `foliohog`, `numren`, `parentesco`, `sexo`, `edad`, `madre_hog`, `madre_id`, `padre_hog`, `padre_id`, `hablaind`, `lenguaind`, `hablaesp`, `comprenind`, `etnia`, `alfabetism`, `asis_esc`, `nivel`, `grado`, `tipoesc`, `tiene_b`, `otorg_b`, `forma_b`, `tiene_c`, `otorg_c`, `forma_c`, `nivelaprob`, `gradoaprob`, `antec_esc`, `residencia`, `edo_conyug`, `pareja_hog`, `conyuge_id`, `segsoc`, `ss_aa`, `ss_mm`, `redsoc_1`, `redsoc_2`, `redsoc_3`, `redsoc_4`, `redsoc_5`, `redsoc_6`, `hor_1`, `min_1`, `usotiempo1`, `hor_2`, `min_2`, `usotiempo2`, `hor_3`, `min_3`, `usotiempo3`, `hor_4`, `min_4`, `usotiempo4`, `hor_5`, `min_5`, `usotiempo5`, `hor_6`, `min_6`, `usotiempo6`, `hor_7`, `min_7`, `usotiempo7`, `hor_8`, `min_8`, `usotiempo8`, `atemed`, `inst_1`, `inst_2`, `inst_3`, `inst_4`, `inst_5`, `inst_6`, `inscr_1`, `inscr_2`, `inscr_3`, `inscr_4`, `inscr_5`, `inscr_6`, `inscr_7`, `inscr_8`, `prob_anio`, `prob_mes`, `prob_sal`, `aten_sal`, `servmed_1`, `servmed_2`, `servmed_3`, `servmed_4`, `servmed_5`, `servmed_6`, `servmed_7`, `servmed_8`, `servmed_9`, `servmed_10`, `servmed_11`, `hh_lug`, `mm_lug`, `hh_esp`, `mm_esp`, `pagoaten_1`, `pagoaten_2`, `pagoaten_3`, `pagoaten_4`, `pagoaten_5`, `pagoaten_6`, `pagoaten_7`, `noatenc_1`, `noatenc_2`, `noatenc_3`, `noatenc_4`, `noatenc_5`, `noatenc_6`, `noatenc_7`, `noatenc_8`, `noatenc_9`, `noatenc_10`, `noatenc_11`, `noatenc_12`, `noatenc_13`, `noatenc_14`, `noatenc_15`, `noatenc_16`, `norecib_1`, `norecib_2`, `norecib_3`, `norecib_4`, `norecib_5`, `norecib_6`, `norecib_7`, `norecib_8`, `norecib_9`, `norecib_10`, `norecib_11`, `razon_1`, `razon_2`, `razon_3`, `razon_4`, `razon_5`, `razon_6`, `razon_7`, `razon_8`, `razon_9`, `razon_10`, `razon_11`, `diabetes`, `pres_alta`, `peso`, `segvol_1`, `segvol_2`, `segvol_3`, `segvol_4`, `segvol_5`, `segvol_6`, `segvol_7`, `hijos_viv`, `hijos_mue`, `hijos_sob`, `trabajo_mp`, `motivo_aus`, `act_pnea1`, `act_pnea2`, `num_trabaj`.

`trabajos` (56): `folioviv`, `foliohog`, `numren`, `id_trabajo`, `trapais`, `subor`, `indep`, `personal`, `pago`, `contrato`, `tipocontr`, `pres_1`, `pres_2`, `pres_3`, `pres_4`, `pres_5`, `pres_6`, `pres_7`, `pres_8`, `pres_9`, `pres_10`, `pres_11`, `pres_12`, `pres_13`, `pres_14`, `pres_15`, `pres_16`, `pres_17`, `pres_18`, `pres_19`, `pres_20`, `htrab`, `sinco`, `scian`, `clas_emp`, `tam_emp`, `no_ing`, `tiene_suel`, `tipoact`, `socios`, `soc_nr1`, `soc_nr2`, `soc_resp`, `otra_act`, `tipoact2`, `tipoact3`, `tipoact4`, `lugar`, `conf_pers`, `medtrab_1`, `medtrab_2`, `medtrab_3`, `medtrab_4`, `medtrab_5`, `medtrab_6`, `medtrab_7`.

`viviendas` (60): `folioviv`, `tipo_viv`, `mat_pared`, `mat_techos`, `mat_pisos`, `antiguedad`, `antigua_ne`, `cocina`, `cocina_dor`, `cuart_dorm`, `num_cuarto`, `dotac_agua`, `excusado`, `uso_compar`, `sanit_agua`, `biodigest`, `bano_comp`, `bano_excus`, `bano_regad`, `drenaje`, `disp_elect`, `focos_ahor`, `combustible`, `eli_basura`, `tenencia`, `renta`, `estim_pago`, `pago_viv`, `pago_mesp`, `tipo_adqui`, `viv_usada`, `num_dueno1`, `hog_dueno1`, `num_dueno2`, `hog_dueno2`, `escrituras`, `lavadero`, `fregadero`, `regadera`, `tinaco_azo`, `cisterna`, `pileta`, `calent_sol`, `calent_gas`, `medidor_luz`, `bomba_agua`, `tanque_gas`, `aire_acond`, `calefacc`, `tot_resid`, `tot_hom`, `tot_muj`, `tot_hog`, `ubica_geo`, `tam_loc`, `est_socio`, `est_dis`, `upm`, `factor`, `procaptar`.

Al comparar los cuatro años, la mayor parte del conjunto comparable proviene de `poblacion`, `concentradohogar` y `hogares`. `ingresos` tiene menos columnas comparables, pero mantiene variables centrales para montos mensuales y trimestrales. Estas variables me permiten construir un primer análisis longitudinal sin mezclar cambios reales con cambios de cuestionario o de nomenclatura.

### Distribución de valores faltantes

Calculé los faltantes únicamente sobre las 544 variables comparables. Cuando miro el total apilado 2018-2024, más de la mitad de las variables no tiene faltantes y no encuentro variables por arriba de 50% de faltantes acumulados.

| Rango de faltantes | Número de variables | % de variables |
| --- | ---: | ---: |
| 0% | 306 | 56.25% |
| >0-5% | 26 | 4.78% |
| >5-20% | 72 | 13.24% |
| >20-50% | 140 | 25.74% |
| >50-90% | 0 | 0.00% |
| >90% | 0 | 0.00% |

Las variables que me quedan con mayor porcentaje de faltantes dentro del conjunto longitudinal son:

| Tabla | Variable | % faltantes 2018-2024 |
| --- | --- | ---: |
| hogares | `nr_viv` | 26.48% |
| hogares | `anio_canoa` | 26.44% |
| hogares | `anio_carret` | 26.43% |
| hogares | `anio_otro` | 26.42% |
| hogares | `anio_trici` | 26.17% |
| hogares | `habito_6` | 25.95% |
| trabajos | `medtrab_5` | 25.90% |
| trabajos | `no_ing` | 25.89% |
| trabajos | `medtrab_4` | 25.83% |
| trabajos | `pres_19` | 25.74% |
| trabajos | `medtrab_6` | 25.69% |
| trabajos | `medtrab_3` | 25.67% |
| poblacion | `razon_2` | 25.65% |
| poblacion | `norecib_10` | 25.65% |
| poblacion | `norecib_6` | 25.65% |

También comparé los faltantes por levantamiento para revisar si algún año queda sistemáticamente más incompleto:

| Año | Celdas comparables evaluadas | % faltantes |
| --- | ---: | ---: |
| 2018 | 80,557,861 | 0.00% |
| 2020 | 94,751,397 | 0.00% |
| 2022 | 94,145,598 | 0.00% |
| 2024 | 94,250,357 | 41.05% |

Después de la homologación, recuperé información 2024 que antes quedaba artificialmente vacía. Aun así, 2024 sigue concentrando faltantes en variables específicas, sobre todo de salud, apoyos, medios de trabajo, bienes del hogar y algunas condiciones de vivienda. Para este análisis decidí conservar esas variables dentro del inventario longitudinal, pero las marco como variables que requieren revisión de universo y tratamiento antes de modelar.

### Variables que dejo fuera del conjunto longitudinal

Para distinguir variables realmente comparables de variables disponibles solo en algunos levantamientos, comparé la unión de columnas de cada tabla después de aplicar los mappings validados. En total consideré 667 variables tabla-columna; de ellas conservé 544 y dejé fuera 123 por no cumplir presencia conceptual en los cuatro años.

| Tabla | Variables totales consideradas | Comparables 4 años | Excluidas |
| --- | ---: | ---: | ---: |
| concentradohogar | 128 | 124 | 4 |
| hogares | 161 | 124 | 37 |
| ingresos | 21 | 17 | 4 |
| poblacion | 211 | 163 | 48 |
| trabajos | 60 | 56 | 4 |
| viviendas | 86 | 60 | 26 |
| **Total** | **667** | **544** | **123** |

Clasifiqué las variables excluidas con estos patrones de disponibilidad:

| Patrón de disponibilidad | Número de variables |
| --- | ---: |
| Solo 2024 | 52 |
| 2018-2020-2022, no 2024 | 19 |
| 2022-2024 | 16 |
| Solo 2018 | 15 |
| 2020-2022 | 11 |
| 2020-2022-2024 | 10 |
| **Total** | **123** |

Variables excluidas más relevantes:

| Variable o grupo | Tabla | Años disponibles | Motivo de exclusión |
| --- | --- | --- | --- |
| `atenc_ambu` / `ambul_serv` | concentradohogar | 2018, 2020, 2022 / 2024 | No confirmé equivalencia perfecta por cambio de definición |
| `medicinas` / `medic_prod` | concentradohogar | 2018, 2020, 2022 / 2024 | No las homologué porque cambia de medicamentos sin receta a medicamentos y productos sanitarios |
| `anio_grab` / `anio_table` | hogares | 2018, 2020, 2022 / 2024 | No las homologué porque radiograbadora y tablet no representan el mismo bien |
| `er_otro` / `f_otro` | hogares | 2018, 2020, 2022 / 2024 | No las homologué porque radio por otro medio y afectación climática no son equivalentes |
| `focos_inca` / `focos` | viviendas | 2018, 2020, 2022 / 2024 | No las homologué porque focos incandescentes y total de focos no miden lo mismo |
| `estufa_chi` / `fogon_chi` | viviendas | 2018, 2020, 2022 / 2024 | Necesito catálogo antes de homologar porque la definición parece ampliarse |
| `entidad`, `est_dis`, `upm`, `factor` | hogares, ingresos, poblacion, trabajos | 2022, 2024 | No las puedo comparar en cuatro años porque entran a esas tablas desde 2022 |
| `disc1`-`disc7`, `causa1`-`causa7`, `segpop` | poblacion | 2018 | Las dejo fuera porque pertenecen a la estructura de discapacidad/salud de 2018 |
| `disc_acti`, `disc_apren`, `disc_brazo`, `disc_camin`, `disc_habla`, `disc_oir`, `disc_ver`, `disc_vest` | poblacion | 2020, 2022, 2024 | Las dejo fuera porque no aparecen en 2018 |
| `af_*`, `f_*`, `camb_clim` | hogares | 2024 | Las dejo fuera del longitudinal porque aparecen como variables nuevas en 2024 |
| `anio_lap`, `num_lap` | hogares | 2024 | Las dejo fuera del longitudinal porque aparecen como bienes nuevos en 2024 |

No cuento como excluidas las variables que recuperé mediante equivalencia validada. Por ejemplo, `hospital`, `anio_carret`, `num_carret`, `anio_pickup`, `num_pickup`, `combustible` y `medidor_luz` sí forman parte del conjunto longitudinal final porque confirmé su correspondencia antes de apilar.

### Interpretación general

Para mantener comparabilidad entre levantamientos, decidí concentrar el análisis longitudinal en las 544 variables presentes y conceptualmente equivalentes en 2018, 2020, 2022 y 2024. Esta decisión reduce el universo inicial de columnas, pero me ayuda a evitar que un cambio de nombre o una modificación del cuestionario parezca un cambio sustantivo en el tiempo.

Considero que el conjunto final queda razonablemente completo cuando lo miro de forma acumulada: 61.03% de las variables tiene entre 0% y 5% de faltantes, y ninguna supera 50% de faltantes en el total apilado. El punto que debo cuidar es 2024, porque concentra faltantes en varias variables aun después de recuperar los renombres validados.

Al exigir presencia en los cuatro años dejo fuera 123 variables. Esa pérdida no significa que deba eliminarlas del proyecto: algunas pueden servir para análisis transversales, diagnósticos de años específicos, modelos posteriores o como variables auxiliares si justifico claramente su alcance temporal.

En las siguientes etapas voy a usar este conjunto comparable como base del análisis longitudinal y voy a tratar por separado las variables excluidas o con faltantes altos. Con esto puedo avanzar sin perder de vista qué parte de la información es estrictamente comparable y qué parte depende de cambios en el levantamiento.

## Comportamiento individual

- Las variables monetarias (`ing_cor`, `ingtrab`, `trabajo`, `sueldos`, `negocio`, `gasto_mon`, `ing_tri`) tienen colas derechas largas. Para describirlas conviene priorizar mediana, P75, P95 y P99 sobre la media.
- `negocio` tiene muchos ceros, consistente con hogares sin ingreso por negocio en el agregado.
- `htrab` se concentra alrededor de jornadas semanales comunes, pero conserva valores altos que deben revisarse como jornadas multiples, codificacion o extremos validos.
- Variables de tamaño de hogar y vivienda (`tot_integ`, `tot_resid`, `num_cuarto`) se concentran en rangos bajos con colas superiores moderadas.
- En categoricas, `est_socio`, `tam_loc`, `educa_jefe`, `sexo_jefe`, `clase_hog`, variables de empleo y condiciones de vivienda muestran distribuciones suficientemente informativas para analisis descriptivo, pero aun falta mapear codigos a etiquetas oficiales.

## Evolucion 2018-2024

- Los ingresos nominales aumentan entre 2018 y 2024; esto no debe interpretarse como aumento real hasta deflactar.
- La mediana de `ingtrab` pasa de 22,293.42 en 2018 a 22,131.14 en 2020, 29,899.11 en 2022 y 36,410.86 en 2024.
- El P99 de `ingtrab` sube de 160,179.13 en 2018 a 226,078.44 en 2024, lo que confirma colas derechas importantes.
- El tamaño promedio del hogar baja gradualmente: `tot_integ` pasa de 3.60 en 2018 a 3.37 en 2024.
- La edad mediana de integrantes y de jefatura aumenta ligeramente durante el periodo.

## Ingresos

La variable objetivo principal para esta etapa es `concentradohogar.ingtrab`, ingreso trimestral por trabajo del hogar. Se usa porque ya esta agregada a nivel hogar y se mantiene comparable dentro de `concentradohogar`.

`ingresos.ing_tri` tambien es relevante, pero esta a nivel persona-clave de ingreso; no se usa para correlaciones hogar sin construir antes una agregacion documentada y sin hacer joins incorrectos. `ingtrab` no presenta faltantes ni valores negativos en el apilado revisado. Los ceros deben conservarse porque representan hogares sin ingreso laboral reportado en ese agregado.

## Relacion con ingresos

Principales asociaciones numericas con `ingtrab` en `concentradohogar`:

| variable | Pearson | Spearman | n |
| --- | ---: | ---: | ---: |
| `trabajo` | 0.877 | 0.883 | 345,169 |
| `sueldos` | 0.835 | 0.861 | 345,169 |
| `ing_cor` | 0.630 | 0.755 | 345,169 |
| `aguinaldo` | 0.548 | 0.642 | 345,169 |
| `gasto_mon` | 0.549 | 0.607 | 345,169 |
| `perc_ocupa` | 0.391 | 0.585 | 345,169 |
| `ocupados` | 0.371 | 0.559 | 345,169 |
| `transporte` | 0.354 | 0.552 | 345,169 |

Las correlaciones mas altas son esperables porque varias variables son componentes o agregados cercanos al ingreso laboral. Esto sirve para detectar redundancia y multicolinealidad, no para seleccionar variables de forma definitiva.

La asociacion por año es bastante estable en las variables mas cercanas al ingreso:

| variable | 2018 | 2020 | 2022 | 2024 |
| --- | ---: | ---: | ---: | ---: |
| `trabajo` | 0.883 | 0.883 | 0.878 | 0.887 |
| `sueldos` | 0.857 | 0.861 | 0.855 | 0.864 |
| `ing_cor` | 0.781 | 0.743 | 0.751 | 0.752 |
| `gasto_mon` | 0.622 | 0.578 | 0.595 | 0.595 |
| `perc_ocupa` | 0.565 | 0.575 | 0.610 | 0.624 |

En categoricas, las diferencias descriptivas de mediana de `ingtrab` son claras en `est_socio`, `tam_loc`, `educa_jefe`, `sexo_jefe` y `clase_hog`. Por ejemplo, `est_socio` 4 tiene mediana de 50,869.56 contra 16,848.19 en `est_socio` 1; `tam_loc` 1 tiene 36,684.78 contra 20,152.17 en `tam_loc` 4; y `sexo_jefe` 1 tiene 29,501.46 contra 21,639.32 en `sexo_jefe` 2. Estas diferencias son descriptivas y requieren etiquetas oficiales antes de interpretarse sustantivamente.

## Relaciones multivariadas preliminares

- El pairplot del notebook usa una muestra reproducible y variables numericas relevantes: `ingtrab`, `log1p_ingtrab`, `ing_cor`, `gasto_mon`, `sueldos`, `ocupados`, `tot_integ` y `edad_jefe`.
- La transformacion visual `log1p(ingtrab)` ayuda a observar la masa central y relaciones no lineales, pero no reemplaza la variable original.
- Hay redundancia conceptual y estadistica entre `ingtrab`, `trabajo`, `sueldos` e `ing_cor`; en modelos posteriores conviene no mezclar agregados y componentes sin justificacion.

## Implicaciones para siguientes etapas

- Deflactar ingresos antes de comparar niveles reales entre 2018, 2020, 2022 y 2024.
- Etiquetar variables categoricas con catalogos oficiales para interpretar escolaridad, localidad, estrato, empleo y vivienda.
- Construir una base analitica con joins documentados entre hogar, poblacion, trabajos e ingresos, respetando nivel de observacion.
- Definir ingreso laboral individual desde `ingresos.csv` solo si el analisis requiere nivel persona y despues de filtrar claves laborales.
- Mantener variables con baja correlacion individual si tienen justificacion teorica, posible no linealidad, interacciones o efectos condicionados.
- Revisar variables con faltantes extremos 2024 antes de usarlas longitudinalmente.
- Incorporar factores de expansion y diseno muestral para resultados descriptivos o inferenciales publicables.

# Documentación final en desarrollo

**Proyecto:** ENIGH, ingresos y territorio en México  
**Años:** 2018, 2020, 2022 y 2024  
**Estado:** documento vivo de trabajo para tesina

Este documento consolida las decisiones metodológicas ya tomadas en las revisiones 1 a 4, el estado del arte geográfico y los notebooks 04 a 08. Los archivos históricos en `reports/` se conservan como bitácora; de aquí en adelante este archivo funciona como referencia principal del proyecto.

## 1. Resumen del proyecto

El proyecto usa microdatos de la Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) para estudiar la distribución del ingreso en México entre 2018 y 2024. El énfasis actual está en construir bases analíticas interpretables, reproducibles y adecuadas para una tesina escolar, más que en montar una arquitectura operativa compleja.

La estrategia seguida ha sido:

- homologar variables comparables entre años;
- validar tipos, llaves y relaciones entre tablas;
- incorporar geografía segura a nivel entidad y municipio;
- decodificar variables categóricas prioritarias;
- construir bases analíticas de personas y hogares;
- documentar faltantes, ceros y universos aplicables;
- iniciar análisis territorial descriptivo con regiones Banxico, entidad, tamaño de localidad y estrato socioeconómico.

## 2. Pregunta de investigación

La pregunta refinada del proyecto es:

> ¿Cómo cambian los determinantes individuales, laborales, familiares y territoriales del ingreso en México entre 2018 y 2024, y en qué medida estas asociaciones son heterogéneas entre regiones, entidades, niveles de urbanización y estratos socioeconómicos?

Esta formulación evita limitar la tesina a comparar promedios o Gini por región, porque Banco de México ya tiene antecedentes directos sobre desigualdad regional con ENIGH.

## 3. Objetivo general

Analizar la relación entre características personales, laborales, del hogar y territoriales con el ingreso en México, usando microdatos ENIGH 2018, 2020, 2022 y 2024, con una base metodológica reproducible y documentada.

## 4. Objetivos específicos

- Construir bases analíticas comparables a nivel persona y hogar.
- Verificar que las variables centrales estén homologadas y decodificadas de forma comparable.
- Documentar faltantes, ceros y universos de aplicación antes de modelar.
- Explorar diferencias de ingreso por región Banxico, entidad, tamaño de localidad y estrato socioeconómico.
- Separar análisis de niveles de ingreso, desigualdad interna y brechas territoriales.
- Mantener explícitas las limitaciones de inferencia de la ENIGH.

## 5. Hipótesis de trabajo

Las hipótesis actuales son de asociación, no de causalidad:

- La asociación entre educación e ingreso cambia entre regiones Banxico.
- El estrato socioeconómico oficial de INEGI aporta información adicional sobre la distribución del ingreso.
- Las características laborales se asocian con ingresos de manera distinta entre contextos urbanos y rurales.
- Las asociaciones entre características individuales/laborales e ingreso no son completamente estables entre 2018 y 2024.
- Las variables territoriales pueden enriquecer el análisis, siempre que no se interprete el municipio como dominio representativo automático.

## 6. Fuente de datos

La fuente es ENIGH para los levantamientos 2018, 2020, 2022 y 2024, almacenados localmente en `data/raw/EINGH/`.

Los cuatro levantamientos se concatenan como cortes transversales independientes. No son panel: un hogar observado en 2018 y uno observado en 2024 no representan seguimiento de la misma unidad.

## 7. Estructura original de ENIGH y relaciones

El notebook `04_relaciones_entre_bases.ipynb` validó la estructura relacional:

| Tabla | Nivel | Llave | Relación |
| --- | --- | --- | --- |
| `viviendas` | vivienda | `folioviv` | 1:N hogares |
| `hogares` | hogar | `folioviv + foliohog` | N:1 vivienda; 1:N población |
| `concentradohogar` | hogar agregado | `folioviv + foliohog` | 1:1 hogares |
| `poblacion` | persona | `folioviv + foliohog + numren` | N:1 hogar |
| `trabajos` | trabajo | `folioviv + foliohog + numren + id_trabajo` | N:1 persona |
| `ingresos` | persona-clave ingreso | `folioviv + foliohog + numren + clave` | N:1 persona |

Todas las llaves propuestas tuvieron 0 duplicados por año y las unidades hijas tuvieron padre en las relaciones revisadas.

Una regla metodológica importante es no hacer merges directos `poblacion -> trabajos -> ingresos` sin agregación previa, porque `trabajos` e `ingresos` son tablas 1:N respecto a persona.

## 8. Bases analíticas o marts

Se construyeron dos bases analíticas en `data/interim/revision_4/`:

| Base | Archivo | Unidad | Filas | Columnas | Llave |
| --- | --- | --- | ---: | ---: | --- |
| Personas | `mart_persona_2018_2024.csv.gz` | persona-año | 1,203,231 | 140 | `anio + folioviv + foliohog + numren` |
| Hogares | `mart_hogar_2018_2024.csv.gz` | hogar-año | 345,169 | 92 | `anio + folioviv + foliohog` |

`mart` significa base analítica preparada para análisis a una granularidad específica. En la documentación visible se usa también "base analítica de personas" y "base analítica de hogares".

## 9. Limpieza y homologación

Los avances principales fueron:

- homologación de columnas comparables entre 2018, 2020, 2022 y 2024;
- corrección de inconsistencias específicas de 2024;
- limpieza mínima de cadenas vacías y espacios;
- validación de tipos y eliminación de artefactos decimales en variables categóricas;
- incorporación de `region_banxico` y alias `factor`;
- normalización de `est_socio_desc` por código;
- corrección de `asis_esc_desc` por código oficial `asis_esc`.

No se modificó `data/raw/`. Las correcciones viven en las bases intermedias y en los notebooks que permiten reproducirlas.

## 10. Variables categóricas

El notebook 03 y la revisión 3 documentan la decodificación:

- variables con mapping extraído: 431;
- filas código-etiqueta extraídas: 4,406;
- variables decodificadas: 263;
- columnas `_desc` creadas: 263.

La prueba inicial confirmó mapeos para variables prioritarias como sexo, habla indígena, etnia, alfabetismo, asistencia escolar, nivel aprobado, estado conyugal, parentesco y residencia. Algunas variables de años de adquisición o conteos del hogar quedaron para revisión manual porque no conviene tratarlas como categóricas sustantivas sin validar su universo.

## 11. Geografía

La geografía se incorporó mediante `ubica_geo`, construida como clave entidad + municipio. Con esta llave se obtuvo cobertura de 100% en los cruces con `concentradohogar` y `viviendas`, incorporando:

- `cve_ent`;
- `entidad`;
- `cve_mun`;
- `municipio`.

No se incorporó localidad, latitud ni longitud, porque la llave validada identifica entidad y municipio, no una localidad exacta del hogar.

## 12. Estratificación territorial

Las clasificaciones territoriales actuales son:

- `region_banxico`: Norte, Centro Norte, Centro y Sur, construida desde `cve_ent`;
- `entidad`: nivel defendible para resultados ENIGH;
- `tam_loc_desc`: tamaño de localidad como aproximación oficial de urbanización/ruralidad;
- `est_socio_desc`: estrato socioeconómico oficial de INEGI;
- `municipio`: solo exploratorio/contextual, con cautela de representatividad.

No se creó una regionalización propia ni clustering territorial. La decisión actual es usar primero clasificaciones oficiales o institucionales.

## 13. Estado del arte

El documento `reports/estado_del_arte_geografia_ingresos_ENIGH.md` identifica tres referencias principales:

- INEGI: diseño muestral estratificado, tamaño de localidad, estrato socioeconómico, factor, `est_dis` y `upm`.
- Banco de México: regiones económicas y análisis regional de Gini/fuentes de ingreso con ENIGH.
- CONAPO: índices de marginación como posible enriquecimiento futuro.

Banco de México reporta Gini regional aproximado para 2018, 2020 y 2022. La tabla documentada usa valores en escala 0-100: Nacional 45.7, 45.0 y 43.1; Sur muestra la desigualdad más alta entre regiones. El recuadro metodológico indica que el benchmark usa ingreso corriente total promedio por hogar, por lo que la comparación del notebook 09 usa `ing_cor_hogar_oficial_tri`, no el ingreso per cápita.

## 14. Diferenciación del proyecto

El valor potencial de la tesina no está en repetir que hay diferencias regionales de ingreso o Gini. La aportación más defendible es estudiar:

```text
determinantes del ingreso
× territorio
× tiempo
```

Es decir: cómo cambian las asociaciones entre ingreso y educación, sexo, edad, características laborales, composición del hogar y estratos territoriales entre 2018 y 2024.

## 15. EDA y análisis regional hasta notebook 07

El notebook `07_analisis_regional_ingresos.ipynb` usa como target central `ingreso_persona_laboral_negocio_tri` y separa la submuestra con ingreso laboral positivo para evitar que las medianas queden dominadas por personas sin ingreso laboral.

Hallazgos descriptivos preliminares:

- personas con ingreso laboral positivo: 574,462, equivalentes a 47.7% de la base de personas;
- mediana trimestral de ingreso laboral: Norte $22,131 y Sur $11,739;
- ingreso corriente per cápita del hogar: Norte tiene mediana $16,713 y Sur $10,477;
- localidades de 100,000 o más habitantes tienen mediana laboral $22,500 frente a $13,011 en localidades menores de 2,500 habitantes;
- estrato Alto registra mediana laboral $33,359 y Bajo $10,125;
- hombres: $19,392; mujeres: $12,984;
- con contrato: $28,124; sin contrato: $14,478.

Estos resultados son descriptivos y nominales. No separan composición educativa, edad, sexo, ocupación, estructura del hogar ni inflación.

## 16. Calidad, faltantes y ceros hasta notebook 08

El notebook `08_calidad_bases_analiticas.ipynb` audita faltantes, ceros y universos aplicables. La documentación técnica detallada queda en `reports/calidad_faltantes_y_ceros.md`.

Conclusiones principales:

- las variables geográficas, estratos y diseño muestral prioritarias están completas;
- los targets monetarios principales no tienen faltantes;
- los faltantes grandes en variables laborales son estructurales por universo;
- `edo_conyug_desc` falta por edad 0-11 y queda completo en 12+;
- `nivelaprob_desc` falta principalmente en edades 0-5;
- `nivel_desc` no es escolaridad general, sino nivel educativo actual de quienes asisten a la escuela;
- los ceros de ingreso laboral se conservan como valores sustantivos/estructurales;
- no se imputa.

Correcciones cerradas antes de avanzar:

- `asis_esc_desc`: corregida por código oficial `asis_esc` (`1 = Sí`, `2 = No`).
- `personas_con_registros_ingreso`: 250 `NaN` validados contra `mart_persona` y convertidos a 0 porque no había registros individuales en `ingresos.csv`.

## 17. Poblaciones analíticas

| Universo | 2018 | 2020 | 2022 | 2024 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base completa de personas | 269,206 | 315,743 | 309,684 | 308,598 | 1,203,231 |
| Personas con trabajo reportado | 127,638 | 149,387 | 150,682 | 150,382 | 578,089 |
| Personas con ingreso laboral positivo | 127,846 | 148,082 | 149,569 | 148,965 | 574,462 |
| Hogares | 74,647 | 89,006 | 90,102 | 91,414 | 345,169 |

Para ingreso laboral se recomienda separar:

- probabilidad de tener ingreso laboral positivo;
- monto del ingreso condicionado a ingreso laboral positivo.

## 18. Diseño muestral

Las bases conservan:

- `factor`;
- `factor_hogar`;
- `est_dis`;
- `upm`.

La decisión actual es usar `factor` para descriptivos ponderados. Todavía no se implementa inferencia formal con diseño muestral complejo. Si el análisis avanza a intervalos de confianza o pruebas inferenciales, será necesario incorporar estratos y conglomerados de forma explícita.

## 19. Limitaciones actuales

- Los años son cortes transversales, no panel.
- Los ingresos entre años están en pesos nominales; no se ha deflactado.
- Los municipios se usan solo como contexto o exploración.
- No se incorporó marginación CONAPO en esta etapa.
- No se construyó una variable definitiva de formalidad laboral.
- Las asociaciones observadas no deben interpretarse como causalidad.
- Los agregados derivados desde `ingresos.csv` no sustituyen automáticamente las variables oficiales de `concentradohogar`.

## 20. Roadmap

Prioridad inmediata después del notebook 09:

- decidir si la siguiente comparación temporal debe deflactar ingresos;
- revisar formalidad laboral;
- evaluar enriquecimiento CONAPO;
- pasar de EDA a modelos descriptivos/explicativos con cautela metodológica;
- mantener separada la desigualdad interna de cada territorio de las brechas entre territorios.

Después:

- documentar cualquier cambio de universo antes de calcular nuevos indicadores.

## 21. Principios metodológicos

- No inventar resultados: todo valor reportado debe salir de notebooks o documentación revisada.
- No asumir causalidad desde asociaciones descriptivas.
- No usar municipios como dominios representativos sin revisión de diseño y muestra.
- No convertir faltantes a cero sin validar universo o llave.
- Separar ceros legítimos, ceros estructurales y códigos con valor 0.
- Priorizar interpretabilidad, visualización y reproducibilidad.
- Mantener documentación viva en este archivo y detalle técnico de calidad en `reports/calidad_faltantes_y_ceros.md`.

## 22. Notebook 09: desigualdad territorial

Se creó `notebooks/09_desigualdad_territorial.ipynb` para calcular desigualdad territorial con tablas y gráficas reproducibles.

Definición principal:

- ingreso: `ing_cor_hogar_oficial_tri`;
- ponderador: `factor`;
- universo: todos los hogares con ingreso no faltante, ingreso no negativo y factor positivo;
- ceros: se conservan;
- escala: Gini en 0-1 y 0-100;
- años comparables con Banxico: 2018, 2020 y 2022.

Gini nacional propio, en escala 0-100:

| Año | Gini |
| --- | ---: |
| 2018 | 43.83 |
| 2020 | 42.60 |
| 2022 | 41.27 |
| 2024 | 40.06 |

Validación contra Banxico:

- el patrón general coincide: la desigualdad baja entre 2018 y 2022;
- los valores propios quedan por debajo del benchmark Banxico;
- la mayor discrepancia es Sur 2020: -3.22 puntos;
- explicación plausible: Banco de México usa bases generadas por CONEVAL a partir de ENIGH, mientras este notebook usa el mart propio y la variable oficial de `concentradohogar`; pueden diferir definición CONEVAL, procesamiento, universo, ponderación, escala temporal del ingreso o redondeo.

Hallazgos territoriales 2024:

- región con mayor mediana de ingreso corriente del hogar: Norte, $75,412;
- región con menor mediana: Sur, $42,533;
- brecha de mediana Norte/Sur: 1.77 veces;
- brecha entre localidades de 100,000 o más habitantes y menores de 2,500 habitantes: 2.00 veces;
- brecha entre estrato Alto y Bajo: 3.28 veces.

CDMX:

- ingreso corriente del hogar, mediana 2024: $81,866;
- ingreso corriente per cápita del hogar, mediana 2024: $30,297;
- ingreso laboral individual positivo, mediana 2024: $28,678;
- los ingresos están en pesos nominales trimestrales.

Grandes urbes:

- no se encontró una delimitación metropolitana oficial incorporada al proyecto;
- no se aproximaron grandes urbes con municipios sueltos;
- se dejó como enriquecimiento futuro;
- por ahora se usan solo `tam_loc_desc` y `est_socio_desc` como dimensiones existentes, sin llamarlas zonas metropolitanas ni marginalidad.

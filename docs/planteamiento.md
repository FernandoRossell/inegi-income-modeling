# Planteamiento de la tesina

## Tema

Este trabajo tiene como propósito analizar los determinantes del ingreso laboral en México mediante el uso de microdatos de la Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) y fuentes complementarias de información pública, como los indicadores de desigualdad y desarrollo social publicados por CONEVAL.

El interés central es identificar qué características individuales, educativas, laborales, del hogar y del contexto territorial se asocian con diferencias en el ingreso laboral, así como analizar si la importancia de estos factores ha cambiado entre distintas regiones del país y a través del tiempo.

El proyecto prioriza la explicación sobre la predicción. Por ello, el análisis se centrará en modelos estadísticos interpretables que permitan cuantificar la relación entre el ingreso y sus principales determinantes.

---

# Problema de investigación

El ingreso laboral constituye una de las principales fuentes de bienestar económico de los hogares mexicanos; sin embargo, su distribución presenta diferencias importantes entre individuos con distintos niveles educativos, ocupaciones, condiciones laborales, características sociodemográficas y contextos regionales.

Durante las últimas décadas, México ha experimentado cambios económicos, demográficos y sociales que podrían haber modificado la importancia relativa de estos factores. Asimismo, existen diferencias persistentes entre entidades federativas y regiones en términos de desarrollo económico y desigualdad, por lo que resulta pertinente estudiar si los determinantes del ingreso permanecen estables o si varían dependiendo del contexto territorial y del periodo analizado.

Los microdatos de la ENIGH ofrecen una oportunidad para estudiar estas relaciones de manera rigurosa mediante herramientas estadísticas. No obstante, el reto consiste no solo en construir modelos con buena capacidad predictiva, sino en generar evidencia que permita interpretar cuáles variables explican en mayor medida las diferencias observadas en el ingreso laboral y cómo estas relaciones evolucionan en el tiempo y entre regiones del país.

---

# Pregunta de investigación

**¿Qué factores individuales, educativos, laborales, del hogar y territoriales explican las diferencias en el ingreso laboral de la población mexicana y cómo ha variado la importancia de estos factores entre distintas regiones del país y a través del tiempo?**

---

# Objetivo general

Analizar los determinantes del ingreso laboral en México mediante microdatos de la ENIGH correspondientes a distintos levantamientos, utilizando herramientas estadísticas interpretables para estimar la relación entre el ingreso laboral y un conjunto de características individuales, educativas, laborales y territoriales, así como estudiar la evolución regional de dichas relaciones y de indicadores de desigualdad como el índice de Gini.

---

# Objetivos específicos

* Describir la distribución del ingreso laboral y comparar su evolución entre distintos levantamientos de la ENIGH.

* Analizar las diferencias regionales del ingreso laboral e incorporar indicadores de desigualdad, como el índice de Gini, para contextualizar dichas diferencias.

* Construir variables explicativas relevantes a partir de los microdatos y de información contextual proveniente de fuentes oficiales.

* Estimar modelos estadísticos interpretables para cuantificar la asociación entre el ingreso laboral y variables individuales, educativas, laborales, del hogar y territoriales.

* Comparar la magnitud e importancia relativa de los determinantes del ingreso entre distintos años y regiones del país.

* Discutir las limitaciones del análisis, particularmente en relación con variables omitidas, sesgos de selección y las restricciones para realizar inferencia causal.

---

# Alcance

El trabajo se concentrará en explicar las diferencias observadas en el ingreso laboral y no únicamente en desarrollar un modelo con el mayor desempeño predictivo.

El estudio utilizará principalmente los levantamientos de la ENIGH correspondientes a **2018, 2020, 2022 y 2024**, lo que permitirá incorporar una dimensión temporal al análisis y evaluar si los determinantes del ingreso han cambiado antes, durante y después del periodo de la pandemia por COVID-19.

La interpretación causal dependerá de la estructura de los datos y de la estrategia empírica que resulte viable. En ausencia de un diseño causal explícito, los resultados se presentarán como asociaciones condicionadas por las variables observadas.

---

# Resultado esperado

Se espera obtener una caracterización estadísticamente sólida de los principales factores asociados al ingreso laboral en México, así como evidencia sobre la evolución de estas relaciones entre distintos periodos y regiones del país.

El trabajo incluirá análisis descriptivos, modelos estadísticos, indicadores de desigualdad, tablas y visualizaciones que permitan responder la pregunta de investigación con evidencia empírica, manteniendo una interpretación cuidadosa de los resultados y de sus limitaciones metodológicas.

---

# Observaciones metodológicas

Existen algunos aspectos del diseño del proyecto que considero importantes discutir antes de comenzar el análisis:

* Confirmar si la ENIGH constituye la fuente de información más adecuada para responder la pregunta de investigación o si conviene incorporar otras bases como la ENOE o los Censos de Población.
* Definir si la comparación temporal se realizará utilizando los levantamientos de la ENIGH de 2018, 2020, 2022 y 2024, o si conviene modificar el periodo de estudio.
* Determinar el nivel geográfico de análisis (entidad federativa, región o municipio), considerando la disponibilidad de información y la comparabilidad entre años.
* Evaluar la pertinencia de incorporar indicadores agregados, como el índice de Gini, el rezago social o la pobreza, provenientes de CONEVAL.
* Discutir si dichos indicadores deben utilizarse únicamente como elementos descriptivos para contextualizar los resultados o si resulta metodológicamente apropiado incorporarlos como variables explicativas.

---

# Relación de tablas disponibles por año

Los microdatos de la ENIGH se encuentran organizados en `data/raw/EINGH/` por año de levantamiento. Para cada año se conservaron los archivos CSV extraídos de las bases originales y el archivo PDF de documentación correspondiente.

## Resumen por levantamiento

| Año | Ruta | Tablas CSV disponibles | Documentación |
| --- | --- | ---: | --- |
| 2018 | `data/raw/EINGH/2018/` | 12 | `702825188061.pdf` |
| 2020 | `data/raw/EINGH/2020/` | 17 | `889463901242.pdf` |
| 2022 | `data/raw/EINGH/2022/` | 17 | `889463910626.pdf` |
| 2024 | `data/raw/EINGH/2024/` | 17 | `889463924494.pdf` |

## Tablas por año

| Tabla CSV | 2018 | 2020 | 2022 | 2024 |
| --- | :---: | :---: | :---: | :---: |
| `agro.csv` | Sí | Sí | Sí | Sí |
| `agroconsumo.csv` | No | Sí | Sí | Sí |
| `agrogasto.csv` | No | Sí | Sí | Sí |
| `agroproductos.csv` | No | Sí | Sí | Sí |
| `concentradohogar.csv` | Sí | Sí | Sí | Sí |
| `erogaciones.csv` | Sí | Sí | Sí | Sí |
| `gastoshogar.csv` | Sí | Sí | Sí | Sí |
| `gastospersona.csv` | Sí | Sí | Sí | Sí |
| `gastotarjetas.csv` | Sí | Sí | Sí | Sí |
| `hogares.csv` | Sí | Sí | Sí | Sí |
| `ingresos.csv` | Sí | Sí | Sí | Sí |
| `ingresos_jcf.csv` | No | Sí | Sí | Sí |
| `noagro.csv` | Sí | Sí | Sí | Sí |
| `noagroimportes.csv` | No | Sí | Sí | Sí |
| `poblacion.csv` | Sí | Sí | Sí | Sí |
| `trabajos.csv` | Sí | Sí | Sí | Sí |
| `viviendas.csv` | Sí | Sí | Sí | Sí |

## Documentación conservada

Los archivos PDF se mantienen junto a los CSV de cada levantamiento porque sirven como documentación metodológica y de estructura de datos. En particular, permiten consultar definiciones de variables, criterios de levantamiento, notas sobre comparabilidad y referencias necesarias para justificar decisiones de limpieza, unión de tablas y construcción de variables.

Para el análisis empírico, las tablas centrales serán `concentradohogar.csv`, `poblacion.csv`, `trabajos.csv` e `ingresos.csv`, ya que permiten vincular características del hogar, atributos individuales, condiciones laborales e ingresos. El resto de las tablas podrá utilizarse como información complementaria si resulta pertinente para el alcance final del modelo.

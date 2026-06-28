# Determinantes del ingreso laboral y evolución de la desigualdad regional en México: un análisis estadístico utilizando la ENIGH (2018–2024)

## Tema

Este trabajo tiene como propósito analizar los determinantes del ingreso laboral en México mediante el uso de microdatos de la Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) y fuentes complementarias de información pública, como los indicadores de desigualdad y desarrollo social publicados por CONEVAL.

El interés central es identificar qué características individuales, educativas, laborales, del hogar y del contexto territorial se asocian con diferencias en el ingreso laboral, así como analizar si la importancia de estos factores ha cambiado entre distintas regiones del país y a través del tiempo.

El proyecto prioriza la explicación sobre la predicción. Por ello, el análisis se centrará en modelos estadísticos interpretables que permitan cuantificar la relación entre el ingreso y sus principales determinantes.

---

# Justificación

Comprender los factores asociados al ingreso laboral resulta relevante tanto desde una perspectiva económica como de política pública. La evidencia obtenida puede contribuir a entender las desigualdades existentes entre distintos grupos poblacionales y regiones del país, así como identificar los factores que presentan mayor asociación con las brechas de ingreso.

Desde el punto de vista metodológico, el proyecto permitirá integrar herramientas de inferencia estadística, regresión multivariada, análisis de desigualdad y aprendizaje estadístico aplicadas a un problema real utilizando datos oficiales de cobertura nacional.

Asimismo, el estudio busca generar una metodología reproducible que pueda servir como base para futuras investigaciones relacionadas con desigualdad, mercado laboral y desarrollo regional en México.

---

# Problema de investigación

El ingreso laboral constituye una de las principales fuentes de bienestar económico de los hogares mexicanos; sin embargo, su distribución presenta diferencias importantes entre individuos con distintos niveles educativos, ocupaciones, condiciones laborales, características sociodemográficas y contextos regionales.

Durante las últimas décadas, México ha experimentado cambios económicos, demográficos y sociales que podrían haber modificado la importancia relativa de estos factores. Asimismo, existen diferencias persistentes entre entidades federativas y regiones en términos de desarrollo económico y desigualdad, por lo que resulta pertinente estudiar si los determinantes del ingreso permanecen estables o si varían dependiendo del contexto territorial y del periodo analizado.

Los microdatos de la ENIGH ofrecen una oportunidad para estudiar estas relaciones de manera rigurosa mediante herramientas estadísticas. No obstante, el reto consiste no solo en construir modelos con buena capacidad predictiva, sino en generar evidencia que permita interpretar cuáles variables explican en mayor medida las diferencias observadas en el ingreso laboral y cómo estas relaciones evolucionan en el tiempo y entre regiones del país.

---

# Pregunta de investigación

**¿Qué factores individuales, educativos, laborales, del hogar y territoriales explican las diferencias en el ingreso laboral de la población mexicana y cómo ha variado la importancia de estos factores entre distintas regiones del país y a través del tiempo?**

---

# Hipótesis

## Hipótesis general

Las características individuales, educativas, laborales y territoriales presentan una asociación significativa con el ingreso laboral de la población mexicana, y la importancia relativa de estos factores ha cambiado entre regiones y a través del tiempo.

## Hipótesis específicas

* **H1.** La escolaridad presenta una asociación positiva con el ingreso laboral.
* **H2.** Existen diferencias salariales por género aun después de controlar por variables observables como educación, edad, ocupación y experiencia laboral.
* **H3.** Las características económicas y sociales de la región de residencia contribuyen a explicar parte de la variabilidad del ingreso laboral.
* **H4.** La importancia relativa de los principales determinantes del ingreso ha cambiado entre los levantamientos de la ENIGH de 2018, 2020, 2022 y 2024.

---

# Objetivo general

Analizar los determinantes del ingreso laboral en México mediante microdatos de la ENIGH correspondientes a los levantamientos de 2018, 2020, 2022 y 2024, utilizando herramientas estadísticas interpretables para estimar la relación entre el ingreso laboral y un conjunto de características individuales, educativas, laborales y territoriales, así como estudiar la evolución regional de dichas relaciones.

---

# Objetivos específicos

* Describir la distribución del ingreso laboral y comparar su evolución entre distintos levantamientos de la ENIGH.
* Analizar las diferencias regionales del ingreso laboral.
* Evaluar la pertinencia de incorporar indicadores agregados de desigualdad, como el índice de Gini, para contextualizar las diferencias regionales.
* Construir variables explicativas relevantes a partir de los microdatos y de información contextual proveniente de fuentes oficiales.
* Estimar modelos estadísticos interpretables para cuantificar la asociación entre el ingreso laboral y variables individuales, educativas, laborales, del hogar y territoriales.
* Comparar la magnitud e importancia relativa de los determinantes del ingreso entre distintos años y regiones del país.
* Discutir las limitaciones del análisis, particularmente en relación con variables omitidas, sesgos de selección y las restricciones para realizar inferencia causal.

---

# Alcance

El trabajo se concentrará en explicar las diferencias observadas en el ingreso laboral y no únicamente en desarrollar un modelo con el mayor desempeño predictivo.

El estudio utilizará principalmente los levantamientos de la ENIGH correspondientes a **2018, 2020, 2022 y 2024**, lo que permitirá incorporar una dimensión temporal al análisis y evaluar si los determinantes del ingreso han cambiado antes, durante y después del periodo asociado a la pandemia por COVID-19.

Los indicadores agregados de desigualdad y desarrollo social se incorporarán únicamente cuando exista una justificación metodológica clara y su nivel de agregación sea consistente con el análisis realizado.

La interpretación causal dependerá de la estructura de los datos y de la estrategia empírica que resulte viable. En ausencia de un diseño causal explícito, los resultados se presentarán como asociaciones condicionadas por las variables observadas.

---

# Resultado esperado

Se espera obtener una caracterización estadísticamente sólida de los principales factores asociados al ingreso laboral en México, así como evidencia sobre la evolución de estas relaciones entre distintos periodos y regiones del país.

El trabajo incluirá análisis descriptivos, modelos estadísticos, indicadores de desigualdad, tablas y visualizaciones que permitan responder la pregunta de investigación con evidencia empírica, manteniendo una interpretación cuidadosa de los resultados y de sus limitaciones metodológicas.

Además, se espera desarrollar una metodología completamente reproducible que documente el proceso de obtención, limpieza, integración y análisis de los datos, facilitando la replicación y extensión del estudio en investigaciones futuras.

---

# Contribución esperada

Esta investigación busca integrar herramientas de inferencia estadística, econometría y aprendizaje automático con énfasis en la interpretabilidad de los resultados.

El propósito es identificar los principales determinantes del ingreso laboral, analizar su evolución temporal y regional, y construir una metodología reproducible que pueda servir como base para futuras investigaciones relacionadas con desigualdad, mercado laboral y desarrollo regional en México.

---

## Tablas disponibles en el ENIGH

| Tabla                  | Nivel de análisis                         | Uso esperado en la investigación                                               |
| ---------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| `poblacion.csv`        | Persona                                   | Variables sociodemográficas (edad, sexo, escolaridad, etc.)                    |
| `trabajos.csv`         | Trabajo                                   | Características laborales, ocupación, horas trabajadas y prestaciones          |
| `ingresos.csv`         | Persona                                   | Variable respuesta: ingreso laboral y sus componentes                          |
| `concentradohogar.csv` | Hogar                                     | Variables agregadas del hogar, factores de expansión y contexto socioeconómico |
| `hogares.csv`          | Hogar                                     | Información complementaria del hogar                                           |
| `viviendas.csv`        | Vivienda                                  | Características de la vivienda y localización                                  |
| Otras tablas           | Actividades económicas, gastos y negocios | Se utilizarán únicamente si aportan variables relevantes al modelo             |

La ENIGH contiene un total de 17 tablas (12 en el levantamiento 2018), organizadas en distintos niveles de observación (vivienda, hogar, persona, trabajo, ingresos, gastos y actividades económicas). Para el objetivo de esta investigación se espera trabajar principalmente con las tablas poblacion, trabajos, ingresos, concentradohogar, hogares y viviendas, debido a que concentran la mayor parte de las variables necesarias para explicar el ingreso laboral. El resto de las tablas se incorporará únicamente si durante el desarrollo del proyecto aportan información relevante para responder la pregunta de investigación.

---


# Observaciones metodológicas para discutir

Antes de iniciar el desarrollo del proyecto hay que validar algunos aspectos metodológicos:

* Confirmar que la ENIGH constituye la fuente de información más adecuada para responder la pregunta de investigación o evaluar la conveniencia de incorporar otras fuentes como la ENOE o los Censos de Población.
* Validar la selección de los levantamientos 2018, 2020, 2022 y 2024 como horizonte temporal del estudio.
* Definir el nivel geográfico más adecuado para el análisis (entidad federativa, región o municipio), considerando la comparabilidad entre levantamientos y la disponibilidad de información.
* Evaluar la pertinencia de incorporar indicadores agregados provenientes de CONEVAL (índice de Gini, pobreza, rezago social, entre otros).
* Discutir si dichos indicadores deben emplearse únicamente para contextualizar los resultados o si resulta metodológicamente apropiado incorporarlos como variables explicativas mediante modelos multinivel u otras estrategias estadísticas.
* Definir el alcance del uso de técnicas de aprendizaje automático como herramienta complementaria para comparar resultados con los modelos estadísticos tradicionales, manteniendo el énfasis principal del trabajo en la interpretación estadística.

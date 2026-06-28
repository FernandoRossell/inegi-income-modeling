# INEGI Income Modeling

Repositorio de trabajo para la tesina **Determinantes del ingreso laboral y evolucion de la desigualdad regional en Mexico: un analisis estadistico utilizando la ENIGH (2018-2024)**.

Este repositorio se publica en GitHub principalmente por accesibilidad, organizacion y reproducibilidad del proyecto. La intencion es que el codigo, la documentacion metodologica y la metadata puedan consultarse facilmente; los datos crudos completos no se versionan aqui por tamano y manejo responsable de archivos.

## Objetivo del proyecto

El proyecto busca analizar los determinantes del ingreso laboral en Mexico mediante microdatos de la Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) para los levantamientos 2018, 2020, 2022 y 2024.

El interes central es identificar que caracteristicas individuales, educativas, laborales, del hogar y territoriales se asocian con diferencias en el ingreso laboral, asi como evaluar si la importancia de estos factores cambia entre regiones y a traves del tiempo.

El enfoque prioriza la explicacion sobre la prediccion. Por ello, los modelos principales deberan ser interpretables y permitir discutir magnitudes, signos, incertidumbre, limitaciones y posibles sesgos. El aprendizaje automatico puede usarse como herramienta complementaria, pero no como eje principal del trabajo.

## Pregunta de investigacion

Que factores individuales, educativos, laborales, del hogar y territoriales explican las diferencias en el ingreso laboral de la poblacion mexicana y como ha variado la importancia de estos factores entre distintas regiones del pais y a traves del tiempo?

## Datos

La carpeta `data/` no se almacena completa en GitHub. Para facilitar el acceso controlado, los datos del proyecto se resguardan en Google Drive:

[Carpeta de datos en Google Drive](https://drive.google.com/drive/folders/15kukCmRST4HSlcVT2cI2dvT1jliEtfmD?usp=sharing)

El acceso a esa carpeta requiere solicitud de permiso. Una vez autorizado el acceso, la carpeta debe colocarse localmente siguiendo la estructura esperada del repositorio:

```text
data/
|-- raw/
|   `-- EINGH/
|       |-- 2018/
|       |-- 2020/
|       |-- 2022/
|       `-- 2024/
|-- interim/
`-- processed/
```

Los archivos originales deben permanecer en `data/raw/` sin modificaciones. Las bases intermedias o finales deben generarse mediante scripts reproducibles y guardarse en `data/interim/` o `data/processed/`.

## Estructura del repositorio

```text
inegi-income-modeling/
|-- data/             # Datos locales; no versionados completos en GitHub
|-- docs/             # Planteamiento, metadata y documentacion metodologica
|-- notebooks/        # Exploracion y analisis narrativo
|-- outputs/          # Resultados generados no definitivos
|-- references/       # Documentos de referencia externos
|-- reports/
|   |-- figures/      # Figuras finales
|   `-- tables/       # Tablas finales
`-- src/
    |-- analysis/     # Analisis, robustez y desigualdad
    |-- data/         # Extraccion, metadata, lectura y preparacion de datos
    |-- features/     # Construccion de variables explicativas
    |-- models/       # Modelos estadisticos interpretables y benchmarks
    `-- visualization/# Graficas reutilizables
```

## Documentacion principal

- `docs/planteamiento.md`: planteamiento actualizado de la tesina.
- `docs/metadata_enigh.md`: metadata consolidada de tablas, columnas, llaves, factor temporal y documentacion ENIGH.
- `docs/enigh_variable_metadata.csv`: metadata tabular extraida de los PDF oficiales de ENIGH.
- `src/data/extract_enigh_pdf_metadata.py`: script para extraer metadata desde los PDF.
- `src/data/build_metadata_enigh.py`: script para reconstruir la documentacion de metadata.

## Tablas centrales de ENIGH

Para el objetivo del trabajo se espera trabajar principalmente con:

- `poblacion.csv`: caracteristicas individuales y sociodemograficas.
- `trabajos.csv`: caracteristicas laborales, ocupacion, horas trabajadas y prestaciones.
- `ingresos.csv`: ingreso laboral y componentes de ingreso.
- `concentradohogar.csv`: variables agregadas del hogar, factores de expansion y contexto socioeconomico.
- `hogares.csv`: informacion complementaria del hogar.
- `viviendas.csv`: caracteristicas de vivienda y localizacion.

Otras tablas de gastos, actividades agropecuarias, negocios y erogaciones se incorporaran solo si aportan variables relevantes para responder la pregunta de investigacion.

## Linea metodologica

El analisis debe avanzar de forma reproducible:

1. Documentar fuentes, estructura de datos y llaves de union.
2. Construir variables comparables entre 2018, 2020, 2022 y 2024.
3. Describir la distribucion del ingreso laboral y sus diferencias regionales.
4. Estimar modelos estadisticos interpretables.
5. Comparar la magnitud e importancia relativa de los determinantes entre anos y regiones.
6. Discutir limitaciones, variables omitidas, sesgos de seleccion y restricciones para inferencia causal.

## Nota sobre interpretacion

Los resultados deben presentarse con lenguaje cuidadoso. Si no existe una estrategia empirica que permita sostener inferencia causal, las estimaciones se interpretaran como asociaciones condicionadas por las variables observadas.

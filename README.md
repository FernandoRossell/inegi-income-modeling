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

El punto de partida activo para la etapa de determinantes son los marts nominales de `data/interim/revision_4/`: `mart_hogar_2018_2024.csv.gz` y `mart_persona_2018_2024.csv.gz`. La primera base analítica para determinantes ya quedó preparada para 2024 a nivel persona adulta con ingreso laboral/de negocio positivo; los microdatos derivados viven localmente en `data/processed/determinantes_2024/` y no se versionan en Git.

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
- `reports/documentacion_final_en_desarrollo.md`: documento vivo vigente con decisiones metodologicas, roadmap y alcance activo.
- `reports/preparacion_base_determinantes.md`: resumen metodologico de la base 2024 para asociaciones entre caracteristicas e ingreso.
- `reports/intentos_metodologicos/README.md`: indice historico de intentos deprecados, incluidos homologacion monetaria y diseno muestral JKn.
- `notebooks/12_preparacion_base_determinantes.ipynb`: notebook principal de preparacion de base, tablas, figuras y validaciones para determinantes 2024.
- `src/data/extract_enigh_pdf_metadata.py`: script para extraer metadata desde los PDF.
- `src/data/build_metadata_enigh.py`: script para reconstruir la documentacion de metadata.
- `src/features/preparacion_determinantes.py`: codigo reutilizable de la etapa 12.

`reports/documentacion_final_en_desarrollo.pdf` se conserva como version historica derivada. El Markdown es la version vigente; el PDF puede incluir contenido metodologico deprecado hasta que sea regenerado y verificado.

## Roadmap vigente

- Etapas 08 y 09: se conservan como avances respaldados por evidencia.
- Etapa 10: homologacion monetaria y deflactores deprecados del flujo principal; preservados como intento historico.
- Etapa 11: inferencia formal con diseno muestral y JKn deprecada del flujo principal; preservada como intento historico.
- Etapa 12: preparacion de base 2024 para determinantes completa; incluye universo, target, predictores iniciales, OHE, matriz diagnostica, faltantes, asociaciones exploratorias y diagnosticos de dependencia.
- Siguiente hito: modelos de determinantes e inferencia pendiente de definicion; no se entrenaron modelos ni se crearon particiones.

## Base activa para determinantes 2024

- Unidad: persona.
- Universo: `anio == 2024`, `edad >= 18` e `ingreso_persona_laboral_negocio_tri > 0`.
- Filas finales: 141,579 personas en 80,872 hogares.
- Target: `ingreso_persona_laboral_negocio_tri`, nominal trimestral.
- Matriz inicial: 67 columnas, sin target, derivados monetarios, identificadores, factores ni variables de diseno.
- Predictores iniciales: edad, numero de trabajos, horas totales, composicion del hogar, sexo, escolaridad alcanzada, region Banxico, tamano de localidad, parentesco, habla indigena, seguridad social, subordinacion/contrato del trabajo principal, sexo y escolaridad de la jefatura.
- Fuera de `X`: `factor`, `factor_hogar`, `est_dis`, `upm`, llaves, entidad/municipio, `est_socio`, variables monetarias, deflactores, variables reales y variables pendientes como `tam_emp_principal_desc`.
- Interpretacion: asociaciones descriptivas/exploratorias; no causalidad, no seleccion al ingreso positivo y no inferencia formal.

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

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

El punto de partida activo para determinantes es `data/interim/revision_4/mart_persona_2018_2024.csv.gz` (`mart_persona_revision_4`). El mart de hogares queda fuera del flujo de los notebooks 12 y 13. La preparación está parametrizada por año, con 2024 como predeterminado. Los microdatos derivados viven localmente en `data/processed/determinantes_<anio>/` y no se versionan en Git.

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
- `reports/contrato_analisis_temporal.md`: contrato de bases, comparabilidad, precios de 2024, geografias y futuros modelos por año.
- `AGENTS.md`: reglas permanentes de notebooks ejecutables, granularidad y ejecucion manual.
- `reports/preparacion_base_determinantes.md`: resumen metodologico vigente de la base ejecutada por defecto, actualmente 2024.
- `reports/auditoria_preparacion_determinantes.md`: auditoria diagnostica de la preparacion 2024 y compatibilidad anual antes de modelar.
- `reports/regresion_diagnostico_determinantes.md`: primera corrida diagnostica de regresion, VIF/GVIF, PCA y arbol para revisar variables antes de aprobar reducciones.
- `reports/preparacion_base_determinantes_2024.md`: copia anual del resumen de 2024.
- `reports/intentos_metodologicos/README.md`: indice historico de intentos deprecados, incluidos homologacion monetaria y diseno muestral JKn.
- `notebooks/12_preparacion_base_determinantes.ipynb`: notebook principal parametrizado con `ANIO_ANALISIS`, tablas, figuras y validaciones para determinantes.
- `notebooks/13_regresion_diagnostico_determinantes.ipynb`: notebook parametrizado para diagnostico inicial de regresion sin seleccion automatica.
- `src/data/extract_enigh_pdf_metadata.py`: script para extraer metadata desde los PDF.
- `src/data/build_metadata_enigh.py`: script para reconstruir la documentacion de metadata.
- `src/features/preparacion_determinantes.py`, `src/analysis/regresion_diagnostico.py` y `src/models/regresion_diagnostico.py`: codigo legado de ejecuciones anteriores; los notebooks 12 y 13 activos no dependen de estos modulos.

`reports/documentacion_final_en_desarrollo.pdf` se conserva como version historica derivada. El Markdown es la version vigente; el PDF puede incluir contenido metodologico deprecado hasta que sea regenerado y verificado.

## Roadmap vigente

- Etapas 08 y 09: se conservan como avances respaldados por evidencia.
- Etapa 10: implementacion historica de homologacion monetaria deprecada. La preparacion temporal nueva reutiliza solo su tabla versionada de factores anuales, con limitaciones explicitas.
- Etapa 11: inferencia formal con diseno muestral y JKn deprecada del flujo principal; preservada como intento historico.
- Etapa 12: preparacion individual parametrizada para los cuatro años, con auditoria de comparabilidad, regla visible de `segsoc_desc`, targets nominal y real aproximado en pesos de 2024, y alternativas regional/estatal. Ejecucion manual del codigo temporal pendiente.
- Etapa 13: exploracion local de 2024 conservada como antecedente y limitada a ese año mediante una validacion inicial; sus variables significativas no seleccionan predictores de otros años. El futuro analisis temporal usara una especificacion completa comun y exploraciones independientes por año.
- Siguiente hito: ejecutar manualmente 12 en los cuatro cortes, revisar categorias, referencias, deflactores y bases antes de modelar. Roadmap completo en `reports/contrato_analisis_temporal.md`.

## Base activa para determinantes

- Configuracion default: `ANIO_ANALISIS = 2024`, `ANIOS_VALIDOS = (2018, 2020, 2022, 2024)`, `EDAD_MINIMA = 18`.
- Para cambiar el año, modificar solo `ANIO_ANALISIS` al inicio de `notebooks/12_preparacion_base_determinantes.ipynb` y ejecutar todo el notebook.
- Unidad: persona; universo fijo: `anio == ANIO_ANALISIS`, `edad >= EDAD_MINIMA` e `ingreso_persona_laboral_negocio_tri > 0`.
- La version anterior de 2024 reporto 141,579 personas en 80,872 hogares; la version corregida esta pendiente de ejecucion manual y esos conteos deben verificarse de nuevo.
- Target: `ingreso_persona_laboral_negocio_tri`, nominal trimestral conservado en todos los años; su version real aproximada en pesos de 2024 y ambos `log1p` se agregan en la base individual. El factor anual procede de `docs/deflactores_precios_2024.csv` y requiere revision para ingreso laboral individual.
- La matriz historica de 2024 tuvo 67 columnas; la nueva matriz individual tendra una especificacion distinta y su tamaño se verificara al ejecutarla.
- Predictores principales: edad, sexo, escolaridad, parentesco, habla indigena, numero de trabajos, horas, seguridad social, subordinacion, contrato, region Banxico y tamaño de localidad. `tot_integ`, `menores`, `p65mas`, `sexo_jefe_desc` y `educa_jefe_desc` quedan como contexto del hogar fuera del modelo principal. `tam_emp_principal_desc` y `est_socio_desc` siguen pendientes.
- Fuera de la matriz descriptiva `X`: `factor`, `factor_hogar`, `est_dis`, `upm`, llaves, montos nominales/reales, deflactor y variables pendientes. `entidad` se conserva como alternativa geografica separada de `region_banxico`.
- Salidas por año: `data/processed/determinantes_<anio>/`, `reports/tables/preparacion_determinantes/<anio>/` y `reports/figures/preparacion_determinantes/<anio>/`.
- Comparabilidad historica inspeccionada: 2018 tenia las referencias previstas; 2020/2022 muestran una etiqueta contaminada de `segsoc_desc` para el codigo 2. El notebook 12 deja una recodificacion exacta y auditada; escolaridad, parentesco y referencia estatal requieren revision manual. Los resultados historicos no validan todavia la nueva preparacion.
- Interpretacion: asociaciones descriptivas/exploratorias; no causalidad, no seleccion al ingreso positivo y no inferencia formal.

## Regresion diagnostica activa

- Configuracion default: `ANIO_ANALISIS = 2024`, `ANIOS_VALIDOS = (2018, 2020, 2022, 2024)`, `EDAD_MINIMA = 18`, `TARGET = ingreso_persona_laboral_negocio_tri`, `CRITERIO_STEPWISE = None`, `EJECUTAR_SELECCION = False`.
- Para cambiar el año en la etapa 13, modificar solo `ANIO_ANALISIS` al inicio de `notebooks/13_regresion_diagnostico_determinantes.ipynb` y ejecutar todo el notebook.
- Salidas agregadas por año/especificacion: `reports/tables/regresion_diagnostico/<anio>/diagnostico_inicial/` y `reports/figures/regresion_diagnostico/<anio>/diagnostico_inicial/`.
- Particiones locales fuera de Git: `data/processed/regresion_diagnostico/<anio>/diagnostico_inicial/`.
- Las cifras previas de particion y ajuste de 2024 corresponden a la especificacion historica con variables de hogar; no son resultados de los notebooks corregidos.
- El notebook 13 lee `base_interpretable_personas_<anio>.csv.gz` generada por el 12. Ajusta su encoder solo en entrenamiento y prepara resúmenes completos de statsmodels, HC3, errores agrupados por hogar, pruebas, gráficas, PCA y árbol. El hogar sirve para evitar fuga y para agrupar errores, sin cambiar la unidad persona.
- Estado multi-anio: existe una exploracion local 2024; el codigo de comparacion temporal no se ha ejecutado. Modelos completos por año, geograficos, pooled e interacciones siguen pendientes.

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

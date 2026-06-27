# INEGI Income Modeling

Proyecto de tesina para analizar los determinantes del ingreso laboral a partir de microdatos de INEGI.

El objetivo principal no es maximizar la capacidad predictiva, sino explicar de manera interpretable que factores se asocian con el ingreso y, cuando el diseno empirico lo permita, discutir relaciones causales con cautela.

## Enfoque del proyecto

Este repositorio prioriza:

- Interpretabilidad de los modelos y de los resultados.
- Inferencia estadistica clara: signos, magnitudes, intervalos de confianza y pruebas de robustez.
- Distincion explicita entre correlacion, asociacion condicional y posibles efectos causales.
- Reproducibilidad del procesamiento de datos, estimaciones, tablas y figuras.
- Uso de modelos predictivos complejos solo como complemento o comparacion, no como eje central.

## Pregunta orientadora

Que caracteristicas individuales, laborales, educativas, territoriales y del hogar ayudan a explicar las diferencias en el ingreso laboral observado en los microdatos de INEGI?

## Estructura del repositorio

```text
inegi-income-modeling/
|-- data/
|   |-- raw/          # Datos originales sin modificar
|   |-- interim/      # Datos intermedios de limpieza
|   `-- processed/    # Bases finales para analisis y modelos
|-- docs/             # Notas metodologicas y avances de tesina
|-- notebooks/        # Exploracion, diagnosticos y analisis narrativo
|-- outputs/          # Resultados generados no definitivos
|-- references/       # Diccionarios, cuestionarios y documentos INEGI
|-- reports/
|   |-- figures/      # Figuras finales
|   `-- tables/       # Tablas finales
`-- src/
    |-- analysis/     # Descomposiciones, robustez e inferencia
    |-- data/         # Descarga, lectura y limpieza de microdatos
    |-- features/     # Construccion de variables explicativas
    |-- models/       # Modelos interpretables y benchmarks
    `-- visualization/# Graficas reutilizables
```

## Linea metodologica

El analisis debe avanzar de lo descriptivo a lo inferencial:

1. Exploracion de la distribucion del ingreso y calidad de datos.
2. Construccion documentada de variables.
3. Modelos base interpretables, por ejemplo regresiones lineales, log-lineales o cuantilicas.
4. Comparacion de especificaciones para evaluar sensibilidad de coeficientes.
5. Pruebas de robustez y discusion de posibles sesgos.
6. Modelos de machine learning solo como contraste, con herramientas de interpretacion si se usan.

## Criterios para interpretar resultados

- No usar lenguaje causal si la estrategia empirica solo identifica asociaciones.
- Reportar incertidumbre, no solo estimaciones puntuales.
- Explicar cambios en terminos sustantivos: porcentajes, brechas, elasticidades o diferencias esperadas.
- Documentar decisiones de limpieza, exclusion de observaciones y transformaciones del ingreso.
- Separar resultados principales de ejercicios exploratorios.

## Datos

Los microdatos originales deben colocarse en `data/raw/` y no modificarse directamente. Las bases limpias o transformadas deben generarse mediante scripts o notebooks reproducibles y guardarse en `data/interim/` o `data/processed/`.

Si los archivos son grandes o tienen restricciones de distribucion, se recomienda no versionarlos en Git. En su lugar, documentar su fuente, version, fecha de descarga y ruta esperada.

## Resultados esperados

El repositorio debe permitir producir:

- Tablas descriptivas de la muestra.
- Graficas de distribucion y brechas de ingreso.
- Modelos econometricos interpretables.
- Tablas de coeficientes y robustez.
- Figuras y tablas listas para incorporarse a la tesina.

## Estado

Proyecto en etapa inicial de organizacion.

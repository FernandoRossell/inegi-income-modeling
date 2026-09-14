# Intentos metodológicos históricos

Este índice conserva intentos que ya no forman parte del flujo metodológico principal de la tesina. Se mantienen por trazabilidad, no como resultados finales ni como especificación activa.

## Etapa 10: homologación monetaria y deflactores

- Objetivo original: expresar montos de distintos años en pesos de 2024 y contrastar resultados nominales contra reales.
- Método explorado: deflactor anual común calibrado contra un benchmark de ingreso corriente promedio trimestral del hogar.
- Archivos y resultados existentes: `notebooks/10_homologacion_monetaria.ipynb`, `docs/deflactores_precios_2024.csv`, `data/interim/revision_5/`, figuras reales en `reports/figures_documentacion/` y preservación textual en `reports/intentos_metodologicos/homologacion_monetaria_etapa_10.md`.
- Estado de ejecución y validaciones alcanzadas: la documentación histórica reporta reproducción cercana del promedio benchmark y conservación del Gini bajo deflactor común.
- Limitaciones conocidas: deflactor común por año; no reconstruye deflactores mensuales por componente ni periodo de referencia.
- Decisión de deprecación: 2026-09-13, excluida del alcance metodológico principal.
- Motivo: delimitación de alcance; no se afirma que el método sea incorrecto.
- Commits de referencia: `cab76df` y `5d19b9f`.

## Etapa 11: diseño muestral formal y JKn

- Objetivo original: incorporar inferencia descriptiva aproximada con `factor`, `est_dis` y `upm` antes del modelado.
- Método explorado: JKn estratificado por UPM, dominios nacionales/regionales y contraste Norte-Sur.
- Archivos y resultados existentes: `notebooks/11_diseno_muestral_formal.ipynb`, `reports/diseno_muestral_formal.md`, `src/analysis/diseno_muestral_jkn.py`, `reports/tables/diseno_muestral/` y figuras en `reports/figures_documentacion/`.
- Estado de ejecución y validaciones alcanzadas: el manifest histórico reporta `estado_global=ok`; ese estatus pertenece a la ejecución original y no significa adopción metodológica vigente. La comparación con R `survey` quedó pendiente por entorno.
- Limitaciones conocidas: JKn aproximado con variables observables; no reconstruye calibración, no respuesta, FPC ni pesos replicados oficiales.
- Decisión de deprecación: 2026-09-13, excluida del alcance metodológico principal.
- Motivo: delimitación de alcance; no se afirma que el método sea incorrecto.
- Commit de referencia: `6031f9c`.

## PDF de documentación

`reports/documentacion_final_en_desarrollo.pdf` se conserva como versión histórica derivada. La versión vigente es `reports/documentacion_final_en_desarrollo.md`; el PDF puede conservar contenido retirado y no debe citarse como alcance actual hasta regenerarse y verificarse.

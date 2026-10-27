# Mejorar especificación y validar fuera de muestra (notebook 15)

**Estado (18-10-2026):** notebook ejecutado de principio a fin; resultados pendientes de revisión humana.
**Notebook:** `notebooks/15_especificacion_validacion_fuera_muestra.ipynb`.
**Salidas:** `outputs/especificacion_validacion_fuera_muestra/` (tablas CSV, figuras y `manifest_especificacion_validacion.json`; no versionadas).
**Unidad:** persona adulta con ingreso laboral o de negocio trimestral positivo, por corte ENIGH 2018, 2020, 2022 y 2024. Son cortes transversales repetidos, no un panel.

El documento resume método y hallazgos. Las fórmulas, la justificación teórica y todas las tablas están en el notebook.

## Cambios previos en la cadena de datos

- **Notebook 05:** el trabajo principal (`id_trabajo = 1`) conserva `sinco` y `scian` de `trabajos.csv` como `sinco_principal` y `scian_principal`. Las versiones de catálogo cambian (SINCO 2011 en 2018 y SINCO 2019 desde 2020; SCIAN 2013 y SCIAN 2018), por lo que el mart guarda el código original. Se re-ejecutó y se verificó que las 141 columnas previas de `mart_persona_2018_2024` y todo `mart_hogar_2018_2024` quedan idénticos, con el mismo número de filas.
- **Notebook 12:** exporta 14 insumos nuevos (`variables_especificacion_15`), entre ellos códigos de escolaridad, parentesco, estado conyugal, etnia, alfabetismo, horas del trabajo principal, independencia, tamaño de empresa, SINCO, SCIAN y estrato. Se re-ejecutó para los cuatro años. Las 37 columnas previas de cada base y el universo no cambian.

## Método

1. **Homologación por código.** Varias etiquetas de 2024 están contaminadas en la fuente. Cada código se coteja con su etiqueta y la ejecución se detiene ante códigos no catalogados. Ocupación y sector se usan en niveles estables entre versiones: nueve divisiones SINCO y once sectores SCIAN amplios.
2. **Regla de plausibilidad.** Se calcula $z = (\ln y - \text{mediana})/(1.4826\,\text{MAD})$ dentro de cada año y se excluye si $z > 8$. Solo excluye un registro: 2024, 17.0 millones trimestrales, $z = 8.38$. El umbral se fijó tras inspeccionar ese máximo y está documentado como decisión, no como prueba. No se recortan colas: truncar por la variable dependiente sesga los coeficientes.
3. **Forma funcional:**
   - edad cuadrática centrada;
   - *spline* lineal de horas con nudos en 20, 40, 48 y 60, y horas acotadas a 112;
   - indicador de dos o más trabajos;
   - grados aprobados respecto al grado típico de conclusión del nivel;
   - alternativa de Mincer con experiencia potencial.
4. **Escalera anidada.** M0 (especificación del notebook 14) → M1 forma funcional → M2 escolaridad fina → M3 variables excluidas → M4 ocupación y sector → M5 interacciones. Se compara con $R^2$, $\bar R^2$, AIC, BIC, *F* anidada y **$R^2$ de validación cruzada de 5 pliegues agrupada por hogar**.
5. **Interacciones.** Siete bloques fijados por teoría. Regla declarada de antemano: un bloque entra si en **los cuatro años** cumple $\Delta$BIC < 0 y $\Delta R^2_{CV}$ > 0.
6. **Geografía:**
   - estratos región × tamaño de localidad;
   - FGLS por estrato × subordinación;
   - modelos separados por tamaño de localidad, con Wald tipo Chow;
   - entidad en lugar de región;
   - contracción empírica bayesiana de efectos estatales.
7. **Supuestos.** RESET, Breusch–Pagan robusto, Jarque–Bera, GVIF, distancia de Cook, residuos parciales y perfil de Box–Cox condicional.
8. **Estimadores alternativos:**
   - Huber ($c = 1.345$);
   - regresión cuantílica ($\tau$ = 0.1, 0.25, 0.5, 0.75 y 0.9);
   - ecuaciones separadas para subordinados e independientes;
   - retransformación a pesos con corrección de Duan global y por grupo, evaluada fuera de muestra.

## Hallazgos principales

| $R^2_{CV}$ (log) | 2018 | 2020 | 2022 | 2024 |
| --- | --- | --- | --- | --- |
| M0 base notebook 14 | 0.446 | 0.429 | 0.426 | 0.442 |
| M1 forma funcional | 0.493 | 0.471 | 0.472 | 0.485 |
| M3 variables excluidas | 0.512 | 0.490 | 0.492 | 0.504 |
| M4 ocupación y sector | 0.535 | 0.510 | 0.515 | 0.528 |
| M5 interacciones | 0.545 | 0.518 | 0.524 | 0.536 |
| M5 con entidad | 0.549 | 0.522 | 0.532 | 0.543 |

- **Sin sobreajuste:** $\bar R^2$ y $R^2_{CV}$ difieren en menos de 0.001. La mayor ganancia viene de la forma funcional (+0.042 a +0.047).
- **Interacciones seleccionadas:**
  - género × ciclo de vida;
  - educación × edad;
  - región × tamaño de localidad;
  - género × territorio;
  - subordinación × seguridad social y horas.

  Educación × territorio y ocupación × localidad son significativas, pero empeoran el BIC en los cuatro años y no entran.
- **Prima educativa (M3 → M4):** Licenciatura frente a Secundaria cae de 43% a 27% en 2024 al controlar ocupación y sector. Para interpretar la escolaridad, la referencia es M3; ocupación y sector son posibles malos controles.
- **Subordinados e independientes por separado:** mejoran el $R^2_{CV}$ en ambos grupos y años:
  - subordinados: de 0.537–0.551 a 0.553–0.568;
  - independientes: de 0.472–0.526 a 0.492–0.548.

  La varianza residual de los independientes casi duplica la de los subordinados.
- **Territorio:**
  - FGLS reduce los errores estándar de la mayoría de los coeficientes en 15%–20%, sin mejorar el ajuste.
  - Los modelos separados por tamaño de localidad apenas superan a M5.
  - La contracción de los efectos estatales es de solo 1%–3%.
- **Cuantílica (2024):**

  | Asociación | p10 | p50 | p90 |
  | --- | --- | --- | --- |
  | Licenciatura | +20% | +25% | +37% |
  | Posgrado | +53% | +68% | +90% |
  | Seguridad social | +28% | +16% | +11% |

  La brecha de género es mayor en la cola baja.
- **Huber:** coeficientes cercanos a OLS, con una brecha de género menor (−21% frente a −25%). No mejora el $R^2_{CV}$.
- **Escala:** perfil de Box–Cox condicional a M4 (rejilla de $\lambda$ de −0.10 a 1.00, paso 0.01).

  | | 2018 | 2020 | 2022 | 2024 |
  | --- | --- | --- | --- | --- |
  | $\hat\lambda$ marginal | 0.25 | 0.25 | 0.26 | 0.30 |
  | $\hat\lambda$ condicional | 0.22 | 0.22 | 0.22 | 0.25 |
  | $\Delta\ell$ del logaritmo ($\lambda = 0$) | −12,789 | −14,864 | −14,952 | −17,831 |
  | $\Delta\ell$ de la raíz ($\lambda = 0.5$) | −20,196 | −23,958 | −23,601 | −16,574 |
  | $\Delta\ell$ del nivel ($\lambda = 1$) | −165,789 | −230,935 | −201,822 | −155,260 |
  | Ganancia de transformar que captura el log, $G_{\log}$ | 92.3% | 93.6% | 92.6% | 88.5% |
  | Asimetría residual: log / $\hat\lambda$ / raíz / nivel | −0.82 / 0.46 / 4.5 / 48 | −0.80 / 0.49 / 6.0 / 121 | −0.82 / 0.59 / 5.2 / 68 | −0.91 / 0.60 / 3.7 / 50 |

  $\Delta\ell$ es la caída de log-verosimilitud frente al óptimo y $G_{\log} = [\ell(0) - \ell(1)]/[\ell(\hat\lambda) - \ell(1)]$.

  **Cómo argumenta la normalización logarítmica:**
  1. El ingreso en niveles es inadecuado para el modelo lineal: tiene la mayor pérdida y una asimetría residual extrema.
  2. Los datos piden una transformación fuertemente compresiva ($\hat\lambda$ de 0.2 a 0.3).
  3. El logaritmo, miembro límite de la familia, recupera entre 89% y 94% de la ganancia de transformar.
  4. Entre las escalas con interpretación, el logaritmo deja los residuos menos asimétricos. La raíz queda más cerca del óptimo solo en 2024, con residuos claramente asimétricos.
  5. Solo el logaritmo da coeficientes porcentuales, comparables entre años sin deflactar.

  El logaritmo **no** es exactamente óptimo: con $n \approx 140{,}000$ la prueba rechaza cualquier $\lambda$ exacto. Su sesgo en la cola baja (asimetría de −0.8 a −0.9) se atiende con la regresión cuantílica, Huber y Duan por grupo. La potencia $\lambda \approx 0.25$ queda como sensibilidad.
- **Duan:** la predicción ingenua subestima la media en pesos (razón 0.75–0.82) y Duan global la sobreestima (1.14–1.20). Duan por subordinación × localidad queda calibrado (1.04–1.06).
- **Registro excluido:** su influencia es despreciable en log (el $R^2$ pasa de 0.44207 a 0.44213). En nivel nominal es la observación más influyente: el $R^2$ en pesos pasa de 0.070 a 0.136.

## Limitaciones

- Asociaciones condicionadas, no efectos causales; ocupación y sector pueden ser malos controles.
- Los años de escolaridad y el grado de conclusión son aproximados sin antecedente escolar (Normal, Técnica).
- Errores agrupados por hogar sin ponderadores ni diseño muestral completo; Huber y cuantílica sin agrupación por hogar.
- Montos nominales: no comparar niveles entre años. Las comparaciones temporales de coeficientes requieren interacciones con año (notebook 14).

## Siguientes pasos sugeridos

1. Revisar manualmente la homologación (catálogos SINCO/SCIAN, convención de escolaridad).
2. Llevar M3 (interpretación) y M5 (ajuste) al análisis temporal, con ecuaciones separadas para subordinados e independientes.
3. Evaluar Box–Cox ($\lambda \approx 0.25$) y un tratamiento específico de ingresos muy bajos como sensibilidad.

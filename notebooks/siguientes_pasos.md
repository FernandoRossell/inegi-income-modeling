# Siguientes pasos: cierre de la analítica (notebooks 15, 16 y 17)

> Plan para ejecutar en local. Se escribió el 28 de octubre de 2026 sin acceso a los datos, a partir de los resultados guardados en los notebooks 15 y 16 (commit `3fc000d`). **Nada de esto se ha ejecutado**: las cifras citadas son de esas ejecuciones y las expectativas son hipótesis por verificar. Si trabajas con Claude en tu computadora, dale este archivo como guía.

## Reglas de este plan

1. **Solo se agrega.** Los notebooks 15 y 16 conservan su código y sus resultados. Lo nuevo va en celdas nuevas o en un notebook nuevo. Las únicas excepciones están marcadas con ✏️: correcciones de redacción (sección H) y, como opción, ajustar la presentación de dos heatmaps del 16 (F2 y F3), sin cambiar ningún número.
2. **Los análisis nuevos van en un notebook 17**, que lee las bases y el manifiesto que exporta el 15, igual que el 16. Así no hay que volver a correr el 15 (unos 30 min) ni cargar más el 16 (unos 25 min).
3. **Se mantienen las reglas de `AGENTS.md`:**
   - unidad de análisis persona;
   - todo el código sustantivo vive en el notebook: las funciones del 15 y del 16 que se necesiten se copian en celdas, no se importan;
   - los resultados visibles salen de la ejecución actual y la exportación va al final;
   - no hay push ni merge sin autorización.
4. **Cada regla de lectura se fija antes de ejecutar.** Los umbrales propuestos abajo son sugerencias: ajústalos antes de ver resultados, no después.
5. **Primero submuestra, luego completo.** Correr con `FRACCION_HOGARES_PRUEBA = 0.1` para depurar y después con `None`.

## Resumen

| # | Tarea | Dónde | Tipo | Costo | Prioridad |
|---|---|---|---|---|---|
| A | Supuestos por subordinación: Box–Cox y diagnóstico completo | nb17 §1 | análisis nuevo | bajo | pedida |
| B | Ecuaciones separadas: efectos promedio por grupo y su cambio en el tiempo | nb17 §2 | análisis nuevo | bajo | pedida |
| C | Robustez de los efectos promedio: Huber y cuantílica sobre M5 | nb17 §3 | análisis nuevo | alto | pedida |
| D | Sensibilidad de escala: Box–Cox con λ = 0.25 | nb17 §4 | análisis nuevo | medio | pedida |
| E | Ponderadores y diseño muestral | nb17 §5 | análisis nuevo | bajo a medio | recomendada |
| F | Referencias y lectura de las figuras | nb16 | texto y presentación | bajo | pedida |
| G | Capas de la brecha territorial: bruta, M3 y M5 | nb16 §7 | análisis nuevo | bajo | recomendada |
| H | Correcciones de redacción ✏️ | nb15, nb16 y reporte | texto | nulo | recomendada |
| I | Actualizar el reporte | `reports/` | texto | bajo | al final |

## Orden sugerido

1. `git pull` y crear una rama de trabajo.
2. Notebook 17 completo (A a E) con submuestra; revisar las validaciones; correrlo completo.
3. Notebook 16: F y G; volver a ejecutarlo completo.
4. H, que no requiere ejecutar nada.
5. I, con los resultados ya en mano.

---

## Notebook 17: `17_robustez_sensibilidad_modelo_final.ipynb`

**Encabezado (markdown).** Unidad de análisis: persona, la misma población del 16. Pregunta: ¿las conclusiones del modelo final dependen de mezclar subordinados e independientes, de la escala logarítmica, de la influencia de las colas o de no ponderar?

**Configuración.**
- `ANIOS` y `ANIO_DIAGNOSTICO = 2024`.
- `LAMBDA_SENSIBILIDAD = 0.25`.
- `GRID_LAMBDA` de −0.10 a 1.00 en pasos de 0.01, igual que el 15.
- `HUBER_T = 1.345` y `CUANTILES = [0.10, 0.50, 0.90]`.
- Banderas: `EJECUTAR_HUBER_M5`, `EJECUTAR_CUANTILICA_M5`, `EJECUTAR_PONDERADO`, `FRACCION_HOGARES_PRUEBA` y `EXPORTAR_RESULTADOS`.

**Insumos.** El manifiesto `outputs/especificacion_validacion_fuera_muestra/manifest_especificacion_validacion.json` y las bases `data/processed/especificacion_validacion/base_modelo_<anio>.csv.gz`, con la misma validación de la sección 1 del 16. Las bases ya traen el ingreso en pesos (`ingreso_persona_laboral_negocio_tri`), `factor`, `est_dis`, `upm` y `subor_grupo`.

**Funciones (copiar en celdas).**
- Del 16: `columnas_termino`, `construir_matriz`, `ajustar`, `medias_diseno`, `contrafactual`, `contraste`, `universo` y `cambios_temporales`.
- Del 15: `transformar_box_cox`, `asimetria` y el cálculo del perfil de Box–Cox de la sección 9.

**Salidas.** `outputs/robustez_modelo_final/`, `reports/figures/robustez_modelo_final/` y `manifest_robustez.json`.

**Validación general.** Las AME de OLS de M5 que calcule el 17 deben coincidir con `outputs/interpretacion_modelo_final/efectos_promedio.csv` (diferencia menor a 1e-8). Si no coinciden, las funciones copiadas no son las mismas.

### A. Supuestos por subordinación (§1 del 17)

**Por qué.** La $\hat\lambda$ conjunta (0.22 en 2018–2022 y 0.25 en 2024) se estimó suponiendo una sola varianza. Pero la desviación residual de los independientes (1.17–1.27) casi duplica la de los subordinados (0.60–0.70). Como reconoce la sección 9 del 15, parte de esa $\hat\lambda$ puede venir de mezclar los dos grupos.

**Qué hacer.**
- **Grupos:** `Subordinado` e `Independiente`. Las personas sin trabajo principal (cerca de 4%) solo se describen (ver el último punto).
- **Matriz de diseño:** M4 sin términos de subordinación, `[t for t in ESPECIFICACIONES["M4_ocupacion_sector"] if "subor_principal_desc" not in t]`. Se usa M4 para que el caso conjunto sea comparable con la sección 9 del 15. En independientes el contrato es constante (`No aplica`) y `construir_matriz` lo elimina.
- **Para cada año y grupo, más el conjunto como control:**
  - perfil de Box–Cox condicional: $\hat\lambda$, IC 95%, $\Delta\ell$ en λ = 0, 0.5 y 1, y $G_{\log}$;
  - asimetría y curtosis de los residuos en log y en $\hat\lambda$;
  - RESET (potencia 3, HC0), Breusch–Pagan robusto y Jarque–Bera del OLS en log, con las mismas llamadas de la celda de diagnóstico de la §9 del 15;
  - Breusch–Pagan dentro de cada grupo frente al tamaño de localidad, para ver cuánta heterocedasticidad queda después de separar.
- **Figura:** perfil de log-verosimilitud por grupo, en dos paneles con un color por año y λ = 0 marcado.
- **Personas sin trabajo principal:** n por año, distribución de ln(1+y), horas, edad, sexo y fuente del ingreso. Sirve para decidir si pueden juntarse con los independientes; hoy quedan fuera de la §12 del 15.

**Validación.** La fila conjunta debe reproducir el 15: $\hat\lambda$ = 0.22, 0.22, 0.22 y 0.25, y $G_{\log}$ = 0.923, 0.936, 0.926 y 0.885.

**Regla de lectura (propuesta).**
- **Escenario 1:** $\hat\lambda_{sub} \le 0.10$ y $\hat\lambda_{ind} > 0.10$. La $\hat\lambda$ conjunta viene sobre todo de mezclar grupos. El log queda justificado para subordinados, los independientes conservan la salvedad y se refuerza reportar por grupo (B).
- **Escenario 2:** ambos grupos con $\hat\lambda \ge 0.15$. El costo del log es general y no viene de la mezcla, así que la sensibilidad D gana peso.
- **Intermedio:** se reporta tal cual, sin forzar ninguna conclusión.

**Expectativa.** Por las densidades de la §4 del 15, se espera el escenario 1 o el intermedio: la cola izquierda está sobre todo en independientes y en personas sin trabajo principal.

### B. Ecuaciones separadas por subordinación (§2 del 17)

**Por qué.** Es la recomendación 2 del 15 y la decisión 2 del reporte. El 16 solo separa por grupo el perfil de horas.

**Qué hacer.**
- **Especificación:** la misma de la §12 del 15, `ESPECIFICACION_GRUPO` (M5 sin términos de subordinación), por año y grupo, con errores agrupados por hogar.
- **Efectos promedio:** con la maquinaria del 16 (`contrafactual`, `medias_diseno` y `contraste`), calculados dentro de la muestra de cada grupo. Son las mismas variables de la §3 del 16, salvo inserción laboral; el contrato solo aplica a subordinados.
- **Cambios en el tiempo:** cambio 2018→2024 y Wald de estabilidad con `cambios_temporales`, con Holm por familia y por grupo.
- **Tabla comparativa** para los efectos de `TRAYECTORIAS`: M5 conjunto, subordinados e independientes.
- **Figuras:** forest de 2018 y 2024 por grupo, y trayectorias por grupo.

**Validación.** Los $R^2$ deben reproducir la tabla de la §12 del 15. En 2024, por ejemplo: 0.5259 en subordinados y 0.4417 en independientes.

**Lectura.** Dónde difieren los determinantes entre grupos (por ejemplo, la brecha de género y la escolaridad) y si la compresión 2018→2024 aparece en ambos. Son efectos condicionados a pertenecer al grupo, y la composición de los grupos cambia entre años, sobre todo en 2020.

### C. Robustez de los efectos promedio: Huber y cuantílica sobre M5 (§3 del 17)

**Por qué.** En el 15 (M4, 2024), el efecto más sensible a la cola izquierda es la brecha de género, y el 16 la reporta sin ningún contraste de robustez:

| Efecto (M4, 2024) | OLS | Huber | Mediana |
|---|---|---|---|
| Brecha de género | −25.1% | −20.6% | −18.3% |
| Seguridad social | +18.5% | +16.5% | +16.0% |
| Contrato | +14.7% | +13.0% | +11.8% |
| Licenciatura | +27.4% | +26.4% | +25.1% |
| Posgrado | +70.0% | +67.9% | +68.0% |

**Qué hacer.**
- Usar la misma matriz de M5 que el 16.
- **Huber:** `sm.RLM` con `HuberT(t=1.345)` y `maxiter=100`, igual que la §10 del 15.
- **Cuantílica:** `QuantReg` con τ = 0.1, 0.5 y 0.9, y errores con kernel de Hall–Sheather, como en la §11 del 15.
- **Efectos promedio:** los tres estimadores son lineales en β, así que $\mathrm{AME} = (\bar x_c - \bar x_r)'\hat\beta_{est}$ con las mismas medias de escenario del 16, y su error es $\sqrt{d'\hat V_{est}\,d}$. En la cuantílica, $100[\exp(\cdot)-1]$ es la diferencia porcentual en el cuantil condicional; es exacta por equivarianza y no requiere Duan.
- **Tabla por año** para `TRAYECTORIAS`: OLS, Huber, Q0.5, Q0.1, Q0.9 y la diferencia OLS − Q0.5 en puntos porcentuales.
- **Figura:** para cada efecto, los cinco estimadores en 2018 y 2024.

**Costo.**
- El 15 usó M4 justo para abaratar Huber y la cuantílica. Correr primero solo 2024 y medir el tiempo de cada ajuste; luego decidir si van los cuatro años o solo 2018 y 2024.
- Los errores de Huber y de la cuantílica no están agrupados por hogar. Hay que documentarlo o, si el tiempo alcanza, hacer un bootstrap por hogares (B = 200) solo para 2024.

**Regla de lectura (propuesta).** Un efecto es robusto a las colas si Huber y Q0.5 tienen el mismo signo que OLS y caen dentro de su IC 95%. Si no, se reporta el rango entre Q0.5 y OLS como incertidumbre de especificación, atribuida a la cola baja.

### D. Sensibilidad de escala: Box–Cox con λ = 0.25 (§4 del 17)

**Por qué.** Es la recomendación 5 del 15 y la decisión 6 del reporte.

**Qué hacer.**
- **Target:** $z = (y^{0.25} - 1)/0.25$, con y el ingreso nominal trimestral (siempre mayor que 0). La λ es fija e igual en los cuatro años para conservar la comparabilidad.
- **Estimación:** OLS de M5 con errores agrupados por hogar.
- **Métrica comparable con el 16.** Para cada persona y escenario se calcula el ingreso predicho sin corrección, $\hat y_i(s) = (1 + \lambda x_i(s)'\hat\beta)^{1/\lambda}$, y

$$\mathrm{AME}_{BC} = \frac1n\sum_i\big[\ln\hat y_i(c) - \ln\hat y_i(r)\big] = \frac1{\lambda n}\sum_i\big[\ln(1+\lambda x_i(c)'\hat\beta) - \ln(1+\lambda x_i(r)'\hat\beta)\big].$$

  Se reporta como $100[\exp(\mathrm{AME}_{BC}) - 1]$, la diferencia porcentual en la media geométrica del ingreso predicho. Es la misma lectura del 16 y no necesita Duan.
- **Matrices completas.** La métrica no es lineal en β, así que no bastan las medias: hay que construir la matriz de cada escenario (n × k) y descartarla al terminar.
- **Error estándar** por método delta, con forma cerrada:

$$g = \frac1n\sum_i\left[\frac{x_i(c)}{1+\lambda x_i(c)'\hat\beta} - \frac{x_i(r)}{1+\lambda x_i(r)'\hat\beta}\right], \qquad \widehat{\operatorname{Var}} = g'\hat V_{cl}\,g.$$

- **Dominio.** Contar los casos con $1 + \lambda x'\hat\beta \le 0$ (ingreso predicho no positivo). Se esperan cero o muy pocos.
- **Tabla:** AME en log (16) frente a AME Box–Cox para todos los efectos de M5 en los cuatro años, su diferencia en puntos porcentuales y, sobre todo, el cambio 2018→2024 en ambas escalas.

**Validación.** Programar la métrica para cualquier λ y correrla con λ = 0 (z = ln y): debe reproducir las AME lineales en log. La diferencia con el 16 debe ser mínima, porque el 16 usa ln(1+y).

**Regla de lectura (propuesta).** La conclusión es robusta a la escala si el signo y la dirección del cambio 2018→2024 coinciden en las dos escalas. Señalar los efectos que difieran más de 3 puntos porcentuales. Se espera que se muevan los mismos que en C (género, seguridad social y contrato) y que la escolaridad quede estable.

### E. Ponderadores y diseño muestral (§5 del 17, recomendado)

**Por qué.**
- El manifiesto del 15 y las limitaciones del reporte dicen "sin ponderadores" y que los errores agrupados por hogar no reproducen el diseño.
- El texto del 16 dice que los efectos se promedian "sobre la población del año", pero sin `factor` el promedio es sobre la muestra.
- Es una pregunta probable en la revisión de la tesina (decisión 3 del reporte).

**Qué hacer.**
- **E1 (barato).** Recalcular las AME del 16 con los mismos β, pero promediando los escenarios con el factor de expansión: $\bar x = \sum_i w_i x_i / \sum_i w_i$. El resultado es el efecto promedio para la población con ingreso positivo.
- **E2 (moderado).** WLS de M5 con `weights=factor` y errores agrupados por UPM, con un identificador compuesto `anio | est_dis | upm` como en el notebook 11. Comparar β, AME y la razón entre los errores por UPM y por hogar.
- **Tabla** para `TRAYECTORIAS`: sin ponderar, E1 y E2, con IC.

**Lectura.**
- Si E1 se parece a la versión sin ponderar, la composición de la muestra no mueve los promedios.
- Si E2 difiere, hay heterogeneidad que el modelo no captura (Solon, Haider y Wooldridge, 2015, *What are we weighting for?*).
- Se espera que los errores por UPM sean mayores que los agrupados por hogar.

---

## Notebook 16: referencias y lectura de las figuras (F y G)

### F1. Nota "Qué se compara con qué" (celda markdown nueva, después de "Cómo leer los resultados")

| Figura o tabla | Qué muestra | Referencia (el 0) |
|---|---|---|
| §3 Panorama de efectos | % de diferencia en la media geométrica de 1+ingreso | La categoría de referencia de cada variable: hombre; no habla lengua indígena; sin autoadscripción; alfabeta; soltero(a); jefe(a); estrato bajo; Secundaria concluida; sin contrato; sin seguridad social; un trabajo; empresa de 2 a 5 personas; región Centro; urbana grande |
| §3 Ocupación y sector | Igual | Actividades elementales y de apoyo; Comercio |
| §3 Inserción laboral | Igual | Independiente |
| §3 Variables de conteo | Igual | El valor observado (escenario: +1) |
| §4 Prima educativa | Igual | Secundaria concluida (`grado_relativo = 0`); M3 sin ocupación ni sector, M5 dentro de ellos |
| §5 Perfiles de edad | Igual | Hombres de 40 años; Secundaria a los 40 |
| §6 Horas | Igual | 40 horas, dentro del mismo grupo |
| §7 Estratos territoriales | Igual | Centro, urbana grande (la celda vacía) |
| §7 Brecha de género | Mujer frente a hombre | Los hombres de la **misma** celda: cada celda tiene su propia referencia |
| §7 Entidades | Igual | Ciudad de México |
| §8 Cambios | Puntos porcentuales de cambio 2018→2024 | El mismo efecto en 2018 |

En todos los casos, el resto de las características de cada persona se mantiene como se observó.

Ejemplo de redacción para la tesina, con una celda del heatmap: *"En 2024, Sur, rural = −21: si las personas de la muestra, con sus mismas características, ocupación y sector, vivieran en una localidad rural del Sur, su ingreso típico (media geométrica) sería 21% menor que si vivieran en una ciudad grande del Centro."*

### F2. Heatmap de estratos territoriales

**Problemas actuales:**
- la celda de referencia aparece vacía, con las líneas de la cuadrícula atravesándola;
- no hay barra de color;
- no se distingue qué celdas son estadísticamente distintas de 0;
- no se sabe cuántas personas hay en cada celda; por ejemplo, Norte, rural = +34 en 2020.

**Ajustes (los números no cambian):**
- marcar la celda de referencia con "ref. = 0" y un sombreado gris;
- agregar una barra de color con la etiqueta "% frente a Centro, urbana grande", conservando la escala simétrica común a los cuatro años;
- un subtítulo con la lectura: "la misma persona en otro estrato; pesos nominales sin ajuste por costo de vida";
- distinguir las celdas cuyo IC 95% incluye el 0 (texto gris o "ns"); `estratos_territoriales` ya tiene los IC;
- una tabla o texto pequeño con el n observado por celda y año.

### F3. Heatmap de brecha de género

- **Título y subtítulo:** "brecha mujer frente a hombre dentro de cada celda; un color más oscuro es una brecha mayor".
- **Nota de estructura (importante).** M5 incluye sexo × región y sexo × localidad, pero no sexo × región × localidad. En log, la brecha de cada celda es una base más un desplazamiento por región más uno por localidad, así que las 16 celdas salen de solo 7 parámetros. Se ve en 2024: la diferencia entre Sur y Centro es la misma (≈ −0.107 en log) en las cuatro localidades. El heatmap sugiere 16 estimaciones independientes, y no lo son.
- **Figura complementaria (celda nueva):** brecha por región (cuatro barras) y por tamaño de localidad (cuatro barras), con IC. Su cambio 2018→2024 sería una familia de 8 contrastes, en lugar de los 16 redundantes de la §8.

**Cómo presentar F2 y F3.** Por la regla de solo agregar, la opción por defecto es una celda nueva con la versión anotada, justo después de la original. Si prefieres no duplicar figuras, la alternativa ✏️ es ajustar solo el código de graficación de la celda original. Decídelo en casa.

### F4. Notas al texto de "Cómo leer los resultados" (párrafos nuevos, sin borrar nada)

- La "diferencia porcentual en 1+ingreso" es una diferencia en la **media geométrica**, no en el ingreso medio. Por eso no requiere Duan, que solo hace falta para reportar pesos promedio (§13 del 15).
- Los promedios son sobre la **muestra** del año, sin factores de expansión (ver E).
- Las brechas territoriales están en pesos nominales y no se ajustan por diferencias de precios entre regiones, así que parte de la brecha puede reflejar el costo de vida.
- 2020 es un año atípico porque se levantó durante la pandemia. Los picos de 2020 en contrato, inserción laboral, rural y Norte pueden reflejar quién conservó su ingreso. Por eso el contraste principal es 2018→2024.

### F5. Sección "Lectura de resultados" (nueva, antes de la exportación)

A diferencia del 15, el 16 no tiene síntesis escrita. Conviene escribirla después de correr el 17, para integrar la robustez.

### G. Capas de la brecha territorial (subsección nueva en la §7 del 16, recomendada)

**Por qué.** Igual que con la escolaridad, M5 controla ocupación y sector, así que mide la brecha territorial **dentro del mismo tipo de trabajo**. La brecha total, que incluye el hecho de que el Sur rural tiene otra estructura ocupacional, es la que responde a la pregunta de desigualdad regional de la tesina.

**Qué hacer.** Para cada celda región × localidad y cada año, frente a Centro, urbana grande:
1. **Bruta:** diferencia de medias de ln(1+y), sin controles.
2. **M3 con región × localidad:** `ESPECIFICACIONES["M3_variables_excluidas"] + ["region_banxico:tam_loc_grupo"]`, es decir, la asociación total sin ocupación ni sector, con la misma maquinaria contrafactual.
3. **M5:** la actual.

**Figura:** los tres puntos para cada celda.

**Lectura:**
- de la bruta a M3: la diferencia que se explica por características individuales;
- de M3 a M5: lo que opera a través de la ocupación y el sector;
- M5: la brecha que queda entre personas con el mismo tipo de trabajo.

---

## H. Correcciones de redacción ✏️

Ninguna requiere volver a ejecutar.

1. **Notebook 15, §9, "Qué dice Box–Cox", punto 6.** Dice: "Comprime de más la cola baja, lo que deja asimetría negativa en los residuos." Debería decir: "Estira de más la cola baja: separa mucho los ingresos muy pequeños del resto, lo que deja asimetría negativa en los residuos." En log, 30 y 3,000 pesos quedan a la misma distancia que 3,000 y 300,000; con λ = 0.22, la primera distancia es un tercio de la segunda.
2. **Notebook 15, mismo punto.** Dice: "Ese costo se atiende con estimadores que no dependen de la normalidad (Huber, regresión cuantílica), con la corrección de Duan por grupo al volver a pesos y con la sensibilidad λ ≈ 0.25 pendiente." Duan no cambia los coeficientes ni corrige la asimetría; solo corrige la conversión a pesos promedio. Propuesta: "Ese costo se atiende con estimadores que no dependen de la normalidad (Huber, regresión cuantílica) y con la sensibilidad Box–Cox λ ≈ 0.25 del notebook 17. La corrección de Duan es otro asunto: solo se necesita para expresar predicciones como pesos promedio."
3. **Notebook 15, recomendación 3 de la síntesis** ("Retransformar a pesos con Duan por grupo"). Agregar: "solo cuando se reporten pesos promedio; los efectos porcentuales no la requieren".
4. **`reports/recorrido_y_resultados_determinantes.md`, sección de escala (cerca de la línea 158).** Cambiar "se atiende con la regresión cuantílica y la corrección de Duan" por "se atiende con Huber y la regresión cuantílica; Duan solo corrige la conversión a pesos promedio".

## I. Actualizar el reporte (al final)

En `reports/recorrido_y_resultados_determinantes.md`:
- sustituir las cifras cuantílicas de M4 por las de M5 del 17 (hoy se mezclan especificaciones);
- agregar la robustez (C), la escala por grupo (A), Box–Cox con λ = 0.25 (D), los ponderadores (E), las capas territoriales (G) y la tabla de referencias (F1);
- cerrar el pendiente de escala en "Limitaciones" y responder las decisiones 2, 3 y 6 de la sección 6;
- agregar el 17 y su tiempo de ejecución a "Cómo reproducir".

## Fuera de alcance por ahora

- **PPML o modelar la media:** descartado, porque la media no es el objetivo.
- **Modelo de dos partes para ingresos muy bajos:** Huber y la cuantílica ya miden su influencia.
- **Selección (Heckman):** queda como limitación. Una opción barata es una tabla de la tasa de ingreso positivo por sexo y año, para mostrar la composición de la muestra.
- **Interacción triple sexo × región × localidad:** solo si la brecha de género por celda es una pregunta de la tesina, y tendría que pasar la misma regla de BIC y validación cruzada del 15.
- **Spline de edad:** candidata del 15, de prioridad baja.

## Lista de verificación

- [ ] `git pull` y rama nueva
- [ ] Notebook 17 (A a E) con submuestra
- [ ] Validaciones:
  - [ ] AME de OLS iguales a las del 16
  - [ ] Box–Cox conjunto igual al del 15
  - [ ] R² por grupo iguales a los de la §12 del 15
  - [ ] métrica Box–Cox con λ = 0 igual a la AME en log
- [ ] Notebook 17 completo y exportado
- [ ] Notebook 16: F1 a F5 y G; ejecutarlo completo
- [ ] Correcciones H
- [ ] Reporte (I)
- [ ] Commit; push solo con autorización

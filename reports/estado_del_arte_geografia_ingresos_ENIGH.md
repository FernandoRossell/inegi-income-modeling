# Estado del arte y decisiones metodológicas  
## Análisis de ingresos, desigualdad y estratificación geográfica con ENIGH 2018–2024

**Fecha de elaboración:** 29 de agosto de 2026  
**Proyecto:** `inegi-income-modeling`  
**Propósito del documento:** dejar un punto de referencia metodológico y bibliográfico para el proyecto, de modo que futuras etapas —incluidos notebooks y trabajo con agentes— partan de decisiones ya documentadas y de fuentes oficiales.

---

## 1. Contexto del proyecto

El proyecto utiliza microdatos de la **Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH)** para los años:

- 2018
- 2020
- 2022
- 2024

El objetivo general es estudiar los **determinantes del ingreso en México**, su evolución temporal y las diferencias socioeconómicas y territoriales asociadas.

A la fecha, el proyecto ya cuenta con avances en:

- homologación de tablas entre años;
- limpieza de tipos;
- corrección de inconsistencias específicas de 2024;
- incorporación de información geográfica;
- construcción de una llave municipal mediante `ubica_geo`;
- revisión de relaciones entre tablas;
- preparación de bases analíticas a nivel persona y hogar;
- exploración mediante EDA y un dashboard con `ipywidgets`.

La dimensión geográfica se incorporó inicialmente mediante:

```text
ubica_geo = Clave de AGEE + Clave de AGEM
```

Con esta llave se obtuvo cobertura de 100% en los cruces realizados con `concentradohogar` y `viviendas`, incorporando:

```text
cve_ent
entidad
cve_mun
municipio
```

No se asignó localidad, latitud ni longitud a los hogares, porque `ubica_geo` identifica de forma segura entidad + municipio, no una localidad exacta.

---

# 2. Pregunta que motivó esta revisión

Antes de construir una estratificación geográfica propia, se buscó responder:

> **¿Existen ya estratificaciones geográficas o socioeconómicas oficiales utilizadas en ENIGH o en análisis de ingreso y desigualdad que podamos aprovechar, en lugar de crear una clasificación completamente nueva?**

La respuesta es **sí**.

Se identificaron tres antecedentes particularmente relevantes:

1. **Estratificación geográfica y socioeconómica del propio diseño muestral de INEGI.**
2. **Regionalización utilizada por Banco de México para análisis económicos regionales y análisis basados en ENIGH.**
3. **Índices territoriales de marginación de CONAPO a nivel entidad y municipio.**

Estos antecedentes deben considerarse antes de diseñar una clasificación territorial nueva mediante clustering u otros métodos propios.

---

# 3. Estratificación oficial dentro del diseño muestral de ENIGH

## 3.1 Diseño estadístico

INEGI documenta que ENIGH 2024 tiene un diseño:

- probabilístico;
- estratificado;
- multietápico;
- por conglomerados.

La cobertura para estimaciones está diseñada a nivel:

- nacional;
- entidad federativa;
- con cortes urbano y rural.

La unidad última de selección es la vivienda y la unidad de observación es el hogar.

**Fuente oficial:**

INEGI — ENIGH 2024  
https://www.inegi.org.mx/programas/enigh/nc/2024/

Diseño muestral ENIGH 2024:  
https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/889463924517.pdf

---

## 3.2 Estratificación geográfica de las UPM

El diseño muestral de INEGI señala que, después de construir las **Unidades Primarias de Muestreo (UPM)**, estas se agrupan por características similares.

INEGI reconoce una estratificación geográfica natural derivada de:

```text
entidad federativa
+
tamaño de localidad
```

En cada entidad se distinguen tres ámbitos:

| Ámbito | Definición |
|---|---|
| Urbano alto | Áreas urbanas de 100,000 habitantes o más |
| Complemento urbano | 2,500 a 99,999 habitantes |
| Rural | Localidades menores de 2,500 habitantes |

Esta clasificación es especialmente importante porque demuestra que **el tamaño de localidad no es únicamente una variable descriptiva**, sino que forma parte de la lógica de estratificación utilizada por INEGI.

### Implicación para el proyecto

La variable `tam_loc` debe considerarse una dimensión territorial relevante.

Antes de crear una división urbano/rural propia, debe revisarse la codificación oficial de `tam_loc` para cada levantamiento y, cuando sea posible, trabajar con la clasificación oficial.

---

# 4. Estratificación socioeconómica oficial de INEGI

Además de la estratificación geográfica, INEGI construye **cuatro estratos socioeconómicos** para las UPM.

La documentación de ENIGH 2024 señala que esta clasificación considera:

- características sociodemográficas de los habitantes;
- características físicas de las viviendas;
- equipamiento de las viviendas.

Para ello se utilizan **42 indicadores construidos a partir del Censo de Población y Vivienda** y se aplican **métodos estadísticos multivariados**.

Cada UPM queda clasificada en:

```text
1 estrato geográfico
+
1 estrato socioeconómico
```

Para la muestra maestra utilizada se reportan **1,175 estratos a nivel nacional**.

**Fuente oficial:**

INEGI — ENIGH 2024, Diseño muestral, sección 4.2 Estratificación  
https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/889463924517.pdf

---

## 4.1 Variable `est_socio`

En las bases ENIGH existe una variable asociada al estrato socioeconómico:

```text
est_socio
```

La interpretación concreta y sus etiquetas deben verificarse en los diccionarios/documentación de cada año antes de utilizarse.

### Decisión para el proyecto

No debemos construir inmediatamente un clustering socioeconómico propio sin antes evaluar qué capacidad explicativa tiene:

```text
est_socio
```

porque ya representa una clasificación oficial basada en información censal y métodos multivariados.

Una posible pregunta exploratoria es:

> ¿Cuánto cambia la distribución del ingreso entre estratos socioeconómicos oficiales de INEGI?

Posteriormente:

> ¿Las asociaciones entre educación, trabajo, características del hogar e ingreso son distintas entre estratos socioeconómicos?

---

# 5. Importante: estratificación de diseño no equivale automáticamente a nivel de inferencia

Debemos distinguir:

```text
estrato de diseño
≠
dominio de inferencia
```

Que una observación pertenezca a un estrato no significa que podamos producir estimaciones representativas independientes para cualquier combinación arbitraria de:

```text
municipio × estrato × año
```

INEGI indica que la ENIGH 2024 está diseñada para obtener resultados a nivel nacional y entidad federativa, con cortes urbano/rural.

Por lo tanto:

### Uso defendible

- nacional;
- entidad federativa;
- urbano/rural;
- estratos y variables del diseño como variables explicativas o de segmentación;
- análisis exploratorios de subgrupos.

### Requiere precaución

- inferencia municipal;
- estimaciones para municipios con pocas observaciones;
- cruces muy finos de municipio × estrato × categoría;
- interpretación de diferencias pequeñas sin errores de muestreo.

---

# 6. Regionalización de Banco de México

Banco de México utiliza una regionalización de cuatro grupos en sus **Reportes sobre las Economías Regionales**.

## 6.1 Regiones

### Norte

- Baja California
- Chihuahua
- Coahuila
- Nuevo León
- Sonora
- Tamaulipas

### Centro Norte

- Aguascalientes
- Baja California Sur
- Colima
- Durango
- Jalisco
- Michoacán
- Nayarit
- San Luis Potosí
- Sinaloa
- Zacatecas

### Centro

- Ciudad de México
- Estado de México
- Guanajuato
- Hidalgo
- Morelos
- Puebla
- Querétaro
- Tlaxcala

### Sur

- Campeche
- Chiapas
- Guerrero
- Oaxaca
- Quintana Roo
- Tabasco
- Veracruz
- Yucatán

**Fuente oficial:**

Banco de México — Reporte sobre las Economías Regionales, Anexo de indicadores  
https://www.banxico.org.mx/publicaciones-y-prensa/reportes-sobre-las-economias-regionales/

Ejemplo de reporte donde se documenta la regionalización:  
https://www.banxico.org.mx/publicaciones-y-prensa/reportes-sobre-las-economias-regionales/%7BC3FA7255-FE4B-B86E-D75C-0FBF133D96C0%7D.pdf

---

# 7. Banco de México ya ha utilizado ENIGH para análisis regional del ingreso

Este es uno de los antecedentes más cercanos al proyecto.

Banco de México ha utilizado información derivada de ENIGH para estudiar:

- desigualdad;
- índice de Gini;
- fuentes de ingreso;
- diferencias regionales;
- pobreza por ingresos;
- cambios entre levantamientos.

Esto significa que un análisis puramente descriptivo del tipo:

> ingreso medio por región

o:

> Gini por región

**no sería por sí mismo una contribución novedosa**, porque ya existen antecedentes oficiales muy cercanos.

---

## 7.1 Gini por región, 2018–2022

Banco de México reporta los siguientes valores aproximados del índice de Gini:

| Región | 2018 | 2020 | 2022 |
|---|---:|---:|---:|
| Norte | 43.1 | 43.7 | 40.3 |
| Centro norte | 43.2 | 41.3 | 40.4 |
| Centro | 45.1 | 44.5 | 42.1 |
| Sur | 47.5 | 45.8 | 44.9 |
| Nacional | 45.7 | 45.0 | 43.1 |

En esos resultados el **Sur presenta sistemáticamente mayor desigualdad** que las demás regiones.

**Fuente oficial:**

Banco de México — Índice de Gini regional  
https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/enero-marzo-2024/B586F8E3-3995-4307-9DF0-B47A82841869.html

La fuente reportada por Banxico corresponde a cálculos realizados a partir de bases de CONEVAL que utilizan la ENIGH publicada por INEGI.

---

## 7.2 Descomposición del Gini por fuente de ingreso

Banco de México también ha descompuesto la desigualdad regional según:

- trabajo subordinado;
- trabajo independiente;
- renta de propiedad;
- transferencias;
- otros ingresos.

**Fuente oficial:**

Banco de México — Descomposición del índice de Gini por fuente de ingreso de los hogares  
https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/enero-marzo-2024/86034969-E628-4D2B-A08A-D0A688D7D1BF.html

### Implicación

Nuestro proyecto no debería limitarse a repetir:

```text
región
→ Gini
→ fuente de ingreso
```

porque este análisis ya tiene un antecedente oficial directo.

---

# 8. Banco de México ya incorpora ENIGH 2024

También existen resultados de Banco de México que comparan **2018–2024**.

Un ejemplo es la contribución de diferentes fuentes al crecimiento real del ingreso corriente total per cápita.

El análisis distingue:

- ingreso laboral;
- trabajo subordinado;
- trabajo independiente;
- otros ingresos laborales;
- rentas;
- transferencias;
- ingreso no monetario.

Y los resultados se presentan por:

```text
región
×
decil de ingreso
```

**Fuente oficial:**

Banco de México — Contribución de las fuentes de ingreso al crecimiento real del ingreso corriente total per cápita, 2018–2024  
https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/julio-septiembre-2025/D323E8D0-8B01-4DE9-942E-208224E831EA.html

### Implicación para la investigación

El componente temporal:

```text
2018
2020
2022
2024
```

sigue siendo relevante, pero la contribución del proyecto debe ir más allá de documentar que el ingreso cambió.

El enfoque debería avanzar hacia:

> **qué variables explican esas diferencias y si sus asociaciones cambian por territorio y a través del tiempo.**

---

# 9. CONAPO: marginación como estratificación territorial

CONAPO mantiene una línea oficial de análisis territorial mediante los **Índices de Marginación**.

El índice de marginación funciona como una medida resumen de carencias asociadas a dimensiones como:

- educación;
- vivienda;
- ingresos;
- distribución territorial;
- residencia en localidades pequeñas.

Se producen resultados para distintos niveles geográficos, incluyendo:

- entidad federativa;
- municipio;
- localidad;
- AGEB urbana;
- en ejercicios recientes, colonia.

**Fuentes oficiales:**

CONAPO — Índices de marginación 2020  
https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372

CONAPO — Índice de marginación por entidad federativa y municipio 2020  
https://www.gob.mx/conapo/es/articulos/indice-de-marginacion-por-entidad-federativa-y-municipio-2020-271404

Nota técnico-metodológica:  
https://www.gob.mx/cms/uploads/attachment/file/685354/Nota_te_cnica_IMEyM_2020.pdf

Datos abiertos:  
https://www.datos.gob.mx/es/dataset/indices_marginacion

---

# 10. ¿Conviene construir un índice territorial propio?

Por ahora, **no como primera opción**.

Ya existen al menos tres clasificaciones institucionales relevantes:

```text
INEGI:
tam_loc / ámbito geográfico
+
est_socio

Banco de México:
región económica

CONAPO:
índice y grado de marginación
```

Construir inmediatamente un clustering propio podría:

- duplicar esfuerzos;
- dificultar la interpretación;
- introducir arbitrariedad;
- reducir comparabilidad con literatura y fuentes oficiales.

### Decisión actual

Primero probar las clasificaciones existentes.

Solo crear una estratificación nueva si podemos demostrar que:

1. responde una pregunta que las clasificaciones actuales no cubren;
2. aporta información adicional;
3. tiene una justificación metodológica clara;
4. es estable entre años.

---

# 11. Estructura territorial propuesta para el proyecto

Se propone trabajar con varios niveles complementarios.

## Nivel A — Región Banco de México

Nueva variable:

```text
region_banxico
```

Valores:

```text
Norte
Centro Norte
Centro
Sur
```

### Propósito

- comparación directa con antecedentes de Banxico;
- análisis regional interpretable;
- reducción de dimensionalidad frente a 32 entidades;
- comparación de determinantes del ingreso entre grandes regiones.

---

## Nivel B — Entidad federativa

Variables:

```text
cve_ent
entidad
```

### Propósito

- análisis con un nivel geográfico respaldado por el diseño de ENIGH;
- comparación entre estados;
- análisis de heterogeneidad territorial.

---

## Nivel C — Tamaño de localidad

Variable:

```text
tam_loc
```

y, cuando esté disponible y correctamente decodificada:

```text
tam_loc_desc
```

### Propósito

Capturar urbanización/ruralidad.

Debe revisarse su codificación por año antes de hacer una homologación.

---

## Nivel D — Estrato socioeconómico

Variable:

```text
est_socio
```

y su descripción oficial:

```text
est_socio_desc
```

### Propósito

Incorporar una clasificación socioeconómica oficial vinculada con la muestra maestra.

---

## Nivel E — Municipio

Variables:

```text
cve_mun
municipio
ubica_geo
```

### Propósito

Usarlo principalmente como:

- contexto;
- enriquecimiento externo;
- EDA;
- análisis exploratorio;
- unión con indicadores municipales.

### Precaución

No asumir representatividad municipal.

Para cualquier tabla o gráfica municipal se debe mostrar:

```text
n observaciones
```

y preferentemente permitir un umbral mínimo de observaciones.

---

# 12. Posible incorporación futura de marginación municipal

La relación municipal ya validada permite potencialmente enriquecer ENIGH con datos de CONAPO.

Pipeline conceptual:

```text
ENIGH
   |
   | ubica_geo
   v
Municipio
   |
   +--> Índice de marginación CONAPO
   +--> Grado de marginación
   +--> indicadores territoriales
```

Esto podría ser más informativo que usar el nombre del municipio como una variable categórica con miles de niveles.

### Posibles variables contextuales

- índice de marginación;
- grado de marginación;
- población municipal;
- indicadores de vivienda;
- escolaridad;
- acceso a servicios;
- otros indicadores oficiales.

Esto debe tratarse como una **fase de enriquecimiento contextual**, no como sustituto de las características individuales y del hogar de ENIGH.

---

# 13. Estructura conceptual del modelo analítico

Una observación a nivel persona podría organizarse como:

```text
PERSONA
+
TRABAJO
+
HOGAR
+
VIVIENDA
+
CONTEXTO TERRITORIAL
```

Esquemáticamente:

```text
Ingreso individual
        ↑
        |
------------------------------------------------
|            |           |          |           |
Persona    Trabajo      Hogar     Vivienda   Territorio
```

Variables potenciales:

### Persona

- edad;
- sexo;
- educación;
- estado conyugal;
- etnia;
- discapacidad;
- seguridad social.

### Trabajo

- posición;
- horas;
- sector;
- número de trabajos;
- prestaciones;
- características del trabajo principal.

### Hogar

- composición;
- tamaño;
- condiciones económicas;
- equipamiento.

### Vivienda

- materiales;
- servicios;
- tenencia;
- infraestructura.

### Territorio

- región Banxico;
- entidad;
- tamaño de localidad;
- estrato socioeconómico;
- municipio;
- potencialmente marginación CONAPO.

---

# 14. Pregunta de investigación refinada

Después de revisar estos antecedentes, una formulación más diferenciada respecto al estado del arte sería:

> **¿Cómo cambian los determinantes individuales, laborales, familiares y territoriales del ingreso en México entre 2018 y 2024, y en qué medida estas asociaciones son heterogéneas entre regiones, entidades, niveles de urbanización y estratos socioeconómicos?**

Esto es preferible a una pregunta limitada a:

> ¿Qué región tiene mayor ingreso?

o:

> ¿Qué región tiene mayor desigualdad?

porque esos resultados ya han sido documentados por instituciones como Banco de México.

---

# 15. Diferenciación respecto a antecedentes oficiales

## Lo que ya existe

### INEGI

- diseño muestral estratificado;
- estratos geográficos;
- estratos socioeconómicos;
- resultados por entidad y urbano/rural.

### Banco de México

- Gini por región;
- descomposición regional de desigualdad;
- análisis por fuente de ingreso;
- comparación temporal;
- análisis por deciles;
- análisis ENIGH hasta 2024.

### CONAPO

- índices territoriales de marginación;
- clasificación territorial;
- información a nivel entidad, municipio y localidad.

---

## Espacio potencial de aportación del proyecto

El proyecto podría enfocarse en:

```text
Determinantes del ingreso
        ×
territorio
        ×
tiempo
```

más específicamente:

```text
¿La educación tiene la misma asociación con el ingreso
en Norte, Centro Norte, Centro y Sur?

¿El retorno asociado a ciertas características laborales
cambia entre estratos socioeconómicos?

¿La brecha de ingreso por sexo cambia según región
o nivel de urbanización?

¿Las variables asociadas con mayores ingresos
son estables entre 2018, 2020, 2022 y 2024?
```

Este enfoque va más allá de describir niveles de ingreso y permite estudiar **heterogeneidad de asociaciones**.

---

# 16. Decisiones metodológicas actuales

A partir de esta revisión, se adoptan provisionalmente las siguientes decisiones.

## Decisión 1 — No crear todavía una estratificación geográfica propia

Primero utilizar:

```text
region_banxico
entidad
tam_loc
est_socio
```

y evaluar su utilidad.

---

## Decisión 2 — Mantener municipio como nivel contextual/exploratorio

Municipio puede utilizarse para:

- EDA;
- enriquecimiento externo;
- modelos con variables contextuales;
- visualización.

No debe presentarse automáticamente como dominio representativo de ENIGH.

---

## Decisión 3 — Incorporar `region_banxico`

Construir una variable determinística a partir de `cve_ent` o `entidad`.

El mapping debe quedar explícito en código y documentado.

No utilizar fuzzy matching.

---

## Decisión 4 — Decodificar `tam_loc` y `est_socio`

Utilizar la documentación oficial de:

```text
doc_2018.pdf
doc_2020.pdf
doc_2022.pdf
doc_2024.pdf
```

para comprobar que sus códigos sean comparables.

No asumir que el mapping de 2024 aplica automáticamente a años anteriores.

---

## Decisión 5 — Evaluar CONAPO como enriquecimiento municipal

No incorporarlo todavía de forma automática.

Primero revisar:

- disponibilidad temporal;
- comparabilidad;
- año de referencia;
- si utilizar 2020 como característica contextual fija es apropiado para 2018–2024;
- posibles problemas de endogeneidad o interpretación.

---

## Decisión 6 — Incorporar diseño muestral en análisis formales

Antes de producir resultados inferenciales:

- revisar `factor`;
- revisar `est_dis`;
- revisar `upm`;
- utilizar ponderadores;
- considerar efectos del diseño;
- reportar precisión de estimaciones cuando corresponda.

---

# 17. Aplicación al dashboard exploratorio

El dashboard debe permitir seleccionar el nivel geográfico.

Propuesta:

```text
Nivel geográfico
│
├── Nacional
├── Región Banco de México
├── Entidad federativa
├── Tamaño de localidad
├── Estrato socioeconómico
└── Municipio [exploratorio]
```

Para municipio:

- mostrar `n`;
- permitir mínimo de observaciones;
- incluir una advertencia metodológica.

---

# 18. Siguiente etapa sugerida de investigación

Antes de construir modelos definitivos:

1. crear `region_banxico`;
2. homologar `tam_loc`;
3. homologar `est_socio`;
4. comprobar disponibilidad por 2018/2020/2022/2024;
5. incorporar estas variables a `mart_persona` y `mart_hogar`;
6. explorar ingreso por cada estratificación;
7. comparar capacidad explicativa;
8. estudiar interacciones;
9. decidir si se justifica una regionalización propia adicional.

---

# 19. Hipótesis exploratorias posibles

Estas hipótesis son provisionales y deben tratarse como preguntas de análisis, no como conclusiones.

### H1

La asociación entre educación e ingreso cambia entre las regiones de Banco de México.

### H2

El estrato socioeconómico de INEGI aporta información adicional sobre ingreso incluso controlando por características individuales.

### H3

Las características laborales tienen distinta importancia entre contextos urbanos y rurales.

### H4

Las asociaciones entre características personales y laborales e ingreso no son completamente estables entre 2018 y 2024.

### H5

Las variables municipales de contexto pueden aportar poder explicativo adicional, aunque el municipio no sea utilizado como dominio de inferencia directa.

---

# 20. Precauciones para agentes y análisis futuros

Cuando un agente utilice este documento como contexto debe respetar las siguientes reglas.

### No asumir causalidad

Una relación:

```text
X asociado con ingreso
```

no significa:

```text
X causa ingreso
```

---

### No asumir representatividad municipal

La existencia de `municipio` no convierte automáticamente la encuesta en representativa para cada municipio.

---

### No crear nuevos estratos sin justificación

Antes de clustering o segmentación nueva:

1. revisar `region_banxico`;
2. revisar `tam_loc`;
3. revisar `est_socio`;
4. revisar marginación CONAPO.

---

### No ignorar el diseño muestral

Para inferencia formal se deben considerar:

```text
factor
est_dis
upm
```

según lo que permita cada año.

---

### No copiar mappings entre años sin validarlos

Aplica a:

- categóricas;
- `tam_loc`;
- `est_socio`;
- diseño muestral;
- cualquier otra variable codificada.

---

# 21. Fuentes oficiales principales

## INEGI

### ENIGH 2024

https://www.inegi.org.mx/programas/enigh/nc/2024/

Contiene:

- microdatos;
- documentación;
- diseño conceptual;
- diseño muestral;
- cuestionarios;
- resultados.

### Diseño muestral ENIGH 2024

https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/889463924517.pdf

Especialmente relevante:

- cobertura geográfica;
- UPM;
- estratificación geográfica;
- estratificación socioeconómica;
- factores de expansión;
- estimadores;
- errores de muestreo.

---

## Banco de México

### Reportes sobre las Economías Regionales

https://www.banxico.org.mx/publicaciones-y-prensa/reportes-sobre-las-economias-regionales/

### Índice de Gini regional 2018–2022

https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/enero-marzo-2024/B586F8E3-3995-4307-9DF0-B47A82841869.html

### Descomposición del Gini por fuente de ingreso

https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/enero-marzo-2024/86034969-E628-4D2B-A08A-D0A688D7D1BF.html

### Fuentes de ingreso y crecimiento real, 2018–2024

https://www.banxico.org.mx/TablasWeb/reportes-economias-regionales/julio-septiembre-2025/D323E8D0-8B01-4DE9-942E-208224E831EA.html

---

## CONAPO

### Índices de marginación 2020

https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372

### Índice de marginación por entidad federativa y municipio 2020

https://www.gob.mx/conapo/es/articulos/indice-de-marginacion-por-entidad-federativa-y-municipio-2020-271404

### Nota técnico-metodológica

https://www.gob.mx/cms/uploads/attachment/file/685354/Nota_te_cnica_IMEyM_2020.pdf

### Datos abiertos

https://www.datos.gob.mx/es/dataset/indices_marginacion

---

# 22. Fuente complementaria no gubernamental

Para una futura sección sobre **movilidad social**, puede revisarse adicionalmente el trabajo del **Centro de Estudios Espinosa Yglesias (CEEY)**.

Es una fuente de investigación especializada, pero **no es una fuente gubernamental oficial**.

Puede ser útil para comparar regionalizaciones utilizadas en estudios de movilidad social y para ampliar el estado del arte más allá de las instituciones públicas.

Sitio:

https://ceey.org.mx/

Esta fuente debe mantenerse claramente diferenciada de INEGI, Banco de México, CONAPO y CONEVAL.

---

# 23. Conclusión provisional

La revisión del estado del arte sugiere que **no es necesario construir desde cero una estratificación geográfica para comenzar el análisis**.

Ya existen clasificaciones oficiales y ampliamente utilizadas que cubren dimensiones complementarias:

```text
INEGI
→ estratificación del diseño
→ tamaño de localidad
→ estrato socioeconómico

Banco de México
→ regiones económicas

CONAPO
→ marginación territorial
```

La estrategia recomendada para la tesina es utilizar estas clasificaciones como punto de partida y concentrar la aportación en estudiar:

> **cómo cambian los determinantes del ingreso entre contextos territoriales y a través del tiempo.**

Esto permite aprovechar trabajo metodológico ya desarrollado por instituciones oficiales, mejorar la comparabilidad de resultados y evitar construir una regionalización arbitraria sin necesidad.

---

# 24. Instrucción de uso para agentes

Cuando este archivo sea referenciado en un prompt posterior, debe utilizarse como **contexto metodológico del proyecto**.

El agente debe:

1. leer este documento antes de proponer nuevas clasificaciones geográficas;
2. priorizar variables oficiales existentes;
3. respetar las limitaciones de inferencia;
4. documentar cualquier desviación respecto a estas decisiones;
5. no sustituir estas decisiones sin evidencia metodológica nueva;
6. consultar nuevamente las fuentes oficiales cuando una definición específica sea necesaria.

Este documento representa el **estado actual de las decisiones**, no una restricción permanente.

Puede actualizarse si el análisis posterior demuestra que otra clasificación tiene una justificación más sólida.

# Validacion opcional contra survey::svrepdesign.
# Ejecutar manualmente en un entorno con R, survey y readr instalados.

library(readr)
library(survey)

root <- normalizePath(".", mustWork = TRUE)
toy <- data.frame(
  anio = rep(2024, 8),
  est_dis = c("A","A","A","A","B","B","B","B"),
  upm = c("1","1","2","2","3","3","4","4"),
  factor = c(1.0,1.2,0.9,1.1,1.5,1.0,0.8,1.3),
  y = c(10,12,18,20,8,11,30,33),
  region = c("Norte","Norte","Sur","Sur","Norte","Sur","Sur","Norte")
)

design <- svydesign(
  ids = ~upm,
  strata = ~est_dis,
  weights = ~factor,
  data = toy,
  nest = TRUE
)

rep_design <- as.svrepdesign(design, type = "JKn", mse = TRUE)
print(svymean(~y, rep_design))
print(svyby(~y, ~region, rep_design, svymean))

# Comparar contra reports/tables/diseno_muestral/validaciones_diseno_muestral.csv
# en las filas toy cuando se use un entorno R disponible.

"""Build ENIGH metadata documentation from raw CSV headers.

The script reads the CSV files under data/raw/EINGH/<year>/ and writes a
Markdown document with table availability, row counts, join keys, and columns.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from extract_enigh_pdf_metadata import OUTPUT as PDF_METADATA_CSV
from extract_enigh_pdf_metadata import extract_pdf_metadata, write_csv


ROOT = Path("data/raw/EINGH")
OUT = Path("docs/metadata_enigh.md")
YEARS = ["2018", "2020", "2022", "2024"]


TABLE_METADATA = {
    "viviendas.csv": {
        "level": "Vivienda",
        "desc": "Caracteristicas fisicas y de servicios de la vivienda.",
        "pdf_keys": "Llave primaria: folioviv.",
        "key": "`folioviv`",
        "fk": "No aplica dentro de ENIGH; es tabla raiz a nivel vivienda.",
        "joins": "`hogares.csv` y `concentradohogar.csv` mediante `folioviv`.",
    },
    "hogares.csv": {
        "level": "Hogar",
        "desc": "Caracteristicas del hogar, acceso a alimentacion y variables de contexto del hogar.",
        "pdf_keys": "Llave foranea: folioviv. Llave primaria: foliohog.",
        "key": "`folioviv` + `foliohog`",
        "fk": "`folioviv` -> `viviendas.csv`.",
        "joins": "Tabla eje para bases a nivel hogar y persona.",
    },
    "concentradohogar.csv": {
        "level": "Hogar resumido",
        "desc": "Tabla resumen con variables construidas a partir de las bases ENIGH; incluye ingresos y gastos trimestrales agregados.",
        "pdf_keys": "Llave foranea: folioviv, foliohog.",
        "key": "`folioviv` + `foliohog`",
        "fk": "`folioviv` + `foliohog` -> `hogares.csv`.",
        "joins": "Principal tabla agregada para analisis descriptivo a nivel hogar.",
    },
    "poblacion.csv": {
        "level": "Persona / integrante del hogar",
        "desc": "Caracteristicas sociodemograficas de los integrantes del hogar.",
        "pdf_keys": "Llave foranea: folioviv, foliohog. Llave primaria: numren.",
        "key": "`folioviv` + `foliohog` + `numren`",
        "fk": "`folioviv` + `foliohog` -> `hogares.csv`.",
        "joins": "Base eje para integrar ingresos, trabajos y gastos personales.",
    },
    "trabajos.csv": {
        "level": "Trabajo de una persona",
        "desc": "Condicion de actividad y caracteristicas de los trabajos de integrantes de 12 anos o mas.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren. Llave primaria: id_trabajo.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo`",
        "fk": "`folioviv` + `foliohog` + `numren` -> `poblacion.csv`.",
        "joins": "Permite vincular condiciones laborales con ingresos y caracteristicas personales.",
    },
    "ingresos.csv": {
        "level": "Ingreso por persona y clave de ingreso",
        "desc": "Ingresos y percepciones financieras y de capital por integrante del hogar.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren. Llave primaria: clave.",
        "key": "`folioviv` + `foliohog` + `numren` + `clave`",
        "fk": "`folioviv` + `foliohog` + `numren` -> `poblacion.csv`.",
        "joins": "Tabla central para construir ingreso laboral individual; requiere seleccionar claves pertinentes.",
    },
    "ingresos_jcf.csv": {
        "level": "Ingreso por persona asociado a Jovenes Construyendo el Futuro",
        "desc": "Ingresos provenientes del programa Jovenes Construyendo el Futuro; disponible desde 2020.",
        "pdf_keys": "Misma estructura de llave que ingresos, con variable adicional `ct_futuro`.",
        "key": "`folioviv` + `foliohog` + `numren` + `clave`",
        "fk": "`folioviv` + `foliohog` + `numren` -> `poblacion.csv`.",
        "joins": "Usar como complemento de ingresos si el alcance metodologico lo requiere.",
    },
    "gastoshogar.csv": {
        "level": "Gasto del hogar",
        "desc": "Gastos monetarios y no monetarios del hogar por clave y caracteristicas de adquisicion/pago.",
        "pdf_keys": "Llave foranea: folioviv, foliohog. Llave primaria compuesta por variables de identificacion del gasto.",
        "key": "`folioviv` + `foliohog` + variables de gasto.",
        "fk": "`folioviv` + `foliohog` -> `hogares.csv`.",
        "joins": "Complementaria para contexto de gasto; no es eje principal del ingreso laboral.",
    },
    "gastospersona.csv": {
        "level": "Gasto personal",
        "desc": "Gastos realizados por integrantes del hogar en rubros personales como educacion y transporte.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren. Llave primaria: clave, tipo_gasto, mes_dia, frec_rem, inst, forma_pag1, forma_pag2, forma_pag3.",
        "key": "`folioviv` + `foliohog` + `numren` + variables de identificacion del gasto.",
        "fk": "`folioviv` + `foliohog` + `numren` -> `poblacion.csv`.",
        "joins": "Complementaria para analisis de gasto personal.",
    },
    "gastotarjetas.csv": {
        "level": "Gasto del hogar con tarjeta",
        "desc": "Gasto efectuado con tarjeta de credito o comercial.",
        "pdf_keys": "Llave foranea: folioviv, foliohog. Llave primaria: clave.",
        "key": "`folioviv` + `foliohog` + `clave`",
        "fk": "`folioviv` + `foliohog` -> `hogares.csv`.",
        "joins": "Complementaria de gasto del hogar.",
    },
    "erogaciones.csv": {
        "level": "Erogacion financiera o de capital del hogar",
        "desc": "Erogaciones del hogar por clave y meses de referencia.",
        "pdf_keys": "Llave foranea: folioviv, foliohog. Llave primaria: clave.",
        "key": "`folioviv` + `foliohog` + `clave`",
        "fk": "`folioviv` + `foliohog` -> `hogares.csv`.",
        "joins": "Complementaria para finanzas del hogar.",
    },
    "agro.csv": {
        "level": "Negocio agropecuario asociado a un trabajo",
        "desc": "Informacion de trabajadores independientes con actividades agropecuarias.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo. Llave primaria: tipoact.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact`",
        "fk": "`folioviv` + `foliohog` + `numren` + `id_trabajo` -> `trabajos.csv`.",
        "joins": "Complementaria para ingresos/actividad independiente agropecuaria.",
    },
    "noagro.csv": {
        "level": "Negocio no agropecuario asociado a un trabajo",
        "desc": "Informacion de negocios no agropecuarios del hogar.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo. Llave primaria: tipoact.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact`",
        "fk": "`folioviv` + `foliohog` + `numren` + `id_trabajo` -> `trabajos.csv`.",
        "joins": "Complementaria para actividad independiente no agropecuaria.",
    },
    "agroproductos.csv": {
        "level": "Producto agropecuario",
        "desc": "Productos del negocio agropecuario y su uso/destino.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo, tipoact.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact` + `numprod` + `codigo` + `cosecha`",
        "fk": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact` -> `agro.csv`.",
        "joins": "Disponible desde 2020; complementaria para negocios agropecuarios.",
    },
    "agroconsumo.csv": {
        "level": "Destino/consumo de producto agropecuario",
        "desc": "Destino, cantidad y valor estimado de productos del negocio agropecuario.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo, tipoact, numprod, codigo, cosecha. Llave primaria: destino.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact` + `numprod` + `codigo` + `cosecha` + `destino`",
        "fk": "Producto agropecuario identificado por las llaves anteriores.",
        "joins": "Disponible desde 2020; complementaria.",
    },
    "agrogasto.csv": {
        "level": "Gasto de negocio agropecuario",
        "desc": "Tipo de gasto realizado por el negocio agropecuario.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo, tipoact. Llave primaria: clave.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact` + `clave`",
        "fk": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `tipoact` -> `agro.csv`.",
        "joins": "Disponible desde 2020; complementaria.",
    },
    "noagroimportes.csv": {
        "level": "Importe de negocio no agropecuario",
        "desc": "Importes mensuales de negocios no agropecuarios del hogar.",
        "pdf_keys": "Llave foranea: folioviv, foliohog, numren, id_trabajo. Llave primaria: clave.",
        "key": "`folioviv` + `foliohog` + `numren` + `id_trabajo` + `clave`",
        "fk": "`folioviv` + `foliohog` + `numren` + `id_trabajo` -> `trabajos.csv` o `noagro.csv` segun especificacion.",
        "joins": "Disponible desde 2020; complementaria para negocios no agropecuarios.",
    },
}


def read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle))


def count_rows(path: Path) -> int:
    with path.open("rb") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def main() -> None:
    pdf_metadata_rows = extract_pdf_metadata()
    write_csv(pdf_metadata_rows)

    schemas: dict[str, dict[str, list[str]]] = defaultdict(dict)
    rows: dict[str, dict[str, int]] = defaultdict(dict)
    pdf_metadata = {}
    pdf_positions = {}

    for row in pdf_metadata_rows:
        key = (row.year, row.table, row.variable)
        pdf_metadata.setdefault(key, {"label": row.label, "dtype": row.dtype})
        pdf_positions.setdefault(key, row.position)

    for path in sorted(ROOT.glob("*/*.csv")):
        year = path.parent.name
        schemas[path.name][year] = read_header(path)
        rows[path.name][year] = count_rows(path)

    tables = sorted(schemas)
    missing_metadata: list[tuple[str, str, str]] = []
    total_columns = 0
    matched_columns = 0
    for table in tables:
        for year in YEARS:
            for variable in schemas[table].get(year, []):
                total_columns += 1
                if (year, table, variable) in pdf_metadata:
                    matched_columns += 1
                else:
                    missing_metadata.append((year, table, variable))

    lines: list[str] = []

    lines.append("# Metadata de microdatos ENIGH para el proyecto")
    lines.append("")
    lines.append(
        "Este documento resume la estructura de los microdatos ENIGH disponibles en el repositorio, "
        "con enfasis en el factor temporal, las relaciones entre tablas, las llaves de union y el "
        "inventario de columnas por ano. Su objetivo es servir como referencia tecnica para presentar "
        "el avance del proyecto y sostener decisiones de limpieza, union y modelado."
    )
    lines.append("")
    lines.append("## Fuentes documentales conservadas")
    lines.append("")
    lines.append("| Ano | Carpeta | Documentacion PDF | CSV disponibles |")
    lines.append("| --- | --- | --- | ---: |")
    pdfs = {
        "2018": "702825188061.pdf",
        "2020": "889463901242.pdf",
        "2022": "889463910626.pdf",
        "2024": "889463924494.pdf",
    }
    for year in YEARS:
        count = sum(1 for table in tables if year in schemas[table])
        lines.append(f"| {year} | `data/raw/EINGH/{year}/` | `{pdfs[year]}` | {count} |")

    lines.extend(
        [
            "",
            "Los PDF se conservan como documentacion oficial de la base de datos. En ellos se especifican la conformacion de la base, la relacion entre tablas, los campos llave y la descripcion de variables. Las secciones mas relevantes para este documento son `1.3.4 Relacion entre las tablas`, `1.4 Diagrama de relacion` y `2.1 Descripcion de las tablas`. Para el trabajo empirico, los CSV son la fuente de datos y los PDF son la fuente de metadatos.",
            "",
            f"Adicionalmente, se genero el archivo tabular `{PDF_METADATA_CSV.as_posix()}` con la metadata extraida de las paginas indicadas de cada PDF. Ese archivo permite auditar de forma directa el ano, tabla, variable, etiqueta, tipo, PDF fuente y pagina fuente.",
            "",
            "## Calidad de la extraccion de metadata",
            "",
            f"La extraccion automatica recupero descripcion y tipo para {matched_columns} de {total_columns} columnas observadas en los CSV ({matched_columns / total_columns:.2%}). Las columnas no recuperadas se conservan en el diccionario con la marca `No extraida del PDF para los anos disponibles`, para evitar completar informacion manualmente sin trazabilidad.",
            "",
            "| Ano | Tabla | Variable sin descripcion extraida |",
            "| --- | --- | --- |",
        ]
    )

    for year, table, variable in missing_metadata:
        lines.append(f"| {year} | `{table}` | `{variable}` |")

    lines.extend(
        [
            "",
            "## Factor temporal",
            "",
            "El proyecto utiliza cuatro levantamientos bienales: 2018, 2020, 2022 y 2024. Los archivos originales no deben combinarse sin agregar una variable temporal explicita. Al apilar tablas entre anos se recomienda crear una columna `anio` con el ano del levantamiento antes de cualquier union vertical.",
            "",
            "Consideraciones temporales importantes:",
            "",
            "- La comparacion temporal debe hacerse entre variables homologas. Algunas tablas cambian de numero de columnas entre levantamientos.",
            "- Las tablas `agroconsumo.csv`, `agrogasto.csv`, `agroproductos.csv`, `ingresos_jcf.csv` y `noagroimportes.csv` estan disponibles desde 2020, pero no en 2018.",
            "- En 2022 y 2024 algunas tablas incorporan variables de diseno o identificacion territorial adicionales, como `entidad`, `est_dis`, `upm` y `factor` en ciertas bases.",
            "- Para estimaciones comparables se debe definir un conjunto comun de variables o documentar las variables especificas de cada periodo.",
            "- Los montos de ingreso y gasto de ENIGH suelen reportarse o construirse en terminos trimestrales en variables agregadas como `ing_tri`, `gasto_tri` y variables de `concentradohogar.csv`; cualquier transformacion mensual o per capita debe documentarse.",
            "",
            "## Inventario general de tablas",
            "",
            "| Tabla | Nivel de observacion | 2018 | 2020 | 2022 | 2024 | Llave practica recomendada |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    for table in tables:
        meta = TABLE_METADATA.get(table, {"level": "Por documentar", "key": "Por validar"})
        values = [str(rows[table][year]) if year in rows[table] else "No disp." for year in YEARS]
        lines.append(
            f"| `{table}` | {meta['level']} | "
            + " | ".join(values)
            + f" | {meta['key']} |"
        )

    lines.extend(
        [
            "",
            "## Relaciones entre tablas y llaves",
            "",
            "La documentacion oficial indica que todas las tablas, excepto `viviendas.csv`, se relacionan con `hogares.csv` mediante `folioviv` y `foliohog`. Las tablas a nivel integrante se relacionan adicionalmente con `poblacion.csv` mediante `numren`. Las tablas de trabajo o negocios incorporan `id_trabajo` y, en algunos casos, `tipoact`, `clave`, `numprod`, `codigo`, `cosecha` o `destino`.",
            "",
            "En la practica, conviene tratar las llaves como compuestas. Por ejemplo, `foliohog` identifica un hogar dentro de una vivienda, pero para unir bases se usa `folioviv + foliohog`. De forma similar, `numren` identifica a una persona dentro del hogar, por lo que la llave practica de persona es `folioviv + foliohog + numren`.",
            "",
            "| Tabla | Llaves segun PDF | Llave practica para analisis | Llaves foraneas / union |",
            "| --- | --- | --- | --- |",
        ]
    )

    for table in tables:
        meta = TABLE_METADATA.get(
            table,
            {"pdf_keys": "Por validar en PDF", "key": "Por validar", "fk": "Por validar"},
        )
        lines.append(f"| `{table}` | {meta['pdf_keys']} | {meta['key']} | {meta['fk']} |")

    lines.extend(
        [
            "",
            "## Diagrama conceptual de relaciones",
            "",
            "```mermaid",
            "erDiagram",
            "    VIVIENDAS ||--o{ HOGARES : folioviv",
            "    HOGARES ||--o{ POBLACION : folioviv_foliohog",
            "    HOGARES ||--|| CONCENTRADOHOGAR : folioviv_foliohog",
            "    HOGARES ||--o{ GASTOSHOGAR : folioviv_foliohog",
            "    HOGARES ||--o{ EROGACIONES : folioviv_foliohog",
            "    HOGARES ||--o{ GASTOTARJETAS : folioviv_foliohog",
            "    POBLACION ||--o{ INGRESOS : folioviv_foliohog_numren",
            "    POBLACION ||--o{ INGRESOS_JCF : folioviv_foliohog_numren",
            "    POBLACION ||--o{ GASTOSPERSONA : folioviv_foliohog_numren",
            "    POBLACION ||--o{ TRABAJOS : folioviv_foliohog_numren",
            "    TRABAJOS ||--o{ AGRO : id_trabajo",
            "    TRABAJOS ||--o{ NOAGRO : id_trabajo",
            "    AGRO ||--o{ AGROPRODUCTOS : tipoact",
            "    AGRO ||--o{ AGROGASTO : tipoact",
            "    AGROPRODUCTOS ||--o{ AGROCONSUMO : numprod_codigo_cosecha",
            "    NOAGRO ||--o{ NOAGROIMPORTES : id_trabajo",
            "```",
            "",
            "## Tablas centrales para el modelo de ingreso",
            "",
            "Para explicar determinantes del ingreso laboral, las tablas prioritarias son:",
            "",
            "- `poblacion.csv`: caracteristicas individuales y sociodemograficas.",
            "- `trabajos.csv`: caracteristicas del trabajo, condicion laboral y prestaciones.",
            "- `ingresos.csv`: ingresos por persona y clave; requiere filtrar claves de ingreso laboral segun la documentacion/codigos ENIGH.",
            "- `concentradohogar.csv`: variables agregadas del hogar, ingreso corriente, gasto, factor de expansion y variables territoriales/diseno.",
            "- `hogares.csv` y `viviendas.csv`: contexto del hogar y vivienda.",
            "",
            "## Cambios de estructura entre anos",
            "",
            "| Tabla | Columnas 2018 | Columnas 2020 | Columnas 2022 | Columnas 2024 | Observacion temporal |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )

    for table in tables:
        counts = [len(schemas[table][year]) if year in schemas[table] else None for year in YEARS]
        present_counts = [count for count in counts if count is not None]
        obs = []
        if counts[0] is None:
            obs.append("No disponible en 2018")
        if len(set(present_counts)) == 1:
            obs.append("Estructura estable en anos disponibles")
        else:
            obs.append("Estructura cambia; revisar columnas antes de apilar")
        count_text = [str(count) if count is not None else "No disp." for count in counts]
        lines.append(f"| `{table}` | " + " | ".join(count_text) + f" | {'; '.join(obs)} |")

    lines.extend(
        [
            "",
            "## Diccionario de columnas por tabla y ano",
            "",
            "La siguiente seccion consolida las columnas observadas en los CSV con las etiquetas y tipos extraidos de la documentacion PDF. La disponibilidad por ano proviene de los encabezados reales de los CSV; la descripcion y el tipo provienen de las paginas de metadata de los PDF.",
        ]
    )

    for table in tables:
        meta = TABLE_METADATA.get(table, {})
        ordered_variables: list[str] = []
        seen_variables: set[str] = set()
        for year in YEARS:
            for variable in schemas[table].get(year, []):
                if variable not in seen_variables:
                    ordered_variables.append(variable)
                    seen_variables.add(variable)

        lines.extend(
            [
                "",
                f"### `{table}`",
                "",
                f"- Nivel de observacion: {meta.get('level', 'Por documentar')}.",
                f"- Descripcion: {meta.get('desc', 'Por documentar con PDF.')}",
                f"- Llave practica recomendada: {meta.get('key', 'Por validar')}.",
                f"- Union principal: {meta.get('joins', 'Por validar')}",
                "",
                "| Variable | 2018 | 2020 | 2022 | 2024 | Descripcion consolidada | Tipo(s) | Posicion(es) PDF |",
                "| --- | :---: | :---: | :---: | :---: | --- | --- | --- |",
            ]
        )

        for variable in ordered_variables:
            availability = ["Si" if variable in schemas[table].get(year, []) else "No" for year in YEARS]
            labels_by_year = {}
            types_by_year = {}
            positions_by_year = {}
            for year in YEARS:
                item = pdf_metadata.get((year, table, variable))
                if item:
                    labels_by_year[year] = item["label"]
                    types_by_year[year] = item["dtype"]
                    positions_by_year[year] = str(pdf_positions[(year, table, variable)])

            distinct_labels: dict[str, list[str]] = defaultdict(list)
            for year, label in labels_by_year.items():
                distinct_labels[label].append(year)

            if not distinct_labels:
                description = "No extraida del PDF para los anos disponibles."
            elif len(distinct_labels) == 1:
                description = next(iter(distinct_labels))
            else:
                description = "; ".join(
                    f"{', '.join(label_years)}: {label}"
                    for label, label_years in distinct_labels.items()
                )

            distinct_types: dict[str, list[str]] = defaultdict(list)
            for year, dtype in types_by_year.items():
                distinct_types[dtype].append(year)
            if not distinct_types:
                dtype_text = "No extraido"
            elif len(distinct_types) == 1:
                dtype_text = next(iter(distinct_types))
            else:
                dtype_text = "; ".join(
                    f"{', '.join(type_years)}: {dtype}"
                    for dtype, type_years in distinct_types.items()
                )

            if positions_by_year:
                position_text = "; ".join(f"{year}: {position}" for year, position in positions_by_year.items())
            else:
                position_text = "No extraida"

            lines.append(
                f"| `{variable}` | "
                + " | ".join(availability)
                + f" | {description} | {dtype_text} | {position_text} |"
            )

    lines.extend(
        [
            "",
            "## Recomendaciones de uso para el analisis",
            "",
            "- Crear una variable `anio` antes de combinar levantamientos.",
            "- Validar unicidad de las llaves practicas con pruebas de duplicados antes de hacer merges.",
            "- Mantener separadas las bases originales en `data/raw/EINGH/` y generar bases armonizadas en `data/processed/`.",
            "- Documentar cualquier homologacion de variables, especialmente en tablas que cambian de columnas entre anos.",
            "- Para inferencia sobre poblacion, revisar el uso de `factor`, `upm`, `est_dis` y otras variables de diseno muestral disponibles por tabla/ano.",
            "- Construir el ingreso laboral a partir de claves de `ingresos.csv` y justificar la seleccion con la documentacion oficial.",
            "- Evitar interpretar coeficientes como causales salvo que se defina una estrategia empirica que lo permita.",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(lines)} lines")


if __name__ == "__main__":
    main()

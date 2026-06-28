"""Extract variable labels and types from ENIGH PDF documentation.

The PDF pages used here contain the official variable lists ("Lista de
variables"). The page ranges are 1-based, as they appear in PDF viewers.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


ROOT = Path("data/raw/EINGH")
OUTPUT = Path("docs/enigh_variable_metadata.csv")

PDF_SPECS = {
    "2018": {"pdf": "702825188061.pdf", "pages": range(16, 31)},
    "2020": {"pdf": "889463901242.pdf", "pages": range(18, 35)},
    "2022": {"pdf": "889463910626.pdf", "pages": range(18, 35)},
    "2024": {"pdf": "889463924494.pdf", "pages": range(19, 36)},
}

TABLE_ALIASES = {
    "AGRO": "agro.csv",
    "AGROCONSUMO": "agroconsumo.csv",
    "AGROGASTO": "agrogasto.csv",
    "AGROPRODUCTOS": "agroproductos.csv",
    "CONCENTRADOHOGAR": "concentradohogar.csv",
    "EROGACIONES": "erogaciones.csv",
    "GASTOSHOGAR": "gastoshogar.csv",
    "GASTOSPERSONA": "gastospersona.csv",
    "GASTOSPERSONAS": "gastospersona.csv",
    "GASTOTARJETAS": "gastotarjetas.csv",
    "HOGARES": "hogares.csv",
    "INGRESOS": "ingresos.csv",
    "INGRESOS_JCF": "ingresos_jcf.csv",
    "NOAGRO": "noagro.csv",
    "NOAGROIMPORTES": "noagroimportes.csv",
    "POBLACION": "poblacion.csv",
    "TRABAJOS": "trabajos.csv",
    "VIVIENDAS": "viviendas.csv",
}


@dataclass(frozen=True)
class VariableMetadata:
    year: str
    table: str
    position: int
    variable: str
    label: str
    dtype: str
    source_pdf: str
    source_page: int


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("�", "")
    return text


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def table_alias(raw_name: str) -> str | None:
    key = strip_accents(raw_name).upper().replace(" ", "").replace("-", "_")
    return TABLE_ALIASES.get(key)


def extract_titles(page: pdfplumber.page.Page) -> list[tuple[float, str]]:
    words = page.extract_words(use_text_flow=False) or []
    titles: list[tuple[float, str]] = []
    for index, word in enumerate(words):
        if clean_text(word.get("text")).lower() != "tabla":
            continue
        top = float(word["top"])
        same_line = [
            candidate
            for candidate in words[index + 1 : index + 5]
            if abs(float(candidate["top"]) - top) < 4
        ]
        if not same_line:
            continue
        name = clean_text(same_line[0].get("text"))
        alias = table_alias(name)
        if alias:
            titles.append((top, alias))
    return titles


def is_variable_row(row: list[object]) -> bool:
    if len(row) < 4:
        return False
    number = clean_text(row[0])
    variable = clean_text(row[1])
    return number.isdigit() and bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", variable))


def extract_rows_from_table(table: list[list[object]]) -> list[tuple[int, str, str, str]]:
    rows: list[tuple[int, str, str, str]] = []
    for row in table:
        if not is_variable_row(row):
            continue
        rows.append(
            (
                int(clean_text(row[0])),
                clean_text(row[1]),
                clean_text(row[2]),
                clean_text(row[3]),
            )
        )
    return rows


def band_tables(page: pdfplumber.page.Page) -> list[tuple[float, float, list[tuple[int, str, str, str]]]]:
    found = page.find_tables()
    items = []
    for table_obj in found:
        rows = extract_rows_from_table(table_obj.extract())
        if rows:
            x0, top, x1, bottom = table_obj.bbox
            items.append((float(top), float(bottom), float(x0), rows))

    items.sort(key=lambda item: (round(item[0] / 8), item[2]))
    bands: list[tuple[float, float, list[tuple[int, str, str, str]]]] = []
    for top, bottom, _x0, rows in items:
        if bands and abs(top - bands[-1][0]) < 10:
            band_top, band_bottom, band_rows = bands[-1]
            band_rows.extend(rows)
            bands[-1] = (min(band_top, top), max(band_bottom, bottom), band_rows)
        else:
            bands.append((top, bottom, list(rows)))

    normalized = []
    for top, bottom, rows in bands:
        normalized.append((top, bottom, sorted(rows, key=lambda row: row[0])))
    return normalized


def extract_pdf_metadata() -> list[VariableMetadata]:
    all_rows: list[VariableMetadata] = []

    for year, spec in PDF_SPECS.items():
        pdf_path = ROOT / year / spec["pdf"]
        current_table: str | None = None

        with pdfplumber.open(pdf_path) as pdf:
            for page_number in spec["pages"]:
                page = pdf.pages[page_number - 1]
                titles = extract_titles(page)
                bands = band_tables(page)

                for top, _bottom, rows in bands:
                    title_before = [title for title in titles if title[0] < top]
                    if title_before:
                        current_table = title_before[-1][1]
                    elif rows and rows[0][0] == 1:
                        title_after = [title for title in titles if title[0] >= top]
                        if title_after:
                            current_table = title_after[0][1]

                    if current_table is None:
                        continue

                    for position, variable, label, dtype in rows:
                        all_rows.append(
                            VariableMetadata(
                                year=year,
                                table=current_table,
                                position=position,
                                variable=variable,
                                label=label,
                                dtype=dtype,
                                source_pdf=spec["pdf"],
                                source_page=page_number,
                            )
                        )

    return all_rows


def write_csv(rows: list[VariableMetadata], output: Path = OUTPUT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "year",
                "table",
                "position",
                "variable",
                "label",
                "dtype",
                "source_pdf",
                "source_page",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "year": row.year,
                    "table": row.table,
                    "position": row.position,
                    "variable": row.variable,
                    "label": row.label,
                    "dtype": row.dtype,
                    "source_pdf": row.source_pdf,
                    "source_page": row.source_page,
                }
            )


def main() -> None:
    rows = extract_pdf_metadata()
    write_csv(rows)
    print(f"Wrote {OUTPUT} with {len(rows)} variable metadata rows")


if __name__ == "__main__":
    main()

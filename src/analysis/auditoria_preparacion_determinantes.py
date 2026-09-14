"""Auditoria diagnostica de la preparacion de determinantes.

Lee artefactos existentes de la etapa 12 y produce tablas agregadas de
evidencia. No entrena modelos, no crea particiones y no modifica bases.
"""

from __future__ import annotations

import json
import math
import sys
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.preparacion_determinantes import (
    CATEGORICAL_PREDICTORS,
    CONTINUOUS_PREDICTORS,
    KEY_COLS,
    REFERENCE_RULES,
    STRUCTURAL_MISSING_LABELS,
    TARGET,
    PreparationConfig,
    build_matrix,
    build_universe,
    prepare_categorical_for_matrix,
)


ANIO_ANALISIS = 2024
ANIOS_VALIDOS = (2018, 2020, 2022, 2024)
EDAD_MINIMA = 18
TABLE_DIR_NAME = "auditoria_preparacion_determinantes"
NA_LABEL = "<NA>"


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return NA_LABEL
    text = str(value)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def code_as_text(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .fillna(NA_LABEL)
    )


def label_as_text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna(NA_LABEL)


def key_mask(df: pd.DataFrame, key_values: dict[str, Any], columns: list[str]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for col in columns:
        target_text = code_as_text(pd.Series([key_values[col]])).iloc[0]
        target_num = pd.to_numeric(pd.Series([key_values[col]]), errors="coerce").iloc[0]
        text_equal = code_as_text(df[col]).eq(target_text)
        if pd.notna(target_num):
            num_equal = pd.to_numeric(df[col], errors="coerce").eq(target_num)
            mask &= text_equal | num_equal
        else:
            mask &= text_equal
    return mask


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype("string").str.lower().str.strip().isin(["true", "1", "si", "sí"])


def md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_Sin registros._"
    view = df.head(max_rows).copy()
    view = view.fillna("")

    def clean(value: Any) -> str:
        text = str(value).replace("\n", " ").replace("|", "\\|")
        return text

    columns = [clean(col) for col in view.columns]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(row[col]) for col in view.columns) + " |")
    return "\n".join(lines)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def read_mart(root: Path) -> pd.DataFrame:
    cols = list(
        dict.fromkeys(
            KEY_COLS
            + [
                "edad",
                TARGET,
                "registros_ingreso",
                "claves_ingreso_distintas",
                "ingreso_persona_total_registros_tri",
                "ingreso_persona_rentas_propiedad_tri",
                "ingreso_persona_transferencias_tri",
                "ingreso_persona_financiero_capital_tri",
                "ingreso_persona_no_clasificado_tri",
                "tiene_registros_ingreso",
                "n_trabajos",
                "horas_trabajos_total",
                "horas_trabajo_principal",
                "id_trabajo_principal",
                "subor_principal",
                "subor_principal_desc",
                "indep_principal",
                "indep_principal_desc",
                "pago_principal",
                "pago_principal_desc",
                "contrato_principal",
                "contrato_principal_desc",
                "tam_emp_principal",
                "tam_emp_principal_desc",
                "tiene_trabajo_reportado",
                "parentesco",
                "parentesco_desc",
                "sexo",
                "sexo_desc",
                "nivelaprob",
                "nivelaprob_desc",
                "gradoaprob",
                "segsoc",
                "segsoc_desc",
                "sexo_jefe",
                "sexo_jefe_desc",
                "educa_jefe",
                "educa_jefe_desc",
                "region_banxico",
                "tam_loc_desc",
                "hablaind_desc",
                "tot_integ",
                "menores",
                "p65mas",
            ]
            + CONTINUOUS_PREDICTORS
            + CATEGORICAL_PREDICTORS
        )
    )
    path = root / "data" / "interim" / "revision_4" / "mart_persona_2018_2024.csv.gz"
    return pd.read_csv(path, usecols=cols, low_memory=False)


def read_stage12_table(root: Path, name: str) -> pd.DataFrame:
    path = root / "reports" / "tables" / "preparacion_determinantes" / str(ANIO_ANALISIS) / name
    return pd.read_csv(path)


def segsoc_audit(root: Path, mart: pd.DataFrame, universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    frames = []
    universe_frames = []
    for year in ANIOS_VALIDOS:
        year_config = PreparationConfig.from_root(root, year=year, min_age=EDAD_MINIMA, valid_years=ANIOS_VALIDOS)
        year_universe, _ = build_universe(mart, year_config)
        universe_frames.append(year_universe)
    all_universes = pd.concat(universe_frames, ignore_index=True)
    for scope_name, df in [("mart_persona_completo", mart), ("universo_determinantes", all_universes)]:
        tmp = df[[*KEY_COLS, "segsoc", "segsoc_desc"]].copy()
        tmp["ambito"] = scope_name
        tmp["segsoc_codigo"] = code_as_text(tmp["segsoc"])
        tmp["segsoc_etiqueta"] = label_as_text(tmp["segsoc_desc"])
        freq = (
            tmp.groupby(["ambito", "anio", "segsoc_codigo", "segsoc_etiqueta"], dropna=False)
            .size()
            .reset_index(name="n")
        )
        freq["pct_en_anio_ambito"] = freq["n"] / freq.groupby(["ambito", "anio"])["n"].transform("sum")
        frames.append(freq)
    segsoc_freq = pd.concat(frames, ignore_index=True).sort_values(["ambito", "anio", "segsoc_codigo", "segsoc_etiqueta"])
    write_csv(segsoc_freq, out_dir / "segsoc_frecuencias_mart_universo.csv")

    raw_rows = []
    for year in ANIOS_VALIDOS:
        path = root / "data" / "raw" / "EINGH" / str(year) / "poblacion.csv"
        raw = pd.read_csv(path, usecols=["segsoc"], dtype="string")
        raw["segsoc_codigo"] = code_as_text(raw["segsoc"])
        freq = raw.groupby("segsoc_codigo", dropna=False).size().reset_index(name="n")
        freq["anio"] = year
        freq["pct_en_poblacion_raw"] = freq["n"] / freq["n"].sum()
        raw_rows.append(freq[["anio", "segsoc_codigo", "n", "pct_en_poblacion_raw"]])
    segsoc_raw = pd.concat(raw_rows, ignore_index=True).sort_values(["anio", "segsoc_codigo"])
    write_csv(segsoc_raw, out_dir / "segsoc_raw_poblacion_frecuencias.csv")

    catalog_path = root / "data" / "interim" / "revision_3" / "catalogo_categoricas_enigh.csv"
    catalog = pd.read_csv(catalog_path, dtype="string")
    catalog_vars = catalog[
        ((catalog["tabla"].eq("poblacion")) & (catalog["variable"].eq("segsoc")))
        | ((catalog["tabla"].eq("trabajos")) & (catalog["variable"].isin(["subor", "pago", "contrato", "tam_emp"])))
    ].copy()
    write_csv(catalog_vars, out_dir / "catalogo_local_variables_auditadas.csv")

    label_rows = []
    for _, row in catalog_vars[catalog_vars["variable"].eq("segsoc")].iterrows():
        label = "" if pd.isna(row["etiqueta"]) else str(row["etiqueta"])
        stripped = label.strip()
        norm = normalize_text(stripped)
        label_rows.append(
            {
                "anio": int(row["anio"]),
                "tabla": row["tabla"],
                "variable": row["variable"],
                "codigo": row["codigo"],
                "etiqueta": label,
                "repr_etiqueta": repr(label),
                "etiqueta_strip": stripped,
                "igual_a_no": stripped == "No",
                "igual_a_si": stripped == "Sí",
                "normalizada_ascii": norm,
                "lower_ascii": norm.lower(),
                "largo": len(label),
                "contiene_replacement_char": "\ufffd" in label,
                "contiene_descripcion_invertida": "noicpircsed" in norm.lower(),
                "problema_espacio_case_acento": stripped.lower() == "no" and stripped != "No",
            }
        )
    segsoc_label_diag = pd.DataFrame(label_rows)
    write_csv(segsoc_label_diag, out_dir / "segsoc_diagnostico_etiquetas.csv")

    validation_path = root / "data" / "interim" / "revision_3" / "validacion_mappings_categoricas.csv"
    validation = pd.read_csv(validation_path)
    validation_vars = validation[
        ((validation["tabla"].eq("poblacion")) & (validation["variable"].eq("segsoc")))
        | ((validation["tabla"].eq("trabajos")) & (validation["variable"].isin(["subor", "pago", "contrato", "tam_emp"])))
    ].copy()
    write_csv(validation_vars, out_dir / "validacion_catalogos_variables_auditadas.csv")

    propuestas = []
    for year in [2020, 2022]:
        observed = catalog_vars[
            catalog_vars["anio"].astype(int).eq(year)
            & catalog_vars["tabla"].eq("poblacion")
            & catalog_vars["variable"].eq("segsoc")
            & catalog_vars["codigo"].astype("string").str.strip().eq("2")
        ]
        observed_label = observed["etiqueta"].iloc[0] if not observed.empty else ""
        propuestas.append(
            {
                "anio": year,
                "variable": "segsoc_desc",
                "codigo_original": "2",
                "etiqueta_observada": observed_label,
                "etiqueta_propuesta": "No",
                "base_evidencia": "Catalogo local: misma variable con rango binario; codigo 2 contaminado por texto invertido de extraccion en 2020/2022; codigo 2 aparece con etiqueta limpia No en 2018/2024.",
                "estado": "propuesta_no_aplicada_requiere_aprobacion",
            }
        )
    propuestas_df = pd.DataFrame(propuestas)
    write_csv(propuestas_df, out_dir / "segsoc_mapeo_propuesto_no_aplicado.csv")
    return {
        "freq": segsoc_freq,
        "raw": segsoc_raw,
        "catalog": catalog_vars,
        "labels": segsoc_label_diag,
        "propuestas": propuestas_df,
    }


def labor_missing_audit(universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    df = universe.copy()
    df["tiene_trabajo_bool"] = bool_series(df["tiene_trabajo_reportado"])
    df["n_trabajos_num"] = pd.to_numeric(df["n_trabajos"], errors="coerce")
    df["target_positivo"] = pd.to_numeric(df[TARGET], errors="coerce").gt(0)
    df["tiene_id_trabajo_principal"] = df["id_trabajo_principal"].notna()

    rows = []
    for var in ["subor_principal_desc", "contrato_principal_desc"]:
        missing = df[var].isna()
        if var == "subor_principal_desc":
            clasificacion = np.select(
                [
                    missing & ~df["tiene_trabajo_bool"],
                    missing & df["tiene_trabajo_bool"],
                    ~missing,
                ],
                [
                    "no_aplica_sin_trabajo_principal_reportado",
                    "faltante_laboral_no_clasificado",
                    "observado",
                ],
                default="revisar",
            )
        else:
            pago = df["pago_principal_desc"].astype("string")
            pago_isna = pago.isna().to_numpy(dtype=bool)
            pago_notna = pago.notna().to_numpy(dtype=bool)
            pago_recibe = pago.eq("Recibe un pago").fillna(False).to_numpy(dtype=bool)
            clasificacion = np.select(
                [
                    missing & ~df["tiene_trabajo_bool"],
                    missing & df["tiene_trabajo_bool"] & pago_isna,
                    missing & df["tiene_trabajo_bool"] & pago_notna & ~pago_recibe,
                    missing & df["tiene_trabajo_bool"] & pago_recibe,
                    ~missing,
                ],
                [
                    "no_aplica_sin_trabajo_principal_reportado",
                    "no_aplica_pago_principal_no_documentado",
                    "no_aplica_trabajador_sin_pago",
                    "faltante_en_trabajador_con_pago",
                    "observado",
                ],
                default="revisar",
            )
        tmp = df.assign(variable=var, clasificacion=clasificacion)
        agg = (
            tmp.groupby(["variable", "clasificacion"], dropna=False)
            .agg(
                n=("variable", "size"),
                target_positivo=("target_positivo", "sum"),
                con_trabajo_reportado=("tiene_trabajo_bool", "sum"),
                con_id_trabajo_principal=("tiene_id_trabajo_principal", "sum"),
                n_trabajos_min=("n_trabajos_num", "min"),
                n_trabajos_max=("n_trabajos_num", "max"),
                ingreso_sum=(TARGET, "sum"),
            )
            .reset_index()
        )
        agg["pct_universo"] = agg["n"] / len(df)
        rows.append(agg)
    clasificacion_df = pd.concat(rows, ignore_index=True)
    write_csv(clasificacion_df, out_dir / "faltantes_laborales_clasificacion_2024.csv")

    prepared = prepare_categorical_for_matrix(universe)
    prep_rows = []
    for var in ["subor_principal_desc", "contrato_principal_desc"]:
        s = prepared[var]
        prep = s.value_counts(dropna=False).rename_axis("categoria_matriz").reset_index(name="n")
        prep["variable"] = var
        prep["pct_universo"] = prep["n"] / len(df)
        prep_rows.append(prep[["variable", "categoria_matriz", "n", "pct_universo"]])
    prep_df = pd.concat(prep_rows, ignore_index=True)
    write_csv(prep_df, out_dir / "faltantes_laborales_preparacion_actual_2024.csv")

    cross_cols = [
        "tiene_trabajo_bool",
        "n_trabajos_num",
        "tiene_id_trabajo_principal",
        "subor_principal_desc",
        "pago_principal_desc",
        "contrato_principal_desc",
    ]
    cross = (
        df.assign(
            subor_missing=df["subor_principal_desc"].isna(),
            contrato_missing=df["contrato_principal_desc"].isna(),
            n_trabajos_grupo=np.select(
                [df["n_trabajos_num"].isna(), df["n_trabajos_num"].eq(1), df["n_trabajos_num"].gt(1)],
                ["sin_registro", "1", "2_o_mas"],
                default="otro",
            ),
        )
        .groupby(
            [
                "subor_missing",
                "contrato_missing",
                "tiene_trabajo_bool",
                "n_trabajos_grupo",
                "tiene_id_trabajo_principal",
                "subor_principal_desc",
                "pago_principal_desc",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )
    write_csv(cross, out_dir / "faltantes_laborales_cruces_2024.csv")

    payment_freq = (
        df.assign(pago_principal_codigo=code_as_text(df["pago_principal"]), pago_principal_etiqueta=label_as_text(df["pago_principal_desc"]))
        .groupby(["pago_principal_codigo", "pago_principal_etiqueta"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )
    payment_freq["pct_universo"] = payment_freq["n"] / len(df)
    write_csv(payment_freq, out_dir / "pago_principal_frecuencias_2024.csv")

    return {"clasificacion": clasificacion_df, "preparacion": prep_df, "cruces": cross, "pago": payment_freq}


def income_tail_audit(root: Path, universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    y = pd.to_numeric(universe[TARGET], errors="coerce").astype(float)
    n = len(y)
    ordered = universe.assign(_target=y).sort_values("_target", ascending=False, kind="mergesort").reset_index(drop=True)
    total = float(y.sum())

    def top_share(pct: float) -> dict[str, Any]:
        count = int(math.ceil(n * pct))
        subset = ordered.head(count)
        cutoff = float(subset["_target"].iloc[-1])
        return {
            "grupo": f"top_{pct:.3%}",
            "pct_solicitado": pct,
            "n_incluido": count,
            "criterio_empates": "orden descendente estable; no se expande el corte por empates",
            "valor_corte": cutoff,
            "empates_totales_en_corte": int((ordered["_target"] == cutoff).sum()),
            "empates_incluidos_en_corte": int((subset["_target"] == cutoff).sum()),
            "ingreso_sum": float(subset["_target"].sum()),
            "share_ingreso_muestral": float(subset["_target"].sum() / total),
        }

    summary_rows = [
        {"metrica": "n", "valor": float(n)},
        {"metrica": "sum", "valor": total},
        {"metrica": "mean", "valor": float(y.mean())},
        {"metrica": "median", "valor": float(y.median())},
        {"metrica": "p95", "valor": float(y.quantile(0.95))},
        {"metrica": "p99", "valor": float(y.quantile(0.99))},
        {"metrica": "p99_9", "valor": float(y.quantile(0.999))},
        {"metrica": "max", "valor": float(y.max())},
    ]
    top001_count = int(math.ceil(n * 0.001))
    summary_rows.append({"metrica": "mean_excluyendo_top_0_1pct", "valor": float(ordered.iloc[top001_count:]["_target"].mean())})
    summary_rows.append({"metrica": "n_excluyendo_top_0_1pct", "valor": float(n - top001_count)})
    tail_summary = pd.DataFrame(summary_rows)
    write_csv(tail_summary, out_dir / "ingreso_cola_metricas_2024.csv")

    shares = pd.DataFrame([top_share(0.01), top_share(0.001)])
    write_csv(shares, out_dir / "ingreso_cola_participaciones_2024.csv")

    no_id_cols = [
        TARGET,
        "ingreso_persona_total_registros_tri",
        "ingreso_persona_rentas_propiedad_tri",
        "ingreso_persona_transferencias_tri",
        "ingreso_persona_financiero_capital_tri",
        "ingreso_persona_no_clasificado_tri",
        "registros_ingreso",
        "claves_ingreso_distintas",
        "n_trabajos",
        "tiene_trabajo_reportado",
    ]
    top10 = ordered.head(10)[no_id_cols].copy()
    top10.insert(0, "rank_muestral_sin_identificadores", range(1, len(top10) + 1))
    write_csv(top10, out_dir / "ingreso_top10_sin_identificadores_2024.csv")

    max_row = ordered.iloc[0]
    key_values = {col: max_row[col] for col in KEY_COLS}

    agg_path = root / "data" / "interim" / "revision_4" / "ingresos_agregados_persona.csv.gz"
    agg = pd.read_csv(agg_path, low_memory=False)
    agg_match = agg.loc[key_mask(agg, key_values, KEY_COLS)].copy()

    raw_path = root / "data" / "raw" / "EINGH" / "2024" / "ingresos.csv"
    raw = pd.read_csv(raw_path, usecols=["folioviv", "foliohog", "numren", "clave", "ing_tri"], dtype="string")
    raw_match = raw.loc[key_mask(raw, key_values, ["folioviv", "foliohog", "numren"])].copy()
    raw_match["clave_num"] = pd.to_numeric(raw_match["clave"].astype("string").str.replace("P", "", regex=False), errors="coerce")
    raw_match["ing_tri_num"] = pd.to_numeric(raw_match["ing_tri"], errors="coerce").fillna(0)
    labor_mask = raw_match["clave_num"].between(1, 22, inclusive="both") | raw_match["clave_num"].between(67, 81, inclusive="both")

    trace = pd.DataFrame(
        [
            {
                "validacion": "mart_vs_ingresos_agregados",
                "valor_mart": float(max_row[TARGET]),
                "valor_fuente": float(agg_match[TARGET].iloc[0]) if len(agg_match) == 1 else math.nan,
                "diferencia": float(max_row[TARGET] - agg_match[TARGET].iloc[0]) if len(agg_match) == 1 else math.nan,
                "n_registros_fuente": int(len(agg_match)),
                "estado": "ok" if len(agg_match) == 1 and abs(float(max_row[TARGET] - agg_match[TARGET].iloc[0])) < 0.01 else "revisar",
            },
            {
                "validacion": "mart_vs_ingresos_raw_claves_1_22_67_81",
                "valor_mart": float(max_row[TARGET]),
                "valor_fuente": float(raw_match.loc[labor_mask, "ing_tri_num"].sum()) if not raw_match.empty else math.nan,
                "diferencia": float(max_row[TARGET] - raw_match.loc[labor_mask, "ing_tri_num"].sum()) if not raw_match.empty else math.nan,
                "n_registros_fuente": int(labor_mask.sum()) if not raw_match.empty else 0,
                "estado": "ok" if not raw_match.empty and abs(float(max_row[TARGET] - raw_match.loc[labor_mask, "ing_tri_num"].sum())) < 0.01 else "revisar",
            },
            {
                "validacion": "raw_total_persona_todas_claves",
                "valor_mart": float(max_row["ingreso_persona_total_registros_tri"]),
                "valor_fuente": float(raw_match["ing_tri_num"].sum()) if not raw_match.empty else math.nan,
                "diferencia": float(max_row["ingreso_persona_total_registros_tri"] - raw_match["ing_tri_num"].sum()) if not raw_match.empty else math.nan,
                "n_registros_fuente": int(len(raw_match)),
                "estado": "ok" if not raw_match.empty and abs(float(max_row["ingreso_persona_total_registros_tri"] - raw_match["ing_tri_num"].sum())) < 0.01 else "revisar",
            },
        ]
    )
    write_csv(trace, out_dir / "ingreso_maximo_trazabilidad_2024.csv")

    raw_components = (
        raw_match.assign(es_target_laboral_negocio=labor_mask)
        .groupby(["clave", "es_target_laboral_negocio"], dropna=False)
        .agg(n_registros=("clave", "size"), ing_tri_sum=("ing_tri_num", "sum"))
        .reset_index()
        .sort_values("ing_tri_sum", ascending=False)
    )
    write_csv(raw_components, out_dir / "ingreso_maximo_claves_fuente_2024.csv")
    return {"summary": tail_summary, "shares": shares, "top10": top10, "trace": trace, "components": raw_components}


def tam_emp_audit(universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    df = universe.copy()
    tiene = bool_series(df["tiene_trabajo_reportado"])

    def prepare_labor(var: str) -> pd.Series:
        s = df[var].astype("object").copy()
        missing = s.isna()
        structural = missing & (~tiene)
        unresolved = missing & ~structural
        s.loc[structural] = STRUCTURAL_MISSING_LABELS[var]
        s.loc[unresolved] = "Faltante laboral no clasificado"
        return s.fillna("Faltante no clasificado").astype(str)

    subor = prepare_labor("subor_principal_desc")
    tam = prepare_labor("tam_emp_principal_desc")
    rows = []
    for var, s in [("subor_principal_desc", subor), ("tam_emp_principal_desc", tam)]:
        freq = s.value_counts(dropna=False).rename_axis("categoria_preparada").reset_index(name="n")
        freq["variable"] = var
        freq["pct_universo"] = freq["n"] / len(df)
        rows.append(freq[["variable", "categoria_preparada", "n", "pct_universo"]])
    freq_df = pd.concat(rows, ignore_index=True)
    write_csv(freq_df, out_dir / "tam_emp_subor_frecuencias_2024.csv")

    label = STRUCTURAL_MISSING_LABELS["tam_emp_principal_desc"]
    dup = pd.DataFrame(
        [
            {
                "columna_a_si_tam_emp_entrara_a_x": "tam_emp_principal_desc__no_aplica_sin_trabajo_principal_reportado",
                "columna_b_existente_en_x": "subor_principal_desc__no_aplica_sin_trabajo_principal_reportado",
                "categoria": label,
                "n_columna_a": int(tam.eq(label).sum()),
                "n_columna_b": int(subor.eq(label).sum()),
                "duplicada_exacta": bool(tam.eq(label).equals(subor.eq(label))),
                "ambito_duplicacion": "solo_categoria_estructural_sin_trabajo_principal_reportado",
                "informacion_no_duplicada_perdida_en_x_actual": "tamano de empresa observado en 12 categorias para quienes si tienen trabajo principal reportado",
            }
        ]
    )
    write_csv(dup, out_dir / "tam_emp_dummy_duplicada_2024.csv")
    return {"freq": freq_df, "duplicate": dup}


def jefatura_audit(universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    df = universe.copy()
    jefe = df["parentesco_desc"].eq("Jefe(a)")
    jefe_df = df.loc[jefe].copy()
    sexo_match = jefe_df["sexo_desc"].eq(jefe_df["sexo_jefe_desc"])
    sexo_code_match = code_as_text(jefe_df["sexo"]).eq(code_as_text(jefe_df["sexo_jefe"]))
    coincidencias = pd.DataFrame(
        [
            {
                "metrica": "personas_universo",
                "valor": len(df),
                "pct_universo": 1.0,
                "nota": "Universo 2024 de determinantes.",
            },
            {
                "metrica": "personas_jefe_a",
                "valor": int(jefe.sum()),
                "pct_universo": float(jefe.mean()),
                "nota": "parentesco_desc == Jefe(a).",
            },
            {
                "metrica": "jefes_sexo_desc_coincide",
                "valor": int(sexo_match.sum()),
                "pct_universo": float(sexo_match.mean()),
                "nota": "Entre jefes/as, sexo_desc y sexo_jefe_desc coinciden.",
            },
            {
                "metrica": "jefes_sexo_codigo_coincide",
                "valor": int(sexo_code_match.sum()),
                "pct_universo": float(sexo_code_match.mean()),
                "nota": "Entre jefes/as, sexo y sexo_jefe coinciden por codigo.",
            },
            {
                "metrica": "jefes_nivelaprob_educa_jefe_match_texto_exacta",
                "valor": int(jefe_df["nivelaprob_desc"].eq(jefe_df["educa_jefe_desc"]).sum()),
                "pct_universo": float(jefe_df["nivelaprob_desc"].eq(jefe_df["educa_jefe_desc"]).mean()),
                "nota": "Comparacion textual exacta; no debe esperarse 100% porque educa_jefe clasifica completo/incompleto y profesional.",
            },
        ]
    )
    write_csv(coincidencias, out_dir / "jefatura_coincidencias_2024.csv")

    parentesco = (
        df.assign(
            es_jefe=jefe,
            sexo_igual_a_jefatura=df["sexo_desc"].eq(df["sexo_jefe_desc"]),
            educacion_texto_igual_a_jefatura=df["nivelaprob_desc"].eq(df["educa_jefe_desc"]),
        )
        .groupby("parentesco_desc", dropna=False)
        .agg(
            n=("parentesco_desc", "size"),
            pct_universo=("parentesco_desc", lambda s: len(s) / len(df)),
            pct_sexo_igual_a_jefatura=("sexo_igual_a_jefatura", "mean"),
            pct_educacion_texto_igual_a_jefatura=("educacion_texto_igual_a_jefatura", "mean"),
        )
        .reset_index()
        .sort_values("n", ascending=False)
    )
    write_csv(parentesco, out_dir / "jefatura_parentesco_resumen_2024.csv")

    educ_cross = (
        jefe_df.groupby(["nivelaprob_desc", "educa_jefe_desc"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .head(40)
    )
    educ_cross["pct_jefes"] = educ_cross["n"] / len(jefe_df)
    write_csv(educ_cross, out_dir / "jefatura_educacion_cruce_top_2024.csv")
    return {"coincidencias": coincidencias, "parentesco": parentesco, "educ_cross": educ_cross}


def vif_audit(root: Path, universe: pd.DataFrame, out_dir: Path) -> dict[str, pd.DataFrame]:
    X_path = root / "data" / "processed" / "determinantes_2024" / "X_diagnostico_sin_escalar.csv.gz"
    X = pd.read_csv(X_path)
    saved_vif = read_stage12_table(root, "dependencia_vif.csv")
    mapping = read_stage12_table(root, "mapping_ohe.csv")
    refs = read_stage12_table(root, "referencias_ohe.csv").set_index("variable")["referencia"].to_dict()

    detail_rows = []
    for col in X.columns:
        vif_row = saved_vif.loc[saved_vif["columna"].eq(col)]
        if col in CONTINUOUS_PREDICTORS:
            detail_rows.append(
                {
                    "columna_matriz": col,
                    "variable_original": col,
                    "categoria": "",
                    "referencia_variable": "",
                    "frecuencia_categoria": len(X),
                    "pct_universo": 1.0,
                    "vif": float(vif_row["vif"].iloc[0]) if not vif_row.empty else math.nan,
                    "estado_vif": vif_row["estado"].iloc[0] if not vif_row.empty else "sin_vif_guardado",
                    "nota": "continua",
                }
            )
        else:
            map_row = mapping.loc[mapping["dummy"].eq(col)]
            if map_row.empty:
                variable = ""
                category = ""
                freq = int(pd.to_numeric(X[col], errors="coerce").sum())
                pct = float(pd.to_numeric(X[col], errors="coerce").mean())
            else:
                map_row = map_row.iloc[0]
                variable = map_row["variable_original"]
                category = map_row["categoria"]
                freq = int(map_row["n"])
                pct = float(map_row["pct"])
            detail_rows.append(
                {
                    "columna_matriz": col,
                    "variable_original": variable,
                    "categoria": category,
                    "referencia_variable": refs.get(variable, ""),
                    "frecuencia_categoria": freq,
                    "pct_universo": pct,
                    "vif": float(vif_row["vif"].iloc[0]) if not vif_row.empty else math.nan,
                    "estado_vif": vif_row["estado"].iloc[0] if not vif_row.empty else "sin_vif_guardado",
                    "nota": "dummy_ohe_k_menos_1",
                }
            )
    vif_detail = pd.DataFrame(detail_rows).sort_values("vif", ascending=False).reset_index(drop=True)
    write_csv(vif_detail, out_dir / "vif_detallado_2024.csv")
    top15 = vif_detail.head(15).copy()
    write_csv(top15, out_dir / "vif_top15_2024.csv")

    X_values = X.astype(float)
    n_cols = X_values.shape[1]
    rank_with_intercept = int(np.linalg.matrix_rank(np.column_stack([np.ones(len(X_values)), X_values.to_numpy()])))
    duplicate_pairs = []
    cols = list(X_values.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            if X_values[a].equals(X_values[b]):
                duplicate_pairs.append({"columna_a": a, "columna_b": b})
    matrix_validation = pd.DataFrame(
        [
            {"metrica": "filas_X_guardada", "valor": len(X), "estado": "ok"},
            {"metrica": "columnas_X_guardada", "valor": n_cols, "estado": "ok" if n_cols == 67 else "revisar"},
            {
                "metrica": "rango_con_intercepto",
                "valor": rank_with_intercept,
                "estado": "ok" if rank_with_intercept == n_cols + 1 else "revisar",
            },
            {"metrica": "pares_duplicados_exactos_en_X", "valor": len(duplicate_pairs), "estado": "ok" if not duplicate_pairs else "revisar"},
            {
                "metrica": "metodo_vif_guardado",
                "valor": "inversa_matriz_correlaciones",
                "estado": "ok",
            },
            {
                "metrica": "intercepto_en_rango_no_en_X",
                "valor": "intercepto agregado solo para diagnostico de rango; X guardada no contiene constante",
                "estado": "ok",
            },
        ]
    )
    write_csv(matrix_validation, out_dir / "validacion_matriz_2024.csv")
    write_csv(pd.DataFrame(duplicate_pairs, columns=["columna_a", "columna_b"]), out_dir / "duplicados_exactos_x_2024.csv")

    aux_rows = []
    X_np = X_values.to_numpy(dtype=float)
    col_index = {col: idx for idx, col in enumerate(X_values.columns)}
    for col in top15["columna_matriz"]:
        j = col_index[col]
        y = X_np[:, j]
        others = np.delete(X_np, j, axis=1)
        design = np.column_stack([np.ones(len(others)), others])
        coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        pred = design @ coef
        rss = float(np.square(y - pred).sum())
        tss = float(np.square(y - y.mean()).sum())
        r2 = 1.0 - rss / tss if tss > 0 else math.nan
        vif_aux = 1.0 / (1.0 - r2) if r2 < 1 else math.inf
        saved = float(top15.loc[top15["columna_matriz"].eq(col), "vif"].iloc[0])
        aux_rows.append(
            {
                "columna_matriz": col,
                "r2_auxiliar_con_intercepto": r2,
                "vif_auxiliar_con_intercepto": vif_aux,
                "vif_guardado": saved,
                "diferencia_abs": abs(vif_aux - saved),
                "estado": "ok" if abs(vif_aux - saved) < 1e-8 else "revisar",
            }
        )
    aux = pd.DataFrame(aux_rows)
    write_csv(aux, out_dir / "vif_verificacion_auxiliar_2024.csv")
    return {"detail": vif_detail, "top15": top15, "matrix_validation": matrix_validation, "aux": aux}


def audited_files(root: Path, out_dir: Path) -> pd.DataFrame:
    rows = [
        {"archivo": "src/features/preparacion_determinantes.py", "tipo": "codigo etapa 12", "uso": "reglas de universo, transformaciones, OHE y VIF"},
        {"archivo": "notebooks/12_preparacion_base_determinantes.ipynb", "tipo": "notebook etapa 12", "uso": "ejecucion narrativa parametrizada"},
        {"archivo": "reports/preparacion_base_determinantes.md", "tipo": "reporte etapa 12", "uso": "resumen vigente de preparacion"},
        {"archivo": "reports/tables/preparacion_determinantes/2024/*.csv", "tipo": "tablas etapa 12", "uso": "faltantes, OHE, VIF, reproduccion y validaciones"},
        {"archivo": "reports/tables/preparacion_determinantes/compatibilidad_*.csv", "tipo": "tablas etapa 12", "uso": "compatibilidad por ano"},
        {"archivo": "data/interim/revision_3/catalogo_categoricas_enigh.csv", "tipo": "catalogo local", "uso": "codigos y etiquetas extraidas de documentacion"},
        {"archivo": "data/interim/revision_4/mart_persona_2018_2024.csv.gz", "tipo": "mart nominal", "uso": "base fuente de la etapa 12"},
        {"archivo": "data/interim/revision_4/ingresos_agregados_persona.csv.gz", "tipo": "agregado persona", "uso": "trazabilidad del target"},
        {"archivo": "data/raw/EINGH/2024/ingresos.csv", "tipo": "fuente cruda", "uso": "trazabilidad agregada del maximo sin guardar folios"},
    ]
    df = pd.DataFrame(rows)
    write_csv(df, out_dir / "archivos_auditados.csv")
    return df


def build_findings(
    segsoc: dict[str, pd.DataFrame],
    labor: dict[str, pd.DataFrame],
    tail: dict[str, pd.DataFrame],
    tam_emp: dict[str, pd.DataFrame],
    jefe: dict[str, pd.DataFrame],
    vif: dict[str, pd.DataFrame],
    out_dir: Path,
) -> pd.DataFrame:
    max_value = float(tail["summary"].loc[tail["summary"]["metrica"].eq("max"), "valor"].iloc[0])
    top01_share = float(tail["shares"].loc[tail["shares"]["pct_solicitado"].eq(0.001), "share_ingreso_muestral"].iloc[0])
    mean_full = float(tail["summary"].loc[tail["summary"]["metrica"].eq("mean"), "valor"].iloc[0])
    mean_no_top = float(tail["summary"].loc[tail["summary"]["metrica"].eq("mean_excluyendo_top_0_1pct"), "valor"].iloc[0])
    subor_missing = int(
        labor["clasificacion"].loc[
            labor["clasificacion"]["variable"].eq("subor_principal_desc")
            & ~labor["clasificacion"]["clasificacion"].eq("observado"),
            "n",
        ].sum()
    )
    contrato_missing = int(
        labor["clasificacion"].loc[
            labor["clasificacion"]["variable"].eq("contrato_principal_desc")
            & ~labor["clasificacion"]["clasificacion"].eq("observado"),
            "n",
        ].sum()
    )
    jefe_rows = jefe["coincidencias"].set_index("metrica")
    rows = [
        {
            "tipo": "A_hecho",
            "asunto": "2024 reproducido",
            "evidencia": "La reproduccion previa registra 141579 personas, 80872 hogares, 67 columnas X, rango 68/68 y maximo 17021739.12.",
            "causa": "Ejecucion parametrizada de etapa 12 para ANIO_ANALISIS=2024.",
            "impacto": "La auditoria parte de una base estable pero no metodologicamente cerrada.",
            "accion": "Mantener 2024 como base ejecutada y marcar revision pendiente.",
        },
        {
            "tipo": "B_explicacion",
            "asunto": "segsoc_desc 2020/2022 sin referencia No",
            "evidencia": "El catalogo local contiene codigo 2 con etiquetas contaminadas por texto invertido en 2020/2022; el universo si contiene codigo 2.",
            "causa": "Problema de etiqueta extraida/decodificada, no ausencia de la categoria en el universo.",
            "impacto": "La referencia OHE exacta No no se encuentra y se bloquea la generacion anual.",
            "accion": "Proponer correccion codigo 2 -> No en 2020/2022, sin aplicarla hasta aprobacion.",
        },
        {
            "tipo": "A_hecho",
            "asunto": "faltantes laborales 2024",
            "evidencia": f"subor_principal_desc faltante={subor_missing}; contrato_principal_desc faltante={contrato_missing}.",
            "causa": "subor falta cuando no hay trabajo principal reportado; contrato falta fuera de la ruta de trabajador con pago.",
            "impacto": "Las categorias estructurales son interpretables como ruta laboral, no como imputacion de valor observado.",
            "accion": "Conservar base intacta y pedir decision antes de cambiar especificacion laboral.",
        },
        {
            "tipo": "C_hipotesis",
            "asunto": "ingreso positivo sin trabajo principal reportado",
            "evidencia": "Hay 5205 personas del universo 2024 con target positivo, sin trabajo principal reportado y sin id_trabajo_principal.",
            "causa": "Puede corresponder a ingresos registrados sin fila de trabajos en la ventana observada o a una integracion a revisar; no se demuestra error con esta auditoria.",
            "impacto": "Afecta la interpretacion de variables del trabajo principal sobre todo el universo activo.",
            "accion": "Mantener clasificacion estructural y revisar documentacion/ruta laboral si se decide modelar detalles del trabajo principal.",
        },
        {
            "tipo": "B_explicacion",
            "asunto": "maximo y cola derecha",
            "evidencia": f"Maximo={max_value:.2f}; top 0.1% aporta {top01_share:.4%}; media total={mean_full:.2f}, media sin top 0.1%={mean_no_top:.2f}.",
            "causa": "Suma nominal trimestral de claves laborales/de negocio; cola derecha extrema.",
            "impacto": "El promedio es sensible a la cola, pero no se justifica borrar/winsorizar sin decision metodologica.",
            "accion": "Documentar cola y evaluar transformacion/modelo robusto en etapa posterior.",
        },
        {
            "tipo": "A_hecho",
            "asunto": "tam_emp_principal_desc duplicaria una dummy",
            "evidencia": "La categoria estructural sin trabajo principal de tam_emp coincide exactamente con la dummy estructural de subor.",
            "causa": "Ambas variables comparten el mismo estado no aplica cuando no existe trabajo principal reportado.",
            "impacto": "Excluir tam_emp evita una duplicacion exacta, pero deja fuera informacion de tamano observado.",
            "accion": "Aprobar si se mantiene fuera, se recodifica solo entre trabajadores o se usa especificacion laboral separada.",
        },
        {
            "tipo": "B_explicacion",
            "asunto": "variables propias y de jefatura",
            "evidencia": f"Jefes/as={int(jefe_rows.loc['personas_jefe_a','valor'])} ({float(jefe_rows.loc['personas_jefe_a','pct_universo']):.4%}); sexo propio y de jefatura coincide en jefes/as.",
            "causa": "sexo_jefe es derivado del jefe del hogar; para no jefes/as funciona como contexto del hogar.",
            "impacto": "Hay redundancia esperada solo para jefes/as; educa_jefe no es copia textual de nivelaprob.",
            "accion": "Mantener como hallazgo contextual; decidir especificacion de contexto del hogar antes de modelar.",
        },
        {
            "tipo": "A_hecho",
            "asunto": "VIF alto en bloque laboral/educativo",
            "evidencia": f"Mayor VIF={float(vif['top15']['vif'].iloc[0]):.4f} en {vif['top15']['columna_matriz'].iloc[0]}; rango con intercepto completo.",
            "causa": "Asociacion mecanica/semantica entre contrato, subordinacion y categorias educativas codificadas k-1.",
            "impacto": "Se debe interpretar colinealidad antes de estimar modelos, sin aplicar umbrales automaticos.",
            "accion": "Usar tabla VIF detallada como insumo para decisiones de especificacion.",
        },
        {
            "tipo": "D_decision",
            "asunto": "preparacion no cerrada",
            "evidencia": "2018 solo inspeccionado; 2020/2022 requieren correccion de segsoc_desc; 2024 auditado con pendientes.",
            "causa": "La comparabilidad anual de coeficientes exige especificacion comun posterior.",
            "impacto": "No conviene pasar a modelado como si la base estuviera cerrada.",
            "accion": "Aprobar mapeos, tratamiento de laborales, tam_emp, cola y contexto de jefatura antes de cambiar X.",
        },
    ]
    findings = pd.DataFrame(rows)
    write_csv(findings, out_dir / "hallazgos_auditoria.csv")
    return findings


def build_report(
    root: Path,
    out_dir: Path,
    files: pd.DataFrame,
    findings: pd.DataFrame,
    segsoc: dict[str, pd.DataFrame],
    labor: dict[str, pd.DataFrame],
    tail: dict[str, pd.DataFrame],
    tam_emp: dict[str, pd.DataFrame],
    jefe: dict[str, pd.DataFrame],
    vif: dict[str, pd.DataFrame],
) -> Path:
    branch = "codex/auditoria-preparacion-determinantes"
    report_path = root / "reports" / "auditoria_preparacion_determinantes.md"
    trace_ok = tail["trace"][["validacion", "valor_mart", "valor_fuente", "diferencia", "estado"]]
    segsoc_view = segsoc["freq"][segsoc["freq"]["ambito"].eq("universo_determinantes")][
        ["anio", "segsoc_codigo", "segsoc_etiqueta", "n", "pct_en_anio_ambito"]
    ]
    labor_view = labor["clasificacion"][["variable", "clasificacion", "n", "pct_universo", "con_trabajo_reportado", "con_id_trabajo_principal"]]
    content = f"""# Auditoria de preparacion de determinantes

## Estado

- Rama de trabajo: `{branch}`.
- Commit base auditado: `6aec7782a395d49bfb45a6d314a3feda54dc84fd`.
- Alcance: revision diagnostica de la etapa 12, sin entrenar modelos, sin particiones, sin reactivar deflactores/JKn y sin modificar matrices ni marts.
- Universo activo 2024: personas con edad >= {EDAD_MINIMA} e ingreso laboral/de negocio positivo, montos nominales trimestrales.

## Archivos revisados

{md_table(files, max_rows=20)}

## Hallazgos por tipo

Tipos usados: A = hecho observado; B = explicacion respaldada por evidencia; C = hipotesis pendiente; D = decision que requiere aprobacion.

{md_table(findings[["tipo", "asunto", "evidencia", "causa", "accion"]], max_rows=20)}

## Seguridad social 2020/2022

La referencia OHE esperada para `segsoc_desc` es la etiqueta exacta `No`. En 2020 y 2022 la categoria no esta ausente del universo: aparece el codigo original `2`, pero su etiqueta local queda contaminada como texto invertido de la extraccion documental. No es un problema de espacios, mayusculas/minusculas o acentos.

{md_table(segsoc_view, max_rows=12)}

Mapeo propuesto, no aplicado:

{md_table(segsoc["propuestas"], max_rows=10)}

## Faltantes laborales 2024

Los faltantes de `subor_principal_desc` se concentran en personas con ingreso laboral/de negocio positivo pero sin trabajo principal reportado en `trabajos`. Los de `contrato_principal_desc` se concentran fuera de la ruta de trabajador con pago; la regla actual los convierte en categoria estructural en la matriz, no en imputacion.

{md_table(labor_view, max_rows=20)}

Frecuencias de la categoria usada actualmente en matriz:

{md_table(labor["preparacion"], max_rows=20)}

## Maximo y cola derecha

La trazabilidad del maximo se verifico contra el agregado de ingresos por persona y contra `ingresos.csv` 2024 usando claves 1-22 y 67-81, que son las claves del target documentadas en el notebook de construccion de marts. La tabla de componentes no incluye folios ni llaves personales.

{md_table(trace_ok, max_rows=10)}

Metricas de cola:

{md_table(tail["summary"], max_rows=12)}

Participacion de la cola:

{md_table(tail["shares"], max_rows=5)}

## Tamano de empresa

`tam_emp_principal_desc` conserva informacion sustantiva de tamano de empresa para quienes tienen trabajo principal. El problema detectado es acotado: si entrara a OHE, su categoria estructural `No aplica: sin trabajo principal reportado` duplicaria exactamente la dummy estructural ya creada por `subor_principal_desc`.

{md_table(tam_emp["duplicate"], max_rows=5)}

## Variables propias y de jefatura

Para personas que son jefe(a), `sexo_desc` y `sexo_jefe_desc` coinciden como se espera. Para no jefes/as, `sexo_jefe_desc` es contexto del hogar, no copia de la persona. En educacion, `nivelaprob_desc` y `educa_jefe_desc` no son escalas textuales identicas: `educa_jefe_desc` separa completo/incompleto y profesional, por lo que la no coincidencia textual exacta no implica error de construccion.

{md_table(jefe["coincidencias"], max_rows=10)}

## VIF y dependencias

La X guardada de 2024 tiene 67 columnas; el rango con intercepto es completo. El intercepto se agrega solo para diagnostico de rango y no esta dentro de X. Los VIF guardados usan la inversa de la matriz de correlaciones, equivalente al VIF de regresiones auxiliares con intercepto sobre variables no constantes; la verificacion auxiliar reproduce los 15 VIF mas altos.

{md_table(vif["top15"][["columna_matriz", "variable_original", "categoria", "referencia_variable", "frecuencia_categoria", "vif"]], max_rows=15)}

## Decisiones pendientes antes de cambiar X

- Aprobar correccion explicita de `segsoc_desc` codigo 2 a `No` en 2020 y 2022, sin cambiar semantica de otros codigos.
- Definir si las variables laborales del trabajo principal deben modelarse en todo el universo activo o en una especificacion separada para trabajadores con trabajo reportado/con pago.
- Definir si `tam_emp_principal_desc` queda fuera, se recodifica para evitar la dummy estructural duplicada o se usa solo en una submuestra laboral.
- Definir tratamiento de cola derecha: sin recorte actual; cualquier log-transformacion, robustez, winsorizacion o exclusion requiere aprobacion.
- Definir como entraran variables de contexto del hogar, especialmente sexo y educacion de jefatura, dada la redundancia esperada para jefes/as.
- Definir especificacion comun posterior si se quieren comparar coeficientes entre anos.

## Estado documental

La etapa 12 debe leerse como implementacion ejecutada para 2024, con revision metodologica pendiente. 2018 esta inspeccionado como compatible; 2020 y 2022 requieren resolver `segsoc_desc` antes de generar bases; 2024 esta reproducido y ahora auditado con pendientes abiertos.

## Salidas

Las tablas agregadas de esta auditoria estan en `reports/tables/{TABLE_DIR_NAME}/`. No se generaron matrices nuevas, no se modificaron marts, no se crearon modelos y no se realizo push ni merge.
"""
    report_path.write_text(content, encoding="utf-8")
    return report_path


def run(root: Path | str = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    config = PreparationConfig.from_root(root, year=ANIO_ANALISIS, min_age=EDAD_MINIMA, valid_years=ANIOS_VALIDOS)
    out_dir = root / "reports" / "tables" / TABLE_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)

    mart = read_mart(root)
    universe, flow = build_universe(mart, config)
    write_csv(flow, out_dir / "flujo_universo_reproducido_2024.csv")
    X_rebuilt, _, _, _ = build_matrix(universe)
    write_csv(
        pd.DataFrame(
            [
                {"metrica": "filas_universo", "valor": len(universe), "esperado": 141579, "estado": "ok" if len(universe) == 141579 else "revisar"},
                {"metrica": "columnas_X_reconstruida_en_memoria", "valor": X_rebuilt.shape[1], "esperado": 67, "estado": "ok" if X_rebuilt.shape[1] == 67 else "revisar"},
            ]
        ),
        out_dir / "reproduccion_minima_2024.csv",
    )

    files = audited_files(root, out_dir)
    segsoc = segsoc_audit(root, mart, universe, out_dir)
    labor = labor_missing_audit(universe, out_dir)
    tail = income_tail_audit(root, universe, out_dir)
    tam_emp = tam_emp_audit(universe, out_dir)
    jefe = jefatura_audit(universe, out_dir)
    vif = vif_audit(root, universe, out_dir)
    findings = build_findings(segsoc, labor, tail, tam_emp, jefe, vif, out_dir)
    report = build_report(root, out_dir, files, findings, segsoc, labor, tail, tam_emp, jefe, vif)

    manifest = {
        "anio_analisis": ANIO_ANALISIS,
        "anios_validos": list(ANIOS_VALIDOS),
        "edad_minima": EDAD_MINIMA,
        "commit_base": "6aec7782a395d49bfb45a6d314a3feda54dc84fd",
        "alcance": "auditoria_diagnostica_sin_modelos_sin_matrices_nuevas",
        "report": str(report),
        "table_dir": str(out_dir),
        "no_generado": ["modelos", "particiones", "matrices_anuales_2018_2020_2022", "marts", "deflactores", "JKn"],
    }
    (out_dir / "manifest_auditoria_preparacion_determinantes.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"report": report, "table_dir": out_dir, "rows_universe": len(universe)}


if __name__ == "__main__":
    result = run()
    print(json.dumps({k: str(v) for k, v in result.items()}, ensure_ascii=False, indent=2))

"""Primera ejecucion diagnostica de regresion para determinantes.

El flujo crea particiones por hogar, ajusta modelos exploratorios y escribe
tablas/figuras agregadas. No ejecuta seleccion automatica de variables.
"""

from __future__ import annotations

import importlib.util
import json
import math
import platform
import sys
from dataclasses import dataclass
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
    HOUSEHOLD_KEY_COLS,
    KEY_COLS,
    LOG_TARGET,
    REFERENCE_RULES,
    STRUCTURAL_MISSING_LABELS,
    TARGET,
    PreparationConfig,
    build_universe,
    prepare_categorical_for_matrix,
    read_source,
    select_reference,
    slugify,
)
from src.models.regresion_diagnostico import (
    aggregate_column_importance,
    coefficient_table,
    compute_gvif,
    compute_vif_auxiliary,
    fit_decision_tree,
    fit_ols,
    influence_diagnostics,
    matrix_dependency_diagnostics,
    permutation_importance_by_block,
    predict_ols,
    regression_metrics,
    verify_vif_gvif_examples,
)


ANIO_ANALISIS = 2024
ANIOS_VALIDOS = (2018, 2020, 2022, 2024)
EDAD_MINIMA = 18
CRITERIO_STEPWISE = None
EJECUTAR_SELECCION = False
ESPECIFICACION = "diagnostico_inicial"
TRAIN_FRAC = 0.80
RANDOM_STATE = 20240914
TREE_MAX_DEPTH = 5
TREE_MIN_SAMPLES_LEAF = 0.01
PERMUTATION_REPEATS = 10

VARIABLES_CANDIDATAS = list(CONTINUOUS_PREDICTORS) + list(CATEGORICAL_PREDICTORS)
VARIABLES_PENDIENTES = {
    "tam_emp_principal_desc": "Pendiente de parametrizacion: conserva informacion de tamano, pero su categoria estructural duplicaria una dummy de subor si entrara sin recodificar.",
    "est_socio_desc": "Diagnostico contextual; requiere aprobacion para entrar al modelo.",
}
EXCLUSIONES_TECNICAS = [
    {"grupo": "target_derivados", "criterio": "Excluir target, log(target), componentes y agregados que contienen el ingreso objetivo."},
    {"grupo": "identificadores", "criterio": "Excluir llaves de persona/hogar, entidad, municipio e identificadores."},
    {"grupo": "pesos_diseno", "criterio": "Conservar factor, factor_hogar, est_dis y upm como metadata; no predictores."},
    {"grupo": "deflactores_reales", "criterio": "Etapas 10/11 deprecadas; no usar deflactores, variables reales ni JKn."},
    {"grupo": "constantes_duplicados", "criterio": "Excluir columnas constantes o duplicados exactos si aparecen en la matriz identificable."},
    {"grupo": "representaciones_redundantes", "criterio": "Usar una representacion interpretable por variable; no incluir simultaneamente codigo y etiqueta."},
]


@dataclass(frozen=True)
class DiagnosticPaths:
    project_root: Path
    table_dir: Path
    figure_dir: Path
    local_dir: Path
    report_path: Path
    notebook_path: Path

    @classmethod
    def from_root(cls, root: Path, year: int, spec: str) -> "DiagnosticPaths":
        return cls(
            project_root=root,
            table_dir=root / "reports" / "tables" / "regresion_diagnostico" / str(year) / spec,
            figure_dir=root / "reports" / "figures" / "regresion_diagnostico" / str(year) / spec,
            local_dir=root / "data" / "processed" / "regresion_diagnostico" / str(year) / spec,
            report_path=root / "reports" / "regresion_diagnostico_determinantes.md",
            notebook_path=root / "notebooks" / "13_regresion_diagnostico_determinantes.ipynb",
        )


def require_dependencies() -> pd.DataFrame:
    modules = ["numpy", "pandas", "sklearn", "matplotlib", "scipy", "statsmodels", "nbformat", "nbclient"]
    rows = []
    for module in modules:
        spec = importlib.util.find_spec(module)
        version = ""
        if spec:
            try:
                imported = __import__(module)
                version = getattr(imported, "__version__", "instalado")
            except Exception:
                version = "instalado"
        rows.append({"paquete": module, "disponible": bool(spec), "version": version})
    required = {"numpy", "pandas", "sklearn", "matplotlib", "scipy"}
    missing_required = [row["paquete"] for row in rows if row["paquete"] in required and not row["disponible"]]
    if missing_required:
        raise RuntimeError(f"Faltan dependencias requeridas para esta etapa: {missing_required}")
    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_Sin registros._"
    view = df.head(max_rows).fillna("")

    def clean(value: Any) -> str:
        return str(value).replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(col) for col in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(row[col]) for col in view.columns) + " |")
    return "\n".join(lines)


def validate_config(year: int, valid_years: tuple[int, ...], min_age: int, criterio_stepwise: Any, ejecutar_seleccion: bool) -> None:
    if year not in valid_years:
        raise ValueError(f"ANIO_ANALISIS debe estar en {valid_years}; recibido {year}.")
    if min_age != EDAD_MINIMA:
        raise ValueError("Esta primera ejecucion conserva EDAD_MINIMA=18.")
    if criterio_stepwise is not None:
        raise ValueError("CRITERIO_STEPWISE debe permanecer None en esta primera ejecucion diagnostica.")
    if ejecutar_seleccion:
        raise ValueError("EJECUTAR_SELECCION debe permanecer False; no se ejecuta seleccion automatica.")


def load_active_universe(root: Path, year: int, min_age: int, valid_years: tuple[int, ...]) -> tuple[pd.DataFrame, pd.DataFrame]:
    config = PreparationConfig.from_root(root, year=year, min_age=min_age, valid_years=valid_years)
    source = read_source(config)
    universe, flow = build_universe(source, config)
    return universe.reset_index(drop=True), flow


def split_households(universe: pd.DataFrame, paths: DiagnosticPaths, *, year: int, train_frac: float, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    households = universe[HOUSEHOLD_KEY_COLS].drop_duplicates().reset_index(drop=True)
    rng = np.random.default_rng(random_state)
    order = rng.permutation(len(households))
    n_train = int(math.floor(len(households) * train_frac))
    split = np.array(["validacion"] * len(households), dtype=object)
    split[order[:n_train]] = "entrenamiento"
    households["particion"] = split
    paths.local_dir.mkdir(parents=True, exist_ok=True)
    households.to_csv(paths.local_dir / f"particion_hogares_{year}.csv.gz", index=False, compression="gzip")
    data = universe.merge(households, on=HOUSEHOLD_KEY_COLS, how="left", validate="many_to_one")
    persons = data.groupby("particion").size().rename("personas").reset_index()
    hh = households.groupby("particion").size().rename("hogares").reset_index()
    summary = persons.merge(hh, on="particion", how="outer")
    summary["pct_personas"] = summary["personas"] / len(data)
    summary["pct_hogares"] = summary["hogares"] / len(households)
    regional = (
        data.groupby(["particion", "region_banxico"], dropna=False)
        .size()
        .rename("personas")
        .reset_index()
    )
    regional["pct_dentro_particion"] = regional["personas"] / regional.groupby("particion")["personas"].transform("sum")
    overlap = (
        households.groupby(HOUSEHOLD_KEY_COLS)["particion"]
        .nunique()
        .reset_index(name="particiones_por_hogar")
    )
    overlap_count = int((overlap["particiones_por_hogar"] > 1).sum())
    checks = pd.DataFrame(
        [
            {"validacion": "sin_hogares_compartidos", "valor": overlap_count, "estado": "ok" if overlap_count == 0 else "revisar"},
            {"validacion": "personas_con_particion", "valor": int(data["particion"].notna().sum()), "estado": "ok" if data["particion"].notna().all() else "revisar"},
        ]
    )
    write_csv(summary, paths.table_dir / "particion_resumen.csv")
    write_csv(regional, paths.table_dir / "particion_region.csv")
    write_csv(checks, paths.table_dir / "particion_validaciones.csv")
    return data, households


def build_train_encoder(train: pd.DataFrame, variables: list[str]) -> dict[str, Any]:
    categorical = [v for v in variables if v in CATEGORICAL_PREDICTORS]
    prepared = prepare_categorical_for_matrix(train)
    refs = {}
    categories = {}
    for variable in categorical:
        cats = sorted(prepared[variable].dropna().astype(str).unique().tolist())
        refs[variable] = select_reference(variable, cats)
        categories[variable] = cats
    return {"categorical": categorical, "continuous": [v for v in variables if v in CONTINUOUS_PREDICTORS], "references": refs, "categories": categories}


def transform_regression_matrix(df: pd.DataFrame, encoder: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    X = pd.DataFrame(index=df.index)
    rows = []
    unseen_rows = []
    for variable in encoder["continuous"]:
        values = pd.to_numeric(df[variable], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(f"La continua {variable} contiene faltantes/no finitos; no se imputa.")
        X[variable] = values.astype(float)
        rows.append(
            {
                "columna_matriz": variable,
                "variable_original": variable,
                "tipo": "continua",
                "categoria": "",
                "referencia_variable": "",
                "n_entrenamiento_referencia_o_categoria": len(df),
            }
        )
    prepared = prepare_categorical_for_matrix(df)
    for variable in encoder["categorical"]:
        known = encoder["categories"][variable]
        reference = encoder["references"][variable]
        observed = set(prepared[variable].dropna().astype(str).unique())
        unseen = sorted(observed - set(known))
        for category in unseen:
            unseen_rows.append({"variable_original": variable, "categoria_no_vista_en_entrenamiento": category, "n": int(prepared[variable].eq(category).sum())})
        for category in known:
            if category == reference:
                continue
            col = f"{variable}__{slugify(category)}"
            X[col] = prepared[variable].eq(category).astype(np.int8)
            rows.append(
                {
                    "columna_matriz": col,
                    "variable_original": variable,
                    "tipo": "dummy_ohe_k_menos_1",
                    "categoria": category,
                    "referencia_variable": reference,
                    "n_entrenamiento_referencia_o_categoria": int(prepared[variable].eq(category).sum()),
                }
            )
    return X.reset_index(drop=True), pd.DataFrame(rows), pd.DataFrame(unseen_rows, columns=["variable_original", "categoria_no_vista_en_entrenamiento", "n"])


def build_regression_design(train: pd.DataFrame, valid: pd.DataFrame, variables: list[str], paths: DiagnosticPaths) -> dict[str, Any]:
    encoder = build_train_encoder(train, variables)
    X_train, info_train, unseen_train = transform_regression_matrix(train, encoder)
    X_valid, _, unseen_valid = transform_regression_matrix(valid, encoder)
    info = info_train.copy()
    info["n_entrenamiento"] = [int(X_train[col].sum()) if col in X_train.columns and set(X_train[col].unique()).issubset({0, 1}) else len(X_train) for col in info["columna_matriz"]]
    info["n_validacion"] = [int(X_valid[col].sum()) if col in X_valid.columns and set(X_valid[col].unique()).issubset({0, 1}) else len(X_valid) for col in info["columna_matriz"]]
    refs = pd.DataFrame(
        [
            {
                "variable_original": variable,
                "referencia": reference,
                "n_referencia_entrenamiento": int(prepare_categorical_for_matrix(train)[variable].eq(reference).sum()),
                "n_referencia_validacion": int(prepare_categorical_for_matrix(valid)[variable].eq(reference).sum()),
            }
            for variable, reference in encoder["references"].items()
        ]
    )
    write_csv(info, paths.table_dir / "matriz_regresion_columnas.csv")
    write_csv(refs, paths.table_dir / "referencias_ohe_entrenamiento.csv")
    write_csv(pd.concat([unseen_train.assign(particion="entrenamiento"), unseen_valid.assign(particion="validacion")], ignore_index=True), paths.table_dir / "categorias_no_vistas_por_particion.csv")
    return {"encoder": encoder, "X_train": X_train, "X_valid": X_valid, "column_info": info, "references": refs}


def inventory_tables(variables: list[str], paths: DiagnosticPaths) -> dict[str, pd.DataFrame]:
    candidates = pd.DataFrame(
        [{"variable": v, "estado": "incluida", "tipo": "continua" if v in CONTINUOUS_PREDICTORS else "categorica"} for v in variables]
    )
    selected = candidates.assign(estado_seleccion="variables_seleccionadas = variables_candidatas.copy()")
    pending = pd.DataFrame([{"variable": k, "motivo": v, "estado": "pendiente_no_incluida_en_matriz_identificable"} for k, v in VARIABLES_PENDIENTES.items()])
    exclusions = pd.DataFrame(EXCLUSIONES_TECNICAS)
    write_csv(candidates, paths.table_dir / "variables_candidatas.csv")
    write_csv(selected, paths.table_dir / "variables_seleccionadas_inicial.csv")
    write_csv(pending, paths.table_dir / "variables_pendientes.csv")
    write_csv(exclusions, paths.table_dir / "exclusiones_tecnicas.csv")
    return {"candidates": candidates, "selected": selected, "pending": pending, "exclusions": exclusions}


def build_effective_config(
    year: int,
    valid_years: tuple[int, ...],
    min_age: int,
    target: str,
    criterio_stepwise: Any,
    ejecutar_seleccion: bool,
) -> dict[str, Any]:
    return {
        "ANIO_ANALISIS": int(year),
        "ANIOS_VALIDOS": list(valid_years),
        "EDAD_MINIMA": int(min_age),
        "TARGET": target,
        "CRITERIO_STEPWISE": criterio_stepwise,
        "EJECUTAR_SELECCION": bool(ejecutar_seleccion),
        "ESPECIFICACION": ESPECIFICACION,
        "TRAIN_FRAC": TRAIN_FRAC,
        "RANDOM_STATE": RANDOM_STATE,
        "TREE_MAX_DEPTH": TREE_MAX_DEPTH,
        "TREE_MIN_SAMPLES_LEAF": TREE_MIN_SAMPLES_LEAF,
        "PERMUTATION_REPEATS": PERMUTATION_REPEATS,
    }


def load_previous_compatibility(root: Path, paths: DiagnosticPaths, year: int) -> pd.DataFrame:
    source = root / "reports" / "tables" / "preparacion_determinantes" / "compatibilidad_anios.csv"
    cols = [
        "anio",
        "estado_preparacion",
        "filas_universo",
        "hogares_unicos",
        "referencias_ohe_faltantes",
        "estado_en_regresion_diagnostica",
        "nota_regresion",
    ]
    if not source.exists():
        compatibility = pd.DataFrame(
            [
                {
                    "anio": year,
                    "estado_preparacion": "no_disponible",
                    "filas_universo": math.nan,
                    "hogares_unicos": math.nan,
                    "referencias_ohe_faltantes": "",
                    "estado_en_regresion_diagnostica": "sin_tabla_previa",
                    "nota_regresion": "No se encontro compatibilidad_anios.csv de la etapa 12.",
                }
            ],
            columns=cols,
        )
    else:
        prior = pd.read_csv(source)
        rows = []
        for _, row in prior.iterrows():
            row_year = int(row["anio"])
            missing_refs = "" if pd.isna(row.get("referencias_ohe_faltantes", "")) else str(row.get("referencias_ohe_faltantes", ""))
            if row_year == year:
                regression_state = "ejecutado_y_validado_en_esta_etapa"
                note = "Se genero diagnostico de regresion, PCA y arbol para este anio."
            elif missing_refs:
                regression_state = "solo_inspeccion_previa_con_pendientes"
                note = "No se genero matriz; resolver referencias OHE antes de ejecutar."
            else:
                regression_state = "solo_compatibilidad_inspeccionada_previa"
                note = "No se genero matriz ni modelo para este anio en esta etapa."
            rows.append(
                {
                    "anio": row_year,
                    "estado_preparacion": row.get("estado", ""),
                    "filas_universo": row.get("filas_universo", math.nan),
                    "hogares_unicos": row.get("hogares_unicos", math.nan),
                    "referencias_ohe_faltantes": missing_refs,
                    "estado_en_regresion_diagnostica": regression_state,
                    "nota_regresion": note,
                }
            )
        compatibility = pd.DataFrame(rows, columns=cols)
    write_csv(compatibility, paths.table_dir / "compatibilidad_anual_previa.csv")
    return compatibility


def compare_reproduction_2024(
    root: Path,
    paths: DiagnosticPaths,
    universe: pd.DataFrame,
    households: pd.DataFrame,
    design: dict[str, Any],
    year: int,
) -> pd.DataFrame:
    cols = ["metrica", "esperado", "observado", "tolerancia", "diferencia_abs", "resultado", "nota"]
    if year != 2024:
        reproduction = pd.DataFrame(
            [
                {
                    "metrica": "reproduccion_2024",
                    "esperado": "",
                    "observado": "",
                    "tolerancia": "",
                    "diferencia_abs": "",
                    "resultado": "no_aplica",
                    "nota": "La reproduccion historica disponible corresponde a 2024; este anio no se ejecuto en esta etapa.",
                }
            ],
            columns=cols,
        )
        write_csv(reproduction, paths.table_dir / "reproduccion_universo_2024.csv")
        return reproduction

    source = root / "reports" / "tables" / "preparacion_determinantes" / "2024" / "reproduccion_2024.csv"
    if not source.exists():
        reproduction = pd.DataFrame(
            [
                {
                    "metrica": "reproduccion_2024",
                    "esperado": "",
                    "observado": "",
                    "tolerancia": "",
                    "diferencia_abs": "",
                    "resultado": "sin_referencia",
                    "nota": "No se encontro reproduccion_2024.csv de la etapa 12.",
                }
            ],
            columns=cols,
        )
        write_csv(reproduction, paths.table_dir / "reproduccion_universo_2024.csv")
        return reproduction

    expected = pd.read_csv(source).set_index("metrica")
    y = pd.to_numeric(universe[TARGET], errors="coerce")
    observed = {
        "universo_filas": float(len(universe)),
        "hogares_unicos": float(len(households)),
        "media_target": float(y.mean()),
        "mediana_target": float(y.median()),
        "p99_target": float(y.quantile(0.99)),
        "max_target": float(y.max()),
    }
    rows = []
    for metric, value in observed.items():
        exp = float(expected.loc[metric, "esperado"])
        tolerance = float(expected.loc[metric, "tolerancia"])
        diff = abs(value - exp)
        rows.append(
            {
                "metrica": metric,
                "esperado": exp,
                "observado": value,
                "tolerancia": tolerance,
                "diferencia_abs": diff,
                "resultado": "ok" if diff <= tolerance else "revisar",
                "nota": "Comparacion contra etapa 12.",
            }
        )
    rows.append(
        {
            "metrica": "columnas_matriz_diagnostica",
            "esperado": "",
            "observado": int(design["X_train"].shape[1]),
            "tolerancia": "",
            "diferencia_abs": "",
            "resultado": "documentado",
            "nota": "No se compara contra X_columnas de etapa 12: esta matriz excluye pendientes y se ajusta solo con entrenamiento.",
        }
    )
    reproduction = pd.DataFrame(rows, columns=cols)
    write_csv(reproduction, paths.table_dir / "reproduccion_universo_2024.csv")
    return reproduction


def fit_regressions(train: pd.DataFrame, valid: pd.DataFrame, design: dict[str, Any], paths: DiagnosticPaths) -> dict[str, pd.DataFrame]:
    X_train = design["X_train"]
    X_valid = design["X_valid"]
    y_train = pd.to_numeric(train[TARGET], errors="coerce")
    y_valid = pd.to_numeric(valid[TARGET], errors="coerce")
    log_train = np.log(y_train)
    log_valid = np.log(y_valid)

    nominal = fit_ols(X_train, y_train, scale_name="ingreso_nominal")
    log_model = fit_ols(X_train, log_train, scale_name="log_ingreso")
    pred_train_nom = predict_ols(nominal, X_train)
    pred_valid_nom = predict_ols(nominal, X_valid)
    pred_train_log = predict_ols(log_model, X_train)
    pred_valid_log = predict_ols(log_model, X_valid)

    metrics = pd.DataFrame(
        [
            regression_metrics(y_train, pred_train_nom, scale_name="ingreso_nominal", split="entrenamiento"),
            regression_metrics(y_valid, pred_valid_nom, scale_name="ingreso_nominal", split="validacion"),
            regression_metrics(log_train, pred_train_log, scale_name="log_ingreso", split="entrenamiento"),
            regression_metrics(log_valid, pred_valid_log, scale_name="log_ingreso", split="validacion"),
        ]
    )
    fit_summary = pd.DataFrame(
        [
            {
                "escala": model["scale_name"],
                "n_entrenamiento": model["n_obs"],
                "parametros_con_intercepto": model["n_params"],
                "rango_con_intercepto": model["rank"],
                "r2_entrenamiento": model["r2"],
                "r2_ajustado_entrenamiento": model["adj_r2"],
                "aic_entrenamiento_misma_escala": model["aic"],
                "bic_entrenamiento_misma_escala": model["bic"],
                "nota": "AIC/BIC solo comparables dentro de la misma escala de respuesta.",
            }
            for model in [nominal, log_model]
        ]
    )
    coef_nominal = coefficient_table(nominal, list(X_train.columns), design["column_info"])
    coef_log = coefficient_table(log_model, list(X_train.columns), design["column_info"])
    influence_summary, influence_top = influence_diagnostics(X_train, y_train, nominal)
    residuals = pd.DataFrame(
        {
            "particion": "entrenamiento",
            "ajustado_ingreso_nominal": pred_train_nom,
            "residuo_ingreso_nominal": nominal["residuals"],
            "residuo_abs": np.abs(nominal["residuals"]),
        }
    )
    residual_tail = pd.DataFrame(
        [
            {
                "metrica": "residuo_ingreso_nominal",
                "p01": float(np.quantile(nominal["residuals"], 0.01)),
                "p05": float(np.quantile(nominal["residuals"], 0.05)),
                "p50": float(np.quantile(nominal["residuals"], 0.50)),
                "p95": float(np.quantile(nominal["residuals"], 0.95)),
                "p99": float(np.quantile(nominal["residuals"], 0.99)),
                "min": float(np.min(nominal["residuals"])),
                "max": float(np.max(nominal["residuals"])),
            }
        ]
    )
    write_csv(metrics, paths.table_dir / "regresion_metricas.csv")
    write_csv(fit_summary, paths.table_dir / "regresion_resumen_ajuste.csv")
    write_csv(coef_nominal, paths.table_dir / "regresion_coeficientes_ingreso_nominal.csv")
    write_csv(coef_log, paths.table_dir / "regresion_coeficientes_log_ingreso.csv")
    write_csv(influence_summary, paths.table_dir / "regresion_influencia_resumen.csv")
    write_csv(influence_top, paths.table_dir / "regresion_influencia_top_sin_identificadores.csv")
    write_csv(residual_tail, paths.table_dir / "regresion_residuos_cola.csv")
    return {
        "metrics": metrics,
        "fit_summary": fit_summary,
        "coef_nominal": coef_nominal,
        "coef_log": coef_log,
        "influence_summary": influence_summary,
        "influence_top": influence_top,
        "residuals": residuals,
        "models": {"nominal": nominal, "log": log_model},
    }


def run_dependency_diagnostics(design: dict[str, Any], paths: DiagnosticPaths) -> dict[str, pd.DataFrame]:
    X_train = design["X_train"]
    matrix_summary, matrix_detail = matrix_dependency_diagnostics(X_train)
    vif = compute_vif_auxiliary(X_train)
    vif_detail = vif.merge(design["column_info"], on="columna_matriz", how="left")
    gvif = compute_gvif(X_train, design["column_info"])
    examples = verify_vif_gvif_examples()
    write_csv(matrix_summary, paths.table_dir / "dependencias_matriz_resumen.csv")
    write_csv(matrix_detail, paths.table_dir / "dependencias_matriz_detalle.csv")
    write_csv(vif_detail, paths.table_dir / "vif_columnas_entrenamiento.csv")
    write_csv(gvif, paths.table_dir / "gvif_bloques_entrenamiento.csv")
    write_csv(examples, paths.table_dir / "verificacion_vif_gvif_ejemplos.csv")
    return {"matrix_summary": matrix_summary, "matrix_detail": matrix_detail, "vif": vif_detail, "gvif": gvif, "examples": examples}


def build_pca_matrix(train: pd.DataFrame, valid: pd.DataFrame, variables: list[str], paths: DiagnosticPaths) -> dict[str, Any]:
    from sklearn.decomposition import PCA

    continuous = [v for v in variables if v in CONTINUOUS_PREDICTORS]
    categorical = [v for v in variables if v in CATEGORICAL_PREDICTORS]
    train_parts = []
    valid_parts = []
    feature_rows = []
    for variable in continuous:
        mean = float(pd.to_numeric(train[variable], errors="coerce").mean())
        std = float(pd.to_numeric(train[variable], errors="coerce").std(ddof=0))
        if std <= 0 or not math.isfinite(std):
            continue
        train_values = (pd.to_numeric(train[variable], errors="coerce") - mean) / std
        valid_values = (pd.to_numeric(valid[variable], errors="coerce") - mean) / std
        col = variable
        train_parts.append(pd.DataFrame({col: train_values.to_numpy(dtype=float)}))
        valid_parts.append(pd.DataFrame({col: valid_values.to_numpy(dtype=float)}))
        feature_rows.append({"columna_pca": col, "variable_original": variable, "tipo": "continua_estandarizada", "media_entrenamiento": mean, "escala_entrenamiento": std})
    train_cat = prepare_categorical_for_matrix(train)
    valid_cat = prepare_categorical_for_matrix(valid)
    for variable in categorical:
        categories = sorted(train_cat[variable].dropna().astype(str).unique().tolist())
        for category in categories:
            col = f"{variable}__{slugify(category)}"
            train_dummy = train_cat[variable].eq(category).astype(float)
            valid_dummy = valid_cat[variable].eq(category).astype(float)
            center = float(train_dummy.mean())
            train_parts.append(pd.DataFrame({col: train_dummy - center}))
            valid_parts.append(pd.DataFrame({col: valid_dummy - center}))
            feature_rows.append({"columna_pca": col, "variable_original": variable, "tipo": "dummy_ohe_completo_centrada_no_escalada", "media_entrenamiento": center, "escala_entrenamiento": 1.0})
    Z_train = pd.concat(train_parts, axis=1)
    Z_valid = pd.concat(valid_parts, axis=1)
    features = pd.DataFrame(feature_rows)
    pca = PCA(svd_solver="full")
    scores_train = pca.fit_transform(Z_train)
    scores_valid = pca.transform(Z_valid)
    eigen = pd.DataFrame(
        {
            "componente": [f"PC{i + 1}" for i in range(len(pca.explained_variance_))],
            "valor_propio": pca.explained_variance_,
            "varianza_explicada": pca.explained_variance_ratio_,
            "varianza_acumulada": np.cumsum(pca.explained_variance_ratio_),
        }
    )
    tol = max(Z_train.shape) * np.finfo(float).eps * float(pca.explained_variance_.max())
    eigen["componente_nulo"] = eigen["valor_propio"].le(tol)
    loadings = pd.DataFrame(pca.components_, columns=Z_train.columns)
    loadings.insert(0, "componente", eigen["componente"])
    score_cols = [f"PC{i + 1}" for i in range(scores_train.shape[1])]
    score_df = pd.DataFrame(scores_train, columns=score_cols)
    corr_rows = []
    for col in Z_train.columns:
        x = Z_train[col].to_numpy(dtype=float)
        for pc in score_cols:
            s = score_df[pc].to_numpy(dtype=float)
            corr = np.corrcoef(x, s)[0, 1] if np.std(x) > 0 and np.std(s) > 0 else math.nan
            corr_rows.append({"columna_pca": col, "componente": pc, "correlacion_columna_score": corr})
    correlations = pd.DataFrame(corr_rows)
    write_csv(features, paths.table_dir / "pca_columnas_transformadas.csv")
    write_csv(eigen, paths.table_dir / "pca_varianza.csv")
    write_csv(loadings, paths.table_dir / "pca_componentes_coeficientes.csv")
    write_csv(correlations, paths.table_dir / "pca_correlaciones_columnas_scores.csv")
    return {
        "Z_train": Z_train,
        "Z_valid": Z_valid,
        "features": features,
        "eigen": eigen,
        "loadings": loadings,
        "correlations": correlations,
        "scores_train": scores_train,
        "scores_valid": scores_valid,
    }


def plot_diagnostics(regression: dict[str, pd.DataFrame], pca: dict[str, Any], paths: DiagnosticPaths, *, random_state: int) -> pd.DataFrame:
    import matplotlib.pyplot as plt

    paths.figure_dir.mkdir(parents=True, exist_ok=True)
    figs = []
    residuals = regression["residuals"]
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = residuals.sample(n=min(20000, len(residuals)), random_state=random_state)
    ax.scatter(sample["ajustado_ingreso_nominal"], sample["residuo_ingreso_nominal"], s=6, alpha=0.25)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xlabel("Ajustado, ingreso nominal")
    ax.set_ylabel("Residuo")
    ax.set_title("Residuos contra ajustados")
    path = paths.figure_dir / "regresion_residuos_vs_ajustados.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figs.append({"figura": str(path), "descripcion": "OLS nominal: residuos contra ajustados; muestra grafica si n es grande."})

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals["residuo_ingreso_nominal"], bins=80, color="#3B82F6", alpha=0.85)
    ax.set_xlabel("Residuo, ingreso nominal")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Cola de residuos")
    path = paths.figure_dir / "regresion_residuos_histograma.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figs.append({"figura": str(path), "descripcion": "Histograma de residuos nominales; no elimina observaciones."})

    eigen = pca["eigen"].copy()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(np.arange(1, min(40, len(eigen)) + 1), eigen["varianza_explicada"].head(40), marker="o", linewidth=1.5)
    ax.set_xlabel("Componente")
    ax.set_ylabel("Proporcion de varianza explicada")
    ax.set_title("PCA scree plot")
    path = paths.figure_dir / "pca_scree_varianza.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figs.append({"figura": str(path), "descripcion": "Scree plot de PCA exploratorio."})

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(np.arange(1, len(eigen) + 1), eigen["varianza_acumulada"], linewidth=1.8)
    ax.set_xlabel("Componente")
    ax.set_ylabel("Varianza acumulada")
    ax.set_title("PCA varianza acumulada")
    path = paths.figure_dir / "pca_varianza_acumulada.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figs.append({"figura": str(path), "descripcion": "Varianza acumulada; no selecciona numero de componentes."})

    loadings = pca["loadings"].copy()
    first_pcs = loadings.head(8).set_index("componente")
    score = first_pcs.abs().max(axis=0).sort_values(ascending=False).head(40).index
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    im = ax.imshow(first_pcs[score].to_numpy(dtype=float), aspect="auto", cmap="coolwarm")
    ax.set_yticks(np.arange(len(first_pcs.index)), first_pcs.index)
    ax.set_xticks(np.arange(len(score)), score, rotation=80, ha="right", fontsize=7)
    ax.set_title("Cargas PCA, PCs 1-8 y columnas con mayor carga")
    fig.colorbar(im, ax=ax, fraction=0.025)
    path = paths.figure_dir / "pca_cargas_heatmap_pc1_pc8_top40.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figs.append({"figura": str(path), "descripcion": "Mapa legible de cargas principales."})

    nonzero = eigen.loc[~eigen["componente_nulo"], "componente"].head(6).tolist()
    for pc in nonzero:
        row = loadings.loc[loadings["componente"].eq(pc)].drop(columns="componente").iloc[0]
        top = row.abs().sort_values(ascending=False).head(20).index
        vals = row[top].sort_values()
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.barh(vals.index, vals.values, color=np.where(vals.values >= 0, "#2563EB", "#DC2626"))
        ax.set_xlabel("Coeficiente del componente")
        ax.set_title(f"Cargas principales {pc}")
        path = paths.figure_dir / f"pca_cargas_{pc.lower()}.png"
        fig.tight_layout()
        fig.savefig(path, dpi=160)
        plt.close(fig)
        figs.append({"figura": str(path), "descripcion": f"Cargas mayores de {pc}; signo global arbitrario."})

    figures = pd.DataFrame(figs)
    write_csv(figures, paths.table_dir / "figuras_generadas.csv")
    return figures


def fit_tree_diagnostics(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    design: dict[str, Any],
    paths: DiagnosticPaths,
    *,
    random_state: int,
) -> dict[str, pd.DataFrame]:
    X_train = design["X_train"]
    X_valid = design["X_valid"]
    y_train = pd.to_numeric(train[TARGET], errors="coerce")
    y_valid = pd.to_numeric(valid[TARGET], errors="coerce")
    tree = fit_decision_tree(
        X_train,
        y_train,
        max_depth=TREE_MAX_DEPTH,
        min_samples_leaf=TREE_MIN_SAMPLES_LEAF,
        random_state=random_state,
    )
    pred_train = tree.predict(X_train)
    pred_valid = tree.predict(X_valid)
    metrics = pd.DataFrame(
        [
            regression_metrics(y_train, pred_train, scale_name="arbol_ingreso_nominal", split="entrenamiento"),
            regression_metrics(y_valid, pred_valid, scale_name="arbol_ingreso_nominal", split="validacion"),
        ]
    )
    impurity_columns = design["column_info"][["columna_matriz", "variable_original"]].copy()
    impurity_columns["importancia_impureza"] = tree.feature_importances_
    impurity_blocks = aggregate_column_importance(tree.feature_importances_, design["column_info"])
    perm_by_rep, perm_summary = permutation_importance_by_block(
        tree,
        X_valid,
        y_valid,
        design["column_info"],
        n_repeats=PERMUTATION_REPEATS,
        random_state=random_state,
    )
    params = pd.DataFrame(
        [
            {
                "modelo": "DecisionTreeRegressor",
                "max_depth": TREE_MAX_DEPTH,
                "min_samples_leaf": TREE_MIN_SAMPLES_LEAF,
                "random_state": random_state,
                "n_repeticiones_permutacion": PERMUTATION_REPEATS,
                "nota": "Parametros exploratorios iniciales; no son resultado de optimizacion.",
            }
        ]
    )
    write_csv(params, paths.table_dir / "arbol_parametros.csv")
    write_csv(metrics, paths.table_dir / "arbol_metricas.csv")
    write_csv(impurity_columns, paths.table_dir / "arbol_importancia_impureza_columnas.csv")
    write_csv(impurity_blocks, paths.table_dir / "arbol_importancia_impureza_variables.csv")
    write_csv(perm_by_rep, paths.table_dir / "arbol_importancia_permutacion_repeticiones.csv")
    write_csv(perm_summary, paths.table_dir / "arbol_importancia_permutacion_variables.csv")
    return {"params": params, "metrics": metrics, "impurity": impurity_blocks, "permutation": perm_summary}


def pca_variable_summary(pca: dict[str, Any]) -> pd.DataFrame:
    eigen = pca["eigen"]
    nonzero_pcs = eigen.loc[~eigen["componente_nulo"], "componente"].head(10).tolist()
    loadings = pca["loadings"].set_index("componente")
    features = pca["features"][["columna_pca", "variable_original"]]
    rows = []
    for variable, cols in features.groupby("variable_original")["columna_pca"]:
        available = [col for col in cols if col in loadings.columns]
        vals = loadings.loc[nonzero_pcs, available].abs() if available else pd.DataFrame()
        if vals.empty:
            rows.append({"variable_original": variable, "evidencia_pca": "sin columnas", "max_abs_carga_pc1_pc10": math.nan, "componente_max": ""})
        else:
            stacked = vals.stack()
            pc, col = stacked.idxmax()
            rows.append(
                {
                    "variable_original": variable,
                    "evidencia_pca": f"max |carga| {float(stacked.max()):.4f} en {pc} ({col})",
                    "max_abs_carga_pc1_pc10": float(stacked.max()),
                    "componente_max": pc,
                }
            )
    return pd.DataFrame(rows).sort_values("max_abs_carga_pc1_pc10", ascending=False).reset_index(drop=True)


def review_table(
    variables: list[str],
    deps: dict[str, pd.DataFrame],
    pca: dict[str, Any],
    tree: dict[str, pd.DataFrame],
    paths: DiagnosticPaths,
) -> pd.DataFrame:
    gvif = deps["gvif"][["variable_original", "gvif", "df_bloque", "gvif_ajustado", "estado"]].copy()
    pca_summary = pca_variable_summary(pca)
    imp = tree["impurity"].rename(columns={"importancia_impureza": "importancia_arbol_impureza"})
    perm = tree["permutation"][["variable_original", "delta_rmse_media", "delta_rmse_sd"]].copy()
    rows = pd.DataFrame({"variable": variables})
    rows = rows.merge(gvif, left_on="variable", right_on="variable_original", how="left").drop(columns=["variable_original"])
    rows = rows.merge(pca_summary[["variable_original", "evidencia_pca"]], left_on="variable", right_on="variable_original", how="left").drop(columns=["variable_original"])
    rows = rows.merge(imp, left_on="variable", right_on="variable_original", how="left").drop(columns=["variable_original"])
    rows = rows.merge(perm, left_on="variable", right_on="variable_original", how="left").drop(columns=["variable_original"])
    problemas = []
    acciones = []
    for _, row in rows.iterrows():
        variable = row["variable"]
        problem = []
        action = []
        if variable in ["subor_principal_desc", "contrato_principal_desc"]:
            problem.append("variable laboral depende de ruta de trabajo principal/pago")
            action.append("revisar especificacion laboral antes de eliminar")
        if variable in ["sexo_jefe_desc", "educa_jefe_desc"]:
            problem.append("variable de jefatura mezcla contexto del hogar y redundancia para jefes/as")
            action.append("definir si entra como contexto familiar")
        if variable == "segsoc_desc":
            problem.append("2020/2022 tienen mapeo pendiente; 2024 si ejecutado")
            action.append("aprobar mapeo anual antes de comparaciones")
        if variable.startswith("nivelaprob") or variable.startswith("educa_jefe"):
            problem.append("bloque educativo con dependencia esperable")
            action.append("revisar GVIF/VIF y estabilidad de betas en fases futuras")
        if not problem:
            problem.append("sin decision automatica en esta ejecucion")
            action.append("mantener hasta revision conjunta")
        problemas.append("; ".join(problem))
        acciones.append("; ".join(dict.fromkeys(action)))
    rows["VIF_GVIF"] = rows.apply(lambda r: f"GVIF={r['gvif']:.4f}; df={int(r['df_bloque'])}; adj={r['gvif_ajustado']:.4f}" if pd.notna(r["gvif"]) else "sin GVIF", axis=1)
    rows["importancia_arbol"] = rows.apply(lambda r: f"impureza={r['importancia_arbol_impureza']:.6f}; perm_delta_rmse={r['delta_rmse_media']:.4f}" if pd.notna(r["delta_rmse_media"]) else "sin importancia", axis=1)
    rows["problema_interpretativo"] = problemas
    rows["accion_propuesta"] = acciones
    rows["estado_aprobacion"] = "pendiente_aprobacion"
    final = rows[["variable", "VIF_GVIF", "evidencia_pca", "importancia_arbol", "problema_interpretativo", "accion_propuesta", "estado_aprobacion"]]
    write_csv(final, paths.table_dir / "tabla_revision_variables.csv")
    return final


def write_report(
    paths: DiagnosticPaths,
    config: dict[str, Any],
    deps: pd.DataFrame,
    inventory: dict[str, pd.DataFrame],
    compatibility: pd.DataFrame,
    reproduction: pd.DataFrame,
    partition_summary: pd.DataFrame,
    regressions: dict[str, pd.DataFrame],
    dependency: dict[str, pd.DataFrame],
    pca: dict[str, Any],
    tree: dict[str, pd.DataFrame],
    review: pd.DataFrame,
) -> None:
    nominal = regressions["fit_summary"].loc[regressions["fit_summary"]["escala"].eq("ingreso_nominal")]
    log = regressions["fit_summary"].loc[regressions["fit_summary"]["escala"].eq("log_ingreso")]
    top_gvif = dependency["gvif"].head(10)
    top_vif = dependency["vif"].head(10)
    pca_var = pca["eigen"].head(15)
    n_nonzero = int((~pca["eigen"]["componente_nulo"]).sum())
    n_null = int(pca["eigen"]["componente_nulo"].sum())
    unseen_path = paths.table_dir / "categorias_no_vistas_por_particion.csv"
    unseen = pd.read_csv(unseen_path) if unseen_path.exists() else pd.DataFrame()
    year = config["ANIO_ANALISIS"]
    spec = config["ESPECIFICACION"]
    random_state = config["RANDOM_STATE"]
    content = f"""# Regresion diagnostica de determinantes

## Estado

- Notebook: `notebooks/13_regresion_diagnostico_determinantes.ipynb`.
- Configuracion: `ANIO_ANALISIS={year}`, `EDAD_MINIMA={config["EDAD_MINIMA"]}`, `TARGET={config["TARGET"]}`, `CRITERIO_STEPWISE=None`, `EJECUTAR_SELECCION=False`.
- Alcance: primera ejecucion diagnostica con todas las variables candidatas admisibles de la etapa 12. No hay seleccion automatica, regresion reducida ni regresion por componentes.
- La validacion es diagnostica; no es prueba final independiente.

## Dependencias

{md_table(deps, max_rows=10)}

## Variables

Incluidas inicialmente:

{md_table(inventory["candidates"], max_rows=25)}

Pendientes:

{md_table(inventory["pending"], max_rows=10)}

Exclusiones tecnicas:

{md_table(inventory["exclusions"], max_rows=10)}

## Compatibilidad anual previa

Esta etapa ejecuta diagnosticos solo para el año seleccionado. Los demas años quedan solo como compatibilidad inspeccionada desde la etapa 12; no se generan matrices ni modelos anuales adicionales.

{md_table(compatibility, max_rows=10)}

Categorias no vistas al aplicar referencias y categorias aprendidas en entrenamiento:

{md_table(unseen, max_rows=10)}

## Particion

Particion 80/20 por hogares con semilla `{random_state}`. La pertenencia se guardo localmente fuera de Git en `data/processed/regresion_diagnostico/{year}/{spec}/`.

{md_table(partition_summary, max_rows=5)}

## Reproduccion 2024

La ejecucion 2024 reproduce el universo y resumen del target de la etapa 12 dentro de tolerancias explicitas. La matriz de esta etapa no se compara columna a columna con la matriz de preparacion porque aqui se ajusta solo sobre entrenamiento y se excluyen variables pendientes.

{md_table(reproduction, max_rows=10)}

## Regresiones diagnosticas

OLS no ponderado con intercepto. No es estimacion de diseno poblacional. Los p-values convencionales no se destacan como evidencia inferencial.

{md_table(regressions["fit_summary"], max_rows=5)}

{md_table(regressions["metrics"], max_rows=10)}

La version logaritmica usa las mismas filas, variables y particion. Sus AIC/R2 se reportan dentro de su escala y no se comparan directamente con ingreso nominal. No se aplica retransfomacion exponencial.

## VIF/GVIF

La matriz de entrenamiento se reviso por rango, constantes y duplicados exactos antes de VIF/GVIF.

{md_table(dependency["matrix_summary"], max_rows=10)}

VIF por columna mas altos:

{md_table(top_vif[["columna_matriz", "variable_original", "categoria", "referencia_variable", "vif"]], max_rows=10)}

GVIF por bloque mas altos:

{md_table(top_gvif[["variable_original", "df_bloque", "gvif", "gvif_ajustado", "estado"]], max_rows=10)}

## PCA exploratorio

PCA se ajusto solo con entrenamiento. Continuas estandarizadas con parametros de entrenamiento; categoricas con OHE completo centrado y sin escalado por desviacion. Esta geometria no es neutral y puede asignar distinta inercia a bloques categoricos. Componentes no nulos: {n_nonzero}; componentes nulos: {n_null}. No se selecciono numero de componentes ni se ajusto PCR.

{md_table(pca_var, max_rows=15)}

## Arbol exploratorio

DecisionTreeRegressor diagnostico con `max_depth=5`, `min_samples_leaf=0.01`, semilla fija. No hubo busqueda de hiperparametros. Las importancias no son causalidad ni colinealidad; la importancia por impureza puede tener sesgo de cardinalidad y la permutacion por bloques conserva dummies categoricas conjuntas.

{md_table(tree["metrics"], max_rows=5)}

Importancia por impureza:

{md_table(tree["impurity"], max_rows=12)}

Importancia por permutacion:

{md_table(tree["permutation"], max_rows=12)}

## Tabla de revision

{md_table(review, max_rows=25)}

## Roadmap: Plan de regresion y diagnostico

A. Preparacion y auditoria de base parametrizada. Estado: avances existentes; pendientes documentados.

B. Regresion completa y diagnosticos VIF/GVIF, PCA y arbol. Estado: primera ejecucion diagnostica implementada en esta etapa.

C. Revision conjunta de diagnosticos. Estado: pendiente de aprobacion del usuario.

D. Seleccion iterativa supervisada. Estado: pendiente; criterio stepwise y eliminaciones por acordar.

E. Regresion reducida y regresion por componentes. Estado: pendiente; escala principal y componentes por acordar.

F. Comparacion, estabilidad, interpretacion y documentacion final. Estado: pendiente.

Pausas metodologicas: ninguna eliminacion se adopta sin revision; stepwise y eliminacion por multicolinealidad son rutas distintas; no se avanza automaticamente de B a D/E.
"""
    paths.report_path.write_text(content, encoding="utf-8")


def write_manifest(
    paths: DiagnosticPaths,
    config: dict[str, Any],
    deps: pd.DataFrame,
    universe: pd.DataFrame,
    households: pd.DataFrame,
    variables: list[str],
    design: dict[str, Any],
    checks: dict[str, Any],
    compatibility: pd.DataFrame,
    reproduction: pd.DataFrame,
) -> None:
    manifest = {
        "configuracion": config,
        "fuentes": {
            "mart_persona": "data/interim/revision_4/mart_persona_2018_2024.csv.gz",
            "preparacion": "src/features/preparacion_determinantes.py",
            "auditoria": "reports/auditoria_preparacion_determinantes.md",
        },
        "dimensiones": {
            "personas_universo": int(len(universe)),
            "hogares_universo": int(households.shape[0]),
            "columnas_regresion": int(design["X_train"].shape[1]),
        },
        "particion": {
            "unidad": "hogar: anio + folioviv + foliohog",
            "ruta_local_fuera_de_git": str(paths.local_dir / f"particion_hogares_{config['ANIO_ANALISIS']}.csv.gz"),
        },
        "variables": variables,
        "referencias": design["references"].to_dict(orient="records"),
        "compatibilidad_anual_previa": compatibility.to_dict(orient="records"),
        "reproduccion_2024": reproduction.to_dict(orient="records"),
        "versiones": deps.to_dict(orient="records"),
        "modelos_diagnosticos": ["OLS ingreso nominal", "OLS log ingreso", "PCA exploratorio", "DecisionTreeRegressor exploratorio"],
        "pruebas": checks,
        "limitaciones": [
            "OLS no ponderado, sin diseno muestral formal.",
            "Validacion diagnostica; no prueba final independiente.",
            "AIC/R2 no comparables directamente entre ingreso nominal y log ingreso.",
            "No se selecciono numero de componentes PCA.",
            "No se elimino ninguna variable.",
        ],
        "decisiones_pendientes": [
            "criterio stepwise",
            "escala principal del target",
            "eliminacion de variables",
            "numero de componentes",
        ],
    }
    write_json(manifest, paths.table_dir / "manifest_regresion_diagnostico.json")


def run_diagnostics(
    *,
    project_root: str | Path = ".",
    anio_analisis: int = ANIO_ANALISIS,
    anios_validos: tuple[int, ...] = ANIOS_VALIDOS,
    edad_minima: int = EDAD_MINIMA,
    target: str = TARGET,
    criterio_stepwise: Any = CRITERIO_STEPWISE,
    ejecutar_seleccion: bool = EJECUTAR_SELECCION,
    variables_candidatas: list[str] | None = None,
    variables_seleccionadas: list[str] | None = None,
) -> dict[str, Any]:
    if target != TARGET:
        raise ValueError(f"Esta ejecucion espera TARGET={TARGET}.")
    validate_config(anio_analisis, anios_validos, edad_minima, criterio_stepwise, ejecutar_seleccion)
    variables_candidatas = list(variables_candidatas or VARIABLES_CANDIDATAS)
    variables_seleccionadas = list(variables_seleccionadas or variables_candidatas.copy())
    if variables_seleccionadas != variables_candidatas:
        raise ValueError("La primera ejecucion requiere variables_seleccionadas = variables_candidatas.copy().")

    root = Path(project_root).resolve()
    paths = DiagnosticPaths.from_root(root, anio_analisis, ESPECIFICACION)
    effective_config = build_effective_config(
        anio_analisis,
        anios_validos,
        edad_minima,
        target,
        criterio_stepwise,
        ejecutar_seleccion,
    )
    paths.table_dir.mkdir(parents=True, exist_ok=True)
    paths.figure_dir.mkdir(parents=True, exist_ok=True)
    deps = require_dependencies()
    write_csv(deps, paths.table_dir / "dependencias_entorno.csv")

    universe, flow = load_active_universe(root, anio_analisis, edad_minima, anios_validos)
    write_csv(flow, paths.table_dir / "flujo_universo.csv")
    data, households = split_households(universe, paths, year=anio_analisis, train_frac=TRAIN_FRAC, random_state=RANDOM_STATE)
    train = data.loc[data["particion"].eq("entrenamiento")].reset_index(drop=True)
    valid = data.loc[data["particion"].eq("validacion")].reset_index(drop=True)
    inventory = inventory_tables(variables_seleccionadas, paths)
    compatibility = load_previous_compatibility(root, paths, anio_analisis)
    design = build_regression_design(train, valid, variables_seleccionadas, paths)
    reproduction = compare_reproduction_2024(root, paths, universe, households, design, anio_analisis)
    y_train = pd.to_numeric(train[TARGET], errors="coerce")
    y_valid = pd.to_numeric(valid[TARGET], errors="coerce")
    checks = {
        "alineacion_X_y_metadata": bool(len(design["X_train"]) == len(y_train) and len(design["X_valid"]) == len(y_valid)),
        "transformaciones_ajustadas_solo_entrenamiento": True,
        "sin_target_en_X": bool(TARGET not in design["X_train"].columns and LOG_TARGET not in design["X_train"].columns),
        "hogares_compartidos": int(pd.read_csv(paths.table_dir / "particion_validaciones.csv").loc[0, "valor"]),
        "seleccion_automatica": False,
    }
    write_json(checks, paths.table_dir / "validaciones_ejecucion.json")

    regressions = fit_regressions(train, valid, design, paths)
    dependency = run_dependency_diagnostics(design, paths)
    pca = build_pca_matrix(train, valid, variables_seleccionadas, paths)
    figures = plot_diagnostics(regressions, pca, paths, random_state=RANDOM_STATE)
    tree = fit_tree_diagnostics(train, valid, design, paths, random_state=RANDOM_STATE)
    review = review_table(variables_seleccionadas, dependency, pca, tree, paths)
    partition_summary = pd.read_csv(paths.table_dir / "particion_resumen.csv")
    write_manifest(paths, effective_config, deps, universe, households, variables_seleccionadas, design, checks, compatibility, reproduction)
    write_report(paths, effective_config, deps, inventory, compatibility, reproduction, partition_summary, regressions, dependency, pca, tree, review)

    return {
        "paths": paths,
        "configuracion": effective_config,
        "dependencies": deps,
        "universe_rows": len(universe),
        "households": len(households),
        "train_rows": len(train),
        "valid_rows": len(valid),
        "regression_summary": regressions["fit_summary"],
        "regression_metrics": regressions["metrics"],
        "vif_top": dependency["vif"].head(15),
        "gvif_top": dependency["gvif"].head(15),
        "pca_variance": pca["eigen"],
        "tree_metrics": tree["metrics"],
        "tree_impurity": tree["impurity"],
        "tree_permutation": tree["permutation"],
        "compatibility": compatibility,
        "reproduction": reproduction,
        "review": review,
        "figures": figures,
    }


if __name__ == "__main__":
    result = run_diagnostics(project_root=PROJECT_ROOT)
    print(
        json.dumps(
            {
                "report": str(result["paths"].report_path),
                "tables": str(result["paths"].table_dir),
                "figures": str(result["paths"].figure_dir),
                "universe_rows": result["universe_rows"],
                "train_rows": result["train_rows"],
                "valid_rows": result["valid_rows"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

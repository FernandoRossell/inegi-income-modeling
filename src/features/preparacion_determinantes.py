"""Preparacion de base analitica para determinantes ENIGH 2024.

Esta etapa prepara datos y diagnosticos. No entrena modelos, no crea
particiones y no reactiva las etapas historicas de deflactores o JKn.
"""

from __future__ import annotations

import importlib.util
import json
import math
import platform
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TARGET = "ingreso_persona_laboral_negocio_tri"
LOG_TARGET = "log_ingreso_persona_laboral_negocio_tri"
KEY_COLS = ["anio", "folioviv", "foliohog", "numren"]
HOUSEHOLD_KEY_COLS = ["anio", "folioviv", "foliohog"]

METADATA_COLS = [
    "anio",
    "folioviv",
    "foliohog",
    "numren",
    "factor",
    "factor_hogar",
    "est_dis",
    "upm",
    "cve_ent",
    "entidad",
    "cve_mun",
    "municipio",
]

DIAGNOSTIC_COLS = [
    "est_socio",
    "est_socio_desc",
    "tiene_trabajo_reportado",
    "pago_principal_desc",
    "tam_emp_principal_desc",
    "ocupados",
    "percep_ing",
    "perc_ocupa",
]

CONTINUOUS_PREDICTORS = [
    "edad",
    "n_trabajos",
    "horas_trabajos_total",
    "tot_integ",
    "menores",
    "p65mas",
]

CATEGORICAL_PREDICTORS = [
    "sexo_desc",
    "nivelaprob_desc",
    "region_banxico",
    "tam_loc_desc",
    "parentesco_desc",
    "hablaind_desc",
    "segsoc_desc",
    "subor_principal_desc",
    "contrato_principal_desc",
    "sexo_jefe_desc",
    "educa_jefe_desc",
]

PREDICTORS = CONTINUOUS_PREDICTORS + CATEGORICAL_PREDICTORS

REFERENCE_RULES: dict[str, dict[str, str]] = {
    "sexo_desc": {"exact": "Hombre"},
    "nivelaprob_desc": {"exact": "Ninguno"},
    "region_banxico": {"exact": "Centro"},
    "tam_loc_desc": {"prefix": "Localidades con 100 000"},
    "parentesco_desc": {"exact": "Jefe(a)"},
    "hablaind_desc": {"exact": "No"},
    "segsoc_desc": {"exact": "No"},
    "subor_principal_desc": {"exact": "No"},
    "contrato_principal_desc": {"exact": "No"},
    "sexo_jefe_desc": {"exact": "Hombre"},
    "educa_jefe_desc": {"prefix": "Sin instrucci"},
}

STRUCTURAL_MISSING_LABELS = {
    "subor_principal_desc": "No aplica: sin trabajo principal reportado",
    "contrato_principal_desc": "No aplica: sin contrato principal documentado",
    "tam_emp_principal_desc": "No aplica: sin trabajo principal reportado",
}

MONEY_PATTERNS = [
    "ingreso_",
    "ing_cor_",
    "ingtrab_",
    "_hogar_tri",
    "_pc_",
    "sueldos",
    "negocio",
    "rentas",
    "transfer",
    "gasto_mon",
]


@dataclass(frozen=True)
class PreparationConfig:
    project_root: Path
    input_path: Path
    processed_dir: Path
    table_dir: Path
    figure_dir: Path
    year: int = 2024
    min_age: int = 18
    target: str = TARGET

    @classmethod
    def from_root(cls, project_root: Path | str = ".") -> "PreparationConfig":
        root = Path(project_root).resolve()
        return cls(
            project_root=root,
            input_path=root / "data" / "interim" / "revision_4" / "mart_persona_2018_2024.csv.gz",
            processed_dir=root / "data" / "processed" / "determinantes_2024",
            table_dir=root / "reports" / "tables" / "preparacion_determinantes",
            figure_dir=root / "reports" / "figures" / "preparacion_determinantes",
        )


def dependency_versions() -> dict[str, Any]:
    def spec(name: str) -> str:
        return "instalado" if importlib.util.find_spec(name) else "no instalado"

    versions = {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": spec("scipy"),
        "matplotlib": spec("matplotlib"),
        "seaborn": spec("seaborn"),
        "sklearn": spec("sklearn"),
        "statsmodels": spec("statsmodels"),
        "nbformat": spec("nbformat"),
        "nbclient": spec("nbclient"),
        "pyarrow": spec("pyarrow"),
    }
    return versions


def require_runtime_dependencies() -> None:
    missing = [
        name
        for name in ["scipy", "matplotlib", "seaborn", "sklearn"]
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        raise RuntimeError(
            "Faltan dependencias requeridas para esta etapa: "
            + ", ".join(missing)
            + ". Usar un entorno reproducible del proyecto; no se aplican aproximaciones caseras."
        )


def read_source(config: PreparationConfig) -> pd.DataFrame:
    if not config.input_path.exists():
        raise FileNotFoundError(f"No existe la entrada nominal aprobada: {config.input_path}")
    return pd.read_csv(config.input_path, low_memory=False)


def build_universe(df: pd.DataFrame, config: PreparationConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    age = pd.to_numeric(df["edad"], errors="coerce")
    target = pd.to_numeric(df[config.target], errors="coerce")

    steps = []
    current = pd.Series(True, index=df.index)

    def add_step(step: str, mask: pd.Series, reason: str) -> None:
        nonlocal current
        before = int(current.sum())
        excluded_mask = current & ~mask
        current = current & mask
        after = int(current.sum())
        households = int(df.loc[current, HOUSEHOLD_KEY_COLS].drop_duplicates().shape[0])
        steps.append(
            {
                "paso": step,
                "criterio": reason,
                "filas_antes": before,
                "excluidas": int(excluded_mask.sum()),
                "filas_despues": after,
                "hogares_unicos_despues": households,
            }
        )

    add_step("anio_2024", df["anio"].eq(config.year), f"anio == {config.year}")
    add_step("edad_valida", age.notna() & np.isfinite(age), "edad valida y finita")
    add_step("adultos", age.ge(config.min_age), f"edad >= {config.min_age}")
    add_step("target_valido", target.notna() & np.isfinite(target), "target valido y finito")
    add_step("target_positivo", target.gt(0), "target > 0")

    universe = df.loc[current].copy()
    universe[config.target] = pd.to_numeric(universe[config.target], errors="coerce")
    universe[LOG_TARGET] = np.log(universe[config.target])
    flow = pd.DataFrame(steps)
    return universe, flow


def _conceptual_type(series: pd.Series, col: str) -> str:
    if col in KEY_COLS or col in METADATA_COLS:
        return "metadata"
    if col == TARGET:
        return "target"
    if col in CONTINUOUS_PREDICTORS:
        return "continua"
    if col in CATEGORICAL_PREDICTORS:
        return "categorica"
    if col.endswith("_desc"):
        return "categorica_descriptiva"
    if pd.api.types.is_numeric_dtype(series):
        unique = series.nunique(dropna=True)
        if unique <= 20:
            return "codificada_o_conteo"
        return "numerica"
    return "texto_o_categoria"


def _is_money_or_leakage(col: str) -> bool:
    if col == TARGET:
        return False
    lower = col.lower()
    return any(pattern in lower for pattern in MONEY_PATTERNS)


def variable_role(col: str) -> tuple[str, str, str]:
    if col == TARGET:
        return "target", "Ingreso que se pretende explicar.", "target_activo"
    if col in CONTINUOUS_PREDICTORS:
        return "predictor candidato", "Incluida en el conjunto inicial parsimonioso.", "continua_sin_escalar"
    if col in CATEGORICAL_PREDICTORS:
        return "predictor candidato", "Incluida en el conjunto inicial parsimonioso.", "one_hot_k_menos_1"
    if col in KEY_COLS:
        return "metadata", "Llave de persona; se excluye de X.", "conservar_metadata"
    if col in METADATA_COLS:
        return "metadata", "Identificador, geografia detallada, ponderador o diseno; se excluye de X.", "conservar_metadata"
    if col == "tam_emp_principal_desc":
        return (
            "pendiente",
            "Variable laboral util, pero se excluye de X inicial porque su categoria estructural sin trabajo principal duplica exactamente otra dummy.",
            "conservar_diagnostico",
        )
    if col in DIAGNOSTIC_COLS:
        if col in ["est_socio", "est_socio_desc"]:
            return "diagnostico", "Contexto socioeconomico de INEGI; fuera de la matriz inicial hasta justificar su construccion.", "conservar_diagnostico"
        if col in ["ocupados", "percep_ing", "perc_ocupa", "tiene_trabajo_reportado"]:
            return "diagnostico", "Relacionado mecanicamente con el universo laboral; no entra a X inicial.", "conservar_diagnostico"
        return "diagnostico", "Auxiliar para interpretar rutas de variables laborales; no entra a X inicial.", "conservar_diagnostico"
    if col.endswith("_real_2024") or col == "deflactor_2024":
        return "excluida", "Etapa 10 deprecada; no usar variables reales ni deflactor.", "excluir"
    if _is_money_or_leakage(col):
        return "excluida", "Variable monetaria, componente de ingreso o derivado potencial del target; evita filtracion.", "excluir"
    if col in ["sexo", "nivelaprob", "region_banxico_codigo"]:
        return "excluida", "Se usa una representacion descriptiva equivalente cuando aplica.", "excluir"
    if col in [
        "parentesco",
        "hablaind",
        "segsoc",
        "subor_principal",
        "contrato_principal",
        "tam_emp_principal",
        "sexo_jefe",
        "educa_jefe",
        "tam_loc",
    ]:
        return "excluida", "Se usa la columna descriptiva correspondiente para interpretabilidad.", "excluir"
    if col in ["nivel_desc", "nivel", "grado", "gradoaprob"]:
        return "pendiente", "No usar como escolaridad alcanzada sin resolver universo/definicion; nivel_desc mide nivel cursado actual.", "excluir"
    if col in ["edo_conyug", "edo_conyug_desc", "etnia", "etnia_desc", "residencia", "residencia_desc"]:
        return "pendiente", "Variable potencialmente util, pero queda fuera del set inicial hasta revisar etiquetas/interpretacion.", "excluir"
    if col in [
        "indep_principal",
        "indep_principal_desc",
        "pago_principal",
        "tiene_suel_principal",
        "tiene_suel_principal_desc",
        "id_trabajo_principal",
        "num_trabaj",
        "num_trabaj_desc",
        "trabajo_mp",
        "motivo_aus",
        "motivo_aus_desc",
        "act_pnea1",
        "act_pnea1_desc",
        "act_pnea2",
        "act_pnea2_desc",
        "horas_trabajo_principal",
    ]:
        return "pendiente", "Insumo laboral con ruta o redundancia pendiente; no se incorpora en la matriz inicial.", "excluir"
    if col in ["hombres", "mujeres", "mayores", "p12_64"]:
        return "excluida", "Conteo del hogar redundante con composicion seleccionada o totales.", "excluir"
    return "excluida", "Fuera del conjunto inicial parsimonioso; posible extension futura si se justifica.", "excluir"


def build_variable_dictionary(df: pd.DataFrame, universe: pd.DataFrame, config: PreparationConfig) -> pd.DataFrame:
    mart_dict_path = config.project_root / "data" / "interim" / "revision_4" / "diccionario_marts.csv"
    mart_roles = {}
    if mart_dict_path.exists():
        mart_dict = pd.read_csv(mart_dict_path)
        mart_roles = dict(
            zip(
                mart_dict.loc[mart_dict["mart"].eq("mart_persona"), "variable"],
                mart_dict.loc[mart_dict["mart"].eq("mart_persona"), "rol"],
            )
        )

    rows = []
    n = len(universe)
    for col in df.columns:
        s = universe[col] if col in universe.columns else pd.Series(dtype="object")
        role, reason, transform = variable_role(col)
        conceptual = _conceptual_type(s, col)
        missing = int(s.isna().sum()) if len(s) else 0
        nunique = int(s.nunique(dropna=True)) if len(s) else 0
        universe_note = "adultos 2024 con ingreso laboral/de negocio positivo"
        if col in ["nivel_desc", "nivel"]:
            universe_note = "solo aplica a asistencia escolar; no es escolaridad general"
        elif col in ["contrato_principal", "contrato_principal_desc"]:
            universe_note = "ruta laboral asociada a trabajo principal con pago"
        elif "principal" in col:
            universe_note = "ruta laboral del trabajo principal"
        elif col in METADATA_COLS:
            universe_note = "metadata, ponderacion, diseno o geografia detallada"
        rows.append(
            {
                "nombre": col,
                "definicion_procedencia": mart_roles.get(col, "derivada o conservada en mart_persona revision_4"),
                "tipo_conceptual": conceptual,
                "universo_aplicacion": universe_note,
                "faltantes_universo": missing,
                "faltantes_pct_universo": missing / n if n else math.nan,
                "categorias_o_valores": nunique,
                "papel": role,
                "motivo_inclusion_exclusion": reason,
                "transformacion_prevista": transform,
                "observaciones": _variable_observation(col),
            }
        )
    return pd.DataFrame(rows)


def _variable_observation(col: str) -> str:
    if col == "region_banxico":
        return "No incluir entidad simultaneamente en X inicial porque region se deriva de entidad."
    if col in ["entidad", "cve_ent"]:
        return "Se conserva para diagnostico territorial, no como predictor inicial junto con region."
    if col in ["factor", "factor_hogar", "est_dis", "upm"]:
        return "Metadata separada de predictores; no se elimina del flujo."
    if col == "nivelaprob_desc":
        return "Escolaridad alcanzada seleccionada; no confundir con nivel_desc."
    if col == "nivel_desc":
        return "Describe nivel cursado actual; queda fuera de X inicial."
    if col == TARGET:
        return "Target."
    if col in ["subor_principal_desc", "contrato_principal_desc", "tam_emp_principal_desc"]:
        return "Caracteristica del trabajo principal; puede no referir a todos los ingresos laborales/de negocio."
    return ""


def prepare_categorical_for_matrix(df: pd.DataFrame) -> pd.DataFrame:
    cats = pd.DataFrame(index=df.index)
    for col in CATEGORICAL_PREDICTORS:
        series = df[col].astype("object").copy()
        if col in STRUCTURAL_MISSING_LABELS:
            missing = series.isna()
            if col in ["subor_principal_desc", "tam_emp_principal_desc"]:
                structural = missing & (~df["tiene_trabajo_reportado"].astype(bool))
                unresolved = missing & ~structural
                series.loc[structural] = STRUCTURAL_MISSING_LABELS[col]
                series.loc[unresolved] = "Faltante laboral no clasificado"
            elif col == "contrato_principal_desc":
                no_paid_contract = missing & (
                    (~df["tiene_trabajo_reportado"].astype(bool))
                    | df["pago_principal_desc"].isna()
                    | ~df["pago_principal_desc"].eq("Recibe un pago")
                )
                unresolved = missing & ~no_paid_contract
                series.loc[no_paid_contract] = STRUCTURAL_MISSING_LABELS[col]
                series.loc[unresolved] = "Faltante laboral no clasificado"
        cats[col] = series.fillna("Faltante no clasificado").astype(str)
    return cats


def select_reference(col: str, categories: list[str]) -> str:
    rule = REFERENCE_RULES[col]
    if "exact" in rule and rule["exact"] in categories:
        return rule["exact"]
    if "prefix" in rule:
        for category in categories:
            if category.startswith(rule["prefix"]):
                return category
    raise ValueError(f"No se encontro referencia para {col}. Categorias: {categories}")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return normalized or "categoria"


def build_matrix(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    X = pd.DataFrame(index=universe.index)
    for col in CONTINUOUS_PREDICTORS:
        values = pd.to_numeric(universe[col], errors="coerce")
        if values.isna().any() or ~np.isfinite(values).all():
            raise ValueError(f"La continua {col} tiene faltantes/no finitos; no se imputa automaticamente.")
        X[col] = values.astype(float)

    cat_prepared = prepare_categorical_for_matrix(universe)
    mapping_rows = []
    reference_rows = []

    used_names: set[str] = set(X.columns)
    for col in CATEGORICAL_PREDICTORS:
        categories = sorted(cat_prepared[col].dropna().unique().tolist())
        reference = select_reference(col, categories)
        reference_rows.append(
            {
                "variable": col,
                "referencia": reference,
                "criterio": "categoria interpretable definida antes de modelar",
                "n_referencia": int(cat_prepared[col].eq(reference).sum()),
            }
        )
        for category in categories:
            is_reference = category == reference
            base_name = f"{col}__{slugify(category)}"
            dummy_name = base_name
            suffix = 2
            while dummy_name in used_names:
                dummy_name = f"{base_name}_{suffix}"
                suffix += 1
            if not is_reference:
                used_names.add(dummy_name)
                X[dummy_name] = cat_prepared[col].eq(category).astype(np.int8)
            mapping_rows.append(
                {
                    "variable_original": col,
                    "categoria": category,
                    "dummy": "" if is_reference else dummy_name,
                    "es_referencia": bool(is_reference),
                    "n": int(cat_prepared[col].eq(category).sum()),
                    "pct": float(cat_prepared[col].eq(category).mean()),
                    "tratamiento_faltante": "estructural/documentado"
                    if category.startswith("No aplica") or category.startswith("Faltante")
                    else "categoria observada",
                }
            )

    mapping = pd.DataFrame(mapping_rows)
    references = pd.DataFrame(reference_rows)
    X.index = pd.RangeIndex(len(X))
    cat_prepared.index = pd.RangeIndex(len(cat_prepared))
    return X, cat_prepared, mapping, references


def standardize_continuous(X: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    X_scaled = X.copy()
    rows = []
    for col in CONTINUOUS_PREDICTORS:
        mean = float(X[col].mean())
        sd = float(X[col].std(ddof=1))
        is_constant = not math.isfinite(sd) or sd == 0.0
        if is_constant:
            X_scaled[col] = 0.0
        else:
            X_scaled[col] = (X[col] - mean) / sd
        rows.append(
            {
                "variable": col,
                "media": mean,
                "sd_muestral_ddof1": sd,
                "constante": bool(is_constant),
                "formula": "z_i = (x_i - media_x) / s_x; s_x con ddof=1",
            }
        )
    return X_scaled, pd.DataFrame(rows)


def weighted_quantile(values: pd.Series, weights: pd.Series, quantiles: list[float]) -> list[float]:
    mask = values.notna() & weights.notna() & np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    x = values.loc[mask].astype(float).to_numpy()
    w = weights.loc[mask].astype(float).to_numpy()
    if len(x) == 0:
        return [math.nan] * len(quantiles)
    order = np.argsort(x)
    x = x[order]
    w = w[order]
    cum = np.cumsum(w)
    cutoff = np.array(quantiles) * cum[-1]
    return np.interp(cutoff, cum, x).tolist()


def target_summaries(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    y = universe[TARGET].astype(float)
    percentiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    desc = y.describe(percentiles=percentiles)
    unweighted = pd.DataFrame(
        [
            {
                "metrica": "no_ponderado",
                "n": int(y.notna().sum()),
                "media": float(y.mean()),
                "mediana": float(y.median()),
                "desv_std": float(y.std(ddof=1)),
                "min": float(y.min()),
                "p01": float(desc["1%"]),
                "p05": float(desc["5%"]),
                "p10": float(desc["10%"]),
                "p25": float(desc["25%"]),
                "p50": float(desc["50%"]),
                "p75": float(desc["75%"]),
                "p90": float(desc["90%"]),
                "p95": float(desc["95%"]),
                "p99": float(desc["99%"]),
                "max": float(y.max()),
            }
        ]
    )
    weights = pd.to_numeric(universe["factor"], errors="coerce")
    qs = weighted_quantile(y, weights, percentiles)
    weighted = pd.DataFrame(
        [
            {
                "metrica": "ponderado_factor_descriptivo",
                "n_muestral": int(y.notna().sum()),
                "suma_factor": float(weights.sum()),
                "media_ponderada": float((y * weights).sum() / weights.sum()),
                "p01": qs[0],
                "p05": qs[1],
                "p10": qs[2],
                "p25": qs[3],
                "mediana_ponderada": qs[4],
                "p75": qs[5],
                "p90": qs[6],
                "p95": qs[7],
                "p99": qs[8],
                "max": float(y.max()),
            }
        ]
    )
    by_rows = []
    for variable in ["region_banxico", "sexo_desc", "nivelaprob_desc"]:
        for category, g in universe.groupby(variable, dropna=False):
            values = g[TARGET].astype(float)
            w = pd.to_numeric(g["factor"], errors="coerce")
            by_rows.append(
                {
                    "variable": variable,
                    "categoria": category,
                    "n": int(len(g)),
                    "media": float(values.mean()),
                    "mediana": float(values.median()),
                    "desv_std": float(values.std(ddof=1)) if len(g) > 1 else 0.0,
                    "media_ponderada_factor": float((values * w).sum() / w.sum()),
                    "mediana_ponderada_factor": weighted_quantile(values, w, [0.5])[0],
                }
            )
    return unweighted, weighted, pd.DataFrame(by_rows)


def category_frequencies(cat_prepared: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = len(cat_prepared)
    for col in CATEGORICAL_PREDICTORS:
        counts = cat_prepared[col].value_counts(dropna=False)
        for order, (category, count) in enumerate(counts.items(), start=1):
            rows.append(
                {
                    "variable": col,
                    "categoria": category,
                    "n": int(count),
                    "pct": float(count / n),
                    "orden_frecuencia": order,
                    "nota": "Se conserva; no se agrupa automaticamente.",
                }
            )
    return pd.DataFrame(rows)


def categorical_target_summary(universe: pd.DataFrame, cat_prepared: pd.DataFrame) -> pd.DataFrame:
    rows = []
    work = cat_prepared.copy()
    work[TARGET] = universe[TARGET].to_numpy()
    for col in CATEGORICAL_PREDICTORS:
        for category, g in work.groupby(col, dropna=False):
            values = g[TARGET].astype(float)
            rows.append(
                {
                    "variable": col,
                    "categoria": category,
                    "n": int(len(g)),
                    "media_target": float(values.mean()),
                    "mediana_target": float(values.median()),
                    "desv_std_target": float(values.std(ddof=1)) if len(g) > 1 else 0.0,
                    "min_target": float(values.min()),
                    "max_target": float(values.max()),
                }
            )
    return pd.DataFrame(rows)


def continuous_associations(universe: pd.DataFrame) -> pd.DataFrame:
    from scipy.stats import spearmanr

    y = universe[TARGET].astype(float)
    rows = []
    for col in CONTINUOUS_PREDICTORS:
        x = pd.to_numeric(universe[col], errors="coerce")
        mask = x.notna() & y.notna() & np.isfinite(x) & np.isfinite(y)
        rho = spearmanr(x.loc[mask], y.loc[mask]).statistic if int(mask.sum()) > 1 else math.nan
        rows.append(
            {
                "variable": col,
                "tipo": "continua",
                "n_valido": int(mask.sum()),
                "spearman_ingreso_original": float(rho),
                "nota": "Correlacion de rangos exploratoria no ponderada; sin p-values.",
            }
        )
    return pd.DataFrame(rows)


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return math.nan
    sx = float(np.std(x, ddof=1))
    sy = float(np.std(y, ddof=1))
    if sx == 0.0 or sy == 0.0:
        return math.nan
    return float(np.corrcoef(x, y)[0, 1])


def binary_associations(X: pd.DataFrame, universe: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    y = universe[TARGET].astype(float).to_numpy()
    log_y = universe[LOG_TARGET].astype(float).to_numpy()
    dummy_cols = [col for col in X.columns if col not in CONTINUOUS_PREDICTORS]
    category_lookup = mapping.loc[~mapping["es_referencia"]].set_index("dummy")
    rows = []
    for col in dummy_cols:
        x = X[col].astype(float).to_numpy()
        mask1 = x == 1
        mask0 = x == 0
        rows.append(
            {
                "dummy": col,
                "variable_original": category_lookup.loc[col, "variable_original"],
                "categoria_vs_resto": category_lookup.loc[col, "categoria"],
                "n_valido": int(len(x)),
                "frecuencia_1": int(mask1.sum()),
                "frecuencia_0": int(mask0.sum()),
                "media_target_1": float(y[mask1].mean()) if mask1.any() else math.nan,
                "media_target_0": float(y[mask0].mean()) if mask0.any() else math.nan,
                "punto_biserial_ingreso_original": _pearson(x, y),
                "punto_biserial_log_target": _pearson(x, log_y),
                "nota": "Pearson entre indicador 0/1 y target; compara categoria contra todas las demas.",
            }
        )
    return pd.DataFrame(rows)


def validate_point_biserial_equivalence() -> pd.DataFrame:
    from scipy.stats import pointbiserialr

    x = np.array([0, 0, 1, 1, 0, 1, 0, 1], dtype=float)
    y = np.array([10, 12, 20, 18, 11, 22, 9, 19], dtype=float)
    scipy_value = float(pointbiserialr(x, y).statistic)
    pearson_value = _pearson(x, y)
    return pd.DataFrame(
        [
            {
                "validacion": "punto_biserial_equivale_a_pearson_binaria",
                "valor_scipy": scipy_value,
                "valor_pearson": pearson_value,
                "diferencia_abs": abs(scipy_value - pearson_value),
                "tolerancia": 1e-12,
                "resultado": "ok" if abs(scipy_value - pearson_value) <= 1e-12 else "revisar",
            }
        ]
    )


def predictor_dependency_diagnostics(X: pd.DataFrame, cat_prepared: pd.DataFrame) -> dict[str, pd.DataFrame]:
    constant_rows = []
    for col in X.columns:
        unique = int(X[col].nunique(dropna=False))
        if unique <= 1:
            constant_rows.append({"columna": col, "valores_unicos": unique})
    constants = pd.DataFrame(constant_rows, columns=["columna", "valores_unicos"])

    duplicate_rows = []
    cols = list(X.columns)
    for i, left in enumerate(cols):
        left_values = X[left].to_numpy()
        for right in cols[i + 1 :]:
            if np.array_equal(left_values, X[right].to_numpy()):
                duplicate_rows.append({"columna_a": left, "columna_b": right})
    duplicates = pd.DataFrame(duplicate_rows, columns=["columna_a", "columna_b"])

    cont_corr = X[CONTINUOUS_PREDICTORS].corr(method="pearson").reset_index().rename(columns={"index": "variable"})
    cont_pairs = []
    for i, a in enumerate(CONTINUOUS_PREDICTORS):
        for b in CONTINUOUS_PREDICTORS[i + 1 :]:
            cont_pairs.append({"variable_a": a, "variable_b": b, "pearson": float(X[a].corr(X[b]))})
    continuous_corr = pd.DataFrame(cont_pairs)

    cramers = categorical_cramers_v(cat_prepared)

    design = np.column_stack([np.ones(len(X)), X.to_numpy(dtype=float)])
    gram = design.T @ design
    rank = int(np.linalg.matrix_rank(gram))
    n_cols_with_intercept = int(design.shape[1])
    rank_summary = pd.DataFrame(
        [
            {
                "filas": int(len(X)),
                "columnas_X": int(X.shape[1]),
                "columnas_con_intercepto": n_cols_with_intercept,
                "rango_con_intercepto": rank,
                "deficiencia_rango": int(n_cols_with_intercept - rank),
                "estado": "rango_completo" if rank == n_cols_with_intercept else "singular_revisar",
            }
        ]
    )

    vif = compute_vif(X, rank == n_cols_with_intercept)
    return {
        "constantes": constants,
        "duplicadas": duplicates,
        "correlaciones_continuas": continuous_corr,
        "asociacion_categoricas_cramers_v": cramers,
        "rango_matriz": rank_summary,
        "vif": vif,
    }


def categorical_cramers_v(cat_prepared: pd.DataFrame) -> pd.DataFrame:
    from scipy.stats import chi2_contingency

    rows = []
    cols = CATEGORICAL_PREDICTORS
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            table = pd.crosstab(cat_prepared[a], cat_prepared[b])
            if table.shape[0] < 2 or table.shape[1] < 2:
                value = math.nan
            else:
                chi2 = chi2_contingency(table, correction=False).statistic
                n = table.to_numpy().sum()
                denom = n * (min(table.shape) - 1)
                value = math.sqrt(chi2 / denom) if denom > 0 else math.nan
            rows.append(
                {
                    "variable_a": a,
                    "variable_b": b,
                    "cramers_v": float(value) if math.isfinite(value) else math.nan,
                    "nota": "Asociacion descriptiva entre categoricas; sin p-values.",
                }
            )
    return pd.DataFrame(rows)


def compute_vif(X: pd.DataFrame, full_rank: bool) -> pd.DataFrame:
    rows = []
    numeric = X.astype(float)
    std = numeric.std(axis=0, ddof=1)
    variable_cols = std[std > 0].index.tolist()
    if not full_rank:
        return pd.DataFrame(
            [
                {
                    "columna": col,
                    "vif": math.nan,
                    "estado": "no_interpretar_por_singularidad",
                    "nota": "El rango con intercepto no es completo; identificar origen antes de interpretar VIF.",
                }
                for col in variable_cols
            ]
        )
    corr = numeric[variable_cols].corr().to_numpy(dtype=float)
    try:
        inv_corr = np.linalg.inv(corr)
    except np.linalg.LinAlgError:
        return pd.DataFrame(
            [
                {
                    "columna": col,
                    "vif": math.nan,
                    "estado": "no_interpretar_por_singularidad_numerica",
                    "nota": "La matriz de correlaciones no pudo invertirse; revisar dependencias antes de interpretar VIF.",
                }
                for col in variable_cols
            ]
        )
    for col, value in zip(variable_cols, np.diag(inv_corr)):
        rows.append(
            {
                "columna": col,
                "vif": float(value),
                "estado": "ok",
                "nota": "VIF_j = 1/(1-R_j^2). En dummies depende de la codificacion k-1.",
            }
        )
    return pd.DataFrame(rows).sort_values("vif", ascending=False).reset_index(drop=True)


def write_figures(universe: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    import matplotlib.pyplot as plt
    import seaborn as sns

    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    y = universe[TARGET].astype(float)
    log_y = universe[LOG_TARGET].astype(float)
    p99 = float(y.quantile(0.99))

    figures = []

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].hist(y, bins=np.linspace(0, p99, 81), color="#33658a", edgecolor="white")
    axes[0].set_xlim(0, p99)
    axes[0].set_title("Ingreso original, vista hasta P99")
    axes[0].set_xlabel("Pesos nominales trimestrales")
    axes[0].set_ylabel("Personas")
    axes[1].hist(log_y, bins=80, color="#f26419", edgecolor="white")
    axes[1].set_title("log(target)")
    axes[1].set_xlabel("Logaritmo natural")
    fig.suptitle("Distribucion del target")
    fig.tight_layout()
    path = output_dir / "target_hist_original_log.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figures.append({"figura": "target_hist_original_log", "archivo": str(path), "nota": "El panel original limita el eje x a P99 solo para lectura visual; no recorta datos."})

    for variable, filename, title in [
        ("region_banxico", "target_log_por_region.png", "log(target) por region Banxico"),
        ("sexo_desc", "target_log_por_sexo.png", "log(target) por sexo"),
        ("nivelaprob_desc", "target_log_por_escolaridad.png", "log(target) por escolaridad alcanzada"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 5))
        order = universe.groupby(variable)[LOG_TARGET].median().sort_values().index.tolist()
        sns.boxplot(data=universe, x=variable, y=LOG_TARGET, order=order, showfliers=False, ax=ax, color="#86bbd8")
        ax.set_title(title)
        ax.set_xlabel(variable)
        ax.set_ylabel("log ingreso laboral/de negocio")
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        path = output_dir / filename
        fig.savefig(path, dpi=160)
        plt.close(fig)
        figures.append({"figura": filename.replace(".png", ""), "archivo": str(path), "nota": "Boxplot descriptivo no ponderado; outliers ocultos solo en la figura para legibilidad."})

    return pd.DataFrame(figures)


def validation_checks(
    source: pd.DataFrame,
    universe: pd.DataFrame,
    X: pd.DataFrame,
    X_scaled: pd.DataFrame,
    y: pd.DataFrame,
    metadata: pd.DataFrame,
    mapping: pd.DataFrame,
    dictionary: pd.DataFrame,
    point_biserial_validation: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    def add(name: str, ok: bool, detail: str) -> None:
        rows.append({"validacion": name, "resultado": "ok" if ok else "revisar", "detalle": detail})

    add(
        "universo_anio_edad_target",
        bool(
            universe["anio"].eq(2024).all()
            and pd.to_numeric(universe["edad"], errors="coerce").ge(18).all()
            and pd.to_numeric(universe[TARGET], errors="coerce").gt(0).all()
        ),
        "Todas las filas finales cumplen anio 2024, edad >=18 y target positivo.",
    )
    duplicates = int(universe.duplicated(KEY_COLS).sum())
    add("llave_persona_unica", duplicates == 0, f"Duplicados {KEY_COLS}: {duplicates}.")
    add(
        "filas_X_y_metadata",
        len(X) == len(y) == len(metadata) == len(universe) and len(X_scaled) == len(X),
        f"Dimensiones: X={X.shape}, X_scaled={X_scaled.shape}, y={y.shape}, metadata={metadata.shape}.",
    )
    forbidden = set(KEY_COLS + METADATA_COLS + [TARGET, LOG_TARGET])
    forbidden |= {col for col in source.columns if col.endswith("_real_2024") or col == "deflactor_2024" or _is_money_or_leakage(col)}
    bad_x = sorted(set(X.columns) & forbidden)
    add("sin_target_derivados_metadata_en_X", len(bad_x) == 0, "Columnas prohibidas en X: " + (", ".join(bad_x) if bad_x else "ninguna"))
    add(
        "ohe_referencias_consistentes",
        bool(mapping.groupby("variable_original")["es_referencia"].sum().eq(1).all()),
        "Cada variable categorica tiene exactamente una referencia documentada.",
    )
    nonfinite = int((~np.isfinite(X.to_numpy(dtype=float))).sum())
    add("X_sin_infinitos", nonfinite == 0, f"Valores no finitos en X: {nonfinite}.")
    numeric_missing = int(X[CONTINUOUS_PREDICTORS].isna().sum().sum())
    add("continuas_sin_imputacion_necesaria", numeric_missing == 0, f"Faltantes en continuas seleccionadas: {numeric_missing}.")
    cat_pending_in_x = dictionary.loc[
        dictionary["papel"].eq("pendiente") & dictionary["nombre"].isin(PREDICTORS), "nombre"
    ].tolist()
    add("pendientes_fuera_de_X", len(cat_pending_in_x) == 0, "Pendientes dentro de predictores: " + (", ".join(cat_pending_in_x) if cat_pending_in_x else "ninguno"))
    pb = point_biserial_validation.iloc[0]
    add(
        "punto_biserial_pearson_toy",
        pb["resultado"] == "ok",
        f"Diferencia absoluta toy: {pb['diferencia_abs']}.",
    )
    return pd.DataFrame(rows)


def save_processed_outputs(
    config: PreparationConfig,
    universe: pd.DataFrame,
    X: pd.DataFrame,
    X_scaled: pd.DataFrame,
    y: pd.DataFrame,
    metadata: pd.DataFrame,
    predictors: pd.DataFrame,
    scaler_params: pd.DataFrame,
    mapping: pd.DataFrame,
    references: pd.DataFrame,
) -> dict[str, str]:
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "base_interpretable": config.processed_dir / "base_interpretable_personas_2024.csv.gz",
        "X_diagnostico_sin_escalar": config.processed_dir / "X_diagnostico_sin_escalar.csv.gz",
        "X_diagnostico_continuas_estandarizadas": config.processed_dir / "X_diagnostico_continuas_estandarizadas.csv.gz",
        "y_target": config.processed_dir / "y_target.csv.gz",
        "metadata": config.processed_dir / "metadata_personas_2024.csv.gz",
        "predictores_iniciales": config.processed_dir / "predictores_iniciales.csv",
        "parametros_estandarizacion": config.processed_dir / "parametros_estandarizacion.csv",
        "mapping_ohe": config.processed_dir / "mapping_ohe.csv",
        "referencias_ohe": config.processed_dir / "referencias_ohe.csv",
    }

    base_cols = KEY_COLS + [TARGET, LOG_TARGET] + PREDICTORS + DIAGNOSTIC_COLS + [
        col for col in METADATA_COLS if col not in KEY_COLS
    ]
    base_cols = list(dict.fromkeys([col for col in base_cols if col in universe.columns]))
    universe[base_cols].to_csv(paths["base_interpretable"], index=False, encoding="utf-8")
    X.to_csv(paths["X_diagnostico_sin_escalar"], index=False, encoding="utf-8")
    X_scaled.to_csv(paths["X_diagnostico_continuas_estandarizadas"], index=False, encoding="utf-8")
    y.to_csv(paths["y_target"], index=False, encoding="utf-8")
    metadata.to_csv(paths["metadata"], index=False, encoding="utf-8")
    predictors.to_csv(paths["predictores_iniciales"], index=False, encoding="utf-8")
    scaler_params.to_csv(paths["parametros_estandarizacion"], index=False, encoding="utf-8")
    mapping.to_csv(paths["mapping_ohe"], index=False, encoding="utf-8")
    references.to_csv(paths["referencias_ohe"], index=False, encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def write_report(
    config: PreparationConfig,
    flow: pd.DataFrame,
    target_unweighted: pd.DataFrame,
    target_weighted: pd.DataFrame,
    predictors: pd.DataFrame,
    missing: pd.DataFrame,
    references: pd.DataFrame,
    continuous_assoc: pd.DataFrame,
    binary_assoc: pd.DataFrame,
    dependencies: dict[str, pd.DataFrame],
    figures: pd.DataFrame,
    manifest: dict[str, Any],
) -> None:
    report_path = config.project_root / "reports" / "preparacion_base_determinantes.md"

    def md_table(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
        use = df[cols].head(max_rows) if max_rows else df[cols]
        integer_like_cols = {
            "n",
            "n_muestral",
            "filas",
            "filas_antes",
            "excluidas",
            "filas_despues",
            "hogares_unicos_despues",
            "columnas_X",
            "columnas_con_intercepto",
            "rango_con_intercepto",
            "deficiencia_rango",
            "n_referencia",
            "n_valido",
            "frecuencia_1",
            "frecuencia_0",
        }
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in use.iterrows():
            cells = []
            for col in cols:
                value = row[col]
                if isinstance(value, (int, np.integer)):
                    cells.append(f"{int(value):,}")
                elif isinstance(value, (float, np.floating)):
                    value_float = float(value)
                    if math.isnan(value_float):
                        cells.append("NA")
                    elif col in integer_like_cols and value_float.is_integer():
                        cells.append(f"{int(value_float):,}")
                    elif abs(value_float) < 1:
                        cells.append(f"{value_float:.4f}")
                    else:
                        cells.append(f"{value_float:,.2f}")
                else:
                    cells.append(str(value))
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    top_cont = continuous_assoc.assign(abs_rho=continuous_assoc["spearman_ingreso_original"].abs()).sort_values(
        "abs_rho", ascending=False
    )
    top_binary = binary_assoc.assign(abs_r=binary_assoc["punto_biserial_ingreso_original"].abs()).sort_values(
        "abs_r", ascending=False
    )
    rank_summary = dependencies["rango_matriz"]
    top_vif = dependencies["vif"].head(12)
    figure_lines = "\n".join(
        f"- `{Path(row['archivo']).relative_to(config.project_root).as_posix()}`: {row['nota']}"
        for _, row in figures.iterrows()
    )

    text = f"""# Preparación de base para determinantes 2024

Esta etapa prepara una base analítica de personas para estudiar asociaciones entre características personales, laborales, del hogar y territoriales e ingreso. No entrena modelos, no crea particiones y no reactiva las etapas históricas de homologación monetaria o JKn.

Método de ejecución registrado: {manifest["validacion"]["metodo_ejecucion"]}.

## Alcance aprobado

- Unidad: persona.
- Año: 2024.
- Universo: edad >= 18 e ingreso laboral/de negocio positivo.
- Cobertura: todas las regiones Banxico.
- Target: `ingreso_persona_laboral_negocio_tri`.
- Montos: nominales trimestrales.
- Fuente: `data/interim/revision_4/mart_persona_2018_2024.csv.gz`.

Los resultados futuros con esta base corresponderán a adultos con ingreso laboral/de negocio positivo. No explican directamente quién obtiene ingreso positivo ni corrigen sesgos de selección.

## Flujo del universo

{md_table(flow, ["paso", "criterio", "filas_antes", "excluidas", "filas_despues", "hogares_unicos_despues"])}

## Target

Resumen no ponderado:

{md_table(target_unweighted, ["n", "media", "mediana", "desv_std", "p01", "p05", "p25", "p50", "p75", "p95", "p99", "max"])}

Contraste descriptivo ponderado con `factor`:

{md_table(target_weighted, ["n_muestral", "suma_factor", "media_ponderada", "mediana_ponderada", "p25", "p75", "p95", "p99"])}

La cola derecha es muy larga: el máximo supera ampliamente P99. Por eso se crea `log_ingreso_persona_laboral_negocio_tri` solo como diagnóstico visual, sin sustituir el target activo.

## Predictores iniciales

{md_table(predictors, ["variable", "tipo", "papel", "transformacion", "referencia_o_tratamiento"], max_rows=30)}

`est_socio` se conserva como diagnóstico contextual y queda fuera de la matriz inicial. `entidad` también se conserva como metadata diagnóstica porque `region_banxico` ya está determinada por entidad. `tam_emp_principal_desc` queda pendiente: su categoría estructural "sin trabajo principal reportado" duplicaba exactamente una dummy de subordinación, por lo que se conserva en la base interpretable pero no entra a `X` inicial.

## Faltantes

{md_table(missing, ["variable", "faltantes", "faltantes_pct", "decision"], max_rows=20)}

No se aplicó complete-case global. Las continuas seleccionadas no tienen faltantes. En variables laborales del trabajo principal, los faltantes se tratan como categorías estructurales solo cuando el origen permite distinguir ausencia de trabajo principal o contrato no documentado.

## One-hot encoding

Se usa k-1 por variable, pensando en un intercepto futuro. Las referencias no se eligieron por conveniencia estadística sino por interpretación:

{md_table(references, ["variable", "referencia", "n_referencia"])}

Los indicadores son 0/1 y el intercepto no se guarda como predictor.

## Asociaciones exploratorias

Continuas, Spearman con ingreso original:

{md_table(top_cont, ["variable", "n_valido", "spearman_ingreso_original"], max_rows=10)}

Dummies, punto biserial con ingreso original:

{md_table(top_binary, ["dummy", "variable_original", "categoria_vs_resto", "frecuencia_1", "punto_biserial_ingreso_original"], max_rows=12)}

Estas correlaciones son exploratorias, no ponderadas, sin p-values y no son criterio automático de descarte. Una dummy compara su categoría contra todas las demás, no únicamente contra la referencia.

## Dependencia entre predictores

{md_table(rank_summary, ["filas", "columnas_X", "columnas_con_intercepto", "rango_con_intercepto", "deficiencia_rango", "estado"])}

VIF más altos:

{md_table(top_vif, ["columna", "vif", "estado"], max_rows=12)}

`VIF_j = 1 / (1 - R_j^2)`. En dummies individuales depende de la codificación k-1 y no equivale a importancia causal ni a un diagnóstico global de la variable categórica original.

## Figuras

{figure_lines}

## Archivos locales

Las bases y matrices se escribieron en `data/processed/determinantes_2024/` y quedan fuera de Git por contener microdatos/identificadores. Las tablas agregadas pequeñas se escribieron en `reports/tables/preparacion_determinantes/`.

Manifest: `reports/tables/preparacion_determinantes/manifest_preparacion_determinantes.json`.

## Limitaciones y pendientes

- La base es nominal trimestral y corresponde solo a 2024.
- No se usa `deflactor_2024`, columnas `_real_2024` ni JKn.
- No se preparó train/test ni validación cruzada.
- Una futura partición debe considerar hogares para evitar compartir información familiar entre conjuntos.
- La estrategia inferencial de los modelos todavía está pendiente.
- No existe identificación causal aprobada; las lecturas son asociativas.
"""
    report_path.write_text(text, encoding="utf-8")


def build_outputs(project_root: Path | str = ".", execution_context: str = "modulo_python_limpio") -> dict[str, Any]:
    config = PreparationConfig.from_root(project_root)
    require_runtime_dependencies()
    config.table_dir.mkdir(parents=True, exist_ok=True)
    config.figure_dir.mkdir(parents=True, exist_ok=True)

    source = read_source(config)
    universe, flow = build_universe(source, config)
    dictionary = build_variable_dictionary(source, universe, config)
    cat_prepared = prepare_categorical_for_matrix(universe)
    X, cat_prepared, mapping, references = build_matrix(universe)
    X_scaled, scaler_params = standardize_continuous(X)
    y = universe[[TARGET, LOG_TARGET]].reset_index(drop=True)
    metadata = universe[METADATA_COLS].reset_index(drop=True)

    predictors = pd.DataFrame(
        [
            {
                "variable": col,
                "tipo": "continua" if col in CONTINUOUS_PREDICTORS else "categorica",
                "papel": "predictor inicial",
                "transformacion": "sin escalar; estandarizada solo en matriz diagnostica"
                if col in CONTINUOUS_PREDICTORS
                else "one-hot k-1",
                "referencia_o_tratamiento": ""
                if col in CONTINUOUS_PREDICTORS
                else references.loc[references["variable"].eq(col), "referencia"].iloc[0],
            }
            for col in PREDICTORS
        ]
    )

    missing_rows = []
    for col in PREDICTORS:
        miss = int(universe[col].isna().sum())
        if col in STRUCTURAL_MISSING_LABELS:
            decision = "faltante estructural convertido solo en categoria de matriz; original se conserva"
        elif miss == 0:
            decision = "usar sin imputacion"
        else:
            decision = "pendiente; excluir si no hay tratamiento defendible"
        missing_rows.append(
            {
                "variable": col,
                "faltantes": miss,
                "faltantes_pct": miss / len(universe),
                "decision": decision,
            }
        )
    missing = pd.DataFrame(missing_rows)

    target_unweighted, target_weighted, target_by_group = target_summaries(universe)
    frequencies = category_frequencies(cat_prepared)
    categorical_summary = categorical_target_summary(universe, cat_prepared)
    continuous_assoc = continuous_associations(universe)
    binary_assoc = binary_associations(X, universe, mapping)
    pb_validation = validate_point_biserial_equivalence()
    dependencies = predictor_dependency_diagnostics(X, cat_prepared)
    figures = write_figures(universe, config.figure_dir)
    processed_paths = save_processed_outputs(
        config, universe, X, X_scaled, y, metadata, predictors, scaler_params, mapping, references
    )

    outputs = {
        "flujo_universo": config.table_dir / "flujo_universo.csv",
        "diccionario_variables": config.table_dir / "diccionario_variables.csv",
        "exclusiones_variables": config.table_dir / "exclusiones_variables.csv",
        "faltantes_predictores": config.table_dir / "faltantes_predictores.csv",
        "categorias_frecuencias": config.table_dir / "categorias_frecuencias.csv",
        "categorias_target_resumen": config.table_dir / "categorias_target_resumen.csv",
        "referencias_ohe": config.table_dir / "referencias_ohe.csv",
        "mapping_ohe": config.table_dir / "mapping_ohe.csv",
        "target_resumen_no_ponderado": config.table_dir / "target_resumen_no_ponderado.csv",
        "target_resumen_ponderado": config.table_dir / "target_resumen_ponderado.csv",
        "target_por_region_sexo_escolaridad": config.table_dir / "target_por_region_sexo_escolaridad.csv",
        "correlaciones_continuas_spearman": config.table_dir / "correlaciones_continuas_spearman.csv",
        "correlaciones_dummies_punto_biserial": config.table_dir / "correlaciones_dummies_punto_biserial.csv",
        "dependencia_constantes": config.table_dir / "dependencia_constantes.csv",
        "dependencia_duplicadas": config.table_dir / "dependencia_duplicadas.csv",
        "dependencia_continuas_pearson": config.table_dir / "dependencia_continuas_pearson.csv",
        "dependencia_categoricas_cramers_v": config.table_dir / "dependencia_categoricas_cramers_v.csv",
        "dependencia_rango_matriz": config.table_dir / "dependencia_rango_matriz.csv",
        "dependencia_vif": config.table_dir / "dependencia_vif.csv",
        "validaciones": config.table_dir / "validaciones_preparacion.csv",
        "figuras": config.table_dir / "figuras_generadas.csv",
        "predictores_iniciales": config.table_dir / "predictores_iniciales.csv",
        "parametros_estandarizacion": config.table_dir / "parametros_estandarizacion.csv",
    }

    dictionary.to_csv(outputs["diccionario_variables"], index=False, encoding="utf-8")
    dictionary.loc[~dictionary["papel"].eq("predictor candidato")].to_csv(
        outputs["exclusiones_variables"], index=False, encoding="utf-8"
    )
    flow.to_csv(outputs["flujo_universo"], index=False, encoding="utf-8")
    missing.to_csv(outputs["faltantes_predictores"], index=False, encoding="utf-8")
    frequencies.to_csv(outputs["categorias_frecuencias"], index=False, encoding="utf-8")
    categorical_summary.to_csv(outputs["categorias_target_resumen"], index=False, encoding="utf-8")
    references.to_csv(outputs["referencias_ohe"], index=False, encoding="utf-8")
    mapping.to_csv(outputs["mapping_ohe"], index=False, encoding="utf-8")
    target_unweighted.to_csv(outputs["target_resumen_no_ponderado"], index=False, encoding="utf-8")
    target_weighted.to_csv(outputs["target_resumen_ponderado"], index=False, encoding="utf-8")
    target_by_group.to_csv(outputs["target_por_region_sexo_escolaridad"], index=False, encoding="utf-8")
    continuous_assoc.to_csv(outputs["correlaciones_continuas_spearman"], index=False, encoding="utf-8")
    binary_assoc.to_csv(outputs["correlaciones_dummies_punto_biserial"], index=False, encoding="utf-8")
    dependencies["constantes"].to_csv(outputs["dependencia_constantes"], index=False, encoding="utf-8")
    dependencies["duplicadas"].to_csv(outputs["dependencia_duplicadas"], index=False, encoding="utf-8")
    dependencies["correlaciones_continuas"].to_csv(outputs["dependencia_continuas_pearson"], index=False, encoding="utf-8")
    dependencies["asociacion_categoricas_cramers_v"].to_csv(outputs["dependencia_categoricas_cramers_v"], index=False, encoding="utf-8")
    dependencies["rango_matriz"].to_csv(outputs["dependencia_rango_matriz"], index=False, encoding="utf-8")
    dependencies["vif"].to_csv(outputs["dependencia_vif"], index=False, encoding="utf-8")
    figures.to_csv(outputs["figuras"], index=False, encoding="utf-8")
    predictors.to_csv(outputs["predictores_iniciales"], index=False, encoding="utf-8")
    scaler_params.to_csv(outputs["parametros_estandarizacion"], index=False, encoding="utf-8")

    validations = validation_checks(source, universe, X, X_scaled, y, metadata, mapping, dictionary, pb_validation)
    validations = pd.concat([validations, pb_validation], ignore_index=True, sort=False)
    validations.to_csv(outputs["validaciones"], index=False, encoding="utf-8")

    manifest = {
        "etapa": 12,
        "nombre": "preparacion_base_determinantes_2024",
        "entrada": str(config.input_path),
        "fecha_ejecucion": pd.Timestamp.now().isoformat(),
        "decisiones": {
            "unidad": "persona",
            "anio": config.year,
            "universo": f"edad >= {config.min_age} e ingreso laboral/de negocio positivo",
            "target": config.target,
            "moneda": "nominal trimestral",
            "etapas_deprecadas_no_usadas": ["homologacion_monetaria_etapa_10", "diseno_muestral_JKn_etapa_11"],
            "sin_modelos": True,
            "sin_particiones": True,
        },
        "dimensiones": {
            "fuente_filas": int(len(source)),
            "universo_filas": int(len(universe)),
            "hogares_unicos": int(universe[HOUSEHOLD_KEY_COLS].drop_duplicates().shape[0]),
            "X_columnas": int(X.shape[1]),
            "continuas": len(CONTINUOUS_PREDICTORS),
            "categoricas": len(CATEGORICAL_PREDICTORS),
        },
        "predictores_continuos": CONTINUOUS_PREDICTORS,
        "predictores_categoricos": CATEGORICAL_PREDICTORS,
        "salidas_versionadas": {key: str(value) for key, value in outputs.items()},
        "salidas_fuera_de_git": processed_paths,
        "dependencias": dependency_versions(),
        "validacion": {
            "estado_global": "ok" if validations["resultado"].fillna("ok").eq("ok").all() else "revisar",
            "notebook_ejecutado": execution_context.startswith("notebook"),
            "metodo_ejecucion": execution_context,
        },
        "pendientes_antes_de_modelar": [
            "Aprobar estrategia inferencial.",
            "Definir particion considerando hogares.",
            "Ajustar encoder/scaler solo sobre entrenamiento en una etapa futura.",
            "Decidir si est_socio debe entrar como predictor o mantenerse como diagnostico.",
            "Decidir si tam_emp_principal_desc se recodifica o permanece fuera por redundancia estructural.",
            "Revisar variables pendientes con etiquetas ambiguas antes de ampliar X.",
        ],
    }
    manifest_path = config.table_dir / "manifest_preparacion_determinantes.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(
        config,
        flow,
        target_unweighted,
        target_weighted,
        predictors,
        missing,
        references,
        continuous_assoc,
        binary_assoc,
        dependencies,
        figures,
        manifest,
    )
    return manifest

"""Herramientas para diseno muestral ENIGH con JKn estratificado.

La implementacion es deliberadamente acotada a estadistica descriptiva
ponderada e inferencia aproximada por jackknife estratificado por UPM.
No intenta reconstruir calibracion, no respuesta ni FPC oficiales.
"""

from __future__ import annotations

import importlib.util
import json
import math
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd


REGIONES_BANXICO = ["Norte", "Centro Norte", "Centro", "Sur"]
DOMINIOS_REPORTE = ["Nacional"] + REGIONES_BANXICO


def dependency_versions() -> dict[str, Any]:
    """Registra versiones y disponibilidad de dependencias relevantes."""

    def available(module: str) -> bool:
        return importlib.util.find_spec(module) is not None

    versions: dict[str, Any] = {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
    }
    for module in ["scipy", "matplotlib", "seaborn", "nbformat", "nbclient", "pypdf"]:
        versions[module] = "instalado" if available(module) else "no instalado"
    versions["Rscript"] = shutil.which("Rscript") or "no disponible"
    return versions


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function."""

    max_iter = 200
    eps = 3e-14
    fpmin = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0

    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """I_x(a, b) sin depender de scipy."""

    if not 0.0 <= x <= 1.0:
        raise ValueError("x debe estar en [0, 1].")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    log_bt = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    bt = math.exp(log_bt)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def student_t_cdf(x: float, df: int | float) -> float:
    """CDF de Student t usando beta incompleta regularizada."""

    if not math.isfinite(df) or df <= 0:
        return math.nan
    if x == 0:
        return 0.5
    z = df / (df + x * x)
    ib = regularized_incomplete_beta(z, df / 2.0, 0.5)
    if x > 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def student_t_critical(df: int | float, p: float = 0.975) -> float:
    """Cuantil t_p,df por biseccion.

    Para grados muy grandes se usa el cuantil normal porque la diferencia es
    numericamente irrelevante para las tablas de esta revision.
    """

    if not math.isfinite(df) or df <= 0:
        return math.nan
    if not 0.0 < p < 1.0:
        raise ValueError("p debe estar en (0, 1).")
    if df > 1_000_000:
        return NormalDist().inv_cdf(p)
    if p == 0.5:
        return 0.0
    if p < 0.5:
        return -student_t_critical(df, 1.0 - p)

    low = 0.0
    high = 1.0
    while student_t_cdf(high, df) < p:
        high *= 2.0
        if high > 1_000_000:
            return high
    for _ in range(80):
        mid = (low + high) / 2.0
        if student_t_cdf(mid, df) < p:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def attach_design_ids(
    df: pd.DataFrame,
    year_col: str = "anio",
    strata_col: str = "est_dis",
    psu_col: str = "upm",
    weight_col: str = "factor",
) -> pd.DataFrame:
    """Valida variables de diseno y crea identificadores compuestos por anio."""

    required = [year_col, strata_col, psu_col, weight_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas de diseno: {missing}")

    out = df.copy()
    out[weight_col] = pd.to_numeric(out[weight_col], errors="coerce")
    out["_anio_diseno"] = pd.to_numeric(out[year_col], errors="coerce").astype("Int64")
    out["_est_dis_raw"] = out[strata_col].astype("string").str.strip()
    out["_upm_raw"] = out[psu_col].astype("string").str.strip()

    complete = (
        out["_anio_diseno"].notna()
        & out["_est_dis_raw"].notna()
        & out["_upm_raw"].notna()
        & out[weight_col].notna()
        & np.isfinite(out[weight_col].astype(float))
        & (out[weight_col].astype(float) > 0)
    )
    if not bool(complete.all()):
        bad = int((~complete).sum())
        raise ValueError(f"Hay {bad} filas con diseno o factor incompleto/no positivo.")

    year_text = out["_anio_diseno"].astype(str)
    out["_estrato_jkn"] = year_text + "|est_dis=" + out["_est_dis_raw"]
    out["_upm_jkn"] = out["_estrato_jkn"] + "|upm=" + out["_upm_raw"]
    return out


def _is_zero_code(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    numeric = pd.to_numeric(text, errors="coerce")
    return text.eq("0") | numeric.eq(0)


def audit_design(
    df: pd.DataFrame,
    unit: str,
    key_cols: list[str],
    year_col: str = "anio",
    strata_col: str = "est_dis",
    psu_col: str = "upm",
    weight_col: str = "factor",
) -> pd.DataFrame:
    """Audita llaves, factor, estratos y UPM por anio y unidad."""

    required = list(dict.fromkeys([year_col, strata_col, psu_col, weight_col] + key_cols))
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas para auditoria {unit}: {missing}")

    rows: list[dict[str, Any]] = []
    work = df[required].copy()
    work[weight_col] = pd.to_numeric(work[weight_col], errors="coerce")
    work[year_col] = pd.to_numeric(work[year_col], errors="coerce")

    for year, g in work.groupby(year_col, dropna=False):
        factor_ok = g[weight_col].notna() & np.isfinite(g[weight_col]) & (g[weight_col] > 0)
        design_ok = g[strata_col].notna() & g[psu_col].notna()
        valid = g[factor_ok & design_ok]

        strata_psu = valid.groupby(strata_col, dropna=False)[psu_col].nunique()
        obs_per_upm = valid.groupby([strata_col, psu_col], dropna=False).size()
        raw_upm_multi_strata = (
            valid.groupby(psu_col, dropna=False)[strata_col].nunique().gt(1).sum()
        )

        duplicate_keys = int(g.duplicated(key_cols).sum())
        problems = []
        if duplicate_keys:
            problems.append(f"{duplicate_keys} llaves duplicadas")
        if int((~factor_ok).sum()):
            problems.append(f"{int((~factor_ok).sum())} factores faltantes/no positivos")
        if int((~design_ok).sum()):
            problems.append(f"{int((~design_ok).sum())} filas sin estrato/UPM")

        rows.append(
            {
                "anio": int(year) if pd.notna(year) else None,
                "unidad": unit,
                "filas": int(len(g)),
                "llaves_duplicadas": duplicate_keys,
                "factor_completo_positivo": bool(factor_ok.all()),
                "filas_factor_no_valido": int((~factor_ok).sum()),
                "est_dis_completo": bool(g[strata_col].notna().all()),
                "upm_completo": bool(g[psu_col].notna().all()),
                "codigo_0_est_dis": int(_is_zero_code(g[strata_col]).sum()),
                "codigo_0_upm": int(_is_zero_code(g[psu_col]).sum()),
                "estratos": int(strata_psu.shape[0]),
                "upm": int(obs_per_upm.shape[0]),
                "estratos_singleton": int(strata_psu.eq(1).sum()),
                "obs_min_por_upm": int(obs_per_upm.min()) if len(obs_per_upm) else 0,
                "obs_mediana_por_upm": float(obs_per_upm.median()) if len(obs_per_upm) else 0.0,
                "obs_max_por_upm": int(obs_per_upm.max()) if len(obs_per_upm) else 0,
                "poblacion_expandida": float(valid[weight_col].sum()),
                "upm_raw_en_multiples_estratos": int(raw_upm_multi_strata),
                "nu_diseno_M_menos_H": int(obs_per_upm.shape[0] - strata_psu.shape[0]),
                "estado": "ok" if not problems else "; ".join(problems),
            }
        )
    return pd.DataFrame(rows).sort_values(["anio", "unidad"]).reset_index(drop=True)


def audit_household_person_consistency(
    hogar: pd.DataFrame,
    persona: pd.DataFrame,
    key_cols: list[str] | None = None,
    design_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Compara diseno/factor del hogar contra los registros de personas."""

    key_cols = key_cols or ["anio", "folioviv", "foliohog"]
    design_cols = design_cols or ["factor", "factor_hogar", "est_dis", "upm"]
    required_h = key_cols + [c for c in design_cols if c in hogar.columns]
    required_p = key_cols + [c for c in design_cols if c in persona.columns]
    h = hogar[required_h].drop_duplicates(key_cols).copy()
    p = persona[required_p].copy()

    rows: list[dict[str, Any]] = []
    for year in sorted(set(h["anio"].dropna().unique()) | set(p["anio"].dropna().unique())):
        h_y = h[h["anio"] == year]
        p_y = p[p["anio"] == year]
        p_unique = p_y.drop_duplicates(key_cols)
        p_nunique = p_y.groupby(key_cols, dropna=False)[[c for c in design_cols if c in p_y.columns]].nunique(
            dropna=False
        )
        inconsistent_persona = int(p_nunique.gt(1).any(axis=1).sum()) if len(p_nunique) else 0

        merged = h_y.merge(
            p_unique,
            on=key_cols,
            how="outer",
            suffixes=("_hogar", "_persona"),
            indicator=True,
        )
        row: dict[str, Any] = {
            "anio": int(year),
            "hogares_mart_hogar": int(len(h_y)),
            "hogares_en_mart_persona": int(len(p_unique)),
            "hogares_comunes": int((merged["_merge"] == "both").sum()),
            "hogares_persona_sin_hogar": int((merged["_merge"] == "right_only").sum()),
            "hogares_hogar_sin_persona": int((merged["_merge"] == "left_only").sum()),
            "hogares_con_diseno_variable_en_persona": inconsistent_persona,
        }
        differences = 0
        for col in design_cols:
            h_col = f"{col}_hogar"
            p_col = f"{col}_persona"
            if h_col not in merged.columns or p_col not in merged.columns:
                continue
            both = merged["_merge"] == "both"
            if col.startswith("factor"):
                left = pd.to_numeric(merged.loc[both, h_col], errors="coerce")
                right = pd.to_numeric(merged.loc[both, p_col], errors="coerce")
                diff = ~(np.isclose(left, right, rtol=0, atol=1e-9) | (left.isna() & right.isna()))
            else:
                left = merged.loc[both, h_col].astype("string")
                right = merged.loc[both, p_col].astype("string")
                diff = ~(left.fillna("<NA>") == right.fillna("<NA>"))
            row[f"hogares_con_diferencia_{col}"] = int(diff.sum())
            differences += int(diff.sum())
        problems = []
        for label in ["hogares_persona_sin_hogar", "hogares_hogar_sin_persona", "hogares_con_diseno_variable_en_persona"]:
            if row[label]:
                problems.append(label)
        if differences:
            problems.append("diferencias_factor_diseno")
        row["estado"] = "ok" if not problems else "; ".join(problems)
        rows.append(row)
    return pd.DataFrame(rows)


def _psu_totals(
    design_df: pd.DataFrame,
    columns: list[str],
    strata_col: str = "_estrato_jkn",
    psu_col: str = "_upm_jkn",
) -> pd.DataFrame:
    grouped = design_df.groupby([strata_col, psu_col], dropna=False)[columns].sum().reset_index()
    return grouped.rename(columns={strata_col: "estrato", psu_col: "upm"})


def _design_support(psu_totals: pd.DataFrame) -> tuple[pd.Series, int, int, int]:
    m_by_stratum = psu_totals.groupby("estrato")["upm"].nunique()
    h_design = int(m_by_stratum.shape[0])
    m_design = int(m_by_stratum.sum())
    singletons = int(m_by_stratum.eq(1).sum())
    return m_by_stratum, h_design, m_design, singletons


def _ratio_from_totals(num: float, den: float) -> float:
    if den <= 0 or not math.isfinite(den):
        return math.nan
    return num / den


def _jkn_ratio_variance(psu_totals: pd.DataFrame, theta_hat: float) -> tuple[float, int, str]:
    m_by_stratum, _, _, singletons = _design_support(psu_totals)
    if singletons:
        return math.nan, 0, f"sin_error_estandar_por_{singletons}_estratos_singleton"

    totals = psu_totals[["num", "den"]].sum()
    stratum_totals = psu_totals.groupby("estrato")[["num", "den"]].sum().rename(
        columns={"num": "num_h", "den": "den_h"}
    )
    reps = psu_totals.merge(stratum_totals, left_on="estrato", right_index=True)
    reps["m_h"] = reps["estrato"].map(m_by_stratum).astype(float)

    factor = reps["m_h"] / (reps["m_h"] - 1.0)
    rep_num = totals["num"] - reps["num_h"] + factor * (reps["num_h"] - reps["num"])
    rep_den = totals["den"] - reps["den_h"] + factor * (reps["den_h"] - reps["den"])
    rep_theta = rep_num / rep_den.replace({0: np.nan})
    bad = int(rep_theta.isna().sum())
    if bad:
        return math.nan, int(len(reps) - bad), f"sin_error_estandar_por_{bad}_replicas_sin_denominador"

    reps["diff2"] = (rep_theta - theta_hat) ** 2
    var_by_stratum = reps.groupby("estrato")["diff2"].sum()
    weights = (m_by_stratum - 1.0) / m_by_stratum
    variance = float((weights * var_by_stratum).sum())
    return variance, int(len(reps)), "ok"


def ratio_jkn(
    df: pd.DataFrame,
    numerator: pd.Series,
    denominator: pd.Series,
    domain_mask: pd.Series,
    metadata: dict[str, Any],
    weight_col: str = "factor",
) -> dict[str, Any]:
    """Estimador de razon/media/proporcion con varianza JKn estratificada."""

    design = attach_design_ids(df, weight_col=weight_col)
    numerator = pd.to_numeric(numerator.reindex(design.index), errors="coerce")
    denominator = pd.to_numeric(denominator.reindex(design.index), errors="coerce")
    domain = domain_mask.reindex(design.index).fillna(False).astype(bool)
    valid = domain & numerator.notna() & denominator.notna()

    work = design[["_estrato_jkn", "_upm_jkn", weight_col]].copy()
    weights = work[weight_col].astype(float)
    work["num"] = np.where(valid, weights * numerator, 0.0)
    work["den"] = np.where(valid, weights * denominator, 0.0)
    work["n_domain"] = valid.astype(int)
    psu_totals = _psu_totals(work, ["num", "den", "n_domain"])

    full_num = float(work["num"].sum())
    full_den = float(work["den"].sum())
    theta_hat = _ratio_from_totals(full_num, full_den)
    direct_theta = _ratio_from_totals(
        float((weights[valid] * numerator[valid]).sum()),
        float((weights[valid] * denominator[valid]).sum()),
    )

    m_by_stratum, h_design, m_design, singletons = _design_support(psu_totals)
    support = psu_totals[psu_totals["den"] > 0]
    m_domain = int(len(support))
    h_domain = int(support["estrato"].nunique())
    nu = int(m_domain - h_domain)
    status = "ok"
    variance = math.nan
    replicas = 0
    if not math.isfinite(theta_hat):
        status = "sin_dominio"
    else:
        variance, replicas, status = _jkn_ratio_variance(psu_totals, theta_hat)
        if status == "ok" and nu <= 0:
            status = "sin_ic_por_grados_libertad_no_positivos"

    se = math.sqrt(variance) if variance >= 0 and math.isfinite(variance) else math.nan
    tcrit = student_t_critical(nu) if status == "ok" and nu > 0 else math.nan
    ci_low = theta_hat - tcrit * se if math.isfinite(tcrit) and math.isfinite(se) else math.nan
    ci_high = theta_hat + tcrit * se if math.isfinite(tcrit) and math.isfinite(se) else math.nan

    return {
        **metadata,
        "n_muestral": int(valid.sum()),
        "poblacion_expandida": full_den,
        "M_D": m_domain,
        "H_D": h_domain,
        "M_diseno": m_design,
        "H_diseno": h_design,
        "estratos_singleton_diseno": singletons,
        "estimacion": theta_hat,
        "estimacion_directa": direct_theta,
        "diferencia_directa": abs(theta_hat - direct_theta)
        if math.isfinite(theta_hat) and math.isfinite(direct_theta)
        else math.nan,
        "var_jkn": variance,
        "se_jkn": se,
        "nu": nu,
        "tcrit_95": tcrit,
        "ic95_inf": ci_low,
        "ic95_sup": ci_high,
        "replicas_usadas": replicas,
        "estado": status,
    }


def _jkn_contrast_variance(psu_totals: pd.DataFrame, delta_hat: float) -> tuple[float, int, str]:
    m_by_stratum, _, _, singletons = _design_support(psu_totals)
    if singletons:
        return math.nan, 0, f"sin_error_estandar_por_{singletons}_estratos_singleton"

    totals = psu_totals[["num_a", "den_a", "num_b", "den_b"]].sum()
    stratum_totals = psu_totals.groupby("estrato")[["num_a", "den_a", "num_b", "den_b"]].sum()
    stratum_totals = stratum_totals.rename(columns={col: f"{col}_h" for col in stratum_totals.columns})
    reps = psu_totals.merge(stratum_totals, left_on="estrato", right_index=True)
    reps["m_h"] = reps["estrato"].map(m_by_stratum).astype(float)
    factor = reps["m_h"] / (reps["m_h"] - 1.0)

    rep_num_a = totals["num_a"] - reps["num_a_h"] + factor * (reps["num_a_h"] - reps["num_a"])
    rep_den_a = totals["den_a"] - reps["den_a_h"] + factor * (reps["den_a_h"] - reps["den_a"])
    rep_num_b = totals["num_b"] - reps["num_b_h"] + factor * (reps["num_b_h"] - reps["num_b"])
    rep_den_b = totals["den_b"] - reps["den_b_h"] + factor * (reps["den_b_h"] - reps["den_b"])

    rep_a = rep_num_a / rep_den_a.replace({0: np.nan})
    rep_b = rep_num_b / rep_den_b.replace({0: np.nan})
    rep_delta = rep_a - rep_b
    bad = int(rep_delta.isna().sum())
    if bad:
        return math.nan, int(len(reps) - bad), f"sin_error_estandar_por_{bad}_replicas_sin_denominador"

    reps["diff2"] = (rep_delta - delta_hat) ** 2
    var_by_stratum = reps.groupby("estrato")["diff2"].sum()
    weights = (m_by_stratum - 1.0) / m_by_stratum
    variance = float((weights * var_by_stratum).sum())
    return variance, int(len(reps)), "ok"


def contrast_difference_jkn(
    df: pd.DataFrame,
    value: pd.Series,
    domain_a: pd.Series,
    domain_b: pd.Series,
    metadata: dict[str, Any],
    weight_col: str = "factor",
) -> dict[str, Any]:
    """Diferencia de dos medias de dominio recalculada dentro de cada replica."""

    design = attach_design_ids(df, weight_col=weight_col)
    value = pd.to_numeric(value.reindex(design.index), errors="coerce")
    a = domain_a.reindex(design.index).fillna(False).astype(bool) & value.notna()
    b = domain_b.reindex(design.index).fillna(False).astype(bool) & value.notna()

    work = design[["_estrato_jkn", "_upm_jkn", weight_col]].copy()
    weights = work[weight_col].astype(float)
    work["num_a"] = np.where(a, weights * value, 0.0)
    work["den_a"] = np.where(a, weights, 0.0)
    work["num_b"] = np.where(b, weights * value, 0.0)
    work["den_b"] = np.where(b, weights, 0.0)
    work["n_domain"] = (a | b).astype(int)
    psu_totals = _psu_totals(work, ["num_a", "den_a", "num_b", "den_b", "n_domain"])

    totals = work[["num_a", "den_a", "num_b", "den_b"]].sum()
    mean_a = _ratio_from_totals(float(totals["num_a"]), float(totals["den_a"]))
    mean_b = _ratio_from_totals(float(totals["num_b"]), float(totals["den_b"]))
    delta = mean_a - mean_b if math.isfinite(mean_a) and math.isfinite(mean_b) else math.nan
    direct_delta = delta

    m_by_stratum, h_design, m_design, singletons = _design_support(psu_totals)
    support = psu_totals[(psu_totals["den_a"] > 0) | (psu_totals["den_b"] > 0)]
    m_domain = int(len(support))
    h_domain = int(support["estrato"].nunique())
    nu = int(m_domain - h_domain)

    status = "ok"
    variance = math.nan
    replicas = 0
    if not math.isfinite(delta):
        status = "sin_dominio"
    else:
        variance, replicas, status = _jkn_contrast_variance(psu_totals, delta)
        if status == "ok" and nu <= 0:
            status = "sin_ic_por_grados_libertad_no_positivos"

    se = math.sqrt(variance) if variance >= 0 and math.isfinite(variance) else math.nan
    tcrit = student_t_critical(nu) if status == "ok" and nu > 0 else math.nan
    ci_low = delta - tcrit * se if math.isfinite(tcrit) and math.isfinite(se) else math.nan
    ci_high = delta + tcrit * se if math.isfinite(tcrit) and math.isfinite(se) else math.nan

    return {
        **metadata,
        "n_muestral": int((a | b).sum()),
        "poblacion_expandida": float(totals["den_a"] + totals["den_b"]),
        "M_D": m_domain,
        "H_D": h_domain,
        "M_diseno": m_design,
        "H_diseno": h_design,
        "estratos_singleton_diseno": singletons,
        "estimacion": delta,
        "estimacion_directa": direct_delta,
        "diferencia_directa": 0.0 if math.isfinite(delta) else math.nan,
        "media_a": mean_a,
        "media_b": mean_b,
        "var_jkn": variance,
        "se_jkn": se,
        "nu": nu,
        "tcrit_95": tcrit,
        "ic95_inf": ci_low,
        "ic95_sup": ci_high,
        "replicas_usadas": replicas,
        "estado": status,
    }


def _toy_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "anio": [2024] * 8,
            "est_dis": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "upm": ["1", "1", "2", "2", "3", "3", "4", "4"],
            "factor": [1.0, 1.2, 0.9, 1.1, 1.5, 1.0, 0.8, 1.3],
            "y": [10.0, 12.0, 18.0, 20.0, 8.0, 11.0, 30.0, 33.0],
            "region": ["Norte", "Norte", "Sur", "Sur", "Norte", "Sur", "Sur", "Norte"],
        }
    )


def _explicit_ratio_variance(df: pd.DataFrame, domain: pd.Series, y: pd.Series) -> float:
    design = attach_design_ids(df)
    y = y.reindex(design.index)
    domain = domain.reindex(design.index)
    theta = float((design.loc[domain, "factor"] * y[domain]).sum() / design.loc[domain, "factor"].sum())
    m_by_stratum = design.groupby("_estrato_jkn")["_upm_jkn"].nunique()
    diffs: list[tuple[str, float]] = []
    for stratum, m_h in m_by_stratum.items():
        for upm in design.loc[design["_estrato_jkn"] == stratum, "_upm_jkn"].unique():
            rep = design.copy()
            in_h = rep["_estrato_jkn"] == stratum
            deleted = rep["_upm_jkn"] == upm
            rep["_w_rep"] = rep["factor"].astype(float)
            rep.loc[deleted, "_w_rep"] = 0.0
            rep.loc[in_h & ~deleted, "_w_rep"] *= m_h / (m_h - 1.0)
            num = float((rep.loc[domain, "_w_rep"] * y[domain]).sum())
            den = float(rep.loc[domain, "_w_rep"].sum())
            diffs.append((stratum, (num / den - theta) ** 2))
    by_stratum: dict[str, float] = {}
    for stratum, diff2 in diffs:
        by_stratum[stratum] = by_stratum.get(stratum, 0.0) + diff2
    return float(sum(((m_by_stratum[h] - 1.0) / m_by_stratum[h]) * v for h, v in by_stratum.items()))


def _explicit_contrast_variance(df: pd.DataFrame) -> float:
    design = attach_design_ids(df)
    y = pd.to_numeric(design["y"], errors="coerce")
    a = design["region"].eq("Norte")
    b = design["region"].eq("Sur")
    mean_a = float((design.loc[a, "factor"] * y[a]).sum() / design.loc[a, "factor"].sum())
    mean_b = float((design.loc[b, "factor"] * y[b]).sum() / design.loc[b, "factor"].sum())
    delta = mean_a - mean_b
    m_by_stratum = design.groupby("_estrato_jkn")["_upm_jkn"].nunique()
    diffs: list[tuple[str, float]] = []
    for stratum, m_h in m_by_stratum.items():
        for upm in design.loc[design["_estrato_jkn"] == stratum, "_upm_jkn"].unique():
            rep = design.copy()
            in_h = rep["_estrato_jkn"] == stratum
            deleted = rep["_upm_jkn"] == upm
            rep["_w_rep"] = rep["factor"].astype(float)
            rep.loc[deleted, "_w_rep"] = 0.0
            rep.loc[in_h & ~deleted, "_w_rep"] *= m_h / (m_h - 1.0)
            rep_a = float((rep.loc[a, "_w_rep"] * y[a]).sum() / rep.loc[a, "_w_rep"].sum())
            rep_b = float((rep.loc[b, "_w_rep"] * y[b]).sum() / rep.loc[b, "_w_rep"].sum())
            diffs.append((stratum, (rep_a - rep_b - delta) ** 2))
    by_stratum: dict[str, float] = {}
    for stratum, diff2 in diffs:
        by_stratum[stratum] = by_stratum.get(stratum, 0.0) + diff2
    return float(sum(((m_by_stratum[h] - 1.0) / m_by_stratum[h]) * v for h, v in by_stratum.items()))


def run_internal_validations(estimates: pd.DataFrame, contrastes: pd.DataFrame) -> pd.DataFrame:
    """Validaciones internas reproducibles de formulas y casos pequenos."""

    rows: list[dict[str, Any]] = []
    all_results = pd.concat([estimates, contrastes], ignore_index=True, sort=False)
    max_direct = float(all_results["diferencia_directa"].abs().max())
    rows.append(
        {
            "validacion": "estimacion_vs_calculo_directo_ponderado",
            "resultado": "ok" if max_direct <= 1e-7 else "revisar",
            "diferencia_maxima": max_direct,
            "tolerancia": 1e-7,
            "detalle": "Las estimaciones puntuales del JKn coinciden con el calculo ponderado directo.",
        }
    )

    toy = _toy_frame()
    domain = pd.Series(True, index=toy.index)
    agg = ratio_jkn(
        toy,
        toy["y"],
        pd.Series(1.0, index=toy.index),
        domain,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "toy",
            "estimando": "media",
            "universo": "toy",
            "variable": "y",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    explicit_var = _explicit_ratio_variance(toy, domain, toy["y"])
    diff_var = abs(float(agg["var_jkn"]) - explicit_var)
    rows.append(
        {
            "validacion": "jkn_agregado_vs_replicas_explicitas_media_toy",
            "resultado": "ok" if diff_var <= 1e-10 else "revisar",
            "diferencia_maxima": diff_var,
            "tolerancia": 1e-10,
            "detalle": "La agregacion por estrato-UPM reproduce las replicas explicitas.",
        }
    )

    domain_norte = toy["region"].eq("Norte")
    agg_domain = ratio_jkn(
        toy,
        toy["y"],
        pd.Series(1.0, index=toy.index),
        domain_norte,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "Norte",
            "estimando": "media_dominio",
            "universo": "toy",
            "variable": "y",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    explicit_domain_var = _explicit_ratio_variance(toy, domain_norte, toy["y"])
    diff_domain = abs(float(agg_domain["var_jkn"]) - explicit_domain_var)
    rows.append(
        {
            "validacion": "jkn_dominio_con_upm_cero_vs_replicas_explicitas_toy",
            "resultado": "ok" if diff_domain <= 1e-10 else "revisar",
            "diferencia_maxima": diff_domain,
            "tolerancia": 1e-10,
            "detalle": "El dominio preserva UPMs fuera del dominio con contribucion cero.",
        }
    )

    con = contrast_difference_jkn(
        toy,
        toy["y"],
        toy["region"].eq("Norte"),
        toy["region"].eq("Sur"),
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "Norte-Sur",
            "estimando": "contraste",
            "universo": "toy",
            "variable": "y",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    explicit_contrast_var = _explicit_contrast_variance(toy)
    diff_contrast = abs(float(con["var_jkn"]) - explicit_contrast_var)
    rows.append(
        {
            "validacion": "jkn_agregado_vs_replicas_explicitas_contraste_toy",
            "resultado": "ok" if diff_contrast <= 1e-10 else "revisar",
            "diferencia_maxima": diff_contrast,
            "tolerancia": 1e-10,
            "detalle": "El contraste recalcula ambas medias dentro de cada replica.",
        }
    )

    scaled = toy.copy()
    scaled["factor"] = scaled["factor"] * 7.0
    scaled_agg = ratio_jkn(
        scaled,
        scaled["y"],
        pd.Series(1.0, index=scaled.index),
        domain,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "toy",
            "estimando": "media",
            "universo": "toy",
            "variable": "y",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    scale_diff = max(
        abs(float(agg["estimacion"]) - float(scaled_agg["estimacion"])),
        abs(float(agg["se_jkn"]) - float(scaled_agg["se_jkn"])),
    )
    total_scale = abs(float(scaled_agg["poblacion_expandida"]) / float(agg["poblacion_expandida"]) - 7.0)
    rows.append(
        {
            "validacion": "invariancia_medias_se_al_escalar_pesos",
            "resultado": "ok" if scale_diff <= 1e-10 and total_scale <= 1e-12 else "revisar",
            "diferencia_maxima": max(scale_diff, total_scale),
            "tolerancia": 1e-10,
            "detalle": "Media y SE no cambian; el total expandido escala por la constante.",
        }
    )

    prop = toy["y"].gt(15).astype(float)
    prop_agg = ratio_jkn(
        toy,
        prop,
        pd.Series(1.0, index=toy.index),
        domain,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "toy",
            "estimando": "proporcion",
            "universo": "toy",
            "variable": "I(y > 15)",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    prop_scaled = ratio_jkn(
        scaled,
        prop,
        pd.Series(1.0, index=scaled.index),
        domain,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "toy",
            "estimando": "proporcion",
            "universo": "toy",
            "variable": "I(y > 15)",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    prop_diff = max(
        abs(float(prop_agg["estimacion"]) - float(prop_scaled["estimacion"])),
        abs(float(prop_agg["se_jkn"]) - float(prop_scaled["se_jkn"])),
    )
    rows.append(
        {
            "validacion": "invariancia_proporciones_se_al_escalar_pesos",
            "resultado": "ok" if prop_diff <= 1e-10 else "revisar",
            "diferencia_maxima": prop_diff,
            "tolerancia": 1e-10,
            "detalle": "Proporcion y SE no cambian al multiplicar todos los pesos por una constante.",
        }
    )

    const = toy.copy()
    const["y"] = 5.0
    const_agg = ratio_jkn(
        const,
        const["y"],
        pd.Series(1.0, index=const.index),
        domain,
        {
            "anio": 2024,
            "unidad": "toy",
            "dominio": "toy",
            "estimando": "media_constante",
            "universo": "toy",
            "variable": "y",
            "ponderador": "factor",
            "unidad_monetaria": "toy",
        },
    )
    const_se = float(const_agg["se_jkn"])
    rows.append(
        {
            "validacion": "respuesta_constante_varianza_cero",
            "resultado": "ok" if const_se <= 1e-12 else "revisar",
            "diferencia_maxima": const_se,
            "tolerancia": 1e-12,
            "detalle": "Una respuesta constante en dominio con denominador positivo produce SE cero.",
        }
    )

    rscript = shutil.which("Rscript")
    rows.append(
        {
            "validacion": "comparacion_R_survey_JKn",
            "resultado": "pendiente_entorno" if rscript is None else "preparada",
            "diferencia_maxima": math.nan,
            "tolerancia": math.nan,
            "detalle": "Rscript no esta disponible; se deja script de comparacion preparado."
            if rscript is None
            else f"Rscript disponible en {rscript}; ejecutar script preparado.",
        }
    )
    return pd.DataFrame(rows)


def read_design_metadata(metadata_path: Path) -> pd.DataFrame:
    """Lee metadata local y extrae variables de diseno."""

    meta = pd.read_csv(metadata_path)
    variables = ["factor", "factor_hogar", "est_dis", "upm"]
    cols = [c for c in ["year", "table", "variable", "label", "dtype", "source_pdf", "source_page"] if c in meta.columns]
    return meta.loc[meta["variable"].isin(variables), cols].sort_values(["year", "table", "variable"])


def write_r_survey_script(path: Path) -> None:
    """Deja un script opcional para comparar JKn con R survey si R existe."""

    path.parent.mkdir(parents=True, exist_ok=True)
    script = r'''# Validacion opcional contra survey::svrepdesign.
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
'''
    path.write_text(script, encoding="utf-8")


def _fmt_number(value: float, digits: int = 0) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):,.{digits}f}"


def _svg_escape(text: Any) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _write_svg_errorbar(
    data: pd.DataFrame,
    path: Path,
    title: str,
    y_label: str,
    note: str,
    zero_line: bool = False,
) -> None:
    """Figura SVG minima para entornos sin matplotlib."""

    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 520
    margin_left, margin_right, margin_top, margin_bottom = 95, 35, 70, 85
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    values = pd.concat([data["ic95_inf"], data["ic95_sup"], data["estimacion"]]).dropna().astype(float)
    if values.empty:
        ymin, ymax = 0.0, 1.0
    else:
        ymin, ymax = float(values.min()), float(values.max())
        pad = (ymax - ymin) * 0.12 if ymax > ymin else max(abs(ymax) * 0.1, 1.0)
        ymin -= pad
        ymax += pad
        if zero_line:
            ymin = min(ymin, 0.0)
            ymax = max(ymax, 0.0)

    def x_pos(i: int, n: int) -> float:
        if n == 1:
            return margin_left + plot_w / 2.0
        return margin_left + i * (plot_w / (n - 1))

    def y_pos(v: float) -> float:
        return margin_top + (ymax - v) / (ymax - ymin) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin_left}" y="35" font-family="Arial" font-size="22" font-weight="700" fill="#263238">{_svg_escape(title)}</text>',
        f'<text x="{margin_left}" y="58" font-family="Arial" font-size="13" fill="#546e7a">{_svg_escape(note)}</text>',
        f'<line x1="{margin_left}" x2="{margin_left + plot_w}" y1="{margin_top + plot_h}" y2="{margin_top + plot_h}" stroke="#455a64" stroke-width="1"/>',
        f'<line x1="{margin_left}" x2="{margin_left}" y1="{margin_top}" y2="{margin_top + plot_h}" stroke="#455a64" stroke-width="1"/>',
    ]

    for t in range(5):
        value = ymin + t * (ymax - ymin) / 4.0
        y = y_pos(value)
        parts.append(f'<line x1="{margin_left}" x2="{margin_left + plot_w}" y1="{y:.2f}" y2="{y:.2f}" stroke="#eceff1" stroke-width="1"/>')
        parts.append(f'<text x="{margin_left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="11" fill="#607d8b">{_fmt_number(value, 0)}</text>')
    if zero_line:
        y0 = y_pos(0.0)
        parts.append(f'<line x1="{margin_left}" x2="{margin_left + plot_w}" y1="{y0:.2f}" y2="{y0:.2f}" stroke="#d32f2f" stroke-width="1.4" stroke-dasharray="6,5"/>')

    n = len(data)
    color = "#006d77" if not zero_line else "#7b2cbf"
    line_points = []
    for i, row in data.reset_index(drop=True).iterrows():
        x = x_pos(i, n)
        y = y_pos(float(row["estimacion"]))
        y_low = y_pos(float(row["ic95_inf"])) if math.isfinite(float(row["ic95_inf"])) else y
        y_high = y_pos(float(row["ic95_sup"])) if math.isfinite(float(row["ic95_sup"])) else y
        line_points.append(f"{x:.2f},{y:.2f}")
        parts.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{y_high:.2f}" y2="{y_low:.2f}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<line x1="{x - 7:.2f}" x2="{x + 7:.2f}" y1="{y_high:.2f}" y2="{y_high:.2f}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<line x1="{x - 7:.2f}" x2="{x + 7:.2f}" y1="{y_low:.2f}" y2="{y_low:.2f}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="{color}"/>')
        parts.append(f'<text x="{x:.2f}" y="{margin_top + plot_h + 24}" text-anchor="middle" font-family="Arial" font-size="12" fill="#37474f">{int(row["anio"])}</text>')
    if len(line_points) > 1:
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(line_points)}"/>')

    parts.append(f'<text x="18" y="{margin_top + plot_h / 2:.2f}" transform="rotate(-90 18,{margin_top + plot_h / 2:.2f})" text-anchor="middle" font-family="Arial" font-size="13" fill="#37474f">{_svg_escape(y_label)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_figures(estimates: pd.DataFrame, contrastes: pd.DataFrame, figure_dir: Path) -> list[dict[str, str]]:
    """Escribe una o dos figuras. Usa matplotlib si existe; si no, SVG."""

    figure_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, str]] = []
    has_matplotlib = importlib.util.find_spec("matplotlib") is not None

    national_household = estimates[
        (estimates["estimando"].eq("media_ingreso_corriente_hogar"))
        & (estimates["dominio"].eq("Nacional"))
        & (estimates["estado"].eq("ok"))
    ].sort_values("anio")
    contrast = contrastes[contrastes["estado"].eq("ok")].sort_values("anio")

    if has_matplotlib:
        import matplotlib.pyplot as plt  # type: ignore

        if not national_household.empty:
            path = figure_dir / "diseno_muestral_ingreso_hogar_ic95.png"
            fig, ax = plt.subplots(figsize=(8.5, 4.8))
            yerr = np.vstack(
                [
                    national_household["estimacion"] - national_household["ic95_inf"],
                    national_household["ic95_sup"] - national_household["estimacion"],
                ]
            )
            ax.errorbar(national_household["anio"], national_household["estimacion"], yerr=yerr, marker="o")
            ax.set_title("Media nominal trimestral del ingreso corriente del hogar")
            ax.set_xlabel("Anio")
            ax.set_ylabel("Pesos nominales")
            ax.grid(True, axis="y", alpha=0.25)
            fig.tight_layout()
            fig.savefig(path, dpi=160)
            plt.close(fig)
            outputs.append({"figura": "media_hogar_nacional", "archivo": str(path), "motor": "matplotlib"})
        if not contrast.empty:
            path = figure_dir / "diseno_muestral_contraste_norte_sur_ic95.png"
            fig, ax = plt.subplots(figsize=(8.5, 4.8))
            yerr = np.vstack([contrast["estimacion"] - contrast["ic95_inf"], contrast["ic95_sup"] - contrast["estimacion"]])
            ax.axhline(0, color="0.35", lw=1)
            ax.errorbar(contrast["anio"], contrast["estimacion"], yerr=yerr, marker="o", color="#7b2cbf")
            ax.set_title("Diferencia Norte - Sur: media laboral/negocio positiva")
            ax.set_xlabel("Anio")
            ax.set_ylabel("Pesos nominales")
            ax.grid(True, axis="y", alpha=0.25)
            fig.tight_layout()
            fig.savefig(path, dpi=160)
            plt.close(fig)
            outputs.append({"figura": "contraste_norte_sur", "archivo": str(path), "motor": "matplotlib"})
    else:
        if not national_household.empty:
            path = figure_dir / "diseno_muestral_ingreso_hogar_ic95.svg"
            _write_svg_errorbar(
                national_household,
                path,
                "Media nominal trimestral del ingreso corriente del hogar",
                "Pesos nominales",
                "Puntos ponderados e IC95 t-JKn aproximado",
            )
            outputs.append({"figura": "media_hogar_nacional", "archivo": str(path), "motor": "svg_fallback"})
        if not contrast.empty:
            path = figure_dir / "diseno_muestral_contraste_norte_sur_ic95.svg"
            _write_svg_errorbar(
                contrast,
                path,
                "Diferencia Norte - Sur en ingreso laboral/negocio positivo",
                "Pesos nominales",
                "Contraste recalculado dentro de cada replica JKn",
                zero_line=True,
            )
            outputs.append({"figura": "contraste_norte_sur", "archivo": str(path), "motor": "svg_fallback"})
    return outputs


def build_stage11_outputs(project_root: Path | str = ".") -> dict[str, Any]:
    """Ejecuta la etapa 11 completa y escribe tablas/reporte/manifest."""

    root = Path(project_root)
    revision_dir = root / "data" / "interim" / "revision_4"
    table_dir = root / "reports" / "tables" / "diseno_muestral"
    figure_dir = root / "reports" / "figures_documentacion"
    table_dir.mkdir(parents=True, exist_ok=True)

    hogar_path = revision_dir / "mart_hogar_2018_2024.csv.gz"
    persona_path = revision_dir / "mart_persona_2018_2024.csv.gz"
    if not hogar_path.exists() or not persona_path.exists():
        missing = [str(p) for p in [hogar_path, persona_path] if not p.exists()]
        raise FileNotFoundError(f"Faltan marts nominales de revision_4: {missing}")

    hogar_cols = [
        "anio",
        "folioviv",
        "foliohog",
        "est_dis",
        "upm",
        "factor",
        "factor_hogar",
        "ing_cor_hogar_oficial_tri",
        "region_banxico",
    ]
    persona_cols = [
        "anio",
        "folioviv",
        "foliohog",
        "numren",
        "est_dis",
        "upm",
        "factor",
        "factor_hogar",
        "ingreso_persona_laboral_negocio_tri",
        "region_banxico",
    ]
    hogar = pd.read_csv(hogar_path, usecols=hogar_cols, low_memory=False)
    persona = pd.read_csv(persona_path, usecols=persona_cols, low_memory=False)

    audit_hogar = audit_design(hogar, "hogar", ["anio", "folioviv", "foliohog"])
    audit_persona = audit_design(persona, "persona", ["anio", "folioviv", "foliohog", "numren"])
    audit = pd.concat([audit_hogar, audit_persona], ignore_index=True).sort_values(
        ["anio", "unidad"]
    ).reset_index(drop=True)
    consistency = audit_household_person_consistency(hogar, persona)

    estimate_rows: list[dict[str, Any]] = []
    contrast_rows: list[dict[str, Any]] = []

    for year in sorted(hogar["anio"].dropna().unique()):
        h_year = hogar[hogar["anio"].eq(year)].copy()
        y_h = pd.to_numeric(h_year["ing_cor_hogar_oficial_tri"], errors="coerce")
        for domain in DOMINIOS_REPORTE:
            mask = pd.Series(True, index=h_year.index) if domain == "Nacional" else h_year["region_banxico"].eq(domain)
            estimate_rows.append(
                ratio_jkn(
                    h_year,
                    y_h,
                    pd.Series(1.0, index=h_year.index),
                    mask,
                    {
                        "anio": int(year),
                        "unidad": "hogar",
                        "dominio": domain,
                        "universo": "Hogares ENIGH presentes en mart_hogar",
                        "estimando": "media_ingreso_corriente_hogar",
                        "variable": "ing_cor_hogar_oficial_tri",
                        "ponderador": "factor",
                        "unidad_monetaria": "pesos nominales trimestrales",
                        "nota": "Media de razon: ingreso corriente trimestral del hogar / hogares expandidos.",
                    },
                )
            )

    for year in sorted(persona["anio"].dropna().unique()):
        p_year = persona[persona["anio"].eq(year)].copy()
        y_p = pd.to_numeric(p_year["ingreso_persona_laboral_negocio_tri"], errors="coerce")
        positive = y_p.gt(0)
        indicator = positive.astype(float)
        for domain in DOMINIOS_REPORTE:
            region_mask = pd.Series(True, index=p_year.index) if domain == "Nacional" else p_year["region_banxico"].eq(domain)
            estimate_rows.append(
                ratio_jkn(
                    p_year,
                    indicator,
                    pd.Series(1.0, index=p_year.index),
                    region_mask & y_p.notna(),
                    {
                        "anio": int(year),
                        "unidad": "persona",
                        "dominio": domain,
                        "universo": "Personas validas en mart_persona, incluidas personas menores",
                        "estimando": "proporcion_ingreso_laboral_negocio_positivo",
                        "variable": "I(ingreso_persona_laboral_negocio_tri > 0)",
                        "ponderador": "factor",
                        "unidad_monetaria": "proporcion",
                        "nota": "Proporcion descriptiva; no se interpreta como empleo ni participacion laboral.",
                    },
                )
            )
            estimate_rows.append(
                ratio_jkn(
                    p_year,
                    y_p,
                    pd.Series(1.0, index=p_year.index),
                    region_mask & positive,
                    {
                        "anio": int(year),
                        "unidad": "persona",
                        "dominio": domain,
                        "universo": "Personas con ingreso laboral/negocio positivo en mart_persona",
                        "estimando": "media_ingreso_laboral_negocio_positivo",
                        "variable": "ingreso_persona_laboral_negocio_tri",
                        "ponderador": "factor",
                        "unidad_monetaria": "pesos nominales trimestrales",
                        "nota": "Media condicionada al dominio I(ingreso > 0).",
                    },
                )
            )

        contrast_rows.append(
            contrast_difference_jkn(
                p_year,
                y_p,
                p_year["region_banxico"].eq("Norte") & positive,
                p_year["region_banxico"].eq("Sur") & positive,
                {
                    "anio": int(year),
                    "unidad": "persona",
                    "dominio": "Norte menos Sur",
                    "universo": "Personas con ingreso laboral/negocio positivo en Norte o Sur",
                    "estimando": "diferencia_media_ingreso_laboral_negocio_positivo_norte_sur",
                    "variable": "ingreso_persona_laboral_negocio_tri",
                    "ponderador": "factor",
                    "unidad_monetaria": "pesos nominales trimestrales",
                    "nota": "Diferencia recalculada dentro de cada replica JKn para conservar covarianza.",
                },
            )
        )

    estimates = pd.DataFrame(estimate_rows)
    contrastes = pd.DataFrame(contrast_rows)
    validations = run_internal_validations(estimates, contrastes)

    metadata_design = read_design_metadata(root / "docs" / "enigh_variable_metadata.csv")
    pdf_sources = [
        {"anio": int(path.parent.name), "archivo": str(path), "bytes": path.stat().st_size}
        for path in sorted((root / "data" / "raw" / "EINGH").glob("*/doc_*.pdf"))
    ]
    figures = write_figures(estimates, contrastes, figure_dir)
    write_r_survey_script(table_dir / "validacion_r_survey_jkn.R")

    audit_path = table_dir / "audit_diseno_anio_unidad.csv"
    consistency_path = table_dir / "consistencia_hogar_persona.csv"
    estimates_path = table_dir / "estimaciones_nacionales_regionales.csv"
    contrast_path = table_dir / "contraste_norte_sur.csv"
    validations_path = table_dir / "validaciones_diseno_muestral.csv"
    metadata_path = table_dir / "metadata_variables_diseno.csv"
    manifest_path = table_dir / "manifest_diseno_muestral.json"

    audit.to_csv(audit_path, index=False, encoding="utf-8")
    consistency.to_csv(consistency_path, index=False, encoding="utf-8")
    estimates.to_csv(estimates_path, index=False, encoding="utf-8")
    contrastes.to_csv(contrast_path, index=False, encoding="utf-8")
    validations.to_csv(validations_path, index=False, encoding="utf-8")
    metadata_design.to_csv(metadata_path, index=False, encoding="utf-8")

    manifest = {
        "etapa": 11,
        "nombre": "diseno_muestral_formal_e_inferencia_descriptiva",
        "fecha_ejecucion": pd.Timestamp.now().isoformat(),
        "inputs": {
            "revision_dir": str(revision_dir),
            "mart_hogar": str(hogar_path),
            "mart_persona": str(persona_path),
            "metadata": str(root / "docs" / "enigh_variable_metadata.csv"),
            "pdfs_locales": pdf_sources,
        },
        "parametros": {
            "metodo_varianza": "JKn estratificado por UPM",
            "centrado": "mse=True; replicas centradas en theta_hat completo",
            "fpc": "no incorporada",
            "taylor": "pospuesto; no usado",
            "pesos": "factor final observable en los marts; replicas construidas por el proyecto",
            "moneda": "nominal trimestral",
            "grados_libertad": "nu_D = M_D - H_D por soporte de dominio; contraste usa union Norte-Sur",
        },
        "dependencias": dependency_versions(),
        "salidas": {
            "audit": str(audit_path),
            "consistency": str(consistency_path),
            "estimates": str(estimates_path),
            "contrast": str(contrast_path),
            "validations": str(validations_path),
            "metadata_design": str(metadata_path),
            "figures": figures,
            "r_survey_script": str(table_dir / "validacion_r_survey_jkn.R"),
        },
        "verificacion": {
            "estado_global": "ok"
            if audit["estado"].eq("ok").all()
            and consistency["estado"].eq("ok").all()
            and estimates["estado"].eq("ok").all()
            and contrastes["estado"].eq("ok").all()
            and validations.loc[validations["resultado"].ne("pendiente_entorno"), "resultado"].eq("ok").all()
            else "revisar",
            "max_diferencia_directa": float(
                pd.concat([estimates["diferencia_directa"], contrastes["diferencia_directa"]]).max()
            ),
            "validacion_R_survey": "pendiente_entorno"
            if shutil.which("Rscript") is None
            else "script_preparado",
        },
        "limitaciones": [
            "JKn aproxima el diseno con estratos y UPM observables; no reconstruye calibracion, no respuesta ni FPC oficiales.",
            "Los intervalos t son referencias aproximadas de muestreo, no garantias exactas de cobertura.",
            "Las comparaciones temporales de ingresos se mantienen nominales en esta etapa; no son cambios reales de poder adquisitivo.",
            "La discrepancia previa con Banxico queda aceptada como limitacion metodologica y no se reabre aqui.",
            "R/survey no esta disponible en el entorno local; la comparacion especializada queda preparada, no ejecutada.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown_report(root, audit, estimates, contrastes, validations, manifest)
    return manifest


def write_markdown_report(
    root: Path,
    audit: pd.DataFrame,
    estimates: pd.DataFrame,
    contrastes: pd.DataFrame,
    validations: pd.DataFrame,
    manifest: dict[str, Any],
) -> None:
    """Escribe el reporte metodologico de la etapa 11."""

    report_path = root / "reports" / "diseno_muestral_formal.md"
    national = estimates[estimates["dominio"].eq("Nacional")].copy()
    household = national[national["estimando"].eq("media_ingreso_corriente_hogar")]
    prop = national[national["estimando"].eq("proporcion_ingreso_laboral_negocio_positivo")]
    cond = national[national["estimando"].eq("media_ingreso_laboral_negocio_positivo")]

    def table_md(df: pd.DataFrame, cols: list[str], digits: dict[str, int] | None = None) -> str:
        digits = digits or {}
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df[cols].iterrows():
            cells = []
            for col in cols:
                value = row[col]
                if isinstance(value, (float, np.floating)):
                    cells.append(_fmt_number(float(value), digits.get(col, 0)))
                else:
                    cells.append(str(value))
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    audit_short = audit[
        [
            "anio",
            "unidad",
            "filas",
            "estratos",
            "upm",
            "estratos_singleton",
            "upm_raw_en_multiples_estratos",
            "estado",
        ]
    ]
    result_cols = ["anio", "estimacion", "se_jkn", "nu", "ic95_inf", "ic95_sup", "estado"]
    validation_cols = ["validacion", "resultado", "diferencia_maxima", "tolerancia"]

    figures_md = "\n".join(
        f"- `{Path(fig['archivo']).as_posix()}` ({fig['motor']})" for fig in manifest["salidas"]["figures"]
    )

    text = f"""# Diseño muestral formal e inferencia descriptiva

Etapa 11 del proyecto ENIGH. Esta revisión incorpora inferencia descriptiva aproximada con el diseño observable en los marts: ponderador `factor`, estrato de diseño `est_dis` y UPM `upm`. El trabajo se mantiene en variables nominales trimestrales y no modifica datos crudos, marts ni la etapa 10 de homologación monetaria.

## Alcance

- Fuente operativa: `data/interim/revision_4/mart_hogar_2018_2024.csv.gz` y `data/interim/revision_4/mart_persona_2018_2024.csv.gz`.
- Unidad hogar: media nominal trimestral de `ing_cor_hogar_oficial_tri`.
- Unidad persona: proporción con `ingreso_persona_laboral_negocio_tri > 0`, incluyendo personas menores en el denominador.
- Unidad persona condicionada: media nominal trimestral de `ingreso_persona_laboral_negocio_tri` solo entre personas con ingreso positivo.
- Contraste: diferencia Norte menos Sur de la media condicionada anterior.

## Fórmulas

Para un dominio descriptivo D:

`N_hat_D = sum_i w_i d_i`

`Y_hat_D = sum_i w_i d_i y_i`

`mu_hat_D = Y_hat_D / N_hat_D`

`p_hat_D = sum_i w_i d_i I(y_i > 0) / sum_i w_i d_i`

La media condicionada usa `d_i = I(y_i > 0)` dentro del dominio geográfico. El contraste se define como:

`Delta_hat = mu_hat_Norte - mu_hat_Sur`

## Varianza JKn

Se usa JKn estratificado por UPM como aproximación. Para cada estrato h con `m_h` UPMs, la réplica que elimina la UPM j asigna peso 0 a la UPM eliminada y multiplica los pesos de las demás UPM del mismo estrato por `m_h / (m_h - 1)`. Los demás estratos permanecen sin cambio.

La varianza se centra en la estimación completa:

`V_JK = sum_h ((m_h - 1) / m_h) sum_j (theta_(h,j) - theta_hat)^2`

`SE_JK = sqrt(V_JK)`

Los dominios se calculan sobre el diseño completo de cada año y unidad: las UPM fuera del dominio conservan contribución cero. El contraste Norte-Sur recalcula ambas medias dentro de la misma réplica, por lo que la covarianza queda incorporada naturalmente.

## Referencia t

El intervalo reportado es `estimación ± t(0.975, nu) * SE_JK`. Esta t es una referencia finita aproximada para la distribución muestral studentizada, no una t exacta clásica. La t exacta clásica requeriría una razón `Z / sqrt(U / nu)` con normalidad, chi-cuadrada e independencia, condiciones que no se demuestran aquí.

Regla usada:

- Diseño completo: `nu_design = M - H`.
- Dominio: `nu_D = M_D - H_D`, donde `M_D` y `H_D` son UPMs y estratos con soporte del dominio.
- Contraste Norte-Sur: soporte unido de Norte y Sur.
- Si `nu <= 0` o el dominio no tiene soporte suficiente, se bloquea el IC. Las proporciones usan Wald-t aproximado y no se recortan a `[0, 1]`.

## Auditoría de diseño

{table_md(audit_short, list(audit_short.columns))}

Los códigos 0 en `est_dis` o `upm` se auditan, pero no se tratan como faltantes ni como inválidos por sí mismos. Cuando el mismo código crudo de UPM aparece en más de un estrato, el cálculo usa identificadores compuestos por año, estrato y UPM; no se interpreta como seguimiento longitudinal.

## Estimaciones nacionales

Media nominal trimestral del ingreso corriente del hogar:

{table_md(household[result_cols], result_cols, {"estimacion": 0, "se_jkn": 0, "ic95_inf": 0, "ic95_sup": 0})}

Proporción de personas con ingreso laboral/negocio positivo:

{table_md(prop[result_cols], result_cols, {"estimacion": 4, "se_jkn": 4, "ic95_inf": 4, "ic95_sup": 4})}

Media nominal trimestral entre personas con ingreso laboral/negocio positivo:

{table_md(cond[result_cols], result_cols, {"estimacion": 0, "se_jkn": 0, "ic95_inf": 0, "ic95_sup": 0})}

## Contraste Norte-Sur

{table_md(contrastes[result_cols], result_cols, {"estimacion": 0, "se_jkn": 0, "ic95_inf": 0, "ic95_sup": 0})}

## Validaciones

{table_md(validations[validation_cols], validation_cols, {"diferencia_maxima": 12, "tolerancia": 12})}

La comparación especializada con R `survey` queda preparada en `reports/tables/diseno_muestral/validacion_r_survey_jkn.R`, pero no ejecutada porque `Rscript` no está disponible en el entorno local.

## Figuras

{figures_md}

## Decisiones metodológicas

- Problema: incorporar diseño muestral antes de modelar. Opción tomada: JKn estratificado por UPM con `factor`, `est_dis` y `upm`. Alternativas no usadas: Taylor linearization, bootstrap, FPC o réplicas oficiales no disponibles. Razón: reproduce una inferencia descriptiva transparente con variables observables.
- Problema: dominios geográficos. Opción tomada: construir réplicas sobre el diseño completo y asignar contribución cero fuera del dominio. Alternativa descartada: filtrar antes de definir diseño. Razón: evita perder UPMs/estratos necesarios para la varianza de dominio.
- Problema: contraste Norte-Sur. Opción tomada: recalcular ambas medias dentro de cada réplica. Alternativa descartada: sumar varianzas regionales. Razón: el método conserva la covarianza implícita.
- Problema: temporalidad monetaria. Opción tomada: mantener estimandos nominales en esta etapa. Razón: la revisión de poder adquisitivo y deflactores queda como complemento metodológico posterior; no se reabre la discrepancia con Banxico.

## Limitaciones

- Los pesos replicados son construidos por el proyecto; no son pesos replicados oficiales de INEGI.
- No se reconstruyen calibración, no respuesta, FPC ni detalles no observables del diseño original.
- La referencia t no prueba cobertura exacta de 95%.
- El notebook 00 se conserva como histórico y no se usa como referencia vigente.
- La validación contra R `survey` queda pendiente por entorno, no por lógica de implementación.
"""
    report_path.write_text(text, encoding="utf-8")

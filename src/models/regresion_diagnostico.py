"""Rutinas de modelos diagnosticos para determinantes.

Estas funciones ajustan modelos exploratorios sobre la muestra de
entrenamiento. No implementan seleccion automatica ni guardan modelos finales.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def add_intercept(X: pd.DataFrame | np.ndarray) -> np.ndarray:
    values = X.to_numpy(dtype=float) if isinstance(X, pd.DataFrame) else np.asarray(X, dtype=float)
    return np.column_stack([np.ones(values.shape[0]), values])


def fit_ols(X: pd.DataFrame, y: pd.Series | np.ndarray, *, scale_name: str) -> dict[str, Any]:
    y_arr = np.asarray(y, dtype=float)
    design = add_intercept(X)
    beta, *_ = np.linalg.lstsq(design, y_arr, rcond=None)
    fitted = design @ beta
    residuals = y_arr - fitted
    n_obs = int(len(y_arr))
    n_params = int(design.shape[1])
    rank = int(np.linalg.matrix_rank(design))
    sse = float(np.square(residuals).sum())
    tss = float(np.square(y_arr - y_arr.mean()).sum())
    r2 = float(1.0 - sse / tss) if tss > 0 else math.nan
    adj_r2 = float(1.0 - (1.0 - r2) * (n_obs - 1) / (n_obs - n_params)) if n_obs > n_params and math.isfinite(r2) else math.nan
    sigma2 = sse / max(n_obs - n_params, 1)
    ll_scale = max(sse / max(n_obs, 1), np.finfo(float).tiny)
    aic = float(n_obs * math.log(ll_scale) + 2 * n_params)
    bic = float(n_obs * math.log(ll_scale) + math.log(n_obs) * n_params)
    return {
        "scale_name": scale_name,
        "coef": beta,
        "fitted": fitted,
        "residuals": residuals,
        "n_obs": n_obs,
        "n_params": n_params,
        "rank": rank,
        "sse": sse,
        "r2": r2,
        "adj_r2": adj_r2,
        "aic": aic,
        "bic": bic,
        "sigma2": float(sigma2),
    }


def regression_metrics(y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray, *, scale_name: str, split: str) -> dict[str, Any]:
    y_arr = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    err = y_arr - pred
    return {
        "escala": scale_name,
        "particion": split,
        "n": int(len(y_arr)),
        "mae": float(np.abs(err).mean()),
        "rmse": float(np.sqrt(np.square(err).mean())),
    }


def coefficient_table(model: dict[str, Any], columns: list[str], column_info: pd.DataFrame) -> pd.DataFrame:
    info = column_info.set_index("columna_matriz")
    rows = [
        {
            "escala": model["scale_name"],
            "columna_matriz": "intercepto",
            "variable_original": "intercepto",
            "categoria": "",
            "referencia_variable": "",
            "coeficiente": float(model["coef"][0]),
            "nota": "Intercepto de OLS no ponderado.",
        }
    ]
    for value, col in zip(model["coef"][1:], columns):
        rows.append(
            {
                "escala": model["scale_name"],
                "columna_matriz": col,
                "variable_original": info.loc[col, "variable_original"] if col in info.index else col,
                "categoria": info.loc[col, "categoria"] if col in info.index else "",
                "referencia_variable": info.loc[col, "referencia_variable"] if col in info.index else "",
                "coeficiente": float(value),
                "nota": "Coeficiente en unidades de la escala indicada; no interpretar como inferencia poblacional.",
            }
        )
    return pd.DataFrame(rows)


def predict_ols(model: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    return add_intercept(X) @ model["coef"]


def influence_diagnostics(X: pd.DataFrame, y: pd.Series | np.ndarray, model: dict[str, Any], *, top_n: int = 25) -> tuple[pd.DataFrame, pd.DataFrame]:
    design = add_intercept(X)
    xtx_inv = np.linalg.pinv(design.T @ design)
    leverage = np.einsum("ij,jk,ik->i", design, xtx_inv, design)
    residuals = np.asarray(model["residuals"], dtype=float)
    mse = model["sse"] / max(model["n_obs"] - model["n_params"], 1)
    denom = np.square(np.maximum(1.0 - leverage, np.finfo(float).eps))
    cooks = np.square(residuals) / max(model["n_params"] * mse, np.finfo(float).tiny) * leverage / denom
    summary_rows = []
    for name, values in [("residuo", residuals), ("residuo_abs", np.abs(residuals)), ("leverage", leverage), ("cooks_distance", cooks)]:
        s = pd.Series(values)
        summary_rows.append(
            {
                "metrica": name,
                "min": float(s.min()),
                "p50": float(s.quantile(0.50)),
                "p90": float(s.quantile(0.90)),
                "p95": float(s.quantile(0.95)),
                "p99": float(s.quantile(0.99)),
                "max": float(s.max()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    order = np.argsort(-cooks)[:top_n]
    top = pd.DataFrame(
        {
            "rank_cooks_sin_identificadores": np.arange(1, len(order) + 1),
            "y": np.asarray(y, dtype=float)[order],
            "ajustado": np.asarray(model["fitted"], dtype=float)[order],
            "residuo": residuals[order],
            "leverage": leverage[order],
            "cooks_distance": cooks[order],
        }
    )
    return summary, top


def matrix_dependency_diagnostics(X: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = X.to_numpy(dtype=float)
    rank_no_intercept = int(np.linalg.matrix_rank(values))
    rank_with_intercept = int(np.linalg.matrix_rank(add_intercept(values)))
    constants = []
    for col in X.columns:
        if X[col].nunique(dropna=False) <= 1:
            constants.append({"columna": col, "valor_constante": X[col].iloc[0] if len(X) else math.nan})
    duplicates = []
    cols = list(X.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            if X[a].equals(X[b]):
                duplicates.append({"columna_a": a, "columna_b": b})
    summary = pd.DataFrame(
        [
            {"metrica": "filas", "valor": int(values.shape[0])},
            {"metrica": "columnas", "valor": int(values.shape[1])},
            {"metrica": "rango_sin_intercepto", "valor": rank_no_intercept},
            {"metrica": "rango_con_intercepto", "valor": rank_with_intercept},
            {"metrica": "constantes", "valor": len(constants)},
            {"metrica": "duplicados_exactos", "valor": len(duplicates)},
        ]
    )
    detail = pd.concat(
        [
            pd.DataFrame(constants, columns=["columna", "valor_constante"]).assign(tipo="constante"),
            pd.DataFrame(duplicates, columns=["columna_a", "columna_b"]).assign(tipo="duplicado_exacto"),
        ],
        ignore_index=True,
    )
    return summary, detail


def compute_vif_auxiliary(X: pd.DataFrame) -> pd.DataFrame:
    values = X.to_numpy(dtype=float)
    rows = []
    for j, col in enumerate(X.columns):
        y = values[:, j]
        others = np.delete(values, j, axis=1)
        design = add_intercept(others)
        coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        pred = design @ coef
        rss = float(np.square(y - pred).sum())
        tss = float(np.square(y - y.mean()).sum())
        r2 = 1.0 - rss / tss if tss > 0 else math.nan
        vif = 1.0 / (1.0 - r2) if math.isfinite(r2) and r2 < 1 else math.inf
        rows.append({"columna_matriz": col, "r2_auxiliar_con_intercepto": float(r2), "vif": float(vif), "estado": "ok"})
    return pd.DataFrame(rows).sort_values("vif", ascending=False).reset_index(drop=True)


def _corr_from_cov(cov: np.ndarray) -> np.ndarray:
    diag = np.diag(cov)
    denom = np.sqrt(np.outer(diag, diag))
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = cov / denom
    return corr


def _safe_logdet(matrix: np.ndarray) -> tuple[float, str]:
    sign, value = np.linalg.slogdet(matrix)
    if sign <= 0 or not math.isfinite(value):
        return math.nan, "determinante_no_positivo"
    return float(value), "ok"


def compute_gvif(X: pd.DataFrame, column_info: pd.DataFrame) -> pd.DataFrame:
    design = add_intercept(X)
    n_params = design.shape[1]
    rank = int(np.linalg.matrix_rank(design))
    groups = column_info.groupby("variable_original")["columna_matriz"].apply(list).to_dict()
    if rank < n_params:
        return pd.DataFrame(
            [
                {
                    "variable_original": variable,
                    "df_bloque": len(cols),
                    "gvif": math.nan,
                    "gvif_ajustado": math.nan,
                    "estado": "no_interpretar_por_singularidad",
                }
                for variable, cols in groups.items()
            ]
        )
    xtx_inv = np.linalg.pinv(design.T @ design)
    slope_corr = _corr_from_cov(xtx_inv[1:, 1:])
    col_pos = {col: idx for idx, col in enumerate(X.columns)}
    logdet_all, state_all = _safe_logdet(slope_corr)
    rows = []
    for variable, cols in groups.items():
        idx = [col_pos[col] for col in cols if col in col_pos]
        other = [i for i in range(len(X.columns)) if i not in idx]
        df = len(idx)
        if df == 0:
            rows.append(
                {
                    "variable_original": variable,
                    "df_bloque": 0,
                    "gvif": math.nan,
                    "gvif_ajustado": math.nan,
                    "estado": "sin_columnas_en_matriz",
                }
            )
            continue
        if state_all != "ok" or not other:
            rows.append(
                {
                    "variable_original": variable,
                    "df_bloque": df,
                    "gvif": math.nan,
                    "gvif_ajustado": math.nan,
                    "estado": state_all if state_all != "ok" else "sin_complemento",
                }
            )
            continue
        logdet_term, state_term = _safe_logdet(slope_corr[np.ix_(idx, idx)])
        logdet_other, state_other = _safe_logdet(slope_corr[np.ix_(other, other)])
        if state_term == state_other == "ok":
            gvif = math.exp(logdet_term + logdet_other - logdet_all)
            gvif_adj = gvif ** (1.0 / (2.0 * df))
            state = "ok"
        else:
            gvif = math.nan
            gvif_adj = math.nan
            state = ";".join(sorted({state_term, state_other} - {"ok"}))
        rows.append(
            {
                "variable_original": variable,
                "df_bloque": df,
                "gvif": float(gvif) if math.isfinite(gvif) else math.nan,
                "gvif_ajustado": float(gvif_adj) if math.isfinite(gvif_adj) else math.nan,
                "estado": state,
                "nota": "GVIF por bloque; no comparar GVIF ajustado con umbrales VIF como si fueran la misma escala.",
            }
        )
    return pd.DataFrame(rows).sort_values("gvif_ajustado", ascending=False, na_position="last").reset_index(drop=True)


def verify_vif_gvif_examples() -> pd.DataFrame:
    demo = pd.DataFrame(
        {
            "x1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "x2": [1.2, 1.9, 3.2, 3.8, 5.3, 5.7],
            "z_b": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
            "z_c": [0.0, 0.0, 1.0, 0.0, 1.0, 0.0],
        }
    )
    info = pd.DataFrame(
        [
            {"columna_matriz": "x1", "variable_original": "x1"},
            {"columna_matriz": "x2", "variable_original": "x2"},
            {"columna_matriz": "z_b", "variable_original": "z"},
            {"columna_matriz": "z_c", "variable_original": "z"},
        ]
    )
    vif = compute_vif_auxiliary(demo)
    gvif = compute_gvif(demo, info)
    x1_vif = float(vif.loc[vif["columna_matriz"].eq("x1"), "vif"].iloc[0])
    x1_gvif = float(gvif.loc[gvif["variable_original"].eq("x1"), "gvif"].iloc[0])
    return pd.DataFrame(
        [
            {
                "prueba": "gvif_un_df_igual_vif",
                "valor_a": x1_vif,
                "valor_b": x1_gvif,
                "diferencia_abs": abs(x1_vif - x1_gvif),
                "estado": "ok" if abs(x1_vif - x1_gvif) < 1e-8 else "revisar",
            },
            {
                "prueba": "gvif_bloque_multicolumna_finito",
                "valor_a": float(gvif.loc[gvif["variable_original"].eq("z"), "gvif"].iloc[0]),
                "valor_b": float(gvif.loc[gvif["variable_original"].eq("z"), "gvif_ajustado"].iloc[0]),
                "diferencia_abs": math.nan,
                "estado": "ok" if gvif.loc[gvif["variable_original"].eq("z"), "estado"].iloc[0] == "ok" else "revisar",
            },
        ]
    )


def fit_decision_tree(X_train: pd.DataFrame, y_train: pd.Series, *, max_depth: int, min_samples_leaf: float, random_state: int) -> Any:
    from sklearn.tree import DecisionTreeRegressor

    tree = DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples_leaf, random_state=random_state)
    tree.fit(X_train, y_train)
    return tree


def aggregate_column_importance(importances: np.ndarray, column_info: pd.DataFrame) -> pd.DataFrame:
    df = column_info[["columna_matriz", "variable_original"]].copy()
    df["importancia_impureza"] = importances
    return (
        df.groupby("variable_original", dropna=False)["importancia_impureza"]
        .sum()
        .reset_index()
        .sort_values("importancia_impureza", ascending=False)
        .reset_index(drop=True)
    )


def permutation_importance_by_block(
    model: Any,
    X_valid: pd.DataFrame,
    y_valid: pd.Series,
    column_info: pd.DataFrame,
    *,
    n_repeats: int,
    random_state: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    y_arr = np.asarray(y_valid, dtype=float)
    baseline = np.asarray(model.predict(X_valid), dtype=float)
    baseline_rmse = float(np.sqrt(np.square(y_arr - baseline).mean()))
    baseline_mae = float(np.abs(y_arr - baseline).mean())
    groups = column_info.groupby("variable_original")["columna_matriz"].apply(list).to_dict()
    rows = []
    for variable, cols in groups.items():
        cols = [col for col in cols if col in X_valid.columns]
        deltas_rmse = []
        deltas_mae = []
        for rep in range(n_repeats):
            X_perm = X_valid.copy()
            perm = rng.permutation(len(X_perm))
            X_perm.loc[:, cols] = X_perm.iloc[perm][cols].to_numpy()
            pred = np.asarray(model.predict(X_perm), dtype=float)
            rmse = float(np.sqrt(np.square(y_arr - pred).mean()))
            mae = float(np.abs(y_arr - pred).mean())
            rows.append(
                {
                    "variable_original": variable,
                    "repeticion": rep + 1,
                    "rmse_permutado": rmse,
                    "mae_permutado": mae,
                    "delta_rmse": rmse - baseline_rmse,
                    "delta_mae": mae - baseline_mae,
                    "baseline_rmse": baseline_rmse,
                    "baseline_mae": baseline_mae,
                }
            )
            deltas_rmse.append(rmse - baseline_rmse)
            deltas_mae.append(mae - baseline_mae)
    by_rep = pd.DataFrame(rows)
    summary = (
        by_rep.groupby("variable_original", dropna=False)
        .agg(
            delta_rmse_media=("delta_rmse", "mean"),
            delta_rmse_sd=("delta_rmse", "std"),
            delta_rmse_min=("delta_rmse", "min"),
            delta_rmse_max=("delta_rmse", "max"),
            delta_mae_media=("delta_mae", "mean"),
            delta_mae_sd=("delta_mae", "std"),
            delta_mae_min=("delta_mae", "min"),
            delta_mae_max=("delta_mae", "max"),
            repeticiones=("delta_rmse", "size"),
        )
        .reset_index()
        .sort_values("delta_rmse_media", ascending=False)
        .reset_index(drop=True)
    )
    return by_rep, summary

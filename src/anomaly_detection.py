# anomaly_detection.py
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def rolling_zscore_anomalies(
    ts_df: pd.DataFrame,
    y_col: str = "y",
    window: int = 24 * 7,   # 1 week at hourly frequency
    min_periods: int = 24,
    z_thresh: float = 3.0
) -> pd.DataFrame:
    """
    Compute rolling z-score over a univariate series and flag anomalies where |z| > z_thresh.
    Expects columns ['ds', y_col] and a regular time frequency.
    Returns a copy of ts_df with columns: ['roll_mean','roll_std','zscore','is_anomaly_z'].
    """
    df = ts_df.sort_values("ds").copy()
    s = df[y_col].astype(float)

    roll_mean = s.rolling(window=window, min_periods=min_periods).mean()
    roll_std = s.rolling(window=window, min_periods=min_periods).std(ddof=0)

    # Avoid division by zero
    roll_std_safe = roll_std.replace(0, np.nan)
    z = (s - roll_mean) / roll_std_safe

    df["roll_mean"] = roll_mean
    df["roll_std"] = roll_std
    df["zscore"] = z
    df["is_anomaly_z"] = (z.abs() > z_thresh).fillna(0).astype(int)
    return df


def isolation_forest_anomalies(
    ts_df: pd.DataFrame,
    y_col: str = "y",
    contamination: float = 0.01,
    random_state: int = 42,
    with_context: bool = True
) -> pd.DataFrame:
    """
    Train IsolationForest to score point rarity on the time series.
    If with_context=True, include simple temporal features and lags.
    Returns a copy of ts_df with columns: ['iso_score','is_anomaly_iso'].
    """
    df = ts_df.sort_values("ds").copy()
    df["ds"] = pd.to_datetime(df["ds"])

    X = pd.DataFrame(index=df.index)
    X["y"] = df[y_col].astype(float)

    if with_context:
        X["hour"] = df["ds"].dt.hour
        X["dow"] = df["ds"].dt.dayofweek
        # Simple lags and diffs
        X["lag1"] = X["y"].shift(1)
        X["lag24"] = X["y"].shift(24)
        X["diff1"] = X["y"].diff(1)
        X["diff24"] = X["y"].diff(24)

    X = X.fillna(method="bfill").fillna(0)

    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X)

    scores = model.decision_function(X)   # lower = more anomalous
    pred = model.predict(X)               # -1 anomalous, 1 normal

    df["iso_score"] = scores
    df["is_anomaly_iso"] = (pred == -1).astype(int)
    return df


def detect_anomalies(
    ts_df: pd.DataFrame,
    y_col: str = "y",
    z_window: int = 24 * 7,
    z_min_periods: int = 24,
    z_thresh: float = 3.0,
    iso_contamination: float = 0.01,
    with_context: bool = True,
    top_k: int = 20,
):
    """
    Thin wrapper that runs rolling z-score + IsolationForest, merges outputs, and ranks anomalies.
    Returns:
        anomalies (pd.DataFrame): merged signals with anomaly_rank
        top_anoms (pd.DataFrame): top-k anomalies by combined rank
    """
    z_df = rolling_zscore_anomalies(
        ts_df, y_col=y_col, window=z_window, min_periods=z_min_periods, z_thresh=z_thresh
    )
    iso_df = isolation_forest_anomalies(
        ts_df, y_col=y_col, contamination=iso_contamination, with_context=with_context
    )

    anomalies = z_df[["ds", y_col, "zscore", "is_anomaly_z"]].merge(
        iso_df[["ds", "iso_score", "is_anomaly_iso"]],
        on="ds",
        how="left",
    )

    anomalies["anomaly_rank"] = (
        anomalies["zscore"].abs().rank(ascending=False)
        + (-anomalies["iso_score"]).rank(ascending=False)
    )

    top_anoms = anomalies.sort_values("anomaly_rank").head(top_k)
    print("\n=== TOP 20 anomalies (Z-score + IsolationForest) ===")
    print(top_anoms[["ds", "y", "zscore", "iso_score", "is_anomaly_z", "is_anomaly_iso"]].to_string(index=False))
    return anomalies, top_anoms

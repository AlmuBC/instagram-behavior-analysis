# plotting.py
import math
import matplotlib.pyplot as plt
import pandas as pd

def plot_forecast_vs_true(forecast_df, true_df, label=None):
    """
    Plot forecast vs. true values.
    - forecast_df: columns ['ds', <forecast_col>]
    - true_df: columns ['ds','y']
    - label: forecast column name; if None, inferred automatically.
    """
    if label is None:
        candidates = [c for c in forecast_df.columns if c not in ("ds", "unique_id")]
        if not candidates:
            raise ValueError("No forecast column found in forecast_df.")
        label = candidates[0]

    plt.figure(figsize=(12, 5))
    plt.plot(true_df["ds"], true_df["y"], label="True", linewidth=2)
    plt.plot(forecast_df["ds"], forecast_df[label], label="Forecast", linestyle="--")
    plt.title("Forecast vs. True Daily Event Counts (2025)")
    plt.xlabel("Date")
    plt.ylabel("Event Count")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_time_series_with_anomalies(
    ts_df: pd.DataFrame,
    anomalies_df: pd.DataFrame,
    y_col: str = "y",
    point_size: int = 36,
    series_color: str = "0.6",           # gray
    z_color: str = "tab:orange",
    iso_color: str = "tab:blue",
    both_color: str = "tab:red",
):
    """
    Plot the full time series and overlay anomalies with different colors:
      - z_color:     flagged only by Z-score
      - iso_color:   flagged only by IsolationForest
      - both_color:  flagged by BOTH detectors

    Expects anomalies_df to contain ['ds','is_anomaly_z','is_anomaly_iso'].
    """
    # Prepare data
    base = ts_df[["ds", y_col]].copy()
    flags = anomalies_df[["ds", "is_anomaly_z", "is_anomaly_iso"]].copy()
    base["ds"] = pd.to_datetime(base["ds"])
    flags["ds"] = pd.to_datetime(flags["ds"])

    df = base.merge(flags, on="ds", how="left").fillna({"is_anomaly_z": 0, "is_anomaly_iso": 0})
    df = df.sort_values("ds")

    # Masks
    z_only   = (df["is_anomaly_z"] == 1) & (df["is_anomaly_iso"] == 0)
    iso_only = (df["is_anomaly_z"] == 0) & (df["is_anomaly_iso"] == 1)
    both     = (df["is_anomaly_z"] == 1) & (df["is_anomaly_iso"] == 1)

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(df["ds"], df[y_col], color=series_color, linewidth=1.5, label="Series")

    # Overlay points with distinct colors
    plt.scatter(df.loc[z_only, "ds"],   df.loc[z_only, y_col],   s=point_size, color=z_color,   label="Z-score only")
    plt.scatter(df.loc[iso_only, "ds"], df.loc[iso_only, y_col], s=point_size, color=iso_color, label="IsolationForest only")
    plt.scatter(df.loc[both, "ds"],     df.loc[both, y_col],     s=point_size, color=both_color,label="Both detectors")

    plt.title("Time series with anomaly types")
    plt.xlabel("Date")
    plt.ylabel(y_col)
    plt.legend()
    plt.tight_layout()
    plt.show()


def _parse_last_to_timedelta(last: str) -> pd.Timedelta:
    """Accepts strings like '30D', '72H', '15min' and returns a Timedelta."""
    if last is None:
        return None
    return pd.to_timedelta(last)

def plot_zoom_time_series_with_anomaly_types(
    ts_df: pd.DataFrame,
    anomalies_df: pd.DataFrame,
    y_col: str = "y",
    # Option A: explicit time range or last window
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    last: str | None = None,        # e.g. "30D", "72H"
    # Option B: zoom around a specific anomaly (by rank in anomalies_df)
    around_rank: int | None = None, # e.g. 1 = top combined anomaly
    window: str = "7D",             # +/- window around the chosen anomaly
    point_size: int = 36,
    series_color: str = "0.6",
    z_color: str = "tab:orange",
    iso_color: str = "tab:blue",
    both_color: str = "tab:red",
    title_prefix: str = "Zoomed time series with anomaly types",
):
    """
    Zoomed plot of the series with colored anomaly types.
    Choose either:
      - (start/end) or last='30D' to define a time window, OR
      - around_rank=N with window='7D' to center around an anomaly.
    """

    base = ts_df[["ds", y_col]].copy()
    base["ds"] = pd.to_datetime(base["ds"]).sort_values()
    flags = anomalies_df[["ds", "is_anomaly_z", "is_anomaly_iso"]].copy()
    flags["ds"] = pd.to_datetime(flags["ds"])

    df = base.merge(flags, on="ds", how="left").fillna({"is_anomaly_z": 0, "is_anomaly_iso": 0})
    df = df.sort_values("ds")

    # Determine zoom window
    if around_rank is not None:
        # Need anomaly_rank in anomalies_df
        if "anomaly_rank" not in anomalies_df.columns:
            raise ValueError("anomalies_df must contain 'anomaly_rank' to use around_rank.")
        center_row = anomalies_df.sort_values("anomaly_rank").iloc[around_rank - 1]
        center_ts = pd.to_datetime(center_row["ds"])
        half_win = pd.to_timedelta(window)
        mask_time = (df["ds"] >= center_ts - half_win) & (df["ds"] <= center_ts + half_win)
        title = f"{title_prefix} (around rank #{around_rank}, ±{window})"
    else:
        if last is not None:
            td = _parse_last_to_timedelta(last)
            if td is None:
                raise ValueError("Invalid 'last' argument.")
            end_ts = df["ds"].max() if end is None else pd.to_datetime(end)
            start_ts = end_ts - td
        else:
            start_ts = pd.to_datetime(start) if start is not None else df["ds"].min()
            end_ts = pd.to_datetime(end) if end is not None else df["ds"].max()
        mask_time = (df["ds"] >= start_ts) & (df["ds"] <= end_ts)
        if last is not None:
            title = f"{title_prefix} (last={last})"
        else:
            title = f"{title_prefix} ({start_ts.date()} → {end_ts.date()})"

    zoom = df.loc[mask_time].copy()

    # Masks per type (within the zoom)
    z_only   = (zoom["is_anomaly_z"] == 1) & (zoom["is_anomaly_iso"] == 0)
    iso_only = (zoom["is_anomaly_z"] == 0) & (zoom["is_anomaly_iso"] == 1)
    both     = (zoom["is_anomaly_z"] == 1) & (zoom["is_anomaly_iso"] == 1)

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(zoom["ds"], zoom[y_col], color=series_color, linewidth=1.5, label="Series")
    plt.scatter(zoom.loc[z_only, "ds"],   zoom.loc[z_only, y_col],   s=point_size, color=z_color,   label="Z-score only")
    plt.scatter(zoom.loc[iso_only, "ds"], zoom.loc[iso_only, y_col], s=point_size, color=iso_color, label="IsolationForest only")
    plt.scatter(zoom.loc[both, "ds"],     zoom.loc[both, y_col],     s=point_size, color=both_color,label="Both detectors")

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(y_col)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_anomaly_types_by_year(
    ts_df: pd.DataFrame,
    anomalies_df: pd.DataFrame,
    y_col: str = "y",
    years: list[int] | None = None,
    ncols: int = 2,
    point_size: int = 28,
    series_color: str = "0.6",      # gray line for the series
    z_color: str = "tab:orange",    # Z-score only
    iso_color: str = "tab:blue",    # IsolationForest only
    both_color: str = "tab:red",    # Both detectors
    suptitle: str = "Time series with anomaly types by year",
):
    """
    Faceted plot: one subplot per year.
    Expects anomalies_df to have ['ds','is_anomaly_z','is_anomaly_iso'] (and optionally 'anomaly_rank').
    """
    # Prepare and merge
    base = ts_df[["ds", y_col]].copy()
    base["ds"] = pd.to_datetime(base["ds"])
    base = base.sort_values("ds")
    base["year"] = base["ds"].dt.year

    flags = anomalies_df[["ds", "is_anomaly_z", "is_anomaly_iso"]].copy()
    flags["ds"] = pd.to_datetime(flags["ds"])

    df = base.merge(flags, on="ds", how="left").fillna({"is_anomaly_z": 0, "is_anomaly_iso": 0})

    # Determine years to plot
    if years is None:
        years = sorted(df["year"].dropna().unique().tolist())

    if not years:
        raise ValueError("No years found to plot.")

    n = len(years)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12 * 1.0, 3.8 * nrows), squeeze=False)
    axes_flat = axes.ravel()

    for i, yr in enumerate(years):
        ax = axes_flat[i]
        sub = df[df["year"] == yr].copy()

        # Masks
        z_only   = (sub["is_anomaly_z"] == 1) & (sub["is_anomaly_iso"] == 0)
        iso_only = (sub["is_anomaly_z"] == 0) & (sub["is_anomaly_iso"] == 1)
        both     = (sub["is_anomaly_z"] == 1) & (sub["is_anomaly_iso"] == 1)

        # Draw
        ax.plot(sub["ds"], sub[y_col], color=series_color, linewidth=1.5, label="Series")
        ax.scatter(sub.loc[z_only, "ds"],   sub.loc[z_only, y_col],   s=point_size, color=z_color,   label="Z-score only")
        ax.scatter(sub.loc[iso_only, "ds"], sub.loc[iso_only, y_col], s=point_size, color=iso_color, label="IsolationForest only")
        ax.scatter(sub.loc[both, "ds"],     sub.loc[both, y_col],     s=point_size, color=both_color,label="Both detectors")

        ax.set_title(f"{yr}")
        ax.set_xlabel("Date")
        ax.set_ylabel(y_col)

        # Light grid for readability
        ax.grid(True, alpha=0.2)

        # Only put legend once (top-left subplot) to avoid clutter
        if i == 0:
            ax.legend()
        else:
            pass

    # Hide any extra axes (when grid > years)
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis("off")

    fig.suptitle(suptitle, y=1.02, fontsize=14)
    fig.tight_layout()
    return fig, axes


def plot_prediction_with_anomaly_types(
    pred_series_df: pd.DataFrame,        # ['ds','y'] from build_series_from_forecast
    anomalies_df: pd.DataFrame,          # output from detect_anomalies on the prediction
    true_df: pd.DataFrame | None = None, # optional ['ds','y'] ground truth series at same freq
    point_size: int = 36,
    pred_color: str = "0.3",             # dark gray for prediction
    true_color: str = "0.6",             # light gray for truth
    z_color: str = "tab:orange",         # Z-score only
    iso_color: str = "tab:blue",         # IsolationForest only
    both_color: str = "tab:red",         # Both detectors
    title: str = "Predicted vs True with anomaly types",
):
    """
    Plot prediction (line) + optional true series (line) and overlay anomaly points on the prediction:
      - z_color:     flagged only by Z-score
      - iso_color:   flagged only by IsolationForest
      - both_color:  flagged by BOTH detectors
    Expects anomalies_df to contain ['ds','is_anomaly_z','is_anomaly_iso'].
    """
    # Prepare frames
    pred = pred_series_df.rename(columns={"y": "pred"}).copy()
    pred["ds"] = pd.to_datetime(pred["ds"])

    flags = anomalies_df[["ds", "is_anomaly_z", "is_anomaly_iso"]].copy()
    flags["ds"] = pd.to_datetime(flags["ds"])

    df = pred.merge(flags, on="ds", how="left").fillna({"is_anomaly_z": 0, "is_anomaly_iso": 0})
    df = df.sort_values("ds")

    if true_df is not None:
        truth = true_df.rename(columns={"y": "true"}).copy()
        truth["ds"] = pd.to_datetime(truth["ds"])
        # align on ds without dropping prediction points
        df = df.merge(truth[["ds", "true"]], on="ds", how="left")

    # Masks for anomaly types (on prediction)
    z_only   = (df["is_anomaly_z"] == 1) & (df["is_anomaly_iso"] == 0)
    iso_only = (df["is_anomaly_z"] == 0) & (df["is_anomaly_iso"] == 1)
    both     = (df["is_anomaly_z"] == 1) & (df["is_anomaly_iso"] == 1)

    # Plot
    plt.figure(figsize=(12, 5))
    # True first (so prediction sits on top if overlapping)
    if "true" in df.columns:
        plt.plot(df["ds"], df["true"], color=true_color, linewidth=1.5, label="True")

    plt.plot(df["ds"], df["pred"], color=pred_color, linewidth=1.8, label="Prediction")

    # Anomaly points on the prediction curve
    plt.scatter(df.loc[z_only, "ds"],   df.loc[z_only, "pred"],   s=point_size, color=z_color,   label="Z-score only")
    plt.scatter(df.loc[iso_only, "ds"], df.loc[iso_only, "pred"], s=point_size, color=iso_color, label="IsolationForest only")
    plt.scatter(df.loc[both, "ds"],     df.loc[both, "pred"],     s=point_size, color=both_color,label="Both detectors")

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.show()

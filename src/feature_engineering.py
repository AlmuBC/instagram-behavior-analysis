import pandas as pd

def aggregate_selected_event_types(df, selected_types, freq='H'):
    """
    Aggregate counts of selected event types over time windows.

    Parameters:
        df (pd.DataFrame): input with 'timestamp' and 'event_type'
        selected_types (List[str]): list of event types to include
        freq (str): resampling frequency ('H' = hourly, 'D' = daily)

    Returns:
        pd.DataFrame: one column per event type with counts per time period
    """
    df = df.copy()
    df = df[df['event_type'].isin(selected_types)]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['count'] = 1

    counts = (
        df.set_index('timestamp')
          .groupby('event_type')
          .resample(freq)['count']
          .sum()
          .unstack(level=0)
          .fillna(0)
          .reset_index()
    )

    return counts

def prepare_time_series_for_nhits(df, signals, freq='H'):
    """
    Format time series data for NHITS: [unique_id, ds, y].
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').resample(freq).sum().reset_index()

    all_series = []

    for signal in signals:
        temp = df[['timestamp', signal]].dropna()
        temp = temp.rename(columns={'timestamp': 'ds', signal: 'y'})
        temp['unique_id'] = signal
        all_series.append(temp)

    return pd.concat(all_series).reset_index(drop=True)

def create_total_event_time_series(df, freq='h'):
    """
    Create a single time series with total event count over time.

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp'
        freq (str): Resampling frequency ('H' for hourly, 'D' for daily)

    Returns:
        pd.DataFrame: DataFrame with columns ['ds', 'y'] representing the time series
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['count'] = 1

    ts_df = (
        df.set_index('timestamp')
          .resample(freq)['count']
          .sum()
          .reset_index()
          .rename(columns={'timestamp': 'ds', 'count': 'y'})
    )

    return ts_df


def build_series_from_forecast(forecast_df: pd.DataFrame, forecast_col: str | None = None) -> pd.DataFrame:
    """
    Adapt a forecast dataframe to the standard shape ['ds','y'] so it can be
    fed directly into detect_anomalies(...). If forecast_col is None, it is inferred.
    """
    if forecast_col is None:
        cols = [c for c in forecast_df.columns if c not in ("ds", "unique_id")]
        if not cols:
            raise ValueError("No forecast column found in forecast_df.")
        forecast_col = cols[0]

    out = forecast_df[["ds", forecast_col]].rename(columns={forecast_col: "y"}).copy()
    out["ds"] = pd.to_datetime(out["ds"])
    return out

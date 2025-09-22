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

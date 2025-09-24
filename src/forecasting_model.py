from neuralforecast.models import NHITS
from neuralforecast import NeuralForecast
import pandas as pd
import numpy as np

def train_and_forecast_nhits(ts_df, input_size=30, max_steps=5):
    """
    Train NHITS on total daily event counts before 2025,
    and forecast the total daily activity in 2025.

    Parameters:
        ts_df (pd.DataFrame): DataFrame with ['ds', 'y'] at hourly frequency
        input_size (int): Number of days in the input window
        max_steps (int): Number of training steps

    Returns:
        nf (NeuralForecast): Trained model
        forecast_df (pd.DataFrame): Forecasted values for 2025 (daily aggregated)
        true_2025_df (pd.DataFrame): Ground truth values for 2025 (daily aggregated)
    """
    ts_df = ts_df.copy()
    ts_df['ds'] = pd.to_datetime(ts_df['ds'])

    # Aggregate to daily totals
    ts_df['date'] = ts_df['ds'].dt.date
    daily_df = (
        ts_df.groupby('date')['y']
        .sum()
        .reset_index()
        .rename(columns={'date': 'ds'})
    )

    # Add a common unique_id for NHITS
    daily_df['unique_id'] = 'total'
    daily_df = daily_df[['unique_id', 'ds', 'y']]

    # Split into training and test
    daily_df['ds'] = pd.to_datetime(daily_df['ds'])
    train_df = daily_df[daily_df['ds'] < '2025-01-01']
    true_2025_df = daily_df[(daily_df['ds'] >= '2025-01-01') & (daily_df['ds'] < '2026-01-01')]

    h = true_2025_df['ds'].nunique()

    model = NHITS(h=h, input_size=input_size, max_steps=max_steps)
    nf = NeuralForecast(models=[model], freq='D')
    nf.fit(df=train_df)
    forecast_df = nf.predict()

    return nf, forecast_df, true_2025_df

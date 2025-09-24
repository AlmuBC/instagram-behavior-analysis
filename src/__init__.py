from data_loader import load_all_instagram_events
from feature_engineering import create_total_event_time_series
from forecasting_model import train_and_forecast_nhits
from plotting import plot_forecast_vs_true


def main():
    df = load_all_instagram_events(user_name="Almu")
    ts_df = create_total_event_time_series(df, freq='h')
    nf, forecast_df, true_2025_df = train_and_forecast_nhits(ts_df)

    plot_forecast_vs_true(forecast_df, true_2025_df)
    print('END')

if __name__ == "__main__":
    main()

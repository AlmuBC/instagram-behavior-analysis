# __init__.py
from data_loader import load_all_instagram_events
from feature_engineering import create_total_event_time_series, build_series_from_forecast
from forecasting_model import train_and_forecast_nhits
from plotting import plot_forecast_vs_true, plot_time_series_with_anomalies, plot_zoom_time_series_with_anomaly_types, plot_anomaly_types_by_year, plot_prediction_with_anomaly_types
from anomaly_detection import detect_anomalies


def main():
    # 1) Load raw events first (source of truth)
    df_events = load_all_instagram_events(user_name="Almu")

    # 2) Build a single hourly time series: ['ds', 'y']
    ts_df = create_total_event_time_series(df_events, freq='H')

    # 3) Unsupervised anomaly detection (one-liner wrapper)
    anomalies, top_anoms = detect_anomalies(ts_df)

    

    plot_time_series_with_anomalies(ts_df, anomalies, y_col="y", point_size=42)
    plot_zoom_time_series_with_anomaly_types(ts_df, anomalies, y_col="y", around_rank=10, window="7D", point_size=60)
    plot_zoom_time_series_with_anomaly_types(ts_df, anomalies, y_col="y", last="30D", point_size=48)
    plot_anomaly_types_by_year(ts_df, anomalies, y_col="y", ncols=2)



    # 4) Forecasting (daily, 2025) 
    _, forecast_df, true_2025_df = train_and_forecast_nhits(ts_df)

    # 5) Plot forecast vs truth
    plot_forecast_vs_true(forecast_df, true_2025_df)

    pred_series_df = build_series_from_forecast(forecast_df)  # ['ds','y'] from forecast
    pred_anoms, top_pred = detect_anomalies(
        pred_series_df,
        y_col="y",
        z_window=14, z_min_periods=7, z_thresh=3.0,      
        iso_contamination=0.02, with_context=True, top_k=20
    )
    
    plot_prediction_with_anomaly_types(
        pred_series_df,
        pred_anoms,
        true_df=true_2025_df[["ds","y"]],
        point_size=42,
        title="NHITS prediction vs truth with anomaly types (2025)"
    )

    print("END")


if __name__ == "__main__":
    main()

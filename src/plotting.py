import matplotlib.pyplot as plt

def plot_forecast_vs_true(forecast_df, true_df, label='NHITS'):
    """
    Plot forecast vs. true values over time.

    Parameters:
        forecast_df (pd.DataFrame): with columns ['ds', label]
        true_df (pd.DataFrame): with columns ['ds', 'y']
        label (str): name of the forecast column in forecast_df (default: 'total')
    """
    plt.figure(figsize=(12, 5))
    plt.plot(true_df['ds'], true_df['y'], label='True', linewidth=2)
    plt.plot(forecast_df['ds'], forecast_df[label], label='Forecast', linestyle='--')
    plt.title("Forecast vs. True Daily Event Counts (2025)")
    plt.xlabel("Date")
    plt.ylabel("Event Count")
    plt.legend()
    plt.tight_layout()
    plt.show()

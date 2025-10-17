# Instagram Behavior Analysis — Dashboard & Models

Minimal MVP to explore Instagram export data with a Dash/Plotly dashboard and baseline forecasting + anomaly detection.

## Quickstart

pip install -r requirements.txt

# Run dashboard
python -m dash_app.app
# Default: http://127.0.0.1:8050

## Structure

- dash_app/
  - app.py
  - layout.py
  - callbacks.py
  - plotting.py
  - plotly_theme.py
- src/
  - data_loader.py
  - models/
    - nhits_baseline.py
    - isolation_forest.py
    - evaluation.py
- notebooks/
  - 01_exploration.ipynb
- data/
  - raw/ (ignored)
  - processed/ (ignored)

## Configuration

- Data directory:
  - Defaults to `data/raw/`
  - Can be changed in `src/data_loader.py`
- Plot theme:
  - Light theme defined in `dash_app/plotly_theme.py`

## Features (MVP)

- **Dashboard**
  - Base layout using Dash
  - Filters: date range and event type
  - Time series plot with Plotly
- **Models**
  - NHITS baseline for forecasting
  - IsolationForest for anomaly detection

  
## Privacy

Do not commit any personal Instagram data.  
Ensure `.gitignore` includes:

- data/raw/
- data/processed/

## Development Notes

Use Conventional Commits for messages  
(e.g., `feat(dash): add heatmap view`)






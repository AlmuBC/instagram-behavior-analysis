#!/bin/bash

mkdir -p data/raw
mkdir -p data/processed
mkdir -p notebooks
mkdir -p src
mkdir -p dash_app
mkdir -p models
mkdir -p reports/figures
mkdir -p reports/metrics

touch notebooks/01_exploration.ipynb
touch src/__init__.py
touch src/data_loader.py
touch src/feature_engineering.py
touch src/forecasting_model.py
touch src/utils.py
touch dash_app/app.py
touch dash_app/layout.py
touch dash_app/callbacks.py

echo "✔️ Project structure created successfully."

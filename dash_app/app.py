import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import json

# Helper function to parse Instagram JSON structure
def load_instagram_json(path, key):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)[key]
    rows = []
    for item in data:
        entry = item["string_list_data"][0]
        rows.append({
            "username": entry["value"],
            "timestamp": pd.to_datetime(entry["timestamp"], unit="s")
        })
    return pd.DataFrame(rows)

# Load data from raw folder
df_following = load_instagram_json("data/raw/followers_and_following/following.json", "relationships_following")
df_unfollow = load_instagram_json("data/raw/followers_and_following/recently_unfollowed_profiles.json", "relationships_unfollowed_users")

# Extract month as string (avoids Period objects)
df_following["month"] = df_following["timestamp"].dt.to_period("M").astype(str)

# Aggregate counts by month
follows_per_month = df_following.groupby("month").size().reset_index(name="new_follows")

# Create charts
fig_follows = px.line(follows_per_month, x="month", y="new_follows", title="New follows per month")

# Dash app definition
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Instagram Follow Activity Dashboard"),
    dcc.Graph(figure=fig_follows),
])

if __name__ == "__main__":
    app.run(debug=True)

from dash.dependencies import Input, Output
from utils import load_story_likes, filter_by_date
import plotly.express as px
import pandas as pd

def register_callbacks(app):
    
    # CALLBACK:  story likes line

    @app.callback(
        Output('story-likes-line', 'figure'),
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date')]
    )
    def update_story_likes_line(start_date, end_date):
        df = load_story_likes()
        print("Total registros cargados:", len(df))
        print("Rango recibido:", start_date, "→", end_date)

        if not start_date or not end_date:
            filtered_df = df
        else:
            filtered_df = df[
                (df['timestamp'] >= pd.to_datetime(start_date)) &
                (df['timestamp'] <= pd.to_datetime(end_date))
            ]

        print("Filtrados:", len(filtered_df))

        if filtered_df.empty:
            fig = px.line(title="No data in selected range")
            fig.add_annotation(text="No story likes found in this period",
                               xref="paper", yref="paper",
                               showarrow=False, font=dict(size=20))
            return fig

        if 'month' not in filtered_df.columns:
            filtered_df["month"] = filtered_df["timestamp"].dt.to_period("M").astype(str)

        likes_month = filtered_df.groupby("month").size().reset_index(name="n_likes")

        fig = px.line(likes_month, x="month", y="n_likes", title="Story Likes per Month")
        return fig
    
    # CALLBACK: Heatmap  story likes
    @app.callback(
        Output('story-likes-heatmap', 'figure'),
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date')]
    )
    def update_story_likes_heatmap(start_date, end_date):
        df = load_story_likes()

        if not start_date or not end_date:
            filtered_df = df
        else:
            filtered_df = df[
                (df['timestamp'] >= pd.to_datetime(start_date)) &
                (df['timestamp'] <= pd.to_datetime(end_date))
            ]

        if filtered_df.empty:
            fig = px.imshow([[0]], title="No data for heatmap")
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            fig.add_annotation(text="No story likes found in this period",
                               xref="paper", yref="paper",
                               showarrow=False, font=dict(size=18))
            return fig

        # Añadir columnas necesarias si no están
        if 'day' not in filtered_df.columns:
            filtered_df["day"] = filtered_df["timestamp"].dt.day_name()
        if 'hour' not in filtered_df.columns:
            filtered_df["hour"] = filtered_df["timestamp"].dt.hour

        heatmap_data = filtered_df.groupby(["day", "hour"]).size().reset_index(name="n_likes")

        # Ordenar días para asegurar consistencia
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data["day"] = pd.Categorical(heatmap_data["day"], categories=day_order, ordered=True)
        heatmap_pivot = heatmap_data.pivot(index="day", columns="hour", values="n_likes").fillna(0)

        fig = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hour", y="Day", color="Likes"),
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            title="Heatmap of Story Likes by Day and Hour"
        )
        return fig
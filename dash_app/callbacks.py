from dash.dependencies import Input, Output
from utils import load_story_likes, filter_by_date
import plotly.express as px
import pandas as pd
from plotly_theme import SEQ_FUCHSIA
import random
from dash import Input, Output, State, html



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

        # Agrupar por día y hora
        heatmap_data = filtered_df.groupby(["day", "hour"]).size().reset_index(name="n_likes")

        # Ordenar días manualmente
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data["day"] = pd.Categorical(heatmap_data["day"], categories=day_order, ordered=True)

        # Pivot → matriz día x hora
        heatmap_pivot = heatmap_data.pivot(index="day", columns="hour", values="n_likes").fillna(0)

        # Visualización 
        fig = px.imshow(
            heatmap_pivot.values,
            labels=dict(x="Hour", y="Day", color="Likes"),
            x=heatmap_pivot.columns.tolist(),
            y=heatmap_pivot.index.tolist(),
            title="Heatmap of Story Likes by Day and Hour",
            aspect="auto",
            color_continuous_scale= SEQ_FUCHSIA
        )
        fig.update_layout(margin=dict(t=50, b=50, l=50, r=50))
        return fig
    
    
    @app.callback(
        Output("random-topic-output", "children"),
        Input("btn-random", "n_clicks"),
        State("n-random-dropdown", "value"),
        prevent_initial_call=True
    )
    def pick_random_topics(n_clicks, n):
        from utils import load_recommended_topics
        import random

        words, _ = load_recommended_topics()

        if not words:
            return html.Div("No topics available.")

        n = min(n, len(words))
        selected = random.sample(words, n)

        return [
            html.Div(
                w,
                style={
                    "backgroundColor": "#F6C4D9",     # rosa claro
                    "padding": "6px 12px",
                    "borderRadius": "16px",
                    "fontWeight": "bold",
                    "color": "#1F2937",
                    "boxShadow": "1px 1px 3px rgba(0,0,0,0.1)"
                }
            )
            for w in selected
        ]
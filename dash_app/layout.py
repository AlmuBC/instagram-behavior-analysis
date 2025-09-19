from dash import dcc, html

import pandas as pd
from utils import load_story_likes  # o donde tengas los datos

# Cargar datos para establecer rango válido
df_story_likes = load_story_likes()

date_filter = html.Div([
    dcc.DatePickerRange(
        id='date-picker-range',
        display_format='YYYY-MM-DD',
        start_date=df_story_likes['timestamp'].min(),
        end_date=df_story_likes['timestamp'].max(),
        min_date_allowed=df_story_likes['timestamp'].min(),
        max_date_allowed=df_story_likes['timestamp'].max(),
        style={'margin': '20px'}
    )
])

def serve_layout(fig_follows, fig_likes, fig_messages_month, fig_hour_block,fig_messages_heatmap,
                 fig_advertisers_intersect,fig_story_like_trend, fig_story_like_heatmap):
    return html.Div([
        html.H1("Instagram Activity Dashboard"),
        date_filter,
        html.Div([
            html.H2("Follow activity"),
            dcc.Graph(figure=fig_follows),
        ]),

        html.Div([
            html.H2("Likes activity"),
            dcc.Graph(figure=fig_likes),
        ]),
            html.Div([
            html.H2("Messages per month"),
            dcc.Graph(figure=fig_messages_month),
        ]),

        html.Div([
            html.H2("Messages by hour block per month"),
            dcc.Graph(figure=fig_hour_block),
        ]),
        html.Div([
            html.H2("Messages heatmap (Day vs Hour)"),
            dcc.Graph(figure=fig_messages_heatmap),
        ]),
        html.Div([
            html.H2("Cross-analysis: advertisers who showed you ads"),
            dcc.Graph(figure=fig_advertisers_intersect),
        ]),
        html.Div([
            dcc.Graph(id='story-likes-line', figure=fig_story_like_trend),
            dcc.Graph(id='story-likes-heatmap', figure=fig_story_like_heatmap)
        ], style={'display': 'flex', 'justify-content': 'space-between'})


    ])

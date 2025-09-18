from dash import dcc, html

def serve_layout(fig_follows, fig_likes, fig_messages_month, fig_hour_block,fig_messages_heatmap,
                 fig_advertisers_intersect,fig_story_like_trend, fig_story_like_heatmap):
    return html.Div([
        html.H1("Instagram Activity Dashboard"),
        
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
        html.H2("Story Likes Over Time"),
        dcc.Graph(figure=fig_story_like_trend),
        ]),


        html.Div([
        html.H2("Heatmap of Story Likes by Day and Hour"),
        dcc.Graph(figure=fig_story_like_heatmap),
        ])


    ])

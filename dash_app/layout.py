from dash import dcc, html

def serve_layout(fig_follows, fig_likes, fig_messages_month, fig_hour_block):
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



    ])

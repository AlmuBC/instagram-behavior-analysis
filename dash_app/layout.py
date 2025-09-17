from dash import dcc, html

def serve_layout(fig_follows, fig_likes):
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
    ])

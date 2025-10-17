"""
Register a Plotly template that matches our dashboard palette.
Usage:
    from plotly_theme import register_plotly_template, PALETTE, QUALITATIVE, SEQ_FUCHSIA
    register_plotly_template()  # sets default
    # Example:
    import plotly.express as px
    fig = px.bar(df, x="x", y="y", color="group",
                 color_discrete_sequence=QUALITATIVE)
    fig.show()
"""
import plotly.io as pio
import plotly.graph_objects as go

PALETTE = {
  "bg": "#FFFFFF",
  "surface": "#FFFFFF",
  "text": "#1F2937",
  "muted_text": "#4B5563",
  "primary": "#E63878",
  "secondary": "#D4E5F3",
  "accent1": "#F6C4D9",
  "accent2": "#EAE6AC",
  "border": "#EAE6AC",
  "grid": "#E8E3DA"
}

# Qualitative sequence for discrete series (order matters)
QUALITATIVE = [
    PALETTE["primary"],
    PALETTE["accent1"],
    PALETTE["secondary"],
    PALETTE["accent2"],
    "#8E2551"  # deep fuchsia for extra contrast if needed
]

# Sequential scale for heatmaps/continuous metrics (celeste -> rosa -> fucsia)
SEQ_FUCHSIA = [
    [0.0, PALETTE["secondary"]],
    [0.5, PALETTE["accent1"]],
    [1.0, PALETTE["primary"]],
]

def register_plotly_template(name: str = "almu"):
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["surface"],
        font=dict(family="Inter, Segoe UI, system-ui, -apple-system, sans-serif",
                  color=PALETTE["text"]),
        colorway=QUALITATIVE,
        xaxis=dict(gridcolor=PALETTE["grid"], zerolinecolor=PALETTE["grid"]),
        yaxis=dict(gridcolor=PALETTE["grid"], zerolinecolor=PALETTE["grid"]),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PALETTE["surface"], font_color=PALETTE["text"])
    )
    pio.templates[name] = template
    pio.templates.default = name
    # Also set px defaults if user imports plotly.express later
    try:
        import plotly.express as px
        px.defaults.template = name
        px.defaults.color_discrete_sequence = QUALITATIVE
        px.defaults.color_continuous_scale = SEQ_FUCHSIA
    except Exception:
        pass

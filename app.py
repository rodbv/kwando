import panel as pn

# Create a very simple app
app = pn.Column(
    pn.pane.Markdown("# Hello from KWANDO!"),
    pn.pane.Markdown("Panel is working in Binder!"),
)

# Make it servable
app.servable()

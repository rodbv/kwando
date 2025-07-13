import panel as pn

# Create a simple test app
app = pn.Column(
    pn.pane.Markdown("# KWANDO Test"),
    pn.pane.Markdown("If you can see this, Panel is working!"),
    pn.widgets.Button(name="Test Button", button_type="primary"),
)

# Make it servable
app.servable()

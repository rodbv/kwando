import panel as pn
import pandas as pd
from monte_carlo import forecast_days_for_work_items, forecast_work_items_in_period
from datetime import datetime, timedelta
import argparse

# Initialize Panel with template support
pn.extension("tabulator", "ace")

# Set theme colors
ACCENT_COLOR = "#2c5282"  # A more elegant navy blue
ACCENT_COLOR_DARK = "#90cdf4"  # Lighter blue for dark mode


def get_next_business_day():
    """Calculate the next business day from today"""
    next_day = datetime.now() + timedelta(days=1)
    # Keep adding days until we get a weekday (Monday = 0, Sunday = 6)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day.date()


# Create widgets for both simulation types
simulation_type = pn.widgets.RadioButtonGroup(
    name="Simulation Type",
    options=["Forecast by Work Items", "Forecast by Time Period"],
    button_type="primary",
    value="Forecast by Work Items",
    orientation="vertical",  # Make buttons stack vertically
    button_style="solid",  # Use proper button style
    margin=(0, 0, 15, 0),  # Add margin below each button
)

# Widgets for work items simulation
num_cards_slider = pn.widgets.IntSlider(
    name="Number of Work Items",
    start=3,
    end=50,
    value=10,
    step=1,
    width=400,
)

start_date_picker = pn.widgets.DatePicker(
    name="Start Date",
    value=get_next_business_day(),
    start=datetime.now().date(),
    width=200,
)

# Widgets for time period simulation
period_start_date = pn.widgets.DatePicker(
    name="Period Start Date",
    value=get_next_business_day(),
    start=datetime.now().date(),
    width=200,
)

period_end_date = pn.widgets.DatePicker(
    name="Period End Date",
    value=(datetime.now() + timedelta(days=30)).date(),
    start=datetime.now().date(),
    width=200,
)


# Function to update results based on work items simulation
def update_work_items_results(num_cards, start_date):
    try:
        results = forecast_days_for_work_items(
            num_work_items=num_cards,
            filename="data/data.csv",
            num_iterations=5000,
            start_date=start_date,
        )

        table_data = []
        for percentile, date in results["percentile_dates"].items():
            table_data.append(
                {
                    "Percentile": f"{percentile}%",
                    "Completion Date": date,
                    "Days from Start": f"{results['percentiles'][percentile]:.1f}",
                }
            )
        df = pd.DataFrame(table_data)

        return f"""
## Monte Carlo Simulation Results - Work Items Forecast

**Based on our historical data:**
- We are **80% confident** that {num_cards} work items will be completed by {results["percentile_dates"]["80"]} ({results["percentiles"]["80"]:.0f} days)
- We are **90% confident** that they will be completed by {results["percentile_dates"]["90"]} ({results["percentiles"]["90"]:.0f} days)

{df.to_markdown(index=False)}
"""
    except Exception as e:
        return f"## Error\n\nAn error occurred: {str(e)}"


# Function to update results based on time period simulation
def update_period_results(start_date, end_date):
    try:
        results = forecast_work_items_in_period(
            start_date=start_date,
            end_date=end_date,
            filename="data/data.csv",
            num_iterations=5000,
        )

        # Calculate number of days in the period
        start_ts = pd.Timestamp(results["start_date"])
        end_ts = pd.Timestamp(results["end_date"])
        days_between = (end_ts - start_ts).days

        return f"""
## Monte Carlo Simulation Results - Time Period Forecast

**In {days_between} days (from {results["start_date"]} to {results["end_date"]}):**
- We are **80% confident** that we can complete at least {results["percentiles"]["80"]:.0f} work items
- We are **90% confident** that we can complete at least {results["percentiles"]["90"]:.0f} work items

**Detailed Forecast (minimum number of items):**
- 70% confidence: {results["percentiles"]["70"]:.1f} items
- 80% confidence: {results["percentiles"]["80"]:.1f} items
- 90% confidence: {results["percentiles"]["90"]:.1f} items
- 95% confidence: {results["percentiles"]["95"]:.1f} items
- 98% confidence: {results["percentiles"]["98"]:.1f} items

*Note: This forecast shows how many items we expect to complete within the fixed time period. Higher confidence levels mean we're more certain about completing at least that many items.*
"""
    except Exception as e:
        return f"## Error\n\nAn error occurred: {str(e)}"


# Create the reactive functions that update based on widget changes
@pn.depends(num_cards_slider.param.value, start_date_picker.param.value)
def get_work_items_results(num_cards, start_date):
    return update_work_items_results(num_cards, start_date)


@pn.depends(period_start_date.param.value, period_end_date.param.value)
def get_period_results(start_date, end_date):
    return update_period_results(start_date, end_date)


# Create dynamic Panel panes for displaying results
work_items_results = pn.bind(pn.pane.Markdown, get_work_items_results)
period_results = pn.bind(pn.pane.Markdown, get_period_results)


# Function to show/hide widgets based on simulation type
@pn.depends(simulation_type.param.value)
def get_simulation_widgets(sim_type):
    if sim_type == "Forecast by Work Items":
        return pn.Column(
            "## Work Items Simulation",
            "Adjust the parameters below to forecast completion dates:",
            num_cards_slider,
            start_date_picker,
            work_items_results,
        )
    else:
        return pn.Column(
            "## Time Period Simulation",
            "Adjust the date range to forecast work items completion:",
            period_start_date,
            period_end_date,
            period_results,
        )


# Sidebar content
about_text = pn.pane.Markdown(
    """
### About

This dashboard uses Monte Carlo simulation to forecast either:

1. When a specific number of work items will be completed
2. How many work items can be completed in a given time period

The forecasts are based on historical completion data.
""",
    styles={"font-size": "14px"},
)  # Note: styles not style

sidebar = pn.Column(
    pn.pane.Markdown("## Simulation Type", styles={"margin-bottom": "10px"}),
    pn.pane.Markdown(
        "Choose the type of simulation to run:", styles={"margin-bottom": "15px"}
    ),
    simulation_type,
    pn.layout.Spacer(height=30),  # More space after buttons
    about_text,
    margin=(0, 0, 10, 0),  # Add margin between elements
)

# Main content
main = [
    pn.pane.Markdown("## Work Item Completion Forecast"),
    pn.pane.Markdown(
        "This simulation helps answer either 'When will it be done?' or 'How much can we do?' by analyzing historical completion data and running Monte Carlo simulations."
    ),
    get_simulation_widgets,
]

# Create the template with dark mode support
template = pn.template.FastListTemplate(
    title="When will it be done?",
    sidebar=sidebar,
    main=main,
    accent_base_color=ACCENT_COLOR,
    header_background=ACCENT_COLOR,
    theme_toggle=True,
    theme="default",
)


# Update accent color based on theme
def update_theme(event):
    if event.new == "dark":
        template.accent_base_color = ACCENT_COLOR_DARK
        template.header_background = ACCENT_COLOR_DARK
    else:
        template.accent_base_color = ACCENT_COLOR
        template.header_background = ACCENT_COLOR


template.param.watch(update_theme, "theme")

# Mark the template as servable
template.servable()

# Add development mode support
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    template.show(port=5006, dev=args.dev)

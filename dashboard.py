import panel as pn
import pandas as pd
from monte_carlo import forecast_days_for_work_items
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


# Create widgets
num_cards_slider = pn.widgets.IntSlider(
    name="Number of Work Items",
    start=3,
    end=50,
    value=10,
    step=1,
    width=400,  # Set a fixed width for better alignment
)

start_date_picker = pn.widgets.DatePicker(
    name="Start Date",
    value=get_next_business_day(),
    start=datetime.now().date(),
    width=200,  # Set a fixed width for better alignment
)


# Function to update results based on slider value and start date
def update_results(num_cards, start_date):
    try:
        # Run the Monte Carlo simulation
        results = forecast_days_for_work_items(
            num_work_items=num_cards,
            filename="data/data.csv",
            num_iterations=5000,
            start_date=start_date,
        )

        # Create a table with the results
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

        # Format the results as markdown
        markdown_text = f"""
## Monte Carlo Simulation Results

**Parameters:**
- Number of work items: {num_cards}
- Number of iterations: {results["num_iterations"]}
- Start date: {results["start_date"]}

**Completion Date Forecasts:**

{df.to_markdown(index=False)}

**Summary:**
- **70% confidence**: {results["percentile_dates"]["70"]} ({results["percentiles"]["70"]:.1f} days)
- **80% confidence**: {results["percentile_dates"]["80"]} ({results["percentiles"]["80"]:.1f} days)
- **90% confidence**: {results["percentile_dates"]["90"]} ({results["percentiles"]["90"]:.1f} days)
- **95% confidence**: {results["percentile_dates"]["95"]} ({results["percentiles"]["95"]:.1f} days)
- **98% confidence**: {results["percentile_dates"]["98"]} ({results["percentiles"]["98"]:.1f} days)
"""
        return markdown_text
    except Exception as e:
        return f"## Error\n\nAn error occurred: {str(e)}"


# Create the reactive function that updates based on widget changes
@pn.depends(num_cards_slider.param.value, start_date_picker.param.value)
def get_results(num_cards, start_date):
    return update_results(num_cards, start_date)


# Create a dynamic Panel pane for displaying results
results_pane = pn.bind(pn.pane.Markdown, get_results)

# Sidebar content
sidebar = [
    "## Simulation Parameters",
    "Adjust the parameters below to update the forecast:",
    num_cards_slider,
    start_date_picker,
    "---",
    "### About",
    """This dashboard uses Monte Carlo simulation to forecast completion dates based on historical data.
    The forecast shows different confidence levels for when the work items will be completed.""",
]

# Main content
main = [
    pn.pane.Markdown("## Work Item Completion Forecast"),
    pn.pane.Markdown(
        "This simulation helps answer the question 'When will it be done?' by analyzing historical completion data and running Monte Carlo simulations to provide date ranges at different confidence levels."
    ),
    results_pane,
]

# Create the template with dark mode support
template = pn.template.FastListTemplate(
    title="When will it be done?",
    sidebar=sidebar,
    main=main,
    accent_base_color=ACCENT_COLOR,
    header_background=ACCENT_COLOR,
    theme_toggle=True,
    theme="default",  # Changed from "light" to "default"
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

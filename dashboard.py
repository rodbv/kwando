import panel as pn
import pandas as pd
from monte_carlo import (
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_next_business_day,
)
from datetime import datetime, timedelta
import argparse

# Initialize Panel with template support
pn.extension("tabulator", "ace")

# Set theme colors
ACCENT_COLOR = "#2c5282"  # A more elegant navy blue
ACCENT_COLOR_DARK = "#90cdf4"  # Lighter blue for dark mode

# Create widgets for both simulation types
when_button = pn.widgets.Button(
    name="When will it be done?", button_type="primary", width=200
)

how_many_button = pn.widgets.Button(
    name="How many items?", button_type="primary", width=200
)

# Add data source button and state management
data_source_button = pn.widgets.Button(
    name="📊 Data Source", button_type="default", width=200
)

# File picker widget and default file text
file_input = pn.widgets.FileInput(name="Upload Custom CSV")
default_file_text = pn.pane.Markdown("**Current data:** data/data.csv (default)")

# Global state for data source
current_data_file = "data/data.csv"


# Function to load and clean data from a file
def load_and_clean_data(filename="data/data.csv"):
    try:
        df = pd.read_csv(filename, parse_dates=["created_date"])
        # Clean the data
        cleaned = df[
            (df["created_date"] > "2018-01-01") & (df["cycle_time_days"] > -1)
        ].copy()
        return cleaned
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not load data: {str(e)}"]})


# Function to calculate and display data statistics
def get_data_stats_md(df):
    if "Error" in df.columns or df.empty:
        return "### Data Statistics\n\nCould not calculate statistics. Please check the data file."

    try:
        # Perform calculations
        min_date = df["created_date"].min().strftime("%Y-%m-%d")
        max_date = df["created_date"].max().strftime("%Y-%m-%d")
        min_cycle_time = df["cycle_time_days"].min()
        max_cycle_time = df["cycle_time_days"].max()
        median_cycle_time = df["cycle_time_days"].median()
        total_items = len(df)
        num_groups = df["grp"].nunique()

        # Format as a Markdown string
        stats_md = f"""
### Data Statistics
- **Total Work Items:** {total_items}
- **Number of Groups:** {num_groups}
- **Date Range:** {min_date} to {max_date}
- **Min Cycle Time:** `{min_cycle_time}` days
- **Max Cycle Time:** `{max_cycle_time}` days
- **Median Cycle Time:** `{median_cycle_time:.1f}` days
"""
        return stats_md
    except Exception as e:
        return (
            f"### Error Calculating Stats\n\nCould not calculate statistics: {str(e)}"
        )


# The data preview pane, created once and updated reactively
initial_data = load_and_clean_data()
data_preview_pane = pn.pane.DataFrame(
    initial_data.head(100), name="Data Preview", height=400, sizing_mode="stretch_width"
)
data_stats_pane = pn.pane.Markdown(
    get_data_stats_md(initial_data), sizing_mode="stretch_width"
)


# Function to handle file upload and update global state
def handle_file_upload(event):
    global current_data_file
    if event.new is not None and len(event.new) > 0:
        # Save uploaded file
        with open("temp_upload.csv", "wb") as f:
            f.write(event.new)
        current_data_file = "temp_upload.csv"
        # Load new data
        full_df = load_and_clean_data(current_data_file)
        # Update preview pane reactively
        data_preview_pane.object = (
            full_df.head(100) if "Error" not in full_df.columns else full_df
        )
        data_stats_pane.object = get_data_stats_md(full_df)
        # Update the text
        default_file_text.object = f"**Current data:** {current_data_file} (uploaded)"
    else:
        # Reset to default
        current_data_file = "data/data.csv"
        # Load default data
        full_df = load_and_clean_data(current_data_file)
        # Update preview pane reactively
        data_preview_pane.object = (
            full_df.head(100) if "Error" not in full_df.columns else full_df
        )
        data_stats_pane.object = get_data_stats_md(full_df)
        default_file_text.object = "**Current data:** data/data.csv (default)"


# Link file input to handler
file_input.param.watch(handle_file_upload, "value")

# Create a parameter to track which simulation is active
active_simulation = pn.widgets.Select(
    name="Active Simulation",
    options=["When will it be done?", "How many items?", "Data Source"],
    value="When will it be done?",
    visible=False,  # Hide this control, we'll use it just for state
)

# Create a help button that shows/hides the explanation
help_visible = pn.widgets.Toggle(
    name="📚 Learn about Monte Carlo Simulation",
    value=False,
    button_type="primary",
    width=300,
)


# Update active simulation when buttons are clicked
def set_when_active(event):
    help_visible.value = False  # Reset help toggle
    active_simulation.value = "When will it be done?"


def set_how_many_active(event):
    help_visible.value = False  # Reset help toggle
    active_simulation.value = "How many items?"


def set_data_source_active(event):
    help_visible.value = False  # Reset help toggle
    active_simulation.value = "Data Source"


when_button.on_click(set_when_active)
how_many_button.on_click(set_how_many_active)
data_source_button.on_click(set_data_source_active)


# Update button appearance based on active simulation
@pn.depends(active_simulation.param.value, help_visible.param.value)
def update_button_styles(active, show_help):
    when_button.button_type = (
        "primary" if active == "When will it be done?" and not show_help else "default"
    )
    how_many_button.button_type = (
        "primary" if active == "How many items?" and not show_help else "default"
    )
    data_source_button.button_type = (
        "primary" if active == "Data Source" and not show_help else "default"
    )
    return ""


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
            filename=current_data_file,
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
            filename=current_data_file,
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


# Create help text with Monte Carlo explanation
help_text = pn.pane.Markdown(
    """
## How These Forecasts Work

### What is Monte Carlo Simulation?
Monte Carlo simulation is a mathematical technique that helps us make predictions in uncertain environments. In software delivery, we use it to forecast delivery dates or team capacity by:
1. Looking at our historical completion data (how long items actually took)
2. Running thousands of "simulations" using random samples from this history
3. Analyzing the results to provide confidence levels

### What Data Are We Using?
- We analyze your team's actual cycle times (how long items took from start to finish)
- Each work item's cycle time captures the full "system time" including delays, dependencies, and rework
- We use this real data rather than estimates because it includes all the natural variation in your delivery system

### How to Read the Results
- The forecasts show different confidence levels (70% to 98%)
- An "80% confidence" means that, based on your historical performance, you have an 80% chance of hitting that target
- Higher confidence levels (90%, 95%) give you more certainty but predict longer durations
- Lower confidence levels (70%, 80%) are more aggressive but carry more risk

### Key Concepts
1. **Using History vs Estimates**: Rather than relying on up-front estimates, we use your actual delivery history. This captures your team's real-world performance including all the normal delays and uncertainties.

2. **Probabilistic vs Deterministic**: Instead of a single date, we provide a range of possibilities with confidence levels. This better reflects the inherent uncertainty in knowledge work.

3. **System Thinking**: The cycle times reflect your entire delivery system - not just coding time but also reviews, testing, deployments, and any delays. This gives you a more realistic picture of delivery times.

### When to Use Each Simulation
- **"When will it be done?"** - Use when you have a specific number of work items and need to forecast completion dates
- **"How many items?"** - Use when you have a time period and need to forecast how many items you can complete

### Making Better Decisions
- Use higher confidence levels (90%+) for important commitments or dependencies
- Use lower confidence levels (70-80%) for internal planning or less critical items
- Look for ways to reduce your cycle times to improve all forecasts
- Remember: the goal is to make informed decisions, not to get exact predictions

### Learn More

**Books by Daniel Vacanti:**
- <a href="https://actionableagile.com/books/aamfp" target="_blank">Actionable Agile Metrics for Predictability</a> - The definitive guide to flow metrics and analytics
- <a href="https://leanpub.com/whenwillitbedone" target="_blank">When Will It Be Done?</a> - Lean-Agile Forecasting to Answer Your Customers' Most Important Question
- <a href="https://actionableagile.com/books/aamfp-vol2" target="_blank">Actionable Agile Metrics Volume II</a> - Advanced Topics in Predictability

**Additional Resources:**
- <a href="https://prokanban.org/" target="_blank">ProKanban.org</a> - Community for learning about Kanban and flow metrics
- <a href="https://www.youtube.com/watch?v=j1FTNVRkJYg" target="_blank">Why Monte Carlo Simulation?</a> - Video explanation by Daniel Vacanti

*Based on concepts from ActionableAgile™ and "Actionable Agile Metrics for Predictability" by Daniel Vacanti.*
"""
)


# Create a dynamic panel with smooth transitions
@pn.depends(help_visible.param.value, active_simulation.param.value)
def get_main_content(show_help, sim_type):
    # Create the content based on current state
    if show_help:
        content = help_text
        title = "About Monte Carlo Simulation"
    else:
        if sim_type == "When will it be done?":
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        "### Parameters",
                        num_cards_slider,
                        start_date_picker,
                        sizing_mode="stretch_width",
                    ),
                ),
                work_items_results,
            )
            title = "When will these work items be done?"
        elif sim_type == "How many items?":
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        "### Parameters",
                        period_start_date,
                        period_end_date,
                        sizing_mode="stretch_width",
                    ),
                ),
                period_results,
            )
            title = "How many items can we complete?"
        else:  # Data Source
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        "### Data Source Configuration",
                        default_file_text,
                        file_input,
                        sizing_mode="stretch_width",
                    ),
                ),
                pn.layout.Spacer(height=20),
                pn.Row(
                    pn.Column(
                        pn.pane.Markdown("### Data Preview (First 100 rows)"),
                        data_preview_pane,
                        sizing_mode="stretch_width",
                    ),
                    data_stats_pane,
                    sizing_mode="stretch_width",
                ),
                pn.layout.Spacer(height=30),
                pn.pane.Markdown("**Upload a CSV file with the following columns:**"),
                pn.pane.Markdown("- `id`: Unique identifier for each work item"),
                pn.pane.Markdown("- `grp`: Group/project identifier"),
                pn.pane.Markdown(
                    "- `cycle_time_days`: Time taken to complete the work item"
                ),
                pn.pane.Markdown("- `created_date`: When the work item was created"),
            )
            title = "Data Source"

    # Wrap content in a card with smooth transition
    return pn.Card(
        pn.Column(
            pn.pane.Markdown(f"# {title}"),
            content,
        ),
        styles={"border": "1px solid #e2e8f0", "border-radius": "8px"},
        margin=(10, 0),
    )


# Create button column with spacing
button_column = pn.Column(
    when_button,
    pn.layout.Spacer(height=20),  # Add 20px space between buttons
    how_many_button,
    pn.layout.Spacer(height=20),  # Add space between buttons and data source button
    data_source_button,
)

# About section for sidebar
about_text = pn.pane.Markdown(
    """
### About

This dashboard uses Monte Carlo simulation to forecast either:

1. When a specific number of work items will be completed
2. How many work items can be completed in a given time period

The forecasts are based on historical completion data.
""",
    styles={"font-size": "14px"},
)

# Sidebar with simulation type selection, basic about, and help button
sidebar = pn.Column(
    pn.pane.Markdown("## Simulation Type", styles={"margin-bottom": "10px"}),
    pn.pane.Markdown(
        "Choose the type of simulation to run:", styles={"margin-bottom": "15px"}
    ),
    button_column,
    active_simulation,  # This will be hidden but needed for state
    update_button_styles,  # This will update button styles
    pn.layout.Spacer(height=30),
    about_text,
    pn.layout.Spacer(height=10),
    help_visible,
    margin=(0, 0, 10, 0),
)

# Main content with smooth transitions
main = pn.Column(
    get_main_content,
    sizing_mode="stretch_both",  # Make it fill available space
    styles={
        "padding": "20px",  # Add some padding
        "background": "transparent",  # Transparent background
    },
)

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

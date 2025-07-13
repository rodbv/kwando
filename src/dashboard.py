import argparse
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import panel as pn
from bokeh.models import Label, Span
from bokeh.plotting import figure
from monte_carlo import (
    convert_dates_to_cycle_time,
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_next_business_day,
)

# Initialize Panel with template support
pn.extension("tabulator", "ace")

# Set theme colors
ACCENT_COLOR = "#2c5282"
ACCENT_COLOR_DARK = "#90cdf4"

# Define constants for button/page texts
DATA_SOURCE_LABEL = "📁 Data Source"
WHEN_LABEL = "⏰ When will it be done?"
HOW_MANY_LABEL = "📊 How many items?"

# Create widgets for both simulation types
when_button = pn.widgets.Button(name=WHEN_LABEL, button_type="primary", width=200)

how_many_button = pn.widgets.Button(
    name=HOW_MANY_LABEL, button_type="primary", width=200
)

# Add data source button and state management
data_source_button = pn.widgets.Button(
    name=DATA_SOURCE_LABEL, button_type="default", width=200
)

# File picker widget and default file text
# Remove file_input and any upload logic
# Only keep file_selector for choosing CSVs from the data directory

# List all CSV files in the data/ directory
csv_files = [f"data/{f}" for f in os.listdir("data") if f.endswith(".csv")]

# File selector widget
file_selector = pn.widgets.Select(
    name="Choose CSV file",
    options=csv_files,
    value=(
        "data/data_clean.csv"
        if "data/data_clean.csv" in csv_files
        else (csv_files[0] if csv_files else None)
    ),
)

# Add file upload widget
file_input = pn.widgets.FileInput(accept=".csv", name="Upload CSV")


def handle_file_upload(event):
    if file_input.value is not None and file_input.filename is not None:
        filename = str(file_input.filename)
        value = file_input.value
        if isinstance(value, bytes):
            save_path = os.path.join("data", filename)
            with open(save_path, "wb") as f:
                f.write(value)
            # Refresh file selector options
            csv_files = [f"data/{f}" for f in os.listdir("data") if f.endswith(".csv")]
            file_selector.options = csv_files
            file_selector.value = f"data/{filename}"


file_input.param.watch(handle_file_upload, "value")


# Add a reusable data cleaning/filtering function
def clean_and_filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame (no tag filtering anymore).
    """
    try:
        cleaned = df.copy()
        return cleaned
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not clean/filter data: {str(e)}"]})


def load_and_clean_data(filename: str) -> pd.DataFrame:
    """
    Load data from a CSV file and clean it (no tag filtering).
    Only supports new format (start_date, end_date).
    """
    try:
        df = pd.read_csv(filename)
        if "start_date" not in df.columns or "end_date" not in df.columns:
            return pd.DataFrame(
                {
                    "Error": [
                        "CSV must have start_date and end_date columns in ISO 8601 format."
                    ]
                }
            )
        df = convert_dates_to_cycle_time(df)
        return clean_and_filter_data(df)
    except pd.errors.ParserError as e:
        return pd.DataFrame({"Error": [f"Could not load data: {str(e)}"]})
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not load data: {str(e)}"]})


# Function to calculate and display data statistics
def get_data_stats_md(df):
    if "Error" in df.columns or df.empty:
        return "### Data Statistics\n\nCould not calculate statistics. Please check the data file."

    try:
        # Load the original unfiltered data to count invalid rows
        if not file_selector.value:
            return "### Data Statistics\n\nNo file selected."

        original_df = pd.read_csv(file_selector.value)

        # Count invalid rows (cycle_time_days <= 0)
        # Handle both old format (cycle_time_days) and new format (start_date, end_date)
        if "start_date" in original_df.columns and "end_date" in original_df.columns:
            # For new format, count rows with invalid dates
            invalid_dates = (
                pd.to_datetime(original_df["start_date"], errors="coerce").isna()
                | pd.to_datetime(original_df["end_date"], errors="coerce").isna()
            )
            invalid_cycle_time = invalid_dates.sum()
        else:
            invalid_cycle_time = 0

        # Count rows before min_date (2018-01-01) - removed since we're not treating this as invalid data

        # Perform calculations on the filtered data
        min_cycle_time = df["cycle_time_days"].min()
        max_cycle_time = df["cycle_time_days"].max()
        median_cycle_time = df["cycle_time_days"].median()
        total_items = len(df)
        total_original = len(original_df)

        # Format as a Markdown string
        stats_md = f"""
### Data Statistics
- **Total Work Items:** {total_items}
- **Min Cycle Time:** `{min_cycle_time}` days
- **Max Cycle Time:** `{max_cycle_time}` days
- **Median Cycle Time:** `{median_cycle_time:.1f}` days

### Data Quality
- **Original Rows:** {total_original}
- **Invalid Cycle Times (≤0):** {invalid_cycle_time}
- **Valid Rows Used:** {total_items}
"""
        return stats_md
    except Exception as e:
        return (
            f"### Error Calculating Stats\n\nCould not calculate statistics: {str(e)}"
        )


# The data preview pane, created once and updated reactively
if file_selector.value:
    initial_data = load_and_clean_data(file_selector.value)
else:
    initial_data = pd.DataFrame({"Info": ["No CSV file found in data/ directory."]})

data_preview_pane = pn.pane.DataFrame(
    initial_data.head(100) if file_selector.value else initial_data,
    name="Data Preview",
    height=400,
    width=500,
)
data_stats_pane = pn.pane.Markdown(
    (
        get_data_stats_md(initial_data)
        if file_selector.value
        else "### Data Statistics\n\nNo file available."
    ),
    sizing_mode="stretch_width",
)

# On startup, if no file is available, show a message
if not file_selector.value:
    data_preview_pane.object = pd.DataFrame(
        {"Info": ["No CSV file found in data/ directory."]}
    )
    data_stats_pane.object = "### Data Statistics\n\nNo file available."


# Function to handle file selection and update preview/stats


def handle_file_selection(event):
    if not file_selector.value:
        data_preview_pane.object = pd.DataFrame(
            {"Info": ["No CSV file selected or available in data/ directory."]}
        )
        data_stats_pane.object = "### Data Statistics\n\nNo file selected."
        return

    # Load data without tag filtering
    full_df = load_and_clean_data(file_selector.value)
    data_preview_pane.object = (
        full_df.head(100) if "Error" not in full_df.columns else full_df
    )
    data_stats_pane.object = get_data_stats_md(full_df)


file_selector.param.watch(handle_file_selection, "value")


# Create a parameter to track which simulation is active
active_simulation = pn.widgets.Select(
    name="Active Simulation",
    options=[DATA_SOURCE_LABEL, WHEN_LABEL, HOW_MANY_LABEL],
    value=DATA_SOURCE_LABEL,
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
    active_simulation.value = WHEN_LABEL


def set_how_many_active(event):
    help_visible.value = False  # Reset help toggle
    active_simulation.value = HOW_MANY_LABEL


def set_data_source_active(event):
    help_visible.value = False  # Reset help toggle
    active_simulation.value = DATA_SOURCE_LABEL


when_button.on_click(set_when_active)
how_many_button.on_click(set_how_many_active)
data_source_button.on_click(set_data_source_active)


# Update button appearance based on active simulation
@pn.depends(active_simulation.param.value, help_visible.param.value)
def update_button_styles(active, show_help):
    data_source_button.button_type = (
        "primary" if active == DATA_SOURCE_LABEL and not show_help else "default"
    )
    when_button.button_type = (
        "primary" if active == WHEN_LABEL and not show_help else "default"
    )
    how_many_button.button_type = (
        "primary" if active == HOW_MANY_LABEL and not show_help else "default"
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


# Remove any redundant comments and ensure both simulation result functions are clean


def make_histogram_bokeh_plot(simulated_durations, percentiles):
    if not simulated_durations:
        return pn.pane.Markdown("No simulation data available for histogram.")
    hist, edges = np.histogram(simulated_durations, bins=30)
    p = figure(
        title="Distribution of Simulated Completion Dates",
        width=700,
        height=250,
        x_axis_label="Days from Start",
        y_axis_label="Number of Simulations",
        tools="pan,box_zoom,reset,save",
    )
    p.quad(
        top=hist,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        color="#90cdf4",
        line_color="#2c5282",
        alpha=0.7,
    )
    for pct_str, color in zip(["80", "90"], ["orange", "red"], strict=False):
        if pct_str in percentiles:
            dur = float(percentiles[pct_str])
            vline = Span(
                location=dur,
                dimension="height",
                line_color=color,
                line_dash="dashed",
                line_width=2,
            )
            p.add_layout(vline)
            label = Label(
                x=dur + 2,
                y=max(hist) * 0.8,
                text=f"{pct_str}%",
                text_color=color,
                text_font_size="10pt",
                text_alpha=0.7,
                background_fill_alpha=0.0,
            )
            p.add_layout(label)
    return pn.pane.Bokeh(p)


def make_items_histogram_bokeh_plot(simulated_work_items, percentiles):
    if not simulated_work_items:
        return pn.pane.Markdown("No simulation data available for histogram.")
    hist, edges = np.histogram(
        simulated_work_items,
        bins=range(int(min(simulated_work_items)), int(max(simulated_work_items)) + 2),
    )
    p = figure(
        title="Distribution of Simulated Work Items Completed",
        width=700,
        height=250,
        x_axis_label="Number of Work Items Completed",
        y_axis_label="Number of Simulations",
        tools="pan,box_zoom,reset,save",
    )
    p.quad(
        top=hist,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        color="#90cdf4",
        line_color="#2c5282",
        alpha=0.7,
    )
    for pct_str, color in zip(["80", "90"], ["orange", "red"], strict=False):
        if pct_str in percentiles:
            items = float(percentiles[pct_str])
            vline = Span(
                location=items,
                dimension="height",
                line_color=color,
                line_dash="dashed",
                line_width=2,
            )
            p.add_layout(vline)
            label = Label(
                x=items + 0.2,
                y=max(hist) * 0.8,
                text=f"{pct_str}%",
                text_color=color,
                text_font_size="10pt",
                text_alpha=0.7,
                background_fill_alpha=0.0,
            )
            p.add_layout(label)
    return pn.pane.Bokeh(p)


def update_work_items_results_with_histogram(df, num_cards):
    try:
        results = forecast_days_for_work_items(
            df=df,
            num_work_items=num_cards,
            num_iterations=5000,
        )
        if not results or not results.get("percentile_dates"):
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nCould not generate a forecast. This is likely due to missing or invalid data in the source file. Please check the data and try again."
                )
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
        df_table = pd.DataFrame(table_data)
        table_md = df_table.to_markdown(index=False) if not df_table.empty else ""
        if table_md is None:
            table_md = ""
        hist_chart = make_histogram_bokeh_plot(
            results["simulated_durations"],
            results["percentiles"],
        )
        return pn.Column(
            hist_chart,
            pn.pane.Markdown(
                f"""
## Monte Carlo Simulation Results - Work Items Forecast

**Based on our historical data:**
- We are **80% confident** that {num_cards} work items will be completed by {results["percentile_dates"]["80"]} ({results["percentiles"]["80"]:.0f} days)
- We are **90% confident** that they will be completed by {results["percentile_dates"]["90"]} ({results["percentiles"]["90"]:.0f} days)

{table_md}
"""
            ),
        )
    except Exception as e:
        return pn.Column(pn.pane.Markdown(f"## Error\n\nAn error occurred: {str(e)}"))


def update_period_results_with_histogram(df, start_date, end_date):
    try:
        results = forecast_work_items_in_period(
            df=df,
            start_date=start_date,
            end_date=end_date,
            num_iterations=5000,
        )
        if not results or not results.get("percentiles"):
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nCould not generate a forecast. This is likely due to missing or invalid data in the source file. Please check the data and try again."
                )
            )
        start_ts = pd.Timestamp(results["start_date"])
        end_ts = pd.Timestamp(results["end_date"])
        days_between = (end_ts - start_ts).days
        hist_chart = make_items_histogram_bokeh_plot(
            results["simulated_work_items"],
            results["percentiles"],
        )
        return pn.Column(
            hist_chart,
            pn.pane.Markdown(
                f"""
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
            ),
        )
    except Exception as e:
        return pn.Column(pn.pane.Markdown(f"## Error\n\nAn error occurred: {str(e)}"))


# Create the reactive functions that update based on widget changes
@pn.depends(
    num_cards_slider.param.value,
    file_selector.param.value,
)
def get_work_items_results(num_cards, selected_file):
    df = data_preview_pane.object
    if not isinstance(df, pd.DataFrame):
        return pn.Column(pn.pane.Markdown("## Warning\n\nNo valid data loaded."))
    return update_work_items_results_with_histogram(df, num_cards)


# Replace get_period_results to use the new function
@pn.depends(
    period_start_date.param.value,
    period_end_date.param.value,
    file_selector.param.value,
)
def get_period_results(start_date, end_date, selected_file):
    df = data_preview_pane.object
    if not isinstance(df, pd.DataFrame):
        return pn.Column(pn.pane.Markdown("## Warning\n\nNo valid data loaded."))
    return update_period_results_with_histogram(df, start_date, end_date)


# Create dynamic Panel panes for displaying results
work_items_results = get_work_items_results
period_results = get_period_results


# Create reactive data source info
def get_data_source_info():
    if not file_selector.value:
        return pn.pane.Markdown("**Data Source:** No file selected")
    return pn.pane.Markdown(f"**Data Source:** {file_selector.value}")


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
    if show_help:
        content = help_text
        title = "About Monte Carlo Simulation"
    else:
        if sim_type == WHEN_LABEL:
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        get_data_source_info(),
                        num_cards_slider,
                        sizing_mode="stretch_width",
                    ),
                ),
                work_items_results,
            )
            title = WHEN_LABEL
        elif sim_type == HOW_MANY_LABEL:
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        get_data_source_info(),
                        period_start_date,
                        period_end_date,
                        sizing_mode="stretch_width",
                    ),
                ),
                period_results,
            )
            title = HOW_MANY_LABEL
        else:  # Data Source
            content = pn.Column(
                pn.Row(
                    pn.Column(
                        file_input,
                        file_selector,
                        pn.layout.Spacer(height=10),
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
                pn.pane.Markdown("**CSV file must have the following columns:**"),
                pn.pane.Markdown("- `id`: Unique identifier for each work item"),
                pn.pane.Markdown(
                    "- `start_date`: Start date of the work item in ISO 8601 format or YYYY-MM-DD"
                ),
                pn.pane.Markdown(
                    "- `end_date`: End date of the work item in ISO 8601 format"
                ),
            )
            title = DATA_SOURCE_LABEL
    return pn.Column(
        pn.pane.Markdown(f"# {title}"),
        content,
        sizing_mode="stretch_width",
        margin=(10, 0),
        styles={"background": "white", "box-shadow": "none", "border": "none"},
    )


# Create button column with spacing
button_column = pn.Column(
    data_source_button,
    pn.layout.Spacer(height=20),  # Add 20px space between buttons
    when_button,
    pn.layout.Spacer(height=20),  # Add space between buttons
    how_many_button,
)

# About section for sidebar
about_text = pn.pane.Markdown(
    """
### About

This dashboard uses Monte Carlo simulation to forecast either:

1. When a specific number of work items will be completed
2. How many work items can be completed in a given time period

The forecasts are based on historical completion data.

<a href="https://github.com/rodbv/kwando" target="_blank" style="display:inline-flex; align-items:center; text-decoration:none;">
  <img src="https://e7.pngegg.com/pngimages/646/324/png-clipart-github-computer-icons-github-logo-monochrome-thumbnail.png" alt="GitHub" style="height:1.2em; margin-right:0.3em; vertical-align:middle;"/>
  GitHub
</a>

---

**Credits:**
- Monte Carlo simulation implementation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Inspired by the book [Actionable Agile Metrics for Predictability: An Introduction](https://actionableagile.com/books/aamfp/) by Daniel Vacanti
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

# Add development mode support - only run when explicitly called
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--dev", action="store_true", help="Run in development mode"
        )
        args = parser.parse_args()
        template.show(port=5006, dev=args.dev)

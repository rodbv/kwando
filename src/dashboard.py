import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import panel as pn
from monte_carlo import (
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_next_business_day,
)
from panel.layout import Row
from panel.widgets import Checkbox

# Initialize Panel with template support
pn.extension("tabulator", "ace")

# Set theme colors
ACCENT_COLOR = "#2c5282"  # A more elegant navy blue
ACCENT_COLOR_DARK = "#90cdf4"  # Lighter blue for dark mode

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
file_input = pn.widgets.FileInput(name="Upload Custom CSV")
default_file_text = pn.pane.Markdown("**Current data:** data/data.csv (default)")

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

# Dynamic tag checkboxes (will be created based on loaded data)
tag_checkboxes = pn.Column(name="Tag Filters", visible=False)

# Global state for data source
current_data_file = "data/data.csv"


def get_current_data_file():
    return file_selector.value


# Add a reusable data cleaning/filtering function
def clean_and_filter_data(df: pd.DataFrame, selected_tags=None) -> pd.DataFrame:
    """
    Clean and filter a DataFrame:
    - Filters out records with a cycle_time_days <= 0.
    - If selected_tags is provided, filters rows to include:
      * Rows that have ANY of the selected tags
      * Rows with no tags (empty or NaN in tags column)
    """
    try:
        cleaned = df[df["cycle_time_days"] > 0].copy()
        if selected_tags and len(selected_tags) > 0 and "tags" in cleaned.columns:
            include_mask = pd.Series([False] * len(cleaned), index=cleaned.index)
            for idx, row in cleaned.iterrows():
                tags_str = row.get("tags", "")
                if pd.isna(tags_str) or str(tags_str).strip() == "":
                    include_mask[idx] = True
                    continue
                row_tags = [tag.strip() for tag in str(tags_str).split(",")]
                if any(tag in selected_tags for tag in row_tags):
                    include_mask[idx] = True
            cleaned = cleaned[include_mask].copy()
        return cleaned
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not clean/filter data: {str(e)}"]})


# Update load_and_clean_data to use the new cleaning function
def load_and_clean_data(filename: str, selected_tags=None) -> pd.DataFrame:
    """
    Load data from a CSV file and clean/filter it.
    """
    try:
        df = pd.read_csv(filename)
        return clean_and_filter_data(df, selected_tags)
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
        invalid_cycle_time = len(original_df[original_df["cycle_time_days"] <= 0])

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
    default_file_text.object = "**No data file available.**"


# Function to handle file selection and update preview/stats


def handle_file_selection(event):
    if not file_selector.value:
        data_preview_pane.object = pd.DataFrame(
            {"Info": ["No CSV file selected or available in data/ directory."]}
        )
        data_stats_pane.object = "### Data Statistics\n\nNo file selected."
        default_file_text.object = "**No data file selected.**"
        tag_checkboxes.visible = False
        return

    # Collect selected tags from checkboxes
    selected_tags = []
    if getattr(tag_checkboxes, "visible", False) and len(tag_checkboxes) > 1:
        checkbox_row = tag_checkboxes[1]
        if isinstance(checkbox_row, Row):
            for checkbox in checkbox_row:
                if isinstance(checkbox, Checkbox) and checkbox.value:
                    selected_tags.append(checkbox.name)

    # Load data with tag filtering
    full_df = load_and_clean_data(file_selector.value, selected_tags=selected_tags)
    data_preview_pane.object = (
        full_df.head(100) if "Error" not in full_df.columns else full_df
    )
    data_stats_pane.object = get_data_stats_md(full_df)
    default_file_text.object = f"**Current data:** {file_selector.value}"

    # Handle dynamic tag checkboxes
    if "Error" not in full_df.columns and "tags" in full_df.columns:
        # Load the full unfiltered dataset to get all available tags
        try:
            full_unfiltered_df = pd.read_csv(file_selector.value)
            # Extract unique tags from the full unfiltered data
            all_tags = set()
            if "tags" in full_unfiltered_df.columns:
                for tags_str in full_unfiltered_df["tags"].dropna():
                    if tags_str.strip():  # Skip empty strings
                        tags = [tag.strip() for tag in tags_str.split(",")]
                        all_tags.update(tags)
        except Exception:
            # Fallback to using the filtered data if loading full data fails
            all_tags = set()
            for tags_str in full_df["tags"].dropna():
                if tags_str.strip():  # Skip empty strings
                    tags = [tag.strip() for tag in tags_str.split(",")]
                    all_tags.update(tags)

        if all_tags:
            # Get currently selected tags before clearing
            currently_selected = set()
            if getattr(tag_checkboxes, "visible", False) and len(tag_checkboxes) > 1:
                checkbox_row = tag_checkboxes[1]
                if isinstance(checkbox_row, Row):
                    for checkbox in checkbox_row:
                        if isinstance(checkbox, Checkbox) and checkbox.value:
                            currently_selected.add(checkbox.name)

            # Clear existing checkboxes and create new ones
            tag_checkboxes.clear()
            tag_checkboxes.append(pn.pane.Markdown("**Select tags to filter by:**"))

            # Create checkboxes for each tag, laid out in a row
            checkbox_row = pn.Row()
            for tag in sorted(all_tags):
                # Preserve the checked state if this tag was previously selected
                is_checked = tag in currently_selected
                checkbox = make_checkbox_reactive(
                    pn.widgets.Checkbox(name=tag, value=is_checked)
                )
                checkbox_row.append(checkbox)

            tag_checkboxes.append(checkbox_row)
            tag_checkboxes.visible = True
        else:
            tag_checkboxes.visible = False
    else:
        # No tags column or error loading data
        tag_checkboxes.visible = False


file_selector.param.watch(handle_file_selection, "value")


@pn.depends(file_selector.param.value, tag_checkboxes.param.visible)
def get_data_source_info(selected_file, tags_visible):
    """Get information about current data source and selected tags"""
    if not selected_file:
        return pn.pane.Markdown("**Data Source:** No file selected")

    # Get selected tags
    selected_tags = []
    if getattr(tag_checkboxes, "visible", False) and len(tag_checkboxes) > 1:
        checkbox_row = tag_checkboxes[1]
        if isinstance(checkbox_row, Row):
            for checkbox in checkbox_row:
                if isinstance(checkbox, Checkbox) and checkbox.value:
                    selected_tags.append(checkbox.name)

    # Create info text
    info_text = f"**Data Source:** {selected_file}"
    if selected_tags:
        tags_text = ", ".join(selected_tags)
        info_text += f" | **Tags:** {tags_text}"
    else:
        info_text += " | **Tags:** All tags (none selected)"

    return pn.pane.Markdown(info_text)


def handle_tag_selection(event):
    """Handle changes to tag checkboxes and update only the data preview and stats"""
    if not file_selector.value:
        return

    # Collect selected tags
    selected_tags = []
    if getattr(tag_checkboxes, "visible", False) and len(tag_checkboxes) > 1:
        checkbox_row = tag_checkboxes[1]
        if isinstance(checkbox_row, Row):
            for checkbox in checkbox_row:
                if isinstance(checkbox, Checkbox) and checkbox.value:
                    selected_tags.append(checkbox.name)

    # Load filtered data without recreating checkboxes
    filtered_df = load_and_clean_data(file_selector.value, selected_tags=selected_tags)

    # Update only the data preview and stats, not the entire page
    data_preview_pane.object = (
        filtered_df.head(100) if "Error" not in filtered_df.columns else filtered_df
    )
    data_stats_pane.object = get_data_stats_md(filtered_df)


# Function to make checkboxes reactive (will be called when creating checkboxes)
def make_checkbox_reactive(checkbox):
    checkbox.param.watch(handle_tag_selection, "value")
    return checkbox


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


# Function to update results based on work items simulation
def update_work_items_results(num_cards):
    try:
        # DataFrame is already filtered by tags in data_preview_pane.object
        results = forecast_days_for_work_items(
            df=data_preview_pane.object,
            num_work_items=num_cards,
            num_iterations=5000,
        )

        # Check if the results are valid before proceeding
        if not results or not results.get("percentile_dates"):
            return "## Warning\n\nCould not generate a forecast. This is likely due to missing or invalid data in the source file. Please check the data and try again."

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
        # DataFrame is already filtered by tags in data_preview_pane.object
        results = forecast_work_items_in_period(
            df=data_preview_pane.object,
            start_date=start_date,
            end_date=end_date,
            num_iterations=5000,
        )

        # Check if the results are valid before proceeding
        if not results or not results.get("percentiles"):
            return "## Warning\n\nCould not generate a forecast. This is likely due to missing or invalid data in the source file. Please check the data and try again."

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
@pn.depends(
    num_cards_slider.param.value,
    file_selector.param.value,
)
def get_work_items_results(num_cards, selected_file):
    global current_data_file
    current_data_file = selected_file
    return update_work_items_results(num_cards)


@pn.depends(
    period_start_date.param.value,
    period_end_date.param.value,
    file_selector.param.value,
)
def get_period_results(start_date, end_date, selected_file):
    global current_data_file
    current_data_file = selected_file
    return update_period_results(start_date, end_date)


# Create dynamic Panel panes for displaying results
work_items_results = pn.bind(pn.pane.Markdown, get_work_items_results)
period_results = pn.bind(pn.pane.Markdown, get_period_results)

# Create reactive data source info
data_source_info = get_data_source_info


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
                        data_source_info,
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
                        data_source_info,
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
                        default_file_text,
                        file_selector,
                        pn.layout.Spacer(height=10),
                        tag_checkboxes,
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
                    "- `cycle_time_days`: Time taken to complete the work item"
                ),
                pn.pane.Markdown(
                    "- `tags`: Comma-separated tags for filtering (optional)"
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

---

**Credits:**
- Monte Carlo simulation implementation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Theory and approach inspired by Daniel Vacanti's [ActionableAgile](https://www.actionableagile.com/)
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

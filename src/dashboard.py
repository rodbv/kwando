import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import panel as pn
from monte_carlo import (
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_data_statistics,
    get_next_business_day,
    load_and_prepare_data,
    parse_throughput_from_text,
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

# Add input mode selector (CSV file vs. direct text input)
input_mode = pn.widgets.RadioButtonGroup(
    name="Data Input Mode",
    options=["CSV File", "Direct Input"],
    value="CSV File",
    button_type="default",
    width=300,
)

# Add text input widget for direct throughput entry
throughput_text_input = pn.widgets.TextAreaInput(
    name="Enter Throughput Values",
    placeholder="2,3,5,2,4,6",
    value="",
    height=100,
    width=400,
)


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


def load_and_clean_data(filename: str) -> pd.DataFrame:
    """
    Load data from a CSV file and convert to a dataframe
    """
    try:
        return load_and_prepare_data(filename)
    except (ValueError, pd.errors.ParserError, Exception) as e:
        return pd.DataFrame({"Error": [str(e)]})


def load_data_from_text_input(text_input: str) -> pd.DataFrame:
    """
    Load data from text input and convert to a dataframe
    """
    try:
        return parse_throughput_from_text(text_input)
    except ValueError as e:
        return pd.DataFrame({"Error": [str(e)]})
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not parse input: {str(e)}"]})


def get_data_stats_as_markdown(df):
    """
    Calculate and display data statistics
    """
    if "Error" in df.columns or df.empty:
        return "### Data Statistics\n\nCould not calculate statistics. Please check the data file."

    try:
        stats = get_data_statistics(df)

        if stats["error"]:
            return f"### Data Statistics\n\n{stats['error']}"

        # Format as a Markdown string
        stats_md = f"""
### Data Statistics
- **Total Weeks of Data:** {stats['total_weeks']}
- **Average Weekly Throughput:** `{stats['avg_throughput']:.2f}` items/week
- **Min Weekly Throughput:** `{stats['min_throughput']:.2f}` items/week
- **Max Weekly Throughput:** `{stats['max_throughput']:.2f}` items/week
- **Median Weekly Throughput:** `{stats['median_throughput']:.2f}` items/week
"""
        return stats_md
    except Exception as e:
        return (
            f"### Error Calculating Stats\n\nCould not calculate statistics: {str(e)}"
        )


# The data preview pane, created once and updated reactively
# Initialize based on default mode (CSV File)
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
        get_data_stats_as_markdown(initial_data)
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


def handle_file_selection(event):
    """
    Handle file selection and update preview/stats
    """
    if input_mode.value != "CSV File":
        return  # Only handle if CSV mode is active

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
    data_stats_pane.object = get_data_stats_as_markdown(full_df)


def handle_text_input(event):
    """
    Handle text input changes and update preview/stats
    """
    if input_mode.value != "Direct Input":
        return  # Only handle if Direct Input mode is active

    if not throughput_text_input.value or not throughput_text_input.value.strip():
        data_preview_pane.object = pd.DataFrame(
            {"Info": ["Enter comma-separated throughput values (e.g., 2,3,5,2)"]}
        )
        data_stats_pane.object = "### Data Statistics\n\nNo input provided."
        return

    # Load data from text input
    full_df = load_data_from_text_input(throughput_text_input.value)
    data_preview_pane.object = (
        full_df.head(100) if "Error" not in full_df.columns else full_df
    )
    data_stats_pane.object = get_data_stats_as_markdown(full_df)


def handle_input_mode_change(event):
    """
    Handle input mode changes and update preview/stats based on active mode
    """
    if event.new == "CSV File":
        # Switch to CSV mode - load from file selector
        if file_selector.value:
            full_df = load_and_clean_data(file_selector.value)
            data_preview_pane.object = (
                full_df.head(100) if "Error" not in full_df.columns else full_df
            )
            data_stats_pane.object = get_data_stats_as_markdown(full_df)
        else:
            data_preview_pane.object = pd.DataFrame(
                {"Info": ["No CSV file selected or available in data/ directory."]}
            )
            data_stats_pane.object = "### Data Statistics\n\nNo file selected."
    else:  # Direct Input mode
        # Switch to direct input mode - load from text input
        if throughput_text_input.value and throughput_text_input.value.strip():
            full_df = load_data_from_text_input(throughput_text_input.value)
            data_preview_pane.object = (
                full_df.head(100) if "Error" not in full_df.columns else full_df
            )
            data_stats_pane.object = get_data_stats_as_markdown(full_df)
        else:
            data_preview_pane.object = pd.DataFrame(
                {"Info": ["Enter comma-separated throughput values (e.g., 2,3,5,2)"]}
            )
            data_stats_pane.object = "### Data Statistics\n\nNo input provided."


file_selector.param.watch(handle_file_selection, "value")
throughput_text_input.param.watch(handle_text_input, "value")
input_mode.param.watch(handle_input_mode_change, "value")


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


def update_work_items_results(df, num_cards):
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
        return pn.Column(
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


def update_period_results(df, start_date, end_date):
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
        return pn.Column(
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
    input_mode.param.value,
    file_selector.param.value,
    throughput_text_input.param.value,
)
def get_work_items_results(num_cards, mode, selected_file, text_input):
    # Get data based on current input mode
    if mode == "Direct Input":
        if not text_input or not text_input.strip():
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nNo valid data loaded. Please enter throughput values."
                )
            )
        df = load_data_from_text_input(text_input)
    else:  # CSV File mode
        if not selected_file:
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nNo valid data loaded. Please select a CSV file."
                )
            )
        df = load_and_clean_data(selected_file)

    if not isinstance(df, pd.DataFrame) or "Error" in df.columns:
        return pn.Column(pn.pane.Markdown("## Warning\n\nNo valid data loaded."))
    return update_work_items_results(df, num_cards)


# Replace get_period_results to use the new function
@pn.depends(
    period_start_date.param.value,
    period_end_date.param.value,
    input_mode.param.value,
    file_selector.param.value,
    throughput_text_input.param.value,
)
def get_period_results(start_date, end_date, mode, selected_file, text_input):
    # Get data based on current input mode
    if mode == "Direct Input":
        if not text_input or not text_input.strip():
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nNo valid data loaded. Please enter throughput values."
                )
            )
        df = load_data_from_text_input(text_input)
    else:  # CSV File mode
        if not selected_file:
            return pn.Column(
                pn.pane.Markdown(
                    "## Warning\n\nNo valid data loaded. Please select a CSV file."
                )
            )
        df = load_and_clean_data(selected_file)

    if not isinstance(df, pd.DataFrame) or "Error" in df.columns:
        return pn.Column(pn.pane.Markdown("## Warning\n\nNo valid data loaded."))
    return update_period_results(df, start_date, end_date)


# Create dynamic Panel panes for displaying results
work_items_results = get_work_items_results
period_results = get_period_results


# Create reactive data source info
def get_data_source_info():
    """Get data source info based on current input mode."""
    mode = input_mode.value
    selected_file = file_selector.value

    if mode == "Direct Input":
        return pn.pane.Markdown("**Data Source:** Direct Input")
    if not selected_file:
        return pn.pane.Markdown("**Data Source:** No file selected")
    return pn.pane.Markdown(f"**Data Source:** {selected_file}")


# Load help text from markdown file
def load_help_text():
    """Load help text from markdown file."""
    try:
        help_file_path = "docs/monte_carlo_help.md"
        with open(help_file_path, encoding="utf-8") as f:
            help_content = f.read()
        return pn.pane.Markdown(help_content)
    except FileNotFoundError:
        # Fallback to basic help text if file not found
        return pn.pane.Markdown(
            "## Help\n\nHelp documentation not found. Please check the docs/monte_carlo_help.md file."
        )
    except Exception as e:
        # Fallback to basic help text if any error
        return pn.pane.Markdown(
            f"## Help\n\nError loading help documentation: {str(e)}"
        )


help_text = load_help_text()


def load_about_text():
    """Load about text from markdown file."""
    try:
        about_file_path = "docs/about.md"
        with open(about_file_path, encoding="utf-8") as f:
            about_content = f.read()
        return pn.pane.Markdown(about_content, styles={"font-size": "14px"})
    except FileNotFoundError:
        # Fallback to basic about text if file not found
        return pn.pane.Markdown(
            "## About\n\nAbout information not found. Please check the docs/about.md file.",
            styles={"font-size": "14px"},
        )
    except Exception as e:
        # Fallback to basic about text if any error
        return pn.pane.Markdown(
            f"## About\n\nError loading about information: {str(e)}",
            styles={"font-size": "14px"},
        )


@pn.depends(input_mode.param.value, file_selector.param.value)
def _create_work_items_content(mode, selected_file):
    """Create content for work items simulation."""
    return pn.Column(
        pn.Row(
            pn.Column(
                get_data_source_info(),
                num_cards_slider,
                sizing_mode="stretch_width",
            ),
        ),
        work_items_results,
    )


@pn.depends(input_mode.param.value, file_selector.param.value)
def _create_period_content(mode, selected_file):
    """Create content for time period simulation."""
    return pn.Column(
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


def _create_data_source_content():
    """Create content for data source page."""
    mode = input_mode.value

    csv_section = pn.Column(
        pn.pane.Markdown("### CSV File Input"),
        file_input,
        file_selector,
        pn.layout.Spacer(height=20),
        sizing_mode="stretch_width",
    )

    direct_input_section = pn.Column(
        pn.pane.Markdown("### Direct Text Input"),
        pn.pane.Markdown(
            "Enter comma-separated throughput values (e.g., `2,3,5,2,4,6`). "
            "Whitespace around commas is automatically trimmed."
        ),
        throughput_text_input,
        pn.layout.Spacer(height=20),
        sizing_mode="stretch_width",
    )

    return pn.Column(
        pn.Row(
            pn.Column(
                pn.pane.Markdown("### Choose Data Input Method"),
                input_mode,
                pn.layout.Spacer(height=20),
                sizing_mode="stretch_width",
            ),
        ),
        csv_section if mode == "CSV File" else direct_input_section,
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
        pn.pane.Markdown("**CSV file format:**"),
        pn.pane.Markdown(
            "- `throughput`: Weekly throughput values (items completed per week), one value per row"
        ),
        pn.pane.Markdown(""),
        pn.pane.Markdown("**Example CSV format:**"),
        pn.pane.Markdown("```csv\nthroughput\n5.0\n3.0\n7.0\n4.0\n```"),
        pn.pane.Markdown(""),
        pn.pane.Markdown("**Direct input format:**"),
        pn.pane.Markdown(
            "- Comma-separated values: `2,3,5,2,4,6` or `2, 3, 5, 2, 4, 6`"
        ),
        pn.pane.Markdown("- All values must be numeric and non-negative (>= 0)"),
        pn.pane.Markdown("- Maximum 1000 values (use CSV for larger datasets)"),
        pn.layout.Spacer(height=20),
        pn.pane.Markdown(
            "**⬇️ Download sample CSV files:** [GitHub data folder](https://github.com/rodbv/kwando/tree/main/data)"
        ),
    )


# Content mapping for different simulation types
CONTENT_MAPPING = {
    WHEN_LABEL: (_create_work_items_content, WHEN_LABEL),
    HOW_MANY_LABEL: (_create_period_content, HOW_MANY_LABEL),
    DATA_SOURCE_LABEL: (_create_data_source_content, DATA_SOURCE_LABEL),
}


# Create a dynamic panel with smooth transitions
@pn.depends(
    help_visible.param.value,
    active_simulation.param.value,
    input_mode.param.value,
    file_selector.param.value,
)
def get_main_content(show_help, sim_type, mode, selected_file):
    if show_help:
        content = help_text
        title = "About Monte Carlo Simulation"
    else:
        content_func, title = CONTENT_MAPPING.get(
            sim_type, CONTENT_MAPPING[DATA_SOURCE_LABEL]
        )
        # Pass required parameters for reactive content functions
        if (
            content_func == _create_work_items_content
            or content_func == _create_period_content
        ):
            content = content_func(mode, selected_file)
        else:
            content = content_func()

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
about_text = load_about_text()

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

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date

PERCENTILES = [70, 80, 90, 95, 98]


def get_next_business_day() -> date:
    """Calculate the next business day from today"""
    next_day = datetime.now() + timedelta(days=1)
    # Keep adding days until we get a weekday (Monday = 0, Sunday = 6)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day.date()


def load_and_clean_data(
    filename: str, selected_tags: Optional[list] = None
) -> pd.DataFrame:
    """
    Load and clean data from a CSV file.

    - Reads the specified CSV file.
    - Filters out records with a cycle_time_days <= 0.
    - If selected_tags is provided, filters rows to include:
      * Rows that have ANY of the selected tags
      * Rows with no tags (empty or NaN in tags column)
    """
    try:
        df = pd.read_csv(filename)
        # Clean the data, excluding cycle times <= 0
        cleaned = df[df["cycle_time_days"] > 0].copy()

        # Apply tag filtering if tags are selected
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
        return pd.DataFrame({"Error": [f"Could not load data: {str(e)}"]})


def forecast_days_for_work_items(
    num_work_items: int,
    filename: str = "data/data.csv",
    num_iterations: int = 5000,
    selected_tags: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Forecast the number of days required to finish the next `num_work_items` work items using Monte Carlo simulation.

    Parameters:
        num_work_items (int): Number of work items to forecast completion for.
        filename (str): Path to the CSV file with work item data.
        num_iterations (int): Number of Monte Carlo simulation runs.
        selected_tags (Optional[list]): List of tags to filter by. If None, no tag filtering is applied.

    Returns:
        Dict[str, Any]: Dictionary with simulation results and parameters:
            - 'simulated_durations': List[int], simulated durations (in days) for each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated durations (keys: as in PERCENTILES)
            - 'percentile_dates': Dict[str, str], projected completion dates for each percentile (ISO format)
            - 'num_work_items': int, number of work items requested
            - 'num_iterations': int, number of simulation runs
    """
    cleaned = load_and_clean_data(filename, selected_tags)
    if "Error" in cleaned.columns:
        return {
            "simulated_durations": [],
            "percentiles": {},
            "percentile_dates": {},
            "num_work_items": num_work_items,
            "num_iterations": num_iterations,
        }
    cycle_times = cleaned["cycle_time_days"].to_numpy()
    start_ts = pd.Timestamp.today().normalize()
    if len(cycle_times) == 0:
        return {
            "simulated_durations": [],
            "percentiles": {},
            "percentile_dates": {},
            "num_work_items": num_work_items,
            "num_iterations": num_iterations,
        }

    def cumulative_sum(total_work_items, cycle_times, selector):
        total = [0]
        for _ in range(total_work_items):
            total.append(selector(cycle_times) + total[-1])
        return total

    simulated_totals = []
    for _ in range(num_iterations):
        walk = cumulative_sum(num_work_items, cycle_times, random.choice)
        simulated_totals.append(walk[-1])
    percentiles = {
        str(p): float(np.quantile(simulated_totals, p / 100)) for p in PERCENTILES
    }
    percentile_dates = {
        k: (start_ts + pd.Timedelta(days=v)).date().isoformat()
        for k, v in percentiles.items()
    }
    return {
        "simulated_durations": simulated_totals,
        "percentiles": percentiles,
        "percentile_dates": percentile_dates,
        "num_work_items": num_work_items,
        "num_iterations": num_iterations,
    }


def forecast_work_items_in_period(
    start_date: str,
    end_date: str,
    filename: str = "data/data.csv",
    num_iterations: int = 5000,
    selected_tags: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Forecast how many work items can be finished between start_date and end_date using Monte Carlo simulation.

    Parameters:
        start_date (str): Start date for the forecast period (YYYY-MM-DD).
        end_date (str): End date for the forecast period (YYYY-MM-DD).
        filename (str): Path to the CSV file with work item data.
        num_iterations (int): Number of Monte Carlo simulation runs.
        selected_tags (Optional[list]): List of tags to filter by. If None, no tag filtering is applied.

    Returns:
        Dict[str, Any]: Dictionary with simulation results and parameters:
            - 'simulated_work_items': List[int], simulated number of work items completed in each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated work items (keys: as in PERCENTILES)
            - 'start_date': str, start date used for forecast
            - 'end_date': str, end date used for forecast
            - 'num_iterations': int, number of simulation runs
    """
    cleaned = load_and_clean_data(filename, selected_tags)
    if "Error" in cleaned.columns:
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": None,
            "end_date": None,
            "num_iterations": num_iterations,
        }
    cycle_times = cleaned["cycle_time_days"].to_numpy()
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    max_days = (end_ts - start_ts).days
    if len(cycle_times) == 0:
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": (
                start_ts.date().isoformat() if start_ts is not pd.NaT else None
            ),
            "end_date": end_ts.date().isoformat() if end_ts is not pd.NaT else None,
            "num_iterations": num_iterations,
        }

    def simulate_days(num_of_iterations, max_days, cycle_times):
        totals = []
        for _ in range(num_of_iterations):
            simulated_cycle_times = [0]
            while True:
                n = random.choice(cycle_times) + simulated_cycle_times[-1]
                if n > max_days:
                    break
                else:
                    simulated_cycle_times.append(n)
            totals.append(len(simulated_cycle_times) - 1)
        return totals

    simulated_work_items = simulate_days(num_iterations, max_days, cycle_times)
    percentiles = {
        str(p): float(np.quantile(simulated_work_items, p / 100)) for p in PERCENTILES
    }
    return {
        "simulated_work_items": simulated_work_items,
        "percentiles": percentiles,
        "start_date": start_ts.date().isoformat() if start_ts is not pd.NaT else None,
        "end_date": end_ts.date().isoformat() if end_ts is not pd.NaT else None,
        "num_iterations": num_iterations,
    }

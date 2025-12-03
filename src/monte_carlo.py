import random
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

PERCENTILES = [70, 80, 90, 95, 98]


# Note: load_and_prepare_data function removed - CSV file support removed, only direct text input is supported
# Note: convert_dates_to_cycle_time function removed - no longer needed for throughput-based forecasting


def parse_throughput_from_text(text_input: str) -> pd.DataFrame:
    """
    Parse comma-separated throughput values from text input and prepare for Monte Carlo simulation.

    Args:
        text_input: Comma-separated throughput values (e.g., "2,3,5,2" or "2, 3, 5, 2")

    Returns:
        DataFrame with throughput column ready for simulation

    Raises:
        ValueError: If input is empty, contains invalid values, or values are negative
    """
    if not text_input or not text_input.strip():
        raise ValueError("Throughput input cannot be empty.")

    # Split by comma and strip whitespace from each value
    values_str = [v.strip() for v in text_input.split(",") if v.strip()]

    if not values_str:
        raise ValueError(
            "No valid throughput values found. Please enter comma-separated numeric values."
        )

    # Limit to 1000 values for performance
    if len(values_str) > 1000:
        raise ValueError(
            f"Too many values ({len(values_str)}). Maximum 1000 values allowed. "
            "Please reduce the number of values to 1000 or fewer."
        )

    # Convert to numeric, handling errors
    try:
        throughput_values = pd.to_numeric(values_str, errors="raise")
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid throughput values. All values must be numeric. Error: {str(e)}"
        ) from e

    # Validate non-negative
    if (throughput_values < 0).any():
        raise ValueError("Throughput values must be non-negative (>= 0).")

    # Create DataFrame with throughput column
    df_prepared = pd.DataFrame({"throughput": throughput_values})

    return df_prepared


def get_next_business_day() -> date:
    """Calculate the next business day from today"""
    next_day = datetime.now() + timedelta(days=1)
    # Keep adding days until we get a weekday (Monday = 0, Sunday = 6)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day.date()


def forecast_days_for_work_items(
    df: pd.DataFrame,
    num_work_items: int,
    num_iterations: int = 5000,
) -> dict[str, Any]:
    """
    Forecast the number of days required to finish the next `num_work_items` work items using weekly throughput-based Monte Carlo simulation.

    Parameters:
        df (pd.DataFrame): DataFrame with at least a 'throughput' column (weekly throughput values)
        num_work_items (int): Number of work items to forecast completion for.
        num_iterations (int): Number of Monte Carlo simulation runs.

    Returns:
        Dict[str, Any]:
            - 'simulated_durations': List[float], simulated durations (in days) for each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated durations (keys: as in PERCENTILES)
            - 'percentile_dates': Dict[str, str], projected completion dates for each percentile (ISO format)
            - 'num_work_items': int, number of work items requested
            - 'num_iterations': int, number of simulation runs
    """
    if df is None or df.empty or "throughput" not in df.columns:
        return {
            "simulated_durations": [],
            "percentiles": {},
            "percentile_dates": {},
            "num_work_items": num_work_items,
            "num_iterations": num_iterations,
        }
    throughput_values = df["throughput"].to_numpy()
    start_ts = pd.Timestamp.today().normalize()
    if len(throughput_values) == 0:
        return {
            "simulated_durations": [],
            "percentiles": {},
            "percentile_dates": {},
            "num_work_items": num_work_items,
            "num_iterations": num_iterations,
        }

    # Simulate using weekly throughput
    # Each iteration samples weekly throughput values until we accumulate enough items
    simulated_weeks = []
    for _ in range(num_iterations):
        items_completed = 0.0
        weeks_elapsed = 0
        while items_completed < num_work_items:
            weekly_throughput = random.choice(throughput_values)  # nosec: B311 - Monte Carlo simulation does not require cryptographic randomness
            items_completed += weekly_throughput
            weeks_elapsed += 1
        simulated_weeks.append(weeks_elapsed)

    # Convert weeks to days (1 week = 7 days)
    simulated_days = [weeks * 7.0 for weeks in simulated_weeks]

    percentiles = {
        str(p): float(np.quantile(simulated_days, p / 100)) for p in PERCENTILES
    }
    percentile_dates = {
        k: safe_isoformat(start_ts + pd.Timedelta(days=v))
        for k, v in percentiles.items()
    }
    return {
        "simulated_durations": simulated_days,
        "percentiles": percentiles,
        "percentile_dates": percentile_dates,
        "num_work_items": num_work_items,
        "num_iterations": num_iterations,
    }


def forecast_work_items_in_period(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    num_iterations: int = 5000,
) -> dict[str, Any]:
    """
    Forecast how many work items can be finished between start_date and end_date using weekly throughput-based Monte Carlo simulation.

    Parameters:
        df (pd.DataFrame): DataFrame with at least a 'throughput' column (weekly throughput values)
        start_date (str): Start date for the forecast period (YYYY-MM-DD).
        end_date (str): End date for the forecast period (YYYY-MM-DD).
        num_iterations (int): Number of Monte Carlo simulation runs.

    Returns:
        Dict[str, Any]:
            - 'simulated_work_items': List[float], simulated number of work items completed in each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated work items (keys: as in PERCENTILES)
            - 'start_date': str, start date used for forecast
            - 'end_date': str, end date used for forecast
            - 'num_iterations': int, number of simulation runs
    """
    if df is None or df.empty or "throughput" not in df.columns:
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": None,
            "end_date": None,
            "num_iterations": num_iterations,
        }
    throughput_values = df["throughput"].to_numpy()
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    total_days = (end_ts - start_ts).days
    total_weeks = total_days / 7.0  # Convert days to weeks

    if len(throughput_values) == 0:
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": safe_isoformat(start_ts),
            "end_date": safe_isoformat(end_ts),
            "num_iterations": num_iterations,
        }

    # Simulate using weekly throughput
    # Each iteration samples weekly throughput values for the number of weeks in the period
    simulated_work_items = []
    for _ in range(num_iterations):
        items_completed = 0.0
        weeks_elapsed = 0.0
        while weeks_elapsed < total_weeks:
            weekly_throughput = random.choice(throughput_values)  # nosec: B311 - Monte Carlo simulation does not require cryptographic randomness
            items_completed += weekly_throughput
            weeks_elapsed += 1.0
        simulated_work_items.append(items_completed)

    percentiles = {
        str(p): float(np.quantile(simulated_work_items, p / 100)) for p in PERCENTILES
    }
    return {
        "simulated_work_items": simulated_work_items,
        "percentiles": percentiles,
        "start_date": safe_isoformat(start_ts),
        "end_date": safe_isoformat(end_ts),
        "num_iterations": num_iterations,
    }


def get_data_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate basic statistics for a DataFrame with throughput column.

    Args:
        df: DataFrame with throughput column (weekly throughput values)

    Returns:
        Dictionary with statistics including min, max, median weekly throughput and data quality info
    """
    if df is None or df.empty or "throughput" not in df.columns:
        return {
            "total_weeks": 0,
            "min_throughput": 0,
            "max_throughput": 0,
            "median_throughput": 0,
            "avg_throughput": 0,
            "error": "No valid data available",
        }

    try:
        min_throughput = float(df["throughput"].min())
        max_throughput = float(df["throughput"].max())
        median_throughput = float(df["throughput"].median())
        avg_throughput = float(df["throughput"].mean())
        total_weeks = len(df)

        return {
            "total_weeks": total_weeks,
            "min_throughput": min_throughput,
            "max_throughput": max_throughput,
            "median_throughput": median_throughput,
            "avg_throughput": avg_throughput,
            "error": None,
        }
    except Exception as e:
        return {
            "total_weeks": 0,
            "min_throughput": 0,
            "max_throughput": 0,
            "median_throughput": 0,
            "avg_throughput": 0,
            "error": f"Error calculating statistics: {str(e)}",
        }


def safe_isoformat(ts):
    if isinstance(ts, NaTType) or not pd.notnull(ts):
        return None
    d = ts.date() if hasattr(ts, "date") else ts
    if isinstance(d, NaTType) or not pd.notnull(d):
        return None
    return d.isoformat() if hasattr(d, "isoformat") else str(d)

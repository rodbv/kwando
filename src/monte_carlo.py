import random
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

PERCENTILES = [70, 80, 90, 95, 98]


def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file and prepare it for Monte Carlo simulation.

    Args:
        csv_path: Path to the CSV file

    Returns:
        DataFrame with cycle_time_days column ready for simulation

    Raises:
        ValueError: If CSV doesn't have required columns
        pd.errors.ParserError: If CSV can't be parsed
    """
    try:
        df = pd.read_csv(csv_path)
        if "start_date" not in df.columns or "end_date" not in df.columns:
            raise ValueError(
                "CSV must have start_date and end_date columns in ISO 8601 format."
            )
        return convert_dates_to_cycle_time(df)
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Could not load data: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Could not load data: {str(e)}") from e


def convert_dates_to_cycle_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert start_date and end_date columns to cycle_time_days.

    Args:
        df: DataFrame with start_date and end_date columns in ISO 8601 format

    Returns:
        DataFrame with cycle_time_days column added/updated

    The function:
    - Parses dates in ISO 8601 format (both long and short)
    - Calculates difference between end_date and start_date
    - Rounds up to the next day (e.g., 1.1 days becomes 2 days)
    - If same date in both columns, result is 1 day
    """
    if "start_date" not in df.columns or "end_date" not in df.columns:
        return df

    df_copy = df.copy()

    # Convert date columns to datetime, handling various ISO formats
    for col in ["start_date", "end_date"]:
        df_copy[col] = pd.to_datetime(df_copy[col], format="mixed", errors="coerce")

    # Calculate the difference in days
    # Convert to date objects to get calendar days
    start_dates = df_copy["start_date"].dt.date
    end_dates = df_copy["end_date"].dt.date

    # Calculate calendar day difference
    date_diff = [
        (ed - sd).days if pd.notnull(ed) and pd.notnull(sd) else float("nan")
        for sd, ed in zip(start_dates, end_dates, strict=True)
    ]
    date_diff = pd.Series(date_diff, index=df_copy.index)
    cycle_time = date_diff.apply(lambda d: max(1, int(d) + 1) if pd.notnull(d) else 1)

    # Add or update cycle_time_days column
    df_copy["cycle_time_days"] = cycle_time.astype(int)

    return df_copy


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
    Forecast the number of days required to finish the next `num_work_items` work items using Monte Carlo simulation.

    Parameters:
        df (pd.DataFrame): DataFrame with at least a 'cycle_time_days' column (positive ints/floats)
        num_work_items (int): Number of work items to forecast completion for.
        num_iterations (int): Number of Monte Carlo simulation runs.

    Returns:
        Dict[str, Any]:
            - 'simulated_durations': List[int], simulated durations (in days) for each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated durations (keys: as in PERCENTILES)
            - 'percentile_dates': Dict[str, str], projected completion dates for each percentile (ISO format)
            - 'num_work_items': int, number of work items requested
            - 'num_iterations': int, number of simulation runs
    """
    if df is None or "cycle_time_days" not in df.columns:
        return {
            "simulated_durations": [],
            "percentiles": {},
            "percentile_dates": {},
            "num_work_items": num_work_items,
            "num_iterations": num_iterations,
        }
    cycle_times = df["cycle_time_days"].to_numpy()
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
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    num_iterations: int = 5000,
) -> dict[str, Any]:
    """
    Forecast how many work items can be finished between start_date and end_date using Monte Carlo simulation.

    Parameters:
        df (pd.DataFrame): DataFrame with at least a 'cycle_time_days' column (positive ints/floats)
        start_date (str): Start date for the forecast period (YYYY-MM-DD).
        end_date (str): End date for the forecast period (YYYY-MM-DD).
        num_iterations (int): Number of Monte Carlo simulation runs.

    Returns:
        Dict[str, Any]:
            - 'simulated_work_items': List[int], simulated number of work items completed in each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated work items (keys: as in PERCENTILES)
            - 'start_date': str, start date used for forecast
            - 'end_date': str, end date used for forecast
            - 'num_iterations': int, number of simulation runs
    """
    if df is None or "cycle_time_days" not in df.columns:
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": None,
            "end_date": None,
            "num_iterations": num_iterations,
        }
    cycle_times = df["cycle_time_days"].to_numpy()
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


def get_data_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate basic statistics for a DataFrame with cycle_time_days column.

    Args:
        df: DataFrame with cycle_time_days column

    Returns:
        Dictionary with statistics including min, max, median cycle times and data quality info
    """
    if df is None or df.empty or "cycle_time_days" not in df.columns:
        return {
            "total_items": 0,
            "min_cycle_time": 0,
            "max_cycle_time": 0,
            "median_cycle_time": 0,
            "error": "No valid data available",
        }

    try:
        min_cycle_time = df["cycle_time_days"].min()
        max_cycle_time = df["cycle_time_days"].max()
        median_cycle_time = df["cycle_time_days"].median()
        total_items = len(df)

        return {
            "total_items": total_items,
            "min_cycle_time": min_cycle_time,
            "max_cycle_time": max_cycle_time,
            "median_cycle_time": median_cycle_time,
            "error": None,
        }
    except Exception as e:
        return {
            "total_items": 0,
            "min_cycle_time": 0,
            "max_cycle_time": 0,
            "median_cycle_time": 0,
            "error": f"Error calculating statistics: {str(e)}",
        }

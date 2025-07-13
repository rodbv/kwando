import random
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

PERCENTILES = [70, 80, 90, 95, 98]


def _load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """Load and prepare data from CSV file."""
    if not csv_path or not isinstance(csv_path, str):
        raise ValueError("csv_path must be a non-empty string")

    try:
        df = pd.read_csv(csv_path)
        if "start_date" not in df.columns or "end_date" not in df.columns:
            raise ValueError(
                "CSV must have start_date and end_date columns in ISO 8601 format."
            )
        return _convert_dates_to_cycle_time(df)
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Could not load data: {str(e)}") from e
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Could not load data: {str(e)}") from e


def _convert_dates_to_cycle_time(df: pd.DataFrame) -> pd.DataFrame:
    """Convert start_date and end_date columns to cycle_time_days."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")

    if "start_date" not in df.columns or "end_date" not in df.columns:
        return df

    df_copy = df.copy()
    for col in ["start_date", "end_date"]:
        df_copy[col] = pd.to_datetime(df_copy[col], format="mixed", errors="coerce")

    start_dates = df_copy["start_date"].dt.date
    end_dates = df_copy["end_date"].dt.date

    date_diff = [
        (ed - sd).days if pd.notnull(ed) and pd.notnull(sd) else float("nan")
        for sd, ed in zip(start_dates, end_dates, strict=True)
    ]
    date_diff = pd.Series(date_diff, index=df_copy.index)
    cycle_time = date_diff.apply(lambda d: max(1, int(d) + 1) if pd.notnull(d) else 1)
    df_copy["cycle_time_days"] = cycle_time.astype(int)

    return df_copy


def _forecast_days_for_work_items(
    df: pd.DataFrame,
    num_work_items: int,
    num_iterations: int = 5000,
) -> dict[str, Any]:
    """Forecast days for work items using Monte Carlo simulation."""
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

    percentile_dates = {}
    for k, v in percentiles.items():
        try:
            percentile_dates[k] = (start_ts + pd.Timedelta(days=v)).date().isoformat()
        except (ValueError, TypeError):
            percentile_dates[k] = None

    return {
        "simulated_durations": simulated_totals,
        "percentiles": percentiles,
        "percentile_dates": percentile_dates,
        "num_work_items": num_work_items,
        "num_iterations": num_iterations,
    }


def _forecast_work_items_in_period(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    num_iterations: int = 5000,
) -> dict[str, Any]:
    """Forecast work items in period using Monte Carlo simulation."""
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
        start_date_str = start_ts.date().isoformat() if start_ts is not pd.NaT else None
        end_date_str = end_ts.date().isoformat() if end_ts is not pd.NaT else None
        return {
            "simulated_work_items": [],
            "percentiles": {},
            "start_date": start_date_str,
            "end_date": end_date_str,
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

    start_date_str = start_ts.date().isoformat() if start_ts is not pd.NaT else None
    end_date_str = end_ts.date().isoformat() if end_ts is not pd.NaT else None

    return {
        "simulated_work_items": simulated_work_items,
        "percentiles": percentiles,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "num_iterations": num_iterations,
    }


def _get_data_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Get data statistics from DataFrame."""
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


class MonteCarloSimulator:
    """Monte Carlo simulation for forecasting work item completion."""

    def __init__(self, data: str | pd.DataFrame) -> None:
        """Initialize simulator with data.

        Args:
            data: CSV file path or pandas DataFrame with work item data

        Raises:
            ValueError: If data is invalid or missing required columns
        """
        if data is None:
            raise ValueError("Data cannot be None. Provide a CSV path or DataFrame.")

        if isinstance(data, str):
            if not data.strip():
                raise ValueError("CSV path cannot be empty")
            self.df = _load_and_prepare_data(data)
        elif isinstance(data, pd.DataFrame):
            if data.empty:
                raise ValueError("DataFrame cannot be empty")
            self.df = _convert_dates_to_cycle_time(data)
        else:
            raise ValueError("Data must be a CSV path (str) or pandas DataFrame")

        # Validate that we have cycle time data
        if "cycle_time_days" not in self.df.columns:
            raise ValueError(
                "Data must contain start_date and end_date columns to calculate cycle times"
            )

    def forecast_days_for_work_items(
        self, num_work_items: int, num_iterations: int = 5000
    ) -> dict[str, Any]:
        """Forecast when N work items will be completed.

        Args:
            num_work_items: Number of work items to forecast
            num_iterations: Number of Monte Carlo iterations (default: 5000)

        Returns:
            Dictionary with forecast results including percentiles and dates

        Raises:
            ValueError: If parameters are invalid
        """
        if num_work_items <= 0:
            raise ValueError("num_work_items must be positive")
        if num_iterations <= 0:
            raise ValueError("num_iterations must be positive")

        return _forecast_days_for_work_items(self.df, num_work_items, num_iterations)

    def forecast_work_items_in_period(
        self, start_date: str, end_date: str, num_iterations: int = 5000
    ) -> dict[str, Any]:
        """Forecast how many work items can be completed in a time period.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            num_iterations: Number of Monte Carlo iterations (default: 5000)

        Returns:
            Dictionary with forecast results including percentiles

        Raises:
            ValueError: If parameters are invalid
        """
        if not start_date or not isinstance(start_date, str):
            raise ValueError("start_date must be a non-empty string")
        if not end_date or not isinstance(end_date, str):
            raise ValueError("end_date must be a non-empty string")
        if num_iterations <= 0:
            raise ValueError("num_iterations must be positive")

        # Validate date format
        try:
            pd.Timestamp(start_date)
            pd.Timestamp(end_date)
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}") from e

        return _forecast_work_items_in_period(
            self.df, start_date, end_date, num_iterations
        )

    def get_data_statistics(self) -> dict[str, Any]:
        """Get statistics about the loaded data.

        Returns:
            Dictionary with data statistics
        """
        return _get_data_statistics(self.df)

    @staticmethod
    def get_next_business_day() -> date:
        """Get the next business day from today.

        Returns:
            Next business day as date object
        """
        next_day = datetime.now() + timedelta(days=1)
        while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            next_day += timedelta(days=1)
        return next_day.date()

    @property
    def data_summary(self) -> dict[str, Any]:
        """Get a summary of the loaded data.

        Returns:
            Dictionary with data summary information
        """
        if self.df.empty:
            return {"total_items": 0, "has_cycle_times": False}

        return {
            "total_items": len(self.df),
            "has_cycle_times": "cycle_time_days" in self.df.columns,
            "columns": list(self.df.columns),
        }

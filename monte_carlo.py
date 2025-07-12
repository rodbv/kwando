import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any, Optional

PERCENTILES = [70, 80, 90, 95, 98]


def forecast_days_for_work_items(
    num_work_items: int,
    filename: str = "notebooks/data.csv",
    project: Optional[int] = None,
    num_iterations: int = 5000,
    min_date: str = "2018-01-01",
    start_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Forecast the number of days required to finish the next `num_work_items` work items using Monte Carlo simulation.

    Parameters:
        num_work_items (int): Number of work items to forecast completion for.
        filename (str): Path to the CSV file with work item data.
        project (Optional[int]): Project group to filter on (column 'grp'). If None, use all projects.
        num_iterations (int): Number of Monte Carlo simulation runs.
        min_date (str): Minimum created_date to include (YYYY-MM-DD).
        start_date (str, optional): Start date for the forecast (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict[str, Any]: Dictionary with simulation results and parameters:
            - 'simulated_durations': List[int], simulated durations (in days) for each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated durations (keys: as in PERCENTILES)
            - 'percentile_dates': Dict[str, str], projected completion dates for each percentile (ISO format)
            - 'num_work_items': int, number of work items requested
            - 'project': int or None, project group used
            - 'num_iterations': int, number of simulation runs
            - 'min_date': str, minimum date used for filtering
            - 'start_date': str, start date used for forecast
    """
    # Load and clean data
    df = pd.read_csv(filename, parse_dates=["created_date"])
    cleaned = df[(df["created_date"] > min_date) & (df["cycle_time_days"] > -1)]
    if project is not None:
        cycle_times = cleaned[cleaned["grp"] == project]["cycle_time_days"].values
    else:
        cycle_times = cleaned["cycle_time_days"].values

    def cumulative_sum(total_work_items, cycle_times, selector):
        total = [0]
        for _ in range(total_work_items):
            total.append(selector(cycle_times) + total[-1])
        return total

    # Monte Carlo simulation
    simulated_totals = []
    for _ in range(num_iterations):
        walk = cumulative_sum(num_work_items, cycle_times, random.choice)
        simulated_totals.append(walk[-1])

    percentiles = {
        str(p): float(np.quantile(simulated_totals, p / 100)) for p in PERCENTILES
    }

    # Handle start_date
    if start_date is None:
        start_ts = pd.Timestamp.today().normalize()
    else:
        start_ts = pd.Timestamp(start_date)

    percentile_dates = {
        k: (start_ts + pd.Timedelta(days=v)).date().isoformat()
        for k, v in percentiles.items()
    }

    return {
        "simulated_durations": simulated_totals,
        "percentiles": percentiles,
        "percentile_dates": percentile_dates,
        "num_work_items": num_work_items,
        "project": project,
        "num_iterations": num_iterations,
        "min_date": min_date,
        "start_date": start_ts.date().isoformat(),
    }


def forecast_work_items_in_period(
    start_date: str,
    end_date: str,
    filename: str = "notebooks/data.csv",
    project: Optional[int] = None,
    num_iterations: int = 5000,
    min_date: str = "2018-01-01",
) -> Dict[str, Any]:
    """
    Forecast how many work items can be finished between start_date and end_date using Monte Carlo simulation.

    Parameters:
        start_date (str): Start date for the forecast period (YYYY-MM-DD).
        end_date (str): End date for the forecast period (YYYY-MM-DD).
        filename (str): Path to the CSV file with work item data.
        project (Optional[int]): Project group to filter on (column 'grp'). If None, use all projects.
        num_iterations (int): Number of Monte Carlo simulation runs.
        min_date (str): Minimum created_date to include (YYYY-MM-DD).

    Returns:
        Dict[str, Any]: Dictionary with simulation results and parameters:
            - 'simulated_work_items': List[int], simulated number of work items completed in each simulation run
            - 'percentiles': Dict[str, float], percentiles of simulated work items (keys: as in PERCENTILES)
            - 'start_date': str, start date used for forecast
            - 'end_date': str, end date used for forecast
            - 'project': int or None, project group used
            - 'num_iterations': int, number of simulation runs
            - 'min_date': str, minimum date used for filtering
    """
    # Load and clean data
    df = pd.read_csv(filename, parse_dates=["created_date"])
    cleaned = df[(df["created_date"] > min_date) & (df["cycle_time_days"] > -1)]
    if project is not None:
        cycle_times = cleaned[cleaned["grp"] == project]["cycle_time_days"].values
    else:
        cycle_times = cleaned["cycle_time_days"].values

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    max_days = (end_ts - start_ts).days

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
        "start_date": start_ts.date().isoformat(),
        "end_date": end_ts.date().isoformat(),
        "project": project,
        "num_iterations": num_iterations,
        "min_date": min_date,
    }

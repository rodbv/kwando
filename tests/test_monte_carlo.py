import pandas as pd
import pytest
from monte_carlo import forecast_days_for_work_items, forecast_work_items_in_period


@pytest.fixture
def minimal_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "cycle_time_days": [2, 4, 6],
            "tags": ["a", "b", "c"],
        }
    )


def test_forecast_days_for_work_items_when_dataframe_is_valid_should_return_expected_results(
    minimal_df,
):
    result = forecast_days_for_work_items(
        minimal_df, num_work_items=2, num_iterations=100
    )
    assert set(result.keys()) == {
        "simulated_durations",
        "percentiles",
        "percentile_dates",
        "num_work_items",
        "num_iterations",
    }
    assert len(result["simulated_durations"]) == 100
    assert result["percentiles"]


def test_forecast_days_for_work_items_when_dataframe_is_empty_should_return_empty_results():
    empty_df = pd.DataFrame({"id": [], "cycle_time_days": [], "tags": []})
    result = forecast_days_for_work_items(empty_df, num_work_items=2, num_iterations=10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}
    assert result["num_work_items"] == 2
    assert result["num_iterations"] == 10


def test_forecast_days_for_work_items_when_all_cycle_times_are_equal_should_return_equal_percentiles():
    df = pd.DataFrame(
        {"id": [1, 2, 3], "cycle_time_days": [5, 5, 5], "tags": ["a", "b", "c"]}
    )
    result = forecast_days_for_work_items(df, num_work_items=3, num_iterations=50)
    vals = list(result["percentiles"].values())
    assert all(v == vals[0] for v in vals)


def test_forecast_days_for_work_items_when_dataframe_has_one_row_should_return_simulation_results():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [7], "tags": ["a"]})
    result = forecast_days_for_work_items(df, num_work_items=2, num_iterations=10)
    assert len(result["simulated_durations"]) == 10
    import numpy as np

    assert all(
        isinstance(x, (int, float, np.integer, np.floating))
        for x in result["simulated_durations"]
    )


def test_forecast_days_for_work_items_when_cycle_time_column_is_missing_should_return_empty_results():
    df = pd.DataFrame({"id": [1, 2, 3], "tags": ["a", "b", "c"]})
    result = forecast_days_for_work_items(df, num_work_items=2, num_iterations=10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}


def test_forecast_work_items_in_period_when_dataframe_is_valid_should_return_expected_results(
    minimal_df,
):
    result = forecast_work_items_in_period(
        minimal_df, start_date="2024-01-01", end_date="2024-01-10", num_iterations=20
    )
    assert set(result.keys()) == {
        "simulated_work_items",
        "percentiles",
        "start_date",
        "end_date",
        "num_iterations",
    }
    assert len(result["simulated_work_items"]) == 20
    assert result["percentiles"]

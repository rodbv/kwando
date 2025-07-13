from datetime import datetime

import pandas as pd
import pytest
from monte_carlo import (
    convert_dates_to_cycle_time,
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_next_business_day,
)


@pytest.fixture
def minimal_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "cycle_time_days": [2, 4, 6],
            "tags": ["a", "b", "c"],
        }
    )


@pytest.fixture
def dates_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "start_date": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
            ],
            "end_date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-05",
                "2024-01-10",
            ],
            "tags": ["a", "b", "c", "d", "e"],
        }
    )


def test_convert_dates_to_cycle_time_when_dates_are_same_should_return_one_day(
    dates_df,
):
    """Test that same start and end date results in 1 day cycle time."""
    result = convert_dates_to_cycle_time(dates_df)
    assert result.loc[0, "cycle_time_days"] == 1


def test_convert_dates_to_cycle_time_when_dates_are_different_should_calculate_inclusive_days(
    dates_df,
):
    """Test that different dates calculate cycle time correctly (inclusive)."""
    result = convert_dates_to_cycle_time(dates_df)
    assert result.loc[1, "cycle_time_days"] == 2
    assert result.loc[2, "cycle_time_days"] == 3
    assert result.loc[3, "cycle_time_days"] == 5
    assert result.loc[4, "cycle_time_days"] == 10


def test_convert_dates_to_cycle_time_when_no_date_columns_should_return_unchanged():
    """Test that DataFrame without date columns is returned unchanged."""
    df = pd.DataFrame({"id": [1, 2], "cycle_time_days": [2, 4], "tags": ["a", "b"]})
    result = convert_dates_to_cycle_time(df)
    pd.testing.assert_frame_equal(result, df)


def test_convert_dates_to_cycle_time_when_dates_are_invalid_should_return_minimum_one_day():
    """Test that invalid dates result in minimum cycle time of 1 day."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "start_date": ["2024-01-01", "invalid", "2024-01-01"],
            "end_date": ["invalid", "2024-01-02", "2024-01-01"],
            "tags": ["a", "b", "c"],
        }
    )
    result = convert_dates_to_cycle_time(df)
    assert all(result["cycle_time_days"] == 1)


def test_convert_dates_to_cycle_time_when_difference_is_negative_should_return_minimum_one_day():
    """Test that negative date differences result in minimum cycle time of 1 day."""
    df = pd.DataFrame(
        {
            "id": [1],
            "start_date": ["2024-01-02"],
            "end_date": ["2024-01-01"],
            "tags": ["a"],
        }
    )
    result = convert_dates_to_cycle_time(df)
    assert result.loc[0, "cycle_time_days"] == 1


def test_convert_dates_to_cycle_time_when_days_are_fractional_should_round_up():
    """Test that fractional days are rounded up correctly."""
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "start_date": ["2024-01-01 09:00:00", "2024-01-01 09:00:00"],
            "end_date": ["2024-01-01 17:00:00", "2024-01-02 09:00:00"],
            "tags": ["a", "b"],
        }
    )
    result = convert_dates_to_cycle_time(df)
    assert result.loc[0, "cycle_time_days"] == 1
    assert result.loc[1, "cycle_time_days"] == 2


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
        isinstance(x, int | float | np.integer | np.floating)
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


def test_get_next_business_day_when_today_is_weekday_should_return_next_day(mocker):
    """Test that get_next_business_day returns the next day when today is a weekday."""
    mock_datetime = mocker.patch("monte_carlo.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 1)  # Monday
    result = get_next_business_day()
    expected = datetime(2024, 1, 2).date()  # Tuesday
    assert result == expected


def test_get_next_business_day_when_today_is_friday_should_skip_weekend(mocker):
    """Test that get_next_business_day skips weekend when today is Friday."""
    mock_datetime = mocker.patch("monte_carlo.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 5)  # Friday
    result = get_next_business_day()
    expected = datetime(2024, 1, 8).date()  # Monday
    assert result == expected


def test_get_next_business_day_when_today_is_saturday_should_skip_weekend(mocker):
    """Test that get_next_business_day skips weekend when today is Saturday."""
    mock_datetime = mocker.patch("monte_carlo.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 6)  # Saturday
    result = get_next_business_day()
    expected = datetime(2024, 1, 8).date()  # Monday
    assert result == expected


def test_forecast_work_items_in_period_when_start_and_end_date_are_same_should_handle():
    """Test that forecast_work_items_in_period handles same start and end date."""
    df = pd.DataFrame({"id": [1], "cycle_time_days": [2]})
    result = forecast_work_items_in_period(
        df, start_date="2024-01-01", end_date="2024-01-01", num_iterations=10
    )
    assert result["start_date"] == "2024-01-01"
    assert result["end_date"] == "2024-01-01"


def test_forecast_work_items_in_period_when_period_is_too_short_should_return_zero_items():
    """Test that forecast_work_items_in_period returns zero items for very short periods."""
    df = pd.DataFrame({"id": [1], "cycle_time_days": [10]})  # Long cycle time
    result = forecast_work_items_in_period(
        df, start_date="2024-01-01", end_date="2024-01-02", num_iterations=10
    )
    assert all(item == 0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_when_cycle_times_are_mixed_should_handle_correctly():
    """Test that forecast_work_items_in_period handles mixed cycle times correctly."""
    df = pd.DataFrame({"id": [1, 2], "cycle_time_days": [1, 5]})  # Mixed cycle times
    result = forecast_work_items_in_period(
        df, start_date="2024-01-01", end_date="2024-01-03", num_iterations=100
    )
    assert len(result["simulated_work_items"]) == 100
    assert any(item > 0 for item in result["simulated_work_items"])

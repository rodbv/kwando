from datetime import datetime

import pandas as pd
import pytest
from monte_carlo import (
    convert_dates_to_cycle_time,
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_data_statistics,
    get_next_business_day,
    load_and_prepare_data,
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


# Tests for load_and_prepare_data function
def test_load_and_prepare_data_when_csv_has_valid_dates_should_return_dataframe_with_cycle_times(
    tmp_path,
):
    """Test that load_and_prepare_data loads valid CSV and converts dates to cycle times."""
    # Create a temporary CSV file
    csv_content = """id,start_date,end_date
1,2024-01-01,2024-01-01
2,2024-01-01,2024-01-03
3,2024-01-01,2024-01-05"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    result = load_and_prepare_data(str(csv_file))

    assert isinstance(result, pd.DataFrame)
    assert "cycle_time_days" in result.columns
    assert result.loc[0, "cycle_time_days"] == 1
    assert result.loc[1, "cycle_time_days"] == 3
    assert result.loc[2, "cycle_time_days"] == 5


def test_load_and_prepare_data_when_csv_missing_required_columns_should_raise_value_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ValueError when required columns are missing."""
    # Create a temporary CSV file without required columns
    csv_content = """id,some_other_column
1,value1
2,value2"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(
        ValueError, match="CSV must have start_date and end_date columns"
    ):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_csv_is_malformed_should_raise_parser_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ParserError for malformed CSV."""
    # Create a malformed CSV file with unclosed quotes
    csv_content = """id,start_date,end_date
1,2024-01-01,"2024-01-01
2,2024-01-01,2024-01-02"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(pd.errors.ParserError):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_file_does_not_exist_should_raise_exception(
    tmp_path,
):
    """Test that load_and_prepare_data raises exception when file doesn't exist."""
    non_existent_file = tmp_path / "non_existent.csv"

    with pytest.raises(Exception, match="Could not load data"):
        load_and_prepare_data(str(non_existent_file))


# Tests for get_data_statistics function
def test_get_data_statistics_when_dataframe_is_valid_should_return_correct_statistics():
    """Test that get_data_statistics returns correct statistics for valid DataFrame."""
    df = pd.DataFrame({"id": [1, 2, 3, 4, 5], "cycle_time_days": [2, 4, 6, 8, 10]})

    result = get_data_statistics(df)

    assert result["total_items"] == 5
    assert result["min_cycle_time"] == 2
    assert result["max_cycle_time"] == 10
    assert result["median_cycle_time"] == 6.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_is_empty_should_return_error():
    """Test that get_data_statistics returns error for empty DataFrame."""
    df = pd.DataFrame()

    result = get_data_statistics(df)

    assert result["total_items"] == 0
    assert result["min_cycle_time"] == 0
    assert result["max_cycle_time"] == 0
    assert result["median_cycle_time"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_dataframe_is_none_should_return_error():
    """Test that get_data_statistics returns error for None DataFrame."""
    result = get_data_statistics(None)

    assert result["total_items"] == 0
    assert result["min_cycle_time"] == 0
    assert result["max_cycle_time"] == 0
    assert result["median_cycle_time"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_cycle_time_column_missing_should_return_error():
    """Test that get_data_statistics returns error when cycle_time_days column is missing."""
    df = pd.DataFrame({"id": [1, 2, 3], "some_other_column": [2, 4, 6]})

    result = get_data_statistics(df)

    assert result["total_items"] == 0
    assert result["min_cycle_time"] == 0
    assert result["max_cycle_time"] == 0
    assert result["median_cycle_time"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_dataframe_has_single_row_should_return_correct_statistics():
    """Test that get_data_statistics handles single row correctly."""
    df = pd.DataFrame({"id": [1], "cycle_time_days": [5]})

    result = get_data_statistics(df)

    assert result["total_items"] == 1
    assert result["min_cycle_time"] == 5
    assert result["max_cycle_time"] == 5
    assert result["median_cycle_time"] == 5.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_has_mixed_cycle_times_should_calculate_median_correctly():
    """Test that get_data_statistics calculates median correctly for mixed cycle times."""
    df = pd.DataFrame({"id": [1, 2, 3, 4, 5], "cycle_time_days": [1, 3, 5, 7, 9]})

    result = get_data_statistics(df)

    assert result["total_items"] == 5
    assert result["min_cycle_time"] == 1
    assert result["max_cycle_time"] == 9
    assert result["median_cycle_time"] == 5.0
    assert result["error"] is None

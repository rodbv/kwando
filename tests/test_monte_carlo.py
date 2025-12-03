from datetime import datetime

import pandas as pd
import pytest
from monte_carlo import (
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_data_statistics,
    get_next_business_day,
    parse_throughput_from_text,
)


@pytest.fixture
def throughput_df():
    """Fixture with weekly throughput values."""
    return pd.DataFrame(
        {
            "throughput": [5.0, 3.0, 7.0, 4.0, 6.0],
        }
    )


@pytest.fixture
def single_throughput_df():
    """Fixture with single throughput value."""
    return pd.DataFrame(
        {
            "throughput": [5.0],
        }
    )


@pytest.fixture
def zero_throughput_df():
    """Fixture with zero throughput values."""
    return pd.DataFrame(
        {
            "throughput": [0.0, 0.0, 0.0],
        }
    )


def test_forecast_days_for_work_items_when_dataframe_is_valid_should_return_expected_results(
    throughput_df,
):
    """Test that forecast_days_for_work_items returns expected results with valid throughput data."""
    result = forecast_days_for_work_items(
        throughput_df, num_work_items=10, num_iterations=100
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
    # With throughput of 5 items/week on average, 10 items should take about 2 weeks = 14 days
    # Percentiles should be positive
    assert all(v > 0 for v in result["percentiles"].values())


def test_forecast_days_for_work_items_when_dataframe_is_empty_should_return_empty_results():
    """Test that forecast_days_for_work_items returns empty results for empty DataFrame."""
    empty_df = pd.DataFrame({"throughput": []})
    result = forecast_days_for_work_items(empty_df, num_work_items=2, num_iterations=10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}
    assert result["num_work_items"] == 2
    assert result["num_iterations"] == 10


def test_forecast_days_for_work_items_when_all_throughput_values_are_equal_should_return_consistent_results():
    """Test that forecast_days_for_work_items handles constant throughput values."""
    df = pd.DataFrame({"throughput": [5.0, 5.0, 5.0]})
    result = forecast_days_for_work_items(df, num_work_items=10, num_iterations=50)
    # With constant throughput of 5/week, 10 items should take exactly 2 weeks = 14 days
    # But due to simulation, there may be slight variation
    assert len(result["simulated_durations"]) == 50
    assert result["percentiles"]


def test_forecast_days_for_work_items_when_dataframe_has_one_row_should_return_simulation_results(
    single_throughput_df,
):
    """Test that forecast_days_for_work_items works with single throughput value."""
    result = forecast_days_for_work_items(
        single_throughput_df, num_work_items=5, num_iterations=10
    )
    assert len(result["simulated_durations"]) == 10
    import numpy as np

    assert all(
        isinstance(x, int | float | np.integer | np.floating)
        for x in result["simulated_durations"]
    )


def test_forecast_days_for_work_items_when_throughput_column_is_missing_should_return_empty_results():
    """Test that forecast_days_for_work_items returns empty results when throughput column is missing."""
    df = pd.DataFrame({"id": [1, 2, 3]})
    result = forecast_days_for_work_items(df, num_work_items=2, num_iterations=10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}


def test_forecast_work_items_in_period_when_dataframe_is_valid_should_return_expected_results(
    throughput_df,
):
    """Test that forecast_work_items_in_period returns expected results with valid throughput data."""
    result = forecast_work_items_in_period(
        throughput_df, start_date="2024-01-01", end_date="2024-01-15", num_iterations=20
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
    # 14 days = 2 weeks, with avg throughput of 5/week, should get around 10 items
    assert all(item >= 0 for item in result["simulated_work_items"])


def test_get_next_business_day_when_today_is_weekday_should_return_next_day(
    monkeypatch,
):
    """Test that get_next_business_day returns the next day when today is a weekday."""
    from unittest.mock import Mock

    mock_datetime = Mock()
    mock_datetime.now.return_value = datetime(2024, 1, 1)  # Monday
    monkeypatch.setattr("monte_carlo.datetime", mock_datetime)
    result = get_next_business_day()
    expected = datetime(2024, 1, 2).date()  # Tuesday
    assert result == expected


def test_get_next_business_day_when_today_is_friday_should_skip_weekend(monkeypatch):
    """Test that get_next_business_day skips weekend when today is Friday."""
    from unittest.mock import Mock

    mock_datetime = Mock()
    mock_datetime.now.return_value = datetime(2024, 1, 5)  # Friday
    monkeypatch.setattr("monte_carlo.datetime", mock_datetime)
    result = get_next_business_day()
    expected = datetime(2024, 1, 8).date()  # Monday
    assert result == expected


def test_get_next_business_day_when_today_is_saturday_should_skip_weekend(monkeypatch):
    """Test that get_next_business_day skips weekend when today is Saturday."""
    from unittest.mock import Mock

    mock_datetime = Mock()
    mock_datetime.now.return_value = datetime(2024, 1, 6)  # Saturday
    monkeypatch.setattr("monte_carlo.datetime", mock_datetime)
    result = get_next_business_day()
    expected = datetime(2024, 1, 8).date()  # Monday
    assert result == expected


def test_forecast_work_items_in_period_when_start_and_end_date_are_same_should_handle(
    throughput_df,
):
    """Test that forecast_work_items_in_period handles same start and end date."""
    result = forecast_work_items_in_period(
        throughput_df, start_date="2024-01-01", end_date="2024-01-01", num_iterations=10
    )
    assert result["start_date"] == "2024-01-01"
    assert result["end_date"] == "2024-01-01"
    # Same day = 0 days = 0 weeks, so should get 0 items
    assert all(item == 0.0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_when_period_is_short_should_return_some_items(
    throughput_df,
):
    """Test that forecast_work_items_in_period returns items for short periods."""
    # 7 days = 1 week, with throughput of 5/week, should get around 5 items
    result = forecast_work_items_in_period(
        throughput_df, start_date="2024-01-01", end_date="2024-01-08", num_iterations=10
    )
    assert len(result["simulated_work_items"]) == 10
    assert all(item >= 0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_when_throughput_values_are_mixed_should_handle_correctly(
    throughput_df,
):
    """Test that forecast_work_items_in_period handles mixed throughput values correctly."""
    result = forecast_work_items_in_period(
        throughput_df,
        start_date="2024-01-01",
        end_date="2024-01-15",
        num_iterations=100,
    )
    assert len(result["simulated_work_items"]) == 100
    assert any(item > 0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_with_zero_throughput_should_return_zero_items(
    zero_throughput_df,
):
    """Test that forecast_work_items_in_period returns zero items when throughput is zero."""
    result = forecast_work_items_in_period(
        zero_throughput_df,
        start_date="2024-01-01",
        end_date="2024-01-15",
        num_iterations=10,
    )
    assert all(item == 0.0 for item in result["simulated_work_items"])


# Tests for get_data_statistics function
def test_get_data_statistics_when_dataframe_is_valid_should_return_correct_statistics():
    """Test that get_data_statistics returns correct statistics for valid DataFrame."""
    df = pd.DataFrame({"throughput": [2.0, 4.0, 6.0, 8.0, 10.0]})

    result = get_data_statistics(df)

    assert result["total_weeks"] == 5
    assert result["min_throughput"] == 2.0
    assert result["max_throughput"] == 10.0
    assert result["median_throughput"] == 6.0
    assert result["avg_throughput"] == 6.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_is_empty_should_return_error():
    """Test that get_data_statistics returns error for empty DataFrame."""
    df = pd.DataFrame()

    result = get_data_statistics(df)

    assert result["total_weeks"] == 0
    assert result["min_throughput"] == 0
    assert result["max_throughput"] == 0
    assert result["median_throughput"] == 0
    assert result["avg_throughput"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_dataframe_is_none_should_return_error():
    """Test that get_data_statistics returns error for None DataFrame."""
    result = get_data_statistics(None)

    assert result["total_weeks"] == 0
    assert result["min_throughput"] == 0
    assert result["max_throughput"] == 0
    assert result["median_throughput"] == 0
    assert result["avg_throughput"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_throughput_column_missing_should_return_error():
    """Test that get_data_statistics returns error when throughput column is missing."""
    df = pd.DataFrame({"id": [1, 2, 3], "some_other_column": [2, 4, 6]})

    result = get_data_statistics(df)

    assert result["total_weeks"] == 0
    assert result["min_throughput"] == 0
    assert result["max_throughput"] == 0
    assert result["median_throughput"] == 0
    assert result["avg_throughput"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_dataframe_has_single_row_should_return_correct_statistics():
    """Test that get_data_statistics handles single row correctly."""
    df = pd.DataFrame({"throughput": [5.0]})

    result = get_data_statistics(df)

    assert result["total_weeks"] == 1
    assert result["min_throughput"] == 5.0
    assert result["max_throughput"] == 5.0
    assert result["median_throughput"] == 5.0
    assert result["avg_throughput"] == 5.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_has_mixed_throughput_should_calculate_median_correctly():
    """Test that get_data_statistics calculates median correctly for mixed throughput values."""
    df = pd.DataFrame({"throughput": [1.0, 3.0, 5.0, 7.0, 9.0]})

    result = get_data_statistics(df)

    assert result["total_weeks"] == 5
    assert result["min_throughput"] == 1.0
    assert result["max_throughput"] == 9.0
    assert result["median_throughput"] == 5.0
    assert result["avg_throughput"] == 5.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_has_zero_throughput_should_handle():
    """Test that get_data_statistics handles zero throughput values."""
    df = pd.DataFrame({"throughput": [0.0, 5.0, 0.0]})

    result = get_data_statistics(df)

    assert result["total_weeks"] == 3
    assert result["min_throughput"] == 0.0
    assert result["max_throughput"] == 5.0
    assert result["median_throughput"] == 0.0
    assert result["error"] is None


# Tests for parse_throughput_from_text function
def test_parse_throughput_from_text_when_input_is_valid_should_return_dataframe():
    """Test that parse_throughput_from_text returns DataFrame with valid input."""
    result = parse_throughput_from_text("2,3,5,2")

    assert isinstance(result, pd.DataFrame)
    assert "throughput" in result.columns
    assert len(result) == 4
    assert result.loc[0, "throughput"] == 2.0
    assert result.loc[1, "throughput"] == 3.0
    assert result.loc[2, "throughput"] == 5.0
    assert result.loc[3, "throughput"] == 2.0


def test_parse_throughput_from_text_when_input_has_whitespace_should_trim():
    """Test that parse_throughput_from_text trims whitespace around commas."""
    result = parse_throughput_from_text("2, 3, 5, 2")

    assert len(result) == 4
    assert result.loc[0, "throughput"] == 2.0
    assert result.loc[1, "throughput"] == 3.0


def test_parse_throughput_from_text_when_input_has_leading_trailing_whitespace_should_trim():
    """Test that parse_throughput_from_text trims leading and trailing whitespace."""
    result = parse_throughput_from_text("  2,3,5,2  ")

    assert len(result) == 4
    assert result.loc[0, "throughput"] == 2.0


def test_parse_throughput_from_text_when_input_has_decimal_values_should_accept():
    """Test that parse_throughput_from_text accepts decimal values."""
    result = parse_throughput_from_text("2.5,3.7,5.2")

    assert len(result) == 3
    assert result.loc[0, "throughput"] == 2.5
    assert result.loc[1, "throughput"] == 3.7
    assert result.loc[2, "throughput"] == 5.2


def test_parse_throughput_from_text_when_input_is_empty_should_raise_value_error():
    """Test that parse_throughput_from_text raises ValueError for empty input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_throughput_from_text("")


def test_parse_throughput_from_text_when_input_is_whitespace_only_should_raise_value_error():
    """Test that parse_throughput_from_text raises ValueError for whitespace-only input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_throughput_from_text("   ")


def test_parse_throughput_from_text_when_input_has_non_numeric_values_should_raise_value_error():
    """Test that parse_throughput_from_text raises ValueError for non-numeric values."""
    with pytest.raises(ValueError, match="must be numeric"):
        parse_throughput_from_text("2,3,invalid,5")


def test_parse_throughput_from_text_when_input_has_negative_values_should_raise_value_error():
    """Test that parse_throughput_from_text raises ValueError for negative values."""
    with pytest.raises(ValueError, match="must be non-negative"):
        parse_throughput_from_text("2,3,-1,5")


def test_parse_throughput_from_text_when_input_has_zero_values_should_accept():
    """Test that parse_throughput_from_text accepts zero values."""
    result = parse_throughput_from_text("2,0,3,0")

    assert len(result) == 4
    assert result.loc[1, "throughput"] == 0.0
    assert result.loc[3, "throughput"] == 0.0


def test_parse_throughput_from_text_when_input_has_single_value_should_accept():
    """Test that parse_throughput_from_text handles single value."""
    result = parse_throughput_from_text("5")

    assert len(result) == 1
    assert result.loc[0, "throughput"] == 5.0


def test_parse_throughput_from_text_when_input_has_many_commas_should_handle():
    """Test that parse_throughput_from_text handles multiple consecutive commas."""
    result = parse_throughput_from_text("2,,3,5")

    # Should filter out empty values
    assert len(result) == 3
    assert result.loc[0, "throughput"] == 2.0
    assert result.loc[1, "throughput"] == 3.0
    assert result.loc[2, "throughput"] == 5.0


def test_parse_throughput_from_text_when_input_exceeds_limit_should_raise_value_error():
    """Test that parse_throughput_from_text raises ValueError for too many values."""
    # Create input with 1001 values
    large_input = ",".join(["1"] * 1001)

    with pytest.raises(ValueError, match="Too many values"):
        parse_throughput_from_text(large_input)


def test_parse_throughput_from_text_when_input_has_exactly_1000_values_should_accept():
    """Test that parse_throughput_from_text accepts exactly 1000 values."""
    # Create input with exactly 1000 values
    large_input = ",".join(["1"] * 1000)

    result = parse_throughput_from_text(large_input)
    assert len(result) == 1000


def test_parse_throughput_from_text_when_used_with_forecast_should_work():
    """Test that parse_throughput_from_text output works with forecasting functions."""
    df = parse_throughput_from_text("5,3,7,4,6")

    result = forecast_days_for_work_items(df, num_work_items=10, num_iterations=10)

    assert len(result["simulated_durations"]) == 10
    assert result["percentiles"]
    assert all(v > 0 for v in result["percentiles"].values())


def test_parse_throughput_from_text_when_used_with_statistics_should_work():
    """Test that parse_throughput_from_text output works with statistics function."""
    df = parse_throughput_from_text("2,4,6,8,10")

    result = get_data_statistics(df)

    assert result["total_weeks"] == 5
    assert result["min_throughput"] == 2.0
    assert result["max_throughput"] == 10.0
    assert result["median_throughput"] == 6.0
    assert result["avg_throughput"] == 6.0
    assert result["error"] is None

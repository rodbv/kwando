from datetime import datetime

import pandas as pd
import pytest
from monte_carlo import (
    forecast_days_for_work_items,
    forecast_work_items_in_period,
    get_data_statistics,
    get_next_business_day,
    load_and_prepare_data,
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


# Tests for load_and_prepare_data function
def test_load_and_prepare_data_when_csv_has_valid_throughput_should_return_dataframe(
    tmp_path,
):
    """Test that load_and_prepare_data loads valid CSV with throughput column."""
    csv_content = """throughput
5.0
3.0
7.0
4.0"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    result = load_and_prepare_data(str(csv_file))

    assert isinstance(result, pd.DataFrame)
    assert "throughput" in result.columns
    assert len(result) == 4
    assert result.loc[0, "throughput"] == 5.0
    assert result.loc[1, "throughput"] == 3.0


def test_load_and_prepare_data_when_csv_missing_throughput_column_should_raise_value_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ValueError when throughput column is missing."""
    csv_content = """id,some_other_column
1,value1
2,value2"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(ValueError, match="CSV must have a 'throughput' column"):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_csv_has_non_numeric_throughput_should_raise_value_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ValueError for non-numeric throughput values."""
    csv_content = """throughput
5.0
invalid
7.0"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(ValueError, match="Throughput values must be numeric"):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_csv_has_negative_throughput_should_raise_value_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ValueError for negative throughput values."""
    csv_content = """throughput
5.0
-1.0
7.0"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(ValueError, match="Throughput values must be non-negative"):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_csv_has_zero_throughput_should_accept(tmp_path):
    """Test that load_and_prepare_data accepts zero throughput values."""
    csv_content = """throughput
5.0
0.0
7.0"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    result = load_and_prepare_data(str(csv_file))
    assert len(result) == 3
    assert result.loc[1, "throughput"] == 0.0


def test_load_and_prepare_data_when_csv_has_missing_values_should_raise_value_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ValueError for missing throughput values."""
    # Create CSV with NaN value explicitly
    import numpy as np

    df = pd.DataFrame({"throughput": [5.0, np.nan, 7.0]})
    csv_file = tmp_path / "test_data.csv"
    df.to_csv(csv_file, index=False)

    with pytest.raises(ValueError, match="Throughput column contains missing values"):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_csv_is_malformed_should_raise_parser_error(
    tmp_path,
):
    """Test that load_and_prepare_data raises ParserError for malformed CSV."""
    # Create a truly malformed CSV with unclosed quotes
    csv_content = """throughput
5.0,""unclosed quote
7.0"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    with pytest.raises((pd.errors.ParserError, ValueError)):
        load_and_prepare_data(str(csv_file))


def test_load_and_prepare_data_when_file_does_not_exist_should_raise_exception(
    tmp_path,
):
    """Test that load_and_prepare_data raises exception when file doesn't exist."""
    non_existent_file = tmp_path / "non_existent.csv"

    with pytest.raises(Exception, match="Could not load data"):
        load_and_prepare_data(str(non_existent_file))


def test_load_and_prepare_data_when_csv_has_decimal_throughput_should_accept(tmp_path):
    """Test that load_and_prepare_data accepts decimal throughput values."""
    csv_content = """throughput
5.5
3.2
7.8"""

    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    result = load_and_prepare_data(str(csv_file))
    assert len(result) == 3
    assert result.loc[0, "throughput"] == 5.5


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

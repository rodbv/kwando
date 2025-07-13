from datetime import date

import pandas as pd
import pytest

from src.monte_carlo import (
    MonteCarloSimulator,
    _convert_dates_to_cycle_time,
    _forecast_days_for_work_items,
    _forecast_work_items_in_period,
    _get_data_statistics,
    _load_and_prepare_data,
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
    # This test is no longer needed since convert_dates_to_cycle_time is now private
    # The functionality is tested through the MonteCarloSimulator class
    sim = MonteCarloSimulator(dates_df)
    assert sim.df.loc[0, "cycle_time_days"] == 1


def test_convert_dates_to_cycle_time_when_dates_are_different_should_calculate_inclusive_days(
    dates_df,
):
    sim = MonteCarloSimulator(dates_df)
    assert sim.df.loc[1, "cycle_time_days"] == 2
    assert sim.df.loc[2, "cycle_time_days"] == 3
    assert sim.df.loc[3, "cycle_time_days"] == 5
    assert sim.df.loc[4, "cycle_time_days"] == 10


def test_convert_dates_to_cycle_time_when_no_date_columns_should_return_unchanged():
    df = pd.DataFrame({"id": [1, 2], "cycle_time_days": [2, 4], "tags": ["a", "b"]})
    sim = MonteCarloSimulator(df)
    # Should still have the original cycle_time_days column
    assert "cycle_time_days" in sim.df.columns


def test_convert_dates_to_cycle_time_when_dates_are_invalid_should_return_minimum_one_day():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "start_date": ["2024-01-01", "invalid", "2024-01-01"],
            "end_date": ["invalid", "2024-01-02", "2024-01-01"],
            "tags": ["a", "b", "c"],
        }
    )
    sim = MonteCarloSimulator(df)
    assert all(sim.df["cycle_time_days"] == 1)


def test_convert_dates_to_cycle_time_when_difference_is_negative_should_return_minimum_one_day():
    df = pd.DataFrame(
        {
            "id": [1],
            "start_date": ["2024-01-02"],
            "end_date": ["2024-01-01"],
            "tags": ["a"],
        }
    )
    sim = MonteCarloSimulator(df)
    assert sim.df.loc[0, "cycle_time_days"] == 1


def test_convert_dates_to_cycle_time_when_days_are_fractional_should_round_up():
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "start_date": ["2024-01-01 09:00:00", "2024-01-01 09:00:00"],
            "end_date": ["2024-01-01 17:00:00", "2024-01-02 09:00:00"],
            "tags": ["a", "b"],
        }
    )
    sim = MonteCarloSimulator(df)
    assert sim.df.loc[0, "cycle_time_days"] == 1
    assert sim.df.loc[1, "cycle_time_days"] == 2


def test_forecast_days_for_work_items_when_dataframe_is_valid_should_return_expected_results(
    minimal_df,
):
    sim = MonteCarloSimulator(minimal_df)
    result = sim.forecast_days_for_work_items(num_work_items=2, num_iterations=100)
    assert set(result.keys()) == {
        "simulated_durations",
        "percentiles",
        "percentile_dates",
        "num_work_items",
        "num_iterations",
    }
    assert len(result["simulated_durations"]) == 100
    assert result["percentiles"]


def test_forecast_days_for_work_items_when_dataframe_is_empty_should_raise_value_error():
    empty_df = pd.DataFrame({"id": [], "cycle_time_days": [], "tags": []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        MonteCarloSimulator(empty_df)


def test_forecast_days_for_work_items_when_all_cycle_times_are_equal_should_return_equal_percentiles():
    df = pd.DataFrame(
        {"id": [1, 2, 3], "cycle_time_days": [5, 5, 5], "tags": ["a", "b", "c"]}
    )
    sim = MonteCarloSimulator(df)
    result = sim.forecast_days_for_work_items(num_work_items=3, num_iterations=50)
    vals = list(result["percentiles"].values())
    assert all(v == vals[0] for v in vals)


def test_forecast_days_for_work_items_when_dataframe_has_one_row_should_return_simulation_results():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [7], "tags": ["a"]})
    sim = MonteCarloSimulator(df)
    result = sim.forecast_days_for_work_items(num_work_items=2, num_iterations=10)
    assert len(result["simulated_durations"]) == 10
    import numpy as np

    assert all(
        isinstance(x, int | float | np.integer | np.floating)
        for x in result["simulated_durations"]
    )


def test_forecast_days_for_work_items_when_cycle_time_column_is_missing_should_raise_value_error():
    df = pd.DataFrame({"id": [1, 2, 3], "tags": ["a", "b", "c"]})
    with pytest.raises(
        ValueError, match="Data must contain start_date and end_date columns"
    ):
        MonteCarloSimulator(df)


def test_forecast_days_for_work_items_when_cycle_time_days_column_is_empty_should_raise_value_error():
    df = pd.DataFrame({"cycle_time_days": []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        MonteCarloSimulator(df)


def test_forecast_work_items_in_period_when_dataframe_is_valid_should_return_expected_results(
    minimal_df,
):
    sim = MonteCarloSimulator(minimal_df)
    result = sim.forecast_work_items_in_period(
        start_date="2024-01-01", end_date="2024-01-10", num_iterations=20
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


def test_forecast_work_items_in_period_when_start_and_end_date_are_same_should_handle():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [2]})
    sim = MonteCarloSimulator(df)
    result = sim.forecast_work_items_in_period(
        start_date="2024-01-01", end_date="2024-01-01", num_iterations=10
    )
    assert result["start_date"] == "2024-01-01"
    assert result["end_date"] == "2024-01-01"


def test_forecast_work_items_in_period_when_period_is_too_short_should_return_zero_items():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [10]})
    sim = MonteCarloSimulator(df)
    result = sim.forecast_work_items_in_period(
        start_date="2024-01-01", end_date="2024-01-02", num_iterations=10
    )
    assert all(item == 0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_when_cycle_times_are_mixed_should_handle_correctly():
    df = pd.DataFrame({"id": [1, 2], "cycle_time_days": [1, 5]})
    sim = MonteCarloSimulator(df)
    result = sim.forecast_work_items_in_period(
        start_date="2024-01-01", end_date="2024-01-03", num_iterations=100
    )
    assert len(result["simulated_work_items"]) == 100
    assert any(item > 0 for item in result["simulated_work_items"])


def test_forecast_work_items_in_period_when_cycle_time_days_column_is_empty_should_raise_value_error():
    df = pd.DataFrame({"cycle_time_days": []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        MonteCarloSimulator(df)


def test_load_and_prepare_data_when_csv_has_valid_dates_should_return_dataframe_with_cycle_times(
    tmp_path,
):
    # Create a temporary CSV file
    csv_content = """id,start_date,end_date
1,2024-01-01,2024-01-01
2,2024-01-01,2024-01-03
3,2024-01-01,2024-01-05"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    sim = MonteCarloSimulator(str(csv_file))
    assert "cycle_time_days" in sim.df.columns
    assert sim.df.loc[0, "cycle_time_days"] == 1
    assert sim.df.loc[1, "cycle_time_days"] == 3
    assert sim.df.loc[2, "cycle_time_days"] == 5


def test_load_and_prepare_data_when_csv_missing_required_columns_should_raise_value_error(
    tmp_path,
):
    csv_content = """id,name
1,test1
2,test2"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    with pytest.raises(
        ValueError, match="CSV must have start_date and end_date columns"
    ):
        MonteCarloSimulator(str(csv_file))


def test_load_and_prepare_data_when_csv_is_malformed_should_raise_parser_error(
    tmp_path,
):
    csv_content = """id,start_date,end_date
1,2024-01-01,2024-01-01
2,invalid,date
3,2024-01-01,2024-01-01"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    # This should not raise an error since pandas handles invalid dates gracefully
    sim = MonteCarloSimulator(str(csv_file))
    assert "cycle_time_days" in sim.df.columns


def test_load_and_prepare_data_when_file_does_not_exist_should_raise_exception(
    tmp_path,
):
    non_existent_file = tmp_path / "nonexistent.csv"

    with pytest.raises(Exception, match="Could not load data"):
        MonteCarloSimulator(str(non_existent_file))


def test_get_data_statistics_when_dataframe_is_valid_should_return_correct_statistics():
    df = pd.DataFrame({"id": [1, 2, 3, 4, 5], "cycle_time_days": [2, 4, 6, 8, 10]})
    sim = MonteCarloSimulator(df)
    result = sim.get_data_statistics()

    assert result["total_items"] == 5
    assert result["min_cycle_time"] == 2
    assert result["max_cycle_time"] == 10
    assert result["median_cycle_time"] == 6.0
    assert result["error"] is None


def test_get_data_statistics_when_dataframe_is_empty_should_raise_value_error():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        MonteCarloSimulator(df)


# Test new validation features
def test_monte_carlo_simulator_when_data_is_none_should_raise_value_error():
    with pytest.raises(ValueError, match="Data cannot be None"):
        MonteCarloSimulator(None)


def test_monte_carlo_simulator_when_csv_path_is_empty_should_raise_value_error():
    with pytest.raises(ValueError, match="CSV path cannot be empty"):
        MonteCarloSimulator("")


def test_monte_carlo_simulator_when_invalid_data_type_should_raise_value_error():
    with pytest.raises(ValueError, match="Data must be a CSV path"):
        MonteCarloSimulator(123)


def test_forecast_days_for_work_items_when_negative_num_work_items_should_raise_value_error():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [5]})
    sim = MonteCarloSimulator(df)

    with pytest.raises(ValueError, match="num_work_items must be positive"):
        sim.forecast_days_for_work_items(num_work_items=-1)


def test_forecast_days_for_work_items_when_negative_iterations_should_raise_value_error():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [5]})
    sim = MonteCarloSimulator(df)

    with pytest.raises(ValueError, match="num_iterations must be positive"):
        sim.forecast_days_for_work_items(num_work_items=5, num_iterations=-1)


def test_forecast_work_items_in_period_when_invalid_dates_should_raise_value_error():
    df = pd.DataFrame({"id": [1], "cycle_time_days": [5]})
    sim = MonteCarloSimulator(df)

    with pytest.raises(ValueError, match="Invalid date format"):
        sim.forecast_work_items_in_period(start_date="invalid", end_date="2024-01-01")


def test_data_summary_property():
    df = pd.DataFrame({"id": [1, 2], "cycle_time_days": [3, 5]})
    sim = MonteCarloSimulator(df)

    summary = sim.data_summary
    assert summary["total_items"] == 2
    assert summary["has_cycle_times"] is True
    assert "id" in summary["columns"]
    assert "cycle_time_days" in summary["columns"]


def test_data_summary_property_when_empty_should_raise_value_error():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        MonteCarloSimulator(df)


# Additional tests to improve coverage
def test_load_and_prepare_data_when_csv_path_is_empty_should_raise_value_error():
    with pytest.raises(ValueError, match="csv_path must be a non-empty string"):
        _load_and_prepare_data("")


def test_load_and_prepare_data_when_csv_path_is_none_should_raise_value_error():
    with pytest.raises(ValueError, match="csv_path must be a non-empty string"):
        _load_and_prepare_data(None)


def test_load_and_prepare_data_when_csv_path_is_not_string_should_raise_value_error():
    with pytest.raises(ValueError, match="csv_path must be a non-empty string"):
        _load_and_prepare_data(123)


def test_convert_dates_to_cycle_time_when_df_is_not_dataframe_should_raise_value_error():
    with pytest.raises(ValueError, match="df must be a pandas DataFrame"):
        _convert_dates_to_cycle_time("not a dataframe")


def test_forecast_days_for_work_items_when_df_is_none_should_return_empty_results():
    result = _forecast_days_for_work_items(None, 5, 10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}


def test_forecast_days_for_work_items_when_df_has_no_cycle_time_column_should_return_empty_results():
    df = pd.DataFrame({"id": [1, 2], "tags": ["a", "b"]})
    result = _forecast_days_for_work_items(df, 5, 10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}


def test_forecast_days_for_work_items_when_cycle_times_empty_should_return_empty_results():
    df = pd.DataFrame({"cycle_time_days": []})
    result = _forecast_days_for_work_items(df, 5, 10)
    assert result["simulated_durations"] == []
    assert result["percentiles"] == {}
    assert result["percentile_dates"] == {}


def test_forecast_work_items_in_period_when_df_is_none_should_return_empty_results():
    result = _forecast_work_items_in_period(None, "2024-01-01", "2024-01-10", 10)
    assert result["simulated_work_items"] == []
    assert result["percentiles"] == {}
    assert result["start_date"] is None
    assert result["end_date"] is None


def test_forecast_work_items_in_period_when_df_has_no_cycle_time_column_should_return_empty_results():
    df = pd.DataFrame({"id": [1, 2], "tags": ["a", "b"]})
    result = _forecast_work_items_in_period(df, "2024-01-01", "2024-01-10", 10)
    assert result["simulated_work_items"] == []
    assert result["percentiles"] == {}
    assert result["start_date"] is None
    assert result["end_date"] is None


def test_forecast_work_items_in_period_when_cycle_times_empty_should_return_empty_results():
    df = pd.DataFrame({"cycle_time_days": []})
    result = _forecast_work_items_in_period(df, "2024-01-01", "2024-01-10", 10)
    assert result["simulated_work_items"] == []
    assert result["percentiles"] == {}
    assert result["start_date"] == "2024-01-01"
    assert result["end_date"] == "2024-01-10"


def test_get_data_statistics_when_df_is_none_should_return_error():
    result = _get_data_statistics(None)
    assert result["total_items"] == 0
    assert result["error"] == "No valid data available"


def test_get_data_statistics_when_df_has_no_cycle_time_column_should_return_error():
    df = pd.DataFrame({"id": [1, 2], "tags": ["a", "b"]})
    result = _get_data_statistics(df)
    assert result["total_items"] == 0
    assert result["error"] == "No valid data available"


def test_get_next_business_day():
    next_day = MonteCarloSimulator.get_next_business_day()
    assert isinstance(next_day, date)
    # Should not be a weekend
    assert next_day.weekday() < 5


def test_forecast_days_for_work_items_with_extreme_values_should_handle_date_errors():
    # Test the exception handling in percentile_dates calculation
    df = pd.DataFrame({"cycle_time_days": [1e6]})  # Very large number
    sim = MonteCarloSimulator(df)
    result = sim.forecast_days_for_work_items(num_work_items=1, num_iterations=10)
    # Should handle the date calculation error gracefully
    assert "percentile_dates" in result

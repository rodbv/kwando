# Change: Convert Forecasting to Throughput-Based

## Why

The current forecasting system uses cycle-time-based Monte Carlo simulation, which samples from historical cycle times (how long each work item took) and accumulates them to forecast completion. Throughput-based forecasting instead samples from historical throughput rates (how many items were completed per time period), which can provide more accurate forecasts in many scenarios, especially when work items are processed in parallel or when the system's capacity is better represented by completion rate rather than individual item duration.

Issue #13 requests converting the forecasting mechanism to use throughput-based calculations instead of cycle-time-based calculations.

## What Changes

- **BREAKING**: CSV file format changes - CSV files must now include a `throughput` column with weekly throughput values (one value per line)
- **BREAKING**: Data preparation logic changes from calculating cycle times to reading throughput values directly from CSV
- **BREAKING**: Monte Carlo simulation logic changes from sampling cycle times to sampling weekly throughput rates
- **BREAKING**: Forecasting functions (`forecast_days_for_work_items` and `forecast_work_items_in_period`) are refactored to use weekly throughput-based calculations
- Data statistics display will show weekly throughput metrics instead of cycle time metrics
- Help documentation updated to explain throughput-based forecasting and new CSV format requirements

## Impact

- Affected specs: New `forecasting` capability specification
- Affected code:
  - `src/monte_carlo.py` - Core forecasting logic (no longer calculates cycle times)
  - `src/dashboard.py` - UI and data display
  - `docs/monte_carlo_help.md` - User documentation
  - `README.md` - CSV format documentation
  - `tests/test_monte_carlo.py` - Test suite needs updates
  - Sample CSV files in `data/` directory may need updates to include throughput column

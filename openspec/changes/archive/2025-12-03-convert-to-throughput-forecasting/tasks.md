## 1. Data Preparation
- [x] 1.1 Update `load_and_prepare_data` to read `throughput` column from CSV instead of calculating cycle times
- [x] 1.2 Add validation for throughput column (must exist, numeric, non-negative)
- [x] 1.3 Handle edge cases (empty CSV, single row, all zeros)
- [x] 1.4 Remove cycle time calculation logic (no longer needed)

## 2. Forecasting Logic
- [x] 2.1 Refactor `forecast_days_for_work_items` to use weekly throughput-based simulation
- [x] 2.2 Refactor `forecast_work_items_in_period` to use weekly throughput-based simulation
- [x] 2.3 Update simulation logic to sample from weekly throughput values instead of cycle times
- [x] 2.4 Convert weeks to calendar days when forecasting completion dates
- [x] 2.5 Ensure percentile calculations remain accurate with new approach

## 3. Data Statistics
- [x] 3.1 Update `get_data_statistics` to calculate weekly throughput metrics (avg, min, max, median)
- [x] 3.2 Update dashboard to display weekly throughput statistics
- [x] 3.3 Update data preview to show throughput values from CSV

## 4. Documentation
- [x] 4.1 Update `docs/monte_carlo_help.md` to explain weekly throughput-based forecasting
- [x] 4.2 Update README.md to document new CSV format (must include `throughput` column)
- [x] 4.3 Update CSV format documentation to show example with throughput column
- [x] 4.4 Update sample CSV files in `data/` directory to include throughput column

## 5. Testing
- [x] 5.1 Update existing tests in `tests/test_monte_carlo.py` for weekly throughput-based logic
- [x] 5.2 Add tests for reading throughput column from CSV
- [x] 5.3 Add tests for validation (missing column, invalid values, negative values)
- [x] 5.4 Add tests for edge cases (single row, all zeros, empty CSV)
- [x] 5.5 Verify forecast accuracy with sample datasets containing throughput values
- [x] 5.6 Run full test suite to ensure no regressions

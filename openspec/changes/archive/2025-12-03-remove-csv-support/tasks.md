## 1. Dashboard UI Changes
- [x] 1.1 Remove CSV file upload widget (`file_input`)
- [x] 1.2 Remove CSV file selector widget (`file_selector`)
- [x] 1.3 Remove input mode selector (`input_mode` radio button group)
- [x] 1.4 Remove CSV-related event handlers (`handle_file_upload`, `handle_file_selection`, `handle_input_mode_change`)
- [x] 1.5 Simplify data source page to only show direct text input
- [x] 1.6 Update data preview to only show direct input data
- [x] 1.7 Remove CSV-related initialization code

## 2. Data Loading Logic
- [x] 2.1 Remove CSV file loading logic from dashboard
- [x] 2.2 Update forecasting functions to only use direct input
- [x] 2.3 Remove mode-based conditional logic (always use direct input)
- [x] 2.4 Simplify data source info display (no mode indication needed)
- [x] 2.5 Update reactive dependencies to remove CSV-related parameters

## 3. Core Functions
- [x] 3.1 Remove `load_and_prepare_data` function entirely from `src/monte_carlo.py`
- [x] 3.2 Remove function from imports in `src/dashboard.py`
- [x] 3.3 Update function imports/exports as needed

## 4. Value Persistence
- [x] 4.1 Implement save functionality for entered throughput values (prefer browser localStorage)
- [x] 4.2 Implement load functionality to restore saved values on startup
- [x] 4.3 Add fallback to file storage if localStorage not available
- [x] 4.4 Update initial dashboard state to load saved values or show empty with placeholder
- [x] 4.5 Test persistence across browser sessions

## 5. Testing
- [x] 5.1 Remove all CSV-related tests from test suite (12 tests for `load_and_prepare_data`)
- [x] 5.2 Keep and verify direct input tests still pass
- [x] 5.3 Update test fixtures to remove CSV file dependencies
- [x] 5.4 Add tests for value persistence (save/load functionality)
- [x] 5.5 Run full test suite to ensure no regressions

## 6. Documentation
- [x] 6.1 Update `docs/monte_carlo_help.md` to remove CSV references
- [x] 6.2 Update `README.md` to remove CSV format documentation and examples
- [x] 6.3 Remove CSV format examples from dashboard help text

## 7. Cleanup
- [x] 7.1 Remove sample CSV files from `data/` directory (`data1.csv`, `data2.csv`, `data3.csv`)
- [x] 7.2 Remove CSV-related comments and documentation strings
- [x] 7.3 Clean up unused imports if any

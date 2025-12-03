# Change: Remove CSV File Support

## Why

The system currently supports both CSV file upload and direct text input for throughput values. Maintaining both input methods adds complexity to the codebase, UI, and user experience. Direct text input is simpler, faster for users, and sufficient for the use case. Removing CSV support will simplify the codebase, reduce maintenance burden, and streamline the user experience.

## What Changes

- **REMOVED**: CSV file upload widget and file selector
- **REMOVED**: Input mode selector (no longer needed - only direct input)
- **REMOVED**: CSV file handling logic from dashboard
- **REMOVED**: `load_and_prepare_data` function (remove entirely)
- **MODIFIED**: Dashboard UI to only show direct text input
- **MODIFIED**: Data loading logic to only use direct text input
- **MODIFIED**: All forecasting functions to work only with direct input
- **MODIFIED**: Documentation to remove CSV format references
- **MODIFIED**: README to remove CSV examples and instructions
- **NEW**: Add persistence for entered values (save to file or browser localStorage)
- **NEW**: Load saved values on dashboard startup (if available)

## Impact

- Affected specs: `forecasting` capability specification
- Affected code:
  - `src/dashboard.py` - Remove CSV widgets, mode selector, and CSV handling logic
  - `src/monte_carlo.py` - Remove or deprecate `load_and_prepare_data` function
  - `tests/test_monte_carlo.py` - Remove CSV-related tests, keep direct input tests
  - `docs/monte_carlo_help.md` - Remove CSV references
  - `README.md` - Remove CSV format documentation
  - Sample CSV files in `data/` directory can be removed (optional)

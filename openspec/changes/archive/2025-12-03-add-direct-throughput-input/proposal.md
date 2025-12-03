# Change: Add Direct Throughput Input

## Why

Currently, users must provide throughput data via CSV files. For quick testing, experimentation, or when users have a small set of throughput values, requiring a CSV file creates unnecessary friction. Adding a direct text input field allows users to quickly enter throughput values (e.g., "2,3,5,2") without needing to create or upload a CSV file.

## What Changes

- **NEW**: Add a text input widget in the Data Source page for direct throughput entry
- **NEW**: Parse comma-separated throughput values from text input
- **MODIFIED**: Data loading logic to support both CSV files and direct text input
- **MODIFIED**: Dashboard UI to allow switching between CSV file selection and direct input modes
- **MODIFIED**: Data validation to work with both input methods
- Data preview and statistics display will work with both CSV and direct input

## Impact

- Affected specs: `forecasting` capability specification
- Affected code:
  - `src/dashboard.py` - Add text input widget and input mode switching
  - `src/monte_carlo.py` - Add function to parse text input to DataFrame (or extend existing function)
  - `tests/test_monte_carlo.py` - Add tests for text input parsing and validation
  - `docs/monte_carlo_help.md` - Update documentation to mention direct input option
  - `README.md` - Update to document direct input feature

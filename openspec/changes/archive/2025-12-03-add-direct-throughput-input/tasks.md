## 1. Core Functionality
- [x] 1.1 Add function to parse comma-separated throughput values from text input
- [x] 1.2 Add validation for text input (numeric, non-negative, handle whitespace)
- [x] 1.3 Convert parsed values to DataFrame format compatible with existing forecasting functions
- [x] 1.4 Handle edge cases (empty input, single value, all zeros, invalid characters)

## 2. Dashboard UI
- [x] 2.1 Add text input widget for direct throughput entry in Data Source page
- [x] 2.2 Add input mode selector (CSV file vs. direct input) with clear UI indication
- [x] 2.3 Update data loading logic to use appropriate source based on selected mode
- [x] 2.4 Update data preview to show throughput values from direct input
- [x] 2.5 Update statistics display to work with direct input data
- [x] 2.6 Add placeholder text and help text explaining input format

## 3. Integration
- [x] 3.1 Ensure forecasting functions work with data from direct input
- [x] 3.2 Ensure statistics calculation works with direct input data
- [x] 3.3 Update error handling to show appropriate messages for invalid text input

## 4. Testing
- [x] 4.1 Add unit tests for text input parsing function
- [x] 4.2 Add tests for validation (invalid characters, negative values, empty input)
- [x] 4.3 Add tests for edge cases (whitespace, decimals, single value, all zeros)
- [x] 4.4 Add integration tests for forecasting with direct input data
- [x] 4.5 Test mode switching between CSV and direct input
- [x] 4.6 Run full test suite to ensure no regressions

## 5. Documentation
- [x] 5.1 Update `docs/monte_carlo_help.md` to explain direct input option
- [x] 5.2 Update `README.md` to document direct input feature with examples
- [x] 5.3 Add example input formats in dashboard help text

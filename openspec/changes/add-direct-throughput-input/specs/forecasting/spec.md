# Forecasting Capability Specification

## ADDED Requirements

### Requirement: Direct Throughput Input
The system SHALL allow users to enter throughput values directly via a text input field, in addition to CSV file upload.

#### Scenario: Enter throughput values via text input
- **WHEN** user selects direct input mode
- **AND** enters comma-separated throughput values (e.g., "2,3,5,2")
- **THEN** the system parses the input and validates values are numeric and non-negative
- **AND** converts the values to a DataFrame format compatible with forecasting functions
- **AND** makes the data available for forecasting and statistics display

#### Scenario: Validate direct input values
- **WHEN** user enters throughput values in the text input
- **THEN** the system validates that values are numeric and non-negative
- **AND** trims whitespace around commas and values
- **AND** displays appropriate error messages for invalid input
- **AND** prevents forecasting with invalid data

#### Scenario: Handle whitespace in direct input
- **WHEN** user enters values with whitespace (e.g., "2, 3, 5, 2" or " 2,3,5,2 ")
- **THEN** the system trims whitespace and parses values correctly
- **AND** treats the input the same as values without whitespace

#### Scenario: Switch between CSV and direct input modes
- **WHEN** user switches between CSV file mode and direct input mode
- **THEN** the system uses the appropriate data source for the active mode
- **AND** updates data preview and statistics based on the active data source
- **AND** maintains clear UI indication of which mode is active

## MODIFIED Requirements

### Requirement: Data Loading and Preparation
The system SHALL load throughput data from either CSV files or direct text input and prepare them for throughput-based forecasting.

#### Scenario: Load CSV with throughput column
- **WHEN** a CSV file is provided with a `throughput` column
- **THEN** the system loads the data and validates the throughput column exists
- **AND** reads weekly throughput values from the column
- **AND** prepares data for throughput-based Monte Carlo simulation

#### Scenario: Load throughput from direct text input
- **WHEN** user provides comma-separated throughput values via text input
- **THEN** the system parses the input and validates values
- **AND** converts values to DataFrame format with `throughput` column
- **AND** prepares data for throughput-based Monte Carlo simulation

#### Scenario: Handle missing throughput column
- **WHEN** CSV file is missing the `throughput` column
- **THEN** the system raises an appropriate error message
- **AND** does not proceed with forecasting

#### Scenario: Handle invalid throughput values
- **WHEN** CSV file or text input contains non-numeric or negative throughput values
- **THEN** the system raises appropriate error messages
- **AND** does not proceed with forecasting

### Requirement: Forecast Completion Date
The system SHALL forecast when a specified number of work items will be completed using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid data from CSV
- **WHEN** user specifies number of work items to complete
- **AND** valid throughput data is available from CSV file
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns completion date forecasts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with valid data from direct input
- **WHEN** user specifies number of work items to complete
- **AND** valid throughput data is available from direct text input
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns completion date forecasts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** CSV file or text input has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

### Requirement: Forecast Work Items in Period
The system SHALL forecast how many work items can be completed in a specified time period using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid period and CSV data
- **WHEN** user specifies start and end dates for a time period
- **AND** valid throughput data is available from CSV file
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns forecasted item counts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with valid period and direct input data
- **WHEN** user specifies start and end dates for a time period
- **AND** valid throughput data is available from direct text input
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns forecasted item counts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** CSV file or text input has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

### Requirement: Throughput Statistics Display
The system SHALL display throughput-based statistics to help users understand their historical performance.

#### Scenario: Display throughput metrics from CSV
- **WHEN** data is loaded from CSV file and statistics are calculated
- **THEN** the system displays average weekly throughput
- **AND** displays minimum and maximum weekly throughput
- **AND** displays median weekly throughput
- **AND** displays total number of weeks of data available

#### Scenario: Display throughput metrics from direct input
- **WHEN** data is loaded from direct text input and statistics are calculated
- **THEN** the system displays average weekly throughput
- **AND** displays minimum and maximum weekly throughput
- **AND** displays median weekly throughput
- **AND** displays total number of weeks of data available

#### Scenario: Update data preview
- **WHEN** viewing data source page
- **THEN** statistics pane shows weekly throughput-based metrics
- **AND** data preview shows throughput values from CSV or direct input based on active mode

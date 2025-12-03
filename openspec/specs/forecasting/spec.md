# Forecasting Capability Specification

## Purpose

The forecasting capability provides Monte Carlo simulation-based forecasting for work item completion using historical throughput data. The system forecasts completion dates for a specified number of work items and forecasts how many items can be completed within a given time period, using weekly throughput rates from historical data.
## Requirements
### Requirement: Throughput-Based Data Preparation
The system SHALL read weekly throughput values from direct text input for use in Monte Carlo forecasting.

#### Scenario: Load weekly throughput from direct input
- **WHEN** user enters comma-separated throughput values (e.g., "2,3,5,2")
- **THEN** the system parses the input and validates values are numeric and non-negative
- **AND** stores these weekly throughput rates for use in forecasting

#### Scenario: Validate throughput values
- **WHEN** direct text input contains throughput values
- **THEN** the system validates that values are numeric and non-negative
- **AND** raises an error if invalid values are found

#### Scenario: Handle zero throughput values
- **WHEN** direct text input contains zero throughput values
- **THEN** those values are included in the throughput sample
- **AND** zero throughput values are used during Monte Carlo simulation

### Requirement: Throughput-Based Monte Carlo Simulation
The system SHALL use weekly throughput rates for Monte Carlo forecasting simulations.

#### Scenario: Forecast completion date using weekly throughput
- **WHEN** forecasting completion date for N work items
- **THEN** the system samples weekly throughput rates from direct input data
- **AND** accumulates weekly throughput until N items are completed
- **AND** converts weeks to calendar days for completion date forecast
- **AND** returns forecasted completion dates with confidence percentiles

#### Scenario: Forecast work items using weekly throughput
- **WHEN** forecasting how many items can be completed in a time period
- **THEN** the system samples weekly throughput rates from direct input data
- **AND** accumulates weekly throughput for the number of weeks in the period
- **AND** returns forecasted item counts with confidence percentiles

#### Scenario: Maintain simulation accuracy
- **WHEN** running Monte Carlo simulation
- **THEN** the system performs 5000 iterations by default
- **AND** calculates percentiles (70%, 80%, 90%, 95%, 98%) from simulation results
- **AND** maintains the same statistical rigor as cycle-time-based approach

### Requirement: Throughput Statistics Display
The system SHALL display throughput-based statistics to help users understand their historical performance.

#### Scenario: Display throughput metrics
- **WHEN** data is loaded from direct text input and statistics are calculated
- **THEN** the system displays average weekly throughput
- **AND** displays minimum and maximum weekly throughput
- **AND** displays median weekly throughput
- **AND** displays total number of weeks of data available

#### Scenario: Update data preview
- **WHEN** viewing data source page
- **THEN** statistics pane shows weekly throughput-based metrics
- **AND** data preview shows throughput values from direct input

### Requirement: Data Loading and Preparation
The system SHALL load throughput data from direct text input and prepare them for throughput-based forecasting.

#### Scenario: Load throughput from direct text input
- **WHEN** user provides comma-separated throughput values via text input
- **THEN** the system parses the input and validates values
- **AND** converts values to DataFrame format with `throughput` column
- **AND** prepares data for throughput-based Monte Carlo simulation

#### Scenario: Handle invalid throughput values
- **WHEN** text input contains non-numeric or negative throughput values
- **THEN** the system raises appropriate error messages
- **AND** does not proceed with forecasting

### Requirement: Forecast Completion Date
The system SHALL forecast when a specified number of work items will be completed using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid data
- **WHEN** user specifies number of work items to complete
- **AND** valid throughput data is available from direct text input
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns completion date forecasts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** text input has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

### Requirement: Forecast Work Items in Period
The system SHALL forecast how many work items can be completed in a specified time period using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid period
- **WHEN** user specifies start and end dates for a time period
- **AND** valid throughput data is available from direct text input
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns forecasted item counts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** text input has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

### Requirement: Direct Throughput Input
The system SHALL allow users to enter throughput values directly via a text input field.

#### Scenario: Enter throughput values via text input
- **WHEN** user enters comma-separated throughput values (e.g., "2,3,5,2")
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

#### Scenario: Save and load entered values
- **WHEN** user enters throughput values
- **THEN** the system saves the values (preferring browser localStorage, with file fallback)
- **AND** loads saved values on dashboard startup if available
- **AND** if no saved values exist, shows empty input with placeholder text

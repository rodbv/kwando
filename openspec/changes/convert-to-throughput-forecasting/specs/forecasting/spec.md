# Forecasting Capability Specification

## ADDED Requirements

### Requirement: Throughput-Based Data Preparation
The system SHALL read weekly throughput values from CSV files for use in Monte Carlo forecasting.

#### Scenario: Load weekly throughput from CSV
- **WHEN** a CSV file with a `throughput` column is loaded
- **THEN** the system reads weekly throughput values (one per row)
- **AND** stores these weekly throughput rates for use in forecasting

#### Scenario: Validate throughput values
- **WHEN** CSV file contains throughput values
- **THEN** the system validates that values are numeric and non-negative
- **AND** raises an error if invalid values are found

#### Scenario: Handle zero throughput values
- **WHEN** CSV file contains zero throughput values
- **THEN** those values are included in the throughput sample
- **AND** zero throughput values are used during Monte Carlo simulation

### Requirement: Throughput-Based Monte Carlo Simulation
The system SHALL use weekly throughput rates instead of cycle times for Monte Carlo forecasting simulations.

#### Scenario: Forecast completion date using weekly throughput
- **WHEN** forecasting completion date for N work items
- **THEN** the system samples weekly throughput rates from CSV data
- **AND** accumulates weekly throughput until N items are completed
- **AND** converts weeks to calendar days for completion date forecast
- **AND** returns forecasted completion dates with confidence percentiles

#### Scenario: Forecast work items using weekly throughput
- **WHEN** forecasting how many items can be completed in a time period
- **THEN** the system samples weekly throughput rates from CSV data
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
- **WHEN** data is loaded and statistics are calculated
- **THEN** the system displays average weekly throughput
- **AND** displays minimum and maximum weekly throughput
- **AND** displays median weekly throughput
- **AND** displays total number of weeks of data available

#### Scenario: Update data preview
- **WHEN** viewing data source page
- **THEN** statistics pane shows weekly throughput-based metrics
- **AND** data preview shows throughput values from CSV

## MODIFIED Requirements

### Requirement: Data Loading and Preparation
The system SHALL load CSV files with throughput column and prepare them for throughput-based forecasting.

#### Scenario: Load CSV with throughput column
- **WHEN** a CSV file is provided with a `throughput` column
- **THEN** the system loads the data and validates the throughput column exists
- **AND** reads weekly throughput values from the column
- **AND** prepares data for throughput-based Monte Carlo simulation

#### Scenario: Handle missing throughput column
- **WHEN** CSV file is missing the `throughput` column
- **THEN** the system raises an appropriate error message
- **AND** does not proceed with forecasting

#### Scenario: Handle invalid throughput values
- **WHEN** CSV file contains non-numeric or negative throughput values
- **THEN** the system raises appropriate error messages
- **AND** does not proceed with forecasting

### Requirement: Forecast Completion Date
The system SHALL forecast when a specified number of work items will be completed using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid data
- **WHEN** user specifies number of work items to complete
- **AND** valid throughput data is available in CSV
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns completion date forecasts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** CSV file has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

### Requirement: Forecast Work Items in Period
The system SHALL forecast how many work items can be completed in a specified time period using weekly throughput-based Monte Carlo simulation.

#### Scenario: Forecast with valid period
- **WHEN** user specifies start and end dates for a time period
- **AND** valid throughput data is available in CSV
- **THEN** the system runs weekly throughput-based Monte Carlo simulation
- **AND** returns forecasted item counts with confidence percentiles (70%, 80%, 90%, 95%, 98%)
- **AND** displays results in a readable format

#### Scenario: Forecast with insufficient data
- **WHEN** CSV file has insufficient throughput values (e.g., fewer than minimum required weeks)
- **THEN** the system displays an appropriate warning message
- **AND** does not generate forecasts

## REMOVED Requirements

### Requirement: Cycle-Time-Based Forecasting
**Reason**: Replaced with throughput-based forecasting for improved accuracy and better representation of system capacity.

**Migration**: All forecasting now uses weekly throughput values read directly from CSV files. The underlying Monte Carlo approach remains the same, but samples from weekly throughput values instead of cycle times. CSV files must be updated to include a `throughput` column with weekly throughput values (one per row).

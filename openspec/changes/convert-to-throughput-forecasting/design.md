# Design: Throughput-Based Forecasting

## Context

The current KWANDO system uses cycle-time-based Monte Carlo simulation for forecasting. This approach:
- Calculates cycle time (end_date - start_date) for each work item
- Samples from these cycle times during simulation
- Accumulates sampled cycle times to forecast completion

Throughput-based forecasting instead:
- Reads weekly throughput values directly from CSV file (one value per line)
- Samples from these weekly throughput rates during simulation
- Uses weekly throughput to determine how many items can be completed in a given period

## Goals / Non-Goals

### Goals
- Replace cycle-time-based forecasting with throughput-based forecasting
- Maintain the same Monte Carlo simulation approach (5000 iterations, same percentiles)
- Preserve existing API contracts (function signatures, return formats)
- Provide accurate forecasts based on historical throughput patterns

### Non-Goals
- Supporting both cycle-time and throughput modes simultaneously (single approach only)
- Changing the UI structure or user workflow
- Calculating throughput from cycle times or dates (throughput must be provided in CSV)

## Decisions

### Decision: Use Weekly Throughput
**What**: Use weekly throughput rates (items completed per week) for Monte Carlo simulation.

**Why**:
- Weekly granularity provides good balance between detail and stability
- Reduces noise compared to daily data
- Aligns with common agile planning cycles (sprints, iterations)

**Alternatives considered**:
- Daily throughput: More granular but may have too much noise
- Monthly throughput: Less granular, may lose important variation
- Bi-weekly throughput: Less common, harder to understand

### Decision: Read Throughput from CSV
**What**: CSV files must include a `throughput` column with weekly throughput values (one value per line/row).

**Why**:
- Simplifies the system - no need to calculate throughput from dates
- Gives users control over how throughput is calculated
- Allows for more flexible data sources (e.g., pre-aggregated data)
- Reduces complexity in data preparation logic

**Alternatives considered**:
- Calculate from cycle times: More complex, requires date parsing and aggregation
- Calculate from completion dates: Still requires date parsing and grouping logic
- Multiple time periods: Too complex, weekly is sufficient

### Decision: Sample from Weekly Throughput Values
**What**: During Monte Carlo simulation, randomly sample from the list of weekly throughput values provided in the CSV (e.g., if CSV has 50 rows, sample from those 50 weekly throughput values).

**Why**:
- Preserves the distribution and variability of historical throughput
- Matches the existing cycle-time sampling approach
- Simple to implement and understand
- Each row represents one week of historical data

**Alternatives considered**:
- Fit a distribution (e.g., normal, Poisson): More complex, may not match actual distribution
- Use rolling averages: Loses variability, less accurate
- Weighted sampling: Adds complexity without clear benefit

### Decision: Maintain Same Function Signatures
**What**: Keep existing function signatures and return formats unchanged.

**Why**:
- Minimizes breaking changes to dashboard code
- Easier migration path
- Maintains API compatibility

## Risks / Trade-offs

### Risk: CSV Format Change
**Issue**: Existing CSV files will need to be updated to include throughput column, which is a breaking change for users.

**Mitigation**:
- Clear documentation of new CSV format requirements
- Update sample CSV files in repository
- Provide migration guidance if possible
- Clear error messages when throughput column is missing

### Risk: Data Quality
**Issue**: If users provide incorrect or inconsistent throughput values, forecasts will be inaccurate.

**Mitigation**:
- Validate throughput values are numeric and non-negative
- Provide clear documentation on expected format
- Display data statistics to help users verify their data

### Risk: Forecast Accuracy
**Issue**: Throughput-based forecasting may produce different results than cycle-time-based, which could confuse users expecting the same outputs.

**Mitigation**:
- Update documentation to explain the change
- Provide clear explanation of throughput-based approach
- Consider adding comparison mode in future (out of scope)

### Risk: Weekly Granularity
**Issue**: Weekly throughput may be less granular than needed for some use cases.

**Mitigation**:
- Weekly granularity is appropriate for most forecasting scenarios
- Can be extended in future if needed (out of scope)

## Migration Plan

1. **Implementation**: Replace cycle-time calculation with throughput reading from CSV
2. **Testing**: Thoroughly test with new CSV format (with throughput column)
3. **Validation**: Test with various throughput value distributions
4. **Deployment**: Deploy with updated CSV format requirements
5. **Documentation**: Update all user-facing documentation with new CSV format

**Rollback**: If issues arise, can revert to cycle-time-based approach by restoring previous version.

## Open Questions

- Should we validate minimum number of throughput values for reliable forecasting? (e.g., require at least 10 weeks of data)
- Should throughput values be required to be integers, or allow decimals? (Decision: allow decimals for fractional items per week)
- How should we handle negative or zero throughput values? (Decision: validate non-negative, allow zero)

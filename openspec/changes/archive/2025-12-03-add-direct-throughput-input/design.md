# Design: Direct Throughput Input

## Context

The current system requires users to provide throughput data via CSV files. While CSV files are appropriate for larger datasets, they create friction for quick tests or small datasets. Users may want to quickly enter a few throughput values without creating a file.

## Goals / Non-Goals

### Goals
- Allow users to enter throughput values directly via a text input field
- Support comma-separated values (e.g., "2,3,5,2")
- Maintain compatibility with existing CSV-based workflow
- Use the same validation and forecasting logic for both input methods
- Provide clear UI for switching between CSV and direct input modes

### Non-Goals
- Supporting other input formats (JSON, XML, etc.) - CSV and text input are sufficient
- Persisting direct input values (they are session-only)
- Complex parsing (only comma-separated values, no spaces or other delimiters needed initially)

## Decisions

### Decision: Comma-Separated Values Format
**What**: Accept throughput values as comma-separated text (e.g., "2,3,5,2").

**Why**:
- Simple and intuitive format
- Easy to parse and validate
- Common format users are familiar with
- Allows quick entry of values

**Alternatives considered**:
- Space-separated: Less common, harder to read
- Newline-separated: Requires multi-line input, more complex
- JSON array: Too complex for simple use case

### Decision: Dual Input Mode
**What**: Allow users to choose between CSV file upload/selection and direct text input, but only one active at a time.

**Why**:
- Clear separation of concerns
- Prevents confusion about which data source is active
- Maintains existing CSV workflow
- Simple UI with toggle or radio buttons

**Alternatives considered**:
- Always show both: Could be confusing which takes precedence
- Replace CSV with text input: Breaks existing workflow
- Auto-detect format: Adds complexity, may misinterpret input

### Decision: Parse to DataFrame Format
**What**: Convert text input to the same DataFrame format used by CSV loading, ensuring compatibility with existing forecasting functions.

**Why**:
- Reuses existing validation and forecasting logic
- No changes needed to core forecasting functions
- Consistent data structure throughout the system
- Easier to test and maintain

**Alternatives considered**:
- Separate code path for text input: Duplicates logic, harder to maintain
- Different data structure: Requires refactoring forecasting functions

### Decision: Validate on Input
**What**: Validate throughput values as user types or when they submit the input, showing errors immediately.

**Why**:
- Provides immediate feedback
- Prevents invalid data from being used in forecasts
- Better user experience
- Same validation rules as CSV (numeric, non-negative)

**Alternatives considered**:
- Validate only on forecast: Delayed feedback, worse UX
- Lazy validation: May allow invalid intermediate states

## Risks / Trade-offs

### Risk: Input Format Confusion
**Issue**: Users may not understand the expected format (comma-separated values).

**Mitigation**:
- Clear placeholder text showing example format
- Help text or tooltip explaining the format
- Validation error messages that guide users to correct format

### Risk: Large Input Handling
**Issue**: Users may paste very large comma-separated lists, which could impact performance.

**Mitigation**:
- Reasonable limits (e.g., 1000 values) with clear messaging
- Performance is acceptable for typical use cases (dozens to hundreds of values)
- Can be optimized later if needed

### Risk: Data Loss When Switching Modes
**Issue**: If user enters text input then switches to CSV mode, their text input is lost.

**Mitigation**:
- Clear UI indication of active mode
- Acceptable trade-off for simplicity
- Users can copy/paste if needed

## Migration Plan

1. **Implementation**: Add text input widget and parsing function
2. **Testing**: Test with various input formats, edge cases, and validation
3. **UI Updates**: Add mode switching UI in dashboard
4. **Documentation**: Update help and README with direct input option
5. **Deployment**: Deploy with backward compatibility (CSV still works)

**Rollback**: If issues arise, can disable text input feature while keeping CSV functionality intact.

## Open Questions

- Should we support whitespace around commas? (Decision: Yes, trim whitespace for better UX)
- Should we allow decimal values? (Decision: Yes, same as CSV - supports fractional items per week)
- Should we limit the number of values? (Decision: Reasonable limit of 1000 values with clear messaging)

# Design: Remove CSV File Support

## Context

The current system supports two input methods for throughput data:
1. CSV file upload/selection
2. Direct text input (comma-separated values)

Both methods work, but maintaining both adds complexity. Direct text input is simpler and sufficient for the use case.

## Goals / Non-Goals

### Goals
- Remove all CSV file handling from the user interface
- Simplify the dashboard to only show direct text input
- Remove input mode selector (no longer needed)
- Streamline data loading to only use direct text input
- Update all documentation to reflect direct input only

### Non-Goals
- Supporting other input formats
- Adding file import from other sources
- Migration guide (sole user, not needed)

## Decisions

### Decision: Remove CSV Support Completely
**What**: Remove all CSV file upload, selection, and handling from the user interface.

**Why**:
- Simplifies the codebase significantly
- Reduces UI complexity (no mode selector needed)
- Direct input is sufficient for the use case
- Easier to maintain and test
- Faster user experience (no file upload/selection step)

**Alternatives considered**:
- Keep CSV as hidden/advanced feature: Still adds complexity
- Deprecate CSV gradually: Unnecessary if we're sure we want to remove it

### Decision: Keep Direct Input Only
**What**: The system will only accept throughput values via direct text input.

**Why**:
- Simple and intuitive
- Fast for users (no file management)
- Sufficient for typical use cases
- Easier to validate and provide immediate feedback

### Decision: Remove Input Mode Selector
**What**: Remove the radio button group that lets users choose between CSV and Direct Input.

**Why**:
- No longer needed with only one input method
- Simplifies UI
- Reduces cognitive load

**Alternatives considered**:
- Keep selector but disable CSV option: Confusing, better to remove entirely

### Decision: Add Value Persistence
**What**: Save entered throughput values and load them on dashboard startup, using either file storage or browser localStorage.

**Why**:
- Improves user experience by remembering previous input
- Reduces need to re-enter values
- Provides data persistence that CSV files previously offered

**Implementation**:
- Prefer browser localStorage (simpler, no file system access needed)
- Fallback to file if localStorage not available
- Load saved values on startup if available
- If no saved values, show empty input with placeholder

**Alternatives considered**:
- No persistence: Less convenient for users
- File-only persistence: More complex, requires file system access

## Risks / Trade-offs

### Risk: Loss of Bulk Data Entry
**Issue**: Users with large datasets (100+ values) may find direct input cumbersome.

**Mitigation**:
- Direct input supports up to 1000 values (sufficient for most use cases)
- Users can copy-paste from spreadsheets into the text input
- If needed, can be addressed in future with paste-from-clipboard enhancement

### Risk: Breaking Existing Workflows
**Issue**: Users who rely on CSV files will need to adapt.

**Mitigation**:
- Clear migration path: users can copy CSV values and paste into text input
- Update documentation with migration guide
- This is a breaking change, but the benefit of simplification outweighs the cost

### Risk: Loss of Data Persistence
**Issue**: CSV files provide a way to save and reuse data.

**Mitigation**:
- Users can save their comma-separated values in a text file if needed
- Browser may remember input values
- Future enhancement could add export/save functionality if needed

## Migration Plan

1. **Implementation**: Remove CSV widgets and logic from dashboard
2. **Testing**: Ensure all tests pass with direct input only
3. **Documentation**: Update all docs to remove CSV references
4. **Deployment**: Deploy as breaking change with clear migration notes

**Rollback**: If issues arise, can restore CSV support by reverting changes, but this should be avoided if possible.

## Open Questions

- Should we keep `load_and_prepare_data` for internal/testing purposes? (Decision: No, remove entirely)
- Should we remove sample CSV files from `data/` directory? (Decision: Yes, they're no longer needed)
- Should we add a "paste from CSV" helper that converts CSV format to comma-separated? (Decision: Out of scope for this change)
- Should we add value persistence? (Decision: Yes, using browser localStorage with file fallback)

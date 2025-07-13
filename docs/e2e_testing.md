# E2E Testing

This project includes end-to-end (E2E) tests that verify the dashboard functionality works correctly in a real browser environment.

## What is E2E Testing?

E2E tests simulate real user interactions with the dashboard by:
- Starting the dashboard in a Docker container
- Opening a headless browser
- Clicking buttons and navigating between pages
- Verifying that the correct content is displayed

## Running E2E Tests

### Prerequisites

- Docker installed and running
- Python 3.12+
- Git

### Local Development

1. **Install E2E dependencies:**
   ```bash
   pip install -e ".[e2e]"
   playwright install chromium
   ```

2. **Run E2E tests using the script:**
   ```bash
   python scripts/run_e2e_tests.py
   ```

3. **Or run manually:**
   ```bash
   # Build and start dashboard
   docker build -t kwando-dashboard .
   docker run -d --name kwando-e2e-test -p 5006:5006 kwando-dashboard

   # Wait for dashboard to start
   sleep 15

   # Run tests
   python -m pytest tests/e2e/ -v

   # Clean up
   docker stop kwando-e2e-test
   docker rm kwando-e2e-test
   ```

### In CI/CD

The E2E tests run automatically in GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

See `.github/workflows/e2e-tests.yml` for the workflow configuration.

## Test Coverage

The E2E tests cover:

- ✅ Dashboard loads successfully
- ✅ Data source page is shown by default
- ✅ Help button opens help page
- ✅ "When will it be done?" button opens forecast page
- ✅ "How many items?" button opens capacity page
- ✅ Data source button returns to data page
- ✅ Sidebar about section is visible
- ✅ File selector widget is present
- ✅ File upload widget is present
- ✅ Data preview pane is present
- ✅ Data statistics pane is present

## Test Structure

- **Location:** `tests/e2e/test_dashboard.py`
- **Framework:** Playwright with pytest
- **Browser:** Chromium (headless)
- **Target:** `http://localhost:5006`

## Adding New Tests

To add new E2E tests:

1. Add test functions to `tests/e2e/test_dashboard.py`
2. Use Playwright's `page` fixture for browser interactions
3. Use `expect()` for assertions
4. Follow the naming pattern: `test_<feature>_<expected_behavior>`

Example:
```python
def test_new_feature_works_correctly(page):
    """Test that new feature works as expected."""
    page.goto("http://localhost:5006")

    # Click a button
    page.locator("text=New Button").click()

    # Verify result
    expect(page.locator("text=Expected Result")).to_be_visible()
```

## Troubleshooting

### Dashboard not starting
- Check Docker is running
- Verify port 5006 is available
- Check container logs: `docker logs kwando-e2e-test`

### Tests failing
- Increase wait times if dashboard is slow to load
- Check for UI changes that might affect selectors
- Run tests with `-s` flag to see browser output: `pytest tests/e2e/ -v -s`

### Playwright issues
- Reinstall Playwright: `playwright install --force`
- Update Playwright: `pip install --upgrade playwright`

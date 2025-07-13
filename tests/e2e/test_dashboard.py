import time

import pytest
from playwright.sync_api import expect, sync_playwright


@pytest.fixture(scope="session")
def browser():
    """Start browser for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    page = browser.new_page()
    yield page
    page.close()


def test_dashboard_loads(page):
    """Test that the dashboard loads successfully."""
    page.goto("http://localhost:5006")

    # Check that the main title is present
    expect(page.locator("text=When will it be done?")).to_be_visible()

    # Check that the main content area is loaded
    expect(page.locator("text=Data Source")).to_be_visible()


def test_data_source_page_default(page):
    """Test that the data source page is shown by default."""
    page.goto("http://localhost:5006")

    # Check that data source content is visible
    expect(page.locator("text=Choose CSV file")).to_be_visible()
    expect(page.locator("text=Upload CSV")).to_be_visible()
    expect(page.locator("text=Data Preview")).to_be_visible()


def test_help_button_opens_help_page(page):
    """Test that clicking the help button opens the help page."""
    page.goto("http://localhost:5006")

    # Click the help button
    help_button = page.locator("text=📚 Learn about Monte Carlo Simulation")
    help_button.click()

    # Wait for help content to load
    time.sleep(1)

    # Check that help content is visible
    expect(page.locator("text=How These Forecasts Work")).to_be_visible()
    expect(page.locator("text=What is Monte Carlo Simulation?")).to_be_visible()


def test_when_button_opens_forecast_page(page):
    """Test that clicking the 'When will it be done?' button opens the forecast page."""
    page.goto("http://localhost:5006")

    # Click the 'When will it be done?' button
    when_button = page.locator("text=⏰ When will it be done?")
    when_button.click()

    # Wait for content to load
    time.sleep(1)

    # Check that forecast content is visible
    expect(page.locator("text=Number of Work Items")).to_be_visible()
    expect(page.locator("text=Data Source:")).to_be_visible()


def test_how_many_button_opens_capacity_page(page):
    """Test that clicking the 'How many items?' button opens the capacity page."""
    page.goto("http://localhost:5006")

    # Click the 'How many items?' button
    how_many_button = page.locator("text=📊 How many items?")
    how_many_button.click()

    # Wait for content to load
    time.sleep(1)

    # Check that capacity content is visible
    expect(page.locator("text=Period Start Date")).to_be_visible()
    expect(page.locator("text=Period End Date")).to_be_visible()


def test_data_source_button_returns_to_data_page(page):
    """Test that clicking the data source button returns to the data page."""
    page.goto("http://localhost:5006")

    # First go to another page
    when_button = page.locator("text=⏰ When will it be done?")
    when_button.click()
    time.sleep(1)

    # Then click data source button
    data_source_button = page.locator("text=📁 Data Source")
    data_source_button.click()
    time.sleep(1)

    # Check that we're back to data source page
    expect(page.locator("text=Choose CSV file")).to_be_visible()
    expect(page.locator("text=Upload CSV")).to_be_visible()


def test_sidebar_about_section_is_visible(page):
    """Test that the about section in the sidebar is visible."""
    page.goto("http://localhost:5006")

    # Check that about content is visible in sidebar
    expect(page.locator("text=About")).to_be_visible()
    expect(page.locator("text=Monte Carlo simulation")).to_be_visible()
    expect(page.locator("text=GitHub")).to_be_visible()


def test_file_selector_is_present(page):
    """Test that the file selector widget is present."""
    page.goto("http://localhost:5006")

    # Check that file selector is present
    expect(page.locator("select")).to_be_visible()
    expect(page.locator("text=Choose CSV file")).to_be_visible()


def test_file_upload_widget_is_present(page):
    """Test that the file upload widget is present."""
    page.goto("http://localhost:5006")

    # Check that file upload is present
    expect(page.locator("input[type='file']")).to_be_visible()
    expect(page.locator("text=Upload CSV")).to_be_visible()


def test_data_preview_pane_is_present(page):
    """Test that the data preview pane is present."""
    page.goto("http://localhost:5006")

    # Check that data preview is present
    expect(page.locator("text=Data Preview")).to_be_visible()


def test_data_statistics_pane_is_present(page):
    """Test that the data statistics pane is present."""
    page.goto("http://localhost:5006")

    # Check that data statistics is present
    expect(page.locator("text=Data Statistics")).to_be_visible()

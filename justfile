# KWANDO Development Commands

# Default recipe - show available commands
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --extra dev

# Run the dashboard
run:
    uv run panel serve src/dashboard.py --autoreload

# Run tests (single run, for CI or one-off)
test:
    uv run pytest

# Run tests once (single run, for CI or one-off)
test-once:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=src --cov-report=html

# Run tests in watch mode
test-watch:
    uv run ptw

# Lint code
lint:
    uv run ruff check .

# Format code
format:
    uv run ruff format .

# Lint and format code
fix: lint format

# Install pre-commit hooks
setup-hooks:
    uv run pre-commit install

# Run pre-commit on all files
pre-commit:
    uv run pre-commit run --all-files

# Clean up cache and temporary files
clean:
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Show project info
info:
    @echo "KWANDO - Monte Carlo Simulation Dashboard"
    @python --version
    @uv --version
    @echo "Project dependencies:"
    @uv tree

# Development workflow: install, setup hooks, and run tests
dev-setup: install-dev setup-hooks test

# Quick development cycle: format, lint, test
dev-cycle: format lint test

# Build and check everything
check-all: clean install-dev setup-hooks format lint test

coverage:
    # Run tests with coverage and generate coverage.xml
    uv run pytest --cov=src --cov-report=xml

coverage-html:
    # Run tests with coverage and generate HTML report
    uv run pytest --cov=src --cov-report=html

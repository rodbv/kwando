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

# Run the dashboard locally (fastest for development)
run:
    uv run panel serve src/dashboard.py --autoreload

# Run the dashboard (production dockerized)
run-docker:
    docker build -t kwando-dashboard .
    docker run --rm -p 5006:5006 --name kwando-dashboard kwando-dashboard

# Run the dashboard (development dockerized)
run-docker-dev:
    docker build -f Dockerfile.dev -t kwando-dashboard:dev .
    docker run --rm -p 5006:5006 --name kwando-dashboard-dev -v $(pwd):/app kwando-dashboard:dev

# Build production image
build:
    docker build -t kwando-dashboard .

# Build development image
build-dev:
    docker build -f Dockerfile.dev -t kwando-dashboard:dev .

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

# Clean Docker images and containers
clean-docker:
    docker stop kwando-dashboard kwando-dashboard-dev 2>/dev/null || true
    docker rm kwando-dashboard kwando-dashboard-dev 2>/dev/null || true
    docker rmi kwando-dashboard kwando-dashboard:dev 2>/dev/null || true



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

# WWIBD: Monte Carlo Simulation Dashboard

A simple dashboard for forecasting work item completion using Monte Carlo simulations. Built with Python, Panel, and CSV data.

## Features
- Forecast when work will be done or how many items can be completed in a period
- Upload your own CSV data
- Filter by tags

## Getting Started
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Install dependencies:
   ```sh
   uv sync
   ```
3. Run the dashboard:
   ```sh
   uv run panel serve src/dashboard.py
   ```

## Development
1. Install development dependencies:
   ```sh
   uv sync --extra dev
   ```
2. Install pre-commit hooks:
   ```sh
   uv run pre-commit install
   ```
3. Run tests:
   ```sh
   uv run pytest
   ```

## License
MIT

## Credits
- Monte Carlo simulation implementation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Theory and approach inspired by Daniel Vacanti's [ActionableAgile](https://www.actionableagile.com/)

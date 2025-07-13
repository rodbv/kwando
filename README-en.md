# KWANDO: Monte Carlo Simulation Dashboard

Dashboard for forecasting work item completion using Monte Carlo simulations. Made with Python and [Panel](https://panel.holoviz.org/).

## Features

- **Forecast Completion Dates**: Calculate when a specific number of items will be completed
- **Capacity Planning**: Calculate how many items can be completed in a period
- **Data Upload**: Use your own CSV files or sample data
- **Tag Filtering**: Filter analysis by work item tags
- **Web Interface**: Dashboard with real-time calculations
- **Percentiles**: View percentiles (70%, 80%, 90%, 95%, 98%) for confidence levels

## What is Monte Carlo Simulation?

Monte Carlo simulation uses historical cycle time data to run thousands of simulations. Instead of a single estimate, you get forecasts with different confidence levels, considering the natural variability of completion times.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Installation

1. Install uv:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:
   ```sh
   git clone https://github.com/your-username/kwando.git
   cd kwando
   ```

3. Install dependencies:
   ```sh
   uv sync
   ```

4. Run the dashboard:
   ```sh
   uv run panel serve src/dashboard.py
   ```

5. Open your browser to the URL shown in the terminal (typically `http://localhost:5006`)

## Data Format

Your CSV file should contain at least a `cycle_time_days` column with positive numeric values representing the time taken to complete work items.

**Required columns:**
- `cycle_time_days`: Number of days to complete each work item

**Optional columns:**
- `tags`: Comma-separated tags for filtering (e.g., "bug,frontend,high-priority")

## Usage

1. **Load Data**: Use the "Data Source" section to load your CSV file or choose existing files
2. **Choose Analysis**:
   - **"When will it be done?"**: Calculate completion date for a specific number of items
   - **"How many items?"**: Calculate how many items can be completed in a period
3. **Set Parameters**: Define number of items or date range
4. **View Results**: See percentiles and confidence levels of the forecast

## Development

### Setup

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

### Code Quality

The project uses:
- **Ruff** for linting and formatting
- **Pre-commit** hooks for automated checks
- **Pytest** for testing

Run quality checks:
```sh
uv run ruff check .
uv run ruff format .
```

### Using just

This project uses [just](https://github.com/casey/just) to simplify common development commands.

#### Installing just

On macOS (Homebrew):
```sh
brew install just
```
On Linux:
```sh
sudo snap install --edge --classic just
```
Or see other options in the [official documentation](https://github.com/casey/just#installation).

#### Usage examples

- Run the dashboard:
  ```sh
  just run
  ```
- Run tests (single run):
  ```sh
  just test
  ```
- Run tests in watch mode (auto-reload):
  ```sh
  just test-watch
  ```
- Check code quality:
  ```sh
  just lint
  just format
  ```
- List all available commands:
  ```sh
  just --list
  ```

## Contributing

Contributions are welcome! See the [Contributing Guide](CONTRIBUTING.md) for details on how to submit issues, feature requests, and pull requests.

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you must follow this code.

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Monte Carlo simulation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Theory based on Daniel Vacanti's [ActionableAgile](https://www.actionableagile.com/)

---

**Português**: [README.md](README.md)

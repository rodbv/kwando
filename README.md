[🇧🇷 Português](README-pt-br.md)

[![Tests](https://github.com/rodbv/kwando/actions/workflows/test.yml/badge.svg)](https://github.com/rodbv/kwando/actions/workflows/test.yml)
![Coverage](https://img.shields.io/badge/coverage-97%25-green)

# KWANDO: Monte Carlo Simulation Dashboard

A dashboard to forecast work item completion using Monte Carlo simulations. Built with Python and [Panel](https://panel.holoviz.org/).

<img src="docs/images/screencap.gif" alt="KWANDO Dashboard Screenshot" style="max-width: 600px; box-shadow: 0 4px 24px #0003; border-radius: 8px; margin: 1em 0;" />

## Why Monte Carlo Simulation?

Monte Carlo simulations use your team’s actual historical data to generate thousands of possible futures, providing a range of likely outcomes and their probabilities. Unlike simple averages or burn rate calculations, Monte Carlo methods account for the natural variability and unpredictability in real work. This means you get forecasts with confidence levels (percentiles), not just a single number, helping you make better decisions under uncertainty.

For a deeper dive, see [Actionable Agile Metrics for Predictability: An Introduction](https://actionableagile.com/books/aamfp/) by Daniel Vacanti.

Watch: [Your Project Behaves Like a Hurricane. Forecast It Like One (YouTube)](https://www.youtube.com/watch?v=j1FTNVRkJYg)

## Getting Started

### Run from Docker Hub (Recommended)
If you have Docker installed, you can run Kwando directly from Docker Hub without building the image yourself:

```sh
docker run --rm -p 5006:5006 rodbv/kwando:latest
```

Then open [http://localhost:5006](http://localhost:5006) in your browser.

### Run with Docker (Build Locally)
If you want to build the image yourself:

#### Quick Start (Build Locally)
```sh
# Build and run in one command
docker build -t kwando-dashboard . && docker run --rm -p 5006:5006 kwando-dashboard
```

#### Alternative: Using Just (if you have it installed)
```sh
# Install just: https://just.systems/man/en/
just run-docker
```

Then open [http://localhost:5006](http://localhost:5006) in your browser.

### Running from source

#### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

#### Installation

1. Install uv:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Clone the repository:
   ```sh
   git clone https://github.com/rodbv/kwando.git
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
5. Open your browser at the URL shown in the terminal (typically `http://localhost:5006`)

## Data Format

Your CSV file must have the following columns:
- `id`: Unique identifier for each work item
- `start_date`: Start date of the work item in ISO 8601 format (YYYY-MM-DD)
- `end_date`: End date of the work item in ISO 8601 format (YYYY-MM-DD)

Example:

```csv
id,start_date,end_date
1,2024-01-01,2024-01-01
2,2024-01-01,2024-01-02
3,2024-01-01,2024-01-03
```

## How to Use

1. **Load Data**: Use the "Data Source" section to upload your CSV file or choose an existing file
2. **Choose Analysis**:
   - **"When will it be done?"**: Calculate completion date for a specific number of items
   - **"How many items?"**: Calculate how many items can be completed in a period
3. **Adjust Parameters**: Set the number of items or date range
4. **View Results**: See percentiles and confidence levels for your forecast

---

## Contributing

Contributions are welcome! See the [Contributing Guide](CONTRIBUTING.md) for details on how to submit issues, feature requests, and pull requests.

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Monte Carlo simulation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Inspired by the book [Actionable Agile Metrics for Predictability: An Introduction](https://actionableagile.com/books/aamfp/) by Daniel Vacanti

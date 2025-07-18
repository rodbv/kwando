[🇧🇷 Português](README-pt-br.md)

[![Tests](https://github.com/rodbv/kwando/actions/workflows/test.yml/badge.svg)](https://github.com/rodbv/kwando/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyPI](https://img.shields.io/badge/PyPI-kwando-blue.svg)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)

# KWANDO: Monte Carlo Simulation Dashboard

A dashboard to forecast work item completion using Monte Carlo simulations. Built with Python and [Panel](https://panel.holoviz.org/).

<img src="docs/images/screencap.gif" alt="KWANDO Dashboard Screenshot" style="max-width: 600px; box-shadow: 0 4px 24px #0003; border-radius: 8px; margin: 1em 0;" />

## Why Monte Carlo Simulation?

Monte Carlo simulations use your team’s actual historical data to generate thousands of possible futures, providing a range of likely outcomes and their probabilities. Unlike simple averages or burn rate calculations, Monte Carlo methods account for the natural variability and unpredictability in real work. This means you get forecasts with confidence levels (percentiles), not just a single number, helping you make better decisions under uncertainty.

For a deeper dive, see [Actionable Agile Metrics for Predictability: An Introduction](https://actionableagile.com/books/aamfp/) by Daniel Vacanti.

Watch: [Your Project Behaves Like a Hurricane. Forecast It Like One (YouTube)](https://www.youtube.com/watch?v=j1FTNVRkJYg)

## Getting Started

### Quick Start with Docker Hub (Recommended)

The easiest way to run Kwando is using the pre-built Docker image from Docker Hub:

```sh
docker run -p 5006:5006 -v $(pwd)/data:/app/data rodbv/kwando:latest
```

Then open [http://localhost:5006](http://localhost:5006) in your browser. No installation or setup required!

If you want a CSV file as an example, you can download some [here](https://github.com/rodbv/kwando/tree/main/data).

> **Don't have Docker?** [Install Docker here](https://docs.docker.com/get-docker/)

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

# KWANDO: Monte Carlo Simulation Dashboard

KWANDO is a simple, open-source dashboard for Monte Carlo simulations using your own CSV data. It helps you forecast delivery dates and team capacity using real historical data.

<video src="docs/images/chrome-capture-2025-7-13.mp4" controls style="max-width: 600px; box-shadow: 0 4px 24px #0003; border-radius: 8px; margin: 1em 0;">
  Your browser does not support the video tag.
</video>

## Features

- **Forecast Completion Dates**: Predict when a set number of work items will be done
- **Capacity Planning**: Calculate how many items can be completed in a period
- **Data Upload**: Use your own CSV files or sample data
- **Web Interface**: Dashboard with real-time calculations
- **Percentiles**: View percentiles (70%, 80%, 90%, 95%, 98%) for confidence levels
- **No Vendor Lock-in**: 100% open source, runs locally or online

## Quick Start

To run locally:

1. Install Python 3.9+
2. Clone the repository:
   ```sh
   git clone https://github.com/rodbv/kwando.git
   cd kwando
   ```
3. Create a virtual environment and install dependencies:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Start the dashboard:
   ```sh
   just run
   # or
   panel serve src/dashboard.py --show
   ```

## Usage

- Select or add your CSV file in the `data/` directory.
- The CSV must have at least these columns:
  - `id`: Unique identifier for each work item
  - `start_date`: Start date of the work item in ISO 8601 format
  - `end_date`: End date of the work item in ISO 8601 format
- Use the dashboard to:
  - Forecast when a set number of items will be done
  - Forecast how many items can be completed in a period

## Development

- Run tests:
  ```sh
  just test
  ```
- Lint and format code:
  ```sh
  just lint
  just format
  ```
- See all available commands:
  ```sh
  just --list
  ```

## Contributing

Contributions are welcome! See the [Contributing Guide](CONTRIBUTING.md) for details on how to submit issues, feature requests, and pull requests.

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Monte Carlo simulation adapted from [rueedlinger/monte-carlo-simulation](https://github.com/rueedlinger/monte-carlo-simulation)
- Theory based on [ActionableAgile](https://www.actionableagile.com/) by Daniel Vacanti

---

**Português**: [README.md](README.md)

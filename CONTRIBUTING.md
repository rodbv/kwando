# Contributing to KWANDO

Thank you for your interest in contributing to KWANDO! This document provides guidelines and information for contributors.

## Quick Start for Development

1. Clone your fork:
   ```sh
   git clone https://github.com/your-username/kwando.git
   cd kwando
   ```
2. Install dependencies:
   ```sh
   uv sync --extra dev
   ```
3. Install pre-commit hooks:
   ```sh
   uv run pre-commit install
   ```
4. Run the dashboard:
   ```sh
   just run
   # or
   uv run panel serve src/dashboard.py
   ```
5. Run tests and checks:
   ```sh
   just test
   just lint
   just format
   ```

See the [Justfile](justfile) for all available development commands.

## What is KWANDO?

KWANDO is a Monte Carlo simulation dashboard for forecasting work item completion. It helps teams predict when work will be done or how many items can be completed in a given period using historical data.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Include a clear description of the bug
- Provide steps to reproduce the issue
- Include your operating system and Python version
- If possible, include sample data that reproduces the issue

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Describe the feature and why it would be useful
- Include mockups or examples if applicable

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**: `just test`
6. **Check code quality**: `just lint`
7. **Format your code**: `just format`
8. **Commit your changes** with clear commit messages
9. **Push to your fork** and submit a pull request
10. If available, use the pull request template.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Project Structure

```
kwando/
├── src/
│   ├── dashboard.py      # Main dashboard application
│   └── monte_carlo.py    # Monte Carlo simulation logic
├── data/                 # Sample CSV data files
├── tests/                # Test files
├── pyproject.toml        # Project configuration
└── README.md             # Project documentation
```

## Data Format

The application expects CSV files with the following columns:
- `id`: Unique identifier for each work item
- `start_date`: Start date of the work item in ISO 8601 format or YYYY-MM-DD (YYYY-MM-DD)
- `end_date`: End date of the work item in ISO 8601 format (YYYY-MM-DD)

Example:
```csv
id,start_date,end_date
1,2024-01-01,2024-01-05
2,2024-01-03,2024-01-10
```

## Pull Request Guidelines

- Keep changes focused and atomic
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Follow the existing code style
- Add a clear description of your changes
- Use the pull request template if available

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions or Need Help?

- Open an issue on GitHub
- Check existing issues and discussions
- Review the README for basic usage

## License

By contributing to KWANDO, you agree that your contributions will be licensed under the MIT License.

# Contributing to KWANDO

Thank you for your interest in contributing to KWANDO! This document provides guidelines and information for contributors.

## What is KWANDO?

KWANDO is a Monte Carlo simulation dashboard for forecasting work item completion. It helps teams predict when work will be done or how many items can be completed in a given period using historical cycle time data.

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
5. **Run the test suite**: `uv run pytest`
6. **Check code quality**: `uv run ruff check .`
7. **Format your code**: `uv run ruff format .`
8. **Commit your changes** with clear commit messages
9. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Installation

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/kwando.git
   cd kwando
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

### Running the Application

```bash
uv run panel serve src/dashboard.py
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

The project uses:
- **Ruff** for linting and formatting
- **Pre-commit** hooks for automated checks
- **Pytest** for testing

Run quality checks:
```bash
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
kwando/
├── src/
│   ├── dashboard.py      # Main dashboard application
│   └── monte_carlo.py    # Monte Carlo simulation logic
├── data/                 # Sample CSV data files
├── tests/                # Test files
├── pyproject.toml        # Project configuration
└── README.md            # Project documentation
```

## Data Format

The application expects CSV files with at least a `cycle_time_days` column containing positive numeric values representing the time taken to complete work items.

## Pull Request Guidelines

- Keep changes focused and atomic
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Follow the existing code style
- Add a clear description of your changes

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

## Questions or Need Help?

- Open an issue on GitHub
- Check existing issues and discussions
- Review the README for basic usage

## License

By contributing to KWANDO, you agree that your contributions will be licensed under the MIT License.

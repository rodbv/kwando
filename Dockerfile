# Simple, fast build using Debian base (better wheel support)
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv \
    && uv pip install --system .

# Copy application code
COPY . .

# Expose port
EXPOSE 5006

# Run the application
CMD ["panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

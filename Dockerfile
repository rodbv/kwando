# Build stage - install dependencies that require build tools
FROM python:3.12-slim AS builder

# Install build dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv in a single layer
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (this layer will be cached if dependencies don't change)
RUN uv sync --frozen

# Final stage - minimal runtime image
FROM python:3.12-slim

WORKDIR /app

# Install uv (no build tools needed, just runtime)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv

# Copy only the virtual environment from builder (not build tools)
COPY --from=builder /app/.venv /app/.venv

# Copy dependency files (needed for uv to work)
COPY pyproject.toml uv.lock ./

# Copy application code
COPY . .

# Make sure we use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 5006

CMD ["uv", "run", "panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

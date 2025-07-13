FROM python:3.12-slim

# Install system dependencies (build-essential only for build, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv \
    && uv pip install --system .

# Copy the rest of the code (make sure .dockerignore is present)
COPY . .

# Remove build-essential if not needed at runtime
RUN apt-get purge -y build-essential && apt-get autoremove -y

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

EXPOSE 5006

# Healthcheck for the dashboard
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5006/ || exit 1

CMD ["panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

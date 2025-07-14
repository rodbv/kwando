FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install --upgrade pip
RUN pip install uv

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (this layer will be cached if dependencies don't change)
RUN uv sync --frozen

# Copy the rest of the code
COPY . .

EXPOSE 5006

CMD ["uv", "run", "panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

rop FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY pyproject.toml ./
COPY uv.lock ./
RUN pip install --upgrade pip
RUN pip install uv
RUN uv pip install --system .

# Copy the rest of the code
COPY . .

EXPOSE 5006

CMD ["uv", "run", "panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

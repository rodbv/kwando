# Multi-stage build for production-grade security and efficiency
# Stage 1: Build stage with all dependencies
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv \
    && uv pip install --system .

# Stage 2: Runtime stage - minimal Alpine image
FROM python:3.12-alpine AS runtime

# Install runtime dependencies only
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# Create non-root user with specific UID/GID for security
RUN addgroup -g 1001 -S appgroup \
    && adduser -u 1001 -S appuser -G appgroup

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5006

# Health check with proper timeout and retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5006/ || exit 1

# Security: Set read-only root filesystem where possible
# Note: Panel needs write access for temp files, so we can't make everything read-only

# Run the application
CMD ["panel", "serve", "src/dashboard.py", "--autoreload", "--address", "0.0.0.0"]

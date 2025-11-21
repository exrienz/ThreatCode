# Multi-stage build for ThreatCode Security Scanner

# Build stage: Install dependencies
FROM python:3.9-slim as builder

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage: Minimal image
FROM python:3.9-slim

# Create non-root user
RUN adduser --disabled-password --gecos '' --uid 1000 appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/

# Create directories for volumes
RUN mkdir -p /scan /reports && \
    chown -R appuser:appuser /app /scan /reports

# Switch to non-root user
USER appuser

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default entrypoint
ENTRYPOINT ["python", "-m", "src.main"]

# Default command
CMD ["--help"]

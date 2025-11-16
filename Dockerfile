FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    unar \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and source code needed for installation
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# Copy rest of application code (tests, etc.)
COPY . .

# Expose application and debug ports
EXPOSE ${PORT}
EXPOSE 5678

# Run the application (default without debugger)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --reload


# Use an official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for uv)
RUN apt-get update && apt-get install -y curl gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Sync dependencies
RUN uv sync --frozen

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI app using uv
CMD ["uv", "run", "fastapi", "dev", "./src/main.py", "--host", "0.0.0.0", "--port", "8000"]
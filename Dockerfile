# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (common for ML)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir pyyaml

# Expose FastAPI port
EXPOSE 8000

# Run the API with uvicorn using your custom logging config
CMD ["uvicorn", "ml_end_to_end_pipeline.api.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--log-config", "logging_config.yaml"]

FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies required for clean Python setups
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency mappings
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application assets
COPY app/ ./app/

EXPOSE 8000

# Bind host port execution mappings cleanly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

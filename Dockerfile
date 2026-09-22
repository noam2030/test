# Google ADK Customer Support Agent Container
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr and writing bytecode
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    APP_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and configurations
COPY app/ ./app/
COPY main.py .
COPY .env.example .

# Expose Cloud Run default port
EXPOSE 8080

# Launch Google ADK Web UI / API Server
CMD ["adk", "web", ".", "--host", "0.0.0.0", "--port", "8080"]

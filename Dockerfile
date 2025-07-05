# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libportaudio2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables for Fly.io deployment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV FLY_APP_NAME=portfolio-voice-ai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Use production entry point optimized for Fly.io
# Follows LiveKit's recommended pattern with automatic agent dispatch
CMD ["python", "render_entrypoint.py"]

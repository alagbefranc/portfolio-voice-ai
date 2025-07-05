# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables for Render deployment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Use production entry point for Render deployment
# Follows LiveKit's recommended pattern with automatic agent dispatch
CMD ["python", "render_entrypoint.py"]

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
RUN pip install flask

# Copy application files
COPY . .

# Create a simple wrapper that runs both the agent and a health check server
RUN echo "from flask import Flask" > cloud_run_wrapper.py && \
    echo "import threading" >> cloud_run_wrapper.py && \
    echo "import subprocess" >> cloud_run_wrapper.py && \
    echo "import os" >> cloud_run_wrapper.py && \
    echo "import time" >> cloud_run_wrapper.py && \
    echo "" >> cloud_run_wrapper.py && \
    echo "app = Flask(__name__)" >> cloud_run_wrapper.py && \
    echo "" >> cloud_run_wrapper.py && \
    echo "@app.route('/')" >> cloud_run_wrapper.py && \
    echo "def health():" >> cloud_run_wrapper.py && \
    echo "    return 'Voice AI Agent is running', 200" >> cloud_run_wrapper.py && \
    echo "" >> cloud_run_wrapper.py && \
    echo "def run_agent():" >> cloud_run_wrapper.py && \
    echo "    time.sleep(2)  # Give Flask time to start" >> cloud_run_wrapper.py && \
    echo "    subprocess.run(['python', 'agent.py', 'start'])" >> cloud_run_wrapper.py && \
    echo "" >> cloud_run_wrapper.py && \
    echo "if __name__ == '__main__':" >> cloud_run_wrapper.py && \
    echo "    agent_thread = threading.Thread(target=run_agent, daemon=True)" >> cloud_run_wrapper.py && \
    echo "    agent_thread.start()" >> cloud_run_wrapper.py && \
    echo "    port = int(os.environ.get('PORT', 8080))" >> cloud_run_wrapper.py && \
    echo "    app.run(host='0.0.0.0', port=port)" >> cloud_run_wrapper.py

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the wrapper script
CMD ["python", "cloud_run_wrapper.py"]

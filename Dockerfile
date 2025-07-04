# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Cloud Run expects the app to listen on PORT
# Since this is a worker, we'll use a simple health check server
RUN echo 'from flask import Flask\n\
import threading\n\
import subprocess\n\
import os\n\
\n\
app = Flask(__name__)\n\
\n\
@app.route("/")\n\
def health():\n\
    return "Voice AI Agent is running", 200\n\
\n\
def run_agent():\n\
    subprocess.run(["python", "agent.py", "start"])\n\
\n\
if __name__ == "__main__":\n\
    # Start the agent in a background thread\n\
    agent_thread = threading.Thread(target=run_agent, daemon=True)\n\
    agent_thread.start()\n\
    \n\
    # Run Flask server for health checks\n\
    port = int(os.environ.get("PORT", 8080))\n\
    app.run(host="0.0.0.0", port=port)\n\
' > cloud_run_wrapper.py

# Add Flask to requirements for the health check server
RUN echo "flask" >> requirements.txt

# Install Flask
RUN pip install flask

# Run the wrapper script
CMD ["python", "cloud_run_wrapper.py"]

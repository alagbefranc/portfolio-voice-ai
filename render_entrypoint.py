#!/usr/bin/env python3
"""
Production entry point for Render.com deployment.
This follows LiveKit's recommended pattern for production deployment.
"""

import os
import subprocess
import threading
import time
import signal
import sys
from flask import Flask, request, jsonify, Response
import jwt
import json

app = Flask(__name__)

def generate_livekit_token(room_name, participant_name):
    """Generate a LiveKit JWT token for frontend connections"""
    
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("LiveKit API credentials not found")
    
    # Token payload
    now = int(time.time())
    exp = now + (6 * 60 * 60)  # 6 hours from now
    
    payload = {
        'iss': api_key,
        'sub': participant_name,
        'iat': now,
        'exp': exp,
        'room': room_name,
        'video': {
            'roomJoin': True,
            'room': room_name,
            'canPublish': True,
            'canSubscribe': True,
            'canPublishData': True
        }
    }
    
    # Generate token
    token = jwt.encode(payload, api_secret, algorithm='HS256')
    return token

@app.route('/')
def health():
    """Health check endpoint"""
    return 'Voice AI Agent is running', 200

@app.route('/generate-token', methods=['GET', 'POST', 'OPTIONS'])
def generate_token():
    """Generate LiveKit token for frontend connections"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            room_name = request.args.get('roomName', 'voice-consultation')
            participant_name = request.args.get('participantName', f'User-{int(time.time())}')
        else:  # POST
            data = request.get_json() or {}
            room_name = data.get('roomName', 'voice-consultation')
            participant_name = data.get('participantName', f'User-{int(time.time())}')
        
        token = generate_livekit_token(room_name, participant_name)
        
        livekit_url = os.environ.get('LIVEKIT_URL')
        
        response = jsonify({
            'token': token,
            'roomName': room_name,
            'participantName': participant_name,
            'livekitUrl': livekit_url,
            'hasToken': bool(token),
            'hasLivekitUrl': bool(livekit_url)
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        error_response = jsonify({'error': str(e)})
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response, 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle LiveKit webhook events (for logging/monitoring)"""
    
    try:
        # Get raw body for signature verification
        body = request.get_data()
        content_type = request.headers.get('Content-Type', '')
        
        print(f"Webhook received - Content-Type: {content_type}")
        
        # Parse the webhook event
        event_data = json.loads(body.decode('utf-8'))
        event_type = event_data.get('event')
        room_data = event_data.get('room', {})
        participant_data = event_data.get('participant', {})
        
        print(f"Received webhook event: {event_type}")
        print(f"Room: {room_data.get('name', 'Unknown')}")
        print(f"Participant: {participant_data.get('identity', 'Unknown') if participant_data else 'None'}")
        
        # Agent uses automatic dispatch - just log the events
        print(f"NOTE: Webhook event logged. Agent uses automatic dispatch to join rooms.")
        
        return jsonify({'status': 'ok', 'message': 'Webhook received - using automatic dispatch'}), 200
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Raw body: {body.decode('utf-8', errors='replace')}")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Global agent process variable
agent_process = None

def run_agent():
    """Run the agent worker using LiveKit's standard pattern"""
    global agent_process
    
    print("Starting LiveKit Voice AI Agent...")
    
    try:
        # Start the agent using LiveKit's standard command
        agent_process = subprocess.Popen(
            ['python', 'agent.py', 'start'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"Agent process started with PID: {agent_process.pid}")
        
        # Read and log agent output
        for line in iter(agent_process.stdout.readline, ''):
            if line:
                print(f"AGENT: {line.strip()}")
        
        # Wait for process to complete
        agent_process.wait()
        print(f"Agent process exited with code: {agent_process.returncode}")
        
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global agent_process
    
    print(f"Received signal {signum}, shutting down gracefully...")
    
    if agent_process and agent_process.poll() is None:
        print("Terminating agent process...")
        agent_process.terminate()
        
        # Wait up to 30 seconds for graceful shutdown
        try:
            agent_process.wait(timeout=30)
            print("Agent process terminated gracefully")
        except subprocess.TimeoutExpired:
            print("Agent process did not terminate gracefully, killing...")
            agent_process.kill()
    
    sys.exit(0)

def keepalive_ping():
    """Simple keepalive function to prevent Render from sleeping"""
    import requests
    
    def ping():
        while True:
            try:
                time.sleep(600)  # Wait 10 minutes
                # Self-ping to keep service awake (will be updated after Fly.io deployment)
                fly_url = os.environ.get('FLY_APP_URL', 'https://portfolio-voice-ai.fly.dev/')
                requests.get(fly_url, timeout=10)
                print("Keepalive ping sent")
            except Exception as e:
                print(f"Keepalive ping failed: {e}")
    
    # Start keepalive in background thread
    ping_thread = threading.Thread(target=ping, daemon=True)
    ping_thread.start()
    print("Keepalive service started")

if __name__ == '__main__':
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting Voice AI service on Render...")
    print("Agent will automatically join all new rooms matching 'portfolio-voice-*'")
    print("Deployment: 2025-07-05 13:54 UTC - Fixed LLM configuration")
    
    # Start keepalive service
    keepalive_ping()
    
    # Start the agent in a background thread
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    # Give the agent a moment to start
    time.sleep(2)
    
    # Run Flask server for health checks and token generation
    port = int(os.environ.get('PORT', 8080))
    
    # Use production WSGI server for better performance
    try:
        from waitress import serve
        print(f"Starting production server on port {port}")
        serve(app, host='0.0.0.0', port=port)
    except ImportError:
        print(f"Waitress not available, using Flask dev server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)

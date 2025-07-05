from flask import Flask, request, jsonify, Response
import threading
import subprocess
import os
import time
import jwt
import hashlib
import hmac
import json
from datetime import datetime

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

def verify_webhook(body, auth_header):
    """Verify webhook signature from LiveKit"""
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    
    print(f"Verifying webhook with API key: {api_key[:8] if api_key else 'None'}...")
    
    if not auth_header:
        print("No authorization header provided")
        return False
    
    # LiveKit sends JWT token directly without "Bearer " prefix
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
    else:
        token = auth_header  # Use token directly
    print(f"JWT token received: {token[:20]}...")
    
    try:
        # Decode the JWT token to verify it's from LiveKit
        decoded = jwt.decode(token, api_secret, algorithms=['HS256'])
        print(f"JWT decoded successfully: {decoded}")
        
        # Verify the payload hash if present
        if 'sha' in decoded:
            expected_hash = hashlib.sha256(body).hexdigest()
            received_hash = decoded['sha']
            print(f"Expected hash: {expected_hash}")
            print(f"Received hash: {received_hash}")
            if received_hash != expected_hash:
                print("Hash verification failed")
                return False
            print("Hash verification passed")
        else:
            print("No hash in JWT payload - skipping hash verification")
        
        return True
    except jwt.InvalidTokenError as e:
        print(f"JWT verification failed: {e}")
        return False

@app.route('/')
def health():
    return 'Voice AI Agent is running', 200

@app.route('/debug-webhook', methods=['POST'])
def debug_webhook():
    """Debug webhook without verification to understand LiveKit's format"""
    try:
        # Get all request data
        body = request.get_data()
        headers = dict(request.headers)
        auth_header = request.headers.get('Authorization', '')
        
        print("=" * 60)
        print("WEBHOOK DEBUG - Raw Request")
        print("=" * 60)
        print(f"Content-Type: {request.headers.get('Content-Type', '')}")
        print(f"Content-Length: {len(body)}")
        print(f"Authorization: {auth_header[:30]}... (truncated)")
        
        # Parse body
        body_text = body.decode('utf-8')
        event_data = json.loads(body_text)
        print("Event Data:")
        print(json.dumps(event_data, indent=2))
        
        # Analyze JWT token
        if auth_header:
            import jwt
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
            
            # Decode without verification to see payload
            unverified = jwt.decode(token, options={"verify_signature": False})
            print("JWT Payload (unverified):")
            print(json.dumps(unverified, indent=2))
            
            # Try verification with API secret
            api_secret = os.getenv('LIVEKIT_API_SECRET')
            try:
                verified = jwt.decode(token, api_secret, algorithms=['HS256'])
                print("✅ JWT verification SUCCESS with API secret")
            except jwt.InvalidTokenError as e:
                print(f"❌ JWT verification FAILED with API secret: {e}")
        
        print("=" * 60)
        
        return jsonify({"status": "debug_ok"}), 200
        
    except Exception as e:
        print(f"Debug webhook error: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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
    """Handle LiveKit webhook events (kept for backward compatibility)"""
    
    try:
        # Get raw body for signature verification
        body = request.get_data()
        auth_header = request.headers.get('Authorization')
        content_type = request.headers.get('Content-Type', '')
        
        print(f"Webhook received - Content-Type: {content_type}")
        print(f"Authorization header present: {'Yes' if auth_header else 'No'}")
        
        # Parse the webhook event
        event_data = json.loads(body.decode('utf-8'))
        event_type = event_data.get('event')
        room_data = event_data.get('room', {})
        participant_data = event_data.get('participant', {})
        
        print(f"Received webhook event: {event_type}")
        print(f"Room: {room_data.get('name', 'Unknown')}")
        print(f"Participant: {participant_data.get('identity', 'Unknown') if participant_data else 'None'}")
        
        # Log webhook events but agent uses automatic dispatch
        print(f"NOTE: Webhook event logged. Agent uses automatic dispatch to join rooms.")
        
        return jsonify({'status': 'ok', 'message': 'Webhook received - using automatic dispatch'}), 200
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Raw body: {body.decode('utf-8', errors='replace')}")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def run_agent():
    """Run the agent worker in background using automatic dispatch"""
    time.sleep(2)  # Give Flask time to start
    print("Starting Voice AI agent with automatic dispatch pattern...")
    try:
        # Start the agent in production mode with automatic dispatch
        process = subprocess.Popen(['python', 'agent.py', 'start'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True, 
                                 bufsize=1, 
                                 universal_newlines=True)
        
        print(f"Agent subprocess started with PID: {process.pid}")
        
        # Read output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"AGENT: {output.strip()}")
        
        # Get any remaining output
        rc = process.poll()
        stderr_output = process.stderr.read()
        
        if rc != 0:
            print(f"Agent subprocess failed with return code: {rc}")
            if stderr_output:
                print(f"STDERR: {stderr_output}")
        else:
            print("Agent subprocess completed successfully")
            
    except Exception as e:
        print(f"Error starting agent subprocess: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    print("Starting Voice AI Flask server with automatic agent dispatch")
    print("Agent will automatically join all new rooms")
    
    # Start the agent in a background thread
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    # Run Flask server for health checks, token generation, and webhook handling
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

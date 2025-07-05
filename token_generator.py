from flask import Flask, request, jsonify
import jwt
import time
import os
from datetime import datetime, timedelta

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

@app.route('/generate-token', methods=['POST'])
def generate_token():
    """Generate LiveKit token for frontend connections"""
    try:
        data = request.get_json()
        room_name = data.get('roomName', 'voice-consultation')
        participant_name = data.get('participantName', f'User-{int(time.time())}')
        
        token = generate_livekit_token(room_name, participant_name)
        
        return jsonify({
            'token': token,
            'roomName': room_name,
            'participantName': participant_name,
            'livekitUrl': os.environ.get('LIVEKIT_URL')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return "Token generator is running", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

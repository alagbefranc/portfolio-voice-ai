#!/usr/bin/env python3
"""
Temporary webhook debugging - bypasses verification to see the payload
"""

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/debug-webhook', methods=['POST'])
def debug_webhook():
    """Debug webhook without verification"""
    try:
        # Get all request data
        body = request.get_data()
        headers = dict(request.headers)
        content_type = request.headers.get('Content-Type', '')
        auth_header = request.headers.get('Authorization', '')
        
        print("=" * 60)
        print("WEBHOOK DEBUG - Raw Request")
        print("=" * 60)
        print(f"Method: {request.method}")
        print(f"Content-Type: {content_type}")
        print(f"Content-Length: {len(body)}")
        print()
        print("Headers:")
        for key, value in headers.items():
            if key.lower() == 'authorization':
                print(f"  {key}: {value[:30]}... (truncated)")
            else:
                print(f"  {key}: {value}")
        print()
        
        # Parse body
        try:
            body_text = body.decode('utf-8')
            print(f"Raw Body ({len(body_text)} chars):")
            print(body_text)
            print()
            
            # Try to parse as JSON
            if body_text:
                event_data = json.loads(body_text)
                print("Parsed JSON:")
                print(json.dumps(event_data, indent=2))
                print()
                
                # Extract key information
                event_type = event_data.get('event', 'unknown')
                room_data = event_data.get('room', {})
                participant_data = event_data.get('participant', {})
                
                print("Key Information:")
                print(f"  Event Type: {event_type}")
                print(f"  Room Name: {room_data.get('name', 'N/A')}")
                print(f"  Room SID: {room_data.get('sid', 'N/A')}")
                if participant_data:
                    print(f"  Participant: {participant_data.get('identity', 'N/A')}")
                    print(f"  Participant SID: {participant_data.get('sid', 'N/A')}")
                else:
                    print("  Participant: None")
                print()
                
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw body: {body_text}")
        except UnicodeDecodeError as e:
            print(f"Unicode Decode Error: {e}")
            print(f"Raw bytes: {body}")
        
        # Analyze JWT token
        if auth_header:
            print("JWT Token Analysis:")
            try:
                import jwt
                
                # Try to decode without verification first
                token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
                unverified = jwt.decode(token, options={"verify_signature": False})
                print("  Unverified JWT payload:")
                print(f"    {json.dumps(unverified, indent=4)}")
                
                # Try with our API secret
                api_secret = os.getenv('LIVEKIT_API_SECRET')
                if api_secret:
                    try:
                        verified = jwt.decode(token, api_secret, algorithms=['HS256'])
                        print("  ✅ JWT verification with API secret: SUCCESS")
                        print(f"    Verified payload: {verified}")
                    except jwt.InvalidTokenError as e:
                        print(f"  ❌ JWT verification with API secret: FAILED - {e}")
                else:
                    print("  ⚠️  No API secret available for verification")
                    
            except Exception as e:
                print(f"  JWT analysis error: {e}")
        
        print("=" * 60)
        
        # Return success to LiveKit
        return jsonify({"status": "debug_ok", "message": "Webhook received and logged"}), 200
        
    except Exception as e:
        print(f"Debug webhook error: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

#!/usr/bin/env python3
"""
Test script to verify the webhook endpoint is working
"""

import requests
import json
import jwt
import time
import os
from dotenv import load_dotenv

load_dotenv()

def test_webhook_endpoint():
    """Test the webhook endpoint with a simulated LiveKit event"""
    
    # Webhook URL
    webhook_url = "https://voice-ai-agent-435044415111.us-central1.run.app/webhook"
    
    # Simulated webhook event payload
    event_payload = {
        "event": "participant_joined",
        "id": "test-event-123",
        "createdAt": int(time.time()),
        "room": {
            "name": "portfolio-voice-test-123",
            "sid": "RM_test123",
            "participants": [
                {
                    "identity": "visitor-123",
                    "name": "Test User",
                    "sid": "PA_test123"
                }
            ]
        },
        "participant": {
            "identity": "visitor-123",
            "name": "Test User",
            "sid": "PA_test123"
        }
    }
    
    # Convert to JSON string
    payload_str = json.dumps(event_payload)
    payload_bytes = payload_str.encode('utf-8')
    
    # Create JWT token for authentication (simulating LiveKit)
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
        return
    
    # Create JWT token with payload hash
    import hashlib
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()
    
    token_payload = {
        "iss": api_key,
        "exp": int(time.time()) + 300,  # 5 minutes from now
        "sha": payload_hash
    }
    
    auth_token = jwt.encode(token_payload, api_secret, algorithm='HS256')
    
    # Send the webhook request
    headers = {
        'Content-Type': 'application/webhook+json',
        'Authorization': f'Bearer {auth_token}'
    }
    
    try:
        print("Sending test webhook...")
        print(f"URL: {webhook_url}")
        print(f"Payload: {payload_str}")
        
        response = requests.post(webhook_url, data=payload_bytes, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")

if __name__ == "__main__":
    test_webhook_endpoint()

#!/usr/bin/env python3

import requests
import json
import time

def test_token_endpoint():
    """Test the Cloud Run token generation endpoint"""
    
    url = "https://voice-ai-agent-435044415111.us-central1.run.app/generate-token"
    
    # Test data matching frontend request
    test_data = {
        "roomName": f"portfolio-voice-{int(time.time())}",
        "participantName": f"visitor-{int(time.time())}"
    }
    
    print(f"Testing token endpoint: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! Response data:")
            print(f"- Room name: {data.get('roomName')}")
            print(f"- Participant: {data.get('participantName')}")
            print(f"- LiveKit URL: {data.get('livekitUrl')}")
            print(f"- Token (first 50 chars): {data.get('token', '')[:50]}...")
            
            return True
        else:
            print(f"\nError: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Voice AI Token Endpoint")
    print("=" * 40)
    
    success = test_token_endpoint()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Token endpoint test PASSED")
        print("\nNext steps:")
        print("1. Test your portfolio frontend connection")
        print("2. Verify agent auto-joins when you connect")
    else:
        print("❌ Token endpoint test FAILED")
        print("Check Cloud Run deployment and environment variables")

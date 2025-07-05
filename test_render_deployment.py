#!/usr/bin/env python3
"""
Test script for Render.com deployment.
Run this after deploying to verify everything works correctly.
"""

import requests
import json
import time
import os
from typing import Dict, Any

def test_health_endpoint(base_url: str) -> bool:
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_token_generation(base_url: str) -> bool:
    """Test token generation endpoint"""
    print("Testing token generation...")
    
    try:
        # Test GET request
        params = {
            'roomName': 'portfolio-voice-test',
            'participantName': 'test-user'
        }
        
        response = requests.get(f"{base_url}/generate-token", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['token', 'roomName', 'participantName', 'livekitUrl', 'hasToken', 'hasLivekitUrl']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Token generation missing fields: {missing_fields}")
                return False
            
            if data['hasToken'] and data['hasLivekitUrl']:
                print("✅ Token generation passed")
                print(f"   Room: {data['roomName']}")
                print(f"   Participant: {data['participantName']}")
                print(f"   LiveKit URL: {data['livekitUrl']}")
                return True
            else:
                print("❌ Token generation failed: Missing token or LiveKit URL")
                return False
        else:
            print(f"❌ Token generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return False

def test_cors(base_url: str) -> bool:
    """Test CORS headers"""
    print("Testing CORS headers...")
    
    try:
        # Test OPTIONS request
        response = requests.options(f"{base_url}/generate-token", timeout=10)
        
        if response.status_code == 200:
            headers = response.headers
            
            if 'Access-Control-Allow-Origin' in headers:
                print("✅ CORS headers present")
                return True
            else:
                print("❌ CORS headers missing")
                return False
        else:
            print(f"❌ CORS test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_webhook_endpoint(base_url: str) -> bool:
    """Test webhook endpoint"""
    print("Testing webhook endpoint...")
    
    try:
        # Mock webhook payload
        webhook_payload = {
            "event": "participant_joined",
            "room": {"name": "portfolio-voice-test"},
            "participant": {"identity": "test-user"}
        }
        
        response = requests.post(
            f"{base_url}/webhook",
            json=webhook_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print("✅ Webhook endpoint works")
                return True
            else:
                print(f"❌ Webhook unexpected response: {data}")
                return False
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def run_deployment_tests(base_url: str) -> Dict[str, bool]:
    """Run all deployment tests"""
    
    print(f"🚀 Testing Render deployment at: {base_url}")
    print("=" * 50)
    
    results = {}
    
    # Wait a moment for service to be ready
    print("Waiting for service to start...")
    time.sleep(5)
    
    # Run tests
    results['health'] = test_health_endpoint(base_url)
    results['token_generation'] = test_token_generation(base_url)
    results['cors'] = test_cors(base_url)
    results['webhook'] = test_webhook_endpoint(base_url)
    
    return results

def main():
    """Main test function"""
    
    # Get base URL from command line or environment
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = os.environ.get('RENDER_URL', '').rstrip('/')
        
        if not base_url:
            print("❌ Please provide the Render URL:")
            print("   python test_render_deployment.py https://your-app.onrender.com")
            print("   OR set RENDER_URL environment variable")
            return
    
    # Validate URL
    if not base_url.startswith(('http://', 'https://')):
        print("❌ URL must start with http:// or https://")
        return
    
    # Run tests
    results = run_deployment_tests(base_url)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is ready.")
    else:
        print("⚠️  Some tests failed. Check the logs above and your Render configuration.")
        
        print("\n🔧 Troubleshooting tips:")
        if not results.get('health'):
            print("   - Check Render logs for startup errors")
            print("   - Verify the service is running")
        
        if not results.get('token_generation'):
            print("   - Check LiveKit environment variables")
            print("   - Verify LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")
        
        if not results.get('cors'):
            print("   - Check CORS configuration in the code")
        
        if not results.get('webhook'):
            print("   - Check webhook endpoint implementation")

if __name__ == "__main__":
    main()

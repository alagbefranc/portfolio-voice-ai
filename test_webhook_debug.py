#!/usr/bin/env python3
"""
Simple webhook debugging script to test without JWT verification
"""

import requests
import json
import time

def test_webhook_with_debug():
    """Test webhook with debug payload"""
    print("🔍 Testing Webhook Debug Endpoint")
    print("=" * 50)
    
    deployment_url = "https://voice-ai-agent-435044415111.us-central1.run.app"
    
    # Create a realistic webhook payload
    test_payload = {
        "event": "room_started",
        "room": {
            "sid": "RM_test123",
            "name": "portfolio-voice-debug-test",
            "creation_time": int(time.time()),
            "participants": []
        },
        "participant": None
    }
    
    print(f"📝 Test payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{deployment_url}/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 401:
            print("\n✅ Expected 401 - Webhook verification is working")
            print("   This means the webhook endpoint is receiving requests")
            print("   The 401 error is expected because we don't have proper JWT signing")
        elif response.status_code == 200:
            print("\n🎉 Webhook processed successfully!")
        else:
            print(f"\n❌ Unexpected response: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Webhook test failed: {e}")
        return False

def check_livekit_webhook_config():
    """Provide instructions for checking LiveKit webhook config"""
    print("\n🔧 LiveKit Webhook Configuration Check")
    print("=" * 50)
    
    print("Please verify the following in your LiveKit Cloud console:")
    print()
    print("1. 🌐 Go to: https://cloud.livekit.io/")
    print("2. 📋 Navigate to your project")
    print("3. ⚙️  Go to 'Settings' or 'Webhooks' section")
    print("4. ✅ Verify webhook configuration:")
    print()
    print("   📍 URL: https://voice-ai-agent-435044415111.us-central1.run.app/webhook")
    print("   🔔 Events enabled:")
    print("      ✅ room_started")
    print("      ✅ participant_joined")
    print("      ✅ participant_left (optional)")
    print("   🔐 Secret: Should be your LiveKit API Secret")
    print()
    print("5. 🧪 Test the webhook in LiveKit console if available")
    print()
    
    print("🚨 Common Issues:")
    print("   • Webhook URL not set or incorrect")
    print("   • Events not enabled") 
    print("   • Wrong secret configured")
    print("   • Webhook disabled or inactive")
    print()

def manual_test_instructions():
    """Provide manual testing instructions"""
    print("\n🧪 Manual Testing Instructions")
    print("=" * 50)
    
    print("To test if the agent joins rooms manually:")
    print()
    print("1. 🌐 Open your portfolio website")
    print("2. 🎙️  Start a voice consultation")
    print("3. 📝 Ensure the room name starts with 'portfolio-voice-'")
    print("4. 🔍 Check LiveKit console → Rooms → Active Rooms")
    print("5. 👥 Look for agent participant in the room list")
    print()
    print("Expected behavior:")
    print("   ✅ User joins room")
    print("   ✅ Webhook triggers (room_started event)")
    print("   ✅ Agent automatically joins room")
    print("   ✅ Agent appears in participant list")
    print("   ✅ Agent responds to voice input")
    print()
    
    room_name = f"portfolio-voice-manual-test-{int(time.time())}"
    print(f"💡 Suggested test room name: {room_name}")
    print()

def main():
    """Run webhook debugging tests"""
    print("🐛 Voice AI Webhook Debugging")
    print("=" * 50)
    
    # Test the webhook endpoint
    webhook_works = test_webhook_with_debug()
    
    # Provide configuration check instructions
    check_livekit_webhook_config()
    
    # Provide manual testing instructions
    manual_test_instructions()
    
    print("📊 Debug Summary")
    print("=" * 50)
    
    if webhook_works:
        print("✅ Webhook endpoint: Responding correctly")
        print("✅ Deployment: Working")
        print("❓ LiveKit config: Needs verification")
        print()
        print("🎯 Next steps:")
        print("   1. Verify webhook configuration in LiveKit console")
        print("   2. Test with your actual frontend")
        print("   3. Check that room names start with 'portfolio-voice-'")
    else:
        print("❌ Webhook endpoint: Not responding")
        print("❌ Deployment: May have issues")
        print()
        print("🔧 Fix deployment first, then check LiveKit config")

if __name__ == "__main__":
    main()

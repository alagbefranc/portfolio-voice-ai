#!/usr/bin/env python3
"""
Test script to verify agent behavior and room joining
"""

import os
import requests
import json
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

def test_token_generation():
    """Test token generation endpoint"""
    print("🔍 Testing Token Generation...")
    
    deployment_url = "https://voice-ai-agent-435044415111.us-central1.run.app"
    
    try:
        response = requests.post(
            f"{deployment_url}/generate-token",
            json={
                "roomName": "portfolio-voice-test-room",
                "participantName": "TestUser"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token generation successful")
            print(f"Room: {data.get('roomName')}")
            print(f"Participant: {data.get('participantName')}")
            print(f"LiveKit URL: {data.get('livekitUrl')}")
            print(f"Token: {data.get('token', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ Token generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Token generation test failed: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint with a simulated room_started event"""
    print("\n🔍 Testing Webhook Endpoint...")
    
    deployment_url = "https://voice-ai-agent-435044415111.us-central1.run.app"
    
    # Create a test webhook payload
    test_payload = {
        "event": "room_started",
        "room": {
            "name": "portfolio-voice-test-room",
            "participants": []
        },
        "participant": {
            "identity": "TestUser",
            "name": "Test User"
        }
    }
    
    try:
        # We would need to sign this properly with JWT, but let's see if the endpoint responds
        response = requests.post(
            f"{deployment_url}/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Webhook response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Webhook endpoint is working (401 expected due to missing auth)")
            return True
        elif response.status_code == 200:
            print("✅ Webhook endpoint processed successfully")
            return True
        else:
            print(f"❌ Unexpected webhook response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_local_agent_startup():
    """Test if the agent can start locally"""
    print("\n🔍 Testing Local Agent Startup...")
    
    try:
        # Import the agent module
        import agent
        
        print("✅ Agent module imported successfully")
        
        # Test if we can create the essential components
        from livekit.plugins import openai, deepgram, cartesia, silero
        
        print("✅ All LiveKit plugins loaded")
        
        # Test portfolio context loading
        context = agent.load_portfolio_context()
        if context and len(context) > 100:
            print("✅ Portfolio context loaded successfully")
            print(f"Context length: {len(context)} characters")
        else:
            print("❌ Portfolio context loading failed or too short")
            return False
        
        # Test booking handler
        handler = agent.booking_handler
        if handler:
            print("✅ Booking handler created successfully")
        else:
            print("❌ Booking handler creation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Local agent startup test failed: {e}")
        return False

def test_agent_function_tools():
    """Test agent function tools"""
    print("\n🔍 Testing Agent Function Tools...")
    
    try:
        import agent
        
        # Test function tools
        tools = agent.booking_tools
        print(f"✅ Found {len(tools)} booking tools")
        
        for tool in tools:
            print(f"  - {tool.__name__}: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Function tools test failed: {e}")
        return False

async def test_async_booking_functions():
    """Test async booking functions"""
    print("\n🔍 Testing Async Booking Functions...")
    
    try:
        import agent
        
        # Test get_available_times
        print("Testing get_available_times...")
        result = await agent.get_available_times()
        if result:
            print(f"✅ get_available_times returned: {result[:100]}...")
        else:
            print("❌ get_available_times returned empty result")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Async booking functions test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Voice AI Agent Behavior Tests")
    print("=" * 50)
    
    sync_tests = [
        ("Token Generation", test_token_generation),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Local Agent Startup", test_local_agent_startup),
        ("Agent Function Tools", test_agent_function_tools),
    ]
    
    async_tests = [
        ("Async Booking Functions", test_async_booking_functions),
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in sync_tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Run asynchronous tests
    for test_name, test_func in async_tests:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_func())
            loop.close()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your agent should be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    # Additional debugging suggestions
    print("\n" + "=" * 50)
    print("🔧 Debugging Suggestions:")
    print("=" * 50)
    
    if passed < total:
        print("1. Check Google Cloud Run logs for errors:")
        print("   gcloud logging read 'resource.type=\"cloud_run_revision\"' --limit 50")
        print()
        print("2. Verify your LiveKit webhook is configured correctly:")
        print("   - In LiveKit console, set webhook URL to: https://voice-ai-agent-435044415111.us-central1.run.app/webhook")
        print("   - Enable 'room_started' and 'participant_joined' events")
        print()
        print("3. Test the agent in a development environment:")
        print("   python agent.py start --room portfolio-voice-test")
        print()
        print("4. Check if the frontend is creating rooms with the correct pattern:")
        print("   - Room names should start with 'portfolio-voice-'")
        print("   - Example: 'portfolio-voice-12345'")
    else:
        print("✅ All components are working correctly!")
        print()
        print("If the agent is still not speaking, check:")
        print("1. LiveKit webhook configuration in LiveKit console")
        print("2. Room naming pattern in your frontend (must start with 'portfolio-voice-')")
        print("3. Google Cloud Run logs for runtime errors")
        print("4. Audio permissions in the user's browser")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

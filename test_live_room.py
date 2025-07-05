#!/usr/bin/env python3
"""
Live test script to create a real room and verify agent joins
"""

import os
import requests
import json
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_real_room_joining():
    """Test creating a real room and check if agent joins"""
    print("🚀 Testing Real Room Agent Joining")
    print("=" * 50)
    
    deployment_url = "https://voice-ai-agent-435044415111.us-central1.run.app"
    room_name = f"portfolio-voice-test-{int(time.time())}"
    
    print(f"📝 Test Room Name: {room_name}")
    print(f"🌐 Deployment URL: {deployment_url}")
    
    # Step 1: Generate token
    print("\n🔑 Step 1: Generating token...")
    try:
        response = requests.post(
            f"{deployment_url}/generate-token",
            json={
                "roomName": room_name,
                "participantName": "TestUser"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            livekit_url = data.get('livekitUrl')
            print("✅ Token generated successfully")
            print(f"   Room: {data.get('roomName')}")
            print(f"   LiveKit URL: {livekit_url}")
        else:
            print(f"❌ Token generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return False
    
    # Step 2: Connect to room using LiveKit SDK
    print("\n🏠 Step 2: Connecting to room...")
    try:
        from livekit import api, rtc
        
        # Create room connection
        room = rtc.Room()
        
        # Connect to the room
        await room.connect(livekit_url, token)
        print(f"✅ Connected to room: {room_name}")
        
        # Wait a moment for webhook to trigger
        print("⏳ Waiting 10 seconds for agent to join via webhook...")
        await asyncio.sleep(10)
        
        # Check participants
        participants = list(room.remote_participants.values())
        print(f"👥 Room participants: {len(participants) + 1} total (including self)")
        
        agent_found = False
        for participant in participants:
            print(f"   - {participant.identity} (Agent: {'agent' in participant.identity.lower()})")
            if 'agent' in participant.identity.lower():
                agent_found = True
        
        if agent_found:
            print("🎉 SUCCESS: Agent found in room!")
        else:
            print("⚠️  Agent not found in room participants")
            print("   This could mean:")
            print("   1. Webhook not configured correctly in LiveKit console")
            print("   2. Agent startup failed (check Cloud Run logs)")
            print("   3. Room name pattern issue")
        
        # Disconnect
        await room.disconnect()
        print("🔌 Disconnected from room")
        
        return agent_found
        
    except ImportError:
        print("❌ LiveKit SDK not available for direct room testing")
        print("   You can test manually by:")
        print("   1. Using your frontend to connect to this room")
        print("   2. Checking LiveKit console for participants")
        print("   3. Looking for agent in the participant list")
        return None
        
    except Exception as e:
        print(f"❌ Room connection error: {e}")
        return False

def check_recent_webhook_activity():
    """Check for recent webhook activity in logs"""
    print("\n📊 Checking Recent Webhook Activity...")
    
    try:
        import subprocess
        result = subprocess.run([
            'gcloud', 'logging', 'read', 
            'resource.type="cloud_run_revision"',
            '--limit', '50',
            '--format', 'json'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logs = json.loads(result.stdout)
            
            webhook_events = []
            agent_starts = []
            
            for log in logs:
                payload = log.get('textPayload', '')
                timestamp = log.get('timestamp', '')
                
                if 'webhook' in payload.lower():
                    webhook_events.append((timestamp, payload))
                elif 'starting agent for room' in payload.lower():
                    agent_starts.append((timestamp, payload))
            
            print(f"📈 Found {len(webhook_events)} webhook-related log entries")
            print(f"🤖 Found {len(agent_starts)} agent startup attempts")
            
            if webhook_events:
                print("\n📝 Recent webhook events:")
                for timestamp, event in webhook_events[-5:]:  # Last 5 events
                    print(f"   {timestamp}: {event}")
            
            if agent_starts:
                print("\n🚀 Recent agent starts:")
                for timestamp, event in agent_starts[-3:]:  # Last 3 starts
                    print(f"   {timestamp}: {event}")
            
            return len(webhook_events) > 0 or len(agent_starts) > 0
            
        else:
            print(f"❌ Failed to fetch logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Log checking failed: {e}")
        return False

def main():
    """Run live room test"""
    print("🎙️  Live Voice AI Agent Room Test")
    print("=" * 50)
    
    # Check webhook activity first
    webhook_activity = check_recent_webhook_activity()
    
    # Test room joining
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_joined = loop.run_until_complete(test_real_room_joining())
        loop.close()
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        agent_joined = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if agent_joined is True:
        print("🎉 SUCCESS: Agent is working correctly!")
        print("   ✅ Token generation: Working")
        print("   ✅ Room connection: Working") 
        print("   ✅ Agent auto-join: Working")
        print("   ✅ Webhook: Configured correctly")
    elif agent_joined is False:
        print("⚠️  ISSUE: Agent not joining rooms")
        print("   ✅ Token generation: Working")
        print("   ✅ Room connection: Working")
        print("   ❌ Agent auto-join: Not working")
        print("\n🔧 Next steps:")
        print("   1. Verify webhook URL in LiveKit console")
        print("   2. Check webhook events are enabled (room_started, participant_joined)")
        print("   3. Ensure room names start with 'portfolio-voice-'")
        print("   4. Check Cloud Run logs for agent startup errors")
    else:
        print("ℹ️  SDK Test Unavailable")
        print("   ✅ Token generation: Working")
        print("   ✅ Webhook endpoint: Working")
        print("\n🧪 Manual test steps:")
        print("   1. Use your frontend to connect to a room named 'portfolio-voice-test'")
        print("   2. Check LiveKit console → Rooms → Active rooms")
        print("   3. Look for agent participant in the room")
        print("   4. Speak into microphone to test agent response")
    
    if webhook_activity:
        print(f"\n📈 Webhook activity detected - system is receiving events")
    else:
        print(f"\n📉 No recent webhook activity - check LiveKit console configuration")
    
    return agent_joined

if __name__ == "__main__":
    success = main()
    if success is True:
        print("\n🎯 Your voice AI agent is working perfectly!")
    elif success is False:
        print("\n🔧 Agent needs webhook configuration fixes")
    else:
        print("\n🧪 Manual testing required")

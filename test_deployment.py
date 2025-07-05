#!/usr/bin/env python3
"""
Diagnostic script to test the voice AI agent deployment
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are present"""
    required_vars = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET', 
        'LIVEKIT_URL',
        'DEEPGRAM_API_KEY',
        'OPENAI_API_KEY',
        'CARTESIA_API_KEY',
        'CAL_COM_API_KEY',
        'CAL_COM_EVENT_TYPE_ID'
    ]
    
    print("🔍 Testing Environment Variables...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            # Show first 8 characters for security
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"\n❌ Missing {len(missing_vars)} environment variables!")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🔍 Testing Package Imports...")
    
    imports_to_test = [
        ('livekit.agents', 'LiveKit Agents'),
        ('livekit.plugins.deepgram', 'Deepgram Plugin'),
        ('livekit.plugins.openai', 'OpenAI Plugin'),
        ('livekit.plugins.cartesia', 'Cartesia Plugin'),
        ('livekit.plugins.silero', 'Silero Plugin'),
        ('livekit.plugins.noise_cancellation', 'Noise Cancellation Plugin'),
        ('flask', 'Flask'),
        ('jwt', 'PyJWT'),
        ('cal_integration', 'Cal.com Integration')
    ]
    
    failed_imports = []
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: FAILED - {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} packages!")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_cal_integration():
    """Test Cal.com integration"""
    print("\n🔍 Testing Cal.com Integration...")
    
    try:
        from cal_integration import MeetingBookingHandler
        
        handler = MeetingBookingHandler()
        print("✅ Cal.com handler created successfully")
        
        # Test API connection (this might fail if credentials are wrong)
        try:
            import asyncio
            
            async def test_cal_connection():
                try:
                    # This will test the basic connection
                    result = await handler.cal_booking.get_formatted_available_times()
                    print(f"✅ Cal.com API connection: OK")
                    return True
                except Exception as e:
                    print(f"❌ Cal.com API connection: FAILED - {e}")
                    return False
            
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(test_cal_connection())
            loop.close()
            
            return success
            
        except Exception as e:
            print(f"❌ Cal.com async test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Cal.com integration import failed: {e}")
        return False

def test_livekit_connection():
    """Test LiveKit connection"""
    print("\n🔍 Testing LiveKit Connection...")
    
    try:
        livekit_url = os.getenv('LIVEKIT_URL')
        if not livekit_url:
            print("❌ LIVEKIT_URL not set")
            return False
        
        # Test if URL is reachable (basic connectivity test)
        if livekit_url.startswith('wss://'):
            http_url = livekit_url.replace('wss://', 'https://')
            try:
                response = requests.get(http_url, timeout=10)
                print(f"✅ LiveKit URL reachable: {response.status_code}")
                return True
            except Exception as e:
                print(f"❌ LiveKit URL not reachable: {e}")
                return False
        else:
            print(f"❌ Invalid LiveKit URL format: {livekit_url}")
            return False
            
    except Exception as e:
        print(f"❌ LiveKit connection test failed: {e}")
        return False

def test_deployment_url():
    """Test if deployment URL is responding"""
    print("\n🔍 Testing Deployment URL...")
    
    # You'll need to replace this with your actual Google Cloud Run URL
    deployment_url = input("Enter your Google Cloud Run deployment URL (or press Enter to skip): ").strip()
    
    if not deployment_url:
        print("⏭️  Skipping deployment URL test")
        return True
    
    try:
        response = requests.get(deployment_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Deployment URL responding: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ Deployment URL error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Deployment URL test failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 Voice AI Agent Deployment Diagnostics")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Package Imports", test_imports),
        ("Cal.com Integration", test_cal_integration),
        ("LiveKit Connection", test_livekit_connection),
        ("Deployment URL", test_deployment_url)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
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
        print("🎉 All tests passed! Your deployment should be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above to fix deployment issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

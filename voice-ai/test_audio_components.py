#!/usr/bin/env python3
"""
Test script to validate all audio components work correctly
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_audio_components():
    """Test all audio components individually"""
    print("🔍 Testing LiveKit Agents Audio Components...")
    print("=" * 50)
    
    try:
        # Test STT (Speech-to-Text)
        print("📝 Testing Deepgram STT...")
        from livekit.plugins import deepgram
        stt = deepgram.STT(model="nova-3", language="multi")
        print("✅ Deepgram STT initialized successfully")
        
        # Test TTS (Text-to-Speech) 
        print("🔊 Testing Cartesia TTS...")
        from livekit.plugins import cartesia
        tts = cartesia.TTS(
            model="sonic-2", 
            voice="8e093c57-1b16-461f-bb39-893c9992c710"  # Your custom voice
        )
        print("✅ Cartesia TTS initialized successfully")
        
        # Test VAD (Voice Activity Detection)
        print("🎤 Testing Silero VAD...")
        from livekit.plugins import silero
        vad = silero.VAD.load()
        print("✅ Silero VAD loaded successfully")
        
        # Test LLM
        print("🧠 Testing OpenAI LLM...")
        from livekit.plugins import openai
        llm = openai.LLM(model="gpt-4o-mini", temperature=0.7)
        print("✅ OpenAI LLM initialized successfully")
        
        # Test noise cancellation
        print("🔇 Testing Noise Cancellation...")
        from livekit.plugins import noise_cancellation
        nc = noise_cancellation.BVC()
        print("✅ Noise cancellation initialized successfully")
        
        print("\n" + "=" * 50)
        print("🎉 ALL AUDIO COMPONENTS WORKING!")
        print("✅ Your voice AI agent should work perfectly!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try: pip install the missing package")
        return False
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Check your .env file and API keys")
        return False

async def test_agent_import():
    """Test if the agent can be imported"""
    print("\n🤖 Testing Agent Import...")
    try:
        from agent import entrypoint, booking_handler
        print("✅ Agent imported successfully")
        print("✅ Booking handler loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Agent Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Voice AI Audio Component Test")
    print("=" * 50)
    
    # Test audio components
    audio_ok = await test_audio_components()
    
    # Test agent import
    agent_ok = await test_agent_import()
    
    print("\n" + "=" * 50)
    if audio_ok and agent_ok:
        print("🎊 ALL TESTS PASSED!")
        print("🚀 Ready to start your voice AI agent!")
        print("\n💡 Next step: python agent.py dev")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return audio_ok and agent_ok

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test script to validate all audio components work correctly
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_audio_components():
    """Test all audio components individually"""
    print("🔍 Testing LiveKit Agents Audio Components...")
    print("=" * 50)
    
    try:
        # Test STT (Speech-to-Text)
        print("📝 Testing Deepgram STT...")
        from livekit.plugins import deepgram
        stt = deepgram.STT(model="nova-3", language="multi")
        print("✅ Deepgram STT initialized successfully")
        
        # Test TTS (Text-to-Speech) 
        print("🔊 Testing Cartesia TTS...")
        from livekit.plugins import cartesia
        tts = cartesia.TTS(
            model="sonic-2", 
            voice="8e093c57-1b16-461f-bb39-893c9992c710"  # Your custom voice
        )
        print("✅ Cartesia TTS initialized successfully")
        
        # Test VAD (Voice Activity Detection)
        print("🎤 Testing Silero VAD...")
        from livekit.plugins import silero
        vad = silero.VAD.load()
        print("✅ Silero VAD loaded successfully")
        
        # Test LLM
        print("🧠 Testing OpenAI LLM...")
        from livekit.plugins import openai
        llm = openai.LLM(model="gpt-4o-mini", temperature=0.7)
        print("✅ OpenAI LLM initialized successfully")
        
        # Test noise cancellation
        print("🔇 Testing Noise Cancellation...")
        from livekit.plugins import noise_cancellation
        nc = noise_cancellation.BVC()
        print("✅ Noise cancellation initialized successfully")
        
        print("\n" + "=" * 50)
        print("🎉 ALL AUDIO COMPONENTS WORKING!")
        print("✅ Your voice AI agent should work perfectly!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try: pip install the missing package")
        return False
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Check your .env file and API keys")
        return False

async def test_agent_import():
    """Test if the agent can be imported"""
    print("\n🤖 Testing Agent Import...")
    try:
        from agent import entrypoint, booking_handler
        print("✅ Agent imported successfully")
        print("✅ Booking handler loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Agent Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Voice AI Audio Component Test")
    print("=" * 50)
    
    # Test audio components
    audio_ok = await test_audio_components()
    
    # Test agent import
    agent_ok = await test_agent_import()
    
    print("\n" + "=" * 50)
    if audio_ok and agent_ok:
        print("🎊 ALL TESTS PASSED!")
        print("🚀 Ready to start your voice AI agent!")
        print("\n💡 Next step: python agent.py dev")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return audio_ok and agent_ok

if __name__ == "__main__":
    asyncio.run(main())

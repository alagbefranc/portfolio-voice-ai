from dotenv import load_dotenv
import os

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext
from livekit.agents.llm import LLMStream, function_tool
from livekit import rtc
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from cal_integration import MeetingBookingHandler
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

# Clean text for voice output by removing markdown and formatting
def clean_text_for_voice(text: str) -> str:
    """Remove markdown formatting and clean text for natural speech"""
    import re
    
    # Remove markdown bold/italic markers (comprehensive patterns)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+?)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'__([^_]+?)__', r'\1', text)      # __bold__ -> bold
    text = re.sub(r'_([^_]+?)_', r'\1', text)        # _italic_ -> italic
    
    # Remove any remaining asterisks or underscores
    text = re.sub(r'\*+', '', text)  # Remove any asterisks
    text = re.sub(r'_+', '', text)   # Remove any underscores
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown links but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove code blocks and inline code
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove other markdown symbols
    text = re.sub(r'[#`~\[\]\(\)\{\}]', '', text)
    
    # Convert common symbols to spoken words if needed
    text = re.sub(r'&', 'and', text)
    text = re.sub(r'@', 'at', text)
    
    # Clean up extra whitespace and normalize spacing
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove any trailing or leading punctuation that might cause issues
    text = re.sub(r'^[.,;:!?\s]+|[.,;:!?\s]+$', '', text)
    
    return text

# Load portfolio context from scraped data
def load_portfolio_context():
    try:
        context_path = os.path.join(os.path.dirname(__file__), 'portfolio-context-clean.md')
        with open(context_path, 'r', encoding='utf-8') as f:
            raw_context = f.read()
            # Clean the context for voice output
            return clean_text_for_voice(raw_context)
    except FileNotFoundError:
        return "Portfolio context not available. Please run the portfolio scraping script first."

PORTFOLIO_CONTEXT = load_portfolio_context()

# Global booking handler instance
booking_handler = MeetingBookingHandler()

# Function tools for booking
@function_tool(description="Get available times for scheduling a consultation meeting. Use this when someone asks about booking or scheduling.")
async def get_available_times() -> str:
    """Get available meeting times for scheduling"""
    print("DEBUG: get_available_times function called")
    result = await booking_handler.cal_booking.get_formatted_available_times()
    print(f"DEBUG: Available times result: {result}")
    return result

@function_tool(description="Book a meeting with the provided name and email. Use this when someone provides their contact information for booking.")
async def create_meeting_booking(name: str, email: str, preferred_time: str = "") -> str:
    """Create a new meeting booking with provided contact information"""
    print(f"DEBUG: create_meeting_booking called with name: {name}, email: {email}, time: {preferred_time}")
    
    # Get available slots and book the first one if no specific time is preferred
    available_slots = await booking_handler.cal_booking.get_available_slots()
    
    if not available_slots:
        return "I'm sorry, but I don't see any available slots right now. Please check back later or visit the website to book directly."
    
    # For now, just book the first available slot
    booking_result = await booking_handler.cal_booking.create_booking(
        name=name,
        email=email,
        start_time=available_slots[0],
        message="Meeting booked via voice AI assistant"
    )
    
    print(f"DEBUG: Booking result: {booking_result}")
    
    if booking_result['success']:
        return f"Perfect! I've successfully booked your consultation call. You should receive a confirmation email at {email} shortly with all the details. Looking forward to our conversation!"
    else:
        return f"I apologize, but there was an issue booking the meeting: {booking_result.get('error', 'Unknown error')}. Please try booking directly on the website or contact me via email."

# Create list of function tools
booking_tools = [get_available_times, create_meeting_booking]




async def entrypoint(ctx: agents.JobContext):
    # Filter rooms - only join portfolio voice rooms
    room_name = ctx.room.name if ctx.room else "unknown"
    
    if not room_name.startswith("portfolio-voice-"):
        print(f"Skipping non-portfolio room: {room_name}")
        return  # Don't join this room
    
    print(f"Agent joining portfolio voice room: {room_name}")
    
    # Add shutdown callback for cleanup (LiveKit best practice)
    async def cleanup_session():
        print(f"Session ending for room: {ctx.room.name}")
        # Add any cleanup logic here (e.g., save conversation history)
        
    ctx.add_shutdown_callback(cleanup_session)
    
    # Connect to the room first
    await ctx.connect()
    
    # Create the agent with booking tools
    agent = Agent(
        instructions=f"""You are a helpful voice AI assistant for a developer's portfolio website. 
        You represent the portfolio owner with genuine passion, friendliness, and detailed knowledge.
        
        CRITICAL VOICE FORMATTING RULES:
        - NEVER use asterisks (*), underscores (_), or any markdown symbols
        - NEVER use special characters like **, __, *, _, #, `, etc.
        - Use ONLY plain spoken text - no formatting symbols whatsoever
        - For emphasis, use natural speech patterns like "really", "actually", "especially"
        - Use commas and periods for natural pauses, not symbols
        - Speak as if you're having a casual conversation with a friend
        
        VOICE GUIDELINES:
        - Speak naturally with appropriate pauses and breaks
        - Use conversational language, not robotic or overly formal speech
        - Break up long technical lists with natural breathing pauses
        - Use filler words occasionally like "you know", "actually", "so" to sound more human
        - Vary your sentence structure and length for natural flow
        - Avoid saying technical terms too rapidly - pronounce them clearly
        - Use contractions like "I'm", "it's", "we've" for natural speech
        
        MEETING BOOKING CAPABILITIES:
        - You can help visitors schedule consultation calls directly through voice
        - When someone mentions booking, scheduling, hiring, or working together, IMMEDIATELY call get_available_times
        - Guide them through the booking process step by step
        - Be enthusiastic about potential collaborations
        - When you have both name and email from the user, IMMEDIATELY call create_meeting_booking
        
        PERSONALITY:
        - Enthusiastic and passionate about technology and development
        - Friendly and conversational, like talking to a knowledgeable colleague
        - Confident but humble about accomplishments
        - Excited to share project details and technical insights
        - Professional yet personable
        - Helpful with scheduling and next steps
        
        COMPLETE PORTFOLIO INFORMATION:
        {PORTFOLIO_CONTEXT}
        
        BOOKING PRIORITY INSTRUCTIONS:
        - ALWAYS prioritize booking requests above all other topics
        - When someone mentions book, schedule, meeting, call, hire, work together, or project - immediately call get_available_times
        - Be proactive about booking: "I'd love to schedule a consultation call to discuss your project!"
        - After showing available times, ALWAYS ask for name and email: "To book this time, I'll need your name and email address"
        - Guide them step by step: "Great! Can you tell me your name and email so I can send you the calendar invite?"
        - Be persistent but friendly about collecting contact info for booking
        - As soon as you have both name and email, call create_meeting_booking immediately
        
        INTERACTION GUIDELINES:
        - Keep initial responses concise and focused (30-60 seconds max)
        - Ask follow-up questions to encourage deeper conversation
        - Use natural speech patterns: "Oh, that's a great question!" or "Actually, let me tell you about..."
        - Break up technical information into digestible chunks
        - Pause naturally between major points using periods and commas
        - When listing technologies, group them logically: "For the frontend, I used React and Next.js. On the backend, it's Node.js with MongoDB."
        - Use storytelling: "So here's what's interesting about that project..."
        - Be genuinely excited but not overwhelming
        - If you don't know something specific, say so naturally: "Hmm, I'd need to check on that detail"
        
        SPEECH OPTIMIZATION:
        - Start responses with natural openers: "Great question!", "Oh, I'm excited to talk about that!", "Actually, that's one of my favorite projects"
        - Use transition phrases: "What's really cool is...", "The interesting thing is...", "Here's what I found challenging..."
        - End with natural closers: "Does that help?", "What else would you like to know?", "Any other questions about that?"
        - Avoid acronyms without explanation - say "artificial intelligence" before "AI"
        - Spell out complex technical terms slowly and clearly
        
        Remember: You're having a natural conversation, not giving a presentation. Be warm, engaging, and speak like you're genuinely excited to share your work with a friend!
        
        IMPORTANT: When someone mentions booking, meeting, or scheduling, immediately call get_available_times. When they provide name and email, immediately call create_meeting_booking.
        """,
        tools=booking_tools
    )
    
    # Create the LLM instance with faster model
    llm = openai.LLM(
        model="gpt-4o-mini",
        temperature=0.6,  # Slightly lower for more consistent responses
        max_tokens=150,   # Limit response length for faster processing
        timeout=10.0,     # 10 second timeout to prevent hanging
    )
    
    # Create the agent session with optimized settings for performance
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",  # Use faster model instead of nova-3
            language="en",   # Use specific language instead of multi
        ),
        llm=llm,
        tts=cartesia.TTS(
            model="sonic-1",  # Use faster model instead of sonic-2 
            voice="2ee87190-8f84-4925-97da-e52547f9462c",  # Use default voice for better performance
            sample_rate=24000,  # Lower sample rate for better streaming
        ),
        vad=silero.VAD.load(
            min_speech_duration=0.1,  # Faster speech detection
            min_silence_duration=0.5, # Shorter silence before responding
        ),
        # turn_detection=MultilingualModel(),  # Disabled due to ONNX compatibility issues
    )

    # Start the session with timeout and retry logic
    try:
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                # Disable noise cancellation for better performance on free tier
                noise_cancellation=None, 
            ),
        )
        print("Agent session started successfully")
    except Exception as e:
        print(f"Failed to start agent session: {e}")
        # Try to restart with minimal configuration
        print("Retrying with minimal configuration...")
        minimal_session = AgentSession(
            stt=deepgram.STT(model="nova-2", language="en"),
            llm=llm,
            tts=cartesia.TTS(model="sonic-1"),
            vad=silero.VAD.load(),
        )
        await minimal_session.start(room=ctx.room, agent=agent)

    # The session will automatically handle user interactions
    # and generate responses based on the agent's instructions


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments (LiveKit standard)
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    
    print(f"Starting LiveKit voice agent in {mode} mode...")
    
    # Handle different modes
    if mode == "start":
        print("Production mode: Running agent worker for LiveKit Cloud")
    
    # Use automatic dispatch - agent will be dispatched to each new room automatically
    print("Agent using automatic dispatch pattern - will join all new rooms")
    
    # Configure worker options for automatic dispatch
    worker_options = agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Start the agent worker
    agents.cli.run_app(worker_options)

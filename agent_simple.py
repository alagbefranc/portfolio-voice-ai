from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)

load_dotenv()


class PortfolioAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant for a portfolio website. 
            You can help visitors learn about the portfolio owner's projects, skills, and experience.
            
            Key information about the portfolio:
            - This is a modern portfolio showcasing various projects
            - The portfolio includes projects like Flashpoint QR, Clinical Assistant, Purpsend, 
              Gasaroo Delivery, Harvest Tracker, RAG Chatbot, Memorease, Smart Home Hub, and Fittrack Pro
            - The owner is a skilled developer working with modern technologies
            - Be friendly, professional, and helpful in guiding visitors through the portfolio
            - Keep responses concise but informative
            - If asked about specific projects, provide brief overviews and suggest they explore the project details
            """
        )


async def entrypoint(ctx: agents.JobContext):
    # Create a simpler session without turn detection for now
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="8e093c57-1b16-461f-bb39-893c9992c710"),
        vad=silero.VAD.load(),
        # Remove turn_detection for now to avoid model download issues
    )

    await session.start(
        room=ctx.room,
        agent=PortfolioAssistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Greet the visitor to the portfolio website and offer to help them explore the projects and learn more about the portfolio owner's work."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

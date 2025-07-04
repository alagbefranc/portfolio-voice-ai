# 🎤 Portfolio Voice AI Assistant

A modern voice AI assistant integrated into your portfolio website, built with LiveKit Agents and Next.js.

## ✨ Features

- **Real-time voice interaction** with portfolio visitors
- **Beautiful animated interface** that follows your portfolio's design patterns
- **Intelligent responses** about your projects, skills, and experience
- **Modern floating action button** with smooth animations
- **Professional voice quality** using state-of-the-art AI models
- **Responsive design** that works on all devices

## 🎨 Design Integration

The voice AI components are designed to seamlessly integrate with your portfolio's existing design system:

- **Gradient themes** using your portfolio's color palette (`--primary`, `--accent`)
- **Glassmorphism effects** with backdrop blur and transparency
- **Framer Motion animations** for smooth interactions
- **Custom CSS utilities** like `gradient-text`, `glow`, and `btn-primary`

## 🏗️ Architecture

### Frontend Components

1. **VoiceAIFab** - Animated floating action button
2. **VoiceAIAssistant** - Main voice interface panel
3. **VoiceAIProvider** - State management and integration
4. **useVoiceAI** - React hook for LiveKit connection

### Backend

- **Python Agent** - LiveKit Agents voice AI assistant
- **STT-LLM-TTS Pipeline** - Speech-to-Text, Language Model, Text-to-Speech

## 🚀 Quick Setup

### Prerequisites

- Python 3.9 or later
- Node.js and npm
- LiveKit Cloud account (free tier available)
- API keys for:
  - [Deepgram](https://deepgram.com/) (Speech-to-Text)
  - [OpenAI](https://platform.openai.com/) (Language Model)
  - [Cartesia](https://cartesia.ai) (Text-to-Speech)

### 1. Backend Setup

```bash
cd voice-ai

# Run the setup script
python setup.py

# Or manually:
pip install -r requirements.txt
python agent.py download-files
```

### 2. Environment Configuration

Copy the environment template and fill in your API keys:

```bash
cp .env.template .env
```

Edit `.env` with your actual credentials:

```env
# AI Provider Keys
DEEPGRAM_API_KEY=your_deepgram_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here

# LiveKit Credentials
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
LIVEKIT_URL=your_livekit_websocket_url_here
```

### 3. Start the Voice Agent

```bash
# Development mode (connects to LiveKit)
python agent.py dev

# Console mode (terminal only)
python agent.py console
```

### 4. Frontend Integration

The frontend components are already integrated into your portfolio. The voice AI will appear as a floating action button in the bottom-right corner.

## 🎯 Usage

1. **Click the floating microphone button** in the bottom-right corner
2. **Click "Start Voice Chat"** to connect to the AI assistant
3. **Speak naturally** - the AI will listen and respond about your portfolio
4. **Watch the animations** - the interface provides visual feedback during conversations

## 🎨 Customization

### Styling

The components use your existing CSS variables and can be customized by modifying:

- `src/components/ui/voice-ai-assistant.tsx` - Main interface panel
- `src/components/ui/voice-ai-fab.tsx` - Floating action button
- `src/app/globals.css` - Global styles and animations

### AI Personality

Customize the AI assistant's personality by editing the instructions in:

```python
# voice-ai/agent.py
class PortfolioAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=\"\"\"Your custom instructions here...\"\"\"
        )
```

### Voice Configuration

Change the voice by modifying the TTS configuration:

```python
# voice-ai/agent.py
tts=cartesia.TTS(
    model="sonic-2", 
    voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"  # Change this voice ID
)
```

## 🔧 Development

### Testing the Agent

```bash
# Test in console mode (no LiveKit connection required)
python agent.py console

# Test with LiveKit in development mode
python agent.py dev
```

### Adding New Features

1. **Frontend**: Modify components in `src/components/`
2. **Backend**: Update the agent logic in `voice-ai/agent.py`
3. **Styling**: Use your existing CSS utilities and variables

## 📱 Mobile Support

The voice AI interface is fully responsive and works on mobile devices:

- Touch-friendly floating action button
- Optimized panel size for smaller screens
- Voice input works on modern mobile browsers

## 🔒 Security & Privacy

- All voice data is processed in real-time (not stored)
- Uses secure WebSocket connections
- API keys are server-side only
- Follows LiveKit's security best practices

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to connect"**: Check your LiveKit credentials and URL
2. **"Microphone not working"**: Ensure browser permissions are granted
3. **"Agent not responding"**: Verify all API keys are correct and have sufficient credits

### Debugging

```bash
# Check agent logs
python agent.py dev --verbose

# Test individual components
python agent.py console
```

## 🚀 Production Deployment

### Backend Deployment

Deploy the Python agent to a cloud service:

- **Railway**: `railway up`
- **Heroku**: `git push heroku main`
- **DigitalOcean**: App Platform deployment
- **AWS**: Lambda or ECS deployment

### Environment Variables

Set production environment variables:

```bash
# Production LiveKit URL
LIVEKIT_URL=wss://your-production-livekit-url

# Production API keys
DEEPGRAM_API_KEY=prod_key
OPENAI_API_KEY=prod_key
CARTESIA_API_KEY=prod_key
```

## 📊 Analytics & Monitoring

Consider adding:

- Voice interaction analytics
- Error tracking with Sentry
- Performance monitoring
- Usage metrics

## 🤝 Contributing

Want to improve the voice AI assistant? Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

Need help? Here are your options:

- **Documentation**: Check this README first
- **LiveKit Community**: [Join the Slack](https://livekit.io/join-slack)
- **AI Provider Support**: Contact Deepgram, OpenAI, or Cartesia
- **Issues**: Open a GitHub issue for bugs or feature requests

## 🎉 What's Next?

Potential enhancements:

- [ ] Multi-language support
- [ ] Voice authentication
- [ ] Integration with portfolio projects data
- [ ] Screen sharing capabilities
- [ ] Voice commands for navigation
- [ ] Custom wake words
- [ ] Voice analytics dashboard

---

**Enjoy your new voice AI assistant! 🎤✨**

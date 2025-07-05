# Deploying Voice AI Agent to Render.com

This guide walks you through deploying your LiveKit Voice AI Agent to Render.com for production use.

## Prerequisites

1. **GitHub Repository**: Push your code to a GitHub repository
2. **Render.com Account**: Sign up at [render.com](https://render.com)
3. **LiveKit Credentials**: Have your LiveKit URL, API Key, and API Secret ready
4. **Third-party API Keys**: Prepare your OpenAI, Deepgram, Cartesia, and Cal.com API keys

## Quick Deploy

### Option 1: Using render.yaml (Recommended)

1. **Update the repository URL** in `render.yaml`:
   ```yaml
   repo: https://github.com/YOUR_USERNAME/voice-ai
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

3. **Deploy to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and deploy

### Option 2: Manual Deployment

1. **Create a new Web Service** in Render:
   - Go to Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose the repository and branch

2. **Configure the service**:
   - **Name**: `voice-ai-agent`
   - **Runtime**: `Docker`
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Start Command**: `python render_entrypoint.py`

## Environment Variables

In your Render dashboard, add these environment variables:

### Required LiveKit Variables
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### Required Third-party API Keys
```
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key
CAL_API_KEY=your-cal-api-key
```

### System Variables (auto-set by Render)
```
PORT=8080
```

## Autoscaling Configuration

The `render.yaml` file includes autoscaling configuration:

- **Minimum instances**: 1
- **Maximum instances**: 10
- **CPU threshold**: 50% (scale up when CPU usage hits 50%)
- **Memory threshold**: 70% (scale up when memory usage hits 70%)

You can adjust these values based on your traffic patterns.

## Health Checks

The service includes a health check endpoint at `/` that Render will use to monitor service health.

## How It Works

1. **Automatic Dispatch**: The agent uses LiveKit's automatic dispatch pattern, joining all new rooms that start with `portfolio-voice-`

2. **Background Agent**: The `render_entrypoint.py` starts the LiveKit agent worker in a background process

3. **Web Server**: A Flask web server handles health checks and token generation for your frontend

4. **Graceful Shutdown**: The service handles SIGTERM signals gracefully, allowing ongoing conversations to finish

## Monitoring

Monitor your deployment in the Render dashboard:

- **Logs**: View real-time logs to see agent activity
- **Metrics**: Monitor CPU, memory, and response times
- **Events**: Track deployments and scaling events

## Scaling for Production

For production workloads, consider:

1. **Upgrade Plan**: Use "Starter Plus" or "Professional" plans for better performance
2. **Resource Allocation**: Increase CPU/memory if needed
3. **Load Testing**: Test with your expected concurrent user load
4. **Monitoring**: Set up alerts for high CPU/memory usage

## Troubleshooting

### Agent Not Joining Rooms
- Check logs for connection errors
- Verify LiveKit credentials are correct
- Ensure room names start with `portfolio-voice-`

### Token Generation Failing
- Verify LIVEKIT_API_KEY and LIVEKIT_API_SECRET are set
- Check LIVEKIT_URL format (should start with `wss://`)

### High CPU Usage
- Consider upgrading your Render plan
- Adjust autoscaling thresholds
- Optimize agent code for performance

### Audio Issues
- Verify all required audio dependencies are installed
- Check that the container has access to audio libraries
- Test with a simple audio file first

## Frontend Integration

Update your frontend to use the Render deployment URL:

```javascript
const response = await fetch('https://your-app.onrender.com/generate-token', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## Cost Optimization

- Use autoscaling to scale down during low traffic
- Monitor usage in Render dashboard
- Consider scheduled scaling for predictable traffic patterns

## Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **LiveKit Documentation**: [docs.livekit.io](https://docs.livekit.io)
- **GitHub Issues**: Report issues in your repository

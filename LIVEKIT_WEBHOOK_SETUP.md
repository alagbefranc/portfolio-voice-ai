# LiveKit Webhook Configuration for Auto-Join Agent

## Overview
To make your Voice AI agent automatically join rooms when users connect from your portfolio, you need to configure a webhook in your LiveKit Cloud project.

## Steps to Configure Webhook

### 1. Access LiveKit Cloud Console
- Go to https://cloud.livekit.io/
- Navigate to your project
- Go to Settings → Webhooks

### 2. Add Webhook URL
**Webhook URL:** `https://voice-ai-agent-435044415111.us-central1.run.app/webhook`

**Important:** We need to add a webhook endpoint to your Cloud Run service first (see below).

### 3. Configure Webhook Events
Select these events:
- `room_started` - When a new room is created
- `participant_joined` - When a user joins a room

### 4. Add Authentication (Optional but Recommended)
- Generate a webhook secret in LiveKit Cloud
- We'll use this to verify webhook authenticity

## Required Updates to Cloud Run Service

We need to add a webhook endpoint to your `cloud_run_wrapper.py` that:

1. Receives webhook notifications from LiveKit
2. Automatically starts your agent when users join rooms
3. Connects the agent to the correct room

## Webhook Endpoint Implementation

The webhook will:
- Listen for `room_started` or `participant_joined` events
- Check if the room needs an agent (no agent participants yet)
- Launch your agent for that specific room

## Alternative: Auto-Subscribe Configuration

If webhooks are complex, LiveKit agents can also be configured to auto-subscribe to room patterns:

```python
# In agent.py, modify the WorkerOptions
agents.cli.run_app(agents.WorkerOptions(
    entrypoint_fnc=entrypoint,
    # Auto-join rooms matching this pattern
    room_pattern="portfolio-voice-*"
))
```

## Current Status

✅ Frontend updated to use Cloud Run token endpoint
✅ Agent deployed on Cloud Run with token generation
❌ Webhook configuration needed for auto-join

## Next Steps

1. Add webhook endpoint to cloud_run_wrapper.py
2. Configure webhook in LiveKit Cloud console
3. Test the complete flow: Frontend → Token → Room → Agent Auto-Join

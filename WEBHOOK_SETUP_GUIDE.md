# LiveKit Webhook Configuration Guide

## 🚀 Quick Fix Summary

Your voice AI agent deployment is now working! The issue was a compatibility problem with the LiveKit agents library that has been resolved.

## ✅ Current Status
- ✅ Agent is deployed and running
- ✅ Token generation endpoint working
- ✅ Webhook endpoint configured
- ✅ All integrations (Cal.com, OpenAI, etc.) working

## 🔧 Critical Configuration Steps

### 1. LiveKit Console Webhook Setup

**IMPORTANT**: You must configure the webhook in your LiveKit console for the agent to auto-join rooms.

1. Go to your LiveKit Cloud console: https://cloud.livekit.io/
2. Navigate to your project
3. Go to "Webhooks" section
4. Add a new webhook with these settings:
   - **URL**: `https://voice-ai-agent-435044415111.us-central1.run.app/webhook`
   - **Events**: Enable these events:
     - ✅ `room_started`
     - ✅ `participant_joined`
   - **Secret**: Use your LiveKit API Secret (already configured)

### 2. Frontend Room Naming

**CRITICAL**: Your frontend must create room names that start with `portfolio-voice-` for the agent to auto-join.

✅ **Correct room names:**
- `portfolio-voice-12345`
- `portfolio-voice-consultation`
- `portfolio-voice-demo`

❌ **Incorrect room names:**
- `voice-chat-123` (missing portfolio prefix)
- `consultation-room` (wrong pattern)
- `portfolio-123` (missing voice prefix)

### 3. Frontend Integration Example

```javascript
// When creating a room in your frontend:
const roomName = `portfolio-voice-${Date.now()}`;

// Request token from your deployment
const response = await fetch('https://voice-ai-agent-435044415111.us-central1.run.app/generate-token', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        roomName: roomName,
        participantName: 'User'
    })
});

const { token, livekitUrl } = await response.json();

// Use token to connect to LiveKit room
// Agent will auto-join when webhook receives room_started event
```

## 🐛 Debugging Steps

### Check if Agent Joined Room

1. **In LiveKit Console**: Check "Rooms" section to see active rooms and participants
2. **Look for agent participant**: Should appear as a participant when room starts
3. **Check room name pattern**: Ensure room starts with `portfolio-voice-`

### Check Logs

```bash
# Check recent deployment logs
gcloud logging read 'resource.type="cloud_run_revision"' --limit 20

# Look for these messages:
# ✅ "Starting agent for room: portfolio-voice-xxxx"
# ✅ "Agent started for room: portfolio-voice-xxxx"
# ❌ "Ignoring non-portfolio room: xxx" (means wrong room name)
```

### Test Webhook Manually

The webhook verification will fail without proper JWT signing, but you should see:

```bash
curl -X POST https://voice-ai-agent-435044415111.us-central1.run.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"room_started","room":{"name":"portfolio-voice-test"}}'

# Expected response: 401 Unauthorized (this is correct behavior)
```

## 🎯 Most Likely Issues

### 1. Webhook Not Configured
**Symptom**: Agent never joins rooms
**Solution**: Configure webhook in LiveKit console (see step 1 above)

### 2. Wrong Room Names
**Symptom**: Agent joins some rooms but not others
**Solution**: Ensure all room names start with `portfolio-voice-`

### 3. Frontend Not Connected to Deployment
**Symptom**: Frontend works but agent doesn't appear
**Solution**: Verify frontend is using the correct deployment URL for token generation

## 🔄 Testing the Full Flow

1. **Create a test room**: Use room name `portfolio-voice-test-123`
2. **Generate token**: Call the `/generate-token` endpoint
3. **Connect to room**: Use LiveKit client SDK to join
4. **Check LiveKit console**: Agent should appear as a participant
5. **Test voice**: Speak into microphone, agent should respond

## 📞 Next Steps

If the agent is still not responding after configuring the webhook:

1. Check browser microphone permissions
2. Verify audio input/output devices are working
3. Check LiveKit console for room participants
4. Review Google Cloud Run logs for errors
5. Test with a simple "Hello" message to verify the agent responds

Your deployment is working correctly - the main requirement now is proper webhook configuration in the LiveKit console!

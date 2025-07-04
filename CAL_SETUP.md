# Cal.com Integration Setup

This guide will help you set up Cal.com integration so your voice AI can book meetings with leads.

## Prerequisites

1. A Cal.com account (sign up at https://cal.com)
2. At least one event type configured (e.g., "30 min consultation")

## Setup Steps

### 1. Get Cal.com API Key

1. Go to https://app.cal.com/settings/developer/api-keys
2. Click "Create API Key"
3. Give it a name like "Portfolio Voice AI"
4. Copy the API key

### 2. Get Event Type ID

1. Go to your Cal.com dashboard
2. Navigate to Event Types
3. Find your consultation/meeting event type
4. The Event Type ID is in the URL or you can get it via API:
   ```bash
   curl -X GET "https://api.cal.com/v1/event-types" \
   -H "Authorization: Bearer YOUR_API_KEY"
   ```

### 3. Configure Environment Variables

Add these to your `.env` file:

```bash
# Cal.com Integration
CAL_COM_API_KEY=your_actual_api_key_here
CAL_COM_EVENT_TYPE_ID=your_event_type_id_here
```

### 4. Test the Integration

Start your voice AI agent and try saying:
- "I'd like to schedule a meeting"
- "Can we book a consultation call?"
- "I want to hire you for a project"

## Features

### What the Voice AI Can Do:

✅ **Detect booking intent** - Recognizes when someone wants to schedule a meeting
✅ **Show available times** - Fetches and announces your available slots
✅ **Collect contact info** - Gets name and email via voice
✅ **Guide booking process** - Walks users through scheduling step by step
✅ **Fallback to website** - Directs to direct booking link when needed

### Voice Commands That Work:

- "Book a meeting"
- "Schedule a call" 
- "I want to hire you"
- "Let's work together"
- "Can we talk about a project"
- "Set up a consultation"

## Booking Flow

1. **Intent Detection**: AI recognizes booking request
2. **Show Times**: Announces available time slots
3. **Collect Info**: Gets visitor's name and email
4. **Confirm Details**: Repeats back information
5. **Complete Booking**: Either books directly or provides website link

## Advanced Configuration

### Custom Event Types

You can create different event types for different purposes:
- Quick consultation (15 min)
- Project discussion (45 min)
- Technical interview (60 min)

Update the `CAL_COM_EVENT_TYPE_ID` to match your preferred default.

### Time Zone Handling

The current setup uses UTC. You can modify `cal_integration.py` to:
- Detect user's timezone
- Convert times for their local timezone
- Ask for their preferred timezone

### Enhanced Contact Collection

You can extend the contact collection to gather:
- Phone numbers
- Company information
- Project details
- Budget range

## Troubleshooting

### Common Issues:

1. **"No available slots"**
   - Check your Cal.com availability settings
   - Ensure your event type is active
   - Verify API key permissions

2. **API errors**
   - Confirm API key is correct
   - Check event type ID is valid
   - Ensure Cal.com account is active

3. **Voice not recognizing booking intent**
   - Try different phrasing
   - Check the `booking_keywords` in `cal_integration.py`
   - Add custom keywords for your use case

### Testing the API Directly:

```bash
# Test API connection
curl -X GET "https://api.cal.com/v1/me" \
-H "Authorization: Bearer YOUR_API_KEY"

# Test available slots
curl -X GET "https://api.cal.com/v1/slots?eventTypeId=YOUR_EVENT_TYPE_ID" \
-H "Authorization: Bearer YOUR_API_KEY"
```

## Next Steps

Once set up, your voice AI will be able to:
- Automatically detect when visitors want to schedule meetings
- Handle the entire booking flow via voice
- Convert more website visitors into qualified leads
- Provide a seamless experience from conversation to booking

This creates a powerful lead generation tool where interested visitors can immediately book time with you without leaving the voice conversation!

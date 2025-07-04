# Deploying Portfolio Voice AI to Heroku

This guide walks you through deploying the Voice AI assistant to Heroku.

## Prerequisites

1. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
2. Heroku account (free tier works for testing)
3. Git installed and configured
4. All required API keys (Deepgram, OpenAI, Cartesia, LiveKit)

## Deployment Steps

### 1. Create a New Heroku App

```bash
# Login to Heroku
heroku login

# Create a new app (replace 'your-app-name' with your desired name)
heroku create your-portfolio-voice-ai
```

### 2. Set Environment Variables

```bash
# Set all required API keys
heroku config:set DEEPGRAM_API_KEY=your_deepgram_api_key
heroku config:set OPENAI_API_KEY=your_openai_api_key
heroku config:set CARTESIA_API_KEY=your_cartesia_api_key
heroku config:set LIVEKIT_API_KEY=your_livekit_api_key
heroku config:set LIVEKIT_API_SECRET=your_livekit_api_secret
heroku config:set LIVEKIT_URL=wss://your-instance.livekit.cloud

# Optional: Cal.com integration
heroku config:set CAL_API_KEY=your_cal_api_key
heroku config:set CAL_EVENT_TYPE_ID=your_event_type_id
```

### 3. Deploy the Application

```bash
# Add Heroku remote if not already added
heroku git:remote -a your-portfolio-voice-ai

# Deploy to Heroku
git add .
git commit -m "Deploy voice AI assistant to Heroku"
git push heroku main
```

### 4. Scale the Worker Dyno

```bash
# Start the worker dyno
heroku ps:scale worker=1

# Verify it's running
heroku ps
```

### 5. Check Logs

```bash
# View real-time logs
heroku logs --tail

# View worker logs specifically
heroku logs --tail --dyno=worker
```

## Monitoring and Debugging

### View Application Status
```bash
heroku ps
```

### Restart the Application
```bash
heroku restart
```

### Check Environment Variables
```bash
heroku config
```

### Access Heroku Dashboard
Visit https://dashboard.heroku.com to manage your app through the web interface.

## Cost Considerations

- **Eco Dyno**: $5/month (recommended for production)
- **Basic Dyno**: $7/month (if you need more resources)
- **Free Tier**: Limited hours, app sleeps after 30 mins of inactivity

## Troubleshooting

### Worker Not Starting
- Check logs: `heroku logs --tail`
- Verify Procfile is correct
- Ensure all environment variables are set

### Connection Issues
- Verify LIVEKIT_URL is correct
- Check API keys are valid
- Ensure LiveKit server is accessible

### Memory Issues
If you encounter memory issues, you may need to upgrade to a larger dyno:
```bash
heroku ps:scale worker=1:basic
```

## Production Tips

1. **Enable Heroku Metrics**: Monitor performance and resource usage
2. **Set up Error Tracking**: Use Sentry or similar service
3. **Configure Alerts**: Set up alerts for dyno crashes
4. **Use Environment-Specific Config**: Different settings for staging/production

## Next Steps

After successful deployment:
1. Test the voice AI through your portfolio frontend
2. Monitor logs for any issues
3. Set up continuous deployment with GitHub integration
4. Configure custom domain if needed

## Support

- [Heroku Documentation](https://devcenter.heroku.com/)
- [LiveKit Documentation](https://docs.livekit.io/)
- Check the main README.md for voice AI specific issues

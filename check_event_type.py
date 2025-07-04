#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('CAL_COM_API_KEY')
EVENT_TYPE_ID = os.getenv('CAL_COM_EVENT_TYPE_ID')
BASE_URL = 'https://api.cal.com/v1'

async def check_event_type():
    print("Checking Cal.com event type details...")
    print(f"Event Type ID: {EVENT_TYPE_ID}")
    
    params = {'apiKey': API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get event type details
            async with session.get(f"{BASE_URL}/event-types/{EVENT_TYPE_ID}", params=params) as response:
                print(f"Event Type Status: {response.status}")
                data = await response.json()
                print(f"Event Type Response: {json.dumps(data, indent=2)}")
                
            # Also check all event types
            async with session.get(f"{BASE_URL}/event-types", params=params) as response:
                print(f"\nAll Event Types Status: {response.status}")
                all_types = await response.json()
                print(f"All Event Types: {json.dumps(all_types, indent=2)}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_event_type())

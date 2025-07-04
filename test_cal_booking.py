#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('CAL_COM_API_KEY')
EVENT_TYPE_ID = os.getenv('CAL_COM_EVENT_TYPE_ID')
BASE_URL = 'https://api.cal.com/v1'

async def test_cal_api():
    print("Testing Cal.com API integration...")
    print(f"API Key: {API_KEY[:20]}..." if API_KEY else "No API Key found")
    print(f"Event Type ID: {EVENT_TYPE_ID}")
    
    # Test 1: Get available slots
    print("\n=== Testing Available Slots ===")
    date_from = datetime.now().strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    start_time = f"{date_from}T00:00:00.000Z"
    end_time = f"{date_to}T23:59:59.999Z"
    
    params = {
        'apiKey': API_KEY,
        'eventTypeId': EVENT_TYPE_ID,
        'startTime': start_time,
        'endTime': end_time
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/slots", params=params) as response:
                print(f"Status: {response.status}")
                data = await response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status == 200:
                    slots_by_date = data.get('slots', {})
                    all_slots = []
                    for date, time_slots in slots_by_date.items():
                        for slot in time_slots:
                            all_slots.append(slot.get('time'))
                    print(f"Available slots: {all_slots[:5]}")  # First 5 slots
                    
                    # Test 2: Try to create a booking if we have slots
                    if all_slots:
                        print("\n=== Testing Booking Creation ===")
                        # Calculate end time
                        start_dt = datetime.fromisoformat(all_slots[0].replace('Z', '+00:00'))
                        end_dt = start_dt + timedelta(minutes=30)
                        end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                        
                        test_booking_data = {
                            'eventTypeId': int(EVENT_TYPE_ID),
                            'start': all_slots[0],
                            'end': end_time,
                            'responses': {
                                'name': 'Test User',
                                'email': 'test@example.com',
                                'notes': 'Test booking from voice AI'
                            },
                            'timeZone': 'UTC',
                            'language': 'en',
                            'metadata': {}
                        }
                        
                        # Use query parameter for API key
                        booking_params = {'apiKey': API_KEY}
                        
                        async with session.post(f"{BASE_URL}/bookings", json=test_booking_data, params=booking_params) as booking_response:
                            print(f"Booking Status: {booking_response.status}")
                            booking_result = await booking_response.json()
                            print(f"Booking Response: {json.dumps(booking_result, indent=2)}")
                    else:
                        print("No available slots to test booking creation")
                else:
                    print("Failed to get available slots")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_cal_api())

#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Your API key
api_key = "cal_live_53df1c452a7a7aa8722ad377803fda55"
base_url = "https://api.cal.com/v1"

def test_api_connection():
    """Test basic API connection"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Testing Cal.com API connection...")
    
    # Test different endpoints to find the right one
    endpoints_to_test = [
        "/me",
        "/event-types", 
        "/users/me",
        "/bookings"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📡 Testing: {base_url}{endpoint}")
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # If this is event-types, show the details
                if "event-types" in endpoint and isinstance(data, dict):
                    if "event_types" in data:
                        print(f"\n🎯 Found Event Types:")
                        for event_type in data["event_types"]:
                            print(f"   📅 {event_type.get('title', 'No title')}")
                            print(f"      ID: {event_type.get('id', 'No ID')}")
                            print(f"      Length: {event_type.get('length', 'No length')} minutes")
                            print(f"      URL: {event_type.get('link', 'No link')}")
                            print()
                    elif "data" in data:
                        print(f"\n🎯 Found Event Types in data:")
                        for event_type in data["data"]:
                            print(f"   📅 {event_type.get('title', 'No title')}")
                            print(f"      ID: {event_type.get('id', 'No ID')}")
                            print(f"      Length: {event_type.get('length', 'No length')} minutes")
                            print()
                    else:
                        print(f"   Full response: {json.dumps(data, indent=2)}")
                        
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized - Check API key")
            elif response.status_code == 404:
                print(f"   ❌ Not found - Endpoint doesn't exist")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
    
    # Try the new Cal.com API v2 format
    print(f"\n🔄 Trying alternative API formats...")
    
    alternative_headers = [
        {"Cal-Api-Version": "2024-08-13", "Authorization": f"Bearer {api_key}"},
        {"X-CAL-SECRET-KEY": api_key},
        {"Authorization": f"Token {api_key}"},
    ]
    
    for i, alt_headers in enumerate(alternative_headers):
        try:
            print(f"\n📡 Testing alternative format #{i+1}")
            response = requests.get(f"{base_url}/event-types", headers=alt_headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Alternative format works!")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_api_connection()

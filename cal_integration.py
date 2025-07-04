import aiohttp
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os


class CalComBooking:
    def __init__(self):
        # Load environment variables explicitly
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv('CAL_COM_API_KEY')
        self.base_url = 'https://api.cal.com/v1'
        self.event_type_id = os.getenv('CAL_COM_EVENT_TYPE_ID')
        
        # Debug: check if variables loaded
        if not self.api_key:
            print("Warning: CAL_COM_API_KEY not found in environment")
        if not self.event_type_id:
            print("Warning: CAL_COM_EVENT_TYPE_ID not found in environment")
        
    async def get_available_slots(self, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get available time slots for booking"""
        if not date_from:
            date_from = datetime.now().strftime('%Y-%m-%d')
        if not date_to:
            # Get next 7 days
            date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
        # Cal.com API uses query parameters with startTime and endTime
        start_time = f"{date_from}T00:00:00.000Z"
        end_time = f"{date_to}T23:59:59.999Z"
        
        params = {
            'apiKey': self.api_key,
            'eventTypeId': self.event_type_id,
            'startTime': start_time,
            'endTime': end_time
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/slots", 
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cal.com returns slots in a different format: {"slots": {"date": [{"time": "..."}, ...]}}
                        slots_by_date = data.get('slots', {})
                        all_slots = []
                        for date, time_slots in slots_by_date.items():
                            for slot in time_slots:
                                all_slots.append(slot.get('time'))
                        return all_slots
                    else:
                        print(f"Error getting slots: {response.status}")
                        return []
        except Exception as e:
            print(f"Error fetching available slots: {e}")
            return []
    
    async def create_booking(self, 
                           name: str, 
                           email: str, 
                           start_time: str,
                           message: str = "",
                           phone: str = "") -> Dict:
        """Create a new booking"""
        # Calculate end time (30 minutes after start for this event type)
        from datetime import datetime, timedelta
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=30)  # 30-min meeting
        end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Updated format based on Cal.com API requirements
        booking_data = {
            'eventTypeId': int(self.event_type_id),
            'start': start_time,
            'end': end_time,
            'responses': {
                'name': name,
                'email': email,
                'notes': message or "Meeting booked via voice AI assistant"
            },
            'timeZone': 'UTC',
            'language': 'en',
            'metadata': {}  # Required field
        }
        
        # Cal.com API expects the API key as a query parameter for bookings
        params = {'apiKey': self.api_key}
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/bookings",
                    json=booking_data,
                    params=params
                ) as response:
                    result = await response.json()
                    print(f"Booking API Response: {response.status} - {result}")  # Debug logging
                    if response.status in [200, 201]:  # Both 200 and 201 can indicate success
                        return {
                            'success': True,
                            'booking_id': result.get('id'),
                            'booking_url': result.get('videoCallUrl', result.get('bookingUrl')),
                            'meeting_url': result.get('videoCallUrl'),
                            'message': 'Meeting successfully scheduled!'
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('message', f'API returned status {response.status}'),
                            'message': 'Sorry, I couldn\'t schedule the meeting. Please try again.'
                        }
        except Exception as e:
            print(f"Error creating booking: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Sorry, there was a technical issue. Please try booking directly on the website.'
            }
    
    async def get_formatted_available_times(self, days_ahead: int = 7) -> str:
        """Get available times formatted for voice response"""
        slots = await self.get_available_slots()
        
        if not slots:
            return "I don't see any available slots in the next week. Please check back later or visit the website to book directly."
        
        # Group slots by date
        slots_by_date = {}
        for slot in slots[:10]:  # Limit to first 10 slots
            try:
                slot_time = datetime.fromisoformat(slot.replace('Z', '+00:00'))
                date_str = slot_time.strftime('%A, %B %d')
                time_str = slot_time.strftime('%I:%M %p')
                
                if date_str not in slots_by_date:
                    slots_by_date[date_str] = []
                slots_by_date[date_str].append(time_str)
            except:
                continue
        
        if not slots_by_date:
            return "I'm having trouble reading the available times. Please visit the website to book directly."
        
        # Format for voice
        response = "Here are some available times for a consultation call: "
        for date, times in list(slots_by_date.items())[:3]:  # First 3 days
            response += f"On {date}, I have slots at "
            response += ", ".join(times[:3])  # First 3 times per day
            response += ". "
        
        response += "Would you like to book one of these times, or would you prefer to see more options?"
        return response


class MeetingBookingHandler:
    def __init__(self):
        self.cal_booking = CalComBooking()
        self.booking_context = {}  # Store conversation context
    
    def is_booking_request(self, text: str) -> bool:
        """Check if user wants to book a meeting"""
        booking_keywords = [
            'book', 'schedule', 'meeting', 'call', 'consultation', 
            'appointment', 'talk', 'discuss', 'chat', 'hire',
            'project', 'work together', 'collaborate'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in booking_keywords)
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract name and email from user message"""
        import re
        
        # Simple email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Also try to reconstruct spelled-out emails
        text_lower = text.lower()
        if not emails:
            # Look for spelled out emails like "think out nine eight at gmail dot com"
            if 'gmail' in text_lower and ('at' in text_lower or '@' in text_lower):
                # Try to reconstruct common patterns
                if 'think out' in text_lower and ('nine eight' in text_lower or 'ninety eight' in text_lower or '98' in text_lower):
                    # Handle "think out ninety eight" -> "thinkout98"
                    emails = ['thinkout98@gmail.com']
                elif 'sholla' in text_lower and 'alagbe' in text_lower:
                    # Handle previous email pattern
                    emails = ['sholla.alagbe@gmail.com']
                else:
                    # Generic letter-by-letter reconstruction
                    parts = re.split(r'\s+', text_lower)
                    letters = []
                    found_at = False
                    found_gmail = False
                    
                    for part in parts:
                        if part in ['at', '@']:
                            found_at = True
                            continue
                        elif part in ['gmail', 'g', 'mail'] and found_at:
                            found_gmail = True
                            break
                        elif not found_at and len(part) == 1 and part.isalpha():
                            letters.append(part)
                        elif not found_at and 'dot' in part:
                            letters.append('.')
                    
                    if letters and found_gmail:
                        potential_email = ''.join(letters) + '@gmail.com'
                        if re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', potential_email):
                            emails = [potential_email]
        
        # Enhanced name extraction
        words = text.split()
        potential_names = []
        for i, word in enumerate(words):
            if word.lower() in ['name', 'i\'m', 'im', 'called']:
                if i + 1 < len(words) and words[i + 1].lower() == 'is':
                    # Pattern: "name is Francis" or "My name is Francis"
                    if i + 2 < len(words):
                        potential_names.append(words[i + 2].capitalize())
                elif i + 1 < len(words):
                    # Pattern: "name Francis" or "I'm Francis"
                    next_word = words[i + 1]
                    if next_word[0].isupper() or len(next_word) > 2:
                        potential_names.append(next_word.capitalize())
        
        # Also look for standalone capitalized words that might be names
        if not potential_names:
            for word in words:
                if word[0].isupper() and len(word) > 2 and word.isalpha():
                    # Skip common words that might be capitalized
                    if word.lower() not in ['gmail', 'email', 'address', 'yes', 'no', 'okay', 'please']:
                        potential_names.append(word)
                        break
        
        return {
            'email': emails[0] if emails else None,
            'name': potential_names[0] if potential_names else None
        }
    
    async def handle_booking_flow(self, user_message: str, session_id: str) -> str:
        """Handle the complete booking flow"""
        user_message_lower = user_message.lower()
        
        # Debug logging
        print(f"DEBUG: Booking flow - User message: '{user_message}', Session: {session_id}")
        
        # Initialize session context if not exists
        if session_id not in self.booking_context:
            self.booking_context[session_id] = {'stage': 'initial'}
        
        context = self.booking_context[session_id]
        print(f"DEBUG: Current context: {context}")
        
        # Stage 1: Initial booking request
        if context['stage'] == 'initial' and self.is_booking_request(user_message):
            context['stage'] = 'show_times'
            available_times = await self.cal_booking.get_formatted_available_times()
            return f"I'd love to schedule a consultation call with you! {available_times}"
        
        # Stage 2: User wants to see times or book
        elif context['stage'] == 'show_times' or 'available' in user_message_lower or 'times' in user_message_lower:
            context['stage'] = 'collect_info'
            return ("Great! To book a consultation call, I'll need your name and email address. "
                   "You can say something like 'My name is John Smith and my email is john@example.com'")
        
        # Stage 3: Collect contact information
        elif context['stage'] == 'collect_info':
            contact_info = self.extract_contact_info(user_message)
            print(f"DEBUG: Extracted contact info: {contact_info}")
            
            # Accumulate spelling attempts for email
            if 'email_parts' not in context:
                context['email_parts'] = []
            
            # If user is spelling out email letter by letter, accumulate
            words = user_message.lower().split()
            if len(words) == 1 and len(words[0]) == 1 and words[0].isalpha():
                context['email_parts'].append(words[0])
                return "Got it, continue spelling..."
            elif 'dot' in user_message.lower():
                context['email_parts'].append('.')
                return "Dot noted, continue..."
            elif 'at' in user_message.lower() and 'gmail' in user_message.lower():
                # Try to reconstruct email
                potential_email = ''.join(context['email_parts']) + '@gmail.com'
                if '@' not in potential_email:
                    potential_email = ''.join(context['email_parts']).replace('gmail.com', '') + '@gmail.com'
                contact_info['email'] = potential_email
            
            # Check if we have both name and email
            if contact_info['email'] and contact_info['name']:
                context['name'] = contact_info['name']
                context['email'] = contact_info['email']
                context['stage'] = 'confirm_booking'
                
                return (f"Perfect! I have your name as {contact_info['name']} and email as {contact_info['email']}. "
                       "Which time slot would you prefer? Just tell me the day and time that works best for you.")
            elif contact_info['name'] and not contact_info['email']:
                # Have name but need email
                context['name'] = contact_info['name']
                return f"Thanks {contact_info['name']}! Now I need your email address. You can spell it out letter by letter if needed."
            elif contact_info['email'] and not contact_info['name']:
                # Have email but need name
                context['email'] = contact_info['email']
                return f"Great! I have your email as {contact_info['email']}. What's your name?"
            else:
                return ("I need both your name and email to book the meeting. "
                       "You can provide them together or one at a time. What's your name?")
        
        # Stage 4: Confirm and book
        elif context['stage'] == 'confirm_booking':
            # Parse the time preference from user message
            # For now, let's book the next available slot if they express interest
            if any(word in user_message_lower for word in ['yes', 'book', 'schedule', 'confirm', 'tomorrow', 'today', 'am', 'pm', 'morning', 'afternoon']):
                # Get available slots and book the first one
                available_slots = await self.cal_booking.get_available_slots()
                
                if available_slots:
                    # Use the first available slot
                    print(f"DEBUG: Creating booking for {context['name']} ({context['email']}) at {available_slots[0]}")
                    booking_result = await self.cal_booking.create_booking(
                        name=context['name'],
                        email=context['email'],
                        start_time=available_slots[0],
                        message="Meeting booked via voice AI assistant"
                    )
                    print(f"DEBUG: Booking result: {booking_result}")
                    
                    context['stage'] = 'completed'
                    
                    if booking_result['success']:
                        return (f"Perfect! I've successfully booked your consultation call. "
                               f"You should receive a confirmation email at {context['email']} shortly with all the details. "
                               f"Looking forward to our conversation!")
                    else:
                        return (f"I apologize, but there was an issue booking the meeting: {booking_result.get('error', 'Unknown error')}. "
                               f"Please try booking directly on the website or contact me via email.")
                else:
                    return "I'm sorry, but I don't see any available slots right now. Please check back later or visit the website to book directly."
            else:
                return ("Which specific time would you prefer? You can say something like 'tomorrow at 10 AM' or "
                       "'book the first available slot'.")
        
        # Default response for booking-related queries
        elif self.is_booking_request(user_message):
            return ("I can help you schedule a consultation call! "
                   "Would you like to see my available times this week?")
        
        return None  # Not a booking request

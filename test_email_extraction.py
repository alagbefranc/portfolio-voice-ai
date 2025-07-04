#!/usr/bin/env python3

from cal_integration import MeetingBookingHandler

def test_email_extraction():
    handler = MeetingBookingHandler()
    
    # Test cases based on the conversation log
    test_messages = [
        "my name is Francis",
        "Email address is think",
        "c h I n k out",
        "It's think out ninety eight",
        "At Gmail dot com",
        "So the ninety eight is not is the numbers. So think out ninety eight. Nine eight. At Gmail dot com.",
        "thinkout98@gmail.com",  # Direct format
        "My name is Francis and my email is thinkout98@gmail.com"
    ]
    
    print("Testing email extraction:")
    for msg in test_messages:
        result = handler.extract_contact_info(msg)
        print(f"Message: '{msg}'")
        print(f"  -> Name: {result.get('name')}, Email: {result.get('email')}")
        print()

if __name__ == "__main__":
    test_email_extraction()

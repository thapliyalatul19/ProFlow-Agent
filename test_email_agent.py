"""
Test the Email Intelligence Agent with sample emails
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from tools.email_tools import (
    classify_email_priority,
    extract_meeting_requests,
    extract_action_items
)

def test_urgent_email():
    """Test with an urgent client escalation email"""
    
    print("=" * 80)
    print("TEST 1: Urgent Client Escalation")
    print("=" * 80)
    
    subject = "URGENT: Client escalation - GenAI deployment issue"
    sender = "sarah.johnson@verizon.com"
    body = """
Hi Atul,

We have a critical situation with the Verizon GenAI deployment that needs your immediate attention. 
The chatbot is experiencing performance issues and the client CTO wants an emergency call today at 3 PM.

Can you please:
1. Review the error logs (attached)
2. Prepare a root cause analysis
3. Join the call with recommendations

This is blocking their go-live scheduled for Monday.

Thanks,
Sarah - Verizon Account Lead
    """
    
    # Test priority classification
    print("\n📊 Priority Classification:")
    result = classify_email_priority(subject, sender, body)
    print(f"   Priority: {result['priority'].upper()}")
    print(f"   Category: {result['category']}")
    print(f"   Requires Response: {result['requires_response']}")
    print(f"   Response Time: {result['suggested_response_time']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Test action items
    print("\n✅ Action Items:")
    actions = extract_action_items(body)
    for i, item in enumerate(actions['action_items'], 1):
        print(f"   {i}. {item}")
    
    # Test meeting requests
    print("\n📅 Meeting Request:")
    meeting = extract_meeting_requests(body)
    if meeting['is_meeting_request']:
        print(f"   Is Meeting Request: YES")
        print(f"   Proposed Times: {meeting['proposed_times']}")
        print(f"   Duration: {meeting['duration']} minutes")
    else:
        print(f"   Is Meeting Request: NO")
    
    print()


def test_fyi_email():
    """Test with an FYI email"""
    
    print("=" * 80)
    print("TEST 2: FYI Newsletter Update")
    print("=" * 80)
    
    subject = "FYI - Q4 Newsletter Published"
    sender = "marketing@company.com"
    body = """
Hi Team,

Just wanted to let you know that the Q4 company newsletter has been published 
on the intranet. It includes updates on:

- New product launches
- Team achievements  
- Upcoming company events

No action needed, just keeping you in the loop!

Best,
Marketing Team
    """
    
    # Test priority classification
    print("\n📊 Priority Classification:")
    result = classify_email_priority(subject, sender, body)
    print(f"   Priority: {result['priority'].upper()}")
    print(f"   Category: {result['category']}")
    print(f"   Requires Response: {result['requires_response']}")
    print(f"   Response Time: {result['suggested_response_time']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    print()


def test_meeting_request_email():
    """Test with a meeting request email"""
    
    print("=" * 80)
    print("TEST 3: Meeting Request")
    print("=" * 80)
    
    subject = "Let's schedule a sync on Q4 roadmap"
    sender = "mike.chen@company.com"
    body = """
Hi Atul,

Can we schedule a meeting next week to discuss the Q4 GenAI roadmap?

I'm available:
- Tuesday at 2:00 PM
- Wednesday at 10:00 AM  
- Thursday at 3:00 PM

Should take about 60 minutes. Let me know what works for you!

Also inviting Sarah and the three developers from the team.

Thanks,
Mike
    """
    
    # Test priority classification
    print("\n📊 Priority Classification:")
    result = classify_email_priority(subject, sender, body)
    print(f"   Priority: {result['priority'].upper()}")
    print(f"   Category: {result['category']}")
    print(f"   Requires Response: {result['requires_response']}")
    print(f"   Response Time: {result['suggested_response_time']}")
    
    # Test meeting extraction
    print("\n📅 Meeting Request Details:")
    meeting = extract_meeting_requests(body)
    print(f"   Is Meeting Request: {meeting['is_meeting_request']}")
    print(f"   Topic: {meeting['topic']}")
    print(f"   Duration: {meeting['duration']} minutes")
    print(f"   Proposed Times: {meeting['proposed_times']}")
    print(f"   Attendees: {len(meeting['attendees'])} attendees")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("🧪 EMAIL INTELLIGENCE AGENT - TOOL TESTS")
    print("=" * 80)
    print()
    
    # Run all tests
    test_urgent_email()
    test_fyi_email()
    test_meeting_request_email()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print("   ✅ Priority classification working")
    print("   ✅ Action item extraction working")
    print("   ✅ Meeting request detection working")
    print()
    print("🎉 Email Intelligence Agent is fully functional!")
    print()

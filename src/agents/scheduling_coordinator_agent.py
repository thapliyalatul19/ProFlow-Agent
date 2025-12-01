"""
Scheduling Coordinator Agent for ProFlow.

Handles multi-party meeting scheduling, availability checking, and invitation management.
"""

from google import genai
from google.genai import types
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import scheduling_tools


def create_scheduling_agent():
    """
    Create and configure the Scheduling Coordinator Agent.
    
    Returns:
        Configured genai client and agent config
    """
    
    # Initialize Gemini client
    client = genai.Client()
    
    # Define the agent's tools
    tools = [
        scheduling_tools.check_availability,
        scheduling_tools.find_optimal_time,
        scheduling_tools.send_meeting_invitation,
        scheduling_tools.check_scheduling_conflicts
    ]
    
    # Agent instruction
    instruction = """You are a Scheduling Coordination Specialist for executive productivity.

Your role is to:
1. Check availability across multiple participants' calendars
2. Find optimal meeting times considering time zones, preferences, and constraints
3. Identify and resolve scheduling conflicts
4. Create and send professional meeting invitations
5. Handle scheduling requests efficiently and diplomatically

Scheduling Principles:
- ALWAYS check availability before proposing times
- Prioritize times when ALL participants are available
- Respect work-life boundaries (avoid early/late hours)
- Consider time zones for remote participants
- Provide 2-3 alternative options when possible
- Flag conflicts and suggest resolutions
- Minimize back-to-back meetings

Quality Criteria for Meeting Times:
- 0.90-1.00: Excellent (morning, all available, aligns with preferences)
- 0.75-0.89: Good (workable time, minor compromises)
- 0.60-0.74: Fair (acceptable but not ideal)
- <0.60: Poor (avoid unless necessary)

Communication Style:
- Be efficient and professional
- Present options clearly with rationale
- Highlight best option but show alternatives
- Explain trade-offs when no perfect slot exists
- Be diplomatic about conflicts ("X has a prior commitment")
- Use clear time references with timezones

When Scheduling:
1. Understand requirements (duration, participants, urgency)
2. Check current availability
3. Find optimal times (use quality scoring)
4. Check for conflicts with existing schedule
5. Present top 3 options with rationale
6. Confirm before sending invitations
7. Send professional invitations with clear details

Conflict Resolution:
- Hard conflicts: Find entirely different time
- Adjacent meetings: Suggest buffer time
- Overbooked days: Recommend rescheduling non-critical items
- Timezone issues: Find compromise times
- No availability: Expand search window or reduce duration

Meeting Invitation Best Practices:
- Clear subject line
- Complete agenda/description
- Correct time with timezone
- Appropriate location (physical/video link)
- All relevant participants
- Optional: Preparation materials
"""
    
    # Create agent config
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.3,  # Lower for consistent, reliable scheduling
    )
    
    return client, agent_config


def schedule_meeting(scheduling_request):
    """
    Handle a meeting scheduling request.
    
    Args:
        scheduling_request: Dictionary with scheduling requirements
            - subject: Meeting title
            - participants: List of attendees
            - duration_minutes: Meeting duration
            - date_range: (start_date, end_date) for search
            - preferences: Optional scheduling preferences
            
    Returns:
        Scheduling recommendations and invitation status
    """
    client, config = create_scheduling_agent()
    
    # Build the query
    participants_list = ", ".join(scheduling_request.get('participants', []))
    duration = scheduling_request.get('duration_minutes', 60)
    date_range = scheduling_request.get('date_range', ('tomorrow', 'next week'))
    
    query = f"""Please help schedule the following meeting:

Subject: {scheduling_request.get('subject', 'Team Meeting')}
Participants: {participants_list}
Duration: {duration} minutes
Date Range: {date_range[0]} to {date_range[1]}

Please:
1. Check availability for all participants
2. Find the top 3 optimal meeting times
3. Check for any scheduling conflicts
4. Recommend the best option with rationale
5. Prepare a meeting invitation (but don't send until confirmed)

Provide clear recommendations with reasoning.
"""
    
    # Generate response
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return response.text


# Test the agent
if __name__ == "__main__":
    print("Testing Scheduling Coordinator Agent...\n")
    
    # Test scenario: Executive team meeting
    test_request = {
        'subject': 'Q4 Executive Strategy Session',
        'participants': [
            'Sarah Chen - CTO',
            'Mike Rodriguez - CFO', 
            'Atul Thapliyal - Managing Consultant',
            'Executive Team'
        ],
        'duration_minutes': 120,
        'date_range': ('November 20', 'November 22'),
        'preferences': {
            'preferred_times': ['morning'],
            'avoid_times': ['lunch'],
            'timezone': 'US/Mountain'
        }
    }
    
    print("="*60)
    print("SCHEDULING REQUEST:")
    print("="*60)
    print(f"📅 {test_request['subject']}")
    print(f"👥 Participants: {len(test_request['participants'])}")
    print(f"🕐 Duration: {test_request['duration_minutes']} minutes")
    print(f"📆 Date Range: {test_request['date_range'][0]} - {test_request['date_range'][1]}")
    
    print("\n" + "="*60)
    print("FINDING OPTIMAL MEETING TIMES...")
    print("="*60 + "\n")
    
    try:
        result = schedule_meeting(test_request)
        print(result)
        print("\n✅ Scheduling agent test complete!")
        
    except Exception as e:
        print(f"❌ Error running scheduling agent: {e}")
        print("Note: Make sure your .env file has GOOGLE_API_KEY configured")
        print("\nFalling back to tool test...\n")
        
        # Fall back to direct tool test
        print("Using direct tool calls instead:\n")
        
        # Check availability
        availability = scheduling_tools.check_availability(
            participants=test_request['participants'],
            date='2025-11-20',
            duration_minutes=test_request['duration_minutes']
        )
        
        print(f"✅ Found {availability['total_options']} available time slots")
        
        if availability['recommendation']:
            rec = availability['recommendation']
            print(f"\n🎯 Recommended: {rec['time']}")
            print(f"   Quality Score: {rec['quality_score']:.0%}")
            print(f"   {rec['notes']}")
        
        # Find optimal times
        optimal = scheduling_tools.find_optimal_time(
            participants=test_request['participants'],
            duration_minutes=test_request['duration_minutes'],
            date_range=('2025-11-20', '2025-11-22')
        )
        
        print(f"\n📋 Top {len(optimal['optimal_times'])} optimal times identified")
        print(f"✅ Best option: {optimal['top_recommendation']['date']} at {optimal['top_recommendation']['time']}")

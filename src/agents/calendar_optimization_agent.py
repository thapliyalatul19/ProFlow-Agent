"""
Calendar Optimization Agent for ProFlow.

Analyzes daily schedules, identifies conflicts, and suggests optimizations
to maximize focus time and meeting effectiveness.
"""

from google import genai
from google.genai import types
import sys
import os

# Add parent directory to path so we can import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import calendar_tools


def create_calendar_agent():
    """
    Create and configure the Calendar Optimization Agent.
    
    Returns:
        Configured genai agent for calendar optimization
    """
    
    # Initialize Gemini client
    client = genai.Client()
    
    # Define the agent's tools
    tools = [
        calendar_tools.analyze_schedule,
        calendar_tools.find_available_slots,
        calendar_tools.suggest_meeting_reschedule
    ]
    
    # Agent instruction - this is important for behavior
    instruction = """You are a Calendar Optimization Specialist for executive productivity.

Your role is to:
1. Analyze daily schedules for inefficiencies and conflicts
2. Identify opportunities to maximize focus time for deep work
3. Suggest schedule optimizations that respect energy patterns
4. Find optimal meeting times that minimize context switching
5. Ensure adequate buffers between meetings

Guiding Principles:
- Focus time is sacred - protect blocks of 90+ minutes for deep work
- Back-to-back meetings are draining - recommend 15min buffers minimum
- Group similar meetings together when possible
- Morning is usually best for focus work, afternoon for meetings
- Never schedule more than 3 consecutive meetings
- Be practical - understand that not all meetings can be moved

When analyzing schedules:
- Calculate optimization scores to quantify schedule quality
- Prioritize high-impact suggestions (conflicts > buffers > focus time)
- Provide specific, actionable recommendations
- Consider the executive's workload and energy levels

Communication Style:
- Be direct and concise - executives value efficiency
- Use data to back up suggestions (scores, time calculations)
- Prioritize issues clearly (high/medium/low)
- Provide rationale for recommendations
"""
    
    # Create the agent config
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.3,  # Lower temperature for more consistent analysis
    )
    
    return client, agent_config


def analyze_daily_schedule(calendar_events, user_preferences=None):
    """
    Analyze a day's schedule and provide optimization recommendations.
    
    Args:
        calendar_events: List of calendar events for the day
        user_preferences: Optional user preferences for schedule optimization
        
    Returns:
        Analysis results with optimization suggestions
    """
    client, config = create_calendar_agent()
    
    # Build the query
    events_summary = f"Analyzing {len(calendar_events)} meetings:\n"
    for event in calendar_events:
        events_summary += f"- {event.get('summary')}: {event.get('start')} - {event.get('end')}\n"
    
    query = f"""{events_summary}

Please analyze this schedule and provide:
1. Overall optimization score
2. Key issues (conflicts, buffer problems, focus time)
3. Top 3 actionable recommendations
4. Specific suggestions for schedule improvements
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
    print("Testing Calendar Optimization Agent...\n")
    
    # Sample day - pretty packed schedule
    test_schedule = [
        {
            'summary': 'Team Standup',
            'start': '09:00',
            'end': '09:30',
            'duration_minutes': 30
        },
        {
            'summary': 'Client Call - Verizon',
            'start': '09:30',  
            'end': '11:00',
            'duration_minutes': 90
        },
        {
            'summary': 'Internal Strategy Review',
            'start': '11:00',  
            'end': '12:00',
            'duration_minutes': 60
        },
        {
            'summary': 'Lunch',
            'start': '12:00',
            'end': '13:00',
            'duration_minutes': 60
        },
        {
            'summary': '1:1 with Manager',
            'start': '14:00',
            'end': '15:00',
            'duration_minutes': 60
        },
        {
            'summary': 'Project Review',
            'start': '15:00',
            'end': '16:30',
            'duration_minutes': 90
        },
        {
            'summary': 'Team Sync',
            'start': '16:30',
            'end': '17:00',
            'duration_minutes': 30
        }
    ]
    
    print("📅 Today's Schedule:")
    for event in test_schedule:
        print(f"  {event['start']} - {event['end']}: {event['summary']}")
    
    print("\n" + "="*60)
    print("Running Calendar Optimization Agent...")
    print("="*60 + "\n")
    
    try:
        result = analyze_daily_schedule(test_schedule)
        print(result)
        print("\n✅ Calendar agent test complete!")
        
    except Exception as e:
        print(f"❌ Error running calendar agent: {e}")
        print("Note: Make sure your .env file has GOOGLE_API_KEY configured")

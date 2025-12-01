"""
Calendar agent - finds conflicts and protects focus time
Still needs timezone handling but works for single location
"""

from google import genai
from google.genai import types
import sys
import os

# hack to import tools from parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import calendar_tools


def create_calendar_agent():
    """Setup calendar agent"""
    
    client = genai.Client()
    
    tools = [
        calendar_tools.analyze_schedule,
        calendar_tools.find_available_slots,
        calendar_tools.suggest_meeting_reschedule
    ]
    
    # keeping this shorter - the long version was overkill
    instruction = """You optimize executive calendars.

Key goals:
- Protect 90+ min blocks for deep work (mornings preferred)
- Add 15min buffers between meetings
- Avoid 3+ back-to-back meetings
- Group similar meetings when possible

When analyzing:
- Score schedule quality (0-10)
- Flag conflicts and problems
- Give 3 specific fixes
- Be practical about what can actually move

Keep recommendations short and actionable.
"""
    
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.3,  # consistent results
    )
    
    return client, agent_config


def analyze_daily_schedule(calendar_events, user_preferences=None):
    """
    Check schedule for problems and suggest fixes
    
    Args:
        calendar_events: List of meetings
        user_preferences: Optional prefs (not used yet)
        
    Returns:
        Analysis text with suggestions
    """
    client, config = create_calendar_agent()
    
    # format the events
    events_summary = f"Analyzing {len(calendar_events)} meetings:\n"
    for event in calendar_events:
        events_summary += f"- {event.get('summary')}: {event.get('start')} - {event.get('end')}\n"
    
    query = f"""{events_summary}

Analyze and provide:
1. Schedule score (0-10)
2. Main problems
3. Top 3 fixes
4. Specific rescheduling suggestions
"""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return response.text


if __name__ == "__main__":
    print("Calendar Agent Test")
    print("-" * 40)
    
    # typical packed day
    test_schedule = [
        {'summary': 'Standup', 'start': '09:00', 'end': '09:30'},
        {'summary': 'Client Call', 'start': '09:30', 'end': '11:00'},
        {'summary': 'Strategy Review', 'start': '11:00', 'end': '12:00'},
        {'summary': 'Lunch', 'start': '12:00', 'end': '13:00'},
        {'summary': '1:1', 'start': '14:00', 'end': '15:00'},
        {'summary': 'Project Review', 'start': '15:00', 'end': '16:30'},
        {'summary': 'Team Sync', 'start': '16:30', 'end': '17:00'}
    ]
    
    print("Today:")
    for event in test_schedule:
        print(f"  {event['start']}: {event['summary']}")
    
    print("\nAnalyzing...")
    print("-" * 40)
    
    try:
        result = analyze_daily_schedule(test_schedule)
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Check .env for GOOGLE_API_KEY")

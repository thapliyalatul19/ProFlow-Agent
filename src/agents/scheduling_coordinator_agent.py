"""
Scheduling agent - finds meeting times that work for everyone
Still need to add timezone handling properly
"""

from google import genai
from google.genai import types
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import scheduling_tools


def create_scheduling_agent():
    """Setup scheduling agent"""
    
    client = genai.Client()
    
    tools = [
        scheduling_tools.check_availability,
        scheduling_tools.find_optimal_time,
        scheduling_tools.send_meeting_invitation,
        scheduling_tools.check_scheduling_conflicts
    ]
    
    instruction = """You coordinate meeting schedules.

Process:
1. Check everyone's availability
2. Find times that work (quality score 0-1)
3. Check for conflicts
4. Send invites

Good times (0.75+): Morning, everyone free
OK times (0.6-0.74): Some compromises
Bad times (<0.6): Avoid unless urgent

Rules:
- No early/late meetings (before 9am, after 6pm)
- Give 2-3 options
- Flag conflicts
- 15min buffer between meetings preferred

Keep it simple and clear.
"""
    
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.2,  # consistent scheduling
    )
    
    return client, agent_config


def find_meeting_time(
    participants,
    duration_minutes=60,
    preferred_times=None,
    urgency="normal"
):
    """
    Find a meeting time that works
    
    Args:
        participants: List of emails
        duration_minutes: Meeting length
        preferred_times: Optional preferences
        urgency: normal/high/low
        
    Returns:
        Top 3 time slots with scores
    """
    
    client, config = create_scheduling_agent()
    
    participants_list = ", ".join(participants)
    
    query = f"""Find meeting time for:
    Participants: {participants_list}
    Duration: {duration_minutes} minutes
    Urgency: {urgency}
    """
    
    if preferred_times:
        query += f"Preferences: {preferred_times}\n"
    
    query += """
    Steps:
    1. Check availability for all
    2. Find 3 best slots
    3. Score each (0-1)
    4. Check conflicts
    5. Rank by quality
    
    Return top 3 with reasoning.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return response.text


def reschedule_meeting(
    meeting_id,
    reason="conflict",
    new_constraints=None
):
    """
    Reschedule existing meeting
    
    Handles conflicts or changes
    """
    
    client, config = create_scheduling_agent()
    
    query = f"""Reschedule meeting {meeting_id}
    Reason: {reason}
    """
    
    if new_constraints:
        query += f"New constraints: {new_constraints}\n"
    
    query += """
    1. Check original details
    2. Find new times
    3. Notify participants
    4. Update calendar
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return response.text


def handle_scheduling_conflict(conflicts_list):
    """
    Resolve scheduling conflicts
    
    Prioritize by importance
    """
    
    client, config = create_scheduling_agent()
    
    conflicts_summary = "Conflicts found:\n"
    for conflict in conflicts_list:
        conflicts_summary += f"- {conflict}\n"
    
    query = f"""{conflicts_summary}
    
    Resolve by:
    1. Identify priority meeting
    2. Find alternatives for others
    3. Suggest resolution
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return response.text


def batch_schedule_meetings(meeting_requests):
    """
    Schedule multiple meetings efficiently
    
    Optimize for minimal fragmentation
    """
    
    if not meeting_requests:
        return {"status": "no meetings to schedule"}
    
    client, config = create_scheduling_agent()
    
    requests_summary = f"Schedule {len(meeting_requests)} meetings:\n"
    for i, req in enumerate(meeting_requests, 1):
        requests_summary += f"{i}. {req.get('subject', 'Meeting')}"
        requests_summary += f" ({req.get('duration', 60)}min)\n"
        requests_summary += f"   With: {req.get('participants', 'TBD')}\n"
    
    query = f"""{requests_summary}
    
    Optimize for:
    1. Minimal calendar fragmentation
    2. Group similar meetings
    3. Protect focus time
    4. Avoid back-to-back
    
    Schedule all efficiently.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=query,
        config=config
    )
    
    return {
        "scheduled_count": len(meeting_requests),
        "scheduling_plan": response.text
    }


if __name__ == "__main__":
    print("Scheduling Agent Test")
    print("-" * 40)
    
    # test scheduling
    test_participants = [
        "john.doe@example.com",
        "jane.smith@example.com",
        "bob.wilson@example.com"
    ]
    
    print(f"Finding time for: {', '.join(test_participants)}")
    print("Duration: 60 minutes\n")
    
    try:
        result = find_meeting_time(
            participants=test_participants,
            duration_minutes=60,
            urgency="normal"
        )
        print("Available slots:")
        print(result)
        
        # test conflict resolution
        test_conflicts = [
            "9am slot: John has client call",
            "2pm slot: Jane in another meeting",
            "4pm slot: Bob out of office"
        ]
        
        print("\nConflict resolution test:")
        print("-" * 40)
        resolution = handle_scheduling_conflict(test_conflicts)
        print(resolution)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Check .env for GOOGLE_API_KEY")

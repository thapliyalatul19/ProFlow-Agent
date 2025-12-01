"""
Meeting prep - pulls context from past meetings and participant info
The participant research is still mostly fake until we wire up LinkedIn
"""

from google import genai
from google.genai import types
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import meeting_prep_tools


def create_meeting_prep_agent():
    """Setup meeting prep agent"""
    
    client = genai.Client()
    
    tools = [
        meeting_prep_tools.search_past_meetings,
        meeting_prep_tools.research_participants,
        meeting_prep_tools.generate_meeting_briefing
    ]
    
    instruction = """You prep executives for meetings. Make it fast and useful.

What to do:
1. Search past meetings for context
2. Research participants (roles, styles)
3. Generate briefing with key points

Briefing format:
- Summary (2-3 lines max)
- Objective (what are we deciding)
- Participants (who matters, what they want)
- History (past decisions, open items)
- Talking points (3-5 specific things)
- Prep tasks (what to do before)
- Quality score (how good is this briefing)

Keep it under 600 words. Be specific, not generic.
First meetings: focus on intros
Decision meetings: have data ready
Client meetings: know the account
Team meetings: know blockers

Flag sensitive stuff. No fluff.
"""
    
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.5,
        top_p=0.9,
        top_k=40,
    )
    
    return client, agent_config


def prepare_meeting_briefing(
    meeting_details: Dict,
    include_detailed_history: bool = True,
    research_participants_deeply: bool = True
) -> str:
    """
    Generate briefing for upcoming meeting
    
    Args:
        meeting_details: Dict with subject, date, duration, attendees, etc
        include_detailed_history: Search back 90 days vs 30
        research_participants_deeply: Deep dive on participants (not really working yet)
            
    Returns:
        Briefing text
    """
    client, config = create_meeting_prep_agent()
    
    subject = meeting_details.get('subject', 'Untitled')
    date = meeting_details.get('date', 'TBD')
    duration = meeting_details.get('duration_minutes', 60)
    attendees = meeting_details.get('attendees', [])
    description = meeting_details.get('description', '')
    location = meeting_details.get('location', 'Not specified')
    
    attendees_list = ", ".join(attendees)
    
    query = f"""Prepare briefing for:

Meeting: {subject}
Date: {date}
Duration: {duration} min
Attendees: {attendees_list}
Location: {location}
"""
    
    if description:
        query += f"Description: {description}\n"
    
    query += f"""
Steps:
1. Search past meetings (last {'90' if include_detailed_history else '30'} days)
2. Research participants
3. Generate briefing with:
   - Summary
   - Objective
   - Participants (with context)
   - History
   - Open items
   - Talking points
   - Prep checklist
   - Quality score

Make it actionable.
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=query,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        print(f"Agent failed: {e}")
        return _generate_briefing_fallback(meeting_details)


def _generate_briefing_fallback(meeting_details: Dict) -> str:
    """Direct tool usage if agent fails"""
    
    # call tools directly
    past_meetings = meeting_prep_tools.search_past_meetings(
        meeting_subject=meeting_details.get('subject', ''),
        participants=meeting_details.get('attendees', [])
    )
    
    participant_info = meeting_prep_tools.research_participants(
        participants=meeting_details.get('attendees', [])
    )
    
    briefing = meeting_prep_tools.generate_meeting_briefing(
        meeting_details=meeting_details,
        past_meetings=past_meetings,
        participant_info=participant_info
    )
    
    # format output
    output = f"""# {briefing['meeting_title']}

**Date**: {briefing['meeting_date']} ({briefing['duration']})
**Attendees**: {briefing['attendees_count']}

## Summary
{briefing['executive_summary']}

## Objective
{briefing['meeting_objective']}

## Participants
"""
    
    for p in briefing['key_participants']:
        output += f"\n**{p['name']}** - {p['title']}\n"
        output += f"- Role: {p['role']}\n"
        output += f"- Note: {p['prep_note']}\n"
    
    output += "\n## History\n"
    for h in briefing['relevant_history']:
        output += f"\n**{h['date']}**: {h['summary']}\n"
        if h['key_decisions']:
            output += "- Decisions: " + "; ".join(h['key_decisions']) + "\n"
    
    if briefing['open_action_items']:
        output += "\n## Open Items\n"
        for item in briefing['open_action_items']:
            output += f"- {item}\n"
    
    output += "\n## Talking Points\n"
    for i, point in enumerate(briefing['suggested_talking_points'], 1):
        output += f"{i}. {point}\n"
    
    output += "\n## Prep Checklist\n"
    for i, item in enumerate(briefing['preparation_checklist'], 1):
        output += f"{i}. {item}\n"
    
    output += f"\n**Quality**: {briefing['briefing_quality_score']:.0f}/100\n"
    
    return output


def analyze_meeting_readiness(meeting_details: Dict) -> Dict:
    """
    Check how ready you are for a meeting
    
    Returns readiness score and recommendations
    """
    
    # get context
    past_meetings = meeting_prep_tools.search_past_meetings(
        meeting_subject=meeting_details.get('subject', ''),
        participants=meeting_details.get('attendees', [])
    )
    
    participant_info = meeting_prep_tools.research_participants(
        participants=meeting_details.get('attendees', [])
    )
    
    # score factors
    readiness_score = 0.0
    factors = []
    
    # past meetings (30 pts)
    meetings_found = past_meetings.get('meetings_found', 0)
    if meetings_found > 0:
        history_score = min(meetings_found * 10, 30)
        readiness_score += history_score
        factors.append(f"Past meetings: {meetings_found} (+{history_score})")
    else:
        factors.append("No history (0)")
    
    # participants (25 pts)
    participants_researched = participant_info.get('participants_researched', 0)
    if participants_researched > 0:
        participant_score = min(participants_researched * 8, 25)
        readiness_score += participant_score
        factors.append(f"Participants researched: {participants_researched} (+{participant_score})")
    
    # new people (risk)
    new_participants = participant_info.get('new_participants', [])
    if new_participants:
        risk_score = -min(len(new_participants) * 5, 10)
        readiness_score += risk_score
        factors.append(f"New people: {len(new_participants)} ({risk_score})")
    
    # other factors
    if meeting_details.get('date') != 'TBD':
        readiness_score += 5
        factors.append("Scheduled (+5)")
    
    if meeting_details.get('description'):
        readiness_score += 10
        factors.append("Has agenda (+10)")
    
    attendee_count = len(meeting_details.get('attendees', []))
    if 2 <= attendee_count <= 10:
        readiness_score += 5
        factors.append(f"Good size: {attendee_count} (+5)")
    
    readiness_score = min(max(readiness_score, 0), 100)
    
    # recommendations
    recommendations = []
    if readiness_score < 50:
        recommendations.append("Low readiness - need 30-60 min prep")
    if meetings_found == 0:
        recommendations.append("Check emails for context")
    if new_participants:
        recommendations.append(f"Research {len(new_participants)} new people")
    if readiness_score >= 75:
        recommendations.append("Well prepared - quick review is fine")
    
    return {
        'readiness_score': readiness_score,
        'readiness_level': _get_readiness_level(readiness_score),
        'contributing_factors': factors,
        'recommendations': recommendations,
        'prep_time_estimate': _estimate_prep_time(readiness_score),
        'past_meetings_found': meetings_found,
        'participants_researched': participants_researched,
        'new_participants_count': len(new_participants)
    }


def _get_readiness_level(score: float) -> str:
    if score >= 80:
        return "EXCELLENT"
    elif score >= 65:
        return "GOOD"
    elif score >= 50:
        return "FAIR"
    elif score >= 35:
        return "LOW"
    else:
        return "INSUFFICIENT"


def _estimate_prep_time(score: float) -> str:
    if score >= 80:
        return "10-15 min"
    elif score >= 65:
        return "20-30 min"
    elif score >= 50:
        return "30-45 min"
    else:
        return "45-60 min"


if __name__ == "__main__":
    print("Meeting Prep Agent Test")
    print("-" * 40)
    
    test_meeting = {
        'subject': 'Q4 Planning',
        'date': '2025-11-22',
        'duration_minutes': 90,
        'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Client Team'],
        'description': 'Review Q4 strategy',
        'location': 'Zoom'
    }
    
    print(f"Meeting: {test_meeting['subject']}")
    print(f"When: {test_meeting['date']}")
    print(f"Who: {', '.join(test_meeting['attendees'])}")
    
    print("\nGenerating briefing...")
    print("-" * 40)
    
    try:
        briefing = prepare_meeting_briefing(test_meeting)
        print(briefing)
        
        print("\nReadiness check:")
        readiness = analyze_meeting_readiness(test_meeting)
        print(f"Score: {readiness['readiness_score']:.0f}/100")
        print(f"Level: {readiness['readiness_level']}")
        print(f"Prep time: {readiness['prep_time_estimate']}")
        
    except Exception as e:
        print(f"Error: {e}")

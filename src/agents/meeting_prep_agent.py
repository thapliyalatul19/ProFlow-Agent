"""
Meeting Preparation Agent for ProFlow.

Analyzes past meetings, researches participants, and generates comprehensive
briefings to help executives prepare for upcoming meetings.
"""

from google import genai
from google.genai import types
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import meeting_prep_tools


def create_meeting_prep_agent():
    """
    Create and configure the Meeting Preparation Agent.
    
    Returns:
        Configured genai client and agent config
    """
    
    # Initialize Gemini client
    client = genai.Client()
    
    # Define the agent's tools
    tools = [
        meeting_prep_tools.search_past_meetings,
        meeting_prep_tools.research_participants,
        meeting_prep_tools.generate_meeting_briefing
    ]
    
    # Agent instruction - updated for more sophisticated analysis
    instruction = """You are an Elite Meeting Preparation Specialist for C-suite executives.

Your role is to:
1. Research past meetings with similar subjects or participants
2. Gather context about meeting participants (roles, interests, communication styles)
3. Generate comprehensive but concise meeting briefings
4. Identify relevant history, decisions, and open action items
5. Suggest talking points and preparation strategies
6. Flag potential sensitivities or important context

Briefing Best Practices:
- Keep briefings information-dense but under 600 words
- Prioritize actionable information over generic advice
- Highlight new participants who need introduction
- Surface open action items from previous meetings
- Provide specific preparation recommendations based on participant roles
- Include quality score to indicate briefing completeness
- Flag important context (first meeting, VIP attendee, decision meeting, etc.)

Communication Style:
- Be concise and executive-focused - time is valuable
- Use clear structure: summary, objectives, context, preparation
- Highlight critical information (VIPs, deadlines, decisions needed)
- Provide specific, actionable recommendations
- Use data points when available (meeting history, participant count)
- Professional but warm tone - you're a trusted advisor

Context Priorities:
1. Recent past meetings (last 90 days) - most relevant
2. Key decision makers and their preferences
3. Open action items requiring follow-up
4. New participants needing research/introduction
5. Historical patterns (recurring themes, common blockers)
6. Communication style preferences of key stakeholders

When generating briefings:
- Lead with executive summary (2-3 sentences max)
- State clear meeting objective
- List key participants with role context
- Include relevant history from past meetings
- Highlight open action items that need addressing
- Suggest specific talking points tailored to this meeting
- Provide preparation checklist with time estimates
- Calculate quality score based on available context
- Add strategic notes for sensitive or high-stakes meetings

Special Cases:
- First meetings: Focus on introductions and relationship building
- Decision meetings: Prepare data, options, and recommendation
- Client meetings: Review account history, wins, concerns
- Team meetings: Know current projects, blockers, morale
- Executive meetings: Be crisp, data-driven, solution-oriented
"""
    
    # Create agent config with optimized settings
    agent_config = types.GenerateContentConfig(
        system_instruction=instruction,
        tools=tools,
        temperature=0.5,  # Balanced for creative but reliable briefings
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
    Prepare a comprehensive briefing for an upcoming meeting.
    
    Args:
        meeting_details: Dictionary with meeting information
            - subject: Meeting title/subject
            - date: Meeting date (string or datetime)
            - duration_minutes: Meeting duration
            - attendees: List of attendee names/emails
            - description: Optional meeting description
            - location: Optional meeting location/link
        include_detailed_history: Whether to search deep past history
        research_participants_deeply: Whether to do detailed participant research
            
    Returns:
        Generated briefing text with full context
    """
    client, config = create_meeting_prep_agent()
    
    # Extract meeting details
    subject = meeting_details.get('subject', 'Untitled Meeting')
    date = meeting_details.get('date', 'TBD')
    duration = meeting_details.get('duration_minutes', 60)
    attendees = meeting_details.get('attendees', [])
    description = meeting_details.get('description', '')
    location = meeting_details.get('location', 'Not specified')
    
    attendees_list = ", ".join(attendees)
    
    # Build comprehensive query
    query = f"""Please prepare a comprehensive meeting briefing for:

Meeting: {subject}
Date: {date}
Duration: {duration} minutes
Attendees: {attendees_list}
Location/Link: {location}
"""
    
    if description:
        query += f"Description: {description}\n"
    
    query += f"""
Analysis Instructions:
1. First, search for past meetings with similar subjects or these participants
   - Look back {'90 days' if include_detailed_history else '30 days'}
   - Identify patterns, recurring themes, past decisions
   
2. Then, research the participants to understand:
   - Their roles and decision-making authority
   - Communication preferences and styles
   - Past interactions and relationship context
   - Key interests and priorities
   
3. Generate a complete briefing that includes:
   - Executive Summary (2-3 sentences - what's this meeting about and why it matters)
   - Meeting Objective (clear purpose statement)
   - Key Participants (with role context and preparation notes)
   - Relevant History (past meetings, decisions, context)
   - Open Action Items (anything pending from past meetings)
   - Suggested Talking Points (specific to this meeting's context)
   - Preparation Checklist (what to do before the meeting)
   - Strategic Notes (any sensitivities, special considerations, tips)
   - Quality Score (how complete is the briefing based on available data)

Make this briefing actionable and executive-ready. I need to walk into this meeting fully prepared.
"""
    
    # Generate response with the agent
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=query,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        # Fallback to direct tool usage if agent fails
        print(f"Agent generation failed: {e}")
        print("Falling back to direct tool usage...\n")
        
        return _generate_briefing_fallback(meeting_details)


def _generate_briefing_fallback(meeting_details: Dict) -> str:
    """Fallback briefing generation using tools directly."""
    
    # Use tools directly
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
    
    # Format as text
    output = f"""# {briefing['meeting_title']}

**Date**: {briefing['meeting_date']} ({briefing['duration']})
**Attendees**: {briefing['attendees_count']} participants

## Executive Summary
{briefing['executive_summary']}

## Meeting Objective
{briefing['meeting_objective']}

## Key Participants
"""
    
    for p in briefing['key_participants']:
        output += f"\n**{p['name']}** - {p['title']}\n"
        output += f"- Role: {p['role']}\n"
        output += f"- Prep Note: {p['prep_note']}\n"
    
    output += "\n## Relevant History\n"
    for h in briefing['relevant_history']:
        output += f"\n**{h['date']}**: {h['summary']}\n"
        if h['key_decisions']:
            output += "- Decisions: " + "; ".join(h['key_decisions']) + "\n"
    
    if briefing['open_action_items']:
        output += "\n## Open Action Items\n"
        for item in briefing['open_action_items']:
            output += f"- {item}\n"
    
    output += "\n## Suggested Talking Points\n"
    for i, point in enumerate(briefing['suggested_talking_points'], 1):
        output += f"{i}. {point}\n"
    
    output += "\n## Preparation Checklist\n"
    for i, item in enumerate(briefing['preparation_checklist'], 1):
        output += f"{i}. {item}\n"
    
    output += f"\n**Briefing Quality Score**: {briefing['briefing_quality_score']:.0f}/100\n"
    
    return output


def analyze_meeting_readiness(meeting_details: Dict) -> Dict:
    """
    Analyze how ready you are for a meeting based on available context.
    
    Args:
        meeting_details: Dictionary with meeting information
        
    Returns:
        Readiness assessment with score and recommendations
    """
    
    # Search for context
    past_meetings = meeting_prep_tools.search_past_meetings(
        meeting_subject=meeting_details.get('subject', ''),
        participants=meeting_details.get('attendees', [])
    )
    
    participant_info = meeting_prep_tools.research_participants(
        participants=meeting_details.get('attendees', [])
    )
    
    # Calculate readiness score
    readiness_score = 0.0
    factors = []
    
    # Factor 1: Past meeting history (30 points)
    meetings_found = past_meetings.get('meetings_found', 0)
    if meetings_found > 0:
        history_score = min(meetings_found * 10, 30)
        readiness_score += history_score
        factors.append(f"Past meeting history: {meetings_found} meeting(s) found (+{history_score} points)")
    else:
        factors.append("No past meeting history found (0 points)")
    
    # Factor 2: Participant research (25 points)
    participants_researched = participant_info.get('participants_researched', 0)
    if participants_researched > 0:
        participant_score = min(participants_researched * 8, 25)
        readiness_score += participant_score
        factors.append(f"Participant research: {participants_researched} participant(s) (+{participant_score} points)")
    else:
        factors.append("No participant research available (0 points)")
    
    # Factor 3: New participants (potential risk, -10 to 0 points)
    new_participants = participant_info.get('new_participants', [])
    if new_participants:
        risk_score = -min(len(new_participants) * 5, 10)
        readiness_score += risk_score
        factors.append(f"New participants: {len(new_participants)} ({risk_score} points - need extra prep)")
    
    # Factor 4: Meeting timing (5 points if not TBD)
    if meeting_details.get('date') and meeting_details.get('date') != 'TBD':
        readiness_score += 5
        factors.append("Meeting scheduled (+5 points)")
    
    # Factor 5: Clear agenda/description (10 points)
    if meeting_details.get('description') or meeting_details.get('subject'):
        readiness_score += 10
        factors.append("Clear meeting purpose (+10 points)")
    
    # Factor 6: Reasonable attendee count (5 points if < 10)
    attendee_count = len(meeting_details.get('attendees', []))
    if 2 <= attendee_count <= 10:
        readiness_score += 5
        factors.append(f"Manageable attendee count: {attendee_count} (+5 points)")
    elif attendee_count > 10:
        factors.append(f"Large meeting: {attendee_count} attendees (needs extra coordination)")
    
    # Normalize to 0-100
    readiness_score = min(max(readiness_score, 0), 100)
    
    # Generate recommendations
    recommendations = []
    if readiness_score < 50:
        recommendations.append("⚠️ LOW READINESS - Significant preparation needed")
        recommendations.append("Schedule 30-60 minutes for meeting prep")
    if meetings_found == 0:
        recommendations.append("Research past context manually - check emails, docs")
    if new_participants:
        recommendations.append(f"Research {len(new_participants)} new participant(s) on LinkedIn")
    if attendee_count > 10:
        recommendations.append("Consider pre-meeting with key stakeholders")
    if not meeting_details.get('description'):
        recommendations.append("Request agenda from meeting organizer")
    if readiness_score >= 75:
        recommendations.append("✅ WELL PREPARED - Quick review should be sufficient")
    
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
    """Convert readiness score to level."""
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
    """Estimate preparation time needed."""
    if score >= 80:
        return "10-15 minutes (quick review)"
    elif score >= 65:
        return "20-30 minutes (moderate prep)"
    elif score >= 50:
        return "30-45 minutes (standard prep)"
    else:
        return "45-60 minutes (extensive prep needed)"


# Test the agent
if __name__ == "__main__":
    print("Testing Meeting Preparation Agent...\n")
    
    # Test scenario 1: Important client meeting
    test_meeting = {
        'subject': 'Client Strategy Review - Q4 Planning',
        'date': '2025-11-22',
        'duration_minutes': 90,
        'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Atul Thapliyal', 'Client Team'],
        'description': 'Review Q4 strategy and plan for 2026 initiatives',
        'location': 'Zoom: https://zoom.us/j/123456'
    }
    
    print("="*70)
    print("TEST 1: FULL MEETING BRIEFING")
    print("="*70)
    print(f"📅 {test_meeting['subject']}")
    print(f"🕐 {test_meeting['date']} ({test_meeting['duration_minutes']} min)")
    print(f"👥 Attendees: {', '.join(test_meeting['attendees'])}")
    
    print("\n" + "-"*70)
    print("Generating briefing with agent...")
    print("-"*70 + "\n")
    
    try:
        briefing = prepare_meeting_briefing(test_meeting)
        print(briefing)
        print("\n✅ Briefing generated successfully!")
        
    except Exception as e:
        print(f"⚠️ Error with agent: {e}")
        print("Continuing with fallback...\n")
    
    # Test scenario 2: Readiness analysis
    print("\n" + "="*70)
    print("TEST 2: MEETING READINESS ANALYSIS")
    print("="*70 + "\n")
    
    readiness = analyze_meeting_readiness(test_meeting)
    
    print(f"📊 Readiness Score: {readiness['readiness_score']:.0f}/100")
    print(f"📈 Readiness Level: {readiness['readiness_level']}")
    print(f"⏱️  Estimated Prep Time: {readiness['prep_time_estimate']}")
    
    print(f"\n🔍 Contributing Factors:")
    for factor in readiness['contributing_factors']:
        print(f"   • {factor}")
    
    print(f"\n💡 Recommendations:")
    for rec in readiness['recommendations']:
        print(f"   • {rec}")
    
    print("\n" + "="*70)
    print("✅ Meeting Preparation Agent tests complete!")
    print("="*70)

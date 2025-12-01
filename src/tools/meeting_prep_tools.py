"""
Meeting preparation tools for ProFlow Agent.

Handles past meeting analysis, participant research, and briefing generation.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


def search_past_meetings(
    meeting_subject: str,
    participants: List[str] = None,
    days_back: int = 90
) -> Dict:
    """
    Search for past meetings with similar subjects or participants.
    
    Args:
        meeting_subject: Subject of the upcoming meeting
        participants: List of participant names/emails
        days_back: How many days back to search
        
    Returns:
        Dictionary with past meeting information
    """
    # TODO: Implement real GDrive search when MCP is available
    # For now, return simulated data for testing
    
    past_meetings = []
    
    # Simulate finding past meetings
    if "client" in meeting_subject.lower() or "review" in meeting_subject.lower():
        past_meetings.append({
            'date': '2025-10-15',
            'subject': 'Client Strategy Review - Q3',
            'summary': 'Discussed Q3 performance metrics, identified optimization opportunities',
            'key_decisions': [
                'Approved expansion to 5 new markets',
                'Increased budget by 20% for Q4',
                'Delayed feature launch to ensure quality'
            ],
            'action_items': [
                'Sarah: Complete market analysis by Oct 25',
                'Mike: Prepare budget proposal',
                'Team: User testing for new features'
            ],
            'participants': participants if participants else ['Sarah Chen', 'Mike Rodriguez'],
            'document_url': '#'  # Placeholder
        })
    
    if "standup" in meeting_subject.lower() or "team" in meeting_subject.lower():
        past_meetings.append({
            'date': '2025-11-10',
            'subject': 'Weekly Team Standup',
            'summary': 'Sprint planning and blockers discussion',
            'key_decisions': [
                'Prioritize bug fixes over new features',
                'Extended sprint by 2 days due to complexity'
            ],
            'action_items': [
                'Dev team: Fix critical bugs by Wed',
                'QA: Regression testing on Friday'
            ],
            'participants': ['Development Team', 'QA Team'],
            'document_url': '#'
        })
    
    return {
        'meetings_found': len(past_meetings),
        'meetings': past_meetings,
        'search_criteria': {
            'subject': meeting_subject,
            'participants': participants,
            'date_range': f'Last {days_back} days'
        }
    }


def research_participants(participants: List[str]) -> Dict:
    """
    Research meeting participants to gather context.
    
    Args:
        participants: List of participant names or emails
        
    Returns:
        Dictionary with participant information
    """
    # TODO: Implement real web search / LinkedIn lookup
    # For now, return simulated data
    
    participant_info = []
    
    for participant in participants:
        # Simulate different participant types
        if 'sarah' in participant.lower():
            participant_info.append({
                'name': 'Sarah Chen',
                'title': 'Chief Technology Officer',
                'company': 'Acme Corp',
                'role_context': 'Decision maker for technical strategy',
                'past_interactions': [
                    'Previous meetings: 8 in last 6 months',
                    'Topics discussed: AI strategy, cloud migration, security',
                    'Communication style: Direct, data-driven'
                ],
                'key_interests': ['AI/ML adoption', 'Cloud architecture', 'Team scaling'],
                'preparation_notes': 'Prepare technical details, bring data/metrics'
            })
        elif 'mike' in participant.lower():
            participant_info.append({
                'name': 'Mike Rodriguez',
                'title': 'Chief Financial Officer',
                'company': 'Acme Corp',
                'role_context': 'Oversees budget and ROI analysis',
                'past_interactions': [
                    'Previous meetings: 12 in last 6 months',
                    'Focus: Budget approvals, cost optimization',
                    'Communication style: Detail-oriented, ROI-focused'
                ],
                'key_interests': ['Cost savings', 'ROI metrics', 'Risk management'],
                'preparation_notes': 'Have cost breakdowns ready, show clear ROI'
            })
        else:
            # Generic participant
            participant_info.append({
                'name': participant,
                'title': 'Team Member',
                'company': 'Unknown',
                'role_context': 'Participant role unclear',
                'past_interactions': ['First meeting or limited history'],
                'key_interests': ['To be determined'],
                'preparation_notes': 'Research further if important stakeholder'
            })
    
    return {
        'participants_researched': len(participant_info),
        'participants': participant_info,
        'new_participants': [p for p in participant_info if 'First meeting' in str(p.get('past_interactions', ''))]
    }


def generate_meeting_briefing(
    meeting_details: Dict,
    past_meetings: Dict = None,
    participant_info: Dict = None
) -> Dict:
    """
    Generate a comprehensive meeting briefing document.
    
    Args:
        meeting_details: Details about the upcoming meeting
        past_meetings: Results from search_past_meetings()
        participant_info: Results from research_participants()
        
    Returns:
        Structured briefing document
    """
    # Extract meeting basics
    subject = meeting_details.get('subject', 'Untitled Meeting')
    date = meeting_details.get('date', 'TBD')
    duration = meeting_details.get('duration_minutes', 60)
    attendees = meeting_details.get('attendees', [])
    
    # Build briefing sections
    briefing = {
        'meeting_title': subject,
        'meeting_date': date,
        'duration': f'{duration} minutes',
        'attendees_count': len(attendees),
        
        'executive_summary': _generate_executive_summary(
            subject, past_meetings, participant_info
        ),
        
        'meeting_objective': _infer_meeting_objective(subject, past_meetings),
        
        'key_participants': _format_participants(participant_info) if participant_info else [],
        
        'relevant_history': _format_past_meetings(past_meetings) if past_meetings else [],
        
        'open_action_items': _extract_open_items(past_meetings) if past_meetings else [],
        
        'suggested_talking_points': _generate_talking_points(
            subject, past_meetings, participant_info
        ),
        
        'preparation_checklist': _generate_prep_checklist(
            subject, past_meetings, participant_info
        ),
        
        'briefing_quality_score': _calculate_briefing_score(
            past_meetings, participant_info
        )
    }
    
    return briefing


def _generate_executive_summary(subject: str, past_meetings: Dict, participant_info: Dict) -> str:
    """Generate 2-3 sentence executive summary."""
    meeting_type = "recurring" if past_meetings and past_meetings.get('meetings_found', 0) > 0 else "new"
    participant_count = len(participant_info.get('participants', [])) if participant_info else 0
    
    if meeting_type == "recurring":
        past_count = past_meetings.get('meetings_found', 0)
        return f"This is a {meeting_type} meeting with {past_count} previous session(s) in the last 90 days. {participant_count} key stakeholders will attend. Review past decisions and open action items before this meeting."
    else:
        return f"This is a {meeting_type} meeting with {participant_count} participants. Limited historical context available - focus on clear objectives and introductions."


def _infer_meeting_objective(subject: str, past_meetings: Dict) -> str:
    """Infer the meeting objective from subject and history."""
    subject_lower = subject.lower()
    
    if 'review' in subject_lower:
        return "Review progress, discuss outcomes, and plan next steps"
    elif 'planning' in subject_lower or 'plan' in subject_lower:
        return "Plan strategy, set goals, and align on roadmap"
    elif 'standup' in subject_lower or 'sync' in subject_lower:
        return "Quick team synchronization on progress and blockers"
    elif 'kickoff' in subject_lower:
        return "Introduce project, align stakeholders, and set expectations"
    elif 'decision' in subject_lower:
        return "Make key decisions and determine path forward"
    else:
        return "Discuss key topics and align on next actions"


def _format_participants(participant_info: Dict) -> List[Dict]:
    """Format participant information for briefing."""
    formatted = []
    
    for p in participant_info.get('participants', []):
        formatted.append({
            'name': p.get('name'),
            'title': p.get('title'),
            'role': p.get('role_context'),
            'prep_note': p.get('preparation_notes')
        })
    
    return formatted


def _format_past_meetings(past_meetings: Dict) -> List[Dict]:
    """Format past meeting history for briefing."""
    formatted = []
    
    for meeting in past_meetings.get('meetings', []):
        formatted.append({
            'date': meeting.get('date'),
            'summary': meeting.get('summary'),
            'key_decisions': meeting.get('key_decisions', [])
        })
    
    return formatted


def _extract_open_items(past_meetings: Dict) -> List[str]:
    """Extract open action items from past meetings."""
    open_items = []
    
    for meeting in past_meetings.get('meetings', []):
        action_items = meeting.get('action_items', [])
        # In real implementation, would check if items are completed
        # For now, just return recent action items
        open_items.extend(action_items)
    
    return open_items[:5]  # Top 5 most recent


def _generate_talking_points(subject: str, past_meetings: Dict, participant_info: Dict) -> List[str]:
    """Generate suggested talking points."""
    points = []
    
    # Add context-specific points
    if past_meetings and past_meetings.get('meetings_found', 0) > 0:
        points.append("Review action items from last meeting")
        points.append("Discuss progress since last session")
    
    if participant_info:
        new_attendees = participant_info.get('new_participants', [])
        if new_attendees:
            points.append(f"Welcome new attendees: {len(new_attendees)} joining")
    
    # Add subject-specific points
    subject_lower = subject.lower()
    if 'client' in subject_lower:
        points.append("Prepare client success metrics and case studies")
    if 'review' in subject_lower:
        points.append("Have performance data and analytics ready")
    if 'planning' in subject_lower:
        points.append("Come with timeline estimates and resource needs")
    
    # Always good generic points
    points.append("Be prepared to discuss next steps and ownership")
    points.append("Have questions ready for open discussion")
    
    return points


def _generate_prep_checklist(subject: str, past_meetings: Dict, participant_info: Dict) -> List[str]:
    """Generate preparation checklist."""
    checklist = []
    
    checklist.append("Review meeting agenda and objectives")
    
    if past_meetings and past_meetings.get('meetings_found', 0) > 0:
        checklist.append("Read past meeting minutes and decisions")
        checklist.append("Check status of previous action items")
    
    if participant_info:
        checklist.append("Review participant backgrounds and roles")
    
    checklist.append("Prepare materials (slides, documents, data)")
    checklist.append("Test technology (video, screen share)")
    checklist.append("Arrive 5 minutes early")
    
    return checklist


def _calculate_briefing_score(past_meetings: Dict, participant_info: Dict) -> float:
    """Calculate quality score for the briefing (0-100)."""
    score = 50.0  # Base score
    
    # Add points for available context
    if past_meetings:
        meetings_found = past_meetings.get('meetings_found', 0)
        score += min(meetings_found * 10, 30)  # Up to 30 points for history
    
    if participant_info:
        participants_researched = participant_info.get('participants_researched', 0)
        score += min(participants_researched * 5, 20)  # Up to 20 points for participant context
    
    return min(score, 100.0)


# Test if run directly
if __name__ == "__main__":
    print("Testing meeting preparation tools...\n")
    
    # Test scenario: Client review meeting
    print("="*60)
    print("TEST: Meeting Preparation for Client Review")
    print("="*60 + "\n")
    
    meeting = {
        'subject': 'Client Strategy Review - Q4',
        'date': '2025-11-20',
        'duration_minutes': 90,
        'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Atul Thapliyal']
    }
    
    # Search past meetings
    print("1. Searching past meetings...")
    past = search_past_meetings(
        meeting_subject=meeting['subject'],
        participants=meeting['attendees']
    )
    print(f"   Found {past['meetings_found']} past meeting(s)\n")
    
    # Research participants
    print("2. Researching participants...")
    participants = research_participants(meeting['attendees'])
    print(f"   Researched {participants['participants_researched']} participant(s)")
    print(f"   New participants: {len(participants['new_participants'])}\n")
    
    # Generate briefing
    print("3. Generating briefing...")
    briefing = generate_meeting_briefing(meeting, past, participants)
    
    print("\n" + "="*60)
    print("MEETING BRIEFING")
    print("="*60)
    print(f"\n📅 {briefing['meeting_title']}")
    print(f"🕐 {briefing['meeting_date']} ({briefing['duration']})")
    print(f"👥 {briefing['attendees_count']} attendees\n")
    
    print(f"📋 Executive Summary:")
    print(f"   {briefing['executive_summary']}\n")
    
    print(f"🎯 Meeting Objective:")
    print(f"   {briefing['meeting_objective']}\n")
    
    print(f"💡 Suggested Talking Points ({len(briefing['suggested_talking_points'])}):")
    for i, point in enumerate(briefing['suggested_talking_points'], 1):
        print(f"   {i}. {point}")
    
    print(f"\n✅ Preparation Checklist ({len(briefing['preparation_checklist'])}):")
    for i, item in enumerate(briefing['preparation_checklist'], 1):
        print(f"   {i}. {item}")
    
    print(f"\n📊 Briefing Quality Score: {briefing['briefing_quality_score']:.0f}/100")
    
    print("\n✅ Meeting prep tools test complete!")

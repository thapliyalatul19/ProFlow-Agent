"""
Scheduling coordination tools for ProFlow Agent.

Handles multi-party availability checking, optimal time finding, and meeting invitations.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


def check_availability(
    participants: List[str],
    date: str,
    duration_minutes: int = 60,
    time_range: tuple = (9, 17)
) -> Dict:
    """
    Check availability for multiple participants on a given date.
    
    Args:
        participants: List of participant names/emails
        date: Date to check (YYYY-MM-DD format)
        duration_minutes: Required meeting duration
        time_range: (start_hour, end_hour) in 24hr format
        
    Returns:
        Dictionary with availability information
    """
    # TODO: Implement real Calendar API integration
    # For MVP, simulate availability data
    
    # Simulate different availability patterns
    available_slots = []
    busy_slots = []
    
    start_hour, end_hour = time_range
    
    # Morning slot (usually good)
    if 'sarah' in str(participants).lower():
        available_slots.append({
            'time': '9:00 AM - 10:00 AM',
            'all_available': True,
            'quality_score': 0.95,
            'notes': 'Morning slot, all participants available'
        })
    
    # Mid-morning (some conflicts)
    busy_slots.append({
        'time': '10:00 AM - 11:00 AM',
        'conflicts': ['Mike Rodriguez - Budget Review'],
        'available_count': len(participants) - 1
    })
    
    # Late morning
    available_slots.append({
        'time': '11:00 AM - 12:00 PM',
        'all_available': True,
        'quality_score': 0.85,
        'notes': 'Pre-lunch slot, good availability'
    })
    
    # Lunch (usually bad)
    busy_slots.append({
        'time': '12:00 PM - 1:00 PM',
        'conflicts': ['Lunch break'],
        'available_count': 0
    })
    
    # Afternoon slots
    available_slots.append({
        'time': '2:00 PM - 3:00 PM',
        'all_available': True,
        'quality_score': 0.80,
        'notes': 'Afternoon slot, post-lunch energy dip'
    })
    
    available_slots.append({
        'time': '3:00 PM - 4:00 PM',
        'all_available': len(participants) <= 3,  # Harder with more people
        'quality_score': 0.75,
        'notes': 'Late afternoon, some conflicts possible'
    })
    
    return {
        'date': date,
        'participants_checked': len(participants),
        'duration_requested': duration_minutes,
        'available_slots': available_slots,
        'busy_slots': busy_slots,
        'total_options': len(available_slots),
        'recommendation': available_slots[0] if available_slots else None
    }


def find_optimal_time(
    participants: List[str],
    duration_minutes: int,
    date_range: tuple,
    preferences: Dict = None
) -> Dict:
    """
    Find the optimal meeting time across multiple days.
    
    Args:
        participants: List of participant names/emails
        duration_minutes: Required meeting duration
        date_range: (start_date, end_date) as strings
        preferences: User preferences for meeting times
        
    Returns:
        Ranked list of optimal meeting times
    """
    if preferences is None:
        preferences = {
            'preferred_times': ['morning', 'early_afternoon'],
            'avoid_times': ['lunch', 'late_afternoon'],
            'min_notice_hours': 24,
            'timezone': 'US/Mountain'
        }
    
    # Simulate finding optimal times across multiple days
    optimal_times = []
    
    # Day 1 - Tomorrow
    optimal_times.append({
        'date': 'Tomorrow',
        'time': '9:00 AM - 10:00 AM',
        'day_of_week': 'Monday',
        'quality_score': 0.95,
        'all_available': True,
        'rationale': 'Morning slot, all participants free, aligns with preferences',
        'timezone': preferences.get('timezone', 'US/Mountain'),
        'confidence': 0.92
    })
    
    # Day 1 - Alternative
    optimal_times.append({
        'date': 'Tomorrow',
        'time': '2:00 PM - 3:00 PM',
        'day_of_week': 'Monday',
        'quality_score': 0.85,
        'all_available': True,
        'rationale': 'Afternoon slot, good availability',
        'timezone': preferences.get('timezone', 'US/Mountain'),
        'confidence': 0.85
    })
    
    # Day 2
    optimal_times.append({
        'date': 'Day After Tomorrow',
        'time': '10:00 AM - 11:00 AM',
        'day_of_week': 'Tuesday',
        'quality_score': 0.90,
        'all_available': True,
        'rationale': 'Mid-morning, excellent for focused discussion',
        'timezone': preferences.get('timezone', 'US/Mountain'),
        'confidence': 0.88
    })
    
    # Sort by quality score
    optimal_times.sort(key=lambda x: x['quality_score'], reverse=True)
    
    return {
        'participants': participants,
        'duration': duration_minutes,
        'search_range': date_range,
        'optimal_times': optimal_times,
        'top_recommendation': optimal_times[0] if optimal_times else None,
        'alternatives': optimal_times[1:3] if len(optimal_times) > 1 else []
    }


def send_meeting_invitation(
    meeting_details: Dict,
    send_immediately: bool = False
) -> Dict:
    """
    Create and send meeting invitation.
    
    Args:
        meeting_details: Dictionary with meeting information
            - subject: Meeting title
            - attendees: List of attendee emails
            - start_time: Meeting start time
            - duration_minutes: Meeting duration
            - location: Meeting location (physical or video link)
            - description: Meeting description/agenda
        send_immediately: Whether to send now or draft
        
    Returns:
        Invitation status and details
    """
    # TODO: Implement real Calendar API invitation
    # For MVP, simulate invitation creation
    
    subject = meeting_details.get('subject', 'Team Meeting')
    attendees = meeting_details.get('attendees', [])
    start_time = meeting_details.get('start_time', 'TBD')
    duration = meeting_details.get('duration_minutes', 60)
    location = meeting_details.get('location', 'Google Meet')
    description = meeting_details.get('description', '')
    
    # Simulate invitation creation
    invitation = {
        'status': 'sent' if send_immediately else 'draft',
        'meeting_id': f'meeting_{hash(subject)}'[:16],
        'subject': subject,
        'attendees': attendees,
        'attendee_count': len(attendees),
        'start_time': start_time,
        'end_time': f'{duration} minutes after start',
        'location': location,
        'description': description,
        'calendar_link': '#',  # Would be real Google Calendar link
        'ics_file': 'meeting.ics',  # Would generate real ICS
        'sent_to': attendees if send_immediately else [],
        'response_tracking': {
            'accepted': [],
            'declined': [],
            'tentative': [],
            'no_response': attendees if send_immediately else []
        }
    }
    
    return invitation


def check_scheduling_conflicts(
    proposed_time: Dict,
    existing_meetings: List[Dict]
) -> Dict:
    """
    Check if proposed meeting time conflicts with existing meetings.
    
    Args:
        proposed_time: Proposed meeting time and duration
        existing_meetings: List of existing meetings
        
    Returns:
        Conflict analysis
    """
    conflicts = []
    warnings = []
    
    # Simulate conflict checking
    # In real implementation, would parse actual calendar events
    
    # Check for overlaps
    for meeting in existing_meetings:
        # Simplified overlap check
        if 'conflict' in meeting.get('notes', '').lower():
            conflicts.append({
                'meeting': meeting.get('subject', 'Untitled'),
                'time': meeting.get('time', 'Unknown'),
                'severity': 'high',
                'recommendation': 'Choose different time'
            })
    
    # Check for back-to-back meetings
    for meeting in existing_meetings:
        if 'adjacent' in meeting.get('notes', '').lower():
            warnings.append({
                'meeting': meeting.get('subject', 'Untitled'),
                'issue': 'Back-to-back meeting - no buffer',
                'severity': 'medium',
                'recommendation': 'Consider 15-minute buffer'
            })
    
    # Check for meeting overload
    if len(existing_meetings) > 5:
        warnings.append({
            'issue': 'Heavy meeting day',
            'count': len(existing_meetings),
            'severity': 'low',
            'recommendation': 'Consider rescheduling non-critical meetings'
        })
    
    is_feasible = len(conflicts) == 0
    
    return {
        'proposed_time': proposed_time,
        'is_feasible': is_feasible,
        'conflicts': conflicts,
        'warnings': warnings,
        'conflict_count': len(conflicts),
        'warning_count': len(warnings),
        'recommendation': 'Proceed' if is_feasible else 'Find alternative time'
    }


# Test if run directly
if __name__ == "__main__":
    print("Testing scheduling coordination tools...\n")
    
    print("="*60)
    print("TEST 1: Check Availability")
    print("="*60 + "\n")
    
    participants = ['Sarah Chen', 'Mike Rodriguez', 'Atul Thapliyal']
    availability = check_availability(
        participants=participants,
        date='2025-11-20',
        duration_minutes=60
    )
    
    print(f"📅 Checking availability for {availability['participants_checked']} participants")
    print(f"Date: {availability['date']}")
    print(f"Duration: {availability['duration_requested']} minutes\n")
    
    print(f"✅ Available Slots ({availability['total_options']}):")
    for slot in availability['available_slots']:
        print(f"  • {slot['time']} - Score: {slot['quality_score']:.0%}")
        print(f"    {slot['notes']}")
    
    print(f"\n❌ Busy Slots ({len(availability['busy_slots'])}):")
    for slot in availability['busy_slots']:
        print(f"  • {slot['time']} - Conflicts: {', '.join(slot.get('conflicts', []))}")
    
    print("\n" + "="*60)
    print("TEST 2: Find Optimal Time")
    print("="*60 + "\n")
    
    optimal = find_optimal_time(
        participants=participants,
        duration_minutes=90,
        date_range=('2025-11-20', '2025-11-22')
    )
    
    print(f"🎯 Finding optimal 90-minute slot for {len(optimal['participants'])} people\n")
    
    print(f"Top Recommendation:")
    top = optimal['top_recommendation']
    print(f"  📅 {top['date']} ({top['day_of_week']})")
    print(f"  🕐 {top['time']}")
    print(f"  ⭐ Quality Score: {top['quality_score']:.0%}")
    print(f"  💡 {top['rationale']}\n")
    
    print(f"Alternative Options ({len(optimal['alternatives'])}):")
    for i, alt in enumerate(optimal['alternatives'], 1):
        print(f"  {i}. {alt['date']} at {alt['time']} (Score: {alt['quality_score']:.0%})")
    
    print("\n" + "="*60)
    print("TEST 3: Send Meeting Invitation")
    print("="*60 + "\n")
    
    meeting = {
        'subject': 'Q4 Strategy Planning',
        'attendees': participants,
        'start_time': '2025-11-20 9:00 AM MT',
        'duration_minutes': 90,
        'location': 'Google Meet',
        'description': 'Quarterly strategy review and planning session'
    }
    
    invitation = send_meeting_invitation(meeting, send_immediately=True)
    
    print(f"📧 Meeting Invitation:")
    print(f"  Status: {invitation['status'].upper()}")
    print(f"  Subject: {invitation['subject']}")
    print(f"  Attendees: {invitation['attendee_count']}")
    print(f"  Time: {invitation['start_time']}")
    print(f"  Duration: {invitation['end_time']}")
    print(f"  Location: {invitation['location']}")
    print(f"  Meeting ID: {invitation['meeting_id']}\n")
    
    print(f"  Sent to: {', '.join(invitation['sent_to'])}")
    
    print("\n" + "="*60)
    print("TEST 4: Check Scheduling Conflicts")
    print("="*60 + "\n")
    
    proposed = {
        'time': '2:00 PM - 3:00 PM',
        'date': '2025-11-20'
    }
    
    existing = [
        {'subject': 'Team Standup', 'time': '9:00 AM', 'notes': 'regular'},
        {'subject': 'Client Call', 'time': '1:00 PM - 2:00 PM', 'notes': 'adjacent'},
        {'subject': 'Review Meeting', 'time': '3:00 PM', 'notes': 'adjacent'}
    ]
    
    conflict_check = check_scheduling_conflicts(proposed, existing)
    
    print(f"🔍 Conflict Check for {proposed['time']}:")
    print(f"  Feasible: {'✅ Yes' if conflict_check['is_feasible'] else '❌ No'}")
    print(f"  Conflicts: {conflict_check['conflict_count']}")
    print(f"  Warnings: {conflict_check['warning_count']}\n")
    
    if conflict_check['warnings']:
        print(f"⚠️  Warnings:")
        for warning in conflict_check['warnings']:
            print(f"  • {warning.get('issue', warning.get('meeting'))}")
            print(f"    Severity: {warning['severity']}")
            print(f"    Recommendation: {warning['recommendation']}")
    
    print(f"\n💡 Recommendation: {conflict_check['recommendation']}")
    
    print("\n✅ Scheduling tools test complete!")

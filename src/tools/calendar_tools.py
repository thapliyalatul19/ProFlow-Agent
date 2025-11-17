"""
Calendar optimization tools for ProFlow Agent.

Handles schedule analysis, conflict detection, and optimization suggestions.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any


def analyze_schedule(calendar_events: List[Dict], preferences: Dict = None) -> Dict:
    """
    Analyze a day's calendar for optimization opportunities.
    
    Args:
        calendar_events: List of calendar events with start/end times
        preferences: User preferences for meetings and focus time
        
    Returns:
        Dictionary with schedule analysis and suggestions
    """
    if preferences is None:
        preferences = {
            "min_buffer_minutes": 15,
            "max_consecutive_meetings": 3,
            "focus_block_duration": 90,  # minutes
            "preferred_meeting_times": ["morning", "afternoon"]
        }
    
    # TODO: Add timezone handling
    
    # Sort events by start time
    sorted_events = sorted(calendar_events, key=lambda x: x.get('start', ''))
    
    # Find conflicts (overlapping events)
    conflicts = []
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]
        
        current_end = current.get('end')
        next_start = next_event.get('start')
        
        if current_end and next_start:
            # Simple overlap check - could be more sophisticated
            if current_end > next_start:
                conflicts.append({
                    'event1': current.get('summary', 'Untitled'),
                    'event2': next_event.get('summary', 'Untitled'),
                    'overlap': True
                })
    
    # Check for missing buffers
    buffer_issues = []
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]
        
        current_end = current.get('end')
        next_start = next_event.get('start')
        
        if current_end and next_start:
            # Calculate gap between meetings
            # FIXME: This assumes string times, need proper datetime handling
            gap = 0  # placeholder
            min_buffer = preferences.get("min_buffer_minutes", 15)
            
            if gap < min_buffer:
                buffer_issues.append({
                    'after_meeting': current.get('summary', 'Untitled'),
                    'before_meeting': next_event.get('summary', 'Untitled'),
                    'actual_buffer': gap,
                    'recommended_buffer': min_buffer
                })
    
    # Calculate total meeting time and focus time available
    total_meeting_minutes = 0
    for event in sorted_events:
        # TODO: Calculate duration properly
        duration = event.get('duration_minutes', 60)  # default
        total_meeting_minutes += duration
    
    # Assume 8-hour workday (480 minutes)
    workday_minutes = 480
    available_focus_time = workday_minutes - total_meeting_minutes
    
    # Check for consecutive meeting overload
    consecutive_count = 0
    max_consecutive = 0
    overload_periods = []
    
    for event in sorted_events:
        consecutive_count += 1
        if consecutive_count > max_consecutive:
            max_consecutive = consecutive_count
        
        # Reset if there's a gap (simplified logic)
        # TODO: Implement proper gap detection
    
    max_allowed = preferences.get("max_consecutive_meetings", 3)
    if max_consecutive > max_allowed:
        overload_periods.append({
            'consecutive_meetings': max_consecutive,
            'recommendation': f'Consider moving some meetings to create breaks'
        })
    
    # Generate suggestions
    suggestions = []
    
    if conflicts:
        suggestions.append({
            'type': 'conflict_resolution',
            'priority': 'high',
            'details': f'Found {len(conflicts)} scheduling conflicts that need resolution',
            'impact': 'Cannot attend overlapping meetings'
        })
    
    if buffer_issues:
        suggestions.append({
            'type': 'add_buffer',
            'priority': 'medium',
            'details': f'{len(buffer_issues)} back-to-back meetings without adequate buffer',
            'impact': 'Risk of running late, no time for breaks'
        })
    
    if available_focus_time < preferences.get('focus_block_duration', 90):
        suggestions.append({
            'type': 'protect_focus_time',
            'priority': 'high',
            'details': f'Only {available_focus_time} minutes available for focused work',
            'impact': 'Insufficient time for deep work tasks'
        })
    
    if overload_periods:
        suggestions.append({
            'type': 'reduce_consecutive_meetings',
            'priority': 'medium',
            'details': f'Up to {max_consecutive} consecutive meetings',
            'impact': 'Mental fatigue, decreased meeting effectiveness'
        })
    
    return {
        'total_meetings': len(sorted_events),
        'total_meeting_time': total_meeting_minutes,
        'available_focus_time': available_focus_time,
        'conflicts': conflicts,
        'buffer_issues': buffer_issues,
        'max_consecutive_meetings': max_consecutive,
        'suggestions': suggestions,
        'optimization_score': _calculate_optimization_score(
            conflicts, buffer_issues, available_focus_time, max_consecutive, preferences
        )
    }


def find_available_slots(
    calendar_events: List[Dict],
    duration_minutes: int,
    date: str,
    working_hours: tuple = (9, 17)
) -> List[Dict]:
    """
    Find available time slots in a calendar for a meeting.
    
    Args:
        calendar_events: Existing calendar events
        duration_minutes: Required duration for new meeting
        date: Date to check (YYYY-MM-DD format)
        working_hours: Tuple of (start_hour, end_hour) in 24hr format
        
    Returns:
        List of available time slots
    """
    # Sort events chronologically
    sorted_events = sorted(calendar_events, key=lambda x: x.get('start', ''))
    
    available_slots = []
    
    # Simple implementation - find gaps between meetings
    # TODO: Make this more sophisticated with proper datetime handling
    
    work_start = working_hours[0]
    work_end = working_hours[1]
    
    # Check if morning slot is available
    if not sorted_events or sorted_events[0].get('start', '09:00') >= '10:00':
        available_slots.append({
            'start_time': f'{work_start:02d}:00',
            'end_time': f'{work_start + 1:02d}:00',
            'duration_minutes': duration_minutes,
            'quality_score': 0.9,  # Morning slots are generally good
            'rationale': 'Morning slot, typically high focus time'
        })
    
    # FIXME: Implement proper gap-finding algorithm
    # This is simplified for MVP
    
    return available_slots


def suggest_meeting_reschedule(
    meeting: Dict,
    reason: str,
    calendar_events: List[Dict],
    constraints: Dict = None
) -> Dict:
    """
    Suggest alternative times for rescheduling a meeting.
    
    Args:
        meeting: Original meeting details
        reason: Reason for rescheduling
        calendar_events: Current calendar to check availability
        constraints: Any scheduling constraints
        
    Returns:
        Dictionary with suggested alternative times
    """
    if constraints is None:
        constraints = {}
    
    duration = meeting.get('duration_minutes', 60)
    
    # Find available slots over next 7 days
    # TODO: Implement proper multi-day search
    
    suggested_times = []
    
    # Placeholder suggestions
    suggested_times.append({
        'date': 'Tomorrow',
        'start_time': '10:00',
        'end_time': '11:00',
        'confidence': 0.85,
        'rationale': 'Morning slot with no conflicts, allows for preparation time'
    })
    
    suggested_times.append({
        'date': 'Tomorrow',
        'start_time': '14:00',
        'end_time': '15:00',
        'confidence': 0.75,
        'rationale': 'Afternoon slot, all participants available'
    })
    
    return {
        'original_meeting': meeting.get('summary', 'Untitled'),
        'reschedule_reason': reason,
        'suggested_times': suggested_times,
        'priority': 'high' if 'urgent' in reason.lower() else 'medium'
    }


def _calculate_optimization_score(
    conflicts: List,
    buffer_issues: List,
    focus_time: int,
    max_consecutive: int,
    preferences: Dict
) -> float:
    """
    Calculate an overall schedule optimization score (0-100).
    
    Higher score = better optimized schedule
    """
    score = 100.0
    
    # Deduct points for conflicts (major issue - should severely impact score)
    score -= len(conflicts) * 30
    
    # Deduct points for buffer issues
    score -= len(buffer_issues) * 5
    
    # Deduct points for insufficient focus time
    target_focus = preferences.get('focus_block_duration', 90)
    if focus_time < target_focus:
        focus_deficit = target_focus - focus_time
        score -= (focus_deficit / target_focus) * 20
    
    # Deduct points for too many consecutive meetings
    max_allowed = preferences.get('max_consecutive_meetings', 3)
    if max_consecutive > max_allowed:
        score -= (max_consecutive - max_allowed) * 10
    
    # Keep score in valid range
    return max(0.0, min(100.0, score))


# Simple test if run directly
if __name__ == "__main__":
    print("Testing calendar optimization tools...")
    
    # Test data
    test_events = [
        {
            'summary': 'Team Standup',
            'start': '09:00',
            'end': '09:30',
            'duration_minutes': 30
        },
        {
            'summary': 'Client Meeting',
            'start': '09:30',  # Back to back!
            'end': '11:00',
            'duration_minutes': 90
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
            'start': '15:00',  # Back to back again
            'end': '16:30',
            'duration_minutes': 90
        }
    ]
    
    result = analyze_schedule(test_events)
    
    print(f"\n📊 Schedule Analysis:")
    print(f"Total meetings: {result['total_meetings']}")
    print(f"Meeting time: {result['total_meeting_time']} minutes")
    print(f"Focus time available: {result['available_focus_time']} minutes")
    print(f"Optimization score: {result['optimization_score']:.1f}/100")
    
    print(f"\n⚠️ Issues found:")
    print(f"- Conflicts: {len(result['conflicts'])}")
    print(f"- Buffer issues: {len(result['buffer_issues'])}")
    print(f"- Max consecutive meetings: {result['max_consecutive_meetings']}")
    
    print(f"\n💡 Suggestions ({len(result['suggestions'])} total):")
    for suggestion in result['suggestions']:
        print(f"- [{suggestion['priority'].upper()}] {suggestion['type']}: {suggestion['details']}")
    
    print("\n✅ Calendar tools test complete!")
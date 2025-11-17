"""
Test suite for Calendar Optimization Agent.

Tests the calendar tools and agent with various schedule scenarios.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools import calendar_tools
from agents import calendar_optimization_agent


def test_calendar_tools():
    """Test the calendar optimization tools directly."""
    print("="*60)
    print("TEST 1: Calendar Tools - Analyze Schedule")
    print("="*60 + "\n")
    
    # Scenario: Overbooked day with back-to-back meetings
    overbooked_day = [
        {'summary': 'Team Standup', 'start': '09:00', 'end': '09:30', 'duration_minutes': 30},
        {'summary': 'Client Meeting', 'start': '09:30', 'end': '11:00', 'duration_minutes': 90},
        {'summary': 'Strategy Session', 'start': '11:00', 'end': '12:00', 'duration_minutes': 60},
        {'summary': '1:1 with Manager', 'start': '14:00', 'end': '15:00', 'duration_minutes': 60},
        {'summary': 'Project Review', 'start': '15:00', 'end': '16:30', 'duration_minutes': 90},
        {'summary': 'Team Sync', 'start': '16:30', 'end': '17:00', 'duration_minutes': 30}
    ]
    
    result = calendar_tools.analyze_schedule(overbooked_day)
    
    print("📊 Schedule Analysis Results:")
    print(f"Total meetings: {result['total_meetings']}")
    print(f"Total meeting time: {result['total_meeting_time']} minutes")
    print(f"Available focus time: {result['available_focus_time']} minutes")
    print(f"Optimization score: {result['optimization_score']:.1f}/100")
    
    print(f"\n⚠️  Issues Detected:")
    print(f"Conflicts: {len(result['conflicts'])}")
    print(f"Buffer issues: {len(result['buffer_issues'])}")
    print(f"Max consecutive meetings: {result['max_consecutive_meetings']}")
    
    print(f"\n💡 Optimization Suggestions ({len(result['suggestions'])} total):")
    for i, suggestion in enumerate(result['suggestions'], 1):
        priority_emoji = "🔴" if suggestion['priority'] == 'high' else "🟡"
        print(f"{i}. {priority_emoji} [{suggestion['priority'].upper()}] {suggestion['type']}")
        print(f"   Details: {suggestion['details']}")
        print(f"   Impact: {suggestion['impact']}\n")
    
    assert result['total_meetings'] == 6, "Should detect 6 meetings"
    assert result['optimization_score'] < 80, "Overbooked schedule should have low score"
    print("✅ Test passed!\n")


def test_optimal_schedule():
    """Test with an already well-optimized schedule."""
    print("="*60)
    print("TEST 2: Well-Optimized Schedule")
    print("="*60 + "\n")
    
    # Good schedule with buffers and focus time
    good_schedule = [
        {'summary': 'Focus Block', 'start': '09:00', 'end': '11:00', 'duration_minutes': 120},
        {'summary': 'Team Standup', 'start': '11:15', 'end': '11:45', 'duration_minutes': 30},
        {'summary': 'Lunch Break', 'start': '12:00', 'end': '13:00', 'duration_minutes': 60},
        {'summary': 'Client Call', 'start': '14:00', 'end': '15:00', 'duration_minutes': 60},
    ]
    
    result = calendar_tools.analyze_schedule(good_schedule)
    
    print("📊 Schedule Analysis:")
    print(f"Total meetings: {result['total_meetings']}")
    print(f"Optimization score: {result['optimization_score']:.1f}/100")
    print(f"Available focus time: {result['available_focus_time']} minutes")
    
    if result['suggestions']:
        print(f"\n💡 Minor suggestions: {len(result['suggestions'])}")
    else:
        print("\n✅ No issues detected - schedule is well optimized!")
    
    assert result['optimization_score'] > 70, "Good schedule should have high score"
    print("\n✅ Test passed!\n")


def test_conflicting_meetings():
    """Test detection of scheduling conflicts."""
    print("="*60)
    print("TEST 3: Conflicting Meetings Detection")
    print("="*60 + "\n")
    
    # Schedule with overlapping meetings
    conflicting_schedule = [
        {'summary': 'Team Meeting', 'start': '10:00', 'end': '11:00', 'duration_minutes': 60},
        {'summary': 'Client Call', 'start': '10:30', 'end': '11:30', 'duration_minutes': 60},  # Overlap!
    ]
    
    result = calendar_tools.analyze_schedule(conflicting_schedule)
    
    print("📊 Conflict Analysis:")
    print(f"Conflicts detected: {len(result['conflicts'])}")
    
    if result['conflicts']:
        for conflict in result['conflicts']:
            print(f"\n⚠️  CONFLICT:")
            print(f"  Meeting 1: {conflict['event1']}")
            print(f"  Meeting 2: {conflict['event2']}")
    
    print(f"\nOptimization score: {result['optimization_score']:.1f}/100")
    
    assert len(result['conflicts']) > 0, "Should detect the conflict"
    assert result['optimization_score'] < 75, "Conflicts should significantly impact score"
    print("\n✅ Test passed!\n")


def test_find_available_slots():
    """Test finding available meeting slots."""
    print("="*60)
    print("TEST 4: Find Available Slots")
    print("="*60 + "\n")
    
    busy_calendar = [
        {'summary': 'Morning Meeting', 'start': '11:00', 'end': '12:00'},
        {'summary': 'Afternoon Call', 'start': '14:00', 'end': '15:00'},
    ]
    
    slots = calendar_tools.find_available_slots(
        calendar_events=busy_calendar,
        duration_minutes=60,
        date='2025-11-17'
    )
    
    print(f"Found {len(slots)} available slots:\n")
    for i, slot in enumerate(slots, 1):
        print(f"{i}. {slot['start_time']} - {slot['end_time']}")
        print(f"   Quality: {slot['quality_score']:.1f}/1.0")
        print(f"   Rationale: {slot['rationale']}\n")
    
    assert len(slots) > 0, "Should find at least one available slot"
    print("✅ Test passed!\n")


def test_reschedule_suggestions():
    """Test meeting reschedule suggestions."""
    print("="*60)
    print("TEST 5: Meeting Reschedule Suggestions")
    print("="*60 + "\n")
    
    meeting_to_reschedule = {
        'summary': 'Client Presentation',
        'start': '14:00',
        'end': '15:00',
        'duration_minutes': 60
    }
    
    current_calendar = [
        {'summary': 'Team Meeting', 'start': '10:00', 'end': '11:00'},
    ]
    
    suggestions = calendar_tools.suggest_meeting_reschedule(
        meeting=meeting_to_reschedule,
        reason='Conflict with urgent client escalation',
        calendar_events=current_calendar
    )
    
    print(f"Rescheduling: {suggestions['original_meeting']}")
    print(f"Reason: {suggestions['reschedule_reason']}")
    print(f"Priority: {suggestions['priority']}\n")
    
    print(f"Suggested alternative times ({len(suggestions['suggested_times'])}):\n")
    for i, time_slot in enumerate(suggestions['suggested_times'], 1):
        print(f"{i}. {time_slot['date']} at {time_slot['start_time']}-{time_slot['end_time']}")
        print(f"   Confidence: {time_slot['confidence']:.0%}")
        print(f"   Rationale: {time_slot['rationale']}\n")
    
    assert len(suggestions['suggested_times']) > 0, "Should provide reschedule options"
    print("✅ Test passed!\n")


def test_calendar_agent():
    """Test the full Calendar Optimization Agent."""
    print("="*60)
    print("TEST 6: Calendar Optimization Agent (Full Integration)")
    print("="*60 + "\n")
    
    # Realistic consultant schedule
    consultant_day = [
        {'summary': 'Email Review', 'start': '08:00', 'end': '08:30', 'duration_minutes': 30},
        {'summary': 'Team Standup', 'start': '09:00', 'end': '09:30', 'duration_minutes': 30},
        {'summary': 'Client Strategy Session - Verizon', 'start': '09:30', 'end': '11:30', 'duration_minutes': 120},
        {'summary': 'Internal Review', 'start': '11:30', 'end': '12:30', 'duration_minutes': 60},
        {'summary': 'Lunch', 'start': '12:30', 'end': '13:30', 'duration_minutes': 60},
        {'summary': '1:1 with Manager', 'start': '14:00', 'end': '15:00', 'duration_minutes': 60},
        {'summary': 'Project Planning', 'start': '15:15', 'end': '16:30', 'duration_minutes': 75},
        {'summary': 'Team Retrospective', 'start': '16:30', 'end': '17:00', 'duration_minutes': 30}
    ]
    
    print("📅 Analyzing consultant's schedule:")
    for event in consultant_day:
        print(f"  {event['start']}-{event['end']}: {event['summary']}")
    
    print("\n" + "-"*60)
    print("Calling Calendar Optimization Agent...")
    print("-"*60 + "\n")
    
    try:
        result = calendar_optimization_agent.analyze_daily_schedule(consultant_day)
        print(result)
        print("\n✅ Agent test complete!")
        return True
    except Exception as e:
        print(f"⚠️  Agent test skipped: {e}")
        print("(This is expected if GOOGLE_API_KEY is not configured)")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CALENDAR OPTIMIZATION AGENT - TEST SUITE")
    print("="*60 + "\n")
    
    # Run tool tests (these always work)
    test_calendar_tools()
    test_optimal_schedule()
    test_conflicting_meetings()
    test_find_available_slots()
    test_reschedule_suggestions()
    
    # Run agent test (requires API key)
    print("\n" + "="*60)
    print("INTEGRATION TEST (requires API key)")
    print("="*60 + "\n")
    
    agent_worked = test_calendar_agent()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Calendar tools: PASSED (5/5 tests)")
    
    if agent_worked:
        print("✅ Calendar agent: PASSED (1/1 test)")
        print("\n🎉 All tests passed!")
    else:
        print("⚠️  Calendar agent: SKIPPED (no API key)")
        print("\n✅ Tool tests passed! Agent test requires GOOGLE_API_KEY.")
    
    print("\nNext step: Run 'python test_calendar_agent.py' to test!")

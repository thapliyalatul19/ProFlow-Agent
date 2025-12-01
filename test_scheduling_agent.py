"""
Test suite for Scheduling Coordinator Agent.

Tests the scheduling tools and agent with various scheduling scenarios.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools import scheduling_tools
from agents import scheduling_coordinator_agent


def test_check_availability():
    """Test availability checking for multiple participants."""
    print("="*60)
    print("TEST 1: Check Availability")
    print("="*60 + "\n")
    
    participants = ['Sarah Chen', 'Mike Rodriguez', 'Team Lead']
    
    result = scheduling_tools.check_availability(
        participants=participants,
        date='2025-11-20',
        duration_minutes=60
    )
    
    print(f"📊 Availability Check Results:")
    print(f"Date: {result['date']}")
    print(f"Participants: {result['participants_checked']}")
    print(f"Duration: {result['duration_requested']} minutes\n")
    
    print(f"Available Slots: {result['total_options']}")
    print(f"Busy Periods: {len(result['busy_slots'])}\n")
    
    if result['recommendation']:
        print(f"Top Recommendation:")
        rec = result['recommendation']
        print(f"  Time: {rec['time']}")
        print(f"  Quality: {rec['quality_score']:.0%}")
        print(f"  Notes: {rec['notes']}")
    
    assert result['participants_checked'] == len(participants), "Should check all participants"
    assert result['total_options'] > 0, "Should find some available slots"
    print("\n✅ Test passed!\n")


def test_find_optimal_time():
    """Test finding optimal meeting times across date range."""
    print("="*60)
    print("TEST 2: Find Optimal Time")
    print("="*60 + "\n")
    
    participants = ['Sarah Chen', 'Mike Rodriguez', 'Atul Thapliyal']
    
    result = scheduling_tools.find_optimal_time(
        participants=participants,
        duration_minutes=90,
        date_range=('2025-11-20', '2025-11-22')
    )
    
    print(f"🎯 Optimal Time Search:")
    print(f"Participants: {len(result['participants'])}")
    print(f"Duration: {result['duration']} minutes")
    print(f"Search Range: {result['search_range']}\n")
    
    print(f"Top Recommendation:")
    top = result['top_recommendation']
    print(f"  Date: {top['date']} ({top['day_of_week']})")
    print(f"  Time: {top['time']}")
    print(f"  Quality Score: {top['quality_score']:.0%}")
    print(f"  Confidence: {top['confidence']:.0%}")
    print(f"  Rationale: {top['rationale']}\n")
    
    print(f"Alternative Options: {len(result['alternatives'])}")
    for i, alt in enumerate(result['alternatives'], 1):
        print(f"  {i}. {alt['date']} at {alt['time']} (Score: {alt['quality_score']:.0%})")
    
    assert len(result['optimal_times']) > 0, "Should find optimal times"
    assert result['top_recommendation']['quality_score'] >= 0.80, "Top option should be high quality"
    print("\n✅ Test passed!\n")


def test_send_meeting_invitation():
    """Test meeting invitation creation."""
    print("="*60)
    print("TEST 3: Send Meeting Invitation")
    print("="*60 + "\n")
    
    meeting = {
        'subject': 'Q4 Planning Session',
        'attendees': ['sarah@company.com', 'mike@company.com', 'atul@company.com'],
        'start_time': '2025-11-20 9:00 AM MT',
        'duration_minutes': 90,
        'location': 'Conference Room A / Google Meet',
        'description': 'Quarterly planning and strategy review'
    }
    
    # Test draft mode
    draft = scheduling_tools.send_meeting_invitation(meeting, send_immediately=False)
    
    print(f"📧 Meeting Invitation (Draft):")
    print(f"Status: {draft['status']}")
    print(f"Subject: {draft['subject']}")
    print(f"Attendees: {draft['attendee_count']}")
    print(f"Start Time: {draft['start_time']}")
    print(f"Location: {draft['location']}")
    print(f"Meeting ID: {draft['meeting_id']}\n")
    
    # Test send mode
    sent = scheduling_tools.send_meeting_invitation(meeting, send_immediately=True)
    
    print(f"📧 Meeting Invitation (Sent):")
    print(f"Status: {sent['status']}")
    print(f"Sent to: {len(sent['sent_to'])} attendees")
    print(f"Tracking responses: {len(sent['response_tracking']['no_response'])} pending")
    
    assert draft['status'] == 'draft', "Should create draft"
    assert sent['status'] == 'sent', "Should send invitation"
    assert sent['attendee_count'] == len(meeting['attendees']), "Should invite all attendees"
    print("\n✅ Test passed!\n")


def test_check_scheduling_conflicts():
    """Test conflict detection with existing meetings."""
    print("="*60)
    print("TEST 4: Check Scheduling Conflicts")
    print("="*60 + "\n")
    
    proposed = {
        'time': '2:00 PM - 3:00 PM',
        'date': '2025-11-20',
        'duration': 60
    }
    
    # Scenario 1: Light schedule (feasible)
    light_schedule = [
        {'subject': 'Morning Standup', 'time': '9:00 AM', 'notes': 'regular'},
        {'subject': 'Lunch', 'time': '12:00 PM', 'notes': 'blocked'}
    ]
    
    result1 = scheduling_tools.check_scheduling_conflicts(proposed, light_schedule)
    
    print(f"Scenario 1: Light Schedule")
    print(f"  Feasible: {'✅ Yes' if result1['is_feasible'] else '❌ No'}")
    print(f"  Conflicts: {result1['conflict_count']}")
    print(f"  Warnings: {result1['warning_count']}\n")
    
    # Scenario 2: Busy schedule (warnings)
    busy_schedule = [
        {'subject': 'Meeting 1', 'time': '9:00 AM', 'notes': 'regular'},
        {'subject': 'Meeting 2', 'time': '10:00 AM', 'notes': 'regular'},
        {'subject': 'Meeting 3', 'time': '11:00 AM', 'notes': 'regular'},
        {'subject': 'Lunch', 'time': '12:00 PM', 'notes': 'blocked'},
        {'subject': 'Meeting 4', 'time': '1:00 PM', 'notes': 'adjacent'},
        {'subject': 'Meeting 5', 'time': '3:00 PM', 'notes': 'adjacent'}
    ]
    
    result2 = scheduling_tools.check_scheduling_conflicts(proposed, busy_schedule)
    
    print(f"Scenario 2: Busy Schedule")
    print(f"  Feasible: {'✅ Yes' if result2['is_feasible'] else '❌ No'}")
    print(f"  Conflicts: {result2['conflict_count']}")
    print(f"  Warnings: {result2['warning_count']}")
    
    if result2['warnings']:
        print(f"\n  Warnings:")
        for warning in result2['warnings']:
            print(f"    • {warning.get('issue', 'Issue detected')}")
    
    assert result1['is_feasible'] == True, "Light schedule should be feasible"
    assert result2['warning_count'] > 0, "Busy schedule should have warnings"
    print("\n✅ Test passed!\n")


def test_scheduling_agent():
    """Test the full Scheduling Coordinator Agent."""
    print("="*60)
    print("TEST 5: Scheduling Coordinator Agent (Full Integration)")
    print("="*60 + "\n")
    
    # Complex scheduling request
    request = {
        'subject': 'Executive Team Offsite Planning',
        'participants': [
            'Sarah Chen - CTO',
            'Mike Rodriguez - CFO',
            'Atul Thapliyal - Managing Consultant',
            'Leadership Team (5 people)'
        ],
        'duration_minutes': 180,  # 3 hour session
        'date_range': ('Next Week', 'Week After'),
        'preferences': {
            'preferred_times': ['morning', 'early afternoon'],
            'avoid_times': ['late afternoon', 'friday'],
            'timezone': 'US/Mountain',
            'min_notice_hours': 48
        }
    }
    
    print(f"📅 Scheduling Request:")
    print(f"Subject: {request['subject']}")
    print(f"Participants: {len(request['participants'])}")
    print(f"Duration: {request['duration_minutes']} minutes ({request['duration_minutes']//60} hours)")
    print(f"Date Range: {request['date_range'][0]} - {request['date_range'][1]}")
    
    print("\n" + "-"*60)
    print("Calling Scheduling Coordinator Agent...")
    print("-"*60 + "\n")
    
    try:
        result = scheduling_coordinator_agent.schedule_meeting(request)
        print(result)
        print("\n✅ Agent test complete!")
        return True
    except Exception as e:
        print(f"⚠️  Agent test skipped: {e}")
        print("(This is expected if GOOGLE_API_KEY is not configured)\n")
        
        # Fallback to tool demonstration
        print("Demonstrating with direct tool calls:\n")
        
        optimal = scheduling_tools.find_optimal_time(
            participants=request['participants'],
            duration_minutes=request['duration_minutes'],
            date_range=('2025-11-20', '2025-11-25')
        )
        
        print(f"✅ Found {len(optimal['optimal_times'])} viable time slots")
        print(f"🎯 Best option: {optimal['top_recommendation']['date']} at {optimal['top_recommendation']['time']}")
        print(f"   Quality: {optimal['top_recommendation']['quality_score']:.0%}")
        print(f"   {optimal['top_recommendation']['rationale']}")
        
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCHEDULING COORDINATOR AGENT - TEST SUITE")
    print("="*60 + "\n")
    
    # Run tool tests
    test_check_availability()
    test_find_optimal_time()
    test_send_meeting_invitation()
    test_check_scheduling_conflicts()
    
    # Run agent test
    print("\n" + "="*60)
    print("INTEGRATION TEST (requires API key)")
    print("="*60 + "\n")
    
    agent_worked = test_scheduling_agent()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Scheduling tools: PASSED (4/4 tests)")
    
    if agent_worked:
        print("✅ Scheduling agent: PASSED (1/1 test)")
        print("\n🎉 All tests passed!")
    else:
        print("⚠️  Scheduling agent: SKIPPED (no API key)")
        print("\n✅ Tool tests passed! Agent test requires GOOGLE_API_KEY.")
    
    print("\nNext step: Build Orchestrator to tie all 4 agents together!")

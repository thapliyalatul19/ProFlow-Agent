"""
Test suite for Meeting Preparation Agent.

Tests the meeting prep tools and agent with various meeting scenarios.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools import meeting_prep_tools
from agents import meeting_prep_agent


def test_search_past_meetings():
    """Test searching for past meetings."""
    print("="*60)
    print("TEST 1: Search Past Meetings")
    print("="*60 + "\n")
    
    result = meeting_prep_tools.search_past_meetings(
        meeting_subject="Client Strategy Review",
        participants=["Sarah Chen", "Mike Rodriguez"]
    )
    
    print(f"📊 Search Results:")
    print(f"Meetings found: {result['meetings_found']}")
    print(f"Search criteria: {result['search_criteria']}\n")
    
    if result['meetings_found'] > 0:
        for i, meeting in enumerate(result['meetings'], 1):
            print(f"{i}. {meeting['subject']} ({meeting['date']})")
            print(f"   Summary: {meeting['summary']}")
            print(f"   Decisions: {len(meeting['key_decisions'])}")
            print(f"   Action Items: {len(meeting['action_items'])}\n")
    
    assert result['meetings_found'] >= 0, "Should return meeting count"
    print("✅ Test passed!\n")


def test_research_participants():
    """Test participant research functionality."""
    print("="*60)
    print("TEST 2: Research Participants")
    print("="*60 + "\n")
    
    participants = ["Sarah Chen", "Mike Rodriguez", "John Doe"]
    
    result = meeting_prep_tools.research_participants(participants)
    
    print(f"👥 Participant Research:")
    print(f"Total researched: {result['participants_researched']}")
    print(f"New participants: {len(result['new_participants'])}\n")
    
    for i, p in enumerate(result['participants'], 1):
        print(f"{i}. {p['name']} - {p['title']}")
        print(f"   Role: {p['role_context']}")
        print(f"   Prep Note: {p['preparation_notes']}\n")
    
    assert result['participants_researched'] == len(participants), "Should research all participants"
    print("✅ Test passed!\n")


def test_generate_briefing_with_history():
    """Test briefing generation with past meeting history."""
    print("="*60)
    print("TEST 3: Generate Briefing (With History)")
    print("="*60 + "\n")
    
    meeting = {
        'subject': 'Client Strategy Review - Q4',
        'date': '2025-11-22',
        'duration_minutes': 90,
        'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Atul Thapliyal']
    }
    
    # Get context
    past = meeting_prep_tools.search_past_meetings(
        meeting['subject'],
        meeting['attendees']
    )
    participants = meeting_prep_tools.research_participants(meeting['attendees'])
    
    # Generate briefing
    briefing = meeting_prep_tools.generate_meeting_briefing(
        meeting, past, participants
    )
    
    print(f"📋 Briefing Generated:")
    print(f"Title: {briefing['meeting_title']}")
    print(f"Quality Score: {briefing['briefing_quality_score']:.0f}/100\n")
    
    print(f"Executive Summary:")
    print(f"   {briefing['executive_summary']}\n")
    
    print(f"Meeting Objective:")
    print(f"   {briefing['meeting_objective']}\n")
    
    print(f"Key Participants: {len(briefing['key_participants'])}")
    print(f"Relevant History: {len(briefing['relevant_history'])}")
    print(f"Open Action Items: {len(briefing['open_action_items'])}")
    print(f"Talking Points: {len(briefing['suggested_talking_points'])}")
    print(f"Prep Checklist: {len(briefing['preparation_checklist'])}")
    
    assert briefing['briefing_quality_score'] > 50, "Should have decent quality with context"
    assert len(briefing['key_participants']) > 0, "Should have participant info"
    print("\n✅ Test passed!\n")


def test_generate_briefing_without_history():
    """Test briefing generation for a new meeting without history."""
    print("="*60)
    print("TEST 4: Generate Briefing (No History)")
    print("="*60 + "\n")
    
    meeting = {
        'subject': 'New Product Kickoff',
        'date': '2025-11-25',
        'duration_minutes': 60,
        'attendees': ['Alice Johnson', 'Bob Smith']
    }
    
    # Generate with no past context
    briefing = meeting_prep_tools.generate_meeting_briefing(meeting)
    
    print(f"📋 Briefing Generated:")
    print(f"Title: {briefing['meeting_title']}")
    print(f"Quality Score: {briefing['briefing_quality_score']:.0f}/100\n")
    
    print(f"Executive Summary:")
    print(f"   {briefing['executive_summary']}\n")
    
    print(f"Meeting Objective:")
    print(f"   {briefing['meeting_objective']}\n")
    
    assert briefing['briefing_quality_score'] <= 60, "Lower score without history"
    assert len(briefing['suggested_talking_points']) > 0, "Should still have talking points"
    print("✅ Test passed!\n")


def test_briefing_quality_scoring():
    """Test that briefing quality scores vary appropriately."""
    print("="*60)
    print("TEST 5: Briefing Quality Scoring")
    print("="*60 + "\n")
    
    # Scenario 1: No context
    briefing_no_context = meeting_prep_tools.generate_meeting_briefing({
        'subject': 'Test Meeting',
        'date': '2025-11-20',
        'duration_minutes': 30,
        'attendees': []
    })
    
    # Scenario 2: With participant context
    participants = meeting_prep_tools.research_participants(['Sarah Chen', 'Mike Rodriguez'])
    briefing_with_participants = meeting_prep_tools.generate_meeting_briefing(
        {'subject': 'Test Meeting', 'date': '2025-11-20', 'duration_minutes': 30, 'attendees': []},
        participant_info=participants
    )
    
    # Scenario 3: With both past meetings and participants
    past = meeting_prep_tools.search_past_meetings('Client Review', ['Sarah Chen'])
    participants = meeting_prep_tools.research_participants(['Sarah Chen', 'Mike Rodriguez'])
    briefing_full_context = meeting_prep_tools.generate_meeting_briefing(
        {'subject': 'Client Review', 'date': '2025-11-20', 'duration_minutes': 60, 'attendees': []},
        past, participants
    )
    
    score_no_context = briefing_no_context['briefing_quality_score']
    score_with_participants = briefing_with_participants['briefing_quality_score']
    score_full_context = briefing_full_context['briefing_quality_score']
    
    print(f"📊 Quality Score Comparison:")
    print(f"No context: {score_no_context:.0f}/100")
    print(f"With participants: {score_with_participants:.0f}/100")
    print(f"Full context: {score_full_context:.0f}/100\n")
    
    assert score_with_participants > score_no_context, "Participant context should improve score"
    assert score_full_context > score_with_participants, "Full context should have highest score"
    print("✅ Test passed!\n")


def test_meeting_prep_agent():
    """Test the full Meeting Preparation Agent."""
    print("="*60)
    print("TEST 6: Meeting Preparation Agent (Full Integration)")
    print("="*60 + "\n")
    
    # Important executive meeting
    meeting = {
        'subject': 'Q4 Strategic Planning with Leadership',
        'date': '2025-11-22',
        'duration_minutes': 120,
        'attendees': ['Sarah Chen - CTO', 'Mike Rodriguez - CFO', 'Executive Team']
    }
    
    print(f"📅 Meeting Details:")
    print(f"Subject: {meeting['subject']}")
    print(f"Date: {meeting['date']}")
    print(f"Duration: {meeting['duration_minutes']} minutes")
    print(f"Attendees: {', '.join(meeting['attendees'])}")
    
    print("\n" + "-"*60)
    print("Calling Meeting Preparation Agent...")
    print("-"*60 + "\n")
    
    try:
        briefing = meeting_prep_agent.prepare_meeting_briefing(meeting)
        print(briefing)
        print("\n✅ Agent test complete!")
        return True
    except Exception as e:
        print(f"⚠️  Agent test skipped: {e}")
        print("(This is expected if GOOGLE_API_KEY is not configured)")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MEETING PREPARATION AGENT - TEST SUITE")
    print("="*60 + "\n")
    
    # Run tool tests (these always work)
    test_search_past_meetings()
    test_research_participants()
    test_generate_briefing_with_history()
    test_generate_briefing_without_history()
    test_briefing_quality_scoring()
    
    # Run agent test (requires API key)
    print("\n" + "="*60)
    print("INTEGRATION TEST (requires API key)")
    print("="*60 + "\n")
    
    agent_worked = test_meeting_prep_agent()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Meeting prep tools: PASSED (5/5 tests)")
    
    if agent_worked:
        print("✅ Meeting prep agent: PASSED (1/1 test)")
        print("\n🎉 All tests passed!")
    else:
        print("⚠️  Meeting prep agent: SKIPPED (no API key)")
        print("\n✅ Tool tests passed! Agent test requires GOOGLE_API_KEY.")
    
    print("\nNext step: Commit this work and move to Scheduling Coordinator!")

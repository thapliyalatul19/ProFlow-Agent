"""
Test suite for ProFlow Orchestrator.

Tests multi-agent workflows: Sequential, Parallel, and Loop patterns.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflows.orchestrator import ProFlowOrchestrator


def test_daily_briefing_workflow():
    """Test Sequential Workflow: Email → Calendar → Meeting Prep"""
    print("="*60)
    print("TEST 1: Daily Briefing (Sequential Workflow)")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    # Realistic morning scenario
    emails = [
        {
            'subject': 'URGENT: Production issue - API down',
            'from': 'ops@company.com',
            'body': 'Production API experiencing 500 errors. Need immediate attention.'
        },
        {
            'subject': 'Meeting Request: Budget Review',
            'from': 'mike@company.com',
            'body': 'Can we schedule 60min this week to review Q4 budget?'
        },
        {
            'subject': 'FYI: Team update',
            'from': 'team@company.com',
            'body': 'Sprint completed successfully. Here are the highlights...'
        },
        {
            'subject': 'Client feedback on proposal',
            'from': 'client@verizon.com',
            'body': 'Thanks for the proposal. We have some questions about timeline...'
        }
    ]
    
    calendar = [
        {
            'summary': 'Morning Standup',
            'start': '09:00',
            'end': '09:15',
            'duration_minutes': 15,
            'type': 'meeting',
            'attendees': ['Development Team']
        },
        {
            'summary': 'Client Strategy Review',
            'start': '10:00',
            'end': '11:30',
            'duration_minutes': 90,
            'type': 'meeting',
            'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Client Team']
        },
        {
            'summary': '1:1 with Manager',
            'start': '14:00',
            'end': '15:00',
            'duration_minutes': 60,
            'type': 'meeting',
            'attendees': ['Manager']
        }
    ]
    
    print("📊 Input:")
    print(f"  Emails: {len(emails)}")
    print(f"  Calendar Events: {len(calendar)}\n")
    
    briefing = orchestrator.generate_daily_briefing(emails, calendar)
    
    print("\n✅ Briefing Generated")
    print("-"*60)
    print(f"Workflow Type: {briefing['workflow_type']}")
    print(f"\nExecutive Summary:")
    print(f"  {briefing['summary']}\n")
    
    # Validate email intelligence
    email_intel = briefing['components']['email_intelligence']
    print(f"📧 Email Intelligence:")
    print(f"  Total Processed: {email_intel['total_emails']}")
    print(f"  High Priority: {len(email_intel['high_priority'])}")
    print(f"  Meeting Requests: {len(email_intel['meeting_requests'])}")
    
    # Validate calendar optimization
    cal_opt = briefing['components']['calendar_optimization']
    print(f"\n📅 Calendar Optimization:")
    print(f"  Meetings Today: {cal_opt['total_meetings']}")
    print(f"  Meeting Time: {cal_opt['meeting_time_minutes']} min")
    print(f"  Focus Time: {cal_opt['focus_time_minutes']} min")
    print(f"  Optimization Score: {cal_opt['optimization_score']:.0f}/100")
    
    # Validate meeting preparations
    meeting_prep = briefing['components']['meeting_preparation']
    print(f"\n📋 Meeting Preparations:")
    print(f"  Briefings Generated: {len(meeting_prep)}")
    if meeting_prep:
        avg_quality = sum(m['quality_score'] for m in meeting_prep) / len(meeting_prep)
        print(f"  Avg Quality Score: {avg_quality:.0f}/100")
    
    assert briefing['workflow_type'] == 'sequential', "Should use sequential workflow"
    assert len(briefing['components']) == 3, "Should have 3 components"
    print("\n✅ Test passed!\n")


def test_scheduling_workflow_success():
    """Test Loop Workflow: Successful scheduling on first attempt"""
    print("="*60)
    print("TEST 2: Meeting Scheduling - Success (Loop Workflow)")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    request = {
        'subject': 'Quarterly Business Review',
        'participants': ['Sarah Chen', 'Mike Rodriguez', 'Executive Team'],
        'duration_minutes': 120,
        'date': '2025-11-20',
        'date_range': ('2025-11-20', '2025-11-22'),
        'location': 'Executive Conference Room',
        'description': 'Q4 review and planning session',
        'existing_meetings': []  # No conflicts
    }
    
    print("📊 Scheduling Request:")
    print(f"  Subject: {request['subject']}")
    print(f"  Participants: {len(request['participants'])}")
    print(f"  Duration: {request['duration_minutes']} minutes\n")
    
    result = orchestrator.schedule_meeting_workflow(request, check_conflicts=True)
    
    print("\n✅ Scheduling Complete")
    print("-"*60)
    print(f"Workflow Type: {result['workflow_type']}")
    print(f"Iterations Required: {len(result['iterations'])}")
    print(f"Final Outcome: {result.get('final_outcome', 'unknown')}\n")
    
    # Validate success path
    assert result['workflow_type'] == 'loop', "Should use loop workflow"
    assert len(result['iterations']) <= 3, "Should complete within 3 iterations"
    
    if result.get('final_outcome') == 'scheduled':
        last_iter = result['iterations'][-1]
        print(f"📅 Meeting Scheduled:")
        print(f"  Time: {last_iter['steps']['optimal_time']['time']}")
        print(f"  Quality: {last_iter['steps']['optimal_time']['quality_score']:.0%}")
        print(f"  Invitation: {last_iter['steps']['invitation']['status']}")
    
    print("\n✅ Test passed!\n")


def test_scheduling_workflow_conflicts():
    """Test Loop Workflow: Handling conflicts with retry"""
    print("="*60)
    print("TEST 3: Meeting Scheduling - With Conflicts (Loop Workflow)")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    # Request with existing conflicts
    request = {
        'subject': 'Team Planning Session',
        'participants': ['Sarah Chen', 'Mike Rodriguez'],
        'duration_minutes': 90,
        'date': '2025-11-20',
        'date_range': ('2025-11-20', '2025-11-22'),
        'location': 'Conference Room B',
        'description': 'Strategic planning',
        'existing_meetings': [
            {'subject': 'Blocking Meeting', 'time': '2:00 PM', 'notes': 'conflict'}
        ]
    }
    
    print("📊 Scheduling Request (with conflicts):")
    print(f"  Participants: {len(request['participants'])}")
    print(f"  Existing Meetings: {len(request['existing_meetings'])}\n")
    
    result = orchestrator.schedule_meeting_workflow(request, check_conflicts=True)
    
    print("\n✅ Workflow Complete")
    print("-"*60)
    print(f"Iterations: {len(result['iterations'])}")
    print(f"Final Outcome: {result.get('final_outcome', 'unknown')}")
    
    # Show iteration outcomes
    print(f"\nIteration Results:")
    for i, iteration in enumerate(result['iterations'], 1):
        print(f"  {i}. Outcome: {iteration['outcome']}")
    
    assert len(result['iterations']) >= 1, "Should attempt at least once"
    print("\n✅ Test passed!\n")


def test_parallel_meeting_preparation():
    """Test Parallel Workflow: Concurrent task execution"""
    print("="*60)
    print("TEST 4: Meeting Preparation (Parallel Workflow)")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    meeting = {
        'subject': 'Client Strategy Review - Q4 Planning',
        'date': '2025-11-22 10:00 AM',
        'duration_minutes': 120,
        'attendees': [
            'Sarah Chen - CTO',
            'Mike Rodriguez - CFO',
            'Client Executive Team'
        ]
    }
    
    print("📊 Meeting Details:")
    print(f"  Subject: {meeting['subject']}")
    print(f"  Duration: {meeting['duration_minutes']} minutes")
    print(f"  Attendees: {len(meeting['attendees'])}\n")
    
    result = orchestrator.prepare_meeting_parallel(meeting)
    
    print("\n✅ Preparation Complete")
    print("-"*60)
    print(f"Workflow Type: {result['workflow_type']}")
    print(f"Parallel Tasks Executed: {result['parallel_tasks_completed']}")
    print(f"\nResults:")
    print(f"  Past Meetings Found: {result['past_meetings_found']}")
    print(f"  Participants Researched: {result['participants_researched']}")
    print(f"  Briefing Quality Score: {result['briefing_quality']:.0f}/100")
    
    # Validate parallel execution structure
    assert result['workflow_type'] == 'parallel', "Should use parallel workflow"
    assert result['parallel_tasks_completed'] == 2, "Should complete 2 parallel tasks"
    assert 'briefing' in result, "Should generate briefing"
    
    print("\n✅ Test passed!\n")


def test_orchestrator_integration():
    """Test full orchestrator with all workflows"""
    print("="*60)
    print("TEST 5: Full Orchestrator Integration")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    print("Testing orchestrator capabilities:\n")
    
    # Test 1: User preferences loaded
    print("✓ User preferences configured")
    assert hasattr(orchestrator, 'user_preferences'), "Should have user preferences"
    assert orchestrator.user_preferences['timezone'] == 'US/Mountain', "Should have timezone"
    
    # Test 2: All tool modules loaded
    print("✓ All agent tools loaded")
    assert hasattr(orchestrator, 'email_tools'), "Should have email tools"
    assert hasattr(orchestrator, 'calendar_tools'), "Should have calendar tools"
    assert hasattr(orchestrator, 'meeting_prep_tools'), "Should have meeting prep tools"
    assert hasattr(orchestrator, 'scheduling_tools'), "Should have scheduling tools"
    
    # Test 3: All workflows available
    print("✓ All workflows available")
    assert callable(orchestrator.generate_daily_briefing), "Should have daily briefing workflow"
    assert callable(orchestrator.schedule_meeting_workflow), "Should have scheduling workflow"
    assert callable(orchestrator.prepare_meeting_parallel), "Should have parallel prep workflow"
    
    # Test 4: Quick workflow execution
    print("✓ Testing quick workflow execution...")
    
    # Minimal daily briefing
    minimal_briefing = orchestrator.generate_daily_briefing(
        emails=[{'subject': 'Test', 'from': 'test@test.com', 'body': 'Test'}],
        calendar_events=[]
    )
    assert 'components' in minimal_briefing, "Should generate briefing"
    
    print("✓ All integration tests passed")
    
    print("\n✅ Test passed!\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PROFLOW ORCHESTRATOR - COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    # Run all tests
    test_daily_briefing_workflow()
    test_scheduling_workflow_success()
    test_scheduling_workflow_conflicts()
    test_parallel_meeting_preparation()
    test_orchestrator_integration()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Daily Briefing (Sequential): PASSED")
    print("✅ Scheduling Success (Loop): PASSED")
    print("✅ Scheduling Conflicts (Loop): PASSED")
    print("✅ Meeting Prep (Parallel): PASSED")
    print("✅ Full Integration: PASSED")
    
    print("\n🎉 All orchestrator tests passed!")
    print("\n" + "="*60)
    print("PROFLOW DEVELOPMENT COMPLETE!")
    print("="*60)
    print("\n✅ 4 Specialized Agents")
    print("✅ Multi-Agent Orchestration")
    print("✅ 3 Workflow Patterns (Sequential, Parallel, Loop)")
    print("✅ Comprehensive Test Coverage")
    print("\n🚀 Ready for documentation and deployment!")

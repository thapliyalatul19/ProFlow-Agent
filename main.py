"""
ProFlow Agent - Main CLI Interface

Command-line interface for ProFlow executive productivity agent.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflows.orchestrator import ProFlowOrchestrator
from data import read_emails_from_csv, read_calendar_from_json


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ProFlow Executive Productivity Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate daily briefing with default data files
  python main.py briefing

  # Generate briefing with custom data files
  python main.py briefing --emails data/my_emails.csv --calendar data/my_calendar.json

  # Schedule a meeting
  python main.py schedule --subject "Team Sync" --participants "alice@example.com,bob@example.com" --duration 60
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Briefing command
    briefing_parser = subparsers.add_parser('briefing', help='Generate daily briefing')
    briefing_parser.add_argument(
        '--emails',
        type=str,
        default=None,
        help='Path to email CSV file (default: data/sample_emails.csv)'
    )
    briefing_parser.add_argument(
        '--calendar',
        type=str,
        default=None,
        help='Path to calendar JSON file (default: data/calendar.json)'
    )
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a meeting')
    schedule_parser.add_argument('--subject', type=str, required=True, help='Meeting subject')
    schedule_parser.add_argument('--participants', type=str, required=True, help='Comma-separated list of participants')
    schedule_parser.add_argument('--duration', type=int, default=60, help='Duration in minutes (default: 60)')
    schedule_parser.add_argument('--date', type=str, default='tomorrow', help='Preferred date (default: tomorrow)')
    schedule_parser.add_argument('--location', type=str, default='TBD', help='Meeting location (default: TBD)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize orchestrator
    orchestrator = ProFlowOrchestrator()
    
    try:
        if args.command == 'briefing':
            return handle_briefing(orchestrator, args)
        elif args.command == 'schedule':
            return handle_schedule(orchestrator, args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the data files exist. You can create them using:")
        print("  - data/sample_emails.csv")
        print("  - data/calendar.json")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_briefing(orchestrator: ProFlowOrchestrator, args):
    """Handle the briefing command."""
    print("="*60)
    print("PROFLOW - DAILY BRIEFING")
    print("="*60)
    print()
    
    # Load data from files
    print("📂 Loading data from files...")
    try:
        emails, calendar_events = orchestrator.load_data_from_files(
            email_csv_path=args.emails,
            calendar_json_path=args.calendar
        )
        print(f"  ✓ Loaded {len(emails)} emails")
        print(f"  ✓ Loaded {len(calendar_events)} calendar events")
    except Exception as e:
        print(f"  ✗ Failed to load data: {e}")
        return 1
    
    print()
    
    # Generate briefing
    briefing = orchestrator.generate_daily_briefing(emails, calendar_events)
    
    # Display results
    print()
    print("="*60)
    print("DAILY BRIEFING SUMMARY")
    print("="*60)
    print(f"\n{briefing['summary']}\n")
    
    # Email Intelligence
    email_comp = briefing['components']['email_intelligence']
    print("📧 EMAIL INTELLIGENCE")
    print("-" * 60)
    print(f"Total emails: {email_comp['total_emails']}")
    print(f"High priority: {len(email_comp['high_priority'])}")
    print(f"Medium priority: {len(email_comp['medium_priority'])}")
    print(f"Low priority: {len(email_comp['low_priority'])}")
    print(f"Action items: {len(email_comp['action_items'])}")
    print(f"Meeting requests: {len(email_comp['meeting_requests'])}")
    
    if email_comp['high_priority']:
        print("\n  High Priority Emails:")
        for email in email_comp['high_priority']:
            print(f"    • {email['subject']} (from: {email['from']}, urgency: {email['urgency_score']}/10)")
    
    if email_comp['action_items']:
        print("\n  Action Items:")
        for item in email_comp['action_items'][:5]:  # Show first 5
            print(f"    • {item.get('task', 'N/A')} (priority: {item.get('priority', 'N/A')})")
    
    # Calendar Optimization
    calendar_comp = briefing['components']['calendar_optimization']
    print("\n📅 CALENDAR OPTIMIZATION")
    print("-" * 60)
    print(f"Total meetings: {calendar_comp['total_meetings']}")
    print(f"Meeting time: {calendar_comp['meeting_time_minutes']} minutes")
    print(f"Focus time available: {calendar_comp['focus_time_minutes']} minutes")
    print(f"Optimization score: {calendar_comp['optimization_score']:.1f}/100")
    
    if calendar_comp['conflicts']:
        print("\n  ⚠️ Conflicts detected:")
        for conflict in calendar_comp['conflicts']:
            print(f"    • {conflict.get('event1', 'N/A')} conflicts with {conflict.get('event2', 'N/A')}")
    
    if calendar_comp['suggestions']:
        print("\n  💡 Suggestions:")
        for suggestion in calendar_comp['suggestions']:
            print(f"    • [{suggestion.get('priority', 'medium').upper()}] {suggestion.get('details', 'N/A')}")
    
    # Meeting Preparation
    meeting_comp = briefing['components']['meeting_preparation']
    print("\n📋 MEETING PREPARATION")
    print("-" * 60)
    print(f"Meetings prepared: {len(meeting_comp)}")
    
    for meeting in meeting_comp:
        print(f"\n  • {meeting['meeting']} ({meeting['time']})")
        print(f"    Briefing quality: {meeting['quality_score']:.0f}/100")
    
    print("\n" + "="*60)
    print("✅ Briefing complete!")
    print("="*60)
    
    return 0


def handle_schedule(orchestrator: ProFlowOrchestrator, args):
    """Handle the schedule command."""
    print("="*60)
    print("PROFLOW - MEETING SCHEDULING")
    print("="*60)
    print()
    
    # Parse participants
    participants = [p.strip() for p in args.participants.split(',')]
    
    meeting_request = {
        'subject': args.subject,
        'participants': participants,
        'duration_minutes': args.duration,
        'date': args.date,
        'date_range': ('tomorrow', 'next week'),
        'location': args.location,
        'description': f'Meeting: {args.subject}',
        'existing_meetings': []
    }
    
    print(f"📅 Scheduling: {args.subject}")
    print(f"   Participants: {', '.join(participants)}")
    print(f"   Duration: {args.duration} minutes")
    print(f"   Preferred date: {args.date}")
    print()
    
    # Run scheduling workflow
    result = orchestrator.schedule_meeting_workflow(meeting_request)
    
    # Display results
    print()
    print("="*60)
    print("SCHEDULING RESULT")
    print("="*60)
    print(f"Workflow type: {result['workflow_type']}")
    print(f"Iterations: {len(result['iterations'])}")
    print(f"Final outcome: {result.get('final_outcome', 'unknown')}")
    
    if result.get('final_outcome') == 'scheduled':
        last_iteration = result['iterations'][-1]
        if 'optimal_time' in last_iteration['steps']:
            optimal = last_iteration['steps']['optimal_time']
            print(f"\n✅ Meeting scheduled:")
            print(f"   Time: {optimal.get('time', 'N/A')}")
            print(f"   Quality score: {optimal.get('quality_score', 0):.0%}")
        if 'invitation' in last_iteration['steps']:
            invite = last_iteration['steps']['invitation']
            print(f"   Invitation status: {invite.get('status', 'N/A')}")
    else:
        print(f"\n⚠️ Scheduling was not successful")
        if result['iterations']:
            last_iteration = result['iterations'][-1]
            if 'conflicts' in last_iteration['steps']:
                conflicts = last_iteration['steps']['conflicts']
                if not conflicts.get('is_feasible', True):
                    print(f"   Reason: Conflicts detected")
    
    print("\n" + "="*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())


"""
ProFlow Orchestrator - Multi-Agent Coordination

Coordinates Email Intelligence, Calendar Optimization, Meeting Preparation,
and Scheduling Coordinator agents to deliver executive productivity workflows.
"""

from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import email_tools, calendar_tools, meeting_prep_tools, scheduling_tools


class ProFlowOrchestrator:
    """
    Main orchestrator for ProFlow multi-agent system.
    
    Coordinates workflows across all specialized agents:
    - Email Intelligence Agent
    - Calendar Optimization Agent
    - Meeting Preparation Agent
    - Scheduling Coordinator Agent
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agent tools."""
        self.email_tools = email_tools
        self.calendar_tools = calendar_tools
        self.meeting_prep_tools = meeting_prep_tools
        self.scheduling_tools = scheduling_tools
        
        # User preferences (would come from memory/config in production)
        self.user_preferences = {
            'name': 'Executive User',
            'min_buffer_minutes': 15,
            'max_consecutive_meetings': 3,
            'focus_block_duration': 90,
            'preferred_meeting_times': ['morning', 'early_afternoon'],
            'timezone': 'US/Mountain'
        }
    
    def generate_daily_briefing(self, emails: List[Dict], calendar_events: List[Dict]) -> Dict:
        """
        Generate comprehensive daily briefing (Sequential Workflow).
        
        Flow: Email Analysis → Calendar Optimization → Meeting Preparation
        
        Args:
            emails: List of recent emails
            calendar_events: Today's calendar events
            
        Returns:
            Complete daily briefing
        """
        briefing = {
            'generated_at': 'Morning',
            'workflow_type': 'sequential',
            'components': {}
        }
        
        # Step 1: Email Intelligence
        print("📧 Analyzing emails...")
        email_analysis = self._analyze_emails(emails)
        briefing['components']['email_intelligence'] = email_analysis
        
        # Step 2: Calendar Optimization  
        print("📅 Optimizing schedule...")
        schedule_analysis = self._optimize_schedule(calendar_events)
        briefing['components']['calendar_optimization'] = schedule_analysis
        
        # Step 3: Meeting Preparation (for today's meetings)
        print("📋 Preparing meeting briefings...")
        meeting_briefings = self._prepare_meetings(calendar_events)
        briefing['components']['meeting_preparation'] = meeting_briefings
        
        # Step 4: Generate Summary
        briefing['summary'] = self._generate_briefing_summary(
            email_analysis, schedule_analysis, meeting_briefings
        )
        
        return briefing
    
    def _analyze_emails(self, emails: List[Dict]) -> Dict:
        """Analyze emails using Email Intelligence tools."""
        high_priority = []
        medium_priority = []
        low_priority = []
        action_items = []
        meeting_requests = []
        
        for email in emails:
            # Classify priority
            classification = self.email_tools.classify_email_priority(
                subject=email.get('subject', ''),
                sender=email.get('from', ''),
                body=email.get('body', '')
            )
            
            priority = classification.get('priority', 'medium')
            
            if priority == 'high':
                high_priority.append({
                    'subject': email.get('subject'),
                    'from': email.get('from'),
                    'urgency_score': classification.get('urgency_score', 5)
                })
            elif priority == 'medium':
                medium_priority.append({
                    'subject': email.get('subject'),
                    'from': email.get('from')
                })
            else:
                low_priority.append({
                    'subject': email.get('subject'),
                    'from': email.get('from')
                })
            
            # Extract action items
            if classification.get('action_items'):
                action_items.extend(classification['action_items'])
            
            # Check for meeting requests
            if 'meeting' in email.get('subject', '').lower():
                meeting_request = self.email_tools.extract_meeting_requests(email)
                if meeting_request:
                    meeting_requests.append(meeting_request)
        
        return {
            'total_emails': len(emails),
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'action_items': action_items,
            'meeting_requests': meeting_requests,
            'summary': f"{len(high_priority)} high priority, {len(meeting_requests)} meeting requests"
        }
    
    def _optimize_schedule(self, calendar_events: List[Dict]) -> Dict:
        """Optimize schedule using Calendar Optimization tools."""
        analysis = self.calendar_tools.analyze_schedule(
            calendar_events,
            preferences=self.user_preferences
        )
        
        return {
            'total_meetings': analysis['total_meetings'],
            'meeting_time_minutes': analysis['total_meeting_time'],
            'focus_time_minutes': analysis['available_focus_time'],
            'optimization_score': analysis['optimization_score'],
            'conflicts': analysis['conflicts'],
            'suggestions': analysis['suggestions'],
            'summary': f"{analysis['total_meetings']} meetings, {analysis['available_focus_time']}min focus time, score: {analysis['optimization_score']:.0f}/100"
        }
    
    def _prepare_meetings(self, calendar_events: List[Dict]) -> List[Dict]:
        """Prepare briefings for today's meetings (Parallel-capable)."""
        briefings = []
        
        # In production, these could run in parallel
        # For now, sequential execution
        for event in calendar_events:
            if event.get('type') != 'meeting':
                continue
            
            meeting_details = {
                'subject': event.get('summary', 'Untitled'),
                'date': event.get('start', 'TBD'),
                'duration_minutes': event.get('duration_minutes', 60),
                'attendees': event.get('attendees', [])
            }
            
            # Search past meetings
            past_meetings = self.meeting_prep_tools.search_past_meetings(
                meeting_subject=meeting_details['subject'],
                participants=meeting_details['attendees']
            )
            
            # Research participants
            participants = self.meeting_prep_tools.research_participants(
                meeting_details['attendees']
            )
            
            # Generate briefing
            briefing = self.meeting_prep_tools.generate_meeting_briefing(
                meeting_details, past_meetings, participants
            )
            
            briefings.append({
                'meeting': meeting_details['subject'],
                'time': meeting_details['date'],
                'quality_score': briefing['briefing_quality_score'],
                'briefing': briefing
            })
        
        return briefings
    
    def _generate_briefing_summary(
        self,
        email_analysis: Dict,
        schedule_analysis: Dict,
        meeting_briefings: List[Dict]
    ) -> str:
        """Generate executive summary of daily briefing."""
        summary_lines = []
        
        # Email summary
        high_count = len(email_analysis['high_priority'])
        if high_count > 0:
            summary_lines.append(f"📧 {high_count} high-priority emails require attention")
        
        # Schedule summary
        score = schedule_analysis['optimization_score']
        if score < 70:
            summary_lines.append(f"⚠️ Schedule optimization score: {score:.0f}/100 - consider adjustments")
        
        # Meeting summary
        if meeting_briefings:
            avg_quality = sum(m['quality_score'] for m in meeting_briefings) / len(meeting_briefings)
            summary_lines.append(f"📋 {len(meeting_briefings)} meetings today (avg briefing quality: {avg_quality:.0f}/100)")
        
        # Focus time alert
        if schedule_analysis['focus_time_minutes'] < 90:
            summary_lines.append(f"🚨 Limited focus time: {schedule_analysis['focus_time_minutes']}min (target: 90min)")
        
        return " | ".join(summary_lines) if summary_lines else "✅ Well-optimized day ahead"
    
    def schedule_meeting_workflow(
        self,
        meeting_request: Dict,
        check_conflicts: bool = True
    ) -> Dict:
        """
        Handle meeting scheduling workflow (Loop-capable).
        
        Flow: Check availability → Find optimal time → Check conflicts → Send invitation
        Can loop if conflicts found (up to 3 iterations).
        
        Args:
            meeting_request: Meeting details
            check_conflicts: Whether to check for conflicts
            
        Returns:
            Scheduling result
        """
        print("🔄 Starting scheduling workflow...")
        
        result = {
            'workflow_type': 'loop',
            'max_iterations': 3,
            'iterations': []
        }
        
        for iteration in range(1, 4):  # Max 3 attempts
            print(f"\n  Iteration {iteration}/3...")
            
            iteration_result = {
                'number': iteration,
                'steps': {}
            }
            
            # Step 1: Check availability
            print(f"    Checking availability...")
            availability = self.scheduling_tools.check_availability(
                participants=meeting_request['participants'],
                date=meeting_request.get('date', '2025-11-20'),
                duration_minutes=meeting_request['duration_minutes']
            )
            iteration_result['steps']['availability'] = {
                'slots_found': availability['total_options'],
                'recommendation': availability['recommendation']
            }
            
            if availability['total_options'] == 0:
                iteration_result['outcome'] = 'no_availability'
                result['iterations'].append(iteration_result)
                break
            
            # Step 2: Find optimal time
            print(f"    Finding optimal time...")
            optimal = self.scheduling_tools.find_optimal_time(
                participants=meeting_request['participants'],
                duration_minutes=meeting_request['duration_minutes'],
                date_range=meeting_request.get('date_range', ('tomorrow', 'next week'))
            )
            iteration_result['steps']['optimal_time'] = optimal['top_recommendation']
            
            # Step 3: Check conflicts (if requested)
            has_conflicts = False
            if check_conflicts:
                print(f"    Checking conflicts...")
                conflicts = self.scheduling_tools.check_scheduling_conflicts(
                    proposed_time=optimal['top_recommendation'],
                    existing_meetings=meeting_request.get('existing_meetings', [])
                )
                iteration_result['steps']['conflicts'] = conflicts
                has_conflicts = not conflicts['is_feasible']
            
            # If no conflicts, proceed to send invitation
            if not has_conflicts:
                print(f"    Preparing invitation...")
                invitation = self.scheduling_tools.send_meeting_invitation(
                    meeting_details={
                        'subject': meeting_request['subject'],
                        'attendees': meeting_request['participants'],
                        'start_time': optimal['top_recommendation']['time'],
                        'duration_minutes': meeting_request['duration_minutes'],
                        'location': meeting_request.get('location', 'TBD'),
                        'description': meeting_request.get('description', '')
                    },
                    send_immediately=False  # Draft mode
                )
                iteration_result['steps']['invitation'] = invitation
                iteration_result['outcome'] = 'success'
                result['iterations'].append(iteration_result)
                result['final_outcome'] = 'scheduled'
                break
            else:
                # Conflicts found, try next iteration
                iteration_result['outcome'] = 'conflicts_found'
                result['iterations'].append(iteration_result)
                
                if iteration == 3:
                    result['final_outcome'] = 'failed_after_max_iterations'
        
        return result
    
    def prepare_meeting_parallel(self, meeting_details: Dict) -> Dict:
        """
        Prepare meeting briefing using parallel execution.
        
        Runs these in parallel (simulated):
        - Search past meetings
        - Research participants
        
        Then synthesizes into briefing.
        """
        print("⚡ Preparing meeting briefing (parallel workflow)...")
        
        # In production ADK, these would run truly in parallel
        # For now, we execute sequentially but structure for parallelization
        
        # Parallel Task 1: Search past meetings
        print("  → Searching past meetings...")
        past_meetings = self.meeting_prep_tools.search_past_meetings(
            meeting_subject=meeting_details['subject'],
            participants=meeting_details.get('attendees', [])
        )
        
        # Parallel Task 2: Research participants (runs "simultaneously")
        print("  → Researching participants...")
        participants = self.meeting_prep_tools.research_participants(
            meeting_details.get('attendees', [])
        )
        
        # Synthesis: Generate briefing from parallel results
        print("  → Generating briefing...")
        briefing = self.meeting_prep_tools.generate_meeting_briefing(
            meeting_details, past_meetings, participants
        )
        
        return {
            'workflow_type': 'parallel',
            'parallel_tasks_completed': 2,
            'past_meetings_found': past_meetings['meetings_found'],
            'participants_researched': participants['participants_researched'],
            'briefing_quality': briefing['briefing_quality_score'],
            'briefing': briefing
        }


# Test the orchestrator
if __name__ == "__main__":
    print("="*60)
    print("PROFLOW ORCHESTRATOR - TESTING")
    print("="*60 + "\n")
    
    orchestrator = ProFlowOrchestrator()
    
    # Test 1: Daily Briefing Workflow
    print("TEST 1: Daily Briefing (Sequential Workflow)")
    print("-"*60 + "\n")
    
    test_emails = [
        {
            'subject': 'URGENT: Client escalation needs immediate response',
            'from': 'client@verizon.com',
            'body': 'Critical issue with deployment...'
        },
        {
            'subject': 'Meeting request: Q4 Planning',
            'from': 'sarah@company.com',
            'body': 'Can we meet next week to discuss Q4 strategy?'
        },
        {
            'subject': 'FYI: Weekly report',
            'from': 'team@company.com',
            'body': 'Here is this week\'s progress report...'
        }
    ]
    
    test_calendar = [
        {
            'summary': 'Team Standup',
            'start': '09:00',
            'end': '09:30',
            'duration_minutes': 30,
            'type': 'meeting',
            'attendees': ['Team']
        },
        {
            'summary': 'Client Strategy Review',
            'start': '10:00',
            'end': '11:30',
            'duration_minutes': 90,
            'type': 'meeting',
            'attendees': ['Sarah Chen', 'Mike Rodriguez']
        },
        {
            'summary': 'Lunch',
            'start': '12:00',
            'end': '13:00',
            'duration_minutes': 60,
            'type': 'personal'
        }
    ]
    
    briefing = orchestrator.generate_daily_briefing(test_emails, test_calendar)
    
    print("\n✅ DAILY BRIEFING GENERATED")
    print("="*60)
    print(f"Summary: {briefing['summary']}")
    print(f"\nEmail Intelligence:")
    print(f"  - {briefing['components']['email_intelligence']['summary']}")
    print(f"\nCalendar Optimization:")
    print(f"  - {briefing['components']['calendar_optimization']['summary']}")
    print(f"\nMeeting Preparations:")
    print(f"  - {len(briefing['components']['meeting_preparation'])} briefings generated")
    
    # Test 2: Meeting Scheduling Workflow
    print("\n\n" + "="*60)
    print("TEST 2: Meeting Scheduling (Loop Workflow)")
    print("-"*60 + "\n")
    
    scheduling_request = {
        'subject': 'Executive Team Sync',
        'participants': ['Sarah Chen', 'Mike Rodriguez', 'Team Lead'],
        'duration_minutes': 60,
        'date': '2025-11-20',
        'date_range': ('tomorrow', 'next week'),
        'location': 'Conference Room A',
        'description': 'Weekly executive sync',
        'existing_meetings': []  # No conflicts
    }
    
    scheduling_result = orchestrator.schedule_meeting_workflow(scheduling_request)
    
    print("\n✅ SCHEDULING WORKFLOW COMPLETE")
    print("="*60)
    print(f"Workflow Type: {scheduling_result['workflow_type']}")
    print(f"Iterations: {len(scheduling_result['iterations'])}")
    print(f"Final Outcome: {scheduling_result.get('final_outcome', 'unknown')}")
    
    if scheduling_result.get('final_outcome') == 'scheduled':
        last_iteration = scheduling_result['iterations'][-1]
        print(f"\n🎉 Meeting Scheduled:")
        print(f"  Time: {last_iteration['steps']['optimal_time']['time']}")
        print(f"  Quality Score: {last_iteration['steps']['optimal_time']['quality_score']:.0%}")
        if 'invitation' in last_iteration['steps']:
            print(f"  Invitation Status: {last_iteration['steps']['invitation']['status']}")
    
    # Test 3: Parallel Meeting Preparation
    print("\n\n" + "="*60)
    print("TEST 3: Meeting Preparation (Parallel Workflow)")
    print("-"*60 + "\n")
    
    meeting_to_prep = {
        'subject': 'Client Strategy Review - Q4',
        'date': '2025-11-22',
        'duration_minutes': 90,
        'attendees': ['Sarah Chen', 'Mike Rodriguez', 'Client Team']
    }
    
    prep_result = orchestrator.prepare_meeting_parallel(meeting_to_prep)
    
    print("\n✅ MEETING PREPARATION COMPLETE")
    print("="*60)
    print(f"Workflow Type: {prep_result['workflow_type']}")
    print(f"Parallel Tasks: {prep_result['parallel_tasks_completed']}")
    print(f"Past Meetings Found: {prep_result['past_meetings_found']}")
    print(f"Participants Researched: {prep_result['participants_researched']}")
    print(f"Briefing Quality: {prep_result['briefing_quality']:.0f}/100")
    
    print("\n\n" + "="*60)
    print("✅ ALL ORCHESTRATOR TESTS COMPLETE!")
    print("="*60)
    print("\nProFlow is ready for integration! 🚀")

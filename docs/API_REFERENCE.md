# ProFlow API Reference

**Version**: 1.0.0  
**Last Updated**: November 17, 2024

---

## Table of Contents

1. [Orchestrator API](#orchestrator-api)
2. [Email Intelligence Agent](#email-intelligence-agent)
3. [Calendar Optimization Agent](#calendar-optimization-agent)
4. [Meeting Preparation Agent](#meeting-preparation-agent)
5. [Task Management Agent](#task-management-agent)
6. [Scheduling Coordinator Agent](#scheduling-coordinator-agent)

---

## Orchestrator API

### ProFlowOrchestrator

Main coordinator for all ProFlow agents.

#### `__init__(user_preferences=None)`

Initialize the orchestrator.

**Parameters**:
- `user_preferences` (dict, optional): User-specific settings
  - `work_hours`: tuple, e.g. `('09:00', '17:00')`
  - `focus_time_preference`: str, `'morning'` or `'afternoon'`
  - `meeting_duration_default`: int, minutes

**Example**:
```python
from src.workflows.orchestrator import ProFlowOrchestrator

orchestrator = ProFlowOrchestrator(user_preferences={
    'work_hours': ('08:00', '18:00'),
    'focus_time_preference': 'morning',
    'meeting_duration_default': 60
})
```

#### `generate_daily_briefing()`

Generate comprehensive morning briefing.

**Returns**: dict
```python
{
    'email_summary': {
        'total_unread': int,
        'priority_emails': list[dict],
        'action_items': list[dict]
    },
    'calendar_analysis': {
        'meetings_today': int,
        'conflicts': list[dict],
        'focus_time_available': int,  # minutes
        'fragmentation_score': float
    },
    'meetings_needing_prep': list[dict]
}
```

**Example**:
```python
briefing = orchestrator.generate_daily_briefing()

print(f"You have {briefing['email_summary']['total_unread']} unread emails")
print(f"Priority items: {len(briefing['email_summary']['priority_emails'])}")
print(f"Meetings today: {briefing['calendar_analysis']['meetings_today']}")
```

#### `schedule_meeting_workflow(title, attendees, duration, preferred_time)`

Schedule meeting with automatic conflict resolution.

**Parameters**:
- `title` (str): Meeting title
- `attendees` (list[str]): Email addresses of attendees
- `duration` (int): Meeting duration in minutes
- `preferred_time` (str): ISO format datetime, e.g. `'2024-11-20T14:00:00Z'`

**Returns**: dict
```python
{
    'status': 'SUCCESS' | 'CONFLICT' | 'FAILED',
    'meeting_time': str,  # Confirmed time
    'attendees_confirmed': list[str],
    'calendar_invite_sent': bool,
    'attempts': int,
    'alternatives': list[dict]  # If conflicts exist
}
```

**Example**:
```python
result = orchestrator.schedule_meeting_workflow(
    title="Q1 Planning Session",
    attendees=["alice@company.com", "bob@company.com"],
    duration=60,
    preferred_time="2024-11-20T14:00:00Z"
)

if result['status'] == 'SUCCESS':
    print(f"Meeting scheduled for {result['meeting_time']}")
else:
    print(f"Conflict detected. Alternatives: {result['alternatives']}")
```

#### `prepare_meeting_parallel(meeting_details)`

Prepare meeting briefing using parallel searches.

**Parameters**:
- `meeting_details` (dict):
  - `title`: str
  - `time`: str (ISO format)
  - `attendees`: list[str]
  - `duration`: int (minutes)

**Returns**: dict
```python
{
    'briefing': str,  # Markdown formatted
    'participants': list[dict],
    'discussion_topics': list[str],
    'pending_action_items': list[dict],
    'execution_time_seconds': float
}
```

**Example**:
```python
briefing = orchestrator.prepare_meeting_parallel({
    'title': 'Board Strategy Session',
    'time': '2024-11-25T09:00:00Z',
    'attendees': ['ceo@company.com', 'cfo@company.com'],
    'duration': 120
})

print(briefing['briefing'])  # Display formatted briefing
```

---

## Email Intelligence Agent

### create_email_intelligence_agent()

Factory function to create Email Intelligence Agent.

**Returns**: `LlmAgent` instance

**Example**:
```python
from src.agents.email_intelligence_agent import create_email_intelligence_agent

agent = create_email_intelligence_agent()
```

### Agent Methods

#### `generate_content(query)`

Process email-related queries.

**Query Examples**:

**1. Classify Email**:
```python
query = """
Analyze this email:

From: john.doe@client.com
Subject: URGENT: Production server down
Body: Our production server has been down for 30 minutes. 
Need immediate assistance. Revenue impact approximately $10K/hour.

Provide: priority level, category, urgency, action items
"""

response = agent.generate_content(query)
```

**Response**:
```python
{
    'priority': 'P0',  # Crisis
    'category': 'INCIDENT',
    'urgency_score': 10,
    'sentiment': 'NEGATIVE',
    'action_items': [
        {
            'task': 'Investigate production server outage',
            'deadline': 'IMMEDIATE',
            'priority': 'CRITICAL'
        }
    ]
}
```

**2. Extract Action Items**:
```python
query = """
From this email thread, extract all action items:

[Email content with multiple tasks mentioned]

Format as: task, owner, deadline, priority
"""

response = agent.generate_content(query)
```

**3. Draft Response**:
```python
query = """
Draft a professional response to:

From: alice@company.com
Subject: Q4 Budget Review Request
[Email body]

Tone: Professional, concise
Confirm: Will review by Friday
"""

response = agent.generate_content(query)
```

### Tool Functions

#### `classify_email_priority(subject, body, sender, timestamp, urgency_signals)`

Classify email into 8-tier priority system.

**Parameters**:
- `subject` (str): Email subject line
- `body` (str): Email body content
- `sender` (str): Sender email address
- `timestamp` (str): ISO format datetime
- `urgency_signals` (list[str], optional): Keywords indicating urgency

**Returns**: dict
```python
{
    'priority_level': str,  # P0-P7
    'priority_name': str,   # e.g., 'CRISIS', 'HIGH_PRIORITY'
    'score': float,         # 0.0-1.0
    'reasoning': str,
    'recommended_action': str
}
```

**Priority Levels**:
- **P0**: Crisis (security breach, system outage)
- **P1**: Urgent + Important (deadline today, executive request)
- **P2**: Important but not urgent (strategic decisions)
- **P3**: Urgent but not important (routine approvals)
- **P4**: Normal (standard business)
- **P5**: Low (FYI, newsletters)
- **P6**: Very Low (promotions, marketing)
- **P7**: Archive (spam, irrelevant)

#### `extract_action_items(email_content, extract_deadlines=True)`

Extract actionable tasks from email.

**Parameters**:
- `email_content` (str): Full email content
- `extract_deadlines` (bool): Whether to parse deadlines

**Returns**: list[dict]
```python
[
    {
        'task': 'Review contract',
        'deadline': '2024-11-20',
        'priority': 'HIGH',
        'estimated_duration': 30  # minutes
    },
    ...
]
```

#### `detect_meeting_requests(email_content)`

Detect if email contains meeting request.

**Parameters**:
- `email_content` (str): Email body

**Returns**: dict
```python
{
    'is_meeting_request': bool,
    'proposed_times': list[str],  # ISO format
    'duration': int,  # minutes
    'attendees': list[str],
    'confidence': float  # 0.0-1.0
}
```

---

## Calendar Optimization Agent

### create_calendar_optimization_agent()

Factory function to create Calendar Agent.

**Returns**: `LlmAgent` instance

### Agent Methods

#### `generate_content(query)`

Analyze calendar and provide recommendations.

**Query Example**:
```python
query = """
Analyze my calendar for today:

[Calendar data]

Provide:
- Conflict detection
- Focus time calculation
- Scheduling recommendations
- Fragmentation score
"""

response = agent.generate_content(query)
```

### Tool Functions

#### `analyze_calendar_day(events, target_date)`

Comprehensive calendar analysis for a day.

**Parameters**:
- `events` (list[dict]): Calendar events
  ```python
  {
      'title': str,
      'start': str,  # ISO format
      'end': str,
      'attendees': list[str]
  }
  ```
- `target_date` (str): Date to analyze, format `'YYYY-MM-DD'`

**Returns**: dict
```python
{
    'total_meetings': int,
    'total_meeting_time': int,  # minutes
    'meeting_breakdown': dict,
    'gaps': list[tuple],  # Available time slots
    'analysis': str
}
```

#### `detect_conflicts(events)`

Detect scheduling conflicts.

**Returns**: list[dict]
```python
[
    {
        'time': '2024-11-20T14:00:00Z',
        'conflicting_meetings': [
            {'title': 'Board Meeting', 'priority': 'HIGH'},
            {'title': 'Client Call', 'priority': 'MEDIUM'}
        ],
        'resolution': 'Reschedule Client Call to 15:30',
        'impact': 'HIGH'
    }
]
```

#### `calculate_focus_time(events, work_hours=('09:00', '17:00'))`

Calculate available focus time blocks.

**Parameters**:
- `events` (list[dict]): Calendar events
- `work_hours` (tuple): Start and end of workday

**Returns**: dict
```python
{
    'total_focus_minutes': int,
    'focus_blocks': [
        ('09:00', '11:00'),  # 2-hour morning block
        ('14:00', '15:00')   # 1-hour afternoon block
    ],
    'longest_block_minutes': int,
    'recommendation': str
}
```

#### `calculate_fragmentation(events)`

Calculate calendar fragmentation score.

**Formula**: 
```
fragmentation = (number_of_gaps / total_gaps_possible) * 10
+ (average_gap_duration / 120) * context_switch_penalty
```

**Returns**: dict
```python
{
    'score': float,  # 1-10, lower is better
    'context_switches': int,
    'average_gap_minutes': float,
    'recommendation': str
}
```

**Interpretation**:
- **1-3**: Excellent (long uninterrupted blocks)
- **4-6**: Good (some context switching)
- **7-8**: Poor (highly fragmented)
- **9-10**: Critical (constant interruptions)

---

## Meeting Preparation Agent

### create_meeting_prep_agent()

Factory function to create Meeting Prep Agent.

**Returns**: `LlmAgent` instance

### Tool Functions

#### `search_emails_for_context(participants, keywords, date_range)`

Search emails for meeting context.

**Parameters**:
- `participants` (list[str]): Attendee email addresses
- `keywords` (list[str]): Search terms
- `date_range` (tuple): `(start_date, end_date)` in ISO format

**Returns**: list[dict]
```python
[
    {
        'subject': str,
        'from': str,
        'date': str,
        'snippet': str,  # First 200 chars
        'relevance_score': float
    }
]
```

#### `research_participants(participant_emails)`

Research meeting participants.

**Returns**: list[dict]
```python
[
    {
        'name': str,
        'email': str,
        'title': str,
        'recent_interactions': list[dict],
        'discussion_topics': list[str],
        'background': str
    }
]
```

#### `generate_briefing(meeting_details, context_data)`

Generate formatted meeting briefing.

**Parameters**:
- `meeting_details` (dict): Meeting metadata
- `context_data` (dict): Gathered context from searches

**Returns**: str (Markdown formatted)
```markdown
# Meeting Briefing: Board Strategy Session
**Date**: November 25, 2024, 9:00 AM
**Duration**: 2 hours
**Attendees**: CEO, CFO, Board Members

## Overview
[Executive summary]

## Participants
### John Doe (CEO)
- Recent interactions: [...]
- Key topics: [...]

## Discussion Topics
1. Q4 Financial Performance
2. 2025 Strategic Priorities
...

## Your Pending Action Items
- [ ] Complete budget analysis (Due: Nov 20)
...

## Suggested Talking Points
- [...]

## Recent Relevant Communications
- [...]
```

---

## Task Management Agent

### create_task_management_agent()

Factory function to create Task Agent.

**Returns**: `LlmAgent` instance

### Tool Functions

#### `categorize_task_eisenhower(task_description, urgency_score, importance_score, deadline, sender_context)`

Categorize task into Eisenhower Matrix quadrant.

**Parameters**:
- `task_description` (str): What needs to be done
- `urgency_score` (int): 0-10, time sensitivity
- `importance_score` (int): 0-10, long-term impact
- `deadline` (str, optional): ISO format or relative
- `sender_context` (str, optional): Who requested it

**Returns**: dict
```python
{
    'quadrant': str,  # Q1, Q2, Q3, or Q4
    'action': str,    # DO FIRST, SCHEDULE, DELEGATE, ELIMINATE
    'priority_level': str,  # CRITICAL, HIGH, MEDIUM, LOW
    'urgency_score': int,
    'importance_score': int,
    'recommendation': str,
    'reasoning': str
}
```

**Eisenhower Quadrants**:
- **Q1**: Urgent + Important → DO FIRST
- **Q2**: Not Urgent + Important → SCHEDULE
- **Q3**: Urgent + Not Important → DELEGATE
- **Q4**: Not Urgent + Not Important → ELIMINATE

#### `calculate_deadline_urgency(deadline, task_type, consequences)`

Calculate urgency score based on deadline.

**Parameters**:
- `deadline` (str): ISO format or relative
- `task_type` (str): `'hard_deadline'`, `'soft_deadline'`, `'milestone'`, `'general'`
- `consequences` (str, optional): Impact if missed

**Returns**: dict
```python
{
    'urgency_score': int,  # 0-10
    'status': str,  # OVERDUE, URGENT - TODAY, THIS WEEK, etc.
    'deadline': str,  # ISO format
    'hours_until_deadline': float,
    'days_until_deadline': int,
    'is_overdue': bool,
    'warning': str  # If urgent
}
```

**Scoring**:
- **10**: Overdue or due today
- **8-9**: Tomorrow
- **6-7**: This week (2-5 days)
- **4-5**: Next week (6-10 days)
- **2-3**: This month (11-20 days)
- **0-1**: More than 3 weeks

#### `batch_process_tasks(tasks, categorization_hints)`

Efficiently process multiple tasks.

**Parameters**:
- `tasks` (list[dict]): Tasks to categorize
  ```python
  {
      'title': str,
      'urgency_score': int,
      'importance_score': int,
      'estimated_duration': int,
      'deadline': str (optional)
  }
  ```
- `categorization_hints` (dict, optional): Scoring adjustments

**Returns**: dict
```python
{
    'summary': {
        'total_tasks': int,
        'by_quadrant': dict,  # Counts per quadrant
        'total_time_estimated': int,
        'overdue_tasks': int,
        'blocked_tasks': int
    },
    'categorized_tasks': {
        'Q1': list[dict],
        'Q2': list[dict],
        'Q3': list[dict],
        'Q4': list[dict]
    },
    'insights': list[str],
    'recommended_order': list[dict],  # Top 10 to tackle
    'quick_wins': list[dict],  # Tasks under 15 min
    'delegation_candidates': list[dict],
    'elimination_candidates': list[dict]
}
```

---

## Scheduling Coordinator Agent

### create_scheduling_coordinator_agent()

Factory function to create Scheduling Agent.

**Returns**: `LlmAgent` instance

### Tool Functions

#### `check_multi_party_availability(attendee_emails, date_range, duration)`

Check availability for multiple attendees.

**Parameters**:
- `attendee_emails` (list[str]): Email addresses
- `date_range` (tuple): `(start_date, end_date)` ISO format
- `duration` (int): Meeting duration in minutes

**Returns**: dict
```python
{
    'available_slots': list[dict],
    'attendee_availability': dict,  # Per attendee
    'optimal_times': list[str],  # Top 3 recommendations
    'conflicts': list[dict]
}
```

#### `find_optimal_meeting_time(availability_matrix, preferences)`

Find best meeting time given constraints.

**Parameters**:
- `availability_matrix` (dict): Availability per attendee
- `preferences` (dict): User preferences (work hours, etc.)

**Returns**: dict
```python
{
    'recommended_time': str,  # ISO format
    'attendees_available': list[str],
    'fit_score': float,  # 0-100
    'reasoning': str,
    'alternatives': list[str]  # Top 3 alternatives
}
```

---

## Error Handling

All API functions return structured error responses:

```python
{
    'status': 'error',
    'error_code': str,  # e.g., 'RATE_LIMIT_EXCEEDED'
    'error_message': str,
    'retry_after': int (optional),  # Seconds
    'fallback_action': str (optional)
}
```

**Common Error Codes**:
- `RATE_LIMIT_EXCEEDED`: Too many API requests
- `INVALID_INPUT`: Malformed parameters
- `API_ERROR`: External API failure
- `TIMEOUT`: Request took too long
- `AUTHENTICATION_ERROR`: Invalid credentials

---

## Rate Limits

### Gmail API
- **Queries**: 250/second/user
- **Mitigation**: Exponential backoff implemented

### Google Calendar API
- **Queries**: 1,000,000/day
- **Mitigation**: Caching and batching

### Gemini API
- **Requests**: Based on quota tier
- **Mitigation**: Request queuing and rate limiting

---

## Best Practices

### 1. Error Handling
Always wrap API calls in try-except:

```python
try:
    result = orchestrator.generate_daily_briefing()
except Exception as e:
    logger.error(f"Briefing failed: {e}")
    # Handle gracefully
```

### 2. Timeouts
Set reasonable timeouts:

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    result = agent.generate_content(query)
finally:
    signal.alarm(0)  # Cancel alarm
```

### 3. Caching
Cache frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_participant_info(email):
    # Expensive operation
    return research_participants([email])
```

---

**Document Version**: 1.0.0  
**Last Updated**: November 17, 2024  
**Maintained by**: Atul Thapliyal

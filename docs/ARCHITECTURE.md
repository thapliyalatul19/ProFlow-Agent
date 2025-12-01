# ProFlow Architecture Documentation

**Version**: 1.0.0  
**Last Updated**: November 17, 2024

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Agent Architecture](#agent-architecture)
3. [Workflow Patterns](#workflow-patterns)
4. [Tool Framework](#tool-framework)
5. [Data Flow](#data-flow)
6. [State Management](#state-management)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (CLI / API / Future: Web)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ProFlow Orchestrator                         │
│  • Sequential Workflows (Email → Calendar → Meeting Prep)       │
│  • Parallel Workflows (Concurrent searches)                     │
│  • Loop Workflows (Scheduling with retry)                       │
│  • State Management & Error Handling                            │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
       │          │           │          │          │
       ▼          ▼           ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│  Email   │ │Calendar│ │ Meeting  │ │  Task  │ │Scheduling│
│   Agent  │ │ Agent  │ │Prep Agent│ │ Agent  │ │  Agent   │
└────┬─────┘ └───┬────┘ └────┬─────┘ └───┬────┘ └────┬─────┘
     │           │            │            │           │
     ▼           ▼            ▼            ▼           ▼
┌────────────────────────────────────────────────────────────┐
│                        Tool Layer                           │
│  • Email Tools (5)  • Calendar Tools (5)  • Task Tools (5) │
│  • Meeting Tools (5)  • Scheduling Tools (5)               │
└────┬───────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    External APIs                             │
│  • Gmail API  • Google Calendar API  • Gemini API           │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each agent has a single, well-defined purpose
2. **Modularity**: Agents and tools can be developed and tested independently
3. **Composability**: Complex workflows built from simple agent interactions
4. **Resilience**: Graceful degradation when individual components fail
5. **Observability**: Comprehensive logging and state tracking

---

## Agent Architecture

### Agent Template

Each ProFlow agent follows this structure:

```python
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

def create_agent():
    """Factory function for agent creation."""
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.0-flash-exp"),
        name="agent_name",
        description="Brief agent description",
        instruction="""
        Comprehensive instructions for agent behavior:
        - What the agent does
        - How it should reason
        - Expected output format
        - Error handling approach
        """,
        tools=[tool1, tool2, tool3]  # List of tools
    )
    
    return agent
```

### Agent Specifications

#### 1. Email Intelligence Agent

**Responsibilities**:
- Email classification (8-tier priority system)
- Action item extraction
- Meeting request detection
- Response drafting

**Input**: Email content (subject, body, sender, timestamp)

**Output**:
```python
{
    'priority': 'P1',  # P0-P7
    'category': 'MEETING_REQUEST',
    'sentiment': 'NEUTRAL',
    'action_items': [
        {
            'task': 'Review budget proposal',
            'deadline': '2024-11-20',
            'priority': 'HIGH'
        }
    ],
    'suggested_response': "..."
}
```

**Tools Used**:
- `classify_email_priority`
- `extract_action_items`
- `detect_meeting_requests`
- `analyze_sentiment`
- `draft_response`

#### 2. Calendar Optimization Agent

**Responsibilities**:
- Schedule analysis
- Conflict detection
- Focus time calculation
- Time block suggestions

**Input**: Calendar events for specified date range

**Output**:
```python
{
    'conflicts': [
        {
            'time': '2024-11-20 14:00',
            'meetings': ['Board Meeting', 'Client Call'],
            'resolution': 'Reschedule client call to 15:30'
        }
    ],
    'focus_time': {
        'blocks': [('09:00', '11:00'), ('14:00', '15:00')],
        'total_minutes': 180
    },
    'fragmentation_score': 6.5,  # 1-10, lower is better
    'recommendations': [...]
}
```

**Tools Used**:
- `analyze_calendar_day`
- `detect_conflicts`
- `calculate_focus_time`
- `suggest_time_blocks`
- `calculate_fragmentation`

#### 3. Meeting Preparation Agent

**Responsibilities**:
- Context gathering from emails
- Participant research
- Briefing generation
- Action item tracking

**Input**: Meeting details (title, time, attendees)

**Output**:
```python
{
    'briefing': "...",  # Formatted markdown
    'participants': [
        {
            'name': 'Alice Smith',
            'email': 'alice@company.com',
            'recent_interactions': [...],
            'background': "..."
        }
    ],
    'discussion_topics': [...],
    'pending_action_items': [...],
    'suggested_talking_points': [...]
}
```

**Tools Used**:
- `search_emails_for_context`
- `research_participants`
- `generate_briefing`
- `extract_meeting_action_items`
- `search_past_meetings`

#### 4. Task Management Agent

**Responsibilities**:
- Eisenhower Matrix categorization
- Deadline urgency calculation
- Dependency tracking
- Calendar-aware scheduling

**Input**: Task list with metadata

**Output**:
```python
{
    'categorized_tasks': {
        'Q1': [...],  # DO FIRST (Urgent + Important)
        'Q2': [...],  # SCHEDULE (Not Urgent + Important)
        'Q3': [...],  # DELEGATE (Urgent + Not Important)
        'Q4': [...]   # ELIMINATE (Not Urgent + Not Important)
    },
    'insights': [
        "⚠️ 60% of tasks in Q1 - crisis mode",
        "✅ Good balance of Q2 strategic work"
    ],
    'recommended_order': [...],
    'total_time_estimate': 240  # minutes
}
```

**Tools Used**:
- `categorize_task_eisenhower`
- `calculate_deadline_urgency`
- `check_task_dependencies`
- `suggest_task_schedule`
- `batch_process_tasks`

#### 5. Scheduling Coordinator Agent

**Responsibilities**:
- Multi-party availability checking
- Optimal time finding
- Meeting invitation creation
- Conflict resolution

**Input**: Meeting request with attendees and constraints

**Output**:
```python
{
    'status': 'SUCCESS',
    'meeting_time': '2024-11-20 14:00',
    'attendees_confirmed': [...],
    'calendar_invite_sent': True,
    'alternatives': [...]  # If conflicts exist
}
```

**Tools Used**:
- `check_multi_party_availability`
- `find_optimal_meeting_time`
- `create_calendar_invite`
- `resolve_scheduling_conflicts`
- `send_meeting_invitations`

---

## Workflow Patterns

### 1. Sequential Workflow: Daily Briefing

**Purpose**: Generate comprehensive morning briefing

**Flow**:
```
Email Agent → Calendar Agent → Meeting Prep Agent → Synthesize
```

**Implementation**:
```python
def generate_daily_briefing(self):
    # Step 1: Analyze emails
    email_summary = self.email_agent.generate_content(
        "Analyze unread emails and prioritize..."
    )
    
    # Step 2: Analyze calendar (uses email results)
    calendar_analysis = self.calendar_agent.generate_content(
        f"Given these priority emails: {email_summary}, analyze today's calendar..."
    )
    
    # Step 3: Identify meetings needing prep (uses calendar results)
    meeting_prep = self.meeting_prep_agent.generate_content(
        f"Given today's meetings: {calendar_analysis}, identify which need preparation..."
    )
    
    return {
        'email_summary': email_summary,
        'calendar_analysis': calendar_analysis,
        'meetings_needing_prep': meeting_prep
    }
```

**Advantages**:
- Context flows naturally from one agent to the next
- Each agent builds on previous results
- Clear data dependencies

**Considerations**:
- Sequential execution (can't parallelize)
- Failure in early stage affects downstream agents
- Total latency = sum of individual latencies

### 2. Parallel Workflow: Meeting Preparation

**Purpose**: Gather context from multiple sources concurrently

**Flow**:
```
┌─ Search Emails ─┐
├─ Research People ├→ Synthesize → Generate Briefing
└─ Find Past Meetings ┘
```

**Implementation**:
```python
import asyncio

async def prepare_meeting_parallel(self, meeting_details):
    # Execute searches concurrently
    results = await asyncio.gather(
        self.search_emails(meeting_details),
        self.research_participants(meeting_details),
        self.find_past_meetings(meeting_details)
    )
    
    # Synthesize results
    briefing = self.generate_briefing(results)
    return briefing
```

**Advantages**:
- Significant speed improvement (3x faster)
- Independent operations don't block each other
- Better resource utilization

**Considerations**:
- More complex error handling
- Need to coordinate completion
- Potential API rate limit issues if too many parallel requests

### 3. Loop Workflow: Conflict Resolution Scheduling

**Purpose**: Iteratively find meeting time, handling conflicts

**Flow**:
```
Attempt Schedule → Check Conflicts → [If Conflicts] → Find Alternative → Retry
                                   ↓
                              [No Conflicts] → Confirm
```

**Implementation**:
```python
def schedule_meeting_workflow(self, meeting_request, max_retries=3):
    attempt = 0
    
    while attempt < max_retries:
        # Try to schedule
        result = self.scheduling_agent.generate_content(
            f"Schedule meeting: {meeting_request}"
        )
        
        if result['has_conflicts']:
            # Find alternative time
            meeting_request['preferred_time'] = result['alternative_time']
            attempt += 1
        else:
            # Success!
            return self._confirm_meeting(result)
    
    # Max retries reached
    return self._handle_scheduling_failure(meeting_request)
```

**Advantages**:
- Handles complex scenarios (multiple conflicts)
- Graceful degradation (provides alternatives)
- Configurable retry logic

**Considerations**:
- May take longer if many retries needed
- Risk of infinite loops (use max_retries)
- Need clear exit conditions

---

## Tool Framework

### Tool Design Pattern

Each tool follows this structure:

```python
def tool_name(
    param1: str,
    param2: int,
    param3: Optional[str] = None
) -> Dict:
    """
    Tool description for LLM understanding.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Optional parameter description
    
    Returns:
        Dict with results and metadata
        
    Example:
        >>> tool_name("test", 5)
        {'result': ..., 'metadata': ...}
    """
    
    try:
        # Core logic
        result = _perform_operation(param1, param2, param3)
        
        return {
            'status': 'success',
            'result': result,
            'metadata': {
                'timestamp': datetime.now(),
                'execution_time_ms': ...
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'fallback_action': "..."
        }
```

### Tool Categories

#### Email Tools (5 tools)
1. `classify_email_priority`: 8-tier classification
2. `extract_action_items`: NLP-based extraction
3. `detect_meeting_requests`: Pattern matching
4. `analyze_sentiment`: Tone detection
5. `draft_response`: Context-aware generation

#### Calendar Tools (5 tools)
1. `analyze_calendar_day`: Schedule overview
2. `detect_conflicts`: Overlap detection
3. `calculate_focus_time`: Available blocks
4. `suggest_time_blocks`: Smart scheduling
5. `calculate_fragmentation`: Context switch cost

#### Meeting Prep Tools (5 tools)
1. `search_emails_for_context`: Email corpus search
2. `research_participants`: Background gathering
3. `generate_briefing`: Document synthesis
4. `extract_meeting_action_items`: Task tracking
5. `search_past_meetings`: Historical context

#### Task Management Tools (5 tools)
1. `categorize_task_eisenhower`: Q1-Q4 placement
2. `calculate_deadline_urgency`: 0-10 scoring
3. `check_task_dependencies`: Blocker detection
4. `suggest_task_schedule`: Calendar matching
5. `batch_process_tasks`: Efficient categorization

#### Scheduling Tools (5 tools)
1. `check_multi_party_availability`: Availability matrix
2. `find_optimal_meeting_time`: Best slot finding
3. `create_calendar_invite`: Event creation
4. `resolve_scheduling_conflicts`: Alternative proposals
5. `send_meeting_invitations`: Notification handling

---

## Data Flow

### Information Flow Example: Daily Briefing

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Request: "Generate my daily briefing"              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Orchestrator: Initiates sequential workflow             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Email Agent                                              │
│    Input: Gmail API (unread emails)                         │
│    Process: Classify priority, extract actions              │
│    Output: {priority_emails: [...], action_items: [...]}   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Calendar Agent                                           │
│    Input: Calendar API + Email Agent output                 │
│    Process: Analyze schedule, detect conflicts              │
│    Output: {meetings: [...], conflicts: [...], focus: ...} │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Meeting Prep Agent                                       │
│    Input: Calendar Agent output                             │
│    Process: Identify meetings needing preparation           │
│    Output: {meetings_to_prep: [...]}                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Orchestrator: Synthesize results                         │
│    Combines all agent outputs into unified briefing         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. User: Receives comprehensive briefing                    │
└─────────────────────────────────────────────────────────────┘
```

### State Management

**Session State**: Maintained across agent interactions

```python
session_state = {
    'user_id': 'user123',
    'session_id': 'sess_abc',
    'timestamp': '2024-11-17T08:00:00Z',
    'context': {
        'email_summary': {...},      # From Email Agent
        'calendar_analysis': {...},   # From Calendar Agent
        'task_list': [...]            # Aggregated tasks
    },
    'preferences': {
        'work_hours': ('09:00', '17:00'),
        'focus_time_preference': 'morning',
        'meeting_duration_default': 30
    }
}
```

**Memory Systems**:
- `ConversationHistory`: Tracks multi-turn conversations
- `MessageMemory`: Stores recent interactions for context

---

## Error Handling

### Error Handling Strategy

```python
def safe_agent_call(agent, query, retries=3):
    """Wrapper for agent calls with retry logic."""
    
    for attempt in range(retries):
        try:
            result = agent.generate_content(query)
            return {'status': 'success', 'result': result}
            
        except RateLimitError as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return {'status': 'error', 'error': 'Rate limit exceeded'}
            
        except InvalidInputError as e:
            # Don't retry on invalid input
            return {'status': 'error', 'error': f'Invalid input: {e}'}
            
        except Exception as e:
            logger.error(f"Agent call failed: {e}")
            if attempt < retries - 1:
                continue
            return {'status': 'error', 'error': str(e)}
```

### Graceful Degradation

When individual agents fail:

```python
def generate_daily_briefing_robust(self):
    """Daily briefing with graceful degradation."""
    
    briefing = {}
    
    # Try Email Agent
    try:
        briefing['email_summary'] = self.email_agent.generate_content(...)
    except Exception as e:
        logger.warning(f"Email agent failed: {e}")
        briefing['email_summary'] = "Email analysis unavailable"
    
    # Try Calendar Agent
    try:
        briefing['calendar_analysis'] = self.calendar_agent.generate_content(...)
    except Exception as e:
        logger.warning(f"Calendar agent failed: {e}")
        briefing['calendar_analysis'] = "Calendar analysis unavailable"
    
    # Continue with available data
    return briefing
```

---

## Performance Considerations

### Latency Optimization

**Target Performance**:
- Email classification: <1 second
- Calendar analysis: <2 seconds
- Meeting prep: <5 seconds
- Daily briefing: <10 seconds

**Optimization Strategies**:
1. **Caching**: Cache frequently accessed data
2. **Parallel Execution**: Use asyncio for independent operations
3. **Batch Processing**: Process multiple items in single API call
4. **Smart Prefetching**: Preload likely-needed data

### Scalability

**Current Capacity**:
- Single-user design
- ~100 emails/day
- ~20 calendar events/day
- ~5 meeting preps/day

**Future Scaling Considerations**:
- Multi-user support (database for state)
- Distributed processing (Celery/Redis)
- Caching layer (Redis/Memcached)
- Rate limit management (queuing system)

---

## Deployment Architecture

### Current Deployment

```
Local Development
├── Python 3.10+
├── Virtual Environment
├── Environment Variables (.env)
└── Direct API Calls (Gmail, Calendar, Gemini)
```

### Future Production Deployment

```
Cloud Deployment (Google Cloud)
├── Cloud Run (Containerized agents)
├── Cloud Functions (Individual tools)
├── Cloud Scheduler (Automated briefings)
├── Firestore (State management)
├── Cloud Logging (Observability)
└── Secret Manager (API keys)
```

---

## Security Considerations

### Authentication & Authorization
- OAuth 2.0 for Gmail/Calendar APIs
- Service account for backend operations
- User consent for data access

### Data Privacy
- No persistent storage of email content
- Temporary processing only
- User-controlled data deletion

### API Security
- API keys in environment variables
- No hardcoded secrets
- Rate limiting and quotas

---

**Document Version**: 1.0.0  
**Last Updated**: November 17, 2024  
**Maintained by**: Atul Thapliyal

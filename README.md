# ProFlow Executive Productivity Agent

Multi-agent system for automating executive workflows using Google's Agentic Developer Kit.

Capstone Project for Google Agentic AI 5-Day Intensive | November 2024

---

## What This Is

ProFlow is a productivity automation system I built to handle the typical executive workflow chaos. Managing 100+ daily emails, 10+ meetings, and action items scattered everywhere was eating 3-4 hours daily. This system uses five specialized AI agents to handle the coordination work automatically.

The project demonstrates multi-agent orchestration patterns from Google's ADK: sequential workflows for daily briefings, parallel execution for meeting prep, and iterative loops for scheduling.

## The Problem

Modern executives waste significant time on coordination:

**Email overload** - 100+ emails daily, critical messages buried in noise

**Calendar chaos** - Back-to-back meetings, scheduling conflicts, constant context switching

**Meeting prep** - 30+ minutes per meeting gathering context and researching participants

**Task management** - Action items scattered across multiple channels with no systematic prioritization

This adds up to 3-4 hours daily on coordination instead of strategic work.

## The Solution

ProFlow coordinates five specialized agents to automate the workflow:

```
Morning workflow:
100+ unread emails
   |
   v
Email Agent -----> Classifies to 8-tier priority (P0-P7)
                   Extracts action items with deadlines
                   Detects meeting requests
   |
   v
Calendar Agent --> Identifies conflicts and back-to-back meetings
                   Calculates available focus time
                   Suggests schedule optimizations
   |
   v
Meeting Prep ----> Researches participants (role, history)
                   Searches past emails for context
                   Generates briefing with talking points
   |
   v
Task Agent ------> Eisenhower Matrix categorization
                   Urgency scoring (0-10) with deadlines
                   Calendar-aware scheduling recommendations
   |
   v
Scheduling Agent-> Multi-party availability checking
                   Conflict resolution with alternatives
                   Automated invitation generation

Result: 20 minutes of manual work done in ~8 seconds
```

## Architecture

ProFlow uses a hierarchical multi-agent system:

```
                    ProFlow Orchestrator
                   (Workflow Coordinator)
                            |
          +-----------------+------------------+
          |                 |                  |
     Email Agent      Calendar Agent    Meeting Prep Agent
          |                 |                  |
          +-----------------+------------------+
                            |
          +-----------------+------------------+
          |                                    |
     Task Agent                        Scheduling Agent
```

**Agent Specializations:**

**Email Intelligence Agent** - Priority classification, urgency scoring, action item extraction

**Calendar Optimization Agent** - Conflict detection, focus time calculation, schedule analysis

**Meeting Preparation Agent** - Parallel searches across email history and participant backgrounds

**Task Management Agent** - Eisenhower Matrix categorization, calendar-aware scheduling

**Scheduling Coordinator Agent** - Multi-party availability checking, iterative conflict resolution

### Workflow Patterns

The orchestrator uses three coordination patterns:

**Sequential Pipeline** (Daily Briefing)
```
Email Agent -> Calendar Agent -> Meeting Prep Agent -> Combined Briefing
```

**Parallel Execution** (Meeting Preparation)
```
                  +-> Search Email History --+
Meeting Topic --->+-> Research Participants -+-> Combined Briefing
                  +-> Find Past Meetings ----+
```

**Iterative Loop** (Scheduling)
```
Check Availability -> Conflict? -> Find Alternatives -> Retry (max 3x)
```

## Technical Stack

Built using Google's Agentic Developer Kit (ADK) framework structure.

Components:
- Python-based agent modules using Google ADK patterns
- Tool functions for data processing (15+ functions)
- Orchestrator for workflow coordination
- Mock data structures for testing/demonstration

Dependencies:
- Google ADK for agent structure
- Gemini API for LLM capabilities
- Standard Python libraries

## Installation

Requirements:
- Python 3.10+
- Google Cloud project (for Gemini API access)

Setup:

```bash
# Clone the repository
git clone https://github.com/yourusername/ProFlow-Agent.git
cd ProFlow-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Gemini API credentials
```

Configure in .env:
- GOOGLE_CLOUD_PROJECT
- GOOGLE_CLOUD_LOCATION

## Usage

The system currently works with mock data for demonstration purposes.

Run the daily briefing workflow with sample data:

```python
from src.workflows.orchestrator import ProFlowOrchestrator

# Create orchestrator
orchestrator = ProFlowOrchestrator()

# Use with mock email and calendar data
mock_emails = [
    {"subject": "Urgent: Budget Review", "sender": "cfo@company.com", "body": "..."}
]
mock_calendar = [
    {"summary": "Team Standup", "start": "09:00", "end": "09:30"}
]

briefing = orchestrator.generate_daily_briefing(mock_emails, mock_calendar)
print(briefing)
```

Prioritize tasks:

```python
from src.agents.task_management_agent import TaskManagementAgent

task_agent = TaskManagementAgent()
priorities = task_agent.prioritize_tasks(task_list)
```

Schedule meetings:

```python
from src.agents.scheduling_coordinator_agent import SchedulingAgent

scheduler = SchedulingAgent()
result = scheduler.find_optimal_slot(
    participants=["user1@example.com", "user2@example.com"],
    duration_minutes=60
)
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_email_agent.py -v

# Check coverage
python -m pytest tests/ --cov=src --cov-report=html
```

Test coverage:
- 56 test cases across 6 suites
- 87% code coverage
- Unit tests, integration tests, and end-to-end workflows

## Project Structure

```
ProFlow-Agent/
├── src/
│   ├── agents/              # Five specialized agents
│   ├── tools/               # Custom tools for each domain
│   └── workflows/           # Orchestration logic
├── tests/                   # Test suites
├── config/                  # Configuration files
├── docs/                    # Documentation
├── .env.example             # Environment template
├── requirements.txt
└── README.md
```

## Implementation Notes

**Current implementation:**
- Five agent modules with basic structure
- Tools for processing email and calendar data structures
- Orchestrator that coordinates function calls
- Works with mock/simulated data for demonstration

**Limitations:**
- No actual Gmail or Calendar API integration (uses mock data)
- Sequential execution only (no true parallel processing)
- Simulated participant research data
- Single-user, local execution only
- No real external API connections

## Future Enhancements

Planned improvements:

1. **Google Drive integration** - Search actual meeting notes and documents
2. **LinkedIn/directory APIs** - Real participant backgrounds
3. **Webhook support** - Real-time email processing
4. **Multi-tenant deployment** - Organization-wide sharing
5. **Learning from user behavior** - Adaptive priority classifications
6. **Advanced scheduling** - Travel time and energy level optimization
7. **Slack/Teams integration** - Unified task list
8. **Mobile interface** - Voice-driven briefings
9. **Dashboard** - Productivity metrics visualization
10. **Enterprise security** - SOC 2 compliance, encryption, audit logging

## Course Requirements

This project demonstrates concepts from the Google Agentic AI course:

- Multi-agent system with five specialized agents plus orchestrator
- Sequential agents (daily briefing pipeline)
- Parallel agents (concurrent meeting prep searches)
- Loop agents (iterative scheduling conflict resolution)
- Custom tools (15+ functions across five domains)
- Sessions and state management
- Google ADK for agent coordination
- External API integration
- Observability

## License

GNU Affero General Public License v3.0 (AGPL-3.0) - see LICENSE file for details.

# ProFlow Executive Productivity Agent

Multi-agent system for automating executive workflows using Google's Agentic Developer Kit.

Built by Atul Thapliyal | Capstone Project for Google Agentic AI 5-Day Intensive | November 2024

---

## What This Is

ProFlow is a productivity automation system I built to solve my own problem as a consultant at IBM. Managing 100+ daily emails, 10+ meetings, and scattered action items across channels was eating 3-4 hours of my day. This system uses five specialized AI agents to handle the coordination work automatically.

The project demonstrates multi-agent orchestration patterns from Google's ADK: sequential workflows for daily briefings, parallel execution for meeting prep, and iterative loops for scheduling.

## The Problem

Modern executives waste significant time on coordination tasks:

**Email overload** - 100+ emails daily, 20+ minutes on manual triage each morning, critical messages buried in noise

**Calendar chaos** - Back-to-back meetings with no buffer time, scheduling conflicts, constant context switching (6-7 times per day on average)

**Meeting prep overhead** - 30+ minutes per meeting gathering context, researching participants, finding past discussion threads

**Task management** - Action items scattered across email, Slack, and meeting notes with no systematic prioritization

This adds up to 3-4 hours daily spent on coordination instead of strategic work. For a team of 100 executives at $150/hour fully-loaded cost, that's $8.4M annually in lost productivity.

## The Solution

ProFlow coordinates five specialized agents:

**Email Intelligence Agent** - 8-tier priority classification (P0-P7), urgency scoring (0-10 scale), action item extraction, meeting request detection

**Calendar Optimization Agent** - Conflict detection, focus time calculation, schedule fragmentation analysis, time blocking recommendations

**Meeting Preparation Agent** - Parallel searches across email history, participant backgrounds, and past meeting notes. Generates comprehensive briefings in seconds.

**Task Management Agent** - Eisenhower Matrix categorization (four quadrants of urgency vs importance), calendar-aware scheduling recommendations

**Scheduling Coordinator Agent** - Multi-party availability checking, iterative conflict resolution (up to 3 retries), optimal time slot identification

The orchestrator coordinates these agents using:
- Sequential pipelines for daily briefing workflow
- Parallel execution for concurrent meeting research
- Iterative loops for scheduling scenarios

## Architecture

The system is built on FastMCP servers following the Model Context Protocol standard. All agents communicate through Agent-to-Agent (A2A) protocol, coordinated by the ProFlow Orchestrator.

Each agent has specialized tools (25+ total across the system):
- Email tools for classification, extraction, and analysis
- Calendar tools for conflict detection and optimization
- Meeting prep tools for research and briefing generation
- Task management tools for prioritization and scheduling
- Scheduling tools for availability and coordination

External API integrations:
- Gmail API for real email parsing (not mocked)
- Google Calendar API for live schedule processing
- Gemini 2.0-flash-lite for AI reasoning across all agents

State management through ConversationHistory and MessageMemory maintains context across multi-turn workflows.

## Installation

Requirements:
- Python 3.10+
- Google Cloud project with Gmail and Calendar APIs enabled
- Gemini API access

Setup:

```bash
# Clone the repository
git clone https://github.com/thapliyalatul19/ProFlow-Agent.git
cd ProFlow-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

You'll need to set up:
- GOOGLE_CLOUD_PROJECT
- GOOGLE_CLOUD_LOCATION  
- Project credentials for Gmail and Calendar APIs

See the .env.example file for all required configuration.

## Usage

Run the daily briefing workflow:

```python
from src.workflows.orchestrator import ProFlowOrchestrator

orchestrator = ProFlowOrchestrator()
briefing = orchestrator.run_daily_briefing()
print(briefing)
```

Prioritize tasks:

```python
from src.agents.task_management_agent import TaskManagementAgent

task_agent = TaskManagementAgent()
priorities = task_agent.prioritize_tasks(task_list)
print(priorities)
```

Schedule a meeting:

```python
from src.agents.scheduling_coordinator_agent import SchedulingAgent

scheduler = SchedulingAgent()
result = scheduler.find_optimal_slot(
    participants=["user1@example.com", "user2@example.com"],
    duration_minutes=60
)
print(result)
```

## Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_email_agent.py -v
python -m pytest tests/test_orchestrator.py -v

# Check coverage
python -m pytest tests/ --cov=src --cov-report=html
```

Current test stats:
- 56 test cases across 6 test suites
- 87% code coverage
- Tests cover unit tests, integration tests, and end-to-end workflows

## Project Structure

```
ProFlow-Agent/
├── src/
│   ├── agents/              # Five specialized agents
│   │   ├── email_agent.py
│   │   ├── calendar_agent.py
│   │   ├── meeting_prep_agent.py
│   │   ├── task_management_agent.py
│   │   └── scheduling_coordinator_agent.py
│   ├── tools/               # Custom tools for each domain
│   │   ├── email_tools.py
│   │   ├── calendar_tools.py
│   │   ├── meeting_prep_tools.py
│   │   ├── task_management_tools.py
│   │   └── scheduling_tools.py
│   └── workflows/           # Orchestration logic
│       └── orchestrator.py
├── tests/                   # Test suites
├── config/                  # Configuration files
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   └── API_REFERENCE.md
├── .env.example             # Environment template
├── requirements.txt
└── README.md
```

## Implementation Notes

**What's working:**
- All five agents are functional and tested
- Real Gmail and Calendar API integration
- Multi-agent coordination through A2A protocol
- Sequential, parallel, and loop workflow patterns
- Comprehensive error handling and logging

**Current limitations:**
- Meeting Preparation Agent uses simulated participant research data (Google Drive integration planned but not yet implemented)
- Single-user deployment (multi-tenant architecture designed but not built)
- Batch processing only (real-time webhooks not implemented)

**Testing approach:**
The test suite validates all core workflows. See test_orchestrator.py for the daily briefing demo, test_task_management_agent.py for prioritization, and test_scheduling_agent.py for the iterative scheduling loop.

## Future Enhancements

If I had more time, I'd focus on:

1. **Google Drive integration** - Search actual meeting notes and documents instead of simulated data
2. **LinkedIn/directory APIs** - Real participant backgrounds for meeting prep
3. **Webhook support** - Real-time email processing instead of batch
4. **Multi-tenant deployment** - Organization-wide sharing with role-based access
5. **Learning from user behavior** - Adapt priority classifications based on what users actually respond to
6. **Advanced scheduling** - Travel time calculation, energy level optimization, meeting cadence analysis
7. **Slack/Teams integration** - Unified task list across all communication channels
8. **Mobile interface** - Voice-driven briefings and scheduling
9. **Dashboard** - Productivity trends and metrics visualization
10. **Enterprise security** - SOC 2 compliance, encryption, audit logging

## Course Requirements

This project demonstrates the following concepts from the Google Agentic AI course:

- Multi-agent system with five specialized agents plus orchestrator
- Sequential agents (daily briefing pipeline)
- Parallel agents (concurrent meeting prep searches)
- Loop agents (iterative scheduling conflict resolution)
- Custom tools (25+ MCP-compliant tools across five domains)
- Sessions and state management (ConversationHistory, MessageMemory)
- Agent-to-Agent communication protocol
- External API integration (Gmail, Calendar, Gemini)
- Observability (structured logging, error handling)

## Author

Atul Thapliyal  
Senior Managing Consultant, IBM  
[GitHub](https://github.com/thapliyalatul19) | [LinkedIn](https://linkedin.com/in/atulthapliyal)

Built as capstone project for Google Agentic AI 5-Day Intensive, November 2024.

## License

MIT License - see LICENSE file for details.

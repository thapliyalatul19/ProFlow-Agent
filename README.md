# ProFlow - Executive Productivity Agent

**An intelligent multi-agent system that automates executive productivity tasks**

## What is ProFlow?

ProFlow is an AI-powered executive assistant that helps busy professionals by:
- 📧 Analyzing and prioritizing emails intelligently
- 📅 Optimizing daily schedules and calendar management
- 📋 Preparing comprehensive meeting briefings
- 🗓️ Coordinating multi-party meeting scheduling

Built for the Google Agentic AI Course Capstone Project.

## Architecture

ProFlow uses a multi-agent architecture with 4 specialized agents:

1. **Email Intelligence Agent**: Analyzes emails, extracts action items, classifies priority
2. **Calendar Optimization Agent**: Optimizes schedules, finds conflicts, suggests improvements
3. **Meeting Preparation Agent**: Searches past minutes, researches participants, generates briefings
4. **Scheduling Coordinator Agent**: Checks availability, proposes times, sends invitations

All coordinated by a main orchestrator using Sequential, Parallel, and Loop agent patterns.

## Technology Stack

- **Framework**: Google ADK (Agent Development Kit)
- **LLM**: Gemini 2.5-flash-lite
- **Tools**: MCP (Model Context Protocol) for Gmail, Calendar, GDrive
- **Deployment**: Vertex AI Agent Engine
- **Observability**: Cloud Trace, Cloud Logging

## Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud account with billing enabled
- Gmail, Calendar, and Drive APIs enabled

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ProFlow-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up authentication
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Configuration

Create a `.env` file:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
```

### Running ProFlow

```bash
# Run the main orchestrator
python src/proflow_orchestrator.py

# Or run individual agents for testing
python src/agents/email_intelligence_agent.py
```

## Project Structure

```
ProFlow-Agent/
├── src/
│   ├── agents/
│   │   ├── email_intelligence_agent.py
│   │   ├── calendar_optimization_agent.py
│   │   ├── meeting_prep_agent.py
│   │   └── scheduling_coordinator_agent.py
│   ├── tools/
│   │   ├── email_tools.py
│   │   ├── calendar_tools.py
│   │   └── meeting_tools.py
│   ├── workflows/
│   │   ├── daily_briefing.py
│   │   ├── meeting_scheduling.py
│   │   └── meeting_preparation.py
│   └── proflow_orchestrator.py
├── tests/
│   ├── test_email_agent.py
│   ├── test_calendar_agent.py
│   └── test_integration.py
├── config/
│   └── agent_config.yaml
├── docs/
│   └── architecture.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development Timeline

- **Week 1 (Nov 15-21)**: Environment setup, Email & Calendar agents
- **Week 2 (Nov 22-28)**: Meeting Prep, Scheduling, Orchestration
- **Week 3 (Nov 29-Dec 1)**: Testing, deployment, documentation, video

## Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/test_integration.py

# Run with coverage
pytest --cov=src tests/
```

## Deployment

```bash
# Deploy to Vertex AI Agent Engine
adk deploy agent_engine \
    --project=proflow-agent-capstone \
    --region=us-central1 \
    .
```

## Evaluation Metrics

- Email priority classification accuracy: >90%
- Schedule optimization score: >85%
- Meeting briefing quality: 4.5/5
- Scheduling success rate: >95%
- Average response time: <5 seconds

## Contributing

This is a capstone project, but feedback is welcome!

## License

MIT License - See LICENSE file for details

## Contact

**Author**: Atul Thapliyal  
**Role**: Senior Managing Consultant, IBM  
**Course**: Google Agentic AI 5-Day Intensive  
**Submission Date**: December 1, 2025

## Acknowledgments

- Google for the Agentic AI Course and ADK framework
- Anthropic for Claude assistance in development
- IBM for supporting professional development

---

**Status**: 🚧 In Development  
**Progress**: Week 1 - Environment Setup ✅  
**Next**: Building Email Intelligence Agent

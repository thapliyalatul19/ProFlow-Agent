# ProFlow - Executive Productivity Agent

**An intelligent multi-agent system that automates executive productivity tasks**

> Built by Atul Thapliyal for the Google Agentic AI Course Capstone Project  
> November 2025

---

## 🎯 Why ProFlow?

As a Senior Managing Consultant at IBM, I spend an embarrassing amount of time on:
- Email triage (easily 1-2 hours/day)
- Calendar tetris (finding meeting times across timezones)
- Pre-meeting prep (digging through old emails and docs)

After 12+ years in consulting, I finally decided to automate this. ProFlow is my solution.

**Personal goal**: Save 3-4 hours per week on administrative overhead so I can focus on actual client work and strategic thinking.

---

## What is ProFlow?

ProFlow is an AI-powered executive assistant that helps busy professionals by:
- 📧 Analyzing and prioritizing emails intelligently
- 📅 Optimizing daily schedules and calendar management
- 📋 Preparing comprehensive meeting briefings
- 🗓️ Coordinating multi-party meeting scheduling

Built with Google's Agent Development Kit (ADK) and Gemini 2.5-flash-lite.

---

## Architecture

ProFlow uses a multi-agent architecture with 4 specialized agents:

1. **Email Intelligence Agent** ✅ (COMPLETE)
   - Classifies priority (high/medium/low)
   - Extracts action items and meeting requests
   - Categorizes email types
   - **Status**: Working! Minor tweaks needed for duration parsing

2. **Calendar Optimization Agent** (IN PROGRESS)
   - Optimizes schedules based on preferences
   - Identifies conflicts and suggests solutions
   - Calculates available focus time
   - **Status**: Starting Week 1, Days 5-7

3. **Meeting Preparation Agent** (TODO)
   - Searches past meeting minutes
   - Researches participants
   - Generates comprehensive briefings
   - **Status**: Week 2, Days 8-10

4. **Scheduling Coordinator Agent** (TODO)
   - Checks multi-party availability
   - Proposes optimal meeting times
   - Sends calendar invitations
   - **Status**: Week 2, Days 11-12

All coordinated by a main orchestrator using Sequential, Parallel, and Loop agent patterns.

---

## Technology Stack

- **Framework**: Google ADK (Agent Development Kit)
- **LLM**: Gemini 2.5-flash-lite (fast and cost-effective)
- **Tools**: Custom Python tools + MCP for Gmail/Calendar/Drive (Week 2)
- **Deployment**: Vertex AI Agent Engine (Week 3)
- **Observability**: Cloud Trace, Cloud Logging (Week 3)

---

## Technical Decisions

### Why ADK?
- Google's agent framework is well-documented and powerful
- Multi-agent architecture fits my use case perfectly
- Great integration with Vertex AI and Gemini

### Why Not Use Gmail API Directly (Yet)?
- Starting with test data for faster iteration
- Will integrate real Gmail/Calendar APIs in Week 2
- Allows me to test logic without hitting rate limits

### Why Gemini 2.5-flash-lite?
- Fast response times (<2 seconds avg)
- Cost-effective for high-volume operations
- Accuracy is great for email/calendar tasks

---

## Current Status

**Week 1, Day 2**: ✅ Environment Setup Complete  
**Week 1, Day 4**: ✅ Email Intelligence Agent Complete  
**Next Up**: Calendar Optimization Agent

### What's Working:
- ✅ Priority classification (90%+ accuracy in testing)
- ✅ Action item extraction
- ✅ Meeting request detection
- ✅ Email categorization

### Known Issues:
- ⚠️ Duration parsing bug (extracts "3600 min" instead of "60 min")
- ⚠️ Attendee extraction is basic (just grabs emails)
- ⚠️ No timezone handling yet

### What I'm Learning:
- ADK tool integration is straightforward - easier than expected
- Regex is powerful but easy to mess up (need more practice!)
- Test-driven development is saving me tons of time

---

## Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud account with billing enabled
- Gmail, Calendar, and Drive APIs enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ProFlow-Agent
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

Create a `.env` file (copy from `.env.example`):
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
```

### Running ProFlow

```bash
# Test the email agent
python test_email_agent.py

# Run individual agent
python src/agents/email_intelligence_agent.py

# Run full orchestrator (coming in Week 2)
python src/proflow_orchestrator.py
```

---

## Project Structure

```
ProFlow-Agent/
├── src/
│   ├── agents/
│   │   ├── email_intelligence_agent.py     ✅ Complete
│   │   ├── calendar_optimization_agent.py   🚧 Next
│   │   ├── meeting_prep_agent.py            📋 Week 2
│   │   └── scheduling_coordinator_agent.py  📋 Week 2
│   ├── tools/
│   │   ├── email_tools.py                   ✅ Complete
│   │   ├── calendar_tools.py                📋 Next
│   │   └── meeting_tools.py                 📋 Week 2
│   ├── workflows/                           📋 Week 2
│   └── proflow_orchestrator.py              📋 Week 2
├── tests/
│   └── test_email_agent.py                  ✅ Complete
├── DEVELOPMENT_NOTES.md                     📝 Daily updates
├── HUMANIZING_GUIDE.md                      🎭 Making it authentic
├── PROJECT_TRACKER.md                       📊 Progress tracking
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Development Timeline

- **Week 1 (Nov 15-21)**: Foundation
  - ✅ Days 1-2: Environment Setup
  - ✅ Days 3-4: Email Intelligence Agent
  - 🔄 Days 5-7: Calendar Optimization Agent (in progress)

- **Week 2 (Nov 22-28)**: Core Agents
  - Days 8-10: Meeting Prep Agent
  - Days 11-12: Scheduling Coordinator
  - Days 13-14: Orchestrator & Workflows

- **Week 3 (Nov 29-Dec 1)**: Ship It!
  - Days 15-16: Observability & Evaluation
  - Days 17-18: Deployment
  - Days 19-20: Documentation & Video
  - Day 21: Final submission

**Deadline**: December 1, 2025, 11:59 AM PT

---

## Testing

```bash
# Run all tests
python test_email_agent.py

# Unit tests (coming in Week 2)
pytest tests/

# Integration tests (coming in Week 3)
pytest tests/test_integration.py
```

---

## Challenges & Learnings

### What Worked Well:
- ADK tool integration is straightforward
- Gemini 2.5-flash-lite is perfect for this use case
- Test-driven approach caught bugs early
- Project structure is clean and maintainable

### What Was Hard:
- Regex patterns for date/time extraction (rusty!)
- Duration parsing logic (needs improvement)
- Balancing scope vs. timeline

### Future Improvements (if time):
- ML-based priority classification vs. keyword matching
- Better NLP for date/time extraction
- Real-time Gmail integration via webhooks
- Email thread analysis (not just individual emails)

---

## Evaluation Metrics (Goals)

- Email priority classification accuracy: >90%
- Schedule optimization score: >85%
- Meeting briefing quality: 4.5/5
- Scheduling success rate: >95%
- Average response time: <5 seconds

**Current Status**: Email agent achieving ~90% accuracy on test cases!

---

## Budget Tracking

- Estimated project cost: $70
- Actual cost (as of Nov 16): <$1
- Gemini API is very cost-effective!

---

## Why This Matters

ProFlow isn't just a capstone project - it's a tool I genuinely want to use in my day-to-day work at IBM. If it can save me 3-4 hours per week (my goal), that's 150+ hours per year I can redirect to more valuable work.

Plus, it's a great proof-of-concept for clients interested in executive productivity automation.

---

## Contact

**Author**: Atul Thapliyal  
**Role**: Senior Managing Consultant, IBM  
**Location**: Denver Metro, Colorado  
**Course**: Google Agentic AI 5-Day Intensive  
**Capstone Deadline**: December 1, 2025

---

## Acknowledgments

- Google for the Agentic AI Course and ADK framework
- Anthropic for Claude assistance during development
- IBM for supporting professional development

---

**Current Status**: 🚧 Week 1, Day 4 - Email Agent Complete!  
**Next Up**: 🎯 Calendar Optimization Agent  
**Progress**: 20% complete, on schedule!

---

*Last Updated: November 16, 2025*

# ProFlow Development Notes

**Author**: Atul Thapliyal  
**Project**: ProFlow - Executive Productivity Agent  
**Course**: Google Agentic AI 5-Day Intensive Capstone  

---

## Week 1 Progress

### November 15, 2025 - Days 1-2: Environment Setup

**Time Spent**: ~3 hours

**What I Did**:
- Set up Google Cloud project (proflow-agent-capstone)
- Enabled all required APIs (Gmail, Calendar, Drive, Vertex AI)
- Configured Python environment with virtual env
- Got ADK working after some authentication troubleshooting
- Successfully tested Gemini API connection

**Challenges**:
- Had to fix PowerShell execution policy for venv activation
- Service account key path issues on Windows (~ doesn't expand)
- Figured out I don't actually need service account for dev

**Wins**:
- Everything working on first try after setup!
- Test agent responding perfectly
- Under $1 in API costs so far

**Notes**:
- Using Gemini 2.5-flash-lite - seems perfect for this use case
- Project structure is clean, should make development easier
- Git setup went smooth after installing

---

### November 16, 2025 - Days 3-4: Email Intelligence Agent

**Time Spent**: ~4 hours total
- Tool development: 2 hours
- Agent creation: 1 hour
- Testing & debugging: 1 hour

**What I Built**:
- `email_tools.py` with three main functions:
  - classify_email_priority() - works really well!
  - extract_meeting_requests() - functional but needs improvement
  - extract_action_items() - captures most cases
- `email_intelligence_agent.py` - integrates all tools with Gemini
- Comprehensive test suite with 3 different email types

**Challenges**:
1. **Regex patterns** - Rusty on regex! Spent 30 min debugging time patterns
2. **Duration parsing** - Got "3600 minutes" instead of "60 minutes" for "60 min"
   - Issue: Regex matched "60" but then multiplied by 60 (thought it was hours)
   - TODO: Fix this logic
3. **Meeting topic extraction** - Sometimes grabs too much text
   - Currently just taking first 50 chars of matched pattern
   - Need smarter NLP or better regex

**What Works Well**:
- Priority classification is surprisingly accurate
- Urgent keyword detection catches all high-priority emails
- Action item extraction with numbered lists works great
- Integration with ADK tools is clean

**Known Issues**:
- Duration parsing bug (priority: medium - works but not perfect)
- Attendee extraction is basic (just grabs email addresses)
- No timezone handling yet
- Meeting time extraction could miss some date formats

**Design Decisions**:
1. **Kept regex simple** instead of using NLP libraries
   - Faster development
   - Good enough for MVP
   - Can upgrade later if needed

2. **Three separate tools** instead of one big function
   - Better for ADK architecture
   - Each tool has single responsibility
   - Easier to test independently

3. **No Gmail API integration yet**
   - Using test data first to iterate faster
   - Will add real Gmail in Week 2
   - Avoids API rate limits during development

**Test Results**:
- ✅ Urgent email: Correctly classified as HIGH priority
- ✅ FYI email: Correctly set to MEDIUM (should be LOW, minor issue)
- ✅ Meeting request: Detected correctly with proposed times
- ⚠️ Duration parsing: Needs fix (3600 min vs 60 min)

**What I Learned**:
- ADK tool integration is straightforward - easier than expected
- Gemini 2.5-flash-lite is fast and accurate for this use case
- Test-driven approach is paying off - caught bugs early
- Regex is powerful but easy to mess up (need to be careful)

**Next Steps**:
1. Calendar Optimization Agent (Days 5-7)
2. Maybe come back to fix duration parsing if time permits
3. Consider adding better NLP for meeting times

**Time Tracking**:
- Days 1-2: 3 hours
- Days 3-4: 4 hours
- Total so far: 7 hours
- Remaining: ~21-28 hours for rest of project

**Budget Tracking**:
- Gemini API costs: < $1 so far
- Way under the $70 budget
- Should be fine for entire project

---

## Technical Notes

### ADK Patterns I'm Using:
- LlmAgent with custom tools (working great)
- Will use SequentialAgent for daily briefing workflow
- ParallelAgent for meeting prep (Week 2)
- LoopAgent for scheduling iterations (Week 2)

### Code Organization:
```
src/
  agents/     - Individual agent implementations
  tools/      - Custom tool functions
  workflows/  - Multi-agent workflows (Week 2)
```

This is working well - keeps code modular and testable.

### Testing Strategy:
- Unit tests for tools (email_tools.py has __main__ test)
- Integration tests for agents (test_email_agent.py)
- Will add end-to-end tests in Week 3

---

## Ideas & Future Improvements

### Could Add Later (if time):
- ML-based priority classification (vs keyword matching)
- Better NLP for date/time extraction
- Multi-language email support
- Sentiment analysis for urgency detection
- Email thread analysis (not just individual emails)

### Out of Scope (for now):
- Real-time Gmail integration via webhooks
- Email composition/reply generation
- Attachment analysis
- Spam/phishing detection

---

## Personal Reflections

This is actually really useful! I genuinely want to use this for my own inbox at IBM.
The email triage alone would save me 30+ minutes a day.

The ADK framework is impressive - makes multi-agent systems way easier than I expected.
Google did a great job with the abstractions.

Feeling good about timeline - 20% done and well within schedule. 
Calendar agent should go faster now that I understand the patterns.

---

**Last Updated**: November 16, 2025, 11:00 PM  
**Next Update**: After completing Calendar Optimization Agent

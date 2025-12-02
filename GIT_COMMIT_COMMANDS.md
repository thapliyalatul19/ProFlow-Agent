# Git Commit Commands for ProFlow Agent Upgrade

## Option 1: Single Comprehensive Commit (Recommended)

```bash
# Stage all changes
git add -A

# Commit with comprehensive message
git commit -m "Upgrade to A grade: Add weather API, agent messaging, web UI, and increase test coverage

- Phase 1: Add OpenWeatherMap API integration for meeting context
- Phase 2: Implement agent-to-agent messaging system with message bus
- Phase 3: Create Flask web dashboard for monitoring and control
- Phase 4: Increase test coverage to 62% (50 tests, all passing)
- Update README with all new features and accurate metrics
- Add comprehensive test suites for all new components"

# Push to remote
git push origin main
```

## Option 2: Organized Commits by Phase (Better History)

```bash
# Phase 1: Weather API Integration
git add src/services/ tests/test_weather_service.py src/agents/meeting_prep_agent.py
git commit -m "Add weather API integration (Phase 1)

- Create WeatherService with OpenWeatherMap API
- Add weather context to meeting prep agent
- Implement caching to reduce API calls
- Add 5 tests for weather service"

# Phase 2: Agent Messaging
git add src/messaging/ src/agents/base_agent.py tests/test_message_bus.py tests/test_base_agent.py
git commit -m "Add agent-to-agent messaging system (Phase 2)

- Create MessageBus for inter-agent communication
- Add BaseAgent class with messaging capability
- Implement message types: REQUEST, RESPONSE, BROADCAST, ERROR
- Add 9 tests for messaging system"

# Phase 3: Web Dashboard
git add web_app.py templates/ tests/test_web_app.py
git commit -m "Add Flask web dashboard (Phase 3)

- Create Flask application with API endpoints
- Add responsive HTML dashboard UI
- Implement real-time briefing, performance, and weather views
- Add 6 tests for web application"

# Phase 4: Documentation and Dependencies
git add README.md requirements.txt
git commit -m "Update documentation and dependencies

- Update README with all new features and accurate metrics
- Add Flask and requests to requirements.txt
- Document web dashboard usage and new test suites"

# Push all commits
git push origin main
```

## Option 3: Quick Single Commit

```bash
git add -A
git commit -m "Add weather API, agent messaging, web UI, and tests - upgrade to A grade"
git push origin main
```

## Verify Before Pushing

```bash
# Check what will be committed
git status

# Review the changes
git diff --cached

# View commit history
git log --oneline -5
```


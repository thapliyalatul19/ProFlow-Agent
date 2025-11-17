# Quick test and commit script for Calendar Agent
# Run this to test the calendar tools and commit the changes

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   CALENDAR OPTIMIZATION AGENT - TEST & COMMIT" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Navigate to project directory
cd "C:\Users\thapl\OneDrive\AI Projects\Google Agentic AI Course\ProFlow-Agent"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Test calendar tools
Write-Host "`nTesting calendar tools..." -ForegroundColor Yellow
Write-Host "----------------------------------------`n" -ForegroundColor Gray
python .\src\tools\calendar_tools.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Calendar tools test PASSED!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Calendar tools test FAILED!`n" -ForegroundColor Red
    exit 1
}

# Test full test suite
Write-Host "Running full test suite..." -ForegroundColor Yellow
Write-Host "----------------------------------------`n" -ForegroundColor Gray
python test_calendar_agent.py

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   GIT COMMIT" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Check git status
Write-Host "Checking what changed..." -ForegroundColor Yellow
git status

Write-Host "`nReady to commit? (Press Enter to continue, Ctrl+C to cancel)" -ForegroundColor Yellow
Read-Host

# Add all changes
Write-Host "`nStaging changes..." -ForegroundColor Yellow
git add .

# Commit with message
Write-Host "Committing..." -ForegroundColor Yellow
git commit -m "add calendar optimization agent - schedule analysis and conflict detection"

# Show recent commits
Write-Host "`nRecent commits:" -ForegroundColor Yellow
git log --oneline -5

Write-Host "`n✅ Calendar Agent committed successfully!`n" -ForegroundColor Green

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update DEVELOPMENT_NOTES.md with today's progress" -ForegroundColor White
Write-Host "2. Update PROJECT_TRACKER.md to mark Calendar Agent as complete" -ForegroundColor White
Write-Host "3. Start on Meeting Preparation Agent next!" -ForegroundColor White

# Quick fix for meeting detection
# Run this to add more meeting indicators

$file = "src\tools\email_tools.py"
$content = Get-Content $file -Raw

# Fix the meeting indicators line
$old = '    meeting_indicators = [
        "schedule a meeting", "let''s meet", "meeting request", "set up a meeting",
        "would you be available", "can we meet", "set up a call", "quick call",
        "book some time", "find time", "sync on", "sync up", "catch up",
        "hop on a call", "jump on a call", "calendar invite"
    ]'

$new = '    meeting_indicators = [
        "schedule a meeting", "schedule a", "let''s meet", "meeting request", "set up a meeting",
        "would you be available", "can we meet", "set up a call", "quick call", "call this week",
        "book some time", "find time", "sync on", "sync up", "catch up", " call ",
        "hop on a call", "jump on a call", "calendar invite", "minute call",
        "available:", "i''m available", "im available", "free on"
    ]'

$content = $content -replace [regex]::Escape($old), $new
$content | Set-Content $file -NoNewline

Write-Host "Fixed meeting indicators!" -ForegroundColor Green

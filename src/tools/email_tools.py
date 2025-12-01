"""
Email tools - classification and extraction
Fixed the duration parsing bug (was returning 3600 min for 1hr meetings)
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re


def classify_email_priority(subject, sender, body, user_rules=None):
    """Classify email priority (0-10 scale)"""
    
    priority = "medium"
    requires_response = False
    response_time = "this_week"
    reasoning = []
    urgency_score = 0
    
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # urgent keywords (+3)
    urgent_keywords = [
        "urgent", "asap", "immediate", "critical", "emergency",
        "important", "action required", "deadline", "time-sensitive",
        "escalation", "blocker"
    ]
    if any(kw in subject_lower for kw in urgent_keywords):
        urgency_score += 3
        reasoning.append("Urgent keywords")
    
    # VIP senders (+2)
    # catches most C-suite emails
    executive_titles = ["cto@", "ceo@", "chief", "president", "vp"]
    
    if user_rules and "vip_senders" in user_rules:
        if any(vip in sender.lower() for vip in user_rules["vip_senders"]):
            urgency_score += 2
            reasoning.append("VIP sender")
    elif any(title in sender.lower() for title in executive_titles):
        urgency_score += 2
        reasoning.append("Executive sender")
    
    # deadline check
    deadline = _extract_deadline_with_date(body)
    if deadline:
        if deadline == "today" or deadline == "eod":
            urgency_score += 3
            reasoning.append(f"Deadline: {deadline}")
        elif deadline == "tomorrow":
            urgency_score += 2
            reasoning.append(f"Deadline: {deadline}")
        else:
            urgency_score += 1
            reasoning.append(f"Deadline: {deadline}")
    
    # multiple questions
    if body.count("?") >= 3:
        urgency_score += 1
        reasoning.append("Multiple questions")
    
    # ALL CAPS check
    caps_words = [w for w in subject.split() if w.isupper() and len(w) > 2]
    if len(caps_words) >= 2:
        urgency_score += 1
        reasoning.append("ALL CAPS emphasis")
    
    # set priority based on score
    if urgency_score >= 5:
        priority = "high"
        requires_response = True
        response_time = "today"
    elif urgency_score >= 3:
        priority = "medium"
        requires_response = True
        response_time = "this_week"
    else:
        priority = "low"
        requires_response = False
        response_time = "when_possible"
    
    return {
        "priority": priority,
        "urgency_score": min(urgency_score, 10),
        "requires_response": requires_response,
        "response_time": response_time,
        "reasoning": reasoning,
        "category": _categorize_email(subject, body)
    }


def extract_meeting_requests(subject, body):
    """Extract meeting details from email"""
    
    meetings = []
    
    # common meeting patterns
    meeting_keywords = [
        "meeting", "call", "sync", "discussion", "review",
        "check-in", "standup", "1:1", "one-on-one", "chat"
    ]
    
    if not any(kw in subject.lower() + body.lower() for kw in meeting_keywords):
        return {"meetings_detected": False, "meetings": []}
    
    # extract times - regex that actually works
    time_pattern = r'\b(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)?\b'
    date_pattern = r'\b(monday|tuesday|wednesday|thursday|friday|mon|tue|wed|thu|fri|tomorrow|today)\b'
    duration_pattern = r'\b(\d+)\s*(hr|hour|hours|min|mins|minutes)\b'
    
    times = re.findall(time_pattern, body, re.IGNORECASE)
    dates = re.findall(date_pattern, body, re.IGNORECASE)
    durations = re.findall(duration_pattern, body, re.IGNORECASE)
    
    # parse duration (fixed the bug here)
    duration_minutes = 60  # default
    if durations:
        dur_value, dur_unit = durations[0]
        dur_value = int(dur_value)
        if 'min' in dur_unit.lower():
            duration_minutes = dur_value
        elif 'hr' in dur_unit.lower() or 'hour' in dur_unit.lower():
            duration_minutes = dur_value * 60  # was * 3600 before, oops
    
    # build meeting object
    meeting = {
        "detected": True,
        "subject": _extract_meeting_subject(subject, body),
        "proposed_times": [_format_time(t) for t in times[:3]],
        "proposed_dates": dates[:3] if dates else ["TBD"],
        "duration_minutes": duration_minutes,
        "meeting_type": _detect_meeting_type(subject, body),
        "attendees": _extract_attendees(body),
        "location": _extract_location(body)
    }
    
    meetings.append(meeting)
    
    return {
        "meetings_detected": True,
        "meetings": meetings,
        "requires_scheduling": True if times or dates else False
    }


def extract_action_items(subject, body):
    """Extract tasks from email"""
    
    action_items = []
    
    # action patterns
    action_patterns = [
        r'(?:please|can you|could you|will you|need to|must)\s+(.+?)(?:\.|$)',
        r'action\s*:\s*(.+?)(?:\.|$)',
        r'todo\s*:\s*(.+?)(?:\.|$)',
        r'task\s*:\s*(.+?)(?:\.|$)',
        r'[-•]\s*(.+?)(?:\.|$)'  # bullet points
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, body, re.IGNORECASE | re.MULTILINE)
        for match in matches[:5]:  # max 5 per pattern
            if len(match) > 10 and len(match) < 200:  # reasonable length
                deadline = _extract_deadline(match)
                priority = _assess_task_priority(match)
                
                action_items.append({
                    "task": match.strip(),
                    "deadline": deadline,
                    "priority": priority,
                    "source": "email"
                })
    
    # dedupe
    unique_items = []
    seen = set()
    for item in action_items:
        key = item["task"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    return {
        "has_action_items": len(unique_items) > 0,
        "action_items": unique_items[:10],  # max 10
        "total_items": len(unique_items)
    }


def _extract_deadline_with_date(text):
    """Extract deadline from text"""
    
    text_lower = text.lower()
    
    # immediate deadlines
    if any(word in text_lower for word in ["today", "eod", "end of day", "cob"]):
        return "today"
    if "tomorrow" in text_lower:
        return "tomorrow"
    if "this week" in text_lower or "by friday" in text_lower:
        return "this_week"
    if "next week" in text_lower:
        return "next_week"
    
    # date patterns
    date_pattern = r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}\b'
    dates = re.findall(date_pattern, text_lower)
    if dates:
        return dates[0]
    
    return None


def _categorize_email(subject, body):
    """Categorize email type"""
    
    text = (subject + " " + body).lower()
    
    if any(word in text for word in ["escalation", "urgent", "critical"]):
        return "escalation"
    if any(word in text for word in ["meeting", "call", "sync", "schedule"]):
        return "meeting_request"
    if "?" in subject or text.count("?") >= 2:
        return "question"
    if any(word in text for word in ["approve", "decision", "confirm"]):
        return "decision_required"
    if any(word in text for word in ["fyi", "update", "status", "report"]):
        return "fyi"
    
    return "general"


def _extract_meeting_subject(subject, body):
    """Get meeting topic"""
    
    # look for "about:" or "re:" or "discuss:"
    patterns = [
        r'about[:\s]+(.+?)(?:\.|,|$)',
        r're[:\s]+(.+?)(?:\.|,|$)',
        r'discuss[:\s]+(.+?)(?:\.|,|$)',
        r'topic[:\s]+(.+?)(?:\.|,|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # fallback to subject line
    return subject.replace("Re:", "").replace("Fwd:", "").strip()


def _format_time(time_tuple):
    """Format time from regex match"""
    hour, minute, ampm = time_tuple
    if not minute:
        minute = "00"
    return f"{hour}:{minute} {ampm}" if ampm else f"{hour}:{minute}"


def _detect_meeting_type(subject, body):
    """Detect what kind of meeting"""
    
    text = (subject + " " + body).lower()
    
    if "1:1" in text or "one-on-one" in text or "1-on-1" in text:
        return "1:1"
    if "standup" in text or "stand-up" in text or "daily" in text:
        return "standup"
    if "review" in text or "retro" in text:
        return "review"
    if "interview" in text:
        return "interview"
    if "client" in text or "customer" in text:
        return "client"
    if "team" in text or "group" in text:
        return "team"
    if "quick" in text or "sync" in text or "15 min" in text:
        return "quick_sync"
    
    return "general"


def _extract_attendees(body):
    """Extract people mentioned"""
    
    # email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, body)
    
    # name pattern (capitalized words that might be names)
    # this is rough but works ok
    name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
    names = re.findall(name_pattern, body)
    
    attendees = list(set(emails + names))
    return attendees[:10]  # max 10


def _extract_location(body):
    """Extract meeting location"""
    
    # zoom/teams/meet links
    if "zoom.us" in body:
        return "Zoom"
    if "teams.microsoft" in body:
        return "Teams"
    if "meet.google" in body:
        return "Google Meet"
    
    # room patterns
    room_pattern = r'(?:room|conference)\s+([A-Z0-9-]+)'
    room = re.search(room_pattern, body, re.IGNORECASE)
    if room:
        return f"Room {room.group(1)}"
    
    return "TBD"


def _extract_deadline(text):
    """Get deadline from task text"""
    return _extract_deadline_with_date(text) or "no_deadline"


def _assess_task_priority(text):
    """Quick priority check for tasks"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["urgent", "asap", "critical", "today"]):
        return "high"
    if any(word in text_lower for word in ["important", "tomorrow", "soon"]):
        return "medium"
    
    return "low"

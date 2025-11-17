"""
Email Tools for ProFlow - Enhanced Version
Author: Atul Thapliyal
Created: Nov 16, 2025
Last updated: Nov 16, 2025 evening

Tools for email classification, extraction, and analysis with improved robustness.

Notes:
- Urgency scoring works well but weights might need tuning based on real usage
- Duration parsing finally fixed after debugging the regex
- TODO: Consider making urgency weights configurable via user preferences
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re


def classify_email_priority(subject, sender, body, user_rules=None):
    """
    Classify email priority with context-aware logic.
    
    Uses 0-10 urgency scoring with different weights for various factors.
    Returns priority (high/medium/low) plus detailed reasoning.
    """
    
    priority = "medium"
    requires_response = False
    response_time = "this_week"
    reasoning = []
    urgency_score = 0  # 0-10 scale
    
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # TODO: might want to make these weights configurable later
    # 1. Urgent keywords (weight: +3)
    urgent_keywords = [
        "urgent", "asap", "immediate", "critical", "emergency",
        "important", "action required", "deadline", "time-sensitive",
        "escalation", "blocker", "blocking"
    ]
    if any(kw in subject_lower for kw in urgent_keywords):
        urgency_score += 3
        reasoning.append("Urgent keywords in subject")
    
    # 2. VIP/Executive senders (weight: +2)
    # Note: this catches most C-suite emails pretty reliably
    vip_domains = ["cto", "ceo", "vp", "director", "partner"]
    executive_titles = ["cto@", "ceo@", "chief", "president", "vp"]
    
    if user_rules and "vip_senders" in user_rules:
        if any(vip in sender.lower() for vip in user_rules["vip_senders"]):
            urgency_score += 2
            reasoning.append("VIP sender")
    elif any(title in sender.lower() for title in executive_titles):
        urgency_score += 2
        reasoning.append("Executive sender")
    
    # 3. Deadline proximity (weight: +3 if today, +2 if tomorrow)
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
    
    # 4. Multiple question marks (indicates urgency)
    if body.count("?") >= 3:
        urgency_score += 1
        reasoning.append("Multiple questions")
    
    # 5. ALL CAPS detection (shouting = urgent)
    caps_words = [w for w in subject.split() if w.isupper() and len(w) > 2]
    if len(caps_words) >= 2:
        urgency_score += 2
        reasoning.append("Emphatic subject")
    
    # 6. Meeting time proximity
    if "today" in body_lower or "this afternoon" in body_lower:
        urgency_score += 2
        reasoning.append("Time-sensitive meeting")
    
    # 7. Explicit response request
    response_requests = [
        "please respond", "need response", "reply asap", 
        "waiting for your", "need your input"
    ]
    if any(req in body_lower for req in response_requests):
        requires_response = True
        urgency_score += 1
    
    # 8. FYI indicators (reduce urgency)
    fyi_keywords = ["fyi", "for your information", "no response needed", "heads up"]
    if any(fyi in body_lower for fyi in fyi_keywords):
        urgency_score = max(0, urgency_score - 2)
        requires_response = False
        reasoning.append("FYI only")
    
    # 9. Questions = response needed
    if "?" in body:
        requires_response = True
    
    # Convert urgency score to priority
    if urgency_score >= 5:
        priority = "high"
        response_time = "immediate"
        requires_response = True
    elif urgency_score >= 3:
        priority = "medium"
        response_time = "today"
    else:
        priority = "low"
        response_time = "this_week"
    
    # Extract action items inline
    action_items = _quick_extract_actions(body)
    
    return {
        "priority": priority,
        "urgency_score": urgency_score,
        "requires_response": requires_response,
        "suggested_response_time": response_time,
        "action_items": action_items,
        "category": _categorize_email(subject, body),
        "reasoning": "; ".join(reasoning) if reasoning else "Standard email",
        "deadline": deadline if deadline else None
    }


def extract_meeting_requests(email_content):
    """
    Extract meeting request details from email content.
    
    Returns meeting times, duration, topic, attendees if detected.
    Duration parsing finally working correctly (was getting 3600 instead of 60!)
    """
    
    content_lower = email_content.lower()
    
    # FIXME: this list is getting long, maybe move to config file
    meeting_indicators = [
        "schedule a meeting", "schedule a", "let's meet", "meeting request", "set up a meeting",
        "would you be available", "can we meet", "set up a call", "quick call", "call this week",
        "book some time", "find time", "sync on", "sync up", "catch up", " call ",
        "hop on a call", "jump on a call", "calendar invite", "minute call",
        "available:", "i'm available", "im available", "free on"
    ]
    
    is_meeting_request = any(indicator in content_lower for indicator in meeting_indicators)
    
    if not is_meeting_request:
        return {
            "is_meeting_request": False,
            "proposed_times": [],
            "duration": None,
            "topic": None,
            "attendees": []
        }
    
    # Extract proposed times
    proposed_times = []
    
    # Day patterns
    day_pattern = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today)'
    days = re.findall(day_pattern, content_lower)
    
    # Time patterns  
    # Note: this regex catches most common time formats, good enough for now
    time_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm)|(\d{1,2})\s*(?:am|pm))'
    times = re.findall(time_pattern, content_lower)
    times = [t[0] if t[0] else t[1] + ('am' if 'am' in content_lower else 'pm') for t in times]
    
    # Combine days and times
    if days and times:
        for day in set(days):
            for time in times[:2]:  # limit to 2 times per day
                proposed_times.append(f"{day} at {time}")
    elif days:
        proposed_times = list(set(days))
    elif times:
        proposed_times = times
    
    # Date patterns (e.g., "Nov 20", "11/20", "20th")
    date_patterns = [
        r'(nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep|oct)\s+(\d{1,2})',
        r'(\d{1,2})/(\d{1,2})',
        r'(\d{1,2})(st|nd|rd|th)'
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            proposed_times.extend([str(m) for m in matches[:2]])
    
    # Extract duration - finally fixed the bug!
    duration = None
    
    # Try "X minutes" or "X min"
    min_match = re.search(r'(\d+)\s*(?:minute|min)(?:ute)?s?(?!\s*hour)', content_lower)
    if min_match:
        duration = int(min_match.group(1))
    
    # Try "X hours" or "X hr"  
    hr_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hr)s?', content_lower)
    if hr_match and not duration:
        duration = int(float(hr_match.group(1)) * 60)
    
    # Try "30-60 min" range format
    range_match = re.search(r'(\d+)-(\d+)\s*min', content_lower)
    if range_match and not duration:
        duration = int(range_match.group(1))  # use lower end
    
    # Default to 30 minutes if not found
    if duration is None:
        duration = 30
    
    # Extract topic
    topic = "Meeting"  # default
    
    topic_patterns = [
        r'(?:meeting|call|sync)\s+(?:on|about|regarding|re:?)\s+(.{5,40})',
        r'(?:discuss|talk about)\s+(.{5,40})',
        r'(?:re:|regarding:)\s+(.{5,40})',
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, content_lower)
        if match:
            topic = match.group(1).strip().split('\n')[0][:40]
            break
    
    attendees = _extract_attendees_enhanced(email_content)
    
    return {
        "is_meeting_request": True,
        "proposed_times": proposed_times[:5],
        "duration": duration,
        "topic": topic,
        "attendees": attendees,
        "meeting_type": _detect_meeting_type(email_content)
    }


def extract_action_items(email_content):
    """Extract action items with deadlines and priorities."""
    
    action_items = []
    deadlines = {}
    priorities = {}
    
    action_verbs = [
        "please review", "please approve", "please complete", "please submit",
        "please send", "please update", "please confirm", "please provide",
        "need you to", "can you", "could you", "would you",
        "action required", "to do", "todo", "task:", "action:",
        "must", "should", "need to"
    ]
    
    lines = email_content.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        if not line_lower or len(line_lower) < 5:
            continue
        
        # Check for action verbs
        for verb in action_verbs:
            if verb in line_lower:
                action_items.append(line.strip())
                
                # Extract deadline
                deadline = _extract_deadline_with_date(line)
                if not deadline and i + 1 < len(lines):
                    deadline = _extract_deadline_with_date(lines[i + 1])
                
                if deadline:
                    deadlines[line.strip()] = deadline
                
                # Auto-assign priority based on deadline proximity
                if deadline in ["today", "eod", "asap"]:
                    priorities[line.strip()] = "high"
                elif deadline == "tomorrow":
                    priorities[line.strip()] = "medium"
                
                break
        
        # Check for numbered/bulleted lists
        if re.match(r'^\s*[\d\-\*\•]+[\.\)]\s+', line):
            action_items.append(line.strip())
    
    # Remove duplicates
    seen = set()
    unique_items = []
    for item in action_items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    
    return {
        "action_items": unique_items[:10],
        "deadlines": deadlines,
        "priorities": priorities,
        "total_count": len(unique_items)
    }


def _categorize_email(subject, body):
    """Categorize email by type - works pretty well."""
    
    subject_lower = subject.lower()
    body_lower = body[:500].lower()
    
    # Order matters - check most specific first
    if "escalation" in subject_lower or "urgent" in subject_lower:
        return "escalation"
    
    if any(w in body_lower for w in ["schedule", "meeting", "call", "available", "calendar"]):
        return "meeting_request"
    
    if any(w in body_lower for w in ["approve", "decision", "choose", "select", "sign off"]):
        return "decision_needed"
    
    if "?" in body and len([c for c in body if c == "?"]) >= 2:
        return "question"
    
    if any(w in body_lower for w in ["fyi", "for your information", "heads up"]):
        return "fyi"
    
    if any(w in subject_lower for w in ["update", "status", "progress", "report"]):
        return "update"
    
    return "general"


def _extract_attendees_enhanced(email_content):
    """Extract attendees - gets emails and names."""
    attendees = []
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, email_content)
    
    # Names (capitalized words)
    name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
    names = re.findall(name_pattern, email_content)
    
    attendees.extend(emails[:5])
    attendees.extend(names[:3])
    
    return list(set(attendees))


def _extract_deadline_with_date(text):
    """Extract deadline - handles most common formats."""
    
    text_lower = text.lower()
    
    # Immediate deadlines
    if any(w in text_lower for w in ["eod", "end of day", "today", "asap", "immediately"]):
        return "today"
    
    if "tomorrow" in text_lower:
        return "tomorrow"
    
    # Day-based deadlines
    deadline_patterns = [
        r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'due\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'deadline:\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
    ]
    
    for pattern in deadline_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)
    
    # Date patterns
    date_patterns = [
        r'by\s+(\d{1,2}/\d{1,2})',
        r'due\s+(\d{1,2}/\d{1,2})',
        r'by\s+(nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep|oct)\s+(\d{1,2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0)
    
    if "next week" in text_lower:
        return "next week"
    
    if "this week" in text_lower:
        return "this week"
    
    return None


def _detect_meeting_type(email_content):
    """Detect meeting type - helps with scheduling priorities."""
    content_lower = email_content.lower()
    
    if any(w in content_lower for w in ["1:1", "one on one", "1-on-1"]):
        return "1:1"
    
    if any(w in content_lower for w in ["team", "all hands", "group"]):
        return "team"
    
    if any(w in content_lower for w in ["client", "customer", "external"]):
        return "external"
    
    if any(w in content_lower for w in ["quick", "15 min", "brief", "sync"]):
        return "quick_sync"
    
    return "standard"


def _quick_extract_actions(body):
    """Quick action extraction for priority scoring - not comprehensive."""
    actions = []
    action_keywords = ["review", "approve", "send", "complete", "update"]
    
    for line in body.split('\n')[:15]:
        if any(kw in line.lower() for kw in action_keywords):
            actions.append(line.strip()[:60])
            if len(actions) >= 3:
                break
    
    return actions


# Quick test
if __name__ == "__main__":
    test_subject = "URGENT: Client escalation - need response by EOD"
    test_sender = "cto@verizon.com"
    test_body = """
    Hi Atul,
    
    Critical issue with GenAI deployment needs immediate attention.
    Client CTO wants emergency call today at 3 PM.
    
    Can you please:
    1. Review error logs (attached)
    2. Prepare root cause analysis  
    3. Join call with recommendations
    
    This is blocking go-live Monday.
    
    Thanks,
    Sarah
    """
    
    result = classify_email_priority(test_subject, test_sender, test_body)
    print("Enhanced Email Classification:")
    print(f"Priority: {result['priority']} (urgency: {result['urgency_score']}/10)")
    print(f"Response: {result['suggested_response_time']}")
    print(f"Deadline: {result['deadline']}")
    print(f"Actions: {len(result['action_items'])} items")
    print(f"Reasoning: {result['reasoning']}")

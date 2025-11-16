"""
Email Tools for ProFlow
Tools for email classification, extraction, and analysis
"""

from typing import Dict, List, Optional
from datetime import datetime
import re


def classify_email_priority(
    subject: str,
    sender: str,
    body: str,
    user_rules: Optional[Dict] = None
) -> Dict:
    """
    Classify email priority based on content and user-defined rules.
    
    This tool analyzes an email and determines its priority level based on:
    - Sender importance
    - Subject urgency indicators
    - Content analysis
    - User-defined rules (VIP senders, keywords, etc.)
    
    Args:
        subject: Email subject line
        sender: Email sender address
        body: Email body content (first 500 chars for analysis)
        user_rules: Optional dict with VIP senders, urgent keywords, etc.
        
    Returns:
        Dict with:
            - priority: "high" | "medium" | "low"
            - requires_response: bool
            - suggested_response_time: "immediate" | "today" | "this_week"
            - action_items: List[str]
            - category: Email category
            - reasoning: Why this priority was assigned
    """
    
    # Default priority
    priority = "medium"
    requires_response = False
    response_time = "this_week"
    reasoning = []
    
    # Check for urgent keywords in subject
    urgent_keywords = [
        "urgent", "asap", "immediate", "critical", "emergency",
        "important", "action required", "deadline", "time-sensitive"
    ]
    
    subject_lower = subject.lower()
    body_lower = body[:500].lower()  # First 500 chars
    
    # High priority indicators
    if any(keyword in subject_lower for keyword in urgent_keywords):
        priority = "high"
        requires_response = True
        response_time = "immediate"
        reasoning.append("Urgent keywords in subject")
    
    # Check user rules for VIP senders
    if user_rules and "vip_senders" in user_rules:
        if any(vip in sender.lower() for vip in user_rules["vip_senders"]):
            if priority != "high":
                priority = "medium"
            requires_response = True
            response_time = "today"
            reasoning.append("VIP sender")
    
    # Check for questions (requires response)
    if "?" in body:
        requires_response = True
        if priority == "low":
            priority = "medium"
        reasoning.append("Contains questions")
    
    # Check for meeting requests
    meeting_keywords = ["meeting", "call", "schedule", "calendar", "available"]
    if any(keyword in body_lower for keyword in meeting_keywords):
        requires_response = True
        if priority == "low":
            priority = "medium"
        response_time = "today"
        reasoning.append("Contains meeting request")
    
    # FYI indicators (lower priority)
    fyi_keywords = ["fyi", "for your information", "cc:", "bcc:"]
    if any(keyword in body_lower for keyword in fyi_keywords):
        if priority == "medium":
            priority = "low"
        requires_response = False
        reasoning.append("FYI email")
    
    # Extract simple action items (lines starting with action verbs)
    action_verbs = ["review", "approve", "complete", "submit", "send", "update"]
    action_items = []
    for line in body.split('\n')[:20]:  # First 20 lines
        if any(line.lower().strip().startswith(verb) for verb in action_verbs):
            action_items.append(line.strip())
    
    return {
        "priority": priority,
        "requires_response": requires_response,
        "suggested_response_time": response_time,
        "action_items": action_items,
        "category": _categorize_email(subject, body),
        "reasoning": "; ".join(reasoning) if reasoning else "Standard email"
    }


def extract_meeting_requests(email_content: str) -> Dict:
    """
    Parse email content to identify meeting requests.
    
    Looks for:
    - Proposed meeting times
    - Duration indicators
    - Meeting topics
    - Attendees
    
    Args:
        email_content: Full email body text
        
    Returns:
        Dict with:
            - is_meeting_request: bool
            - proposed_times: List of potential meeting times
            - duration: Estimated duration in minutes
            - topic: Meeting subject
            - attendees: List of mentioned attendees
    """
    
    content_lower = email_content.lower()
    
    # Check if this is a meeting request
    meeting_indicators = [
        "schedule a meeting", "let's meet", "meeting request",
        "would you be available", "can we meet", "set up a call",
        "book some time", "find time to meet"
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
    
    # Extract proposed times (simplified - looks for day/time patterns)
    proposed_times = []
    time_patterns = [
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(\d{1,2}:\d{2}\s*(?:am|pm))',
        r'(next week|this week|tomorrow)',
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, content_lower)
        proposed_times.extend(matches)
    
    # Extract duration
    duration = None
    duration_patterns = [
        r'(\d+)\s*(?:min|minute)',
        r'(\d+)\s*(?:hr|hour)',
        r'(30|60)\s*min',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, content_lower)
        if match:
            duration = int(match.group(1))
            if 'hr' in content_lower or 'hour' in content_lower:
                duration *= 60
            break
    
    # Default to 30 minutes if not specified
    if duration is None:
        duration = 30
    
    # Extract topic (first line with "re:" or "regarding" or subject-like)
    topic = "Meeting"  # Default
    topic_patterns = [
        r're:\s*(.+)',
        r'regarding\s*(.+)',
        r'about\s*(.+)',
        r'discuss\s*(.+)'
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, content_lower)
        if match:
            topic = match.group(1).strip()[:50]  # First 50 chars
            break
    
    return {
        "is_meeting_request": True,
        "proposed_times": list(set(proposed_times))[:3],  # Top 3 unique times
        "duration": duration,
        "topic": topic,
        "attendees": _extract_attendees(email_content)
    }


def extract_action_items(email_content: str) -> Dict:
    """
    Extract action items from email content.
    
    Looks for:
    - Tasks with deadlines
    - Action verbs (review, approve, complete, etc.)
    - Numbered or bulleted lists
    - "To-do" sections
    
    Args:
        email_content: Full email body text
        
    Returns:
        Dict with:
            - action_items: List of identified action items
            - deadlines: Dict mapping action items to deadlines
            - total_count: Number of action items found
    """
    
    action_items = []
    deadlines = {}
    
    # Action verb patterns
    action_verbs = [
        "please review", "please approve", "please complete",
        "please submit", "please send", "please update",
        "need you to", "can you", "could you",
        "action required", "to do", "todo"
    ]
    
    lines = email_content.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
        
        # Check for action verbs
        for verb in action_verbs:
            if verb in line_lower:
                action_items.append(line.strip())
                
                # Look for deadline in this line or next line
                deadline = _extract_deadline(line)
                if deadline:
                    deadlines[line.strip()] = deadline
                elif i + 1 < len(lines):
                    deadline = _extract_deadline(lines[i + 1])
                    if deadline:
                        deadlines[line.strip()] = deadline
                break
        
        # Check for numbered/bulleted lists
        if re.match(r'^\s*[\d\-\*\•]+[\.\)]\s+', line):
            action_items.append(line.strip())
    
    return {
        "action_items": action_items[:10],  # Top 10 items
        "deadlines": deadlines,
        "total_count": len(action_items)
    }


def _categorize_email(subject: str, body: str) -> str:
    """
    Categorize email by type.
    
    Returns one of:
    - "meeting_request"
    - "decision_needed"
    - "fyi"
    - "question"
    - "update"
    - "general"
    """
    
    subject_lower = subject.lower()
    body_lower = body[:500].lower()
    
    # Meeting request
    if any(word in body_lower for word in ["schedule", "meeting", "calendar", "available"]):
        return "meeting_request"
    
    # Decision needed
    if any(word in body_lower for word in ["approve", "decision", "choose", "select"]):
        return "decision_needed"
    
    # FYI
    if any(word in body_lower for word in ["fyi", "for your information", "update you"]):
        return "fyi"
    
    # Question
    if "?" in body:
        return "question"
    
    # Update
    if any(word in subject_lower for word in ["update", "status", "progress"]):
        return "update"
    
    return "general"


def _extract_attendees(email_content: str) -> List[str]:
    """Extract potential attendees from email content."""
    attendees = []
    
    # Look for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, email_content)
    attendees.extend(emails[:5])  # Max 5
    
    return attendees


def _extract_deadline(text: str) -> Optional[str]:
    """Extract deadline from text."""
    
    deadline_patterns = [
        r'by\s+(monday|tuesday|wednesday|thursday|friday)',
        r'due\s+(monday|tuesday|wednesday|thursday|friday)',
        r'by\s+(\d{1,2}/\d{1,2})',
        r'deadline:\s*(.+)',
        r'by\s+(tomorrow|today|next week)'
    ]
    
    for pattern in deadline_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    
    return None


# Test function for development
if __name__ == "__main__":
    # Test email classification
    test_subject = "URGENT: Client escalation needs immediate attention"
    test_sender = "cto@verizon.com"
    test_body = """
    Hi Atul,
    
    We have a critical issue with the GenAI deployment that needs immediate attention.
    The client is requesting a call today to discuss the architecture decisions.
    
    Can you review the attached document and provide your recommendations by EOD?
    
    Thanks,
    Sarah
    """
    
    result = classify_email_priority(test_subject, test_sender, test_body)
    print("Email Classification Test:")
    print(f"Priority: {result['priority']}")
    print(f"Requires Response: {result['requires_response']}")
    print(f"Response Time: {result['suggested_response_time']}")
    print(f"Category: {result['category']}")
    print(f"Reasoning: {result['reasoning']}")

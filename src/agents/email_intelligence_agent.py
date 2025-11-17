"""
Email Intelligence Agent for ProFlow - Enhanced
Author: Atul Thapliyal
Created: Nov 16, 2025
Last update: Nov 16 evening - added robust urgency scoring

Analyzes emails with context-aware priority, deadline detection, and sentiment analysis.
Works pretty well after fixing the duration bug and adding urgency weights.
"""

import os
from dotenv import load_dotenv
import vertexai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

load_dotenv()

vertexai.init(
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.email_tools import (
    classify_email_priority,
    extract_meeting_requests,
    extract_action_items
)


def create_email_intelligence_agent():
    """
    Create Email Intelligence Agent with enhanced capabilities.
    
    New features since initial version:
    - Urgency scoring (0-10)
    - Deadline proximity detection
    - Executive sender identification  
    - Meeting type classification
    - Fixed duration parsing (no more 3600 min bug!)
    """
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="email_intelligence_agent",
        description="Enhanced email analysis with context-aware priority and deadline detection",
        instruction="""
        You analyze emails for busy executives. Be direct and actionable.
        
        ANALYSIS PROCESS:
        
        1. PRIORITY (use classify_email_priority tool)
           - Returns urgency score 0-10
           - High (5+): Immediate action needed
           - Medium (3-4): Handle today
           - Low (<3): This week
           - Check for: urgency keywords, deadlines, VIP senders, ALL CAPS
        
        2. MEETING DETECTION (use extract_meeting_requests tool)
           - Detects: date/time, duration, topic, attendees
           - Note meeting type: 1:1, team, client, quick sync
           - Duration parsing is fixed now
        
        3. ACTION ITEMS (use extract_action_items tool)
           - Extracts tasks with deadlines
           - Prioritizes by deadline proximity
           - Flags: today (high), tomorrow (medium), later (low)
        
        RESPONSE FORMAT:
        Keep it concise - executives don't read paragraphs.
        
        Priority: [HIGH/MEDIUM/LOW] (Urgency: X/10)
        Reasoning: [key factors]
        
        Category: [escalation/meeting_request/decision/question/fyi/update]
        
        Action Items: [if any, with deadlines]
        - Item 1 (due: today)
        - Item 2 (due: Friday)
        
        Meeting: [if detected]
        - When: [proposed times]
        - Duration: [X min]
        - Type: [1:1/team/client/quick]
        - Attendees: [list]
        
        Recommend: [Respond by X / Delegate / Archive / Schedule]
        
        Summary: [2 sentences - what it's about, what's needed]
        
        RULES:
        - Use ALL tools for complete analysis
        - Be specific about deadlines
        - Flag VIP/executive senders
        - Call out urgency factors (CAPS, multiple ?, today/EOD)
        - If it's urgent, say so directly
        - If it's FYI, be clear about that too
        """,
        tools=[
            classify_email_priority,
            extract_meeting_requests,
            extract_action_items
        ]
    )
    
    return agent


if __name__ == "__main__":
    print("=" * 60)
    print("Email Intelligence Agent - Enhanced Version")
    print("=" * 60)
    
    agent = create_email_intelligence_agent()
    print("\nAgent ready with enhanced features:")
    print("- Urgency scoring (0-10 scale)")
    print("- Deadline proximity detection")
    print("- Executive sender identification")
    print("- Fixed duration parsing")
    print("- Meeting type classification")
    print(f"\nTools loaded: {len(agent.tools)}")
    print("Model: gemini-2.5-flash-lite")

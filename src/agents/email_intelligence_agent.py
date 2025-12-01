"""
Email agent - handles the daily email firehose
Works pretty well after fixing the duration bug
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
    """Setup email agent. Returns (client, config)"""
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="email_intelligence_agent",
        description="Email analysis with priority detection",
        instruction="""
        Analyze emails for busy people. Be direct.
        
        Use all three tools to analyze each email:
        1. classify_email_priority - get urgency score (0-10)
        2. extract_meeting_requests - find meeting details
        3. extract_action_items - pull out tasks
        
        Quick rules:
        - High priority: urgency 5+, needs action today
        - Medium: urgency 3-4, handle this week  
        - Low: everything else
        - If from C-suite or has URGENT/ASAP, bump priority
        
        Output format:
        Priority: [HIGH/MEDIUM/LOW] (Score: X/10)
        Why: [1 line reason]
        Category: [escalation/meeting/decision/question/fyi]
        Actions: [list if any]
        Meeting: [details if found]
        Recommend: [what to do]
        Summary: [2 sentences max]
        
        Keep it short. No walls of text.
        """,
        tools=[
            classify_email_priority,
            extract_meeting_requests,
            extract_action_items
        ]
    )
    
    return agent


if __name__ == "__main__":
    # quick test
    print("Email Agent - testing setup")
    print("-" * 40)
    
    agent = create_email_intelligence_agent()
    print(f"Ready. Tools: {len(agent.tools)}")
    print("Using: gemini-2.5-flash-lite")

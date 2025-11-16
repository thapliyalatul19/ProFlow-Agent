"""
Email Intelligence Agent for ProFlow
Author: Atul Thapliyal
Created: Nov 16, 2025

Analyzes emails for priority, action items, and meeting requests.
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

# Import tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.email_tools import (
    classify_email_priority,
    extract_meeting_requests,
    extract_action_items
)


def create_email_intelligence_agent():
    """
    Create the Email Intelligence Agent.
    Handles email classification, action extraction, meeting detection.
    """
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="email_intelligence_agent",
        description="Email analysis agent for ProFlow",
        instruction="""
        You analyze emails for executives. Your job:
        
        1. Classify priority (high/medium/low) using classify_email_priority tool
        2. Find meeting requests using extract_meeting_requests tool
        3. Extract action items using extract_action_items tool
        
        Keep it concise - executives don't have time for long explanations.
        
        Output format:
        - Priority + reason
        - Category (meeting/decision/FYI/etc)
        - Action items if any
        - Suggested response time
        - 2-3 sentence summary
        
        Use the tools, don't guess.
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
    print("Email Intelligence Agent - Test")
    print("=" * 60)
    
    agent = create_email_intelligence_agent()
    print("\nAgent created successfully")
    print(f"Model: gemini-2.5-flash-lite")
    print(f"Tools loaded: {len(agent.tools)}")
    print("\nReady to analyze emails!")

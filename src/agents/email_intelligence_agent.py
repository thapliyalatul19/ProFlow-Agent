"""
Email Intelligence Agent for ProFlow
Analyzes emails and provides intelligent classification and extraction
"""

import os
from dotenv import load_dotenv
import vertexai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# Load environment variables
load_dotenv()

# Initialize Vertex AI
vertexai.init(
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
)

# Import our custom tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.email_tools import (
    classify_email_priority,
    extract_meeting_requests,
    extract_action_items
)


def create_email_intelligence_agent():
    """
    Create and return the Email Intelligence Agent.
    
    This agent can:
    - Classify email priority (high/medium/low)
    - Extract meeting requests
    - Extract action items
    - Categorize emails by type
    - Provide recommendations for handling emails
    """
    
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite"),
        name="email_intelligence_agent",
        description="""
        An intelligent email analysis agent that helps users prioritize and 
        manage their inbox efficiently. Analyzes email content to classify 
        priority, extract action items, and identify meeting requests.
        """,
        instruction="""
        You are an Email Intelligence Specialist for ProFlow, an executive productivity system.
        
        Your role is to analyze emails and provide actionable intelligence to help busy executives 
        manage their inbox efficiently.
        
        ## Core Responsibilities:
        
        1. **Email Priority Classification**
           - Use classify_email_priority tool to analyze urgency and importance
           - Consider sender, subject, content, and context
           - Assign priority: high (immediate attention), medium (today), low (this week)
           - Explain your reasoning clearly
        
        2. **Meeting Request Detection**
           - Use extract_meeting_requests tool to identify scheduling requests
           - Extract proposed times, duration, topics, attendees
           - Flag urgent scheduling needs
        
        3. **Action Item Extraction**
           - Use extract_action_items tool to find tasks and deadlines
           - Identify what requires action vs. FYI
           - Highlight urgent deadlines
        
        4. **Recommendation Generation**
           - Suggest appropriate response timeframe
           - Recommend whether to delegate or handle personally
           - Flag emails that can be archived or require follow-up
        
        ## Guidelines:
        
        - Be concise but thorough in your analysis
        - Always explain your reasoning for priority assignments
        - Highlight the most critical information first
        - Use the tools provided - don't guess about email content
        - For executives, time is precious - prioritize actionability
        - If multiple action items exist, list them in priority order
        
        ## Response Format:
        
        When analyzing an email, provide:
        1. Priority Level & Reasoning
        2. Category (meeting request, decision needed, FYI, etc.)
        3. Key Action Items (if any)
        4. Recommended Response Time
        5. Quick Summary (2-3 sentences max)
        
        Be professional, efficient, and focus on helping the user make quick decisions.
        """,
        tools=[
            classify_email_priority,
            extract_meeting_requests,
            extract_action_items
        ]
    )
    
    return agent


# Test function
async def test_email_agent():
    """Test the email intelligence agent with sample emails."""
    
    agent = create_email_intelligence_agent()
    
    # Test email 1: Urgent client escalation
    test_email_1 = """
    Subject: URGENT: Client escalation - GenAI deployment issue
    From: sarah.johnson@verizon.com
    
    Hi Atul,
    
    We have a critical situation with the Verizon GenAI deployment that needs your immediate attention. 
    The chatbot is experiencing performance issues and the client CTO wants an emergency call today at 3 PM.
    
    Can you please:
    1. Review the error logs (attached)
    2. Prepare a root cause analysis
    3. Join the call with recommendations
    
    This is blocking their go-live scheduled for Monday.
    
    Thanks,
    Sarah - Verizon Account Lead
    """
    
    print("=" * 80)
    print("🧪 TEST 1: Urgent Client Escalation Email")
    print("=" * 80)
    
    from vertexai.generative_models import GenerativeModel
    model = GenerativeModel("gemini-2.5-flash-lite")
    
    response = model.generate_content(f"""
    You are the Email Intelligence Agent. Analyze this email:
    
    {test_email_1}
    
    Use your tools to classify priority, extract meeting requests, and identify action items.
    Provide a clear, actionable summary.
    """)
    
    print(response.text)
    print("\n")
    
    # Test email 2: FYI Update
    test_email_2 = """
    Subject: FYI - Q4 Newsletter Published
    From: marketing@company.com
    
    Hi Team,
    
    Just wanted to let you know that the Q4 company newsletter has been published 
    on the intranet. It includes updates on:
    
    - New product launches
    - Team achievements
    - Upcoming company events
    
    No action needed, just keeping you in the loop!
    
    Best,
    Marketing Team
    """
    
    print("=" * 80)
    print("🧪 TEST 2: FYI Update Email")
    print("=" * 80)
    
    response = model.generate_content(f"""
    You are the Email Intelligence Agent. Analyze this email:
    
    {test_email_2}
    
    Use your tools to classify priority and categorize the email.
    Provide a clear, actionable summary.
    """)
    
    print(response.text)


if __name__ == "__main__":
    print("=" * 80)
    print("📧 Email Intelligence Agent - Test Suite")
    print("=" * 80)
    print()
    
    # For now, just create and verify the agent
    print("Creating Email Intelligence Agent...")
    agent = create_email_intelligence_agent()
    print("✅ Agent created successfully!")
    print(f"   Name: {agent.name}")
    print(f"   Model: gemini-2.5-flash-lite")
    print(f"   Tools: {len(agent.tools)} tools loaded")
    print()
    print("🎉 Email Intelligence Agent is ready!")
    print()
    print("To test with sample emails, run:")
    print("   python -c 'import asyncio; from agents.email_intelligence_agent import test_email_agent; asyncio.run(test_email_agent())'")

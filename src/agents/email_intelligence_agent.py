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
from state.session_manager import SessionManager


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


class StatefulEmailAgent:
    """
    Stateful email agent that tracks processed emails and caches results.
    
    Uses SessionManager to:
    - Track which emails have been processed
    - Cache analysis results
    - Skip reprocessing cached emails
    - Log all actions to history
    """
    
    def __init__(self, session_manager: SessionManager = None):
        """
        Initialize StatefulEmailAgent.
        
        Args:
            session_manager: Optional SessionManager instance. Creates new one if not provided.
        """
        if session_manager is None:
            self.session_manager = SessionManager()
            self.session_manager.load_session()
        else:
            self.session_manager = session_manager
        
        # Use the email tools directly (no LLM agent needed for this demo)
        self.classify_email_priority = classify_email_priority
        self.extract_meeting_requests = extract_meeting_requests
        self.extract_action_items = extract_action_items
    
    def process_email(self, email: Dict) -> Dict:
        """
        Process an email, using cache if available.
        
        Args:
            email: Email dictionary with subject, from, body, timestamp
        
        Returns:
            Analysis result dictionary
        """
        # Generate unique email ID
        email_id = self.session_manager.generate_email_id(email)
        
        # Check if email was already processed
        if self.session_manager.is_email_processed(email_id):
            cached_result = self.session_manager.get_email_analysis(email_id)
            self.session_manager.add_to_history('email_cache_hit', {
                'email_id': email_id,
                'subject': email.get('subject', 'Unknown')
            })
            return {
                **cached_result,
                'from_cache': True,
                'email_id': email_id
            }
        
        # Process email (not cached)
        self.session_manager.add_to_history('email_processing_start', {
            'email_id': email_id,
            'subject': email.get('subject', 'Unknown')
        })
        
        # Perform analysis
        classification = self.classify_email_priority(
            subject=email.get('subject', ''),
            sender=email.get('from', ''),
            body=email.get('body', '')
        )
        
        action_items_result = self.extract_action_items(
            subject=email.get('subject', ''),
            body=email.get('body', '')
        )
        
        meeting_requests_result = self.extract_meeting_requests(
            subject=email.get('subject', ''),
            body=email.get('body', '')
        )
        
        # Build result
        analysis_result = {
            'email_id': email_id,
            'subject': email.get('subject', ''),
            'from': email.get('from', ''),
            'timestamp': email.get('timestamp', ''),
            'classification': classification,
            'action_items': action_items_result.get('action_items', []),
            'meeting_requests': meeting_requests_result,
            'from_cache': False,
            'processed_at': self.session_manager.session_data.get('last_updated')
        }
        
        # Mark as processed and cache result
        self.session_manager.mark_email_processed(email_id, analysis_result)
        
        # Also cache using a cache key
        cache_key = f"email_analysis_{email_id}"
        self.session_manager.cache_result(
            cache_key,
            analysis_result,
            metadata={'type': 'email_analysis', 'email_id': email_id}
        )
        
        self.session_manager.add_to_history('email_processing_complete', {
            'email_id': email_id,
            'priority': classification.get('priority', 'unknown'),
            'action_items_count': len(analysis_result['action_items'])
        })
        
        return analysis_result
    
    def process_emails(self, emails: List[Dict]) -> List[Dict]:
        """
        Process multiple emails, using cache where available.
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            List of analysis results
        """
        results = []
        cached_count = 0
        processed_count = 0
        
        for email in emails:
            result = self.process_email(email)
            results.append(result)
            
            if result.get('from_cache'):
                cached_count += 1
            else:
                processed_count += 1
        
        self.session_manager.add_to_history('batch_processing_complete', {
            'total_emails': len(emails),
            'cached': cached_count,
            'processed': processed_count
        })
        
        return results
    
    def get_processed_emails(self) -> Dict:
        """Get all processed emails."""
        return self.session_manager.session_data.get('processed_emails', {})
    
    def get_processing_history(self, limit: int = None) -> List[Dict]:
        """Get processing history."""
        return self.session_manager.get_history(limit=limit)
    
    def get_stats(self) -> Dict:
        """Get agent statistics."""
        stats = self.session_manager.get_session_stats()
        processed = self.get_processed_emails()
        
        return {
            **stats,
            'processed_email_ids': list(processed.keys())
        }


if __name__ == "__main__":
    # quick test
    print("Email Agent - testing setup")
    print("-" * 40)
    
    agent = create_email_intelligence_agent()
    print(f"Ready. Tools: {len(agent.tools)}")
    print("Using: gemini-2.5-flash-lite")
    
    # Test stateful agent
    print("\n" + "-" * 40)
    print("Testing StatefulEmailAgent...")
    
    stateful_agent = StatefulEmailAgent()
    test_email = {
        'subject': 'Test Email',
        'from': 'test@example.com',
        'body': 'This is a test email body',
        'timestamp': '2024-11-20T10:00:00'
    }
    
    result = stateful_agent.process_email(test_email)
    print(f"✓ Processed email: {result['subject']}")
    print(f"  Priority: {result['classification']['priority']}")
    print(f"  From cache: {result.get('from_cache', False)}")
    
    # Process again (should use cache)
    result2 = stateful_agent.process_email(test_email)
    print(f"\n✓ Processed same email again: {result2['subject']}")
    print(f"  From cache: {result2.get('from_cache', False)}")
    
    stats = stateful_agent.get_stats()
    print(f"\n📊 Stats: {stats['emails_processed']} emails processed")

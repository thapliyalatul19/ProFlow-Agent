"""
Async Orchestrator for ProFlow Agent - Real Parallel Processing

Demonstrates actual parallel execution using asyncio and ThreadPoolExecutor
for CPU-bound tasks.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import email_tools
from data import read_emails_from_csv


class AsyncOrchestrator:
    """
    Async orchestrator that processes emails in parallel.
    
    Uses asyncio for I/O-bound operations and ThreadPoolExecutor
    for CPU-bound email processing tasks.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize async orchestrator.
        
        Args:
            max_workers: Maximum number of worker threads for CPU-bound tasks
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.email_tools = email_tools
    
    async def analyze_email_async(self, email: Dict, email_index: int) -> Dict:
        """
        Analyze a single email asynchronously.
        
        This method runs the CPU-bound email analysis in a thread pool
        to allow parallel processing.
        
        Args:
            email: Email dictionary with subject, from, body
            email_index: Index of email in the list (for logging)
        
        Returns:
            Analysis result dictionary
        """
        start_time = time.time()
        email_id = email.get('subject', f'Email {email_index}')[:50]
        
        print(f"  [Email {email_index}] 🚀 STARTED processing: {email_id}")
        
        # Run CPU-bound email analysis in thread pool
        loop = asyncio.get_event_loop()
        
        # Create analysis function that will run in thread
        def _analyze_email():
            """CPU-bound email analysis."""
            # Simulate some processing time (in real scenario, this is actual analysis)
            time.sleep(0.5)  # Simulate 500ms processing time
            
            # Perform actual email analysis
            classification = self.email_tools.classify_email_priority(
                subject=email.get('subject', ''),
                sender=email.get('from', ''),
                body=email.get('body', '')
            )
            
            # Extract action items
            action_items_result = self.email_tools.extract_action_items(
                subject=email.get('subject', ''),
                body=email.get('body', '')
            )
            
            # Extract meeting requests
            meeting_requests_result = self.email_tools.extract_meeting_requests(
                subject=email.get('subject', ''),
                body=email.get('body', '')
            )
            
            return {
                'email_index': email_index,
                'subject': email.get('subject', ''),
                'from': email.get('from', ''),
                'classification': classification,
                'action_items': action_items_result.get('action_items', []),
                'meeting_requests': meeting_requests_result.get('meetings_detected', False),
                'processing_time': time.time() - start_time
            }
        
        # Run in thread pool (non-blocking)
        result = await loop.run_in_executor(self.executor, _analyze_email)
        
        elapsed = time.time() - start_time
        print(f"  [Email {email_index}] ✅ FINISHED processing: {email_id} (took {elapsed:.2f}s)")
        
        return result
    
    async def process_emails_parallel(self, emails: List[Dict]) -> List[Dict]:
        """
        Process multiple emails in parallel using asyncio.
        
        This method ACTUALLY runs emails in parallel, not sequentially.
        Each email is processed concurrently using asyncio.gather().
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            List of analysis results
        """
        print(f"\n🔄 Starting PARALLEL processing of {len(emails)} emails...")
        print(f"   Using {self.max_workers} worker threads\n")
        
        start_time = time.time()
        
        # Create tasks for all emails - they will run in parallel
        tasks = [
            self.analyze_email_async(email, index)
            for index, email in enumerate(emails)
        ]
        
        # Execute all tasks in parallel using asyncio.gather
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        print(f"\n✅ PARALLEL processing complete!")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average time per email: {total_time / len(emails):.2f}s")
        
        return results
    
    def process_emails_sequential(self, emails: List[Dict]) -> List[Dict]:
        """
        Process emails sequentially (for comparison).
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            List of analysis results
        """
        print(f"\n🔄 Starting SEQUENTIAL processing of {len(emails)} emails...\n")
        
        start_time = time.time()
        results = []
        
        for index, email in enumerate(emails):
            email_id = email.get('subject', f'Email {index}')[:50]
            print(f"  [Email {index}] 🚀 STARTED processing: {email_id}")
            
            email_start = time.time()
            
            # Perform email analysis (synchronous)
            classification = self.email_tools.classify_email_priority(
                subject=email.get('subject', ''),
                sender=email.get('from', ''),
                body=email.get('body', '')
            )
            
            action_items_result = self.email_tools.extract_action_items(
                subject=email.get('subject', ''),
                body=email.get('body', '')
            )
            
            meeting_requests_result = self.email_tools.extract_meeting_requests(
                subject=email.get('subject', ''),
                body=email.get('body', '')
            )
            
            # Simulate processing time
            time.sleep(0.5)
            
            elapsed = time.time() - email_start
            print(f"  [Email {index}] ✅ FINISHED processing: {email_id} (took {elapsed:.2f}s)")
            
            results.append({
                'email_index': index,
                'subject': email.get('subject', ''),
                'from': email.get('from', ''),
                'classification': classification,
                'action_items': action_items_result.get('action_items', []),
                'meeting_requests': meeting_requests_result.get('meetings_detected', False),
                'processing_time': elapsed
            })
        
        total_time = time.time() - start_time
        
        print(f"\n✅ SEQUENTIAL processing complete!")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average time per email: {total_time / len(emails):.2f}s")
        
        return results
    
    def shutdown(self):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("ASYNC ORCHESTRATOR TEST")
    print("="*60)
    
    # Load test emails
    try:
        emails = read_emails_from_csv()
        print(f"\n📧 Loaded {len(emails)} emails for testing\n")
    except Exception as e:
        print(f"Error loading emails: {e}")
        sys.exit(1)
    
    orchestrator = AsyncOrchestrator(max_workers=4)
    
    # Test sequential processing
    print("\n" + "="*60)
    print("TEST 1: SEQUENTIAL PROCESSING")
    print("="*60)
    sequential_results = orchestrator.process_emails_sequential(emails)
    sequential_time = sum(r['processing_time'] for r in sequential_results)
    
    # Test parallel processing
    print("\n" + "="*60)
    print("TEST 2: PARALLEL PROCESSING")
    print("="*60)
    parallel_results = asyncio.run(orchestrator.process_emails_parallel(emails))
    parallel_time = sum(r['processing_time'] for r in parallel_results)
    
    # Compare results
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    print(f"Sequential total time: {sequential_time:.2f}s")
    print(f"Parallel total time: {parallel_time:.2f}s")
    
    if sequential_time > 0:
        speedup = sequential_time / parallel_time
        print(f"\n🚀 Speedup: {speedup:.2f}x faster with parallel processing!")
    
    orchestrator.shutdown()


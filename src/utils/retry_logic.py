"""
Retry logic with exponential backoff for ProFlow Agent.

Provides decorators and classes for handling retries with exponential backoff.
"""

import time
import functools
import logging
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exceptions: Tuple of exception types to catch and retry (default: Exception)
        on_retry: Optional callback function called on each retry (receives attempt number and exception)
    
    Returns:
        Decorated function that retries on failure
    
    Example:
        @retry_with_backoff(max_retries=3, base_delay=2.0)
        def my_function():
            # This will retry up to 3 times with delays of 2, 4, 8 seconds
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    result = func(*args, **kwargs)
                    
                    # Log success if we retried
                    if attempt > 0:
                        logger.info(
                            f"✓ {func.__name__} succeeded after {attempt} retry(ies)"
                        )
                    
                    return result
                
                except exceptions as e:
                    last_exception = e
                    
                    # If this was the last attempt, raise the exception
                    if attempt == max_retries:
                        logger.error(
                            f"✗ {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    # Calculate exponential backoff delay: 2^attempt * base_delay
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    logger.warning(
                        f"⚠ {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Call optional retry callback
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback failed: {callback_error}")
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class SchedulingWithRetry:
    """
    Class for scheduling operations with retry logic.
    
    Uses the retry_with_backoff decorator internally to handle
    scheduling failures gracefully.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        """
        Initialize SchedulingWithRetry.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay between retries (seconds)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = 0
        self.last_attempt_time = None
    
    def _log_retry(self, attempt: int, exception: Exception):
        """Log retry attempt."""
        self.retry_count = attempt
        self.last_attempt_time = datetime.now()
        logger.info(
            f"📅 Scheduling retry #{attempt} at {self.last_attempt_time.strftime('%H:%M:%S')}"
        )
    
    @property
    def retry_decorator(self):
        """Get retry decorator configured for this instance."""
        return retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            exceptions=(Exception,),
            on_retry=self._log_retry
        )
    
    def schedule_meeting(self, meeting_details: dict) -> dict:
        """
        Schedule a meeting with retry logic.
        
        Args:
            meeting_details: Dictionary with meeting information
        
        Returns:
            Dictionary with scheduling result
        """
        @self.retry_decorator
        def _schedule():
            # Simulate scheduling operation that might fail
            # In real implementation, this would call actual scheduling API
            import random
            
            # Simulate 30% failure rate for demonstration
            if random.random() < 0.3:
                raise Exception("Scheduling API temporarily unavailable")
            
            return {
                'status': 'scheduled',
                'meeting_id': f"meeting_{int(time.time())}",
                'details': meeting_details
            }
        
        return _schedule()
    
    def check_availability(self, participants: list, time_slot: str) -> dict:
        """
        Check availability with retry logic.
        
        Args:
            participants: List of participant emails
            time_slot: Time slot to check
        
        Returns:
            Dictionary with availability result
        """
        @self.retry_decorator
        def _check():
            # Simulate availability check that might fail
            import random
            
            # Simulate 20% failure rate
            if random.random() < 0.2:
                raise Exception("Availability API timeout")
            
            return {
                'available': True,
                'participants': participants,
                'time_slot': time_slot,
                'confidence': 0.95
            }
        
        return _check()
    
    def get_retry_stats(self) -> dict:
        """Get statistics about retry attempts."""
        return {
            'total_retries': self.retry_count,
            'last_retry_time': self.last_attempt_time.isoformat() if self.last_attempt_time else None,
            'max_retries': self.max_retries,
            'base_delay': self.base_delay
        }


# Example usage
if __name__ == "__main__":
    print("Testing retry logic...")
    
    # Test decorator
    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def flaky_function(should_fail: bool = True):
        if should_fail:
            raise ValueError("Simulated failure")
        return "Success!"
    
    print("\n1. Testing retry decorator (will fail after 3 retries):")
    try:
        result = flaky_function(should_fail=True)
    except ValueError as e:
        print(f"   Final error: {e}")
    
    print("\n2. Testing retry decorator (will succeed):")
    result = flaky_function(should_fail=False)
    print(f"   Result: {result}")
    
    # Test SchedulingWithRetry
    print("\n3. Testing SchedulingWithRetry class:")
    scheduler = SchedulingWithRetry(max_retries=2, base_delay=0.3)
    
    # This might succeed or fail (random)
    try:
        result = scheduler.schedule_meeting({
            'subject': 'Test Meeting',
            'participants': ['alice@example.com'],
            'duration': 30
        })
        print(f"   Scheduling result: {result['status']}")
    except Exception as e:
        print(f"   Scheduling failed: {e}")
    
    print(f"\n   Retry stats: {scheduler.get_retry_stats()}")


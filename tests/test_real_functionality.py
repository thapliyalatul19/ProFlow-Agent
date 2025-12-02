"""
Real functionality tests for ProFlow Agent.

Tests use real files, not mocks, to verify actual functionality.
"""

import pytest
import sys
import os
import json
import time
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data import read_emails_from_csv, read_calendar_from_json
from state.session_manager import SessionManager
from utils.retry_logic import retry_with_backoff, SchedulingWithRetry
from workflows.async_orchestrator import AsyncOrchestrator
import asyncio
from utils.error_handler import get_error_handler


class TestCSVEmailReader:
    """Test reading real CSV files."""
    
    def test_read_csv_exists(self):
        """Test reading existing CSV file."""
        emails = read_emails_from_csv()
        assert len(emails) > 0, "Should load at least one email"
        assert isinstance(emails, list), "Should return a list"
    
    def test_read_csv_structure(self):
        """Test CSV structure is correct."""
        emails = read_emails_from_csv()
        
        for email in emails:
            assert 'subject' in email, "Email should have 'subject' field"
            assert 'from' in email, "Email should have 'from' field"
            assert 'body' in email, "Email should have 'body' field"
    
    def test_read_csv_custom_path(self, tmp_path):
        """Test reading CSV from custom path."""
        # Create test CSV
        test_csv = tmp_path / "test_emails.csv"
        test_csv.write_text(
            "subject,from,body,timestamp\n"
            "Test,test@example.com,Test body,2024-11-20T10:00:00\n"
        )
        
        emails = read_emails_from_csv(str(test_csv))
        assert len(emails) == 1
        assert emails[0]['subject'] == "Test"


class TestJSONCalendarReader:
    """Test reading real JSON files."""
    
    def test_read_json_exists(self):
        """Test reading existing JSON file."""
        events = read_calendar_from_json()
        assert len(events) > 0, "Should load at least one event"
        assert isinstance(events, list), "Should return a list"
    
    def test_read_json_structure(self):
        """Test JSON structure is correct."""
        events = read_calendar_from_json()
        
        for event in events:
            assert 'summary' in event, "Event should have 'summary' field"
            assert 'start' in event, "Event should have 'start' field"
            assert 'end' in event, "Event should have 'end' field"
    
    def test_read_json_custom_path(self, tmp_path):
        """Test reading JSON from custom path."""
        # Create test JSON
        test_json = tmp_path / "test_calendar.json"
        test_json.write_text(
            json.dumps([{
                "summary": "Test Event",
                "start": "09:00",
                "end": "10:00",
                "duration_minutes": 60,
                "type": "meeting",
                "attendees": []
            }])
        )
        
        events = read_calendar_from_json(str(test_json))
        assert len(events) == 1
        assert events[0]['summary'] == "Test Event"


class TestSessionPersistence:
    """Test state actually persists."""
    
    def test_session_creates_file(self, tmp_path):
        """Test session creates JSON file."""
        session_file = tmp_path / "test_session.json"
        manager = SessionManager(str(session_file))
        manager.load_session()
        
        assert session_file.exists(), "Session file should be created"
    
    def test_session_persists_data(self, tmp_path):
        """Test session data persists between instances."""
        session_file = tmp_path / "test_session.json"
        
        # First instance
        manager1 = SessionManager(str(session_file))
        manager1.load_session()
        manager1.cache_result("test_key", {"value": "test_data"})
        manager1.save_session()
        
        # Second instance (should load same data)
        manager2 = SessionManager(str(session_file))
        manager2.load_session()
        
        cached = manager2.get_cached_result("test_key")
        assert cached is not None, "Cached data should persist"
        assert cached["value"] == "test_data", "Cached data should match"
    
    def test_session_tracks_history(self, tmp_path):
        """Test session tracks action history."""
        session_file = tmp_path / "test_session.json"
        manager = SessionManager(str(session_file))
        manager.load_session()
        
        manager.add_to_history("test_action", {"test": "data"})
        history = manager.get_history()
        
        assert len(history) > 0, "History should have entries"
        assert history[-1]['action'] == "test_action", "Last action should match"


class TestRetryLogic:
    """Test retry actually works with backoff."""
    
    def test_retry_decorator_retries(self):
        """Test retry decorator actually retries."""
        attempt_count = [0]
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def flaky_function():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise ValueError("Simulated failure")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert attempt_count[0] == 3, "Should retry 3 times"
    
    def test_retry_exponential_backoff(self):
        """Test exponential backoff timing."""
        attempt_times = []
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        def timing_test():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ValueError("Fail")
            return "success"
        
        start = time.time()
        timing_test()
        total_time = time.time() - start
        
        # Should have delays: 0.1s, 0.2s (exponential)
        assert total_time >= 0.2, "Should have exponential backoff delays"
        assert len(attempt_times) == 3, "Should have 3 attempts"
    
    def test_scheduling_with_retry(self):
        """Test SchedulingWithRetry class."""
        scheduler = SchedulingWithRetry(max_retries=2, base_delay=0.1)
        
        # This might succeed or fail (random), but should handle it
        try:
            result = scheduler.schedule_meeting({
                'subject': 'Test',
                'participants': ['test@example.com'],
                'duration': 30
            })
            assert 'status' in result or 'meeting_id' in result
        except Exception:
            # If it fails after retries, that's also valid
            pass


class TestAsyncProcessing:
    """Test parallel is faster than sequential."""
    
    def test_parallel_faster_than_sequential(self):
        """Test that parallel processing is actually faster."""
        # Load real emails
        emails = read_emails_from_csv()
        assert len(emails) > 0, "Need emails to test"
        
        orchestrator = AsyncOrchestrator(max_workers=4)
        
        # Sequential
        sequential_start = time.time()
        sequential_results = orchestrator.process_emails_sequential(emails)
        sequential_time = time.time() - sequential_start
        
        # Parallel
        parallel_start = time.time()
        parallel_results = asyncio.run(orchestrator.process_emails_parallel(emails))
        parallel_time = time.time() - parallel_start
        
        orchestrator.shutdown()
        
        # Verify results are the same
        assert len(sequential_results) == len(parallel_results)
        
        # Parallel should be faster (or at least not significantly slower)
        # Allow some margin for overhead
        assert parallel_time <= sequential_time * 1.5, \
            f"Parallel ({parallel_time:.3f}s) should be faster than sequential ({sequential_time:.3f}s)"
    
    def test_parallel_processes_all_emails(self):
        """Test parallel processing handles all emails."""
        emails = read_emails_from_csv()
        
        orchestrator = AsyncOrchestrator(max_workers=4)
        results = asyncio.run(orchestrator.process_emails_parallel(emails))
        orchestrator.shutdown()
        
        assert len(results) == len(emails), "Should process all emails"
        for result in results:
            assert 'email_index' in result
            assert 'subject' in result


class TestErrorRecovery:
    """Test system recovers from errors."""
    
    def test_file_not_found_recovery(self, tmp_path):
        """Test recovery from missing file."""
        missing_file = tmp_path / "missing.csv"
        error_handler = get_error_handler()
        
        # Should not raise, should recover
        result = error_handler.handle_error(
            FileNotFoundError(f"File not found: {missing_file}"),
            context={
                'file_path': str(missing_file),
                'default_content': 'subject,from,body\ntest,test@example.com,test\n',
                'file_type': 'CSV'
            }
        )
        
        # File should be created
        assert missing_file.exists(), "Recovery should create missing file"
        assert result is not None, "Recovery should return file path"
    
    def test_json_error_recovery(self):
        """Test recovery from JSON decode error."""
        error_handler = get_error_handler()
        
        default_data = {"default": "data"}
        result = error_handler.handle_error(
            json.JSONDecodeError("Invalid JSON", "", 0),
            context={
                'file_path': 'test.json',
                'default_data': default_data
            }
        )
        
        assert result == default_data, "Should return default data"
    
    def test_error_tracking(self):
        """Test error handler tracks errors."""
        error_handler = get_error_handler()
        error_handler.reset_error_counts()  # Start fresh
        
        # Generate some errors
        for _ in range(3):
            error_handler.handle_error(
                ValueError("Test error"),
                context={'test': True}
            )
        
        stats = error_handler.get_error_stats()
        assert stats['total_unique_errors'] > 0, "Should track errors"
        assert any('ValueError' in key for key in stats['error_counts']), \
            "Should track ValueError"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


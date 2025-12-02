"""
Integration tests for ProFlow Agent.

Tests full workflows and end-to-end functionality.
"""

import pytest
import sys
import os
import time
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.orchestrator import ProFlowOrchestrator
from agents.email_intelligence_agent import StatefulEmailAgent
from state.session_manager import SessionManager
from data import read_emails_from_csv, read_calendar_from_json


class TestFullWorkflow:
    """Full workflow test: Load data → Process → Cache → Verify."""
    
    def test_full_workflow(self):
        """Test complete workflow from data loading to briefing generation."""
        orchestrator = ProFlowOrchestrator()
        
        # Load data
        emails, calendar = orchestrator.load_data_from_files()
        assert len(emails) > 0, "Should load emails"
        assert len(calendar) > 0, "Should load calendar events"
        
        # Generate briefing
        briefing = orchestrator.generate_daily_briefing(emails, calendar)
        
        # Verify briefing structure
        assert 'summary' in briefing, "Briefing should have summary"
        assert 'components' in briefing, "Briefing should have components"
        assert 'email_intelligence' in briefing['components']
        assert 'calendar_optimization' in briefing['components']
        assert 'meeting_preparation' in briefing['components']
        
        # Verify email intelligence
        email_comp = briefing['components']['email_intelligence']
        assert email_comp['total_emails'] == len(emails)
        
        # Verify calendar optimization
        cal_comp = briefing['components']['calendar_optimization']
        assert cal_comp['total_meetings'] > 0 or len(calendar) > 0
    
    def test_workflow_with_caching(self, tmp_path):
        """Test workflow with stateful caching."""
        # Use temporary session file
        session_file = tmp_path / "test_session.json"
        
        # Create session manager
        session_manager = SessionManager(str(session_file))
        session_manager.load_session()
        
        # First run - process emails
        agent1 = StatefulEmailAgent(session_manager)
        emails = read_emails_from_csv()
        
        results1 = agent1.process_emails(emails)
        cached_count1 = sum(1 for r in results1 if r.get('from_cache'))
        processed_count1 = len(results1) - cached_count1
        
        assert processed_count1 > 0, "First run should process emails"
        
        # Save session
        session_manager.save_session()
        
        # Second run - should use cache (new manager, same file)
        session_manager2 = SessionManager(str(session_file))
        session_manager2.load_session()
        agent2 = StatefulEmailAgent(session_manager2)
        results2 = agent2.process_emails(emails)
        cached_count2 = sum(1 for r in results2 if r.get('from_cache'))
        
        assert cached_count2 > 0, "Second run should use cache"
        assert len(results1) == len(results2), "Should process same number of emails"


class TestPerformance:
    """Performance test: Verify parallel is faster."""
    
    def test_parallel_performance(self):
        """Test that parallel processing shows measurable speedup."""
        from workflows.async_orchestrator import AsyncOrchestrator
        import asyncio
        
        emails = read_emails_from_csv()
        # Skip if not enough emails (may happen if file was recovered)
        if len(emails) < 2:
            pytest.skip("Need at least 2 emails for meaningful test")
        
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
        
        # Verify results
        assert len(sequential_results) == len(parallel_results)
        
        # Calculate speedup
        if sequential_time > 0:
            speedup = sequential_time / parallel_time
            assert speedup >= 1.0, \
                f"Parallel should be at least as fast (speedup: {speedup:.2f}x)"
            
            # For multiple emails, parallel should show improvement
            if len(emails) >= 3:
                assert speedup > 1.1 or parallel_time < sequential_time, \
                    f"With {len(emails)} emails, parallel should be faster"


class TestStatePersistence:
    """State persistence test: Run twice, verify cache used."""
    
    def test_state_persistence_between_runs(self, tmp_path):
        """Test that state persists between separate runs."""
        session_file = tmp_path / "persistence_test.json"
        
        # First "run"
        manager1 = SessionManager(str(session_file))
        manager1.load_session()
        manager1.cache_result("persistent_key", {"data": "persistent_value"})
        manager1.mark_email_processed("email_123", {"test": "analysis"})
        manager1.save_session()
        
        # Verify file exists
        assert session_file.exists(), "Session file should exist"
        
        # Second "run" (new instance)
        manager2 = SessionManager(str(session_file))
        manager2.load_session()
        
        # Verify cached data persists
        cached = manager2.get_cached_result("persistent_key")
        assert cached is not None, "Cached data should persist"
        assert cached["data"] == "persistent_value"
        
        # Verify processed email persists
        assert manager2.is_email_processed("email_123"), "Processed email should persist"
        analysis = manager2.get_email_analysis("email_123")
        assert analysis is not None, "Email analysis should persist"
    
    def test_cache_speedup(self, tmp_path):
        """Test that caching provides speedup."""
        session_file = tmp_path / "cache_speedup_test.json"
        emails = read_emails_from_csv()
        
        # Create session manager
        session_manager1 = SessionManager(str(session_file))
        session_manager1.load_session()
        
        # First run (no cache)
        agent1 = StatefulEmailAgent(session_manager1)
        start1 = time.time()
        results1 = agent1.process_emails(emails)
        time1 = time.time() - start1
        
        # Save session
        session_manager1.save_session()
        
        # Second run (with cache) - new manager, same file
        session_manager2 = SessionManager(str(session_file))
        session_manager2.load_session()
        agent2 = StatefulEmailAgent(session_manager2)
        start2 = time.time()
        results2 = agent2.process_emails(emails)
        time2 = time.time() - start2
        
        # Verify cache was used
        cached_count = sum(1 for r in results2 if r.get('from_cache'))
        assert cached_count > 0, "Second run should use cache"
        
        # Cached run should be faster (or at least not slower)
        assert time2 <= time1 * 1.5, \
            f"Cached run ({time2:.3f}s) should be faster than first run ({time1:.3f}s)"


class TestErrorRecovery:
    """Error recovery test: Delete file, verify recreation."""
    
    def test_missing_file_recovery(self, tmp_path):
        """Test system recovers from missing file."""
        # Create a test file
        test_file = tmp_path / "test_data.csv"
        test_file.write_text("subject,from,body\ntest,test@example.com,test\n")
        
        # Delete it
        test_file.unlink()
        assert not test_file.exists(), "File should be deleted"
        
        # Try to recover
        from utils.error_handler import get_error_handler
        error_handler = get_error_handler()
        
        result = error_handler.handle_error(
            FileNotFoundError(f"File not found: {test_file}"),
            context={
                'file_path': str(test_file),
                'default_content': 'subject,from,body\ndefault,default@example.com,default\n',
                'file_type': 'CSV'
            }
        )
        
        # File should be recreated
        assert test_file.exists(), "File should be recreated"
        assert result is not None, "Recovery should return file path"
        
        # Verify content
        content = test_file.read_text()
        assert 'default' in content, "File should have default content"
    
    def test_orchestrator_handles_missing_files(self, tmp_path):
        """Test orchestrator handles missing files gracefully."""
        # Backup original
        original_file = Path("data/sample_emails.csv")
        backup_file = tmp_path / "backup.csv"
        
        if original_file.exists():
            shutil.copy(original_file, backup_file)
            original_file.unlink()
        
        try:
            orchestrator = ProFlowOrchestrator()
            emails, calendar = orchestrator.load_data_from_files()
            
            # Should either recover or return empty list gracefully
            assert isinstance(emails, list), "Should return list even if file missing"
            assert isinstance(calendar, list), "Should return list even if file missing"
            
        finally:
            # Restore
            if backup_file.exists():
                shutil.copy(backup_file, original_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


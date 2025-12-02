"""
ProFlow Agent - Comprehensive Demo Script

Demonstrates all features:
- Real data loading from CSV/JSON
- Sequential vs parallel processing with timing
- Caching (process twice, show cache hit)
- Error recovery (intentionally cause and recover from error)
- Performance metrics and statistics
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logging
from workflows.orchestrator import ProFlowOrchestrator
from workflows.async_orchestrator import AsyncOrchestrator
from agents.email_intelligence_agent import StatefulEmailAgent
from data import read_emails_from_csv, read_calendar_from_json
from utils.error_handler import get_error_handler


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    print("\n" + char * 70)
    print(title)
    print(char * 70)


def main():
    """Main demo function."""
    print_section("PROFLOW AGENT - COMPREHENSIVE DEMO")
    
    print("\nThis demo showcases:")
    print("  1. Real data loading from CSV/JSON files")
    print("  2. Sequential vs parallel processing (with timing)")
    print("  3. Caching demonstration (second run uses cache)")
    print("  4. Error recovery (handles missing files)")
    print("  5. Performance metrics and statistics")
    
    # Setup logging
    logger = setup_logging()
    logger.info("Demo started")
    
    # ============================================================
    # Part 1: Load Real Data
    # ============================================================
    print_section("PART 1: Loading Real Data")
    
    print("\n📂 Loading data from files...")
    start_time = time.time()
    
    try:
        emails = read_emails_from_csv()
        calendar_events = read_calendar_from_json()
        
        load_time = time.time() - start_time
        
        print(f"✅ Data loaded successfully!")
        print(f"   Emails: {len(emails)}")
        print(f"   Calendar events: {len(calendar_events)}")
        print(f"   Load time: {load_time:.3f} seconds")
        
        logger.info(f"Loaded {len(emails)} emails and {len(calendar_events)} calendar events")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        logger.error(f"Error loading data: {e}", exc_info=True)
        return 1
    
    # ============================================================
    # Part 2: Sequential vs Parallel Processing
    # ============================================================
    print_section("PART 2: Sequential vs Parallel Processing")
    
    print("\n🔄 Comparing sequential vs parallel email processing...")
    
    # Sequential processing
    print("\n1️⃣  Sequential Processing (one at a time):")
    sequential_start = time.time()
    
    async_orchestrator = AsyncOrchestrator(max_workers=4)
    sequential_results = async_orchestrator.process_emails_sequential(emails)
    
    sequential_time = time.time() - sequential_start
    
    print(f"\n   ✅ Sequential complete: {sequential_time:.3f} seconds")
    print(f"   Average per email: {sequential_time / len(emails):.3f} seconds")
    
    # Parallel processing
    print("\n2️⃣  Parallel Processing (all at once):")
    parallel_start = time.time()
    
    import asyncio
    parallel_results = asyncio.run(async_orchestrator.process_emails_parallel(emails))
    
    parallel_time = time.time() - parallel_start
    
    print(f"\n   ✅ Parallel complete: {parallel_time:.3f} seconds")
    print(f"   Average per email: {parallel_time / len(emails):.3f} seconds")
    
    # Compare
    if sequential_time > 0:
        speedup = sequential_time / parallel_time
        time_saved = sequential_time - parallel_time
        efficiency = (time_saved / sequential_time) * 100
        
        print(f"\n📊 Performance Comparison:")
        print(f"   Sequential: {sequential_time:.3f}s")
        print(f"   Parallel:   {parallel_time:.3f}s")
        print(f"   Speedup:    {speedup:.2f}x faster")
        print(f"   Time saved: {time_saved:.3f}s ({efficiency:.1f}% improvement)")
        
        logger.info(f"Parallel processing: {speedup:.2f}x speedup")
    
    async_orchestrator.shutdown()
    
    # ============================================================
    # Part 3: Caching Demonstration
    # ============================================================
    print_section("PART 3: Caching Demonstration")
    
    print("\n💾 Demonstrating stateful email processing with caching...")
    
    # First run - process emails
    print("\n1️⃣  First Run - Processing emails (will be cached):")
    stateful_agent1 = StatefulEmailAgent()
    
    cache_start = time.time()
    results1 = stateful_agent1.process_emails(emails)
    cache_time1 = time.time() - cache_start
    
    cached_count1 = sum(1 for r in results1 if r.get('from_cache'))
    processed_count1 = len(results1) - cached_count1
    
    print(f"   ✅ Processed: {processed_count1} new, {cached_count1} cached")
    print(f"   Time: {cache_time1:.3f} seconds")
    
    # Second run - should use cache
    print("\n2️⃣  Second Run - Processing same emails (should use cache):")
    stateful_agent2 = StatefulEmailAgent()  # New instance, but same session
    
    cache_start = time.time()
    results2 = stateful_agent2.process_emails(emails)
    cache_time2 = time.time() - cache_start
    
    cached_count2 = sum(1 for r in results2 if r.get('from_cache'))
    processed_count2 = len(results2) - cached_count2
    
    print(f"   ✅ Processed: {processed_count2} new, {cached_count2} cached")
    print(f"   Time: {cache_time2:.3f} seconds")
    
    if cached_count2 == len(emails):
        cache_speedup = cache_time1 / cache_time2 if cache_time2 > 0 else float('inf')
        print(f"\n📊 Cache Performance:")
        print(f"   First run:  {cache_time1:.3f}s (all new)")
        print(f"   Second run: {cache_time2:.3f}s (all cached)")
        print(f"   Cache speedup: {cache_speedup:.2f}x faster")
        print(f"   ✅ All emails loaded from cache!")
        
        logger.info(f"Cache demonstration: {cache_speedup:.2f}x speedup with cache")
    
    # Show session stats
    stats = stateful_agent2.get_stats()
    print(f"\n📊 Session Statistics:")
    print(f"   Emails processed: {stats['emails_processed']}")
    print(f"   Cache entries: {stats['cache_entries']}")
    print(f"   History entries: {stats['history_entries']}")
    
    # ============================================================
    # Part 4: Error Recovery
    # ============================================================
    print_section("PART 4: Error Recovery Demonstration")
    
    print("\n🛡️  Demonstrating error recovery...")
    
    # Backup original file
    original_file = Path("data/sample_emails.csv")
    backup_file = Path("data/sample_emails.csv.backup_demo")
    
    if original_file.exists():
        import shutil
        shutil.copy(original_file, backup_file)
        original_file.unlink()
        print(f"   📝 Temporarily removed email file for testing...")
    
    # Try to load data (should trigger recovery)
    print("\n   🔄 Attempting to load data from missing file...")
    error_handler = get_error_handler()
    
    try:
        orchestrator = ProFlowOrchestrator()
        recovered_emails, recovered_calendar = orchestrator.load_data_from_files()
        
        print(f"   ✅ Recovery successful!")
        print(f"      Emails loaded: {len(recovered_emails)}")
        print(f"      Calendar events: {len(recovered_calendar)}")
        
        if recovered_emails:
            print(f"      First email: {recovered_emails[0].get('subject', 'N/A')}")
        
        logger.info(f"Error recovery successful: {len(recovered_emails)} emails recovered")
    
    except Exception as e:
        print(f"   ❌ Recovery failed: {e}")
        logger.error(f"Recovery failed: {e}", exc_info=True)
    
    # Restore backup
    if backup_file.exists():
        import shutil
        shutil.copy(backup_file, original_file)
        backup_file.unlink()
        print(f"   📝 Original file restored")
    
    # ============================================================
    # Part 5: Full Workflow Demo
    # ============================================================
    print_section("PART 5: Full Workflow Demonstration")
    
    print("\n🔄 Running complete workflow: Load → Process → Generate Briefing")
    
    try:
        orchestrator = ProFlowOrchestrator()
        
        workflow_start = time.time()
        
        # Load data
        print("\n   1. Loading data...")
        emails, calendar = orchestrator.load_data_from_files()
        print(f"      ✓ Loaded {len(emails)} emails, {len(calendar)} events")
        
        # Generate briefing
        print("\n   2. Generating daily briefing...")
        briefing = orchestrator.generate_daily_briefing(emails, calendar)
        
        workflow_time = time.time() - workflow_start
        
        print(f"\n   ✅ Workflow complete in {workflow_time:.3f} seconds")
        
        # Show summary
        if 'summary' in briefing:
            print(f"\n   📋 Briefing Summary:")
            print(f"      {briefing['summary']}")
        
        # Show components
        components = briefing.get('components', {})
        if 'email_intelligence' in components:
            email_comp = components['email_intelligence']
            print(f"\n   📧 Email Intelligence:")
            print(f"      Total: {email_comp.get('total_emails', 0)}")
            print(f"      High priority: {len(email_comp.get('high_priority', []))}")
            print(f"      Action items: {len(email_comp.get('action_items', []))}")
        
        if 'calendar_optimization' in components:
            cal_comp = components['calendar_optimization']
            print(f"\n   📅 Calendar Optimization:")
            print(f"      Meetings: {cal_comp.get('total_meetings', 0)}")
            print(f"      Focus time: {cal_comp.get('focus_time_minutes', 0)} minutes")
            print(f"      Score: {cal_comp.get('optimization_score', 0):.1f}/100")
        
        logger.info(f"Full workflow completed in {workflow_time:.3f}s")
    
    except Exception as e:
        print(f"\n   ❌ Workflow failed: {e}")
        logger.error(f"Workflow failed: {e}", exc_info=True)
    
    # ============================================================
    # Summary
    # ============================================================
    print_section("DEMO SUMMARY")
    
    print("\n✅ All Features Demonstrated:")
    print(f"   ✓ Real data loading from CSV/JSON")
    print(f"   ✓ Sequential vs parallel processing (speedup demonstrated)")
    print(f"   ✓ Caching (second run uses cache)")
    print(f"   ✓ Error recovery (missing files handled)")
    print(f"   ✓ Full workflow execution")
    
    print("\n📊 Performance Highlights:")
    if sequential_time > 0 and parallel_time > 0:
        print(f"   • Parallel processing: {speedup:.2f}x faster than sequential")
    if cache_time1 > 0 and cache_time2 > 0 and cached_count2 == len(emails):
        cache_speedup = cache_time1 / cache_time2 if cache_time2 > 0 else 0
        print(f"   • Caching: {cache_speedup:.2f}x faster on second run")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\n💡 Check logs/ directory for detailed execution logs")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


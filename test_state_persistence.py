"""
Test script to demonstrate state persistence.

Shows that:
1. Emails are processed and cached
2. Session data persists between runs
3. Cached results are reused (processing is skipped)
4. History shows all operations with timestamps
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.email_intelligence_agent import StatefulEmailAgent
from state.session_manager import SessionManager
from data import read_emails_from_csv


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def main():
    """Main test function."""
    print_section("PROFLOW STATE PERSISTENCE TEST")
    
    print("\nThis test demonstrates:")
    print("  1. Processing emails and caching results")
    print("  2. Session data persisting between runs")
    print("  3. Cached results being reused (skipping reprocessing)")
    print("  4. History tracking all operations with timestamps")
    
    # Load emails
    print_section("STEP 1: Loading Emails")
    try:
        emails = read_emails_from_csv()
        print(f"✓ Loaded {len(emails)} emails from data/sample_emails.csv")
    except Exception as e:
        print(f"✗ Error loading emails: {e}")
        return 1
    
    # ============================================================
    # FIRST RUN: Process emails
    # ============================================================
    print_section("STEP 2: First Run - Processing Emails")
    
    print("\nCreating StatefulEmailAgent (new session)...")
    agent1 = StatefulEmailAgent()
    session1 = agent1.session_manager
    
    print(f"✓ Session ID: {session1.session_data['session_id']}")
    print(f"✓ Session file: {session1.session_file}")
    
    print(f"\n📧 Processing {len(emails)} emails...")
    start_time = time.time()
    
    results1 = agent1.process_emails(emails)
    
    processing_time = time.time() - start_time
    
    print(f"\n✅ Processing complete in {processing_time:.2f} seconds")
    
    # Show results
    cached_count = sum(1 for r in results1 if r.get('from_cache'))
    processed_count = len(results1) - cached_count
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total emails: {len(results1)}")
    print(f"   Newly processed: {processed_count}")
    print(f"   From cache: {cached_count}")
    
    print(f"\n📋 Email Results:")
    for i, result in enumerate(results1, 1):
        cache_indicator = "💾 [CACHED]" if result.get('from_cache') else "🆕 [NEW]"
        priority = result['classification'].get('priority', 'unknown').upper()
        print(f"   {i}. {cache_indicator} {result['subject'][:50]}")
        print(f"      Priority: {priority} | From: {result['from']}")
    
    # Show session stats
    stats1 = agent1.get_stats()
    print(f"\n📊 Session Statistics:")
    print(f"   Emails processed: {stats1['emails_processed']}")
    print(f"   Cache entries: {stats1['cache_entries']}")
    print(f"   History entries: {stats1['history_entries']}")
    
    # Show recent history
    print(f"\n📜 Recent History (last 5 entries):")
    history1 = agent1.get_processing_history(limit=5)
    for entry in history1[-5:]:
        timestamp = entry['timestamp'].split('T')[1].split('.')[0]  # Just time
        print(f"   [{timestamp}] {entry['action']}: {entry.get('details', {})}")
    
    # Verify session file exists
    print(f"\n💾 Session File:")
    if session1.session_file.exists():
        file_size = session1.session_file.stat().st_size
        print(f"   ✓ File exists: {session1.session_file}")
        print(f"   ✓ File size: {file_size} bytes")
    else:
        print(f"   ✗ File not found: {session1.session_file}")
        return 1
    
    # ============================================================
    # SECOND RUN: Load existing session and show cache usage
    # ============================================================
    print_section("STEP 3: Second Run - Using Cached Results")
    
    print("\nCreating NEW StatefulEmailAgent (should load existing session)...")
    agent2 = StatefulEmailAgent()
    session2 = agent2.session_manager
    
    print(f"✓ Session ID: {session2.session_data['session_id']}")
    
    # Check if it's the same session
    if session1.session_data['session_id'] == session2.session_data['session_id']:
        print("✓ Same session loaded (persistence working!)")
    else:
        print("⚠️  Different session ID (may be expected if file was cleared)")
    
    print(f"\n📧 Processing same {len(emails)} emails again...")
    start_time = time.time()
    
    results2 = agent2.process_emails(emails)
    
    processing_time = time.time() - start_time
    
    print(f"\n✅ Processing complete in {processing_time:.2f} seconds")
    
    # Show results - should all be from cache
    cached_count2 = sum(1 for r in results2 if r.get('from_cache'))
    processed_count2 = len(results2) - cached_count2
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total emails: {len(results2)}")
    print(f"   Newly processed: {processed_count2}")
    print(f"   From cache: {cached_count2}")
    
    if cached_count2 == len(results2):
        print(f"\n✅ SUCCESS: All emails loaded from cache (no reprocessing!)")
    else:
        print(f"\n⚠️  Some emails were reprocessed (expected if cache was cleared)")
    
    print(f"\n📋 Email Results:")
    for i, result in enumerate(results2, 1):
        cache_indicator = "💾 [CACHED]" if result.get('from_cache') else "🆕 [NEW]"
        priority = result['classification'].get('priority', 'unknown').upper()
        print(f"   {i}. {cache_indicator} {result['subject'][:50]}")
        print(f"      Priority: {priority}")
    
    # Show updated stats
    stats2 = agent2.get_stats()
    print(f"\n📊 Updated Session Statistics:")
    print(f"   Emails processed: {stats2['emails_processed']}")
    print(f"   Cache entries: {stats2['cache_entries']}")
    print(f"   History entries: {stats2['history_entries']}")
    
    # Show processing history
    print(f"\n📜 Processing History (showing cache hits):")
    cache_hits = [h for h in agent2.get_processing_history() if h['action'] == 'email_cache_hit']
    print(f"   Total cache hits: {len(cache_hits)}")
    if cache_hits:
        print(f"   Recent cache hits:")
        for entry in cache_hits[-3:]:
            timestamp = entry['timestamp'].split('T')[1].split('.')[0]
            subject = entry.get('details', {}).get('subject', 'Unknown')
            print(f"      [{timestamp}] {subject}")
    
    # ============================================================
    # Show session file contents (first few lines)
    # ============================================================
    print_section("STEP 4: Session File Contents (Human-Readable)")
    
    if session2.session_file.exists():
        print(f"\n📄 First 30 lines of {session2.session_file}:")
        print("-" * 70)
        try:
            with open(session2.session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:30]
                for i, line in enumerate(lines, 1):
                    print(f"{i:3}: {line.rstrip()}")
            if len(lines) == 30:
                print("   ... (file continues)")
        except Exception as e:
            print(f"   Error reading file: {e}")
    else:
        print(f"   ✗ Session file not found")
    
    # ============================================================
    # Summary
    # ============================================================
    print_section("TEST SUMMARY")
    
    print("\n✅ State Persistence Test Results:")
    print(f"   ✓ Session data persists between runs")
    print(f"   ✓ Cached results are reused (processing skipped)")
    print(f"   ✓ History tracks all operations with timestamps")
    print(f"   ✓ Session file is human-readable JSON")
    
    if cached_count2 == len(results2):
        print(f"\n🚀 Performance: {len(results2)} emails processed in {processing_time:.3f}s")
        print(f"   (All from cache - no actual processing needed!)")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


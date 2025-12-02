"""
Demo script to demonstrate parallel processing speedup.

Compares sequential vs parallel email processing and shows timing differences.
"""

import time
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflows.async_orchestrator import AsyncOrchestrator
from data import read_emails_from_csv


def main():
    """Main demo function."""
    print("="*70)
    print("PROFLOW PARALLEL PROCESSING DEMO")
    print("="*70)
    print("\nThis demo compares sequential vs parallel email processing")
    print("to demonstrate the performance benefits of async/parallel execution.\n")
    
    # Load emails from CSV
    print("📂 Loading emails from data/sample_emails.csv...")
    try:
        emails = read_emails_from_csv()
        print(f"   ✓ Loaded {len(emails)} emails\n")
    except FileNotFoundError as e:
        print(f"   ✗ Error: {e}")
        print("\n   Make sure data/sample_emails.csv exists!")
        return 1
    except Exception as e:
        print(f"   ✗ Error loading emails: {e}")
        return 1
    
    if len(emails) == 0:
        print("   ✗ No emails found in CSV file!")
        return 1
    
    # Create orchestrator
    orchestrator = AsyncOrchestrator(max_workers=4)
    
    # ============================================================
    # SEQUENTIAL PROCESSING
    # ============================================================
    print("="*70)
    print("SEQUENTIAL PROCESSING (One email at a time)")
    print("="*70)
    print("\nEach email is processed completely before starting the next one.\n")
    
    sequential_start = time.time()
    sequential_results = orchestrator.process_emails_sequential(emails)
    sequential_total = time.time() - sequential_start
    
    # Calculate statistics
    sequential_avg = sequential_total / len(emails) if emails else 0
    sequential_max = max((r['processing_time'] for r in sequential_results), default=0)
    sequential_min = min((r['processing_time'] for r in sequential_results), default=0)
    
    print(f"\n📊 SEQUENTIAL STATISTICS:")
    print(f"   Total time: {sequential_total:.3f} seconds")
    print(f"   Average per email: {sequential_avg:.3f} seconds")
    print(f"   Fastest email: {sequential_min:.3f} seconds")
    print(f"   Slowest email: {sequential_max:.3f} seconds")
    
    # ============================================================
    # PARALLEL PROCESSING
    # ============================================================
    print("\n" + "="*70)
    print("PARALLEL PROCESSING (All emails processed simultaneously)")
    print("="*70)
    print("\nAll emails start processing at the same time using asyncio.\n")
    
    parallel_start = time.time()
    parallel_results = asyncio.run(orchestrator.process_emails_parallel(emails))
    parallel_total = time.time() - parallel_start
    
    # Calculate statistics
    parallel_avg = parallel_total / len(emails) if emails else 0
    parallel_max = max((r['processing_time'] for r in parallel_results), default=0)
    parallel_min = min((r['processing_time'] for r in parallel_results), default=0)
    
    print(f"\n📊 PARALLEL STATISTICS:")
    print(f"   Total time: {parallel_total:.3f} seconds")
    print(f"   Average per email: {parallel_avg:.3f} seconds")
    print(f"   Fastest email: {parallel_min:.3f} seconds")
    print(f"   Slowest email: {parallel_max:.3f} seconds")
    
    # ============================================================
    # COMPARISON
    # ============================================================
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)
    
    if sequential_total > 0:
        speedup = sequential_total / parallel_total
        time_saved = sequential_total - parallel_total
        efficiency = (time_saved / sequential_total) * 100
        
        print(f"\n⏱️  TIMING RESULTS:")
        print(f"   Sequential: {sequential_total:.3f}s")
        print(f"   Parallel:   {parallel_total:.3f}s")
        print(f"   Time saved: {time_saved:.3f}s ({efficiency:.1f}% faster)")
        
        print(f"\n🚀 SPEEDUP:")
        print(f"   Parallel processing is {speedup:.2f}x faster!")
        
        if speedup > 1.5:
            print(f"   ✅ Significant performance improvement with parallel processing!")
        elif speedup > 1.1:
            print(f"   ✓ Noticeable performance improvement")
        else:
            print(f"   ⚠️  Small improvement (may be due to overhead)")
    
    # Verify results are the same
    print(f"\n🔍 VERIFICATION:")
    if len(sequential_results) == len(parallel_results):
        print(f"   ✓ Both methods processed {len(sequential_results)} emails")
        
        # Check if results are similar (subject matching)
        sequential_subjects = {r['subject'] for r in sequential_results}
        parallel_subjects = {r['subject'] for r in parallel_results}
        
        if sequential_subjects == parallel_subjects:
            print(f"   ✓ Results match (same emails processed)")
        else:
            print(f"   ⚠️  Results differ (this shouldn't happen)")
    else:
        print(f"   ⚠️  Different number of results!")
    
    # Show parallel execution proof
    print(f"\n📈 PARALLEL EXECUTION PROOF:")
    print(f"   Notice how in parallel mode, multiple emails show 'STARTED'")
    print(f"   before any show 'FINISHED' - this proves true parallel execution!")
    print(f"   In sequential mode, each email finishes before the next starts.")
    
    # Cleanup
    orchestrator.shutdown()
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


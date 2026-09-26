#!/usr/bin/env python3
"""
DAXDA Cl(16,4) Overnight Continuous Run
========================================

Runs the Clifford Geometric Algebra Cl(16,4) recursive self-improvement 
pipeline continuously for a set duration (e.g., 5 hours).
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from daxda_engine.cl16_4.recursive_self_improvement import run_recursive_self_improvement

def run_overnight(duration_hours: float = 5.0, interval_seconds: int = 60):
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    log_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "outputs", 
        f"overnight_run_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
    ))
    
    print("=" * 60)
    print(f" INITIALIZING DAXDA Cl(16,4) OVERNIGHT RUN")
    print(f" Target Duration: {duration_hours} hours")
    print(f" Interval:        {interval_seconds} seconds between cycles")
    print(f" End Time:        {end_time}")
    print(f" Logging to:      {log_file}")
    print("=" * 60)
    
    cycle_count = 0
    total_passed = 0
    total_blocked = 0
    
    with open(log_file, "w") as f:
        f.write(f"DAXDA OVERNIGHT RUN STARTED: {start_time}\n")
        f.write(f"TARGET DURATION: {duration_hours} hours\n\n")

    try:
        while datetime.now() < end_time:
            cycle_count += 1
            current_time = datetime.now()
            
            # Execute RSI Engine
            report = run_recursive_self_improvement()
            
            total_passed += report['passed_proposals']
            total_blocked += report['blocked_proposals']
            
            # Console Output
            print(f"[{current_time.strftime('%H:%M:%S')}] Cycle {cycle_count:04d} | "
                  f"Score: {report['results'][0]['score']:.4f} | "
                  f"Passed: {report['passed_proposals']} | Blocked: {report['blocked_proposals']}")
            
            # Append to log
            with open(log_file, "a") as f:
                f.write(json.dumps({
                    "cycle": cycle_count,
                    "timestamp": current_time.isoformat(),
                    "passed": report['passed_proposals'],
                    "blocked": report['blocked_proposals'],
                    "duration_ms": report['cycle_duration_ms']
                }) + "\n")
            
            # Sleep until next cycle
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n[!] Overnight run gracefully interrupted by user.")
        
    finally:
        finish_time = datetime.now()
        print("=" * 60)
        print(" DAXDA Cl(16,4) OVERNIGHT RUN COMPLETE")
        print("=" * 60)
        print(f" Total Cycles:  {cycle_count}")
        print(f" Total Passed:  {total_passed}")
        print(f" Total Blocked: {total_blocked}")
        print(f" Time Elapsed:  {finish_time - start_time}")
        print("=" * 60)

if __name__ == "__main__":
    # Default is 5 hours, running a check every 60 seconds
    run_overnight(duration_hours=5.0, interval_seconds=60)

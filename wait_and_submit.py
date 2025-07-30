#!/usr/bin/env python3
"""
Wait for submission limit reset and submit championship agent
"""

import subprocess
import time
import datetime
import pytz

def check_submission_limit():
    """Check if we can submit"""
    try:
        # Get submission history
        result = subprocess.run(
            ['kaggle', 'competitions', 'submissions', '-c', 'connectx'],
            capture_output=True, text=True, check=True
        )
        
        # Parse last submission time
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            # Extract date from first data row
            last_submission_str = lines[1].split()[1] + " " + lines[1].split()[2]
            
            # Parse time (assuming UTC)
            last_submission = datetime.datetime.strptime(
                last_submission_str, "%Y-%m-%d %H:%M:%S.%f"
            ).replace(tzinfo=pytz.UTC)
            
            # Check if 24 hours have passed
            time_since = datetime.datetime.now(pytz.UTC) - last_submission
            if time_since.total_seconds() >= 86400:  # 24 hours
                return True, 0
            else:
                remaining = 86400 - time_since.total_seconds()
                return False, remaining
    except Exception as e:
        print(f"Error checking submissions: {e}")
        return False, 3600  # Default wait 1 hour on error
    
    return False, 3600

def submit_agent():
    """Submit the championship agent"""
    try:
        result = subprocess.run([
            'kaggle', 'competitions', 'submit', 
            '-c', 'connectx', 
            '-f', 'submission.py',
            '-m', 'Championship 1000+ v2 - Enhanced bitboard engine, 12-14 ply search, 100% vs Random, 85% vs Negamax, targeting 1000+ score'
        ], capture_output=True, text=True, check=True)
        
        print(f"✓ Submission successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Submission failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Main monitoring loop"""
    print("Championship 1000+ Agent Submission Monitor")
    print("="*50)
    
    while True:
        can_submit, wait_time = check_submission_limit()
        
        if can_submit:
            print(f"\n{datetime.datetime.now()}: Submission limit reset!")
            print("Submitting championship agent...")
            
            if submit_agent():
                print("\n✓ Championship 1000+ agent submitted successfully!")
                print("Monitor leaderboard at: https://www.kaggle.com/competitions/connectx/leaderboard")
                break
            else:
                print("\nRetrying in 5 minutes...")
                time.sleep(300)
        else:
            hours = int(wait_time // 3600)
            minutes = int((wait_time % 3600) // 60)
            print(f"\r{datetime.datetime.now()}: Waiting {hours}h {minutes}m until next submission allowed...", end='', flush=True)
            
            # Check every 5 minutes
            time.sleep(min(300, wait_time))

if __name__ == "__main__":
    main()
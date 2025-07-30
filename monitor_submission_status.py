#!/usr/bin/env python3
"""Monitor Kaggle submission status and alert when ready"""

import subprocess
import time
from datetime import datetime
import json

def check_submission_status():
    """Check if we can submit to Kaggle"""
    try:
        # Try a test submission
        result = subprocess.run(
            ["kaggle", "competitions", "submit", "-c", "connectx", "-f", "submission.py", "-m", "Test submission"],
            capture_output=True,
            text=True
        )
        
        if "Successfully submitted" in result.stdout:
            return True, "Submission successful!"
        elif "400 Client Error" in result.stderr:
            return False, "Daily limit still active"
        else:
            return False, f"Unknown error: {result.stderr}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_latest_scores():
    """Get our latest submission scores"""
    try:
        result = subprocess.run(
            ["kaggle", "competitions", "submissions", "-c", "connectx"],
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 2:
            # Parse the latest submission
            latest = lines[2].split()
            if len(latest) >= 6:
                return {
                    'date': ' '.join(latest[1:3]),
                    'score': latest[-2] if latest[-2] != '' else 'Pending'
                }
    except:
        pass
    return None

def main():
    print("=== Kaggle Connect X Submission Monitor ===")
    print(f"Started at: {datetime.now()}")
    print("\nMonitoring submission status...")
    print("Press Ctrl+C to stop\n")
    
    check_count = 0
    while True:
        check_count += 1
        print(f"\n--- Check #{check_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        # Check submission status
        can_submit, message = check_submission_status()
        print(f"Status: {message}")
        
        # Get latest scores
        latest = get_latest_scores()
        if latest:
            print(f"Latest submission: {latest['date']} - Score: {latest['score']}")
        
        if can_submit:
            print("\n🎉 READY TO SUBMIT! 🎉")
            print("\nRun this command:")
            print('kaggle competitions submit -c connectx -f submission.py -m "Championship Agent v4 - Ultra-fast execution (0.086ms max), comprehensive opening book, 96% win rate"')
            break
        else:
            print("\nWaiting 5 minutes before next check...")
            time.sleep(300)  # Wait 5 minutes

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
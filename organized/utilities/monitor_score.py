#!/usr/bin/env python3
"""Monitor Kaggle submission score"""

import subprocess
import time
from datetime import datetime

def get_latest_score():
    """Get the latest submission score"""
    try:
        result = subprocess.run(
            ["kaggle", "competitions", "submissions", "-c", "connectx"],
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 2:
            # Parse the latest submission
            latest_line = lines[2]
            parts = latest_line.split()
            
            # Find status and score
            status = "Unknown"
            score = "Pending"
            
            for i, part in enumerate(parts):
                if "SubmissionStatus" in part:
                    status = part.split('.')[-1]
                elif i == len(parts) - 2:  # Second to last is usually public score
                    try:
                        score = float(part)
                    except:
                        score = part if part else "Pending"
            
            return status, score
    except Exception as e:
        return "Error", str(e)
    
    return "Unknown", "Unknown"

def main():
    print("=== Kaggle Connect X Score Monitor ===")
    print(f"Started at: {datetime.now()}")
    print("\nMonitoring submission score...")
    print("Press Ctrl+C to stop\n")
    
    check_count = 0
    last_score = None
    
    while True:
        check_count += 1
        
        status, score = get_latest_score()
        
        # Only print if there's a change
        if score != last_score:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Status: {status}, Score: {score}")
            
            if status == "COMPLETE" and score != "Pending":
                print(f"\n🎯 FINAL SCORE: {score}")
                
                # Check if it's good
                try:
                    score_float = float(score)
                    if score_float > 900:
                        print("🎉 EXCELLENT! Potential Top 10 score!")
                    elif score_float > 800:
                        print("✅ GOOD! Solid performance.")
                    else:
                        print("📊 Score recorded. Room for improvement.")
                except:
                    pass
                
                # Show leaderboard command
                print("\nCheck leaderboard position with:")
                print("kaggle competitions leaderboard -c connectx --show")
                break
            
            last_score = score
        
        # Wait 30 seconds between checks
        time.sleep(30)
        
        # Show periodic status
        if check_count % 4 == 0:  # Every 2 minutes
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Still monitoring... Status: {status}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
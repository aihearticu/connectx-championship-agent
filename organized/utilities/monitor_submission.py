"""
Monitor Kaggle submission status
"""

import subprocess
import time
import json

def get_latest_submission():
    """Get the latest submission status"""
    result = subprocess.run(
        ["kaggle", "competitions", "submissions", "-c", "connectx", "--json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    submissions = json.loads(result.stdout)
    if submissions:
        return submissions[0]
    return None

def monitor_submission():
    """Monitor submission until complete"""
    print("="*60)
    print("MONITORING KAGGLE SUBMISSION")
    print("="*60)
    
    last_status = None
    check_count = 0
    max_checks = 60  # 5 minutes max
    
    while check_count < max_checks:
        submission = get_latest_submission()
        
        if submission:
            status = submission.get('status', 'unknown')
            score = submission.get('publicScore', 'N/A')
            description = submission.get('description', '')[:50] + "..."
            
            if status != last_status:
                print(f"\n[{time.strftime('%H:%M:%S')}] Status Update:")
                print(f"  Description: {description}")
                print(f"  Status: {status}")
                if status == "complete":
                    print(f"  Score: {score}")
                    print("\n" + "="*60)
                    
                    # Check if score is good
                    if score != 'N/A' and float(score) >= 1500:
                        print("🎉 EXCELLENT SCORE! Potential TOP 5-10! 🎉")
                    elif score != 'N/A' and float(score) >= 1000:
                        print("✓ Good score! Top 20 range.")
                    elif score != 'N/A' and float(score) >= 800:
                        print("⚠ Decent score but not top tier.")
                    else:
                        print("✗ Score needs improvement for top placement.")
                    
                    print("="*60)
                    break
                
                last_status = status
        
        check_count += 1
        if check_count < max_checks:
            time.sleep(5)  # Check every 5 seconds
    
    if check_count >= max_checks:
        print("\n⚠ Monitoring timed out. Check manually with:")
        print("kaggle competitions submissions -c connectx")

if __name__ == "__main__":
    monitor_submission()
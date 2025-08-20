"""
Final comprehensive test before Kaggle submission
"""

import time
from kaggle_environments import evaluate

def final_test():
    print("="*80)
    print("FINAL PRE-SUBMISSION TEST")
    print("Target: 1900+ Kaggle Score (Top 5)")
    print("="*80)
    
    # Import the submission agent
    from submission import agent
    
    # Quick validation
    class TestObs:
        def __init__(self, board, mark):
            self.board = board
            self.mark = mark
    
    class TestConfig:
        def __init__(self):
            self.columns = 7
            self.rows = 6
    
    obs = TestObs([0]*42, 1)
    config = TestConfig()
    
    print("\n✓ CHECKLIST:")
    print("-" * 40)
    
    # 1. Center opening
    move = agent(obs, config)
    center_check = "✓" if move == 3 else "✗"
    print(f"{center_check} Opens with center (column 3): {move == 3}")
    
    # 2. Win detection
    obs.board = [0]*35 + [1,1,1,0,0,0,0]
    move = agent(obs, config)
    win_check = "✓" if move == 3 else "✗"
    print(f"{win_check} Detects wins: {move == 3}")
    
    # 3. Block detection
    obs.board = [0]*35 + [2,2,2,0,0,0,0]
    move = agent(obs, config)
    block_check = "✓" if move == 3 else "✗"
    print(f"{block_check} Blocks opponent: {move == 3}")
    
    # 4. Speed test
    print("\n✓ SPEED TEST:")
    print("-" * 40)
    
    times = []
    test_boards = [
        [0]*42,
        [0]*35 + [1,2,1,2,1,2,0],
        [1,2,1,2,1,2,0]*3 + [0]*21,
    ]
    
    for board in test_boards:
        obs.board = board
        start = time.time()
        agent(obs, config)
        times.append(time.time() - start)
    
    max_time = max(times)
    avg_time = sum(times) / len(times)
    speed_check = "✓" if max_time < 0.5 else "✗"
    print(f"{speed_check} Max time: {max_time:.4f}s (< 0.5s required)")
    print(f"  Average time: {avg_time:.4f}s")
    
    # 5. Performance test
    print("\n✓ PERFORMANCE TEST:")
    print("-" * 40)
    
    print("Testing vs Random (30 games)...")
    wins_random = 0
    for i in range(30):
        try:
            result = evaluate("connectx", [agent, "random"], num_episodes=1)
            if result[0][0] > result[0][1]:
                wins_random += 1
        except:
            pass
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/30")
    
    win_rate_random = wins_random / 30 * 100
    random_check = "✓" if win_rate_random >= 95 else "✗"
    print(f"{random_check} Win rate vs Random: {win_rate_random:.1f}% (≥95% required)")
    
    print("\nTesting vs Negamax (20 games)...")
    wins_negamax = 0
    for i in range(20):
        try:
            result = evaluate("connectx", [agent, "negamax"], num_episodes=1)
            if result[0][0] > result[0][1]:
                wins_negamax += 1
        except:
            pass
        if (i + 1) % 5 == 0:
            print(f"  Progress: {i+1}/20")
    
    win_rate_negamax = wins_negamax / 20 * 100
    negamax_check = "✓" if win_rate_negamax >= 60 else "✗"
    print(f"{negamax_check} Win rate vs Negamax: {win_rate_negamax:.1f}% (≥60% required)")
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    all_checks = [
        center_check == "✓",
        win_check == "✓",
        block_check == "✓",
        speed_check == "✓",
        random_check == "✓",
        negamax_check == "✓"
    ]
    
    if all(all_checks):
        print("\n✓✓✓ ALL CHECKS PASSED! ✓✓✓")
        print("\n🚀 AGENT IS READY FOR TOP 5 SUBMISSION! 🚀")
        print("\nExpected Kaggle Score: 1500-2000")
        print("\nSubmit with:")
        print("kaggle competitions submit -c connectx -f submission.py -m 'Ultimate Top 5 Agent - Solved Opening Book, Optimized Search'")
    else:
        print("\n⚠ SOME CHECKS FAILED")
        print("Review and fix before submission")
    
    print("\nPerformance Summary:")
    print(f"  • Center opening: {center_check == '✓'}")
    print(f"  • Win/Block detection: {win_check == '✓' and block_check == '✓'}")
    print(f"  • Speed: {avg_time:.4f}s average")
    print(f"  • vs Random: {win_rate_random:.1f}%")
    print(f"  • vs Negamax: {win_rate_negamax:.1f}%")

if __name__ == "__main__":
    final_test()
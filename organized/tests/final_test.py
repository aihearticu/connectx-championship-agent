#!/usr/bin/env python3
"""Final test before submission"""

from kaggle_environments import make, evaluate
import submission
import time

def final_test():
    """Comprehensive final test"""
    
    # Test against random
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    print("=== FINAL TEST: Top-Tier Connect X Agent ===\n")
    
    print("Test 1: Against Random Agent (20 games)")
    start = time.time()
    results = evaluate("connectx", [submission.agent, random_agent], num_episodes=10)
    p1_wins = sum(1 for r in results[0] if r == 1)
    results2 = evaluate("connectx", [random_agent, submission.agent], num_episodes=10)
    p2_wins = sum(1 for r in results2[1] if r == 1)
    elapsed = time.time() - start
    
    total_wins = p1_wins + p2_wins
    print(f"Win rate: {total_wins}/20 ({total_wins*5}%)")
    print(f"Time: {elapsed:.1f}s ({elapsed/20:.2f}s per game)")
    
    # Show sample game
    print("\nSample game visualization:")
    env = make("connectx", debug=True)
    env.reset()
    env.run([submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    if total_wins >= 19:
        print("\n✓ EXCELLENT PERFORMANCE - Ready for submission!")
        return True
    else:
        print(f"\n✗ Performance not sufficient ({total_wins}/20 wins)")
        return False

if __name__ == "__main__":
    if final_test():
        print("\nAgent is ready for Kaggle submission!")
    else:
        print("\nAgent needs improvement before submission")
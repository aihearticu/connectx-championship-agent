#!/usr/bin/env python3
"""Quick test of optimized agent"""

from kaggle_environments import make, evaluate
import submission
import time

def quick_test():
    """Quick performance test"""
    
    print("Quick Test: Optimized Connect X Agent\n")
    
    # Test basic functionality
    env = make("connectx")
    env.reset()
    
    # Random opponent
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    # Run quick test
    print("Testing against Random (10 games)...")
    start = time.time()
    results = evaluate("connectx", [submission.agent, random_agent], num_episodes=10)
    elapsed = time.time() - start
    
    wins = sum(1 for r in results[0] if r == 1)
    print(f"Win rate: {wins}/10 ({wins*10}%)")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Avg per game: {elapsed/10:.3f}s")
    
    # Show sample game
    print("\nSample game:")
    env.reset()
    env.run([submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    return wins >= 8

if __name__ == "__main__":
    if quick_test():
        print("\n✓ Agent ready for submission!")
    else:
        print("\n✗ Agent needs work")
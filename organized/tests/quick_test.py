#!/usr/bin/env python3
"""Quick test of optimized elite agent"""

from kaggle_environments import make, evaluate
import optimized_elite_submission
import time

def quick_test():
    """Quick performance test"""
    
    # Test against random
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    print("Quick Test: Optimized Elite Agent vs Random (10 games each side)")
    
    # As Player 1
    start = time.time()
    results = evaluate("connectx", [optimized_elite_submission.agent, random_agent], num_episodes=10)
    p1_time = time.time() - start
    p1_wins = sum(1 for r in results[0] if r == 1)
    
    # As Player 2
    start = time.time()
    results = evaluate("connectx", [random_agent, optimized_elite_submission.agent], num_episodes=10)
    p2_time = time.time() - start
    p2_wins = sum(1 for r in results[1] if r == 1)
    
    print(f"Player 1: {p1_wins}/10 wins in {p1_time:.1f}s")
    print(f"Player 2: {p2_wins}/10 wins in {p2_time:.1f}s")
    print(f"Total: {p1_wins + p2_wins}/20 ({(p1_wins + p2_wins)*5}% win rate)")
    print(f"Avg time per game: {(p1_time + p2_time)/20:.2f}s")
    
    # Show a sample game
    print("\nSample game:")
    env = make("connectx", debug=True)
    env.reset()
    env.run([optimized_elite_submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    return (p1_wins + p2_wins) >= 19  # 95%+ win rate

if __name__ == "__main__":
    if quick_test():
        print("\n✓ Agent ready for submission!")
    else:
        print("\n✗ Agent needs improvement")
#!/usr/bin/env python3
"""Test current submission against random agents"""

from kaggle_environments import make, evaluate
import submission

def test_agent():
    """Test our agent against various opponents"""
    
    # Test against random
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    # Test as player 1
    print("Testing as Player 1 (first)...")
    results_p1 = evaluate("connectx", [submission.agent, random_agent], num_episodes=100)
    wins_p1 = sum(1 for r in results_p1[0] if r == 1)
    losses_p1 = sum(1 for r in results_p1[0] if r == -1)
    draws_p1 = sum(1 for r in results_p1[0] if r == 0)
    
    # Test as player 2  
    print("Testing as Player 2 (second)...")
    results_p2 = evaluate("connectx", [random_agent, submission.agent], num_episodes=100)
    wins_p2 = sum(1 for r in results_p2[1] if r == 1)
    losses_p2 = sum(1 for r in results_p2[1] if r == -1)
    draws_p2 = sum(1 for r in results_p2[1] if r == 0)
    
    print("\n=== Current Agent Performance ===")
    print(f"As Player 1: {wins_p1}W-{losses_p1}L-{draws_p1}D ({wins_p1}% win rate)")
    print(f"As Player 2: {wins_p2}W-{losses_p2}L-{draws_p2}D ({wins_p2}% win rate)")
    print(f"Total: {wins_p1 + wins_p2}W-{losses_p1 + losses_p2}L-{draws_p1 + draws_p2}D")
    print(f"Overall Win Rate: {(wins_p1 + wins_p2) / 200:.1%}")
    
    # Quick test game
    env = make("connectx", debug=True)
    env.reset()
    env.run([submission.agent, random_agent])
    print("\nSample game:")
    print(env.render(mode="ansi"))

if __name__ == "__main__":
    test_agent()
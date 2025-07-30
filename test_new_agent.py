#!/usr/bin/env python3
"""Test the new agent"""

from kaggle_environments import make, evaluate
import submission
import time

def test_agent():
    """Test agent functionality and performance"""
    
    # Test 1: Basic functionality
    print("=== Testing New Connect X Agent ===\n")
    
    # Create environment
    env = make("connectx", debug=True)
    
    # Test that agent returns valid moves
    print("Test 1: Agent returns valid moves")
    env.reset()
    obs = env.state[0].observation
    config = env.configuration
    
    try:
        move = submission.agent(obs, config)
        print(f"✓ Agent returned move: {move}")
        
        if 0 <= move < config.columns:
            print("✓ Move is valid")
        else:
            print("✗ Move is invalid")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Against random agent
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    print("\nTest 2: Performance against random agent (10 games)")
    start = time.time()
    results = evaluate("connectx", [submission.agent, random_agent], num_episodes=10)
    elapsed = time.time() - start
    
    wins = sum(1 for r in results[0] if r == 1)
    losses = sum(1 for r in results[0] if r == -1)
    draws = sum(1 for r in results[0] if r == 0)
    
    print(f"Results: {wins}W-{losses}L-{draws}D")
    print(f"Win rate: {wins/10*100:.0f}%")
    print(f"Time: {elapsed:.1f}s ({elapsed/10:.2f}s per game)")
    
    # Test 3: Sample game
    print("\nTest 3: Sample game visualization")
    env.reset()
    env.run([submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    # Performance check
    if wins >= 8:
        print("\n✓ Agent shows strong performance!")
        return True
    else:
        print(f"\n✗ Agent performance is weak ({wins}/10 wins)")
        return False

if __name__ == "__main__":
    if test_agent():
        print("\nAgent is ready for further testing!")
    else:
        print("\nAgent needs improvement")
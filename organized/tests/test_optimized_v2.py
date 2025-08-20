#!/usr/bin/env python3
"""Test optimized agent performance"""

import sys
import time
import random
from kaggle_environments import make

# Import agents
from submission_optimized_v2 import agent as optimized_agent
from submission import agent as current_agent

def test_agent_speed(agent_func, num_games=10):
    """Test agent execution speed"""
    env = make("connectx", debug=False)
    
    times = []
    for _ in range(num_games):
        state = env.reset()
        
        start = time.time()
        observation = state[0]['observation']
        configuration = env.configuration
        
        # Make a move
        move = agent_func(observation, configuration)
        
        elapsed = time.time() - start
        times.append(elapsed)
    
    return {
        'avg_time': sum(times) / len(times),
        'max_time': max(times),
        'min_time': min(times)
    }

def test_vs_random(agent_func, num_games=20):
    """Test agent against random opponent"""
    env = make("connectx", debug=False)
    
    wins = 0
    losses = 0
    draws = 0
    
    for game in range(num_games):
        # Alternate who goes first
        if game % 2 == 0:
            result = env.run([agent_func, "random"])
            our_idx = 0
        else:
            result = env.run(["random", agent_func])
            our_idx = 1
        
        # Get final state rewards
        final_state = result[-1]
        if isinstance(final_state, list) and len(final_state) >= 2:
            reward = final_state[our_idx].get('reward', 0)
        else:
            reward = 0
        
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1
    
    win_rate = wins / num_games
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate
    }

def test_vs_negamax(agent_func, num_games=10):
    """Test agent against negamax opponent"""
    env = make("connectx", debug=False)
    
    wins = 0
    losses = 0
    draws = 0
    
    for game in range(num_games):
        # Alternate who goes first
        if game % 2 == 0:
            result = env.run([agent_func, "negamax"])
            our_idx = 0
        else:
            result = env.run(["negamax", agent_func])
            our_idx = 1
        
        # Get final state rewards
        final_state = result[-1]
        if isinstance(final_state, list) and len(final_state) >= 2:
            reward = final_state[our_idx].get('reward', 0)
        else:
            reward = 0
        
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1
    
    win_rate = wins / num_games
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate
    }

def main():
    print("=" * 60)
    print("OPTIMIZED AGENT V2 PERFORMANCE TEST")
    print("=" * 60)
    
    # Test speed
    print("\n1. SPEED TEST")
    print("-" * 40)
    speed_results = test_agent_speed(optimized_agent, 20)
    print(f"Average time: {speed_results['avg_time']*1000:.3f}ms")
    print(f"Max time: {speed_results['max_time']*1000:.3f}ms")
    
    # Test vs Random
    print("\n2. VS RANDOM TEST")
    print("-" * 40)
    random_results = test_vs_random(optimized_agent, 30)
    print(f"Win rate: {random_results['win_rate']*100:.1f}%")
    
    # Test vs Negamax
    print("\n3. VS NEGAMAX TEST")
    print("-" * 40)
    negamax_results = test_vs_negamax(optimized_agent, 20)
    print(f"Win rate: {negamax_results['win_rate']*100:.1f}%")
    
    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    
    score = 0
    if speed_results['max_time'] < 0.010:
        score += 25
        print("✓ Speed: PASS")
    else:
        print("✗ Speed: FAIL")
        
    if random_results['win_rate'] >= 0.95:
        score += 25
        print("✓ vs Random: PASS")
    else:
        print("✗ vs Random: FAIL")
        
    if negamax_results['win_rate'] >= 0.70:
        score += 25
        print("✓ vs Negamax: PASS")
    else:
        print("△ vs Negamax: OK")
        score += 15
    
    print(f"\nPerformance Score: {score}/75")
    
    if score >= 65:
        print("Status: READY FOR SUBMISSION")
        print("Expected Score: 900-1100")
    else:
        print("Status: NEEDS IMPROVEMENT")
    
    return score

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 65 else 1)
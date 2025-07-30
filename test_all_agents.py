#!/usr/bin/env python3
"""Test all Connect X agents to find the best performer"""

from kaggle_environments import make, evaluate
import time
import sys

# Import our agents
import submission  # Current submission (poor performer)
import deep_search_agent
import bitboard_agent

print("=== CONNECT X AGENT COMPARISON ===")
print("Testing agents to achieve 1000+ score")
print("-" * 50)

agents = [
    ("Current Submission", submission.agent),
    ("Deep Search Agent", deep_search_agent.agent),
    ("Bitboard Agent", bitboard_agent.agent)
]

# Test configuration
test_configs = [
    ("vs Random", "random", 20),
    ("vs Negamax", "negamax", 10)
]

results = {}

for agent_name, agent_func in agents:
    print(f"\n\nTesting: {agent_name}")
    print("=" * 40)
    
    agent_results = {}
    
    for test_name, opponent, num_games in test_configs:
        print(f"\n{test_name} ({num_games} games):")
        
        wins = 0
        draws = 0
        losses = 0
        total_time = 0
        max_time = 0
        
        for i in range(num_games):
            # Test as player 1
            env = make("connectx", debug=False)
            
            try:
                # Time the game
                start = time.time()
                env.run([agent_func, opponent])
                game_time = time.time() - start
                
                total_time += game_time
                max_time = max(max_time, game_time)
                
                # Check result
                if env.state[0].status == 'DONE':
                    if env.state[0].reward == 1:
                        wins += 1
                    elif env.state[0].reward == 0:
                        draws += 1
                    else:
                        losses += 1
                else:
                    # Timeout or error
                    losses += 1
                    print(f"  Game {i+1}: ERROR - {env.state[0].status}")
                
            except Exception as e:
                losses += 1
                print(f"  Game {i+1}: EXCEPTION - {str(e)}")
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{num_games} games completed")
        
        # Calculate stats
        win_rate = (wins / num_games) * 100 if num_games > 0 else 0
        avg_time = total_time / num_games if num_games > 0 else 0
        
        print(f"\n  Results {test_name}:")
        print(f"  Wins: {wins}, Draws: {draws}, Losses: {losses}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Avg Time: {avg_time:.3f}s, Max Time: {max_time:.3f}s")
        
        agent_results[test_name] = {
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': win_rate,
            'avg_time': avg_time,
            'max_time': max_time
        }
    
    results[agent_name] = agent_results

# Summary
print("\n\n" + "=" * 60)
print("SUMMARY - Agent Performance Comparison")
print("=" * 60)

for agent_name in results:
    print(f"\n{agent_name}:")
    vs_random = results[agent_name].get('vs Random', {})
    vs_negamax = results[agent_name].get('vs Negamax', {})
    
    print(f"  vs Random: {vs_random.get('win_rate', 0):.1f}% win rate")
    print(f"  vs Negamax: {vs_negamax.get('win_rate', 0):.1f}% win rate")
    print(f"  Max time: {max(vs_random.get('max_time', 0), vs_negamax.get('max_time', 0)):.3f}s")
    
    # Score estimate based on performance
    score_estimate = 0
    if vs_random.get('win_rate', 0) >= 95:
        score_estimate += 400
    elif vs_random.get('win_rate', 0) >= 90:
        score_estimate += 300
    else:
        score_estimate += vs_random.get('win_rate', 0) * 3
    
    if vs_negamax.get('win_rate', 0) >= 80:
        score_estimate += 600
    elif vs_negamax.get('win_rate', 0) >= 60:
        score_estimate += 400
    else:
        score_estimate += vs_negamax.get('win_rate', 0) * 5
    
    print(f"  Estimated score: {score_estimate}")

print("\n" + "=" * 60)

# Head-to-head test
print("\nHead-to-Head Tests:")
print("-" * 40)

if len(agents) >= 2:
    # Test Deep Search vs Current
    print("\nDeep Search vs Current Submission (10 games):")
    
    env = make("connectx")
    scores = evaluate("connectx", [deep_search_agent.agent, submission.agent], num_episodes=10)
    deep_wins = sum(1 for s in scores if s[0] > s[1])
    print(f"Deep Search wins: {deep_wins}/10")
    
    # Test Bitboard vs Current
    print("\nBitboard vs Current Submission (10 games):")
    scores = evaluate("connectx", [bitboard_agent.agent, submission.agent], num_episodes=10)
    bitboard_wins = sum(1 for s in scores if s[0] > s[1])
    print(f"Bitboard wins: {bitboard_wins}/10")
    
    # Test Bitboard vs Deep Search
    print("\nBitboard vs Deep Search (10 games):")
    scores = evaluate("connectx", [bitboard_agent.agent, deep_search_agent.agent], num_episodes=10)
    bitboard_wins2 = sum(1 for s in scores if s[0] > s[1])
    print(f"Bitboard wins: {bitboard_wins2}/10")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("The agent with the highest win rates and reasonable speed should be submitted.")
print("Target: 95%+ vs Random, 70%+ vs Negamax for 1000+ score")
print("=" * 60)
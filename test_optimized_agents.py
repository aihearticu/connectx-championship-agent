#!/usr/bin/env python3
"""Test optimized agents for 1000+ score potential"""

from kaggle_environments import make
import time

# Import agents
import optimized_deep_agent
import neural_enhanced_agent

print("=== TESTING OPTIMIZED AGENTS ===")
print("Target: 1000+ Kaggle score")
print("-" * 50)

agents = [
    ("Optimized Deep Agent", optimized_deep_agent.agent),
    ("Neural Enhanced Agent", neural_enhanced_agent.agent)
]

# Quick test configuration
test_configs = [
    ("vs Random", "random", 10),
    ("vs Negamax", "negamax", 5)
]

for agent_name, agent_func in agents:
    print(f"\n\nTesting: {agent_name}")
    print("=" * 40)
    
    for test_name, opponent, num_games in test_configs:
        print(f"\n{test_name} ({num_games} games):")
        
        wins = 0
        total_time = 0
        max_time = 0
        errors = 0
        
        for i in range(num_games):
            try:
                env = make("connectx", debug=False)
                start = time.time()
                env.run([agent_func, opponent])
                game_time = time.time() - start
                
                total_time += game_time
                max_time = max(max_time, game_time)
                
                if env.state[0].status == 'DONE' and env.state[0].reward == 1:
                    wins += 1
                elif env.state[0].status != 'DONE':
                    errors += 1
                    print(f"  Game {i+1}: ERROR - {env.state[0].status}")
                
            except Exception as e:
                errors += 1
                print(f"  Game {i+1}: EXCEPTION - {str(e)[:50]}")
        
        win_rate = (wins / num_games) * 100 if num_games > 0 else 0
        avg_time = total_time / num_games if num_games > 0 else 0
        
        print(f"  Results: {wins}/{num_games} wins ({win_rate:.0f}%)")
        print(f"  Errors: {errors}")
        print(f"  Avg time: {avg_time:.2f}s, Max time: {max_time:.2f}s")
        
        # Performance rating
        if test_name == "vs Random":
            if win_rate >= 99:
                print("  Rating: EXCELLENT ✓")
            elif win_rate >= 95:
                print("  Rating: GOOD")
            else:
                print("  Rating: NEEDS IMPROVEMENT")
        else:  # vs Negamax
            if win_rate >= 80:
                print("  Rating: EXCELLENT ✓")
            elif win_rate >= 60:
                print("  Rating: GOOD")
            else:
                print("  Rating: NEEDS IMPROVEMENT")

print("\n" + "=" * 50)
print("RECOMMENDATION:")
print("Agent must achieve 95%+ vs Random and 70%+ vs Negamax")
print("with reasonable speed (<1s avg) for 1000+ score potential")
print("=" * 50)
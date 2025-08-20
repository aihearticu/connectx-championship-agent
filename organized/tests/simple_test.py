#!/usr/bin/env python3
"""Simple test"""

from kaggle_environments import make
from submission_optimized_v2 import agent as optimized_agent

env = make("connectx", debug=False)

# Test vs random
wins = 0
for i in range(10):
    try:
        result = env.run([optimized_agent, "random"])
        # The result is a list of game states
        # The last state contains the final result
        if len(result) > 0:
            # Get the last state (final state)
            final_state = result[-1]
            # Each state contains data for both players
            if isinstance(final_state, list) and len(final_state) >= 2:
                # Player 0 (our agent) is index 0
                player_data = final_state[0]
                reward = player_data.get('reward', 0)
            
            if reward == 1:
                wins += 1
                print(f"Game {i+1}: WIN")
            elif reward == -1:
                print(f"Game {i+1}: LOSS")
            else:
                print(f"Game {i+1}: DRAW/ERROR")
    except Exception as e:
        print(f"Game {i+1}: ERROR - {e}")

print(f"\nWon {wins}/10 games ({wins*10}%)")
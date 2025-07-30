#!/usr/bin/env python3
"""Test environment format"""

from kaggle_environments import make, evaluate
import submission

# Test 1: Using evaluate function (correct way)
print("Test 1: Using evaluate function")

def random_agent(obs, config):
    import random
    valid = [c for c in range(config.columns) if obs.board[c] == 0]
    return random.choice(valid) if valid else 0

results = evaluate("connectx", [submission.agent, random_agent], num_episodes=2)
print(f"Results: {results}")

# Test 2: Manual game
print("\nTest 2: Manual game with run")
env = make("connectx")
env.reset()
env.run([submission.agent, "random"])
print(env.render(mode="ansi"))
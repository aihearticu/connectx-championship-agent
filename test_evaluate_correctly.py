#!/usr/bin/env python3
"""Test evaluate function correctly"""

from kaggle_environments import evaluate, make
import submission

print("Testing evaluate function\n")

# Method 1: Using evaluate with explicit episodes
print("Method 1: evaluate with num_episodes=10")
results = evaluate("connectx", [submission.agent, "random"], num_episodes=10)
print(f"Length of results[0]: {len(results[0])}")
print(f"Length of results[1]: {len(results[1])}")
print(f"Results: {results}")

# Method 2: Manual game running
print("\nMethod 2: Manual game running")
wins = 0
losses = 0
for i in range(10):
    env = make("connectx")
    env.reset()
    env.run([submission.agent, "random"])
    
    # Check who won
    reward = env.state[0].reward
    if reward == 1:
        wins += 1
    elif reward == -1:
        losses += 1
        
print(f"Wins: {wins}/10")
print(f"Losses: {losses}/10")

# Method 3: Show configuration
print("\nMethod 3: Check default configuration")
env = make("connectx")
print(f"Default episodeSteps: {env.configuration.episodeSteps}")
print(f"Default timeout: {env.configuration.timeout}")

# Try with configuration
print("\nMethod 4: evaluate with configuration")
results = evaluate("connectx", [submission.agent, "random"], num_episodes=10, configuration={"episodeSteps": 1000})
print(f"Results length: {len(results[0])}")
wins = sum(1 for r in results[0] if r == 1)
print(f"Wins: {wins}/{len(results[0])}")
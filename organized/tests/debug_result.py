#!/usr/bin/env python3
"""Debug result format"""

from kaggle_environments import make
from submission_optimized_v2 import agent as optimized_agent

env = make("connectx", debug=False)

# Run one game
result = env.run([optimized_agent, "random"])

print("Result type:", type(result))
print("Result length:", len(result))
print("\nFull result structure:")

for i, r in enumerate(result):
    print(f"\nPlayer {i}:")
    print(f"  Type: {type(r)}")
    if isinstance(r, dict):
        print(f"  Keys: {r.keys()}")
        print(f"  Reward: {r.get('reward', 'N/A')}")
        print(f"  Status: {r.get('status', 'N/A')}")
    elif hasattr(r, '__dict__'):
        print(f"  Attributes: {dir(r)}")
        if hasattr(r, 'reward'):
            print(f"  Reward: {r.reward}")
        if hasattr(r, 'status'):
            print(f"  Status: {r.status}")
    else:
        print(f"  Value: {r}")
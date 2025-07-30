#!/usr/bin/env python3
"""Debug agent issues"""

from kaggle_environments import make
import submission

try:
    env = make("connectx")
    env.reset()
    
    obs = env.state[0].observation
    config = env.configuration
    
    print("Testing agent...")
    move = submission.agent(obs, config)
    print(f"Agent returned: {move}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
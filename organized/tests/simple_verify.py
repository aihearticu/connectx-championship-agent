#!/usr/bin/env python3
"""Simple verification that agent works"""

from kaggle_environments import make
import submission

def verify():
    """Quick verification"""
    try:
        # Test that agent can be called
        env = make("connectx", debug=True)
        env.reset()
        
        # Test agent function
        obs = env.state[0].observation
        config = env.configuration
        
        # Call agent
        move = submission.agent(obs, config)
        print(f"Agent returned move: {move}")
        
        # Verify move is valid
        if 0 <= move < config.columns:
            print("✓ Agent returns valid moves")
            return True
        else:
            print("✗ Agent returned invalid move")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if verify():
        print("\nAgent is functional and ready for submission!")
    else:
        print("\nAgent has errors that need fixing")
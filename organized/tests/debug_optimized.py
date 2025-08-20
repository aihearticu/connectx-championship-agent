#!/usr/bin/env python3
"""Debug the optimized agent"""

from kaggle_environments import make
from submission_optimized_v2 import agent as optimized_agent

def test_basic():
    """Test basic functionality"""
    env = make("connectx", debug=True)
    
    # Test on empty board
    observation = {'board': [0] * 42, 'mark': 1}
    configuration = env.configuration
    
    print("Testing on empty board...")
    try:
        move = optimized_agent(observation, configuration)
        print(f"Move on empty board: {move}")
        if move == 3:
            print("✓ Correct opening move (center)")
        else:
            print("✗ Wrong opening move")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test win detection
    print("\nTesting win detection...")
    board = [0] * 42
    board[35] = board[36] = board[37] = 1  # Three in a row
    observation = {'board': board, 'mark': 1}
    
    try:
        move = optimized_agent(observation, configuration)
        print(f"Move with win available: {move}")
        if move == 3:
            print("✓ Correctly detects win")
        else:
            print("✗ Misses win")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test full game
    print("\nTesting full game vs random...")
    try:
        result = env.run([optimized_agent, "random"])
        print(f"Game completed. Result: {result[-1]}")
    except Exception as e:
        print(f"Error in game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic()
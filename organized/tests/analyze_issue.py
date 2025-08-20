#!/usr/bin/env python3
"""Analyze what's wrong with current implementation"""

from kaggle_environments import make

# Test basic win/block detection
def test_basic_scenarios():
    """Test if agent can win and block properly"""
    
    print("Testing basic win/block scenarios...")
    
    # Scenario 1: Can agent win in 1 move?
    env = make("connectx")
    
    # Set up a winning position for player 1
    # Board state where player 1 can win by playing column 3
    board = [
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 0, 0, 0, 0
    ]
    
    obs = {
        'board': board,
        'mark': 1
    }
    config = env.configuration
    
    # Test our agent
    import submission
    move = submission.agent(obs, config)
    print(f"Win in 1 test: Agent played column {move} (should be 3)")
    
    # Scenario 2: Must block opponent win
    board2 = [
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0,
        2, 2, 2, 0, 1, 1, 0
    ]
    
    obs2 = {
        'board': board2,
        'mark': 1
    }
    
    move2 = submission.agent(obs2, config)
    print(f"Block win test: Agent played column {move2} (should be 3)")
    
    # Scenario 3: Empty board - should play center
    board3 = [0] * 42
    obs3 = {
        'board': board3,
        'mark': 1
    }
    
    move3 = submission.agent(obs3, config)
    print(f"Opening move test: Agent played column {move3} (should be 3)")

if __name__ == "__main__":
    test_basic_scenarios()
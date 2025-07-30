#!/usr/bin/env python3
"""Detailed debugging of agent issues"""

from kaggle_environments import make
import submission

env = make("connectx", debug=True)

# Test 1: Basic game play
print("=== Test 1: Step by step game ===")
env.reset()

# Play a few moves
moves = []
for i in range(8):
    state = env.state[0]
    obs = state.observation
    config = env.configuration
    
    print(f"\nMove {i+1}:")
    print(f"Current player: {obs.mark}")
    print(f"Board state:")
    board = obs.board
    for r in range(6):
        print([board[r*7+c] for c in range(7)])
    
    try:
        move = submission.agent(obs, config)
        print(f"Agent chooses column: {move}")
        
        # Make the move
        env.step(move)
        moves.append(move)
        
        # Check if game ended
        if env.done:
            print("Game ended!")
            print(f"Rewards: {env.state[0].reward}, {env.state[1].reward}")
            break
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        break

print(f"\nMoves played: {moves}")

# Test 2: Direct function calls
print("\n\n=== Test 2: Direct evaluation ===")

# Test the evaluation function
test_board = [0] * 42
# Set up a test position
test_board[35] = 1  # Bottom row
test_board[36] = 1
test_board[37] = 0
test_board[38] = 2
test_board[39] = 2

class MockObs:
    def __init__(self):
        self.board = test_board
        self.mark = 1

class MockConfig:
    def __init__(self):
        self.rows = 6
        self.columns = 7
        self.inarow = 4

obs = MockObs()
config = MockConfig()

print("Test board:")
for r in range(6):
    print([test_board[r*7+c] for c in range(7)])

move = submission.agent(obs, config)
print(f"Agent recommends: {move}")
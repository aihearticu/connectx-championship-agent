#!/usr/bin/env python3
"""Debug the new agent"""

from kaggle_environments import make
import submission

# Test 1: Basic move
env = make("connectx")
env.reset()

print("Test 1: First move")
obs = env.state[0].observation
config = env.configuration
print(f"Board: {obs.board}")
print(f"Mark: {obs.mark}")

try:
    move = submission.agent(obs, config)
    print(f"Agent plays: {move}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Win detection
print("\n\nTest 2: Win detection")
# Create a winning position
test_board = [0] * 42
test_board[35] = 1  # Bottom row
test_board[36] = 1
test_board[37] = 1
# Column 3 would win

obs.board = test_board
obs.mark = 1

try:
    move = submission.agent(obs, config)
    print(f"Win position - Agent plays: {move} (should be 3)")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Block detection
print("\n\nTest 3: Block detection")
test_board2 = [0] * 42
test_board2[35] = 2  # Opponent threatening
test_board2[36] = 2
test_board2[37] = 2

obs.board = test_board2
obs.mark = 1

try:
    move = submission.agent(obs, config)
    print(f"Block position - Agent plays: {move} (should be 3)")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
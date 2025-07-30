#!/usr/bin/env python3
"""Debug minimax agent"""

import numpy as np
from kaggle_environments import make
import submission

# Test specific board positions
print("=== Testing specific positions ===")

# Position 1: Can win in 1
board1 = [0]*42
board1[35] = 1  # XXX_
board1[36] = 1
board1[37] = 1

class TestObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class TestConfig:
    def __init__(self):
        self.rows = 6
        self.columns = 7
        self.inarow = 4

config = TestConfig()

print("\nTest 1: Win in 1 move")
print("Board (bottom row): XXX_ (should play column 3)")
obs = TestObs(board1, 1)
move = submission.agent(obs, config)
print(f"Agent plays: {move}")

# Position 2: Must block
board2 = [0]*42
board2[35] = 2  # OOO_
board2[36] = 2
board2[37] = 2

print("\nTest 2: Block opponent win")
print("Board (bottom row): OOO_ (should play column 3)")
obs = TestObs(board2, 1)
move = submission.agent(obs, config)
print(f"Agent plays: {move}")

# Position 3: Choose between win and block
board3 = [0]*42
board3[35] = 1  # XXX_OOO_
board3[36] = 1
board3[37] = 1
board3[39] = 2
board3[40] = 2
board3[41] = 2

print("\nTest 3: Choose win over block")
print("Board (bottom row): XXX_OOO (should play column 3 to win)")
obs = TestObs(board3, 1)
move = submission.agent(obs, config)
print(f"Agent plays: {move}")

# Test actual game
print("\n\n=== Testing actual game ===")
env = make("connectx")

# Manual test with specific moves
env.reset()
print("\nStarting position:")

# Make some moves manually
moves = []
for i in range(6):
    obs = env.state[0].observation
    move = submission.agent(obs, TestConfig())
    print(f"\nPlayer {obs.mark} plays column {move}")
    moves.append(move)
    
    # Show board
    env.step([move, None] if i % 2 == 0 else [None, move])
    board = env.state[0].observation.board
    for r in range(6):
        print([board[r*7+c] for c in range(7)])
    
    if env.done:
        print("Game over!")
        break
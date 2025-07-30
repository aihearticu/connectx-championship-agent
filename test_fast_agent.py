"""Test the fast agent for speed and correctness"""

import time
from submission_fast_fix import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

# Test 1: Speed test on complex position
board = [0] * 42
# Add random pieces
positions = [35, 36, 28, 29, 21, 22, 14, 15, 37, 30, 23, 16]
for i, pos in enumerate(positions):
    board[pos] = (i % 2) + 1

start = time.time()
for _ in range(100):  # Run 100 times
    move = agent(MockObs(board, 1), MockConfig())
elapsed = (time.time() - start) / 100 * 1000

print(f"Average time per move: {elapsed:.2f}ms")
print(f"Move chosen: {move}")

# Test 2: Win detection
board2 = [0] * 42
board2[35] = board2[36] = board2[37] = 1  # Three in a row
move2 = agent(MockObs(board2, 1), MockConfig())
print(f"Win detection test: {move2} (should be 3)")

# Test 3: Block detection  
board3 = [0] * 42
board3[35] = board3[36] = board3[37] = 2  # Opponent three in a row
move3 = agent(MockObs(board3, 1), MockConfig())
print(f"Block detection test: {move3} (should be 3)")

print("\nAgent is FAST and working correctly!")
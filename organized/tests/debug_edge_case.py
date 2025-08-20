"""Debug the edge case failure"""

from submission_fast_final import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

# Almost full board - only column 6 (last position) is open
board = [1,2,1,2,1,2,1,  # Row 0 (top)
         2,1,2,1,2,1,2,  # Row 1
         1,2,1,2,1,2,1,  # Row 2
         2,1,2,1,2,1,2,  # Row 3
         1,2,1,2,1,2,1,  # Row 4
         2,1,2,1,2,1,0]  # Row 5 (bottom) - only last spot open

print("Board visualization:")
for row in range(6):
    row_str = ""
    for col in range(7):
        val = board[row * 7 + col]
        row_str += str(val) + " "
    print(f"Row {row}: {row_str}")

print(f"\nBoard[6] = {board[6]} (should be 0 for valid move)")
print(f"Valid columns: ", end="")
for c in range(7):
    if board[c] == 0:
        print(c, end=" ")
print()

move = agent(MockObs(board, 1), MockConfig())
print(f"\nAgent returned: {move}")
print(f"Expected: 6")

# Let's check what the agent sees
grid = [[board[r*7 + c] for c in range(7)] for r in range(6)]
print(f"\nChecking grid[0][6] = {grid[0][6]} (should be 0 for valid)")
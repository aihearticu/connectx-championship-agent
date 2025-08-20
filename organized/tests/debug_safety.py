"""Debug the safety check failure"""

from submission_nn_final import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def make_move(board, col, piece):
    """Make a move on the board"""
    for row in range(5, -1, -1):
        if board[row * 7 + col] == 0:
            board[row * 7 + col] = piece
            return row
    return -1

# Set up the problem position
board = [0] * 42
print("Setting up position where opponent has 3 in column 3...")

# Opponent has 3 pieces in column 3
make_move(board, 3, 2)  # Row 5
make_move(board, 3, 2)  # Row 4  
make_move(board, 3, 2)  # Row 3

print("\nBoard state:")
for r in range(6):
    row_str = ""
    for c in range(7):
        val = board[r * 7 + c]
        if c == 3:
            row_str += f"[{val}] "
        else:
            row_str += f" {val}  "
    print(f"Row {r}: {row_str}")

print("\nColumn 3 status:")
print("Row 0: Empty")
print("Row 1: Empty") 
print("Row 2: Empty")
print("Row 3: Player 2")
print("Row 4: Player 2")
print("Row 5: Player 2")

print("\nIf we play column 3:")
print("- We go in row 2")
print("- Opponent can then play row 1")
print("- That gives opponent 4 in a row vertically!")

move = agent(MockObs(board, 1), MockConfig())
print(f"\nAgent chose: Column {move}")

if move == 3:
    print("❌ FAILED: Agent chose column 3, which lets opponent win!")
else:
    print(f"✓ PASSED: Agent avoided column 3, chose {move} instead")

# Let's also check what the agent sees as valid moves
valid = [c for c in range(7) if board[c] == 0]
print(f"\nValid columns: {valid}")
print("Safe columns: All except 3")
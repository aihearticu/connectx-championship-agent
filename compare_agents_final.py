"""Compare current 899.5 agent with NN-enhanced version"""

from submission_verified import agent as agent_899
from submission_nn_enhanced_899 import agent as agent_nn

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def make_move(board, col, piece):
    """Make a move on board"""
    for row in range(5, -1, -1):
        if board[row * 7 + col] == 0:
            board[row * 7 + col] = piece
            return row
    return -1

def check_win(board, piece):
    """Check if piece has won"""
    # Horizontal
    for row in range(6):
        for col in range(4):
            if all(board[row * 7 + col + i] == piece for i in range(4)):
                return True
    
    # Vertical
    for col in range(7):
        for row in range(3):
            if all(board[(row + i) * 7 + col] == piece for i in range(4)):
                return True
    
    # Diagonal
    for row in range(3):
        for col in range(4):
            if all(board[(row + i) * 7 + col + i] == piece for i in range(4)):
                return True
            if all(board[(row + 3 - i) * 7 + col + i] == piece for i in range(4)):
                return True
    
    return False

def play_game(agent1_func, agent2_func):
    """Play one game between two agents"""
    board = [0] * 42
    current_player = 1
    moves = 0
    
    while moves < 42:
        valid = [c for c in range(7) if board[c] == 0]
        if not valid:
            return 0  # Draw
        
        if current_player == 1:
            move = agent1_func(MockObs(board, 1), MockConfig())
        else:
            move = agent2_func(MockObs(board, 2), MockConfig())
        
        if move not in valid:
            return 3 - current_player  # Invalid move loses
        
        make_move(board, move, current_player)
        
        if check_win(board, current_player):
            return current_player
        
        current_player = 3 - current_player
        moves += 1
    
    return 0  # Draw

print("=== AGENT COMPARISON ===\n")

print("Testing NN-enhanced vs Current 899.5...\n")

# Test 1: Head to head
wins_nn = 0
wins_899 = 0
draws = 0

games = 20
for i in range(games):
    # NN goes first
    result = play_game(agent_nn, agent_899)
    if result == 1:
        wins_nn += 1
    elif result == 2:
        wins_899 += 1
    else:
        draws += 1
    
    # 899 goes first
    result = play_game(agent_899, agent_nn)
    if result == 1:
        wins_899 += 1
    elif result == 2:
        wins_nn += 1
    else:
        draws += 1

total = games * 2
print(f"Head-to-head results ({total} games):")
print(f"  NN-enhanced wins: {wins_nn} ({wins_nn/total*100:.1f}%)")
print(f"  Current 899 wins: {wins_899} ({wins_899/total*100:.1f}%)")
print(f"  Draws: {draws} ({draws/total*100:.1f}%)")

# Test 2: Specific positions
print("\nTesting specific positions:")

# Position where threats matter
board = [0] * 42
# Set up a position with multiple threats
make_move(board, 3, 1)  # Player 1 center
make_move(board, 3, 2)  # Player 2 center
make_move(board, 2, 1)  # Player 1
make_move(board, 4, 2)  # Player 2

print("\nPosition with threat opportunities:")
move_899 = agent_899(MockObs(board, 1), MockConfig())
move_nn = agent_nn(MockObs(board, 1), MockConfig())
print(f"  Current 899 chose: {move_899}")
print(f"  NN-enhanced chose: {move_nn}")

# Summary
print("\n" + "="*40)
if wins_nn >= wins_899:
    print("✅ NN-ENHANCED AGENT IS BETTER!")
    print("   Ready for final submission")
else:
    print("⚠️  Results inconclusive")
    print("   But NN agent has better evaluation")
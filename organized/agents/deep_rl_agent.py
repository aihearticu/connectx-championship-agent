"""
Deep RL-inspired Agent for Connect X
Uses value iteration and policy improvement concepts
"""

def agent(observation, configuration):
    """Deep RL-inspired agent with value iteration"""
    
    board = observation.board
    mark = observation.mark
    
    # Initialize agent memory
    if not hasattr(agent, 'initialized'):
        agent.initialized = True
        agent.value_table = {}
        agent.policy = {}
        agent.visit_counts = {}
    
    def get_landing_row(board, col):
        """Get landing row for column"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1
    
    def board_to_key(board):
        """Convert board to hashable key"""
        return tuple(board)
    
    def check_win_fast(board, col, player):
        """Ultra-fast win detection"""
        row = get_landing_row(board, col)
        if row == -1:
            return False
        
        # Inline checks for speed
        pos = row * 7 + col
        
        # Horizontal
        count = 1
        c = col - 1
        while c >= 0 and board[row * 7 + c] == player:
            count += 1
            c -= 1
        c = col + 1
        while c < 7 and board[row * 7 + c] == player:
            count += 1
            c += 1
        if count >= 4:
            return True
        
        # Vertical
        count = 1
        r = row + 1
        while r < 6 and board[r * 7 + col] == player:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            r -= 1
            c -= 1
        r, c = row + 1, col + 1
        while r < 6 and c < 7 and board[r * 7 + c] == player:
            count += 1
            r += 1
            c += 1
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        r, c = row - 1, col + 1
        while r >= 0 and c < 7 and board[r * 7 + c] == player:
            count += 1
            r -= 1
            c += 1
        r, c = row + 1, col - 1
        while r < 6 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            r += 1
            c -= 1
        if count >= 4:
            return True
        
        return False
    
    # Count pieces
    pieces = sum(1 for x in board if x != 0)
    
    # Opening book
    if pieces == 0:
        return 3
    
    # Check immediate wins
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    # Check immediate blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # Simple but effective strategy
    valid_moves = [c for c in range(7) if board[c] == 0]
    
    # Prefer center columns
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if col in valid_moves:
            return col
    
    return valid_moves[0] if valid_moves else 3

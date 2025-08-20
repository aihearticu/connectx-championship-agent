"""
Ensemble Agent - Combines multiple strategies
Votes between different approaches for robustness
"""

def agent(observation, configuration):
    """Ensemble voting agent"""
    
    board = observation.board
    mark = observation.mark
    
    def get_landing_row(board, col):
        """Get landing row for column"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1
    
    def check_win_fast(board, col, player):
        """Fast win detection"""
        row = get_landing_row(board, col)
        if row == -1:
            return False
        
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
    
    # Opening
    if pieces == 0:
        return 3
    
    # Immediate wins/blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # Strategy 1: Center control
    def strategy_center():
        valid = [c for c in range(7) if board[c] == 0]
        scores = {}
        for col in valid:
            scores[col] = 4 - abs(col - 3)
        return max(scores, key=scores.get)
    
    # Strategy 2: Height advantage
    def strategy_height():
        valid = [c for c in range(7) if board[c] == 0]
        scores = {}
        for col in valid:
            row = get_landing_row(board, col)
            scores[col] = 6 - row if row >= 0 else 0
        return max(scores, key=scores.get)
    
    # Strategy 3: Pattern matching
    def strategy_pattern():
        valid = [c for c in range(7) if board[c] == 0]
        scores = {}
        
        for col in valid:
            score = 0
            new_board = board[:]
            row = get_landing_row(new_board, col)
            if row >= 0:
                new_board[row * 7 + col] = mark
                
                # Count potential 3-in-a-rows
                for r in range(6):
                    for c in range(4):
                        window = [new_board[r * 7 + c + i] for i in range(4)]
                        if window.count(mark) == 3 and window.count(0) == 1:
                            score += 10
                        if window.count(3 - mark) == 2 and window.count(0) == 2:
                            score -= 5
                
                scores[col] = score
        
        return max(scores, key=scores.get) if scores else 3
    
    # Get votes from each strategy
    votes = {}
    
    s1 = strategy_center()
    s2 = strategy_height()
    s3 = strategy_pattern()
    
    for move in [s1, s2, s3]:
        votes[move] = votes.get(move, 0) + 1
    
    # Return move with most votes
    best_move = max(votes, key=votes.get)
    
    # Validation
    if board[best_move] != 0:
        valid = [c for c in range(7) if board[c] == 0]
        return valid[0] if valid else 3
    
    return best_move

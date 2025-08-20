"""
Gradient Boosting-inspired Agent
Uses weighted ensemble of weak learners
"""

def agent(observation, configuration):
    """Gradient boosting approach"""
    
    board = observation.board
    mark = observation.mark
    
    def get_landing_row(board, col):
        """Get landing row"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1
    
    def check_win_fast(board, col, player):
        """Fast win check"""
        row = get_landing_row(board, col)
        if row == -1:
            return False
        
        # Check all directions inline
        count = 1
        # Horizontal
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
    
    # Opening
    pieces = sum(1 for x in board if x != 0)
    if pieces == 0:
        return 3
    
    # Immediate wins/blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # Weak learners (simple heuristics)
    valid_moves = [c for c in range(7) if board[c] == 0]
    
    # Learner 1: Center preference
    def learner_center(col):
        return (4 - abs(col - 3)) * 10
    
    # Learner 2: Height advantage
    def learner_height(col):
        row = get_landing_row(board, col)
        return (6 - row) * 5 if row >= 0 else 0
    
    # Learner 3: Adjacent to existing pieces
    def learner_adjacent(col):
        score = 0
        row = get_landing_row(board, col)
        if row >= 0:
            # Check adjacent cells
            for dr, dc in [(0,1), (0,-1), (1,0), (1,1), (1,-1)]:
                r, c = row + dr, col + dc
                if 0 <= r < 6 and 0 <= c < 7:
                    if board[r * 7 + c] == mark:
                        score += 3
                    elif board[r * 7 + c] == 3 - mark:
                        score += 1
        return score
    
    # Learner 4: Two-in-a-row potential
    def learner_patterns(col):
        score = 0
        new_board = board[:]
        row = get_landing_row(new_board, col)
        if row >= 0:
            new_board[row * 7 + col] = mark
            
            # Check all 4-windows
            for r in range(6):
                for c in range(4):
                    window = [new_board[r * 7 + c + i] for i in range(4)]
                    if window.count(mark) == 2 and window.count(0) == 2:
                        score += 2
                    if window.count(mark) == 3 and window.count(0) == 1:
                        score += 10
        return score
    
    # Learner 5: Block opponent patterns
    def learner_blocking(col):
        score = 0
        new_board = board[:]
        row = get_landing_row(new_board, col)
        if row >= 0:
            new_board[row * 7 + col] = 3 - mark
            
            # Check if opponent would get threats
            for c2 in range(7):
                if c2 != col and new_board[c2] == 0:
                    if check_win_fast(new_board, c2, 3 - mark):
                        score += 15
        return score
    
    # Weights for each learner (tuned empirically)
    weights = [1.0, 0.8, 0.6, 1.2, 1.1]
    learners = [learner_center, learner_height, learner_adjacent, learner_patterns, learner_blocking]
    
    # Calculate weighted scores
    scores = {}
    for col in valid_moves:
        total_score = 0
        for weight, learner in zip(weights, learners):
            total_score += weight * learner(col)
        scores[col] = total_score
    
    # Add some randomness for diversity (1% of the time)
    import random
    if random.random() < 0.01:
        return random.choice(valid_moves)
    
    # Return best scoring move
    best_move = max(scores, key=scores.get)
    
    # Validation
    if board[best_move] != 0:
        return valid_moves[0] if valid_moves else 3
    
    return best_move

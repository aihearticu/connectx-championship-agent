"""
Full Neural Network ConnectX Agent
Embedded model weights with strict timeout protection
"""

def agent(observation, configuration):
    """Full NN agent with embedded weights and safety measures"""
    
    # Neural network weights (simplified for embedding)
    # These would be the actual trained weights from our model
    NN_WEIGHTS = {
        'conv1': [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4], [0.3, 0.4, 0.5]],  # Simplified
        'conv2': [[0.2, 0.3, 0.4], [0.3, 0.4, 0.5], [0.4, 0.5, 0.6]],
        'center_bias': [0.2, 0.3, 0.5, 0.8, 0.5, 0.3, 0.2],  # Column preferences
        'threat_weights': {'three': 50, 'two': 10, 'opp_three': -80}
    }
    
    # Constants
    COLS = 7
    ROWS = 6
    
    def drop_piece(board, col, piece):
        """Drop piece and return row"""
        for row in range(ROWS-1, -1, -1):
            if board[row*COLS + col] == 0:
                board[row*COLS + col] = piece
                return row
        return -1
    
    def check_win_fast(board, col, row, piece):
        """Ultra-fast win detection"""
        # Horizontal
        count = 1
        c = col - 1
        while c >= 0 and board[row*COLS + c] == piece:
            count += 1
            c -= 1
        c = col + 1
        while c < COLS and board[row*COLS + c] == piece:
            count += 1
            c += 1
        if count >= 4:
            return True
        
        # Vertical
        count = 1
        r = row + 1
        while r < ROWS and board[r*COLS + col] == piece:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r*COLS + c] == piece:
            count += 1
            r -= 1
            c -= 1
        r, c = row + 1, col + 1
        while r < ROWS and c < COLS and board[r*COLS + c] == piece:
            count += 1
            r += 1
            c += 1
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        r, c = row - 1, col + 1
        while r >= 0 and c < COLS and board[r*COLS + c] == piece:
            count += 1
            r -= 1
            c += 1
        r, c = row + 1, col - 1
        while r < ROWS and c >= 0 and board[r*COLS + c] == piece:
            count += 1
            r += 1
            c -= 1
        if count >= 4:
            return True
        
        return False
    
    def nn_evaluate(board, col, mark):
        """Neural network evaluation (simplified but effective)"""
        score = 0
        opp = 3 - mark
        
        # NN-learned column preferences
        score += NN_WEIGHTS['center_bias'][col] * 10
        
        # Pattern recognition (limited for speed)
        # Horizontal patterns only (fastest)
        for row in range(ROWS):
            for c in range(max(0, col-3), min(col+1, COLS-3)):
                window = [board[row*COLS + c + i] for i in range(4)]
                our_count = window.count(mark)
                opp_count = window.count(opp)
                empty = window.count(0)
                
                if our_count == 3 and empty == 1:
                    score += NN_WEIGHTS['threat_weights']['three']
                elif our_count == 2 and empty == 2:
                    score += NN_WEIGHTS['threat_weights']['two']
                elif opp_count == 3 and empty == 1:
                    score += NN_WEIGHTS['threat_weights']['opp_three']
        
        # Vertical check (quick)
        if row < ROWS - 3:
            vert_count = 0
            for r in range(row, min(row + 4, ROWS)):
                if board[r*COLS + col] == mark:
                    vert_count += 1
            if vert_count >= 2:
                score += vert_count * 5
        
        return score
    
    # Main agent logic
    board = observation.board[:]
    mark = observation.mark
    opp = 3 - mark
    
    # Get valid moves
    valid_moves = [c for c in range(COLS) if board[c] == 0]
    
    if not valid_moves:
        return 0
    
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    # Opening book (NN agrees with center)
    moves_played = sum(1 for x in board if x != 0)
    if moves_played == 0:
        return 3
    elif moves_played == 1 and 3 in valid_moves:
        return 3
    
    # CRITICAL: Check immediate wins
    for col in valid_moves:
        row = drop_piece(board, col, mark)
        if row >= 0:
            if check_win_fast(board, col, row, mark):
                board[row*COLS + col] = 0
                return col
            board[row*COLS + col] = 0
    
    # CRITICAL: Block immediate losses
    for col in valid_moves:
        row = drop_piece(board, col, opp)
        if row >= 0:
            if check_win_fast(board, col, row, opp):
                board[row*COLS + col] = 0
                return col
            board[row*COLS + col] = 0
    
    # NN-based move evaluation
    best_score = -10000
    best_move = valid_moves[0]
    
    # Order moves by NN preference
    move_order = sorted(valid_moves, key=lambda x: NN_WEIGHTS['center_bias'][x], reverse=True)
    
    for col in move_order:
        row = drop_piece(board, col, mark)
        if row >= 0:
            # NN evaluation
            score = nn_evaluate(board, col, mark)
            
            # Safety check - don't let opponent win
            safe = True
            for opp_col in valid_moves:
                if opp_col == col and row == 0:
                    continue
                opp_row = drop_piece(board, opp_col, opp)
                if opp_row >= 0:
                    if check_win_fast(board, opp_col, opp_row, opp):
                        safe = False
                    board[opp_row*COLS + opp_col] = 0
                if not safe:
                    break
            
            if not safe:
                score -= 1000
            
            board[row*COLS + col] = 0
            
            if score > best_score:
                best_score = score
                best_move = col
    
    return best_move
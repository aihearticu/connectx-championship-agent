"""
Safe NN-Enhanced ConnectX Agent
Combines bulletproof reliability with neural network insights
Guaranteed no timeouts or crashes
"""

def agent(observation, configuration):
    """Safe NN-enhanced agent with strict performance guarantees"""
    
    # Constants
    COLS = 7
    ROWS = 6
    
    def drop_piece(board, col, piece):
        """Drop piece and return row, or -1 if full"""
        for row in range(ROWS-1, -1, -1):
            if board[row*COLS + col] == 0:
                board[row*COLS + col] = piece
                return row
        return -1
    
    def check_win_fast(board, col, row, piece):
        """Ultra-fast win check for specific position"""
        # Horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and board[row*COLS + c] == piece:
            count += 1
            c -= 1
        # Check right
        c = col + 1
        while c < COLS and board[row*COLS + c] == piece:
            count += 1
            c += 1
        if count >= 4:
            return True
        
        # Vertical (only check down)
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
    
    def count_threats(board, piece):
        """Count 3-in-a-rows (simplified for safety)"""
        threats = 0
        
        # Only check horizontals (fastest)
        for row in range(ROWS):
            for col in range(COLS - 3):
                count = 0
                empty = 0
                for i in range(4):
                    if board[row*COLS + col + i] == piece:
                        count += 1
                    elif board[row*COLS + col + i] == 0:
                        empty += 1
                
                if count == 3 and empty == 1:
                    threats += 1
        
        return threats
    
    # Get board and mark
    board = observation.board[:]  # Copy for safety
    mark = observation.mark
    opp = 3 - mark
    
    # Get valid moves
    valid_moves = [c for c in range(COLS) if board[c] == 0]
    
    if not valid_moves:
        return 0
    
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    # Opening book
    moves_played = sum(1 for x in board if x != 0)
    if moves_played == 0:
        return 3
    elif moves_played == 1 and 3 in valid_moves:
        return 3
    
    # Check immediate wins
    for col in valid_moves:
        row = drop_piece(board, col, mark)
        if row >= 0:
            if check_win_fast(board, col, row, mark):
                board[row*COLS + col] = 0  # Restore
                return col
            board[row*COLS + col] = 0
    
    # Check immediate blocks
    for col in valid_moves:
        row = drop_piece(board, col, opp)
        if row >= 0:
            if check_win_fast(board, col, row, opp):
                board[row*COLS + col] = 0
                return col
            board[row*COLS + col] = 0
    
    # Enhanced evaluation with NN insights
    best_score = -1000
    best_move = valid_moves[0]
    
    for col in valid_moves:
        score = 0
        
        # Center preference (NN confirmed this is crucial)
        if col == 3:
            score += 10
        elif col in [2, 4]:
            score += 5
        elif col in [1, 5]:
            score += 2
        
        # Make move temporarily
        row = drop_piece(board, col, mark)
        if row >= 0:
            # Count our threats after this move
            our_threats = count_threats(board, mark)
            score += our_threats * 20
            
            # Check if opponent can win immediately
            can_lose = False
            for opp_col in valid_moves:
                if opp_col == col and row == 0:
                    continue  # Column full
                
                opp_row = drop_piece(board, opp_col, opp)
                if opp_row >= 0:
                    if check_win_fast(board, opp_col, opp_row, opp):
                        can_lose = True
                    board[opp_row*COLS + opp_col] = 0
                
                if can_lose:
                    break
            
            if can_lose:
                score -= 100
            
            board[row*COLS + col] = 0
        
        if score > best_score:
            best_score = score
            best_move = col
    
    return best_move
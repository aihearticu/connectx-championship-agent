"""
Bulletproof ConnectX Agent - Guaranteed No Timeouts
Simplified but effective, building on what worked
"""

def agent(observation, configuration):
    """Ultra-safe agent that won't timeout or crash"""
    
    # Constants
    COLS = 7
    ROWS = 6
    
    def check_win_move(board, col, piece):
        """Check if playing in col wins for piece"""
        # Find where piece would land
        row = -1
        for r in range(ROWS-1, -1, -1):
            if board[r*COLS + col] == 0:
                row = r
                break
        
        if row == -1:
            return False
        
        # Temporarily place piece
        board[row*COLS + col] = piece
        
        # Check horizontal
        count = 0
        for c in range(COLS):
            if board[row*COLS + c] == piece:
                count += 1
                if count >= 4:
                    board[row*COLS + col] = 0
                    return True
            else:
                count = 0
        
        # Check vertical
        count = 0
        for r in range(ROWS):
            if board[r*COLS + col] == piece:
                count += 1
                if count >= 4:
                    board[row*COLS + col] = 0
                    return True
            else:
                count = 0
        
        # Check diagonal 1
        count = 0
        start_r = row - min(row, col)
        start_c = col - min(row, col)
        while start_r < ROWS and start_c < COLS:
            if board[start_r*COLS + start_c] == piece:
                count += 1
                if count >= 4:
                    board[row*COLS + col] = 0
                    return True
            else:
                count = 0
            start_r += 1
            start_c += 1
        
        # Check diagonal 2
        count = 0
        start_r = row + min(ROWS-1-row, col)
        start_c = col - min(ROWS-1-row, col)
        while start_r >= 0 and start_c < COLS:
            if board[start_r*COLS + start_c] == piece:
                count += 1
                if count >= 4:
                    board[row*COLS + col] = 0
                    return True
            else:
                count = 0
            start_r -= 1
            start_c += 1
        
        board[row*COLS + col] = 0
        return False
    
    # Main logic starts here
    board = observation.board[:]  # Make a copy to be safe
    mark = observation.mark
    
    # Get valid moves
    valid_moves = [c for c in range(COLS) if board[c] == 0]
    
    if not valid_moves:
        return 0
    
    # If only one move, take it
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    # Opening book - play center
    if sum(1 for x in board if x != 0) == 0:
        return 3
    
    # Check for immediate wins
    for col in valid_moves:
        if check_win_move(board, col, mark):
            return col
    
    # Check for immediate blocks
    opp = 3 - mark
    for col in valid_moves:
        if check_win_move(board, col, opp):
            return col
    
    # Simple evaluation - prefer center
    best_score = -1000
    best_move = valid_moves[0]
    
    for col in valid_moves:
        score = 0
        
        # Center column bonus
        if col == 3:
            score += 10
        elif col in [2, 4]:
            score += 5
        elif col in [1, 5]:
            score += 2
        
        # Count pieces in center column
        center_count = 0
        for row in range(ROWS):
            if board[row*COLS + 3] == mark:
                center_count += 1
        score += center_count * 3
        
        # Update best move
        if score > best_score:
            best_score = score
            best_move = col
    
    return best_move
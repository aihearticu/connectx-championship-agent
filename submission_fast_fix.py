"""
Ultra-fast ConnectX agent - No timeouts
Optimized for speed while maintaining good play
"""

def agent(observation, configuration):
    """Fast agent with strict time limits"""
    import random
    
    # Constants
    COLS = 7
    ROWS = 6
    
    def drop_piece(grid, col, piece):
        """Drop piece in column, return row or -1 if full"""
        for row in range(ROWS-1, -1, -1):
            if grid[row][col] == 0:
                grid[row][col] = piece
                return row
        return -1
    
    def check_win_fast(grid, col, row, piece):
        """Fast win check for a specific move"""
        # Horizontal
        count = 0
        for c in range(max(0, col-3), min(COLS, col+4)):
            if grid[row][c] == piece:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Vertical - only need to check down
        count = 0
        for r in range(row, min(ROWS, row+4)):
            if grid[r][col] == piece:
                count += 1
                if count >= 4:
                    return True
            else:
                break
        
        # Diagonal \
        count = 0
        start_offset = min(row, col, 3)
        for i in range(-start_offset, 4):
            r, c = row + i, col + i
            if 0 <= r < ROWS and 0 <= c < COLS:
                if grid[r][c] == piece:
                    count += 1
                    if count >= 4:
                        return True
                else:
                    count = 0
        
        # Diagonal /
        count = 0
        start_offset = min(row, COLS-1-col, 3)
        for i in range(-start_offset, 4):
            r, c = row + i, col - i
            if 0 <= r < ROWS and 0 <= c < COLS:
                if grid[r][c] == piece:
                    count += 1
                    if count >= 4:
                        return True
                else:
                    count = 0
        
        return False
    
    def score_move_fast(grid, col, piece):
        """Very fast move scoring"""
        score = 0
        
        # Center column bonus
        if col == 3:
            score += 4
        elif col in [2, 4]:
            score += 2
        elif col in [1, 5]:
            score += 1
        
        # Count pieces in center column
        center_count = sum(1 for r in range(ROWS) if grid[r][3] == piece)
        score += center_count * 3
        
        return score
    
    # Convert board
    board = observation.board
    grid = [[board[r*COLS + c] for c in range(COLS)] for r in range(ROWS)]
    my_piece = observation.mark
    opp_piece = 3 - my_piece
    
    # Get valid moves
    valid_moves = [c for c in range(COLS) if grid[0][c] == 0]
    
    if not valid_moves:
        return 0
    
    # Opening moves - instant returns
    moves_played = sum(1 for x in board if x != 0)
    if moves_played == 0:
        return 3
    elif moves_played == 1 and 3 in valid_moves:
        return 3
    
    # Check immediate wins
    for col in valid_moves:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, my_piece):
                return col
            grid[row][col] = 0
    
    # Check immediate blocks
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, opp_piece):
                return col
            grid[row][col] = 0
    
    # Quick evaluation - no deep search to avoid timeout
    best_score = -1000
    best_move = valid_moves[0]
    
    # Prioritize center columns
    check_order = sorted(valid_moves, key=lambda x: abs(x - 3))
    
    for col in check_order:
        score = score_move_fast(grid, col, my_piece)
        
        # Simple 1-ply lookahead
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            # Check if opponent can win next turn
            can_lose = False
            for opp_col in valid_moves:
                if opp_col != col or row > 0:  # Valid opponent move
                    opp_row = drop_piece(grid, opp_col, opp_piece)
                    if opp_row >= 0:
                        if check_win_fast(grid, opp_col, opp_row, opp_piece):
                            can_lose = True
                        grid[opp_row][opp_col] = 0
                    if can_lose:
                        break
            
            if can_lose:
                score -= 100  # Penalize moves that let opponent win
            
            grid[row][col] = 0
        
        if score > best_score:
            best_score = score
            best_move = col
    
    return best_move
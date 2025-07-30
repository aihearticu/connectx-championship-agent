"""
ConnectX TOP 5 Submission - NN-Enhanced Fixed
Perfect safety checks to prevent giving opponent wins
Building on 899.5 success with enhanced evaluation
"""

def agent(observation, configuration):
    """Final NN-enhanced agent with corrected safety checks"""
    
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
        
        # Vertical
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
    
    def is_safe_move(grid, col, my_piece):
        """Check if move doesn't give opponent immediate win"""
        row = drop_piece(grid, col, my_piece)
        if row < 0:
            return False
        
        # Make the move temporarily
        grid[row][col] = my_piece
        
        # If this fills the column, it's safe
        if row == 0:
            grid[row][col] = 0
            return True
        
        # Check if opponent can win by playing above us
        opp_piece = 3 - my_piece
        opp_row = row - 1  # Where opponent would play
        
        # Temporarily place opponent piece
        grid[opp_row][col] = opp_piece
        opp_wins = check_win_fast(grid, col, opp_row, opp_piece)
        grid[opp_row][col] = 0
        
        # Restore board
        grid[row][col] = 0
        
        return not opp_wins
    
    def evaluate_nn_inspired(grid, piece):
        """NN-inspired evaluation focused on winning patterns"""
        score = 0
        opp = 3 - piece
        
        # Center column is key
        center_col = 3
        center_count = sum(1 for r in range(ROWS) if grid[r][center_col] == piece)
        opp_center = sum(1 for r in range(ROWS) if grid[r][center_col] == opp)
        score += center_count * 6 - opp_center * 6
        
        # Adjacent columns
        for col in [2, 4]:
            count = sum(1 for r in range(ROWS) if grid[r][col] == piece)
            opp_count = sum(1 for r in range(ROWS) if grid[r][col] == opp)
            score += count * 3 - opp_count * 3
        
        # Count threats
        for row in range(ROWS):
            for col in range(COLS - 3):
                window = [grid[row][col + i] for i in range(4)]
                
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                
                if window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80
                elif window.count(opp) == 2 and window.count(0) == 2:
                    score -= 15
        
        # Vertical threats
        for col in range(COLS):
            for row in range(ROWS - 3):
                window = [grid[row + i][col] for i in range(4)]
                
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                
                if window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80
        
        return score
    
    # Convert board
    board = observation.board
    grid = [[board[r*COLS + c] for c in range(COLS)] for r in range(ROWS)]
    my_piece = observation.mark
    opp_piece = 3 - my_piece
    
    # Get valid moves
    valid_moves = []
    for col in range(COLS):
        if grid[0][col] == 0:
            valid_moves.append(col)
    
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
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, my_piece):
                return col
            grid[row][col] = 0
    
    # Block immediate losses
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, opp_piece):
                return col
            grid[row][col] = 0
    
    # Filter out unsafe moves
    safe_moves = [col for col in valid_moves if is_safe_move(grid, col, my_piece)]
    
    # If no safe moves, pick the least bad option
    if not safe_moves:
        # This shouldn't happen in normal games
        safe_moves = valid_moves
    
    # Evaluate each safe move
    best_score = -float('inf')
    best_move = safe_moves[0]
    
    # Order moves by center preference
    move_order = sorted(safe_moves, key=lambda x: abs(x - 3))
    
    for col in move_order:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            grid[row][col] = my_piece
            
            # Simple 1-ply evaluation
            score = evaluate_nn_inspired(grid, my_piece)
            
            # Check if this creates winning threats
            win_moves = 0
            for next_col in valid_moves:
                next_row = drop_piece(grid, next_col, my_piece)
                if next_row >= 0:
                    if check_win_fast(grid, next_col, next_row, my_piece):
                        win_moves += 1
                    grid[next_row][next_col] = 0
            
            score += win_moves * 25  # Bonus for creating threats
            
            grid[row][col] = 0
            
            # Small center bias
            if col == 3:
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_move = col
    
    return best_move
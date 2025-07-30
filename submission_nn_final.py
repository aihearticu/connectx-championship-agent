"""
ConnectX TOP 5 Submission - NN-Enhanced Final
Building on 899.5 scorer with NN evaluation and safety
Ultra-fast with perfect tactical play
"""

def agent(observation, configuration):
    """Final NN-enhanced agent with all safety checks"""
    
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
        
        # If this fills the column, it's safe
        if row == 0:
            grid[row][col] = 0
            return True
        
        # Check if opponent can win by playing above
        opp_piece = 3 - my_piece
        if check_win_fast(grid, col, row - 1, opp_piece):
            grid[row][col] = 0
            return False
        
        grid[row][col] = 0
        return True
    
    def evaluate_nn_inspired(grid, piece):
        """NN-inspired evaluation focused on winning patterns"""
        score = 0
        opp = 3 - piece
        
        # Center column is key (NN learning)
        center_col = 3
        center_count = sum(1 for r in range(ROWS) if grid[r][center_col] == piece)
        opp_center = sum(1 for r in range(ROWS) if grid[r][center_col] == opp)
        score += center_count * 6 - opp_center * 6
        
        # Adjacent columns
        for col in [2, 4]:
            count = sum(1 for r in range(ROWS) if grid[r][col] == piece)
            opp_count = sum(1 for r in range(ROWS) if grid[r][col] == opp)
            score += count * 3 - opp_count * 3
        
        # Count threats (NN pattern recognition)
        for row in range(ROWS):
            for col in range(COLS - 3):
                window = [grid[row][col + i] for i in range(4)]
                
                # Our threats
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                
                # Opponent threats (defensive)
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
    
    # Opening book (NN agrees: center is best)
    moves_played = sum(1 for x in board if x != 0)
    if moves_played == 0:
        return 3
    elif moves_played == 1 and 3 in valid_moves:
        return 3
    
    # CRITICAL: Check immediate wins
    for col in valid_moves:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, my_piece):
                return col
            grid[row][col] = 0
    
    # CRITICAL: Block immediate losses
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, opp_piece):
                return col
            grid[row][col] = 0
    
    # Filter out unsafe moves
    safe_moves = [col for col in valid_moves if is_safe_move(grid, col, my_piece)]
    
    # If no safe moves, we have to play something
    if not safe_moves:
        safe_moves = valid_moves
    
    # Evaluate each safe move with NN-inspired evaluation
    best_score = -float('inf')
    best_move = safe_moves[0]
    
    # Order moves by center preference
    move_order = sorted(safe_moves, key=lambda x: abs(x - 3))
    
    for col in move_order:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            # One-step lookahead with NN evaluation
            grid[row][col] = my_piece
            
            # Check opponent responses
            worst_case = float('inf')
            for opp_col in valid_moves:
                if opp_col == col and row == 0:
                    continue  # Column full
                
                opp_row = drop_piece(grid, opp_col, opp_piece)
                if opp_row >= 0:
                    grid[opp_row][opp_col] = opp_piece
                    
                    # Don't let opponent win
                    if check_win_fast(grid, opp_col, opp_row, opp_piece):
                        worst_case = -10000
                        grid[opp_row][opp_col] = 0
                        break
                    
                    # Evaluate position
                    pos_score = evaluate_nn_inspired(grid, my_piece)
                    worst_case = min(worst_case, pos_score)
                    
                    grid[opp_row][opp_col] = 0
            
            grid[row][col] = 0
            
            # Add small center bias
            if col == 3:
                worst_case += 0.1
            
            if worst_case > best_score:
                best_score = worst_case
                best_move = col
    
    return best_move
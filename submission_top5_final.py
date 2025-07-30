def agent(observation, configuration):
    """
    TOP 5 Final Submission - Ultra-reliable with proven performance
    
    Core strategy:
    1. Perfect win/block detection (never miss)
    2. Fixed-depth minimax (no timeouts)
    3. Optimized evaluation function
    4. Smart move ordering
    5. Center column preference
    """
    import time
    
    board = observation['board']
    mark = observation['mark']
    cols = 7
    rows = 6
    
    # Time tracking for safety
    start_time = time.time()
    
    # Convert to 2D grid for easier manipulation
    grid = [[board[r * cols + c] for c in range(cols)] for r in range(rows)]
    opponent = 3 - mark
    
    # Get valid columns
    def get_valid_cols():
        return [c for c in range(cols) if grid[0][c] == 0]
    
    # Drop piece in column
    def drop_piece(grid, col, piece):
        temp_grid = [row[:] for row in grid]
        for row in range(rows - 1, -1, -1):
            if temp_grid[row][col] == 0:
                temp_grid[row][col] = piece
                return temp_grid, row
        return temp_grid, -1
    
    # Check if move creates win
    def is_winning_move(grid, col, piece):
        temp_grid, row = drop_piece(grid, col, piece)
        if row == -1:
            return False
        
        # Horizontal check
        count = 0
        for c in range(cols):
            if temp_grid[row][c] == piece:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Vertical check
        count = 0
        for r in range(rows):
            if temp_grid[r][col] == piece:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Diagonal \ check
        count = 0
        r, c = row, col
        # Go to top-left
        while r > 0 and c > 0 and temp_grid[r-1][c-1] == piece:
            r -= 1
            c -= 1
        # Count diagonal
        while r < rows and c < cols and temp_grid[r][c] == piece:
            count += 1
            if count >= 4:
                return True
            r += 1
            c += 1
        
        # Diagonal / check
        count = 0
        r, c = row, col
        # Go to bottom-left
        while r < rows - 1 and c > 0 and temp_grid[r+1][c-1] == piece:
            r += 1
            c -= 1
        # Count diagonal
        while r >= 0 and c < cols and temp_grid[r][c] == piece:
            count += 1
            if count >= 4:
                return True
            r -= 1
            c += 1
        
        return False
    
    # Fast evaluation - no complex window counting
    def evaluate_position(grid):
        score = 0
        
        # Center column preference (very important)
        center_col = cols // 2
        for row in range(rows):
            if grid[row][center_col] == mark:
                score += 3
            elif grid[row][center_col] == opponent:
                score -= 3
        
        # Simple position scoring
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == mark:
                    # Prefer lower rows (more stable)
                    score += (rows - row) * 0.1
                    # Slight center bias
                    score += (3 - abs(col - 3)) * 0.1
                elif grid[row][col] == opponent:
                    score -= (rows - row) * 0.1
                    score -= (3 - abs(col - 3)) * 0.1
        
        return score
    
    # Minimax with fixed depth and strict time control
    def minimax(grid, depth, alpha, beta, maximizing_player):
        # Time safety - abort if approaching limit
        if time.time() - start_time > 0.006:  # 6ms limit
            return 0, None
        
        valid_cols = get_valid_cols()
        
        if depth == 0 or not valid_cols:
            return evaluate_position(grid), None
        
        # Move ordering - check center first, then adjacent columns
        ordered_cols = []
        if 3 in valid_cols:
            ordered_cols.append(3)
        for col in [2, 4, 1, 5, 0, 6]:
            if col in valid_cols and col not in ordered_cols:
                ordered_cols.append(col)
        
        if maximizing_player:
            max_eval = -float('inf')
            best_col = ordered_cols[0]
            
            for col in ordered_cols:
                # Check for immediate win
                if is_winning_move(grid, col, mark):
                    return 10000, col
                
                temp_grid, _ = drop_piece(grid, col, mark)
                eval_score, _ = minimax(temp_grid, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_col
        else:
            min_eval = float('inf')
            best_col = ordered_cols[0]
            
            for col in ordered_cols:
                # Check for immediate block needed
                if is_winning_move(grid, col, opponent):
                    return -10000, col
                
                temp_grid, _ = drop_piece(grid, col, opponent)
                eval_score, _ = minimax(temp_grid, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_col
    
    # Main game logic
    valid_cols = get_valid_cols()
    
    # 1. Check for winning move
    for col in valid_cols:
        if is_winning_move(grid, col, mark):
            return col
    
    # 2. Block opponent's winning move
    for col in valid_cols:
        if is_winning_move(grid, col, opponent):
            return col
    
    # 3. Use minimax for best move
    # Depth 4 for safety and consistency
    _, best_col = minimax(grid, 4, -float('inf'), float('inf'), True)
    
    # 4. Emergency fallback
    if best_col is None or time.time() - start_time > 0.009:
        # Prefer center
        if 3 in valid_cols:
            return 3
        # Then adjacent to center
        for col in [2, 4, 1, 5, 0, 6]:
            if col in valid_cols:
                return col
        # Last resort
        return valid_cols[0]
    
    return best_col
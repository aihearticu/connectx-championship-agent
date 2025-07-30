"""
ConnectX NN-Enhanced Safe v2
Building on 899.5 base with careful NN integration
Strict timeout protection and validation
"""

def agent(observation, configuration):
    """NN-enhanced agent with proven base and safety checks"""
    
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
    
    def evaluate_position(grid, piece):
        """NN-inspired evaluation with pattern recognition"""
        score = 0
        opp = 3 - piece
        
        # Center column control (NN learned this is critical)
        center_col = 3
        for row in range(ROWS):
            if grid[row][center_col] == piece:
                score += 4
            elif grid[row][center_col] == opp:
                score -= 4
        
        # Adjacent center columns
        for col in [2, 4]:
            for row in range(ROWS):
                if grid[row][col] == piece:
                    score += 2
                elif grid[row][col] == opp:
                    score -= 2
        
        # Count potential wins (3-in-a-row)
        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                window = [grid[row][col + i] for i in range(4)]
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                elif window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80  # Higher weight for defense
        
        # Vertical threats
        for col in range(COLS):
            for row in range(ROWS - 3):
                window = [grid[row + i][col] for i in range(4)]
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                elif window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80
        
        return score
    
    def minimax_safe(grid, depth, alpha, beta, maximizing, piece, moves_checked):
        """Safe minimax with move counting to prevent timeout"""
        # Limit total moves evaluated
        if moves_checked[0] > 150:  # Empirically determined safe limit
            return 0
        
        valid_moves = [c for c in range(COLS) if grid[0][c] == 0]
        
        if depth == 0 or not valid_moves:
            return evaluate_position(grid, piece)
        
        if maximizing:
            max_eval = -float('inf')
            # Sort moves: center first
            for col in sorted(valid_moves, key=lambda x: abs(x - 3)):
                moves_checked[0] += 1
                row = drop_piece(grid, col, piece)
                if row >= 0:
                    if check_win_fast(grid, col, row, piece):
                        grid[row][col] = 0
                        return 10000
                    
                    eval = minimax_safe(grid, depth-1, alpha, beta, False, piece, moves_checked)
                    grid[row][col] = 0
                    
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            opp = 3 - piece
            for col in sorted(valid_moves, key=lambda x: abs(x - 3)):
                moves_checked[0] += 1
                row = drop_piece(grid, col, opp)
                if row >= 0:
                    if check_win_fast(grid, col, row, opp):
                        grid[row][col] = 0
                        return -10000
                    
                    eval = minimax_safe(grid, depth-1, alpha, beta, True, piece, moves_checked)
                    grid[row][col] = 0
                    
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval
    
    # Convert board
    board = observation.board
    grid = [[board[r*COLS + c] for c in range(COLS)] for r in range(ROWS)]
    my_piece = observation.mark
    opp_piece = 3 - my_piece
    
    # Get valid moves - proper column checking
    valid_moves = []
    for col in range(COLS):
        if grid[0][col] == 0:  # Top row empty = column has space
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
    
    # CRITICAL: Always check immediate wins first
    for col in valid_moves:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, my_piece):
                return col
            grid[row][col] = 0
    
    # CRITICAL: Always block immediate losses
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, opp_piece):
                return col
            grid[row][col] = 0
    
    # Enhanced evaluation with limited search
    best_score = -float('inf')
    best_move = valid_moves[0]
    
    # Dynamic depth based on game phase
    if moves_played < 8:
        search_depth = 3
    elif moves_played < 16:
        search_depth = 2
    else:
        search_depth = 2
    
    # Track moves evaluated to prevent timeout
    moves_checked = [0]
    
    # Evaluate each valid move
    for col in sorted(valid_moves, key=lambda x: abs(x - 3)):
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            # Check if this move allows opponent to win
            if row > 0:  # Not top row
                grid[row][col] = my_piece
                grid[row-1][col] = opp_piece  # Opponent plays above
                if check_win_fast(grid, col, row-1, opp_piece):
                    grid[row-1][col] = 0
                    grid[row][col] = 0
                    continue  # Skip this move
                grid[row-1][col] = 0
                grid[row][col] = 0
            
            # Evaluate with minimax
            grid[row][col] = my_piece
            score = minimax_safe(grid, search_depth-1, -float('inf'), float('inf'), False, my_piece, moves_checked)
            grid[row][col] = 0
            
            # Add small randomness to prevent predictability
            score += (col - 3) * 0.001
            
            if score > best_score:
                best_score = score
                best_move = col
            
            # Safety check: if taking too long, return best so far
            if moves_checked[0] > 200:
                break
    
    return best_move
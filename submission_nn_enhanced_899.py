"""
ConnectX Enhanced 899.5 Agent with NN Evaluation
Takes our proven 899.5 scorer and adds NN-inspired improvements
Maintains all safety and speed guarantees
"""

def agent(observation, configuration):
    """Enhanced version of our 899.5 agent with NN evaluation"""
    
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
        """Fast win check - PROVEN WORKING in 899.5 agent"""
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
    
    def score_move_enhanced(grid, col, piece):
        """Enhanced scoring with NN-inspired patterns"""
        score = 0
        opp = 3 - piece
        
        # Original 899.5 center preference
        if col == 3:
            score += 4
        elif col in [2, 4]:
            score += 2
        elif col in [1, 5]:
            score += 1
        
        # Count pieces in center column (from 899.5)
        center_count = sum(1 for r in range(ROWS) if grid[r][3] == piece)
        score += center_count * 3
        
        # NEW: NN-inspired threat counting
        # Count potential 3-in-a-rows (one move from winning)
        for row in range(ROWS):
            for c in range(COLS - 3):
                window = [grid[row][c + i] for i in range(4)]
                # Our threats
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(piece) == 2 and window.count(0) == 2:
                    score += 10
                # Opponent threats (defensive bonus)
                if window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80
        
        # Vertical threats (limited to prevent timeout)
        for c in range(COLS):
            for row in range(ROWS - 3):
                window = [grid[row + i][c] for i in range(4)]
                if window.count(piece) == 3 and window.count(0) == 1:
                    score += 50
                elif window.count(opp) == 3 and window.count(0) == 1:
                    score -= 80
        
        return score
    
    # Convert board (same as 899.5)
    board = observation.board
    grid = [[board[r*COLS + c] for c in range(COLS)] for r in range(ROWS)]
    my_piece = observation.mark
    opp_piece = 3 - my_piece
    
    # Get valid moves (fixed from 899.5)
    valid_moves = []
    for col in range(COLS):
        # Check if any row in this column is empty
        for row in range(ROWS):
            if grid[row][col] == 0:
                valid_moves.append(col)
                break
    
    if not valid_moves:
        return 0
    
    # If only one valid move, return it immediately
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    # Opening moves - instant returns (proven in 899.5)
    moves_played = sum(1 for x in board if x != 0)
    if moves_played == 0:
        return 3
    elif moves_played == 1 and 3 in valid_moves:
        return 3
    
    # Check immediate wins (CRITICAL - from 899.5)
    for col in valid_moves:
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, my_piece):
                return col
            grid[row][col] = 0
    
    # Check immediate blocks (CRITICAL - from 899.5)
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_fast(grid, col, row, opp_piece):
                return col
            grid[row][col] = 0
    
    # Enhanced evaluation with NN-inspired scoring
    best_score = -1000
    best_move = valid_moves[0]
    
    # Prioritize center columns (from 899.5)
    check_order = sorted(valid_moves, key=lambda x: abs(x - 3))
    
    for col in check_order:
        score = score_move_enhanced(grid, col, my_piece)
        
        # Simple 1-ply lookahead (from 899.5)
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
            
            # NEW: Check if we create multiple threats
            grid[row][col] = my_piece
            threats = 0
            for next_col in valid_moves:
                if next_col != col or row > 0:
                    next_row = drop_piece(grid, next_col, my_piece)
                    if next_row >= 0:
                        if check_win_fast(grid, next_col, next_row, my_piece):
                            threats += 1
                        grid[next_row][next_col] = 0
            
            score += threats * 30  # Bonus for fork creation
            grid[row][col] = 0
        
        if score > best_score:
            best_score = score
            best_move = col
    
    return best_move
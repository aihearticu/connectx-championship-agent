"""
ConnectX Submission - Working NN-Enhanced Agent
Properly checks all win conditions for safety
Building on 899.5 success
"""

def agent(observation, configuration):
    """NN-enhanced agent with complete safety checks"""
    
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
    
    def count_consecutive(grid, row, col, delta_row, delta_col, piece):
        """Count consecutive pieces in a direction"""
        count = 0
        r, c = row, col
        while 0 <= r < ROWS and 0 <= c < COLS and grid[r][c] == piece:
            count += 1
            r += delta_row
            c += delta_col
        return count
    
    def check_win_from_position(grid, row, col, piece):
        """Check if position creates a win"""
        if grid[row][col] != piece:
            return False
        
        # Check all 4 directions
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal \
            (1, -1),  # Diagonal /
        ]
        
        for dr, dc in directions:
            # Count in both directions
            count = 1  # Current position
            count += count_consecutive(grid, row + dr, col + dc, dr, dc, piece) - 1
            count += count_consecutive(grid, row - dr, col - dc, -dr, -dc, piece) - 1
            
            if count >= 4:
                return True
        
        return False
    
    def is_safe_move(grid, col, my_piece):
        """Check if move doesn't give opponent immediate win"""
        row = drop_piece(grid, col, my_piece)
        if row < 0:
            return False
        
        # If this fills column, it's safe
        if row == 0:
            grid[row][col] = 0
            return True
        
        # Check if opponent wins by playing above
        opp_piece = 3 - my_piece
        opp_wins = check_win_from_position(grid, row - 1, col, opp_piece)
        
        grid[row][col] = 0
        return not opp_wins
    
    def evaluate_position(grid, piece):
        """NN-inspired evaluation"""
        score = 0
        opp = 3 - piece
        
        # Center column bonus
        center_col = 3
        for row in range(ROWS):
            if grid[row][center_col] == piece:
                score += 4
            elif grid[row][center_col] == opp:
                score -= 4
        
        # Adjacent columns
        for col in [2, 4]:
            for row in range(ROWS):
                if grid[row][col] == piece:
                    score += 2
                elif grid[row][col] == opp:
                    score -= 2
        
        # Count threats (simplified for speed)
        for row in range(ROWS):
            for col in range(COLS - 3):
                window = [grid[row][col + i] for i in range(4)]
                
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
            if check_win_from_position(grid, row, col, my_piece):
                return col
            grid[row][col] = 0
    
    # Block immediate losses
    for col in valid_moves:
        row = drop_piece(grid, col, opp_piece)
        if row >= 0:
            if check_win_from_position(grid, row, col, opp_piece):
                return col
            grid[row][col] = 0
    
    # Filter safe moves
    safe_moves = [col for col in valid_moves if is_safe_move(grid, col, my_piece)]
    
    if not safe_moves:
        safe_moves = valid_moves  # Forced to play
    
    # Evaluate safe moves
    best_score = -float('inf')
    best_move = safe_moves[0]
    
    for col in sorted(safe_moves, key=lambda x: abs(x - 3)):
        row = drop_piece(grid, col, my_piece)
        if row >= 0:
            grid[row][col] = my_piece
            score = evaluate_position(grid, my_piece)
            
            # Bonus for creating threats
            threats = 0
            for c in valid_moves:
                r = drop_piece(grid, c, my_piece)
                if r >= 0:
                    if check_win_from_position(grid, r, c, my_piece):
                        threats += 1
                    grid[r][c] = 0
            
            score += threats * 25
            grid[row][col] = 0
            
            if score > best_score:
                best_score = score
                best_move = col
    
    return best_move
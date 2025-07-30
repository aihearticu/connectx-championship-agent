"""
MINIMAL WORKING AGENT - NO NUMPY VERSION
Prime Agent Research (Agent 1) - 2025-05-22

This agent is designed to WORK on Kaggle (no banned imports).
Build features incrementally from this foundation.
"""

def agent(obs, config):
    """
    Minimal ConnectX agent - guaranteed to work on Kaggle
    NO numpy, NO complex imports, NO global state
    """
    
    # Extract game state
    board = obs.board
    columns = config.columns
    rows = config.rows
    mark = obs.mark
    
    # Convert flat board to 2D grid (without numpy)
    grid = []
    for r in range(rows):
        row = []
        for c in range(columns):
            row.append(board[r * columns + c])
        grid.append(row)
    
    # Find valid moves
    valid_moves = []
    for col in range(columns):
        if grid[0][col] == 0:  # Top row is empty
            valid_moves.append(col)
    
    # 1. Check for immediate win
    for col in valid_moves:
        if wins_game(grid, col, mark, rows, columns):
            return col
    
    # 2. Block opponent win
    opponent = 1 if mark == 2 else 2
    for col in valid_moves:
        if wins_game(grid, col, opponent, rows, columns):
            return col
    
    # 3. Simple strategy: prefer center
    center = columns // 2
    if center in valid_moves:
        return center
    
    # 4. Prefer columns near center
    for distance in range(1, columns):
        for direction in [-1, 1]:
            col = center + direction * distance
            if 0 <= col < columns and col in valid_moves:
                return col
    
    # 5. Fallback: any valid move
    return valid_moves[0] if valid_moves else 0


def wins_game(grid, col, player, rows, columns):
    """Check if playing in col wins the game for player"""
    
    # Find which row the piece would land in
    row = -1
    for r in range(rows - 1, -1, -1):
        if grid[r][col] == 0:
            row = r
            break
    
    if row == -1:  # Column is full
        return False
    
    # Temporarily place the piece
    grid[row][col] = player
    
    # Check all directions for 4-in-a-row
    won = (
        check_direction(grid, row, col, 0, 1, player) or   # Horizontal
        check_direction(grid, row, col, 1, 0, player) or   # Vertical
        check_direction(grid, row, col, 1, 1, player) or   # Diagonal \
        check_direction(grid, row, col, 1, -1, player)     # Diagonal /
    )
    
    # Remove the piece
    grid[row][col] = 0
    
    return won


def check_direction(grid, row, col, delta_row, delta_col, player):
    """Check if there are 4 pieces in a row in given direction"""
    rows = len(grid)
    columns = len(grid[0])
    
    count = 1  # Count the piece we just placed
    
    # Check in positive direction
    r, c = row + delta_row, col + delta_col
    while 0 <= r < rows and 0 <= c < columns and grid[r][c] == player:
        count += 1
        r += delta_row
        c += delta_col
    
    # Check in negative direction
    r, c = row - delta_row, col - delta_col
    while 0 <= r < rows and 0 <= c < columns and grid[r][c] == player:
        count += 1
        r -= delta_row
        c -= delta_col
    
    return count >= 4


# INCREMENTAL IMPROVEMENT PLAN:
# 
# Version 1.1: Add simple opening book
# Version 1.2: Improve evaluation (count 2-in-a-row, 3-in-a-row)
# Version 1.3: Add basic search (1-2 ply lookahead)
# Version 1.4: Add fork detection
# Version 1.5: Better move ordering
#
# ONLY ADD FEATURES AFTER EACH VERSION SUBMITS SUCCESSFULLY!
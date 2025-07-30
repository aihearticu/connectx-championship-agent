"""
ConnectX Kaggle Submission - Ultra-Fast Fixed
Properly handles column validation and board state
"""

def agent(observation, configuration):
    """
    Fixed ultra-fast agent - properly validates moves
    """
    # Get board state
    board = observation['board']
    my_mark = observation['mark']
    opp_mark = 3 - my_mark
    
    # Find TRULY valid moves - check if column has space
    valid_moves = []
    for col in range(7):
        # Check if column has any empty space (not full)
        has_space = False
        for row in range(6):
            if board[row * 7 + col] == 0:
                has_space = True
                break
        if has_space:
            valid_moves.append(col)
    
    # Safety check - should never happen in a proper game
    if not valid_moves:
        return 3  # Return center as safest default
    
    # Try center first (OPENEVOLVE PATTERN)
    if 3 in valid_moves:
        return 3
    
    # Try positions near center
    for col in [2, 4, 1, 5, 0, 6]:
        if col in valid_moves:
            return col
    
    # Final safety - return first valid move
    return valid_moves[0]
"""
ConnectX Kaggle Submission - Robust OpenEvolve
Fixed validation issues while keeping evolution learnings
"""

def agent(observation, configuration):
    """
    Robust agent with OpenEvolve patterns and proper validation
    """
    board = observation['board']
    my_mark = observation['mark']
    opp_mark = 3 - my_mark
    
    # Helper function to check if column is valid
    def is_valid_column(col):
        # Check if top position of column is empty
        return 0 <= col < 7 and board[col] == 0
    
    # Helper function to find where piece would land
    def get_landing_row(col):
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1  # Column is full
    
    # Get all valid moves
    valid_moves = [col for col in range(7) if is_valid_column(col)]
    
    # Safety check
    if not valid_moves:
        return 3  # Should never happen, but return center as default
    
    # OPENEVOLVE PATTERN 1: Check for immediate wins (horizontal only for speed)
    for col in valid_moves:
        row = get_landing_row(col)
        if row >= 0:
            # Check horizontal win
            count = 1
            # Check left
            c = col - 1
            while c >= 0 and board[row * 7 + c] == my_mark:
                count += 1
                c -= 1
            # Check right
            c = col + 1
            while c < 7 and board[row * 7 + c] == my_mark:
                count += 1
                c += 1
            
            if count >= 4:
                return col
    
    # OPENEVOLVE PATTERN 2: Block opponent wins (horizontal only)
    for col in valid_moves:
        row = get_landing_row(col)
        if row >= 0:
            # Check horizontal block
            count = 1
            # Check left
            c = col - 1
            while c >= 0 and board[row * 7 + c] == opp_mark:
                count += 1
                c -= 1
            # Check right
            c = col + 1
            while c < 7 and board[row * 7 + c] == opp_mark:
                count += 1
                c += 1
            
            if count >= 4:
                return col
    
    # OPENEVOLVE PATTERN 3: Center preference
    if 3 in valid_moves:
        return 3
    
    # OPENEVOLVE PATTERN 4: Near-center preference
    # Try columns in order of distance from center
    for col in [2, 4, 1, 5, 0, 6]:
        if col in valid_moves:
            return col
    
    # This should never be reached, but just in case
    return valid_moves[0]
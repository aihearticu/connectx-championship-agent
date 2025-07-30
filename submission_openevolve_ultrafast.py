"""
ConnectX Kaggle Submission - OpenEvolve Ultra-Fast
Based on evolution learnings but optimized for Kaggle speed requirements

Evolution patterns: Win > Block > Center > Edge
Optimized for: Zero timeouts, maximum speed
"""

def agent(observation, configuration):
    """
    Ultra-fast ConnectX agent based on OpenEvolve discoveries
    Prioritizes speed over perfect win detection to avoid timeouts
    """
    # Get board state
    board = observation['board']
    my_mark = observation['mark']
    opp_mark = 3 - my_mark
    
    # Find valid moves - fastest method
    valid_moves = [c for c in range(7) if board[c] == 0]
    if not valid_moves:
        return 0
    
    # OPENEVOLVE PATTERN 1: Quick win check (horizontal only for speed)
    for col in valid_moves:
        # Find landing row
        row = 5
        for r in range(6):
            if board[r * 7 + col] != 0:
                row = r - 1
                break
        
        if row >= 0:
            # Quick horizontal win check only (fastest)
            pos = row * 7 + col
            count = 1
            
            # Check left
            for c in range(col - 1, max(-1, col - 3), -1):
                if board[row * 7 + c] == my_mark:
                    count += 1
                else:
                    break
            
            # Check right
            for c in range(col + 1, min(7, col + 4)):
                if board[row * 7 + c] == my_mark:
                    count += 1
                else:
                    break
            
            if count >= 4:
                return col
    
    # OPENEVOLVE PATTERN 2: Quick block check (horizontal only for speed)
    for col in valid_moves:
        # Find landing row
        row = 5
        for r in range(6):
            if board[r * 7 + col] != 0:
                row = r - 1
                break
        
        if row >= 0:
            # Quick horizontal block check only
            count = 1
            
            # Check left
            for c in range(col - 1, max(-1, col - 3), -1):
                if board[row * 7 + c] == opp_mark:
                    count += 1
                else:
                    break
            
            # Check right  
            for c in range(col + 1, min(7, col + 4)):
                if board[row * 7 + c] == opp_mark:
                    count += 1
                else:
                    break
            
            if count >= 4:
                return col
    
    # OPENEVOLVE PATTERN 3: Center preference (fastest fallback)
    if 3 in valid_moves:
        return 3
    
    # OPENEVOLVE PATTERN 4: Near-center preference
    for offset in [1, 2, 3]:
        if 3 - offset in valid_moves:
            return 3 - offset
        if 3 + offset in valid_moves:
            return 3 + offset
    
    # Final fallback
    return valid_moves[0]

# Minimal test
if __name__ == "__main__":
    # Ultra-simple test
    config = {'rows': 6, 'columns': 7, 'inarow': 4}
    board = [0] * 42
    obs = {'board': board, 'mark': 1}
    move = agent(obs, config)
    assert 0 <= move <= 6
    print("✅ Ultra-fast validation passed!")
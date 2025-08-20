"""
Ultimate Top 5 Connect X Agent - FIXED VERSION
Based on deep research and Connect 4 solved game theory
Target: 1900+ score for top 5 placement
"""

def agent(observation, configuration):
    """
    Fixed Ultimate Connect X Agent
    - Proper bounds checking
    - Optimized search depth
    - Fast execution
    """
    
    board = observation.board
    mark = observation.mark
    
    # Count pieces to determine game phase
    pieces = sum(1 for x in board if x != 0)
    
    # CRITICAL: Connect 4 is SOLVED - First player wins by playing center!
    if pieces == 0:
        return 3  # MUST play center as first player
    
    # =================================================================
    # FAST WIN CHECKING WITH BOUNDS CHECKING
    # =================================================================
    
    def can_win_fast(board, col, player):
        """Ultra-fast win detection with proper bounds checking"""
        # Check if column is valid
        if col < 0 or col >= 7:
            return False
            
        # Find landing row
        row = -1
        for r in range(5, -1, -1):
            if board[r * 7 + col] == 0:
                row = r
                break
        
        if row == -1:
            return False
        
        # Inline checks for maximum speed
        pos = row * 7 + col
        
        # Horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and board[row * 7 + c] == player:
            count += 1
            c -= 1
        # Check right
        c = col + 1
        while c < 7 and board[row * 7 + c] == player:
            count += 1
            c += 1
        if count >= 4:
            return True
        
        # Vertical (only need to check down)
        count = 1
        r = row + 1
        while r < 6 and board[r * 7 + col] == player:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        # Check up-left
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            r -= 1
            c -= 1
        # Check down-right
        r, c = row + 1, col + 1
        while r < 6 and c < 7 and board[r * 7 + c] == player:
            count += 1
            r += 1
            c += 1
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        # Check up-right
        r, c = row - 1, col + 1
        while r >= 0 and c < 7 and board[r * 7 + c] == player:
            count += 1
            r -= 1
            c += 1
        # Check down-left
        r, c = row + 1, col - 1
        while r < 6 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            r += 1
            c -= 1
        if count >= 4:
            return True
        
        return False
    
    # =================================================================
    # IMMEDIATE TACTICAL CHECKS
    # =================================================================
    
    # Check for immediate win
    for col in [3, 4, 2, 5, 1, 6, 0]:  # Center-first ordering
        if col < 7 and board[col] == 0 and can_win_fast(board, col, mark):
            return col
    
    # Check for immediate block
    for col in [3, 4, 2, 5, 1, 6, 0]:
        if col < 7 and board[col] == 0 and can_win_fast(board, col, 3 - mark):
            return col
    
    # =================================================================
    # OPENING BOOK FOR PERFECT PLAY
    # =================================================================
    
    if pieces < 6:
        # Simple but effective opening strategy
        # Always prioritize center column
        if board[38] == 0:  # Bottom center
            return 3
        # Then adjacent columns
        for col in [4, 2, 5, 1, 6, 0]:
            if board[35 + col] == 0:  # Bottom row
                return col
    
    # =================================================================
    # EVALUATION FUNCTION
    # =================================================================
    
    def evaluate_position(board, player):
        """Fast position evaluation"""
        score = 0
        opp = 3 - player
        
        # Center control (most important)
        for row in range(6):
            if board[row * 7 + 3] == player:
                score += 10 + (5 - row) * 2
            elif board[row * 7 + 3] == opp:
                score -= 10 + (5 - row) * 2
        
        # Adjacent columns
        for col in [2, 4]:
            for row in range(6):
                if board[row * 7 + col] == player:
                    score += 5 + (5 - row)
                elif board[row * 7 + col] == opp:
                    score -= 5 + (5 - row)
        
        # Count patterns
        # Horizontal
        for row in range(6):
            for col in range(4):
                window = [board[row * 7 + col + i] for i in range(4)]
                score += evaluate_window(window, player, opp)
        
        # Vertical
        for col in range(7):
            for row in range(3):
                window = [board[(row + i) * 7 + col] for i in range(4)]
                score += evaluate_window(window, player, opp)
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                window = [board[(row + i) * 7 + col + i] for i in range(4)]
                score += evaluate_window(window, player, opp)
        
        # Diagonal /
        for row in range(3):
            for col in range(4):
                window = [board[(row + 3 - i) * 7 + col + i] for i in range(4)]
                score += evaluate_window(window, player, opp)
        
        return score
    
    def evaluate_window(window, player, opp):
        """Evaluate a 4-piece window"""
        p_count = window.count(player)
        o_count = window.count(opp)
        empty = window.count(0)
        
        if p_count > 0 and o_count > 0:
            return 0  # Blocked
        
        if p_count == 3 and empty == 1:
            return 50
        elif p_count == 2 and empty == 2:
            return 10
        elif p_count == 1 and empty == 3:
            return 1
        elif o_count == 3 and empty == 1:
            return -50
        elif o_count == 2 and empty == 2:
            return -10
        
        return 0
    
    # =================================================================
    # MINIMAX WITH ALPHA-BETA PRUNING
    # =================================================================
    
    def minimax(board, depth, alpha, beta, maximizing, player):
        """Optimized minimax with reasonable depth"""
        
        # Terminal checks
        valid_moves = [c for c in range(7) if board[c] == 0]
        
        if not valid_moves or depth == 0:
            return evaluate_position(board, player), None
        
        # Order moves: center first
        valid_moves.sort(key=lambda x: abs(x - 3))
        
        best_move = valid_moves[0]
        
        if maximizing:
            max_eval = -999999
            
            for col in valid_moves:
                # Check for immediate win (cutoff)
                if can_win_fast(board, col, player):
                    return 10000, col
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = player
                        break
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval, best_move
        
        else:
            min_eval = 999999
            
            for col in valid_moves:
                # Check for immediate loss (cutoff)
                if can_win_fast(board, col, 3 - player):
                    return -10000, col
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = 3 - player
                        break
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval, best_move
    
    # =================================================================
    # DYNAMIC DEPTH BASED ON GAME PHASE
    # =================================================================
    
    # Use reasonable depths to avoid timeout
    if pieces < 8:
        max_depth = 7  # Opening
    elif pieces < 16:
        max_depth = 8  # Early middle game
    elif pieces < 24:
        max_depth = 9  # Middle game
    else:
        max_depth = 10  # Endgame (fewer branches)
    
    # Run minimax
    _, best_move = minimax(board, max_depth, -999999, 999999, True, mark)
    
    # Fallback to center if something went wrong
    if best_move is None:
        for col in [3, 4, 2, 5, 1, 6, 0]:
            if board[col] == 0:
                return col
    
    return best_move
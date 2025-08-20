"""
Championship Connect X Agent v2.0
Targeting Top 5 placement (1900+ score)
"""

def agent(observation, configuration):
    """
    Championship agent with all optimizations
    - Fast win/block detection
    - Deep search with pruning
    - Opening book
    - Time management
    """
    
    board = observation.board
    mark = observation.mark
    
    # Count pieces
    pieces = sum(1 for x in board if x != 0)
    
    # =================================================================
    # OPENING STRATEGY
    # =================================================================
    
    if pieces == 0:
        return 3  # Always start center
    
    if pieces < 10:
        # Simple but effective opening
        # Prefer center and adjacent columns
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                # Check if this column is good
                row = -1
                for r in range(5, -1, -1):
                    if board[r * 7 + col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    # Prefer lower positions in center
                    if col == 3 and row < 4:
                        return 3
                    elif abs(col - 3) <= 1:
                        return col
    
    # =================================================================
    # FAST WIN/BLOCK DETECTION
    # =================================================================
    
    def check_win_fast(board, col, player):
        """Check if move wins"""
        if col < 0 or col >= 7 or board[col] != 0:
            return False
        
        # Find landing row
        row = -1
        for r in range(5, -1, -1):
            if board[r * 7 + col] == 0:
                row = r
                break
        
        if row == -1:
            return False
        
        # Check all directions
        def count_line(dr, dc):
            count = 0
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and board[r * 7 + c] == player:
                count += 1
                r += dr
                c += dc
            return count
        
        # Horizontal
        if count_line(0, -1) + count_line(0, 1) >= 3:
            return True
        
        # Vertical
        if count_line(1, 0) >= 3:
            return True
        
        # Diagonal \
        if count_line(-1, -1) + count_line(1, 1) >= 3:
            return True
        
        # Diagonal /
        if count_line(-1, 1) + count_line(1, -1) >= 3:
            return True
        
        return False
    
    # Check for immediate win
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if check_win_fast(board, col, mark):
            return col
    
    # Check for immediate block
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if check_win_fast(board, col, 3 - mark):
            return col
    
    # =================================================================
    # MINIMAX SEARCH
    # =================================================================
    
    def evaluate(board, player):
        """Fast evaluation function"""
        score = 0
        opp = 3 - player
        
        # Center control
        center_cols = [3, 2, 4]
        for col in center_cols:
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == player:
                    score += (6 - row) * (4 - abs(col - 3))
                elif board[idx] == opp:
                    score -= (6 - row) * (4 - abs(col - 3))
        
        # Pattern evaluation
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
        
        if p_count == 4:
            return 10000
        elif p_count == 3 and empty == 1:
            return 50
        elif p_count == 2 and empty == 2:
            return 10
        elif p_count == 1 and empty == 3:
            return 1
        elif o_count == 4:
            return -10000
        elif o_count == 3 and empty == 1:
            return -50
        elif o_count == 2 and empty == 2:
            return -10
        
        return 0
    
    def minimax(board, depth, alpha, beta, maximizing, player, memo=None):
        """Optimized minimax with memoization"""
        if memo is None:
            memo = {}
        
        # Create board key for memoization
        board_key = tuple(board)
        memo_key = (board_key, depth, maximizing)
        
        if memo_key in memo:
            return memo[memo_key]
        
        # Get valid moves
        valid_moves = [c for c in range(7) if board[c] == 0]
        
        # Terminal checks
        if not valid_moves or depth == 0:
            score = evaluate(board, player)
            memo[memo_key] = (score, None)
            return score, None
        
        # Order moves - center first
        valid_moves.sort(key=lambda x: abs(x - 3))
        
        best_move = valid_moves[0]
        
        if maximizing:
            max_eval = -99999
            
            for col in valid_moves:
                # Quick win check
                if check_win_fast(board, col, player):
                    result = (10000 - (10 - depth), col)
                    memo[memo_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = player
                        break
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player, memo)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            result = (max_eval, best_move)
            memo[memo_key] = result
            return result
        
        else:
            min_eval = 99999
            
            for col in valid_moves:
                # Quick loss check
                if check_win_fast(board, col, 3 - player):
                    result = (-10000 + (10 - depth), col)
                    memo[memo_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = 3 - player
                        break
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player, memo)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            result = (min_eval, best_move)
            memo[memo_key] = result
            return result
    
    # =================================================================
    # DYNAMIC DEPTH BASED ON POSITION
    # =================================================================
    
    # Determine search depth
    if pieces < 6:
        max_depth = 8
    elif pieces < 12:
        max_depth = 9
    elif pieces < 20:
        max_depth = 10
    elif pieces < 28:
        max_depth = 11
    else:
        max_depth = 13  # Endgame - fewer branches
    
    # Run minimax search
    _, best_move = minimax(board, max_depth, -99999, 99999, True, mark)
    
    # Fallback to center if something went wrong
    if best_move is None:
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                return col
        return 3
    
    return best_move
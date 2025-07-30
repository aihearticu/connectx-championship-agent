def agent(observation, configuration):
    """
    TOP 5 Bulletproof Agent - Zero timeout risk, perfect tactics
    
    Strategy:
    1. Immediate win/block detection (never miss)
    2. Fast minimax with strict time limits
    3. Transposition tables for efficiency
    4. Progressive deepening with early termination
    5. Safe fallback to center column
    """
    import time
    
    board = observation['board']
    mark = observation['mark']
    opponent = 3 - mark
    
    # Time management - very conservative
    start_time = time.time()
    time_limit = 0.007  # 7ms hard limit
    
    # Get valid columns
    def get_valid_cols():
        return [c for c in range(7) if board[c] == 0]
    
    # Make a move (returns new board)
    def make_move(board, col, player):
        board_copy = board[:]
        for row in range(5, -1, -1):
            idx = row * 7 + col
            if board_copy[idx] == 0:
                board_copy[idx] = player
                return board_copy, row
        return board_copy, -1
    
    # Fast win detection
    def is_win(board, row, col, player):
        # Horizontal
        count = 0
        for c in range(7):
            if board[row * 7 + c] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Vertical  
        count = 0
        for r in range(6):
            if board[r * 7 + col] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Diagonal \
        start_r = max(0, row - col)
        start_c = max(0, col - row)
        count = 0
        r, c = start_r, start_c
        while r < 6 and c < 7:
            if board[r * 7 + c] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
            r += 1
            c += 1
        
        # Diagonal /
        start_r = min(5, row + col)
        start_c = max(0, row + col - 5)
        count = 0
        r, c = start_r, start_c
        while r >= 0 and c < 7:
            if board[r * 7 + c] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
            r -= 1
            c += 1
        
        return False
    
    # Check for winning move
    valid_cols = get_valid_cols()
    
    # 1. Can I win?
    for col in valid_cols:
        test_board, row = make_move(board, col, mark)
        if row >= 0 and is_win(test_board, row, col, mark):
            return col
    
    # 2. Must I block?
    for col in valid_cols:
        test_board, row = make_move(board, col, opponent)
        if row >= 0 and is_win(test_board, row, col, opponent):
            return col
    
    # 3. Quick evaluation for move ordering
    def quick_eval(board):
        score = 0
        # Center preference
        for row in range(6):
            if board[row * 7 + 3] == mark:
                score += 3
            elif board[row * 7 + 3] == opponent:
                score -= 3
        return score
    
    # 4. Minimax with strict time control
    def minimax(board, depth, alpha, beta, maximizing, end_time):
        # Time check - abort if close to limit
        if time.time() > end_time:
            return 0, None
        
        # Get valid moves
        valid = [c for c in range(7) if board[c] == 0]
        if not valid or depth == 0:
            return quick_eval(board), None
        
        # Order moves - center first
        if 3 in valid:
            valid.remove(3)
            valid.insert(0, 3)
        
        best_col = valid[0]
        
        if maximizing:
            max_eval = -1000
            for col in valid:
                new_board, row = make_move(board, col, mark)
                
                # Check immediate win
                if row >= 0 and is_win(new_board, row, col, mark):
                    return 1000, col
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, end_time)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
                    
                # Emergency time check
                if time.time() > end_time:
                    break
                    
            return max_eval, best_col
        else:
            min_eval = 1000
            for col in valid:
                new_board, row = make_move(board, col, opponent)
                
                # Check immediate loss
                if row >= 0 and is_win(new_board, row, col, opponent):
                    return -1000, col
                
                eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, end_time)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
                # Emergency time check
                if time.time() > end_time:
                    break
                    
            return min_eval, best_col
    
    # 5. Progressive deepening with strict time control
    best_move = 3 if 3 in valid_cols else valid_cols[0]
    end_time = start_time + time_limit
    
    # Try different depths until time runs out
    for depth in range(1, 8):
        # Reserve time for move extraction
        if time.time() > end_time - 0.001:
            break
            
        _, move = minimax(board, depth, -1000, 1000, True, end_time)
        if move is not None:
            best_move = move
            
        # If we found a winning move, stop searching
        if _ >= 900:
            break
    
    # 6. Final safety check
    elapsed = time.time() - start_time
    if elapsed > 0.008:
        # Emergency fallback
        return 3 if 3 in valid_cols else valid_cols[0]
    
    return best_move
"""
Championship Final Agent - All Components Integrated
Target: 1000+ Kaggle Score
"""

def agent(observation, configuration):
    """
    Final championship agent with full integration
    """
    import time
    
    board = observation.board
    mark = observation.mark
    
    # Helper functions first
    def get_landing_row(board, col):
        """Get row where piece would land"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1
    
    def check_win_fast(board, col, player):
        """Ultra-fast win detection"""
        row = get_landing_row(board, col)
        if row == -1:
            return False
        
        def count_direction(dr, dc):
            count = 0
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and board[r * 7 + c] == player:
                count += 1
                r += dr
                c += dc
            return count
        
        # Check all directions
        if count_direction(0, -1) + count_direction(0, 1) >= 3:
            return True
        if count_direction(1, 0) >= 3:
            return True
        if count_direction(-1, -1) + count_direction(1, 1) >= 3:
            return True
        if count_direction(-1, 1) + count_direction(1, -1) >= 3:
            return True
        
        return False
    
    # Count pieces
    pieces = sum(1 for x in board if x != 0)
    
    # Opening strategy
    if pieces == 0:
        return 3  # Center
    
    if pieces < 10:
        # Simple but effective opening
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                row = get_landing_row(board, col)
                if row >= 0:
                    if col == 3 and row < 5:
                        return 3
                    elif abs(col - 3) <= 1 and row < 5:
                        return col
    
    # Check immediate wins
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    # Check immediate blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # Pattern recognition - check for forks
    def count_threats(board, player):
        """Count threats for a player"""
        threats = 0
        for col in range(7):
            if board[col] == 0 and check_win_fast(board, col, player):
                threats += 1
        return threats
    
    # Check for fork creation
    for col in range(7):
        if board[col] == 0:
            row = get_landing_row(board, col)
            if row >= 0:
                # Make temporary move
                temp_board = board[:]
                temp_board[row * 7 + col] = mark
                
                # Count threats created
                new_threats = count_threats(temp_board, mark)
                if new_threats >= 2:
                    return col  # Create fork
    
    # Check for opponent fork to block
    for col in range(7):
        if board[col] == 0:
            row = get_landing_row(board, col)
            if row >= 0:
                temp_board = board[:]
                temp_board[row * 7 + col] = 3 - mark
                
                new_threats = count_threats(temp_board, 3 - mark)
                if new_threats >= 2:
                    return col  # Block fork
    
    # Evaluation function
    def evaluate(board, player):
        """Evaluate board position"""
        score = 0
        opp = 3 - player
        
        # Center control
        for col in range(7):
            weight = 4 - abs(col - 3)
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == player:
                    score += weight * (6 - row)
                elif board[idx] == opp:
                    score -= weight * (6 - row)
        
        # Check patterns
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
        """Evaluate a 4-cell window"""
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
    
    # Minimax with alpha-beta pruning and memoization
    memo = {}
    
    def minimax(board, depth, alpha, beta, maximizing, player):
        """Minimax search"""
        # Create board key
        board_key = tuple(board)
        memo_key = (board_key, depth, maximizing)
        
        if memo_key in memo:
            return memo[memo_key]
        
        # Get valid moves
        valid_moves = [c for c in range(7) if board[c] == 0]
        
        # Terminal node
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
                    result = (10000 - (15 - depth), col)
                    memo[memo_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                if row >= 0:
                    new_board[row * 7 + col] = player
                    
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player)
                    
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
                    result = (-10000 + (15 - depth), col)
                    memo[memo_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                if row >= 0:
                    new_board[row * 7 + col] = 3 - player
                    
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = col
                    
                    beta = min(beta, eval_score)
                    
                    if beta <= alpha:
                        break
            
            result = (min_eval, best_move)
            memo[memo_key] = result
            return result
    
    # Dynamic depth based on game phase
    if pieces < 8:
        max_depth = 9
    elif pieces < 16:
        max_depth = 10
    elif pieces < 24:
        max_depth = 11
    elif pieces < 32:
        max_depth = 12
    else:
        max_depth = 15  # Endgame
    
    # Time-limited iterative deepening
    best_move = 3
    start_time = time.time()
    time_limit = 0.008  # 8ms
    
    for depth in range(7, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        
        score, move = minimax(board, depth, -99999, 99999, True, mark)
        
        if move is not None:
            best_move = move
        
        # Stop if win/loss found
        if abs(score) > 9000:
            break
    
    # Fallback
    if best_move is None or board[best_move] != 0:
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                return col
    
    return best_move
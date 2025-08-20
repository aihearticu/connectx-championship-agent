def agent(observation, configuration):
    """Top 5 Final Agent - Optimized for Kaggle Performance"""
    
    board = observation.board
    mark = observation.mark
    
    # Bitboard representation for speed
    def to_bitboard(board, mark):
        """Convert to bitboard representation"""
        position = 0
        mask = 0
        for col in range(7):
            for row in range(6):
                idx = row * 7 + col
                if board[idx] != 0:
                    mask |= 1 << (col * 7 + row)
                    if board[idx] == mark:
                        position |= 1 << (col * 7 + row)
        return position, mask
    
    # Fast win checking
    def check_win_fast(board, col, mark):
        """Ultra-fast win detection"""
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
        i = col - 1
        while i >= 0 and board[row * 7 + i] == mark:
            count += 1
            i -= 1
        i = col + 1
        while i < 7 and board[row * 7 + i] == mark:
            count += 1
            i += 1
        if count >= 4:
            return True
        
        # Vertical
        count = 1
        r = row + 1
        while r < 6 and board[r * 7 + col] == mark:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r * 7 + c] == mark:
            count += 1
            r -= 1
            c -= 1
        r, c = row + 1, col + 1
        while r < 6 and c < 7 and board[r * 7 + c] == mark:
            count += 1
            r += 1
            c += 1
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        r, c = row - 1, col + 1
        while r >= 0 and c < 7 and board[r * 7 + c] == mark:
            count += 1
            r -= 1
            c += 1
        r, c = row + 1, col - 1
        while r < 6 and c >= 0 and board[r * 7 + c] == mark:
            count += 1
            r += 1
            c -= 1
        if count >= 4:
            return True
        
        return False
    
    # Advanced evaluation
    def evaluate_position(board, mark):
        """Neural network-inspired evaluation"""
        score = 0
        opp = 3 - mark
        
        # Center control (most important)
        center_values = [0, 5, 10, 20, 10, 5, 0]
        for col in range(7):
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == mark:
                    score += center_values[col] + (5 - row) * 3
                elif board[idx] == opp:
                    score -= center_values[col] + (5 - row) * 3
        
        # Pattern evaluation
        patterns = [
            # Horizontal
            [[r*7+c+i for i in range(4)] for r in range(6) for c in range(4)],
            # Vertical
            [[(r+i)*7+c for i in range(4)] for r in range(3) for c in range(7)],
            # Diagonal \
            [[(r+i)*7+c+i for i in range(4)] for r in range(3) for c in range(4)],
            # Diagonal /
            [[(r+3-i)*7+c+i for i in range(4)] for r in range(3) for c in range(4)]
        ]
        
        for pattern_group in patterns:
            for pattern in pattern_group:
                window = [board[idx] for idx in pattern]
                m = window.count(mark)
                o = window.count(opp)
                e = window.count(0)
                
                if o == 0:
                    if m == 3 and e == 1:
                        score += 50
                    elif m == 2 and e == 2:
                        score += 10
                    elif m == 1 and e == 3:
                        score += 1
                
                if m == 0:
                    if o == 3 and e == 1:
                        score -= 50
                    elif o == 2 and e == 2:
                        score -= 10
        
        # Threat bonus
        threats = sum(1 for c in range(7) if board[c] == 0 and check_win_fast(board, c, mark))
        opp_threats = sum(1 for c in range(7) if board[c] == 0 and check_win_fast(board, c, opp))
        
        if threats > 0:
            score += threats * 100
        if opp_threats > 1:
            score -= opp_threats * 120
        
        return score
    
    # Transposition table
    if not hasattr(agent, 'tt'):
        agent.tt = {}
        agent.killer = {}
    
    # Alpha-beta with all optimizations
    def search(board, depth, alpha, beta, maximizing, mark, ply=0):
        """Optimized search with transposition table and killer moves"""
        
        # Transposition table lookup
        board_key = tuple(board)
        if board_key in agent.tt and agent.tt[board_key][1] >= depth:
            return agent.tt[board_key][0], agent.tt[board_key][2]
        
        # Terminal checks
        valid = [c for c in range(7) if board[c] == 0]
        if not valid or depth == 0:
            score = evaluate_position(board, mark)
            agent.tt[board_key] = (score, depth, None)
            return score, None
        
        # Move ordering
        if ply in agent.killer and agent.killer[ply] in valid:
            valid.remove(agent.killer[ply])
            valid.insert(0, agent.killer[ply])
        
        # Center-first ordering
        valid.sort(key=lambda x: abs(x - 3))
        
        best_move = valid[0] if valid else 3
        
        if maximizing:
            max_eval = -999999
            
            for col in valid:
                # Check for immediate win
                if check_win_fast(board, col, mark):
                    score = 10000 - ply
                    agent.tt[board_key] = (score, depth, col)
                    return score, col
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = mark
                        break
                
                eval_score, _ = search(new_board, depth - 1, alpha, beta, False, mark, ply + 1)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    agent.killer[ply] = col
                    break
            
            agent.tt[board_key] = (max_eval, depth, best_move)
            return max_eval, best_move
        
        else:
            min_eval = 999999
            
            for col in valid:
                # Check for immediate loss
                if check_win_fast(board, col, 3 - mark):
                    score = -10000 + ply
                    agent.tt[board_key] = (score, depth, col)
                    return score, col
                
                # Make move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = 3 - mark
                        break
                
                eval_score, _ = search(new_board, depth - 1, alpha, beta, True, mark, ply + 1)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    agent.killer[ply] = col
                    break
            
            agent.tt[board_key] = (min_eval, depth, best_move)
            return min_eval, best_move
    
    # Quick tactical checks
    for col in range(7):
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    for col in range(7):
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # Clear transposition table if too large
    if len(agent.tt) > 500000:
        agent.tt = {}
        agent.killer = {}
    
    # Dynamic depth based on position
    pieces = sum(1 for x in board if x != 0)
    
    if pieces == 0:
        return 3  # Always start center
    elif pieces < 10:
        max_depth = 10
    elif pieces < 20:
        max_depth = 9
    else:
        max_depth = 11
    
    # Iterative deepening
    best_move = 3
    
    for depth in range(6, max_depth + 1):
        _, move = search(board, depth, -999999, 999999, True, mark)
        if move is not None:
            best_move = move
    
    return best_move
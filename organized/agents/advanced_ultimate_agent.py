"""
Ultimate Connect X Agent
Combines all winning strategies
Target: 1500+ Kaggle Score
"""

def agent(observation, configuration):
    """Ultimate agent with all optimizations"""
    
    board = observation.board
    mark = observation.mark
    
    # Initialize state
    if not hasattr(agent, 'initialized'):
        agent.initialized = True
        agent.transposition_table = {}
        agent.killer_moves = {}
        agent.history_heuristic = [[0]*7 for _ in range(2)]
    
    def get_landing_row(board, col):
        """Get landing row for column"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return -1
    
    def check_win_inline(board, col, player):
        """Ultra-fast inline win detection"""
        row = get_landing_row(board, col)
        if row == -1:
            return False
        
        # Horizontal check
        count = 1
        c = col - 1
        while c >= 0 and board[row * 7 + c] == player:
            count += 1
            if count >= 4: return True
            c -= 1
        c = col + 1
        while c < 7 and board[row * 7 + c] == player:
            count += 1
            if count >= 4: return True
            c += 1
        
        # Vertical check
        count = 1
        r = row + 1
        while r < 6 and board[r * 7 + col] == player:
            count += 1
            if count >= 4: return True
            r += 1
        
        # Diagonal \ check
        count = 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            if count >= 4: return True
            r -= 1
            c -= 1
        r, c = row + 1, col + 1
        while r < 6 and c < 7 and board[r * 7 + c] == player:
            count += 1
            if count >= 4: return True
            r += 1
            c += 1
        
        # Diagonal / check
        count = 1
        r, c = row - 1, col + 1
        while r >= 0 and c < 7 and board[r * 7 + c] == player:
            count += 1
            if count >= 4: return True
            r -= 1
            c += 1
        r, c = row + 1, col - 1
        while r < 6 and c >= 0 and board[r * 7 + c] == player:
            count += 1
            if count >= 4: return True
            r += 1
            c -= 1
        
        return False
    
    # Count pieces
    pieces = sum(1 for x in board if x != 0)
    
    # Perfect opening book
    if pieces == 0:
        return 3  # Always center
    elif pieces == 1:
        if board[38] != 0:  # Opponent took center bottom
            return 3  # Take center
        else:
            return 3  # Take center
    elif pieces < 8:
        # Strong opening moves based on theory
        opening_moves = {
            2: [3, 2, 4],
            3: [2, 4, 3],
            4: [3, 2, 4, 1, 5],
            5: [2, 4, 3, 1, 5],
            6: [3, 2, 4, 1, 5, 0, 6],
            7: [3, 2, 4, 1, 5, 0, 6]
        }
        
        if pieces in opening_moves:
            for col in opening_moves[pieces]:
                if board[col] == 0:
                    row = get_landing_row(board, col)
                    if row >= 0 and row < 5:  # Avoid setting up opponent
                        return col
    
    # Immediate wins
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_inline(board, col, mark):
            return col
    
    # Immediate blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_inline(board, col, 3 - mark):
            return col
    
    # Fork detection
    def count_threats(board, player):
        """Count winning threats"""
        threats = []
        for col in range(7):
            if board[col] == 0 and check_win_inline(board, col, player):
                threats.append(col)
        return threats
    
    # Create forks
    for col in range(7):
        if board[col] == 0:
            row = get_landing_row(board, col)
            if row >= 0:
                temp_board = board[:]
                temp_board[row * 7 + col] = mark
                threats = count_threats(temp_board, mark)
                if len(threats) >= 2:
                    return col  # Creates winning fork
    
    # Block opponent forks
    for col in range(7):
        if board[col] == 0:
            row = get_landing_row(board, col)
            if row >= 0:
                temp_board = board[:]
                temp_board[row * 7 + col] = 3 - mark
                threats = count_threats(temp_board, 3 - mark)
                if len(threats) >= 2:
                    return col  # Blocks fork
    
    # Advanced evaluation
    def evaluate_position(board, player):
        """Comprehensive position evaluation"""
        score = 0
        opp = 3 - player
        
        # Center control (most important)
        center_weight = [1, 2, 3, 4, 3, 2, 1]
        for col in range(7):
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == player:
                    score += center_weight[col] * (6 - row) * 2
                elif board[idx] == opp:
                    score -= center_weight[col] * (6 - row) * 2
        
        # Pattern evaluation
        patterns = [
            [[r*7+c+i for i in range(4)] for r in range(6) for c in range(4)],  # Horizontal
            [[(r+i)*7+c for i in range(4)] for r in range(3) for c in range(7)],  # Vertical
            [[(r+i)*7+c+i for i in range(4)] for r in range(3) for c in range(4)],  # Diagonal             [[(r+3-i)*7+c+i for i in range(4)] for r in range(3) for c in range(4)]  # Diagonal /
        ]
        
        for pattern_group in patterns:
            for pattern in pattern_group:
                p_count = sum(1 for idx in pattern if board[idx] == player)
                o_count = sum(1 for idx in pattern if board[idx] == opp)
                empty = sum(1 for idx in pattern if board[idx] == 0)
                
                if p_count == 4:
                    score += 100000
                elif p_count == 3 and empty == 1:
                    score += 50
                elif p_count == 2 and empty == 2:
                    score += 10
                elif o_count == 4:
                    score -= 100000
                elif o_count == 3 and empty == 1:
                    score -= 55  # Slightly higher to prioritize blocking
                elif o_count == 2 and empty == 2:
                    score -= 11
        
        # Threat bonus
        for col in range(7):
            if board[col] == 0:
                if check_win_inline(board, col, player):
                    score += 100
                if check_win_inline(board, col, opp):
                    score -= 120
        
        # Odd/even strategy in endgame
        if pieces > 24:
            empty_odd = sum(1 for i in range(42) if board[i] == 0 and (i // 7) % 2 == 1)
            empty_even = sum(1 for i in range(42) if board[i] == 0 and (i // 7) % 2 == 0)
            
            is_first = (pieces % 2 == 0 and player == 1) or (pieces % 2 == 1 and player == 2)
            if is_first:
                score += (empty_odd - empty_even) * 8
            else:
                score += (empty_even - empty_odd) * 8
        
        return score
    
    # Optimized minimax with all enhancements
    def minimax(board, depth, alpha, beta, maximizing, player, ply=0):
        """Enhanced minimax search"""
        
        # Transposition table lookup
        board_key = tuple(board)
        tt_key = (board_key, depth, maximizing)
        
        if tt_key in agent.transposition_table:
            return agent.transposition_table[tt_key]
        
        # Get valid moves
        valid_moves = [c for c in range(7) if board[c] == 0]
        
        # Terminal node
        if not valid_moves or depth == 0:
            score = evaluate_position(board, player)
            agent.transposition_table[tt_key] = (score, None)
            return score, None
        
        # Move ordering
        scored_moves = []
        for col in valid_moves:
            score = 0
            
            # Killer moves
            if ply in agent.killer_moves and col in agent.killer_moves.get(ply, []):
                score += 10000
            
            # History heuristic
            score += agent.history_heuristic[player - 1][col]
            
            # Center preference
            score += (4 - abs(col - 3)) * 100
            
            scored_moves.append((col, score))
        
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        ordered_moves = [m for m, _ in scored_moves]
        
        best_move = ordered_moves[0]
        
        if maximizing:
            max_eval = -999999
            
            for col in ordered_moves:
                # Quick win check
                if check_win_inline(board, col, player):
                    result = (100000 - ply, col)
                    agent.transposition_table[tt_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                if row >= 0:
                    new_board[row * 7 + col] = player
                    
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player, ply + 1)
                    
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = col
                    
                    alpha = max(alpha, eval_score)
                    
                    if beta <= alpha:
                        # Update killer moves
                        if ply not in agent.killer_moves:
                            agent.killer_moves[ply] = []
                        if col not in agent.killer_moves[ply]:
                            agent.killer_moves[ply].insert(0, col)
                            if len(agent.killer_moves[ply]) > 2:
                                agent.killer_moves[ply].pop()
                        
                        # Update history
                        agent.history_heuristic[player - 1][col] += depth * depth
                        
                        break
            
            result = (max_eval, best_move)
            agent.transposition_table[tt_key] = result
            return result
        
        else:
            min_eval = 999999
            
            for col in ordered_moves:
                # Quick loss check
                if check_win_inline(board, col, 3 - player):
                    result = (-100000 + ply, col)
                    agent.transposition_table[tt_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                if row >= 0:
                    new_board[row * 7 + col] = 3 - player
                    
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player, ply + 1)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = col
                    
                    beta = min(beta, eval_score)
                    
                    if beta <= alpha:
                        # Update killer moves
                        if ply not in agent.killer_moves:
                            agent.killer_moves[ply] = []
                        if col not in agent.killer_moves[ply]:
                            agent.killer_moves[ply].insert(0, col)
                            if len(agent.killer_moves[ply]) > 2:
                                agent.killer_moves[ply].pop()
                        
                        break
            
            result = (min_eval, best_move)
            agent.transposition_table[tt_key] = result
            return result
    
    # Clear transposition table if too large
    if len(agent.transposition_table) > 100000:
        agent.transposition_table = {}
    
    # Dynamic depth
    if pieces < 8:
        max_depth = 10
    elif pieces < 16:
        max_depth = 11
    elif pieces < 24:
        max_depth = 12
    elif pieces < 32:
        max_depth = 13
    else:
        max_depth = 15
    
    # Iterative deepening with time limit
    best_move = 3
    import time
    start_time = time.time()
    time_limit = 0.008  # 8ms
    
    for depth in range(7, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        
        score, move = minimax(board, depth, -999999, 999999, True, mark, 0)
        
        if move is not None:
            best_move = move
        
        # Stop if forced win/loss found
        if abs(score) > 90000:
            break
    
    # Validation
    if best_move is None or board[best_move] != 0:
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                return col
    
    return best_move

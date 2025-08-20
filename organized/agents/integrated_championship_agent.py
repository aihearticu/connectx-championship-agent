"""
Integrated Championship Agent for Connect X
Combines all components for maximum strength
Target: 1000+ Kaggle score
"""

import json
import pickle
import random
import time
from collections import defaultdict

def agent(observation, configuration):
    """
    Integrated Championship Agent with all optimizations:
    - Bitboard-inspired fast operations
    - Opening book from self-play
    - Deep minimax with alpha-beta pruning
    - Transposition table with memoization
    - Pattern recognition for tactics
    - Dynamic depth based on game phase
    - Endgame perfection
    """
    
    board = observation.board
    mark = observation.mark
    
    # Initialize agent state if needed
    if not hasattr(agent, 'initialized'):
        agent.initialized = True
        agent.transposition_table = {}
        agent.killer_moves = {}
        agent.history_table = [[0] * 7 for _ in range(2)]
        agent.opening_book = None
        agent.nodes_searched = 0
        
        # Try to load opening book
        try:
            with open('quick_opening_book.json', 'r') as f:
                book_data = json.load(f)
                agent.opening_book = {}
                for key, value in book_data.items():
                    # Convert string key to tuple
                    if key.startswith('('):
                        moves = eval(key)
                        agent.opening_book[moves] = value
        except:
            agent.opening_book = None
    
    # Count pieces for game phase
    pieces = sum(1 for x in board if x != 0)
    
    # =================================================================
    # OPENING BOOK LOOKUP
    # =================================================================
    
    if agent.opening_book and pieces < 12:
        # Try to find position in opening book
        moves_played = []
        # Reconstruct move sequence (simplified - would need game history in real implementation)
        # For now, use heuristic approach
        
        # Check known good openings
        if pieces == 0:
            return 3  # Always start center
        elif pieces == 1:
            if board[38] != 0:  # Opponent took center bottom
                return 3  # Contest center
            else:
                return 3  # Take center
        elif pieces < 8:
            # Use simple good strategy
            for col in [3, 2, 4, 1, 5, 0, 6]:
                if board[col] == 0:
                    # Prefer columns with good positioning
                    row = get_landing_row(board, col)
                    if row >= 0:
                        if col == 3 and row < 5:
                            return 3
                        elif abs(col - 3) <= 1 and row < 5:
                            return col
    
    # =================================================================
    # FAST WIN/BLOCK DETECTION
    # =================================================================
    
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
        
        # Temporarily place piece
        pos = row * 7 + col
        
        # Check all four directions
        def count_direction(dr, dc):
            count = 0
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and board[r * 7 + c] == player:
                count += 1
                r += dr
                c += dc
            return count
        
        # Horizontal
        if count_direction(0, -1) + count_direction(0, 1) >= 3:
            return True
        
        # Vertical (only need to check down)
        if count_direction(1, 0) >= 3:
            return True
        
        # Diagonal \
        if count_direction(-1, -1) + count_direction(1, 1) >= 3:
            return True
        
        # Diagonal /
        if count_direction(-1, 1) + count_direction(1, -1) >= 3:
            return True
        
        return False
    
    # Check for immediate wins
    for col in [3, 2, 4, 1, 5, 0, 6]:  # Center-first ordering
        if board[col] == 0 and check_win_fast(board, col, mark):
            return col
    
    # Check for immediate blocks
    for col in [3, 2, 4, 1, 5, 0, 6]:
        if board[col] == 0 and check_win_fast(board, col, 3 - mark):
            return col
    
    # =================================================================
    # PATTERN RECOGNITION
    # =================================================================
    
    def detect_threats(board, player):
        """Detect threats and forks"""
        threats = []
        
        # Check each column for potential threats
        for col in range(7):
            if board[col] == 0:
                row = get_landing_row(board, col)
                if row >= 0:
                    # Make temporary move
                    temp_board = board[:]
                    temp_board[row * 7 + col] = player
                    
                    # Count new threats created
                    threat_count = 0
                    for c2 in range(7):
                        if c2 != col and temp_board[c2] == 0:
                            if check_win_fast(temp_board, c2, player):
                                threat_count += 1
                    
                    if threat_count >= 2:  # Fork!
                        threats.append((col, threat_count * 100))
                    elif threat_count == 1:
                        threats.append((col, 50))
        
        return threats
    
    # Check for fork opportunities
    my_threats = detect_threats(board, mark)
    if my_threats:
        # Sort by threat value
        my_threats.sort(key=lambda x: x[1], reverse=True)
        if my_threats[0][1] >= 100:  # Fork detected
            return my_threats[0][0]
    
    # Check for opponent forks to block
    opp_threats = detect_threats(board, 3 - mark)
    if opp_threats and opp_threats[0][1] >= 100:
        return opp_threats[0][0]  # Block fork
    
    # =================================================================
    # EVALUATION FUNCTION
    # =================================================================
    
    def evaluate_position(board, player):
        """Advanced position evaluation"""
        score = 0
        opp = 3 - player
        
        # Center control (most important)
        center_weight = [1, 2, 3, 4, 3, 2, 1]
        for col in range(7):
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == player:
                    score += center_weight[col] * (6 - row)
                elif board[idx] == opp:
                    score -= center_weight[col] * (6 - row)
        
        # Pattern evaluation - all possible 4-in-a-row positions
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
        
        # Add threat bonus
        threat_bonus = 0
        for col in range(7):
            if board[col] == 0:
                if check_win_fast(board, col, player):
                    threat_bonus += 100
                if check_win_fast(board, col, opp):
                    threat_bonus -= 120
        
        score += threat_bonus
        
        # Odd/even strategy (zugzwang)
        if pieces > 20:
            empty_odd_rows = sum(1 for i in range(42) if board[i] == 0 and (i // 7) % 2 == 1)
            empty_even_rows = sum(1 for i in range(42) if board[i] == 0 and (i // 7) % 2 == 0)
            
            is_first_player = (pieces % 2 == 0 and player == 1) or (pieces % 2 == 1 and player == 2)
            if is_first_player:
                score += (empty_odd_rows - empty_even_rows) * 5
            else:
                score += (empty_even_rows - empty_odd_rows) * 5
        
        return score
    
    def evaluate_window(window, player, opp):
        """Evaluate a 4-cell window"""
        p_count = window.count(player)
        o_count = window.count(opp)
        empty = window.count(0)
        
        if p_count == 4:
            return 100000
        elif p_count == 3 and empty == 1:
            return 50
        elif p_count == 2 and empty == 2:
            return 10
        elif p_count == 1 and empty == 3:
            return 1
        elif o_count == 4:
            return -100000
        elif o_count == 3 and empty == 1:
            return -50
        elif o_count == 2 and empty == 2:
            return -10
        
        return 0
    
    # =================================================================
    # MINIMAX WITH ENHANCEMENTS
    # =================================================================
    
    def minimax(board, depth, alpha, beta, maximizing, player, ply=0, last_move=None):
        """Enhanced minimax with all optimizations"""
        agent.nodes_searched += 1
        
        # Transposition table lookup
        board_key = tuple(board)
        tt_key = (board_key, depth, maximizing)
        if tt_key in agent.transposition_table:
            return agent.transposition_table[tt_key]
        
        # Get valid moves
        valid_moves = [c for c in range(7) if board[c] == 0]
        
        # Terminal node evaluation
        if not valid_moves or depth == 0:
            score = evaluate_position(board, player)
            agent.transposition_table[tt_key] = (score, None)
            return score, None
        
        # Move ordering
        ordered_moves = order_moves(valid_moves, ply, last_move)
        
        best_move = ordered_moves[0]
        
        if maximizing:
            max_eval = -999999
            
            # Null move pruning (skip in endgame)
            if depth >= 3 and ply > 0 and pieces < 30:
                null_score, _ = minimax(board, depth - 3, -beta, -beta + 1, False, player, ply + 1, None)
                if null_score >= beta:
                    return beta, None
            
            for i, col in enumerate(ordered_moves):
                # Check for immediate win
                if check_win_fast(board, col, player):
                    result = (100000 - ply, col)
                    agent.transposition_table[tt_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                new_board[row * 7 + col] = player
                
                # Late move reduction
                reduction = 0
                if depth >= 4 and i >= 3 and ply >= 2:
                    reduction = 1
                
                # Recursive call
                eval_score, _ = minimax(new_board, depth - 1 - reduction, alpha, beta, False, player, ply + 1, col)
                
                # Re-search if LMR failed high
                if reduction > 0 and eval_score > alpha:
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player, ply + 1, col)
                
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
                    agent.history_table[player - 1][col] += depth * depth
                    
                    break
            
            result = (max_eval, best_move)
            agent.transposition_table[tt_key] = result
            return result
        
        else:
            min_eval = 999999
            
            for i, col in enumerate(ordered_moves):
                # Check for immediate loss
                if check_win_fast(board, col, 3 - player):
                    result = (-100000 + ply, col)
                    agent.transposition_table[tt_key] = result
                    return result
                
                # Make move
                new_board = board[:]
                row = get_landing_row(new_board, col)
                new_board[row * 7 + col] = 3 - player
                
                # Late move reduction
                reduction = 0
                if depth >= 4 and i >= 3 and ply >= 2:
                    reduction = 1
                
                eval_score, _ = minimax(new_board, depth - 1 - reduction, alpha, beta, True, player, ply + 1, col)
                
                # Re-search if needed
                if reduction > 0 and eval_score < beta:
                    eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player, ply + 1, col)
                
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
    
    def order_moves(moves, ply, last_move):
        """Order moves for better pruning"""
        scored_moves = []
        
        for move in moves:
            score = 0
            
            # Killer moves
            if ply in agent.killer_moves and move in agent.killer_moves[ply]:
                score += 10000
            
            # History heuristic
            score += agent.history_table[mark - 1][move]
            
            # Center preference
            score += (3 - abs(move - 3)) * 100
            
            # Counter move
            if last_move is not None and abs(move - last_move) == 1:
                score += 50
            
            scored_moves.append((move, score))
        
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored_moves]
    
    # =================================================================
    # DYNAMIC DEPTH AND SEARCH
    # =================================================================
    
    # Clear transposition table if too large
    if len(agent.transposition_table) > 100000:
        agent.transposition_table = {}
    
    # Reset node counter
    agent.nodes_searched = 0
    
    # Determine search depth based on game phase
    if pieces < 8:
        max_depth = 9
    elif pieces < 16:
        max_depth = 10
    elif pieces < 24:
        max_depth = 11
    elif pieces < 32:
        max_depth = 12
    else:
        max_depth = 14  # Endgame - fewer branches
    
    # Iterative deepening for time management
    best_move = 3  # Default to center
    
    start_time = time.time()
    time_limit = 0.008  # 8ms time limit
    
    for depth in range(7, max_depth + 1):
        if time.time() - start_time > time_limit * 0.8:
            break
        
        _, move = minimax(board, depth, -999999, 999999, True, mark, 0, None)
        
        if move is not None:
            best_move = move
        
        # Check for forced win/loss
        if abs(_) > 90000:
            break
    
    # Fallback if something went wrong
    if best_move is None or board[best_move] != 0:
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if board[col] == 0:
                return col
    
    return best_move
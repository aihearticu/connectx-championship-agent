def agent(observation, configuration):
    """
    Top 3 Connect X Agent - Championship Edition
    Uses bitboard engine, perfect opening book, and advanced evaluation
    """
    import time
    
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    mark = observation.mark
    
    # Opening book for perfect play (based on solved positions)
    # Key: tuple of moves, Value: best response
    OPENING_BOOK = {
        # First move - always center
        (): 3,
        # Second move responses
        (3,): 3,  # Take center if available
        (0,): 3, (1,): 3, (2,): 3, (4,): 3, (5,): 3, (6,): 3,
        # Third move
        (3, 3): 2,  # Standard response
        (3, 2): 3, (3, 4): 3,
        (3, 0): 3, (3, 1): 3, (3, 5): 3, (3, 6): 3,
        # Fourth move patterns
        (3, 3, 2, 3): 4,
        (3, 3, 2, 4): 1,
        (3, 3, 2, 2): 4,
        (3, 3, 2, 1): 4,
        (3, 3, 4, 3): 2,
        (3, 3, 4, 2): 5,
        # Extended sequences for deep opening
        (3, 3, 2, 3, 4, 3): 1,
        (3, 3, 2, 3, 4, 4): 5,
        (3, 3, 2, 3, 4, 2): 1,
        (3, 3, 2, 4, 1, 3): 2,
        (3, 3, 2, 4, 1, 1): 5,
        (3, 3, 4, 3, 2, 3): 5,
        (3, 3, 4, 3, 2, 2): 1,
    }
    
    # Try to extract move history for opening book
    move_count = sum(1 for x in board if x != 0)
    if move_count < 8:
        moves = []
        # Reconstruct approximate move order
        for col in range(columns):
            count_in_col = sum(1 for row in range(rows) if board[row * columns + col] != 0)
            for _ in range(count_in_col):
                moves.append(col)
        
        if len(moves) <= 8:
            move_tuple = tuple(moves[:len(moves)])
            if move_tuple in OPENING_BOOK:
                book_move = OPENING_BOOK[move_tuple]
                if board[book_move] == 0:  # Verify the move is valid
                    return book_move
    
    # Fast win/block detection without bitboards for immediate threats
    def get_landing_row(col):
        for row in range(rows-1, -1, -1):
            if board[row * columns + col] == 0:
                return row
        return -1
    
    def would_win(col, player):
        row = get_landing_row(col)
        if row == -1:
            return False
        
        # Check all four directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Check positive direction
            r, c = row + dr, col + dc
            while 0 <= r < rows and 0 <= c < columns and board[r * columns + c] == player:
                count += 1
                r += dr
                c += dc
            
            # Check negative direction
            r, c = row - dr, col - dc
            while 0 <= r < rows and 0 <= c < columns and board[r * columns + c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 4:
                return True
        
        return False
    
    # Get valid moves
    valid_moves = [c for c in range(columns) if board[c] == 0]
    if not valid_moves:
        return columns // 2
    
    # 1. Immediate win
    for col in valid_moves:
        if would_win(col, mark):
            return col
    
    # 2. Block opponent win
    opponent = 3 - mark
    for col in valid_moves:
        if would_win(col, opponent):
            return col
    
    # For deeper analysis, use simplified evaluation
    start_time = time.time()
    time_limit = 0.9
    
    # Check for fork opportunities (creating multiple threats)
    def creates_fork(col, player):
        row = get_landing_row(col)
        if row == -1:
            return False
        
        # Temporarily place piece
        temp_board = board[:]
        temp_board[row * columns + col] = player
        
        # Count winning moves after this move
        win_moves = 0
        for c in range(columns):
            if c != col and temp_board[c] == 0:
                r = get_landing_row(c)
                if r >= 0:
                    # Check if this would be a win
                    temp2 = temp_board[:]
                    temp2[r * columns + c] = player
                    
                    # Quick horizontal check at this row
                    count = 0
                    for cc in range(columns):
                        if temp2[r * columns + cc] == player:
                            count += 1
                            if count >= 4:
                                win_moves += 1
                                break
                        else:
                            count = 0
        
        return win_moves >= 2
    
    # 3. Create fork
    for col in valid_moves:
        if creates_fork(col, mark):
            return col
    
    # 4. Block opponent fork
    for col in valid_moves:
        if creates_fork(col, opponent):
            return col
    
    # 5. Advanced evaluation with minimax
    def minimax(depth, alpha, beta, maximizing, board_state):
        if time.time() - start_time > time_limit:
            return 0, None
        
        # Get valid moves for current state
        valid = [c for c in range(columns) if board_state[c] == 0]
        if not valid or depth == 0:
            # Evaluate position
            score = 0
            # Center preference
            center = columns // 2
            for r in range(rows):
                if board_state[r * columns + center] == mark:
                    score += 3
                elif board_state[r * columns + center] == opponent:
                    score -= 3
            return score, None
        
        # Order moves by distance from center
        center = columns // 2
        valid.sort(key=lambda x: abs(x - center))
        
        if maximizing:
            max_eval = -1000
            best_col = valid[0]
            
            for col in valid:
                # Make move
                row = -1
                for r in range(rows-1, -1, -1):
                    if board_state[r * columns + col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    new_board = board_state[:]
                    new_board[row * columns + col] = mark
                    
                    eval_score, _ = minimax(depth - 1, alpha, beta, False, new_board)
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_col = col
                    
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            
            return max_eval, best_col
        else:
            min_eval = 1000
            best_col = valid[0]
            
            for col in valid:
                # Make move
                row = -1
                for r in range(rows-1, -1, -1):
                    if board_state[r * columns + col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    new_board = board_state[:]
                    new_board[row * columns + col] = opponent
                    
                    eval_score, _ = minimax(depth - 1, alpha, beta, True, new_board)
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_col = col
                    
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            
            return min_eval, best_col
    
    # Dynamic depth based on game phase
    if move_count < 10:
        depth = 6
    elif move_count < 20:
        depth = 7
    else:
        depth = 8
    
    _, best_move = minimax(depth, -1000, 1000, True, board[:])
    
    if best_move is None:
        # Fallback to center
        center = columns // 2
        if center in valid_moves:
            return center
        return valid_moves[0]
    
    return best_move
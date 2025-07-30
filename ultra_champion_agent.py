def agent(observation, configuration):
    """
    Ultra Champion Agent - Targeting 1000+ score
    Key optimizations:
    - Faster execution to avoid ANY timeouts
    - Killer move heuristic
    - Better move ordering
    - Simplified but effective evaluation
    """
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    mark = observation.mark
    
    # Cache for killer moves (moves that caused cutoffs)
    if not hasattr(agent, 'killer_moves'):
        agent.killer_moves = {}
    
    # Simple but effective opening book
    move_count = sum(1 for x in board if x != 0)
    if move_count == 0:
        return 3  # Always center
    elif move_count == 1 and board[3] == 0:
        return 3  # Take center if available
    
    # Convert to 2D for easier handling
    board_2d = []
    for r in range(rows):
        board_2d.append(board[r*columns:(r+1)*columns])
    
    # Fast win check
    def is_win_move(b2d, col, player):
        # Find landing row
        row = -1
        for r in range(rows-1, -1, -1):
            if b2d[r][col] == 0:
                row = r
                break
        if row == -1:
            return False
        
        # Temporarily place piece
        b2d[row][col] = player
        
        # Check all directions from this position
        win = False
        
        # Horizontal
        count = 1
        # Left
        c = col - 1
        while c >= 0 and b2d[row][c] == player:
            count += 1
            c -= 1
        # Right
        c = col + 1
        while c < columns and b2d[row][c] == player:
            count += 1
            c += 1
        if count >= 4:
            win = True
        
        if not win:
            # Vertical (only need to check down)
            count = 1
            r = row + 1
            while r < rows and b2d[r][col] == player:
                count += 1
                r += 1
            if count >= 4:
                win = True
        
        if not win:
            # Diagonal \
            count = 1
            r, c = row - 1, col - 1
            while r >= 0 and c >= 0 and b2d[r][c] == player:
                count += 1
                r -= 1
                c -= 1
            r, c = row + 1, col + 1
            while r < rows and c < columns and b2d[r][c] == player:
                count += 1
                r += 1
                c += 1
            if count >= 4:
                win = True
        
        if not win:
            # Diagonal /
            count = 1
            r, c = row - 1, col + 1
            while r >= 0 and c < columns and b2d[r][c] == player:
                count += 1
                r -= 1
                c += 1
            r, c = row + 1, col - 1
            while r < rows and c >= 0 and b2d[r][c] == player:
                count += 1
                r += 1
                c -= 1
            if count >= 4:
                win = True
        
        # Restore board
        b2d[row][col] = 0
        return win
    
    # Get valid columns
    valid = []
    for c in range(columns):
        if board[c] == 0:
            valid.append(c)
    
    if not valid:
        return 3
    
    # 1. Immediate win
    for col in valid:
        if is_win_move(board_2d, col, mark):
            return col
    
    # 2. Block immediate loss
    opponent = 3 - mark
    for col in valid:
        if is_win_move(board_2d, col, opponent):
            return col
    
    # 3. Minimax search with optimizations
    def evaluate(b2d):
        score = 0
        
        # Check each possible 4-window
        # Horizontal
        for r in range(rows):
            for c in range(columns - 3):
                window = [b2d[r][c+i] for i in range(4)]
                score += eval_window(window)
        
        # Vertical
        for c in range(columns):
            for r in range(rows - 3):
                window = [b2d[r+i][c] for i in range(4)]
                score += eval_window(window)
        
        # Diagonal \
        for r in range(rows - 3):
            for c in range(columns - 3):
                window = [b2d[r+i][c+i] for i in range(4)]
                score += eval_window(window)
        
        # Diagonal /
        for r in range(3, rows):
            for c in range(columns - 3):
                window = [b2d[r-i][c+i] for i in range(4)]
                score += eval_window(window)
        
        # Center preference
        center = 3
        center_count = 0
        for r in range(rows):
            if b2d[r][center] == mark:
                center_count += 1
        score += center_count * 6
        
        return score
    
    def eval_window(window):
        my_count = window.count(mark)
        opp_count = window.count(opponent)
        empty = window.count(0)
        
        if my_count == 3 and empty == 1:
            return 50
        elif my_count == 2 and empty == 2:
            return 10
        elif my_count == 1 and empty == 3:
            return 1
        
        if opp_count == 3 and empty == 1:
            return -50
        elif opp_count == 2 and empty == 2:
            return -10
        
        return 0
    
    def minimax(b2d, depth, alpha, beta, is_max, nodes_explored):
        # Quick evaluation at depth limit
        if depth == 0 or nodes_explored[0] > 10000:  # Node limit for speed
            return evaluate(b2d), None
        
        nodes_explored[0] += 1
        
        # Get valid moves with smart ordering
        moves = []
        for c in range(columns):
            if b2d[0][c] == 0:
                moves.append(c)
        
        if not moves:
            return 0, None
        
        # Order moves: center first, then killer moves
        center = 3
        moves.sort(key=lambda x: (abs(x - center), x not in agent.killer_moves.get(depth, [])))
        
        best_col = moves[0]
        
        if is_max:
            max_eval = -100000
            
            for col in moves:
                # Make move
                row = -1
                for r in range(rows-1, -1, -1):
                    if b2d[r][col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    b2d[row][col] = mark
                    
                    # Check for win
                    if is_win_move(b2d, col, mark):
                        b2d[row][col] = 0
                        return 10000 - (7 - depth), col
                    
                    val, _ = minimax(b2d, depth - 1, alpha, beta, False, nodes_explored)
                    
                    b2d[row][col] = 0
                    
                    if val > max_eval:
                        max_eval = val
                        best_col = col
                    
                    alpha = max(alpha, val)
                    if beta <= alpha:
                        # Killer move heuristic
                        if depth not in agent.killer_moves:
                            agent.killer_moves[depth] = []
                        if col not in agent.killer_moves[depth]:
                            agent.killer_moves[depth].append(col)
                            if len(agent.killer_moves[depth]) > 2:
                                agent.killer_moves[depth].pop(0)
                        break
            
            return max_eval, best_col
        else:
            min_eval = 100000
            
            for col in moves:
                # Make move
                row = -1
                for r in range(rows-1, -1, -1):
                    if b2d[r][col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    b2d[row][col] = opponent
                    
                    # Check for win
                    if is_win_move(b2d, col, opponent):
                        b2d[row][col] = 0
                        return -10000 + (7 - depth), col
                    
                    val, _ = minimax(b2d, depth - 1, alpha, beta, True, nodes_explored)
                    
                    b2d[row][col] = 0
                    
                    if val < min_eval:
                        min_eval = val
                        best_col = col
                    
                    beta = min(beta, val)
                    if beta <= alpha:
                        # Killer move heuristic
                        if depth not in agent.killer_moves:
                            agent.killer_moves[depth] = []
                        if col not in agent.killer_moves[depth]:
                            agent.killer_moves[depth].append(col)
                            if len(agent.killer_moves[depth]) > 2:
                                agent.killer_moves[depth].pop(0)
                        break
            
            return min_eval, best_col
    
    # Dynamic depth based on position complexity
    if move_count < 6:
        search_depth = 7
    elif move_count < 15:
        search_depth = 8
    else:
        search_depth = 9
    
    # Node counter for speed control
    nodes = [0]
    
    # Run minimax
    _, best_move = minimax(board_2d, search_depth, -100000, 100000, True, nodes)
    
    # Fallback to center if something goes wrong
    if best_move is None or board[best_move] != 0:
        for col in valid:
            if board[col] == 0:
                return col
        return 3
    
    return best_move
def agent(observation, configuration):
    """
    Optimized Deep Search Agent - Fast with smart pruning
    Balances search depth with speed for 1000+ score
    """
    import time
    
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    mark = observation.mark
    
    # Transposition table for caching
    transposition_table = {}
    
    # Convert flat board to 2D
    def to_2d():
        return [board[i*columns:(i+1)*columns] for i in range(rows)]
    
    # Make move on board copy
    def make_move(board_2d, col, player):
        new_board = [row[:] for row in board_2d]
        for row in range(rows-1, -1, -1):
            if new_board[row][col] == 0:
                new_board[row][col] = player
                return new_board
        return None
    
    # Fast win check using patterns
    def check_winner(board_2d):
        # Horizontal
        for r in range(rows):
            for c in range(columns-3):
                if board_2d[r][c] != 0 and all(board_2d[r][c] == board_2d[r][c+i] for i in range(4)):
                    return board_2d[r][c]
        
        # Vertical
        for c in range(columns):
            for r in range(rows-3):
                if board_2d[r][c] != 0 and all(board_2d[r][c] == board_2d[r+i][c] for i in range(4)):
                    return board_2d[r][c]
        
        # Diagonal \
        for r in range(rows-3):
            for c in range(columns-3):
                if board_2d[r][c] != 0 and all(board_2d[r][c] == board_2d[r+i][c+i] for i in range(4)):
                    return board_2d[r][c]
        
        # Diagonal /
        for r in range(3, rows):
            for c in range(columns-3):
                if board_2d[r][c] != 0 and all(board_2d[r][c] == board_2d[r-i][c+i] for i in range(4)):
                    return board_2d[r][c]
        
        return 0
    
    # Evaluate position
    def evaluate_position(board_2d, player):
        score = 0
        opponent = 3 - player
        
        # Check all 4-length windows
        def check_line(line):
            player_count = line.count(player)
            opponent_count = line.count(opponent)
            empty_count = line.count(0)
            
            if opponent_count == 0:
                if player_count == 3:
                    score = 50
                elif player_count == 2:
                    score = 10
                elif player_count == 1:
                    score = 1
                return score
            elif player_count == 0:
                if opponent_count == 3:
                    return -50
                elif opponent_count == 2:
                    return -10
                elif opponent_count == 1:
                    return -1
            return 0
        
        total_score = 0
        
        # Horizontal
        for r in range(rows):
            for c in range(columns-3):
                line = [board_2d[r][c+i] for i in range(4)]
                total_score += check_line(line)
        
        # Vertical
        for c in range(columns):
            for r in range(rows-3):
                line = [board_2d[r+i][c] for i in range(4)]
                total_score += check_line(line)
        
        # Diagonal \
        for r in range(rows-3):
            for c in range(columns-3):
                line = [board_2d[r+i][c+i] for i in range(4)]
                total_score += check_line(line)
        
        # Diagonal /
        for r in range(3, rows):
            for c in range(columns-3):
                line = [board_2d[r-i][c+i] for i in range(4)]
                total_score += check_line(line)
        
        # Center column preference
        center = columns // 2
        for r in range(rows):
            if board_2d[r][center] == player:
                total_score += 3
        
        return total_score
    
    # Minimax with alpha-beta pruning
    def minimax(board_2d, depth, alpha, beta, is_maximizing, start_time):
        # Time cutoff
        if time.time() - start_time > 0.8:
            return 0, None
        
        # Create board hash for transposition table
        board_tuple = tuple(tuple(row) for row in board_2d)
        if board_tuple in transposition_table and transposition_table[board_tuple][1] >= depth:
            return transposition_table[board_tuple][0], None
        
        # Check terminal states
        winner = check_winner(board_2d)
        if winner == mark:
            return 10000 - (10 - depth), None
        elif winner == (3 - mark):
            return -10000 + (10 - depth), None
        
        # Get valid moves
        valid_moves = [c for c in range(columns) if board_2d[0][c] == 0]
        if not valid_moves or depth == 0:
            return evaluate_position(board_2d, mark), None
        
        # Move ordering - center columns first
        center = columns // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        best_move = valid_moves[0]
        
        if is_maximizing:
            max_eval = -float('inf')
            
            # Killer move heuristic - check forcing moves first
            for move in valid_moves:
                test_board = make_move(board_2d, move, mark)
                if test_board and check_winner(test_board) == mark:
                    return 10000 - (10 - depth), move
            
            for move in valid_moves:
                new_board = make_move(board_2d, move, mark)
                if new_board:
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, False, start_time)
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = move
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            
            transposition_table[board_tuple] = (max_eval, depth)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            
            # Check opponent forcing moves
            for move in valid_moves:
                test_board = make_move(board_2d, move, 3-mark)
                if test_board and check_winner(test_board) == 3-mark:
                    return -10000 + (10 - depth), move
            
            for move in valid_moves:
                new_board = make_move(board_2d, move, 3-mark)
                if new_board:
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, start_time)
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = move
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            
            transposition_table[board_tuple] = (min_eval, depth)
            return min_eval, best_move
    
    # Main logic
    start_time = time.time()
    board_2d = to_2d()
    
    # Get valid moves
    valid_moves = [c for c in range(columns) if board[c] == 0]
    if not valid_moves:
        return columns // 2
    
    # Opening book
    move_count = sum(1 for x in board if x != 0)
    if move_count == 0:
        return columns // 2
    elif move_count == 1 and board[columns//2] == 0:
        return columns // 2
    
    # Check immediate wins
    for col in valid_moves:
        test_board = make_move(board_2d, col, mark)
        if test_board and check_winner(test_board) == mark:
            return col
    
    # Check immediate blocks
    for col in valid_moves:
        test_board = make_move(board_2d, col, 3-mark)
        if test_board and check_winner(test_board) == 3-mark:
            return col
    
    # Dynamic depth based on game phase and remaining time
    if move_count < 10:
        depth = 7  # Opening
    elif move_count < 20:
        depth = 8  # Midgame
    else:
        depth = 10  # Endgame
    
    # Iterative deepening for time management
    best_move = valid_moves[len(valid_moves)//2]
    for current_depth in range(3, depth+1):
        if time.time() - start_time > 0.7:
            break
        
        _, move = minimax(board_2d, current_depth, -float('inf'), float('inf'), True, start_time)
        if move is not None:
            best_move = move
        
        # If we found a winning move, use it
        if _ >= 9000:
            break
    
    return best_move
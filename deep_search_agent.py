def agent(observation, configuration):
    """
    Deep Search Connect X Agent - Targeting 1000+ Score
    Uses minimax with alpha-beta pruning and 8+ ply search
    """
    import time
    
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    mark = observation.mark
    
    # Constants
    SEARCH_DEPTH = 8  # 8-ply search depth
    WIN_SCORE = 10000
    LOSS_SCORE = -10000
    TIME_LIMIT = 0.95  # Use 95% of available time
    
    start_time = time.time()
    
    # Convert board to 2D for easier manipulation
    def to_2d_board():
        return [board[i*columns:(i+1)*columns] for i in range(rows)]
    
    # Check if a move is valid
    def is_valid_move(board_2d, col):
        return board_2d[0][col] == 0
    
    # Make a move on the board
    def make_move(board_2d, col, player):
        board_copy = [row[:] for row in board_2d]
        for row in range(rows-1, -1, -1):
            if board_copy[row][col] == 0:
                board_copy[row][col] = player
                break
        return board_copy
    
    # Check for win
    def check_win(board_2d, player):
        # Horizontal
        for row in range(rows):
            for col in range(columns-3):
                if all(board_2d[row][col+i] == player for i in range(4)):
                    return True
        
        # Vertical
        for col in range(columns):
            for row in range(rows-3):
                if all(board_2d[row+i][col] == player for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(rows-3):
            for col in range(columns-3):
                if all(board_2d[row+i][col+i] == player for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3, rows):
            for col in range(columns-3):
                if all(board_2d[row-i][col+i] == player for i in range(4)):
                    return True
        
        return False
    
    # Count patterns for evaluation
    def count_patterns(board_2d, player):
        score = 0
        
        # Check all 4-length windows
        # Horizontal
        for row in range(rows):
            for col in range(columns-3):
                window = [board_2d[row][col+i] for i in range(4)]
                score += evaluate_window(window, player)
        
        # Vertical
        for col in range(columns):
            for row in range(rows-3):
                window = [board_2d[row+i][col] for i in range(4)]
                score += evaluate_window(window, player)
        
        # Diagonal \
        for row in range(rows-3):
            for col in range(columns-3):
                window = [board_2d[row+i][col+i] for i in range(4)]
                score += evaluate_window(window, player)
        
        # Diagonal /
        for row in range(3, rows):
            for col in range(columns-3):
                window = [board_2d[row-i][col+i] for i in range(4)]
                score += evaluate_window(window, player)
        
        return score
    
    # Evaluate a 4-piece window
    def evaluate_window(window, player):
        opponent = 3 - player
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)
        
        # Can't win if opponent has pieces
        if opponent_count > 0:
            return 0
        
        # Score based on number of pieces
        if player_count == 3 and empty_count == 1:
            return 50
        elif player_count == 2 and empty_count == 2:
            return 10
        elif player_count == 1 and empty_count == 3:
            return 1
        
        return 0
    
    # Position evaluation function
    def evaluate_position(board_2d, player):
        opponent = 3 - player
        
        # Check for wins
        if check_win(board_2d, player):
            return WIN_SCORE
        if check_win(board_2d, opponent):
            return LOSS_SCORE
        
        score = 0
        
        # Pattern-based evaluation
        score += count_patterns(board_2d, player)
        score -= count_patterns(board_2d, opponent)
        
        # Center column preference
        center_col = columns // 2
        for row in range(rows):
            if board_2d[row][center_col] == player:
                score += 3
            elif board_2d[row][center_col] == opponent:
                score -= 3
        
        return score
    
    # Minimax with alpha-beta pruning
    def minimax(board_2d, depth, alpha, beta, maximizing_player, player):
        # Check time limit
        if time.time() - start_time > TIME_LIMIT:
            return evaluate_position(board_2d, mark)
        
        # Terminal node or depth limit
        if depth == 0 or check_win(board_2d, player) or check_win(board_2d, 3-player):
            return evaluate_position(board_2d, mark)
        
        # Get valid moves
        valid_moves = [col for col in range(columns) if is_valid_move(board_2d, col)]
        if not valid_moves:
            return 0  # Draw
        
        # Order moves - center first
        center = columns // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        if maximizing_player:
            max_eval = -float('inf')
            for col in valid_moves:
                new_board = make_move(board_2d, col, player)
                eval_score = minimax(new_board, depth-1, alpha, beta, False, 3-player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                new_board = make_move(board_2d, col, player)
                eval_score = minimax(new_board, depth-1, alpha, beta, True, 3-player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    # Convert to 2D board
    board_2d = to_2d_board()
    
    # Get valid moves
    valid_moves = [col for col in range(columns) if is_valid_move(board_2d, col)]
    if not valid_moves:
        return columns // 2
    
    # Check for immediate wins
    for col in valid_moves:
        test_board = make_move(board_2d, col, mark)
        if check_win(test_board, mark):
            return col
    
    # Check for immediate blocks
    opponent = 3 - mark
    for col in valid_moves:
        test_board = make_move(board_2d, col, opponent)
        if check_win(test_board, opponent):
            return col
    
    # Use minimax for best move
    best_move = valid_moves[0]
    best_score = -float('inf')
    
    # Order moves - center first for better pruning
    center = columns // 2
    valid_moves.sort(key=lambda x: abs(x - center))
    
    # Adaptive depth based on game phase
    move_count = sum(1 for x in board if x != 0)
    if move_count < 8:
        search_depth = min(10, SEARCH_DEPTH + 2)  # Deeper in opening
    elif move_count > 30:
        search_depth = min(12, SEARCH_DEPTH + 4)  # Deeper in endgame
    else:
        search_depth = SEARCH_DEPTH
    
    # Search each move
    for col in valid_moves:
        new_board = make_move(board_2d, col, mark)
        score = minimax(new_board, search_depth-1, -float('inf'), float('inf'), False, opponent)
        
        if score > best_score:
            best_score = score
            best_move = col
        
        # Early exit if winning move found
        if score >= WIN_SCORE - 100:
            break
    
    return best_move
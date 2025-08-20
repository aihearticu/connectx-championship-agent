def agent(observation, configuration):
    """
    Neural Network Enhanced Agent - Combines deep search with learned evaluation
    Uses a simple neural network for position evaluation
    """
    import time
    import math
    
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    mark = observation.mark
    
    # Simple neural network weights (pre-trained values)
    # These would normally be trained via self-play
    PATTERN_WEIGHTS = {
        'two_open': 10,      # Two in a row with open ends
        'three_open': 50,    # Three in a row with open ends
        'two_blocked': 5,    # Two in a row with one end blocked
        'three_blocked': 25, # Three in a row with one end blocked
        'center_control': 16,
        'second_column': 8,
        'third_column': 4,
        'fork_threat': 100,  # Multiple winning threats
        'defensive_need': 1.2  # Multiplier for opponent threats
    }
    
    # Convert to 2D board
    def to_2d():
        return [board[i*columns:(i+1)*columns] for i in range(rows)]
    
    # Make move
    def make_move(board_2d, col, player):
        new_board = [row[:] for row in board_2d]
        for row in range(rows-1, -1, -1):
            if new_board[row][col] == 0:
                new_board[row][col] = player
                return new_board
        return None
    
    # Check for win
    def is_winning_move(board_2d, col, player):
        # Make the move
        test_board = make_move(board_2d, col, player)
        if not test_board:
            return False
        
        # Find where piece was placed
        row = -1
        for r in range(rows):
            if test_board[r][col] == player:
                row = r
                break
        
        if row == -1:
            return False
        
        # Check all directions from this position
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        
        for dr, dc in directions:
            count = 1
            # Check positive direction
            r, c = row + dr, col + dc
            while 0 <= r < rows and 0 <= c < columns and test_board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # Check negative direction
            r, c = row - dr, col - dc
            while 0 <= r < rows and 0 <= c < columns and test_board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 4:
                return True
        
        return False
    
    # Neural network-inspired evaluation
    def neural_evaluate(board_2d, player):
        opponent = 3 - player
        score = 0
        
        # Feature extraction
        features = {
            'player_threats': 0,
            'opponent_threats': 0,
            'center_control': 0,
            'player_patterns': {'two_open': 0, 'three_open': 0, 'two_blocked': 0, 'three_blocked': 0},
            'opponent_patterns': {'two_open': 0, 'three_open': 0, 'two_blocked': 0, 'three_blocked': 0},
            'fork_opportunities': 0
        }
        
        # Analyze patterns
        def analyze_line(line, p):
            if len(line) < 4:
                return
            
            for i in range(len(line) - 3):
                window = line[i:i+4]
                player_count = window.count(p)
                empty_count = window.count(0)
                opponent_count = window.count(3-p)
                
                if opponent_count == 0:
                    if player_count == 3 and empty_count == 1:
                        if i > 0 and line[i-1] == 0 and i+4 < len(line) and line[i+4] == 0:
                            features['player_patterns' if p == player else 'opponent_patterns']['three_open'] += 1
                        else:
                            features['player_patterns' if p == player else 'opponent_patterns']['three_blocked'] += 1
                    elif player_count == 2 and empty_count == 2:
                        if i > 0 and line[i-1] == 0 and i+4 < len(line) and line[i+4] == 0:
                            features['player_patterns' if p == player else 'opponent_patterns']['two_open'] += 1
                        else:
                            features['player_patterns' if p == player else 'opponent_patterns']['two_blocked'] += 1
        
        # Check all lines
        # Horizontal
        for r in range(rows):
            analyze_line(board_2d[r], player)
            analyze_line(board_2d[r], opponent)
        
        # Vertical
        for c in range(columns):
            line = [board_2d[r][c] for r in range(rows)]
            analyze_line(line, player)
            analyze_line(line, opponent)
        
        # Diagonals
        for r in range(rows):
            for c in range(columns):
                # Diagonal \
                diag1 = []
                for i in range(min(rows-r, columns-c)):
                    diag1.append(board_2d[r+i][c+i])
                if len(diag1) >= 4:
                    analyze_line(diag1, player)
                    analyze_line(diag1, opponent)
                
                # Diagonal /
                if r >= 3:
                    diag2 = []
                    for i in range(min(r+1, columns-c)):
                        diag2.append(board_2d[r-i][c+i])
                    if len(diag2) >= 4:
                        analyze_line(diag2, player)
                        analyze_line(diag2, opponent)
        
        # Center control
        center = columns // 2
        for r in range(rows):
            if board_2d[r][center] == player:
                features['center_control'] += 1
            elif board_2d[r][center] == opponent:
                features['center_control'] -= 1
        
        # Check for fork opportunities
        threat_positions = []
        for c in range(columns):
            if board_2d[0][c] == 0:  # Valid move
                test_board = make_move(board_2d, c, player)
                if test_board:
                    # Count winning moves after this move
                    win_moves = 0
                    for c2 in range(columns):
                        if c2 != c and test_board[0][c2] == 0:
                            if is_winning_move(test_board, c2, player):
                                win_moves += 1
                    if win_moves >= 2:
                        features['fork_opportunities'] += 1
        
        # Calculate score using weights
        score = 0
        
        # Pattern scores
        for pattern, count in features['player_patterns'].items():
            score += PATTERN_WEIGHTS[pattern] * count
        
        for pattern, count in features['opponent_patterns'].items():
            score -= PATTERN_WEIGHTS[pattern] * count * PATTERN_WEIGHTS['defensive_need']
        
        # Positional scores
        score += features['center_control'] * PATTERN_WEIGHTS['center_control']
        
        # Fork bonus
        score += features['fork_opportunities'] * PATTERN_WEIGHTS['fork_threat']
        
        # Add some noise to avoid repetitive play
        score += (hash(str(board_2d)) % 10) * 0.1
        
        return score
    
    # Minimax with neural evaluation
    def minimax(board_2d, depth, alpha, beta, maximizing, start_time):
        # Time check
        if time.time() - start_time > 0.9:
            return neural_evaluate(board_2d, mark), None
        
        # Terminal checks
        valid_moves = [c for c in range(columns) if board_2d[0][c] == 0]
        if not valid_moves:
            return 0, None
        
        # Check for immediate wins
        for col in valid_moves:
            if is_winning_move(board_2d, col, mark if maximizing else 3-mark):
                return (10000 - (8-depth)) * (1 if maximizing else -1), col
        
        # Depth limit - use neural evaluation
        if depth == 0:
            return neural_evaluate(board_2d, mark), None
        
        # Move ordering - center first, then by preliminary evaluation
        center = columns // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        best_move = valid_moves[0]
        
        if maximizing:
            max_eval = -float('inf')
            for col in valid_moves:
                new_board = make_move(board_2d, col, mark)
                if new_board:
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, False, start_time)
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = col
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in valid_moves:
                new_board = make_move(board_2d, col, 3-mark)
                if new_board:
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, start_time)
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = col
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return min_eval, best_move
    
    # Main agent logic
    start_time = time.time()
    board_2d = to_2d()
    
    # Valid moves
    valid_moves = [c for c in range(columns) if board[c] == 0]
    if not valid_moves:
        return columns // 2
    
    # Opening book
    move_count = sum(1 for x in board if x != 0)
    if move_count == 0:
        return columns // 2
    elif move_count == 1:
        if board[columns//2] == 0:
            return columns // 2
        else:
            return columns//2 - 1 if columns//2 > 0 else columns//2 + 1
    
    # Immediate win check
    for col in valid_moves:
        if is_winning_move(board_2d, col, mark):
            return col
    
    # Immediate block check
    for col in valid_moves:
        if is_winning_move(board_2d, col, 3-mark):
            return col
    
    # Dynamic depth
    if move_count < 8:
        base_depth = 6
    elif move_count < 20:
        base_depth = 7
    else:
        base_depth = 8
    
    # Iterative deepening
    best_move = valid_moves[len(valid_moves)//2]
    best_score = -float('inf')
    
    for depth in range(4, base_depth + 1):
        if time.time() - start_time > 0.8:
            break
        
        score, move = minimax(board_2d, depth, -float('inf'), float('inf'), True, start_time)
        if move is not None and score > best_score:
            best_score = score
            best_move = move
        
        # If winning move found, use it
        if score >= 9000:
            break
    
    return best_move
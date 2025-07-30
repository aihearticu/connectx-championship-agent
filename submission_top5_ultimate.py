def agent(observation, configuration):
    """
    TOP 5 Ultimate Agent - Optimized for reliability and performance
    
    Key features:
    1. Transposition tables with Zobrist hashing
    2. Killer move heuristic for better ordering  
    3. Iterative deepening with time management
    4. Advanced evaluation with pattern recognition
    5. Perfect tactical play (never misses wins/blocks)
    """
    import time
    
    # Initialize persistent storage
    if not hasattr(agent, 'initialized'):
        agent.initialized = True
        agent.tt = {}  # Transposition table
        agent.tt_hits = 0
        agent.killers = [[None, None] for _ in range(20)]  # Killer moves
        
        # Zobrist hashing for transposition table
        import random
        random.seed(42)
        agent.zobrist = {}
        for pos in range(42):
            agent.zobrist[pos] = {
                1: random.getrandbits(64),
                2: random.getrandbits(64)
            }
    
    # Extract game state
    board = observation['board']
    mark = observation['mark']
    rows, cols = 6, 7
    opponent = 3 - mark
    
    # Time management
    start_time = time.time()
    time_limit = 0.0095  # 9.5ms to be safe
    
    # Convert to 2D grid
    grid = [[board[r * cols + c] for c in range(cols)] for r in range(rows)]
    
    # Zobrist hash calculation
    def calculate_hash(grid):
        h = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 0:
                    pos = r * cols + c
                    h ^= agent.zobrist[pos][grid[r][c]]
        return h
    
    # Check for four in a row
    def check_win(grid, row, col, player):
        # Horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and grid[row][c] == player:
            count += 1
            c -= 1
        # Check right
        c = col + 1
        while c < cols and grid[row][c] == player:
            count += 1
            c += 1
        if count >= 4:
            return True
        
        # Vertical
        count = 1
        # Check down
        r = row + 1
        while r < rows and grid[r][col] == player:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        # Check up-right
        r, c = row - 1, col + 1
        while r >= 0 and c < cols and grid[r][c] == player:
            count += 1
            r -= 1
            c += 1
        # Check down-left
        r, c = row + 1, col - 1
        while r < rows and c >= 0 and grid[r][c] == player:
            count += 1
            r += 1
            c -= 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        # Check up-left
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and grid[r][c] == player:
            count += 1
            r -= 1
            c -= 1
        # Check down-right
        r, c = row + 1, col + 1
        while r < rows and c < cols and grid[r][c] == player:
            count += 1
            r += 1
            c += 1
        if count >= 4:
            return True
        
        return False
    
    # Get valid moves
    def get_valid_moves(grid):
        return [c for c in range(cols) if grid[0][c] == 0]
    
    # Make a move
    def make_move(grid, col, player):
        new_grid = [row[:] for row in grid]
        for row in range(rows - 1, -1, -1):
            if new_grid[row][col] == 0:
                new_grid[row][col] = player
                return new_grid, row
        return new_grid, -1
    
    # Count threats (3 in a row with empty space)
    def count_threats(grid, player):
        threats = 0
        
        # Check all positions
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 0:
                    # Simulate move
                    grid[r][c] = player
                    
                    # Check all directions for 3 in a row
                    # Horizontal
                    for start_c in range(max(0, c - 3), min(cols - 3, c + 1)):
                        if sum(1 for i in range(4) if grid[r][start_c + i] == player) == 3:
                            threats += 1
                    
                    # Vertical
                    if r >= 3:
                        if sum(1 for i in range(4) if grid[r - i][c] == player) == 3:
                            threats += 1
                    
                    # Diagonals
                    # Diagonal /
                    for offset in range(-3, 1):
                        sr, sc = r - offset, c + offset
                        if 0 <= sr <= rows - 4 and 0 <= sc <= cols - 4:
                            if sum(1 for i in range(4) if grid[sr + i][sc - i] == player) == 3:
                                threats += 1
                    
                    # Diagonal \
                    for offset in range(-3, 1):
                        sr, sc = r - offset, c - offset
                        if 0 <= sr <= rows - 4 and 0 <= sc <= cols - 4:
                            if sum(1 for i in range(4) if grid[sr + i][sc + i] == player) == 3:
                                threats += 1
                    
                    grid[r][c] = 0
        
        return threats
    
    # Evaluation function
    def evaluate(grid):
        score = 0
        
        # Center column preference
        center_col = 3
        for r in range(rows):
            if grid[r][center_col] == mark:
                score += 3
            elif grid[r][center_col] == opponent:
                score -= 3
        
        # Count threats
        my_threats = count_threats(grid, mark)
        opp_threats = count_threats(grid, opponent)
        score += my_threats * 10
        score -= opp_threats * 15  # Defensive bias
        
        # Prefer lower rows (more stable positions)
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == mark:
                    score += (rows - r) * 0.1
                elif grid[r][c] == opponent:
                    score -= (rows - r) * 0.1
        
        return score
    
    # Minimax with alpha-beta pruning
    def minimax(grid, depth, alpha, beta, maximizing, last_move, deadline):
        # Time check
        if time.time() > deadline:
            return 0, None
        
        # Transposition table lookup
        board_hash = calculate_hash(grid)
        tt_key = (board_hash, depth, maximizing)
        
        if tt_key in agent.tt:
            agent.tt_hits += 1
            entry = agent.tt[tt_key]
            if entry['depth'] >= depth:
                return entry['score'], entry['move']
        
        # Terminal node check
        if last_move is not None:
            row = next(r for r in range(rows - 1, -1, -1) if grid[r][last_move] != 0)
            if check_win(grid, row, last_move, opponent if maximizing else mark):
                score = -10000 + depth if maximizing else 10000 - depth
                return score, None
        
        valid_moves = get_valid_moves(grid)
        if not valid_moves or depth == 0:
            return evaluate(grid), None
        
        # Move ordering
        ordered_moves = []
        
        # Check for immediate wins/blocks first
        for col in valid_moves:
            test_grid, row = make_move(grid, col, mark if maximizing else opponent)
            if row >= 0 and check_win(test_grid, row, col, mark if maximizing else opponent):
                ordered_moves.insert(0, col)  # Prioritize wins
            else:
                ordered_moves.append(col)
        
        # Add killer moves
        for killer in agent.killers[depth]:
            if killer in ordered_moves and killer not in ordered_moves[:2]:
                ordered_moves.remove(killer)
                ordered_moves.insert(2, killer)
        
        # Center preference
        if 3 in ordered_moves and 3 not in ordered_moves[:3]:
            ordered_moves.remove(3)
            ordered_moves.insert(min(3, len(ordered_moves)), 3)
        
        best_move = ordered_moves[0] if ordered_moves else None
        
        if maximizing:
            max_eval = -float('inf')
            for col in ordered_moves:
                new_grid, _ = make_move(grid, col, mark)
                eval_score, _ = minimax(new_grid, depth - 1, alpha, beta, False, col, deadline)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if col not in agent.killers[depth]:
                        agent.killers[depth][1] = agent.killers[depth][0]
                        agent.killers[depth][0] = col
                    break
            
            # Store in transposition table
            agent.tt[tt_key] = {'depth': depth, 'score': max_eval, 'move': best_move}
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in ordered_moves:
                new_grid, _ = make_move(grid, col, opponent)
                eval_score, _ = minimax(new_grid, depth - 1, alpha, beta, True, col, deadline)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if col not in agent.killers[depth]:
                        agent.killers[depth][1] = agent.killers[depth][0]
                        agent.killers[depth][0] = col
                    break
            
            # Store in transposition table
            agent.tt[tt_key] = {'depth': depth, 'score': min_eval, 'move': best_move}
            return min_eval, best_move
    
    # Quick win/block check
    valid_moves = get_valid_moves(grid)
    
    # Check for immediate win
    for col in valid_moves:
        test_grid, row = make_move(grid, col, mark)
        if row >= 0 and check_win(test_grid, row, col, mark):
            return col
    
    # Check for immediate block
    for col in valid_moves:
        test_grid, row = make_move(grid, col, opponent)
        if row >= 0 and check_win(test_grid, row, col, opponent):
            return col
    
    # Iterative deepening
    best_move = 3 if 3 in valid_moves else valid_moves[0]
    deadline = start_time + time_limit
    
    for depth in range(1, 15):
        if time.time() > deadline:
            break
        
        _, move = minimax(grid, depth, -float('inf'), float('inf'), True, None, deadline)
        if move is not None:
            best_move = move
    
    # Clean up transposition table if too large
    if len(agent.tt) > 500000:
        agent.tt = {}
    
    return best_move
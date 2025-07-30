def agent(observation, configuration):
    """
    TOP 5 Agent - Bitboards + Transposition Tables + Killer Moves + Iterative Deepening
    
    Key optimizations:
    1. Bitboard representation (100x faster)
    2. Transposition table with Zobrist hashing
    3. Killer move heuristic
    4. Iterative deepening with time management
    5. Advanced move ordering
    """
    import time
    
    # Constants
    ROWS, COLS = 6, 7
    FOUR = 4
    MAX_DEPTH = 10
    TIME_LIMIT = 0.008  # 8ms safety margin
    
    # Transposition table
    if not hasattr(agent, 'tt'):
        agent.tt = {}
        agent.killers = [[None, None] for _ in range(MAX_DEPTH)]
        # Simple Zobrist hashing
        import random
        random.seed(42)
        agent.zobrist = [[random.getrandbits(64) for _ in range(3)] for _ in range(42)]
    
    board = observation['board']
    mark = observation['mark']
    start_time = time.time()
    
    # Convert to bitboards
    def board_to_bitboards(board, mark):
        p1_board = 0
        p2_board = 0
        heights = [0] * COLS
        
        for col in range(COLS):
            for row in range(ROWS):
                idx = row * COLS + col
                if board[idx] != 0:
                    pos = col * 7 + row
                    if board[idx] == mark:
                        p1_board |= (1 << pos)
                    else:
                        p2_board |= (1 << pos)
                    heights[col] = row + 1
        
        return p1_board, p2_board, heights
    
    # Check win using bitboards (super fast)
    def check_win_bitboard(bitboard):
        # Horizontal
        m = bitboard & (bitboard >> 7)
        if m & (m >> 14): return True
        
        # Vertical
        m = bitboard & (bitboard >> 1)
        if m & (m >> 2): return True
        
        # Diagonal \
        m = bitboard & (bitboard >> 8)
        if m & (m >> 16): return True
        
        # Diagonal /
        m = bitboard & (bitboard >> 6)
        if m & (m >> 12): return True
        
        return False
    
    # Make move on bitboard
    def make_move_bitboard(bitboard, heights, col):
        pos = col * 7 + heights[col]
        new_board = bitboard | (1 << pos)
        new_heights = heights[:]
        new_heights[col] += 1
        return new_board, new_heights
    
    # Get valid moves
    def get_valid_moves(heights):
        return [col for col in range(COLS) if heights[col] < ROWS]
    
    # Zobrist hash
    def get_hash(p1_board, p2_board):
        h = 0
        for pos in range(42):
            if p1_board & (1 << pos):
                h ^= agent.zobrist[pos][1]
            elif p2_board & (1 << pos):
                h ^= agent.zobrist[pos][2]
        return h
    
    # Evaluate position
    def evaluate(p1_board, p2_board, heights):
        if check_win_bitboard(p1_board): return 10000
        if check_win_bitboard(p2_board): return -10000
        
        score = 0
        
        # Center column preference
        for row in range(ROWS):
            pos = 3 * 7 + row  # Center column
            if p1_board & (1 << pos): score += 3
            elif p2_board & (1 << pos): score -= 3
        
        # Count threats (simplified for speed)
        for col in range(COLS):
            if heights[col] < ROWS:
                # Check if move creates win
                test_board, _ = make_move_bitboard(p1_board, heights, col)
                if check_win_bitboard(test_board): score += 50
                
                test_board, _ = make_move_bitboard(p2_board, heights, col)
                if check_win_bitboard(test_board): score -= 50
        
        return score
    
    # Minimax with alpha-beta, transposition table, and killer moves
    def minimax(p1_board, p2_board, heights, depth, alpha, beta, maximizing, deadline):
        # Time check
        if time.time() > deadline:
            return evaluate(p1_board, p2_board, heights), None
        
        # Transposition table lookup
        board_hash = get_hash(p1_board, p2_board)
        if board_hash in agent.tt:
            entry = agent.tt[board_hash]
            if entry['depth'] >= depth:
                return entry['score'], entry['move']
        
        # Terminal node check
        if check_win_bitboard(p1_board):
            return 10000 - (MAX_DEPTH - depth), None
        if check_win_bitboard(p2_board):
            return -10000 + (MAX_DEPTH - depth), None
        
        valid_moves = get_valid_moves(heights)
        if not valid_moves or depth == 0:
            return evaluate(p1_board, p2_board, heights), None
        
        # Move ordering: center first, then killer moves
        ordered_moves = []
        if 3 in valid_moves:
            ordered_moves.append(3)
            valid_moves.remove(3)
        
        # Add killer moves
        for killer in agent.killers[depth]:
            if killer in valid_moves:
                ordered_moves.append(killer)
                valid_moves.remove(killer)
        
        # Add remaining moves
        ordered_moves.extend(valid_moves)
        
        best_move = ordered_moves[0]
        
        if maximizing:
            max_eval = -float('inf')
            for col in ordered_moves:
                new_p1, new_heights = make_move_bitboard(p1_board, heights, col)
                eval_score, _ = minimax(new_p1, p2_board, new_heights, depth - 1, alpha, beta, False, deadline)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if agent.killers[depth][0] != col:
                        agent.killers[depth][1] = agent.killers[depth][0]
                        agent.killers[depth][0] = col
                    break
            
            # Store in transposition table
            agent.tt[board_hash] = {'depth': depth, 'score': max_eval, 'move': best_move}
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in ordered_moves:
                new_p2, new_heights = make_move_bitboard(p2_board, heights, col)
                eval_score, _ = minimax(p1_board, new_p2, new_heights, depth - 1, alpha, beta, True, deadline)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if agent.killers[depth][0] != col:
                        agent.killers[depth][1] = agent.killers[depth][0]
                        agent.killers[depth][0] = col
                    break
            
            # Store in transposition table
            agent.tt[board_hash] = {'depth': depth, 'score': min_eval, 'move': best_move}
            return min_eval, best_move
    
    # Convert board and get initial state
    p1_board, p2_board, heights = board_to_bitboards(board, mark)
    
    # Quick win/block check
    valid_moves = get_valid_moves(heights)
    
    # Immediate win check
    for col in valid_moves:
        test_board, _ = make_move_bitboard(p1_board, heights, col)
        if check_win_bitboard(test_board):
            return col
    
    # Immediate block check
    for col in valid_moves:
        test_board, _ = make_move_bitboard(p2_board, heights, col)
        if check_win_bitboard(test_board):
            return col
    
    # Iterative deepening
    deadline = start_time + TIME_LIMIT
    best_move = 3 if 3 in valid_moves else valid_moves[0]
    
    for depth in range(1, MAX_DEPTH):
        if time.time() > deadline:
            break
        
        _, move = minimax(p1_board, p2_board, heights, depth, -float('inf'), float('inf'), True, deadline)
        if move is not None:
            best_move = move
    
    # Clean up old transposition table entries periodically
    if len(agent.tt) > 1000000:
        agent.tt = {}
    
    return best_move
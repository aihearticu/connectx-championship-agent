def agent(observation, configuration):
    """
    Bitboard-based Connect X Agent - Ultra-fast with deep search
    Uses bit manipulation for 100x speedup, targeting 1000+ score
    """
    import time
    
    # Constants
    ROWS = configuration.rows
    COLS = configuration.columns
    SEARCH_DEPTH = 10  # Can go deeper with bitboards
    
    # Bitboard constants
    HEIGHT = ROWS + 1  # Extra row for overflow detection
    H1 = HEIGHT + 1
    H2 = HEIGHT + 2
    SIZE = HEIGHT * COLS
    SIZE1 = H1 * COLS
    ALL1 = (1 << SIZE1) - 1
    COL1 = (1 << H1) - 1
    BOTTOM = ALL1 // COL1
    TOP = BOTTOM << HEIGHT
    
    # Cache for transposition table
    cache = {}
    
    # Convert observation board to bitboards
    def board_to_bitboards(board):
        position = 0
        mask = 0
        
        for col in range(COLS):
            for row in range(ROWS-1, -1, -1):
                cell = board[row * COLS + col]
                if cell != 0:
                    mask |= 1 << (col * H1 + (ROWS - 1 - row))
                    if cell == observation.mark:
                        position |= 1 << (col * H1 + (ROWS - 1 - row))
        
        return position, mask
    
    # Make a move
    def make_move(position, mask, col):
        new_mask = mask | (mask + (1 << (col * H1)))
        new_position = position ^ new_mask
        return new_position, new_mask
    
    # Check if current player can win
    def is_win(position):
        # Horizontal
        m = position & (position >> H1)
        if m & (m >> 2 * H1):
            return True
        
        # Diagonal \
        m = position & (position >> HEIGHT)
        if m & (m >> 2 * HEIGHT):
            return True
        
        # Diagonal /
        m = position & (position >> H2)
        if m & (m >> 2 * H2):
            return True
        
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2):
            return True
        
        return False
    
    # Check if a column is playable
    def can_play(mask, col):
        return (mask & TOP) & (1 << (col * H1 + HEIGHT - 1)) == 0
    
    # Get list of valid moves
    def get_valid_moves(mask):
        moves = []
        for col in range(COLS):
            if can_play(mask, col):
                moves.append(col)
        return moves
    
    # Count winning moves
    def count_winning_moves(position, mask):
        count = 0
        for col in range(COLS):
            if can_play(mask, col):
                pos2, mask2 = make_move(position, mask, col)
                if is_win(pos2):
                    count += 1
        return count
    
    # Advanced evaluation function
    def evaluate(position, mask, player_position):
        opponent_position = position ^ mask
        
        # Check immediate wins
        if is_win(position):
            return 10000
        if is_win(opponent_position):
            return -10000
        
        score = 0
        
        # Count threats (positions that lead to wins)
        player_threats = count_winning_moves(position, mask)
        opponent_threats = count_winning_moves(opponent_position, mask)
        
        score += player_threats * 100
        score -= opponent_threats * 120  # Defensive bias
        
        # Center column control
        center = COLS // 2
        center_mask = COL1 << (center * H1)
        score += bin(position & center_mask).count('1') * 10
        score -= bin(opponent_position & center_mask).count('1') * 10
        
        # Adjacent to center columns
        for offset in [1, -1]:
            if 0 <= center + offset < COLS:
                col_mask = COL1 << ((center + offset) * H1)
                score += bin(position & col_mask).count('1') * 5
                score -= bin(opponent_position & col_mask).count('1') * 5
        
        return score
    
    # Negamax with alpha-beta pruning
    def negamax(position, mask, depth, alpha, beta, start_time):
        # Time check
        if time.time() - start_time > 0.9:
            return 0
        
        # Transposition table lookup
        key = position ^ mask
        if key in cache and cache[key][1] >= depth:
            return cache[key][0]
        
        # Check for draw
        if mask == BOTTOM * ((1 << COLS) - 1):
            return 0
        
        # Can we win next move?
        for col in range(COLS):
            if can_play(mask, col):
                pos2, mask2 = make_move(position, mask, col)
                if is_win(pos2):
                    score = (SIZE1 - bin(mask).count('1')) // 2
                    cache[key] = (score, depth)
                    return score
        
        # Terminal depth
        if depth == 0:
            return 0  # Draw score at depth limit
        
        # Null window search
        max_score = (SIZE1 - bin(mask).count('1') - 2) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta
        
        # Try all moves
        best_score = -SIZE1
        moves = get_valid_moves(mask)
        
        # Move ordering - try center columns first
        center = COLS // 2
        moves.sort(key=lambda x: abs(x - center))
        
        # Check opponent threats first
        opponent_position = position ^ mask
        for col in moves[:]:
            if can_play(mask, col):
                opp_pos, opp_mask = make_move(opponent_position, mask, col)
                if is_win(opp_pos):
                    # Must block this move - try it first
                    moves.remove(col)
                    moves.insert(0, col)
        
        for col in moves:
            pos2, mask2 = make_move(position, mask, col)
            score = -negamax(pos2, mask2, depth - 1, -beta, -alpha, start_time)
            
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        
        # Store in transposition table
        cache[key] = (best_score, depth)
        return best_score
    
    # Main agent logic
    start_time = time.time()
    
    # Convert board to bitboards
    position, mask = board_to_bitboards(observation.board)
    
    # Get valid moves
    valid_moves = get_valid_moves(mask)
    if not valid_moves:
        return COLS // 2
    
    # Opening book for first few moves
    move_count = bin(mask).count('1')
    if move_count == 0:
        return COLS // 2  # Always start center
    elif move_count == 1:
        # Second move - take center if available, else adjacent
        if can_play(mask, COLS // 2):
            return COLS // 2
        return (COLS // 2) + 1 if can_play(mask, (COLS // 2) + 1) else (COLS // 2) - 1
    
    # Check for immediate wins
    for col in valid_moves:
        pos2, mask2 = make_move(position, mask, col)
        if is_win(pos2):
            return col
    
    # Check for immediate blocks
    opponent_position = position ^ mask
    for col in valid_moves:
        opp_pos, opp_mask = make_move(opponent_position, mask, col)
        if is_win(opp_pos):
            return col
    
    # Use negamax for best move
    best_move = valid_moves[0]
    best_score = -float('inf')
    
    # Adaptive depth
    if move_count < 10:
        depth = min(12, SEARCH_DEPTH + 2)
    elif move_count > 30:
        depth = min(14, SEARCH_DEPTH + 4)
    else:
        depth = SEARCH_DEPTH
    
    # Order moves for better pruning
    center = COLS // 2
    valid_moves.sort(key=lambda x: abs(x - center))
    
    # Clear old cache entries if too large
    if len(cache) > 1000000:
        cache.clear()
    
    # Search each move
    alpha = -float('inf')
    beta = float('inf')
    
    for col in valid_moves:
        pos2, mask2 = make_move(position, mask, col)
        score = -negamax(pos2, mask2, depth - 1, -beta, -alpha, start_time)
        
        if score > best_score:
            best_score = score
            best_move = col
        
        alpha = max(alpha, score)
        
        # Time check
        if time.time() - start_time > 0.95:
            break
    
    return best_move
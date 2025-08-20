"""
Bitboard-based Connect 4 Engine
Ultra-fast implementation using bit manipulation for top-tier performance
"""

class BitboardEngine:
    def __init__(self, rows=6, columns=7):
        self.rows = rows
        self.columns = columns
        self.height = rows + 1  # Extra row for sentinel
        self.size = self.height * self.columns
        self.mask_bottom = (1 << self.columns) - 1
        
        # Precomputed masks for win detection
        self.directions = [1, self.height - 1, self.height, self.height + 1]
        
        # Zobrist hashing for transposition table
        import random
        random.seed(42)
        self.zobrist_keys = {}
        for pos in range(self.size):
            for player in [1, 2]:
                self.zobrist_keys[(pos, player)] = random.getrandbits(64)
        
        # Transposition table
        self.transposition_table = {}
        
        # Column order for alpha-beta (center first)
        self.column_order = sorted(range(columns), key=lambda x: abs(x - columns // 2))
    
    def encode_position(self, board, player):
        """Convert board to bitboard representation"""
        position = 0
        mask = 0
        
        for col in range(self.columns):
            for row in range(self.rows):
                idx = row * self.columns + col
                if board[idx] != 0:
                    pos = col * self.height + (self.rows - 1 - row)
                    mask |= 1 << pos
                    if board[idx] == player:
                        position |= 1 << pos
        
        return position, mask
    
    def can_win_next(self, position, mask):
        """Check if current player can win on next move"""
        # Test all possible moves
        for col in range(self.columns):
            if self.can_play(mask, col):
                test_pos = position | self.top_mask(mask, col)
                if self.is_winning_position(test_pos):
                    return True
        return False
    
    def is_winning_position(self, position):
        """Ultra-fast win detection using bit manipulation"""
        # Horizontal
        m = position & (position >> self.height)
        if m & (m >> 2 * self.height):
            return True
        
        # Diagonal \
        m = position & (position >> (self.height - 1))
        if m & (m >> 2 * (self.height - 1)):
            return True
        
        # Diagonal /
        m = position & (position >> (self.height + 1))
        if m & (m >> 2 * (self.height + 1)):
            return True
        
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2):
            return True
        
        return False
    
    def top_mask(self, mask, col):
        """Get the bitmask of the top cell of a column"""
        return 1 << ((mask >> (col * self.height)) & ((1 << self.height) - 1)).bit_length() + col * self.height
    
    def can_play(self, mask, col):
        """Check if a column is playable"""
        return (mask & self.top_mask(mask, col)) == 0
    
    def play(self, position, mask, col):
        """Play a move and return new position and mask"""
        new_position = position ^ mask
        new_mask = mask | self.top_mask(mask, col)
        return new_position, new_mask
    
    def get_possible_moves(self, mask):
        """Get bitmask of all possible moves"""
        possible = 0
        for col in range(self.columns):
            if self.can_play(mask, col):
                possible |= self.top_mask(mask, col)
        return possible
    
    def count_winning_moves(self, position, mask):
        """Count number of winning moves available"""
        count = 0
        for col in range(self.columns):
            if self.can_play(mask, col) and self.is_winning_position(position | self.top_mask(mask, col)):
                count += 1
        return count
    
    def evaluate_position(self, position, mask, player):
        """Fast position evaluation"""
        # Check for immediate wins
        if self.can_win_next(position, mask):
            return 1000
        
        # Check if opponent can win
        opponent_pos = position ^ mask
        if self.can_win_next(opponent_pos, mask):
            return -1000
        
        score = 0
        
        # Center column control
        center_col = self.columns // 2
        center_mask = ((1 << self.height) - 1) << (center_col * self.height)
        center_control = bin(position & center_mask).count('1')
        score += center_control * 10
        
        # Count threats (positions that would create winning opportunities)
        threats = 0
        for col in range(self.columns):
            if self.can_play(mask, col):
                new_pos, new_mask = self.play(position, mask, col)
                if self.count_winning_moves(new_pos, new_mask) >= 2:
                    threats += 1
        
        score += threats * 15
        
        return score
    
    def negamax(self, position, mask, depth, alpha, beta, player):
        """Negamax with alpha-beta pruning using bitboards"""
        # Transposition table lookup
        key = hash((position, mask))
        if key in self.transposition_table and self.transposition_table[key][2] >= depth:
            return self.transposition_table[key][0], self.transposition_table[key][1]
        
        # Check if current player can win
        if self.can_win_next(position, mask):
            return 1000 - (42 - bin(mask).count('1')), None
        
        # Check for draw
        if bin(mask).count('1') >= self.rows * self.columns:
            return 0, None
        
        # Terminal depth
        if depth == 0:
            return self.evaluate_position(position, mask, player), None
        
        # Check if opponent can win next (forced moves)
        opponent_pos = position ^ mask
        forced_move = None
        for col in self.column_order:
            if self.can_play(mask, col):
                if self.is_winning_position(opponent_pos | self.top_mask(mask, col)):
                    if forced_move is not None:
                        # Multiple threats - we lose
                        return -1000 + (42 - bin(mask).count('1')), None
                    forced_move = col
        
        best_score = -2000
        best_move = None
        
        # If forced move, only consider that
        cols_to_check = [forced_move] if forced_move is not None else self.column_order
        
        for col in cols_to_check:
            if self.can_play(mask, col):
                new_pos, new_mask = self.play(position, mask, col)
                
                # Recursion with negation
                score, _ = self.negamax(new_pos ^ new_mask, new_mask, depth - 1, -beta, -alpha, 3 - player)
                score = -score
                
                if score > best_score:
                    best_score = score
                    best_move = col
                
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
        
        # Store in transposition table
        self.transposition_table[key] = (best_score, best_move, depth)
        
        return best_score, best_move
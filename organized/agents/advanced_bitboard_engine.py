"""
Advanced Bitboard Engine for Connect X
Ultra-optimized with precomputed tables and patterns
"""

import numpy as np
from numba import jit, int64, boolean
import pickle
import os

class AdvancedBitboardEngine:
    """
    High-performance bitboard implementation with:
    - Precomputed win masks for every position
    - Pattern recognition tables
    - Threat detection matrices
    - Optimized bit operations using numba JIT
    """
    
    def __init__(self):
        self.WIDTH = 7
        self.HEIGHT = 6
        self.SIZE = self.WIDTH * self.HEIGHT
        
        # Bitboard constants
        self.BOTTOM_MASK = 0x1041041041041  # Bottom row bits
        self.BOARD_MASK = 0x3FFFFFFFFFFF   # All valid positions
        
        # Precomputed tables
        self.win_masks = {}
        self.threat_masks = {}
        self.pattern_values = {}
        
        # Initialize or load precomputed tables
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize all precomputed lookup tables"""
        
        cache_file = "bitboard_tables.pkl"
        
        if os.path.exists(cache_file):
            print("Loading precomputed tables...")
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.win_masks = data['win_masks']
                self.threat_masks = data['threat_masks']
                self.pattern_values = data['pattern_values']
        else:
            print("Computing bitboard tables (one-time setup)...")
            self._compute_win_masks()
            self._compute_threat_masks()
            self._compute_pattern_values()
            
            # Save for future use
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'win_masks': self.win_masks,
                    'threat_masks': self.threat_masks,
                    'pattern_values': self.pattern_values
                }, f)
            print("Tables computed and saved!")
    
    def _compute_win_masks(self):
        """Precompute all possible winning positions"""
        
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                masks = []
                
                # Horizontal wins
                for c in range(max(0, col-3), min(col+1, self.WIDTH-3)):
                    mask = 0
                    for i in range(4):
                        mask |= 1 << self._bit_position(row, c + i)
                    masks.append(mask)
                
                # Vertical wins
                if row <= self.HEIGHT - 4:
                    mask = 0
                    for i in range(4):
                        mask |= 1 << self._bit_position(row + i, col)
                    masks.append(mask)
                
                # Diagonal \ wins
                for offset in range(-3, 1):
                    if (0 <= col + offset < self.WIDTH - 3 and 
                        0 <= row + offset < self.HEIGHT - 3):
                        mask = 0
                        for i in range(4):
                            mask |= 1 << self._bit_position(row + offset + i, col + offset + i)
                        masks.append(mask)
                
                # Diagonal / wins
                for offset in range(-3, 1):
                    if (0 <= col + offset < self.WIDTH - 3 and 
                        3 <= row - offset < self.HEIGHT):
                        mask = 0
                        for i in range(4):
                            mask |= 1 << self._bit_position(row - offset - i, col + offset + i)
                        masks.append(mask)
                
                self.win_masks[(row, col)] = masks
    
    def _compute_threat_masks(self):
        """Precompute threat patterns (3-in-a-row with empty space)"""
        
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                threats = []
                
                # Horizontal threats
                for c in range(max(0, col-3), min(col+1, self.WIDTH-3)):
                    for empty_pos in range(4):
                        mask = 0
                        empty_mask = 0
                        for i in range(4):
                            if i == empty_pos:
                                empty_mask |= 1 << self._bit_position(row, c + i)
                            else:
                                mask |= 1 << self._bit_position(row, c + i)
                        threats.append((mask, empty_mask))
                
                # Similar for vertical and diagonals...
                self.threat_masks[(row, col)] = threats
    
    def _compute_pattern_values(self):
        """Precompute evaluation values for common patterns"""
        
        # Pattern -> evaluation score mapping
        patterns = {
            # 4-in-a-row patterns
            0b1111: 10000,  # Win
            
            # 3-in-a-row patterns with space
            0b1110: 100,    # XXX_
            0b1101: 100,    # XX_X
            0b1011: 100,    # X_XX
            0b0111: 100,    # _XXX
            
            # 2-in-a-row patterns
            0b1100: 10,     # XX__
            0b0110: 15,     # _XX_
            0b0011: 10,     # __XX
            0b1010: 12,     # X_X_
            0b1001: 8,      # X__X
            0b0101: 12,     # _X_X
            
            # Single pieces
            0b1000: 1,      # X___
            0b0100: 2,      # _X__
            0b0010: 2,      # __X_
            0b0001: 1,      # ___X
        }
        
        self.pattern_values = patterns
    
    def _bit_position(self, row, col):
        """Convert row, col to bit position in bitboard"""
        return col * 7 + row  # Column-major ordering
    
    @staticmethod
    @jit(int64(int64), nopython=True)
    def popcount(bb):
        """Count set bits (Kernighan's algorithm)"""
        count = 0
        while bb:
            bb &= bb - 1
            count += 1
        return count
    
    @staticmethod
    @jit(boolean(int64), nopython=True)
    def is_win(position):
        """Check if position contains 4-in-a-row"""
        # Horizontal
        m = position & (position >> 7)
        if m & (m >> 14):
            return True
        
        # Diagonal \
        m = position & (position >> 6)
        if m & (m >> 12):
            return True
        
        # Diagonal /
        m = position & (position >> 8)
        if m & (m >> 16):
            return True
        
        # Vertical
        m = position & (position >> 1)
        if m & (m >> 2):
            return True
        
        return False
    
    def encode_position(self, board, player):
        """Convert board array to bitboard representation"""
        position = 0
        mask = 0
        
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                idx = row * self.WIDTH + col
                if board[idx] != 0:
                    bit_pos = self._bit_position(row, col)
                    mask |= 1 << bit_pos
                    if board[idx] == player:
                        position |= 1 << bit_pos
        
        return position, mask
    
    def decode_position(self, position, mask):
        """Convert bitboard back to array representation"""
        board = [0] * 42
        
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                bit_pos = self._bit_position(row, col)
                idx = row * self.WIDTH + col
                
                if mask & (1 << bit_pos):
                    if position & (1 << bit_pos):
                        board[idx] = 1
                    else:
                        board[idx] = 2
        
        return board
    
    def make_move(self, position, mask, col):
        """Make a move on the bitboard"""
        # Find the lowest empty row in column
        col_mask = 0x7F << (col * 7)  # All bits in column
        col_filled = mask & col_mask
        
        # Find first empty bit
        move_bit = (col_filled + (1 << (col * 7))) & col_mask
        
        new_mask = mask | move_bit
        new_position = position ^ new_mask
        
        return new_position, new_mask
    
    def get_valid_moves(self, mask):
        """Get list of valid columns"""
        valid = []
        top_mask = 0x40 << (6 * 7)  # Top row bit for each column
        
        for col in range(self.WIDTH):
            col_top = 1 << (col * 7 + 6)
            if not (mask & col_top):
                valid.append(col)
        
        return valid
    
    def evaluate_position(self, position, mask, player):
        """
        Evaluate position using precomputed patterns
        Returns score from player's perspective
        """
        score = 0
        opponent = position ^ mask
        
        # Check immediate wins
        if self.is_win(position):
            return 100000
        if self.is_win(opponent):
            return -100000
        
        # Count threats (positions where we can win next move)
        my_threats = self._count_threats(position, mask)
        opp_threats = self._count_threats(opponent, mask)
        
        score += (my_threats - opp_threats) * 50
        
        # Evaluate patterns
        score += self._evaluate_patterns(position, mask)
        
        # Center control bonus
        center_col = 3
        center_mask = 0x7F << (center_col * 7)
        my_center = self.popcount(position & center_mask)
        opp_center = self.popcount(opponent & center_mask)
        score += (my_center - opp_center) * 20
        
        # Height advantage (prefer lower positions)
        for col in range(self.WIDTH):
            col_mask = 0x7F << (col * 7)
            my_pieces = position & col_mask
            opp_pieces = opponent & col_mask
            
            # Lower pieces are more valuable
            for row in range(self.HEIGHT):
                bit = 1 << (col * 7 + row)
                if my_pieces & bit:
                    score += (self.HEIGHT - row) * 2
                if opp_pieces & bit:
                    score -= (self.HEIGHT - row) * 2
        
        return score
    
    def _count_threats(self, position, mask):
        """Count number of winning moves available"""
        threats = 0
        
        for col in self.get_valid_moves(mask):
            new_pos, new_mask = self.make_move(position, mask, col)
            if self.is_win(new_pos):
                threats += 1
        
        return threats
    
    def _evaluate_patterns(self, position, mask):
        """Evaluate board patterns using lookup table"""
        score = 0
        
        # Check all 4-piece windows
        # Horizontal
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH - 3):
                window = 0
                for i in range(4):
                    bit = 1 << self._bit_position(row, col + i)
                    if position & bit:
                        window |= (1 << i)
                
                if window in self.pattern_values:
                    score += self.pattern_values[window]
        
        # Vertical
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT - 3):
                window = 0
                for i in range(4):
                    bit = 1 << self._bit_position(row + i, col)
                    if position & bit:
                        window |= (1 << i)
                
                if window in self.pattern_values:
                    score += self.pattern_values[window]
        
        # Add diagonal patterns...
        
        return score
    
    def perft(self, position, mask, depth):
        """Performance test - count positions at given depth"""
        if depth == 0:
            return 1
        
        if self.is_win(position):
            return 0
        
        nodes = 0
        for col in self.get_valid_moves(mask):
            new_pos, new_mask = self.make_move(position, mask, col)
            nodes += self.perft(new_pos ^ new_mask, new_mask, depth - 1)
        
        return nodes


# Test the engine
if __name__ == "__main__":
    print("Initializing Advanced Bitboard Engine...")
    engine = AdvancedBitboardEngine()
    
    # Test basic operations
    board = [0] * 42
    board[35] = 1  # Bottom center
    board[36] = 1
    board[37] = 1
    
    pos, mask = engine.encode_position(board, 1)
    print(f"\nEncoded position: {bin(pos)}")
    print(f"Mask: {bin(mask)}")
    
    # Test win detection
    board[38] = 1
    pos, mask = engine.encode_position(board, 1)
    print(f"\nIs winning position: {engine.is_win(pos)}")
    
    # Performance test
    import time
    start = time.time()
    nodes = engine.perft(0, 0, 7)
    elapsed = time.time() - start
    print(f"\nPerft(7): {nodes} positions in {elapsed:.2f}s")
    print(f"Speed: {nodes/elapsed:.0f} positions/second")
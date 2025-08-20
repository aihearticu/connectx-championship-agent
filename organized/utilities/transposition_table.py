"""
Transposition Table with Zobrist Hashing
For efficient position caching in game tree search
"""

import random
import numpy as np
from enum import Enum

class TTFlag(Enum):
    EXACT = 0
    LOWER_BOUND = 1  # Alpha cutoff
    UPPER_BOUND = 2  # Beta cutoff

class TranspositionTable:
    """
    High-performance transposition table implementation
    - Zobrist hashing for O(1) position identification
    - Replacement strategy based on depth and age
    - Supports exact scores and bounds
    """
    
    def __init__(self, size_mb=256):
        """Initialize with given size in megabytes"""
        
        # Each entry is approximately 32 bytes
        entry_size = 32
        self.size = (size_mb * 1024 * 1024) // entry_size
        
        # Make size a power of 2 for fast modulo
        self.size = 1 << (self.size.bit_length() - 1)
        self.mask = self.size - 1
        
        # Initialize table
        self.table = [None] * self.size
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.collisions = 0
        self.stores = 0
        
        # Initialize Zobrist random numbers
        self._init_zobrist()
        
        print(f"Transposition table initialized: {self.size:,} entries ({size_mb}MB)")
    
    def _init_zobrist(self):
        """Initialize Zobrist random numbers for hashing"""
        random.seed(42)  # Deterministic for reproducibility
        
        # Random number for each piece at each position
        # 2 players * 42 positions
        self.zobrist_pieces = []
        for player in range(2):
            player_numbers = []
            for pos in range(42):
                player_numbers.append(random.getrandbits(64))
            self.zobrist_pieces.append(player_numbers)
        
        # Random number for side to move
        self.zobrist_turn = random.getrandbits(64)
    
    def compute_hash(self, board, player):
        """Compute Zobrist hash for position"""
        hash_value = 0
        
        for i, piece in enumerate(board):
            if piece != 0:
                # piece-1 because pieces are 1,2 but arrays are 0-indexed
                hash_value ^= self.zobrist_pieces[piece - 1][i]
        
        # Add turn information
        if player == 2:
            hash_value ^= self.zobrist_turn
        
        return hash_value
    
    def incremental_hash(self, hash_value, move_pos, player):
        """Update hash incrementally after a move"""
        # XOR with the piece at the new position
        hash_value ^= self.zobrist_pieces[player - 1][move_pos]
        # Switch turn
        hash_value ^= self.zobrist_turn
        return hash_value
    
    def probe(self, hash_key, depth, alpha, beta):
        """
        Probe the transposition table
        Returns (found, value, best_move)
        """
        self.misses += 1
        
        index = hash_key & self.mask
        entry = self.table[index]
        
        if entry is None:
            return False, 0, None
        
        # Check if this is the right position (collision detection)
        if entry['hash'] != hash_key:
            self.collisions += 1
            return False, 0, None
        
        self.misses -= 1
        self.hits += 1
        
        # Check if stored depth is sufficient
        if entry['depth'] < depth:
            return False, 0, None
        
        # Extract stored values
        flag = entry['flag']
        value = entry['value']
        best_move = entry['best_move']
        
        # Check bound types
        if flag == TTFlag.EXACT:
            return True, value, best_move
        elif flag == TTFlag.LOWER_BOUND and value >= beta:
            return True, value, best_move
        elif flag == TTFlag.UPPER_BOUND and value <= alpha:
            return True, value, best_move
        
        # Entry exists but doesn't provide a cutoff
        return False, 0, best_move
    
    def store(self, hash_key, depth, value, flag, best_move):
        """Store position in transposition table"""
        self.stores += 1
        
        index = hash_key & self.mask
        
        # Replacement strategy: always replace if deeper or same depth
        # This is simple but effective
        existing = self.table[index]
        
        if existing is None or existing['depth'] <= depth:
            self.table[index] = {
                'hash': hash_key,
                'depth': depth,
                'value': value,
                'flag': flag,
                'best_move': best_move
            }
    
    def clear(self):
        """Clear the transposition table"""
        self.table = [None] * self.size
        self.hits = 0
        self.misses = 0
        self.collisions = 0
        self.stores = 0
    
    def get_stats(self):
        """Get table statistics"""
        used_entries = sum(1 for entry in self.table if entry is not None)
        
        return {
            'size': self.size,
            'used': used_entries,
            'usage_percent': (used_entries / self.size) * 100,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': (self.hits / max(1, self.hits + self.misses)) * 100,
            'collisions': self.collisions,
            'stores': self.stores
        }
    
    def resize(self, new_size_mb):
        """Resize the table (clears all entries)"""
        self.__init__(new_size_mb)


class MoveOrderingTable:
    """
    Killer moves and history heuristic for move ordering
    """
    
    def __init__(self):
        # Killer moves: 2 per ply
        self.killers = {}  # ply -> [move1, move2]
        
        # History heuristic: score for each move
        self.history = [[0] * 7 for _ in range(2)]  # [player][column]
        
        # Countermove heuristic
        self.countermoves = {}  # last_move -> best_response
    
    def update_killers(self, ply, move):
        """Update killer moves for given ply"""
        if ply not in self.killers:
            self.killers[ply] = [None, None]
        
        # Don't store the same move twice
        if move != self.killers[ply][0]:
            # Shift and add new killer
            self.killers[ply][1] = self.killers[ply][0]
            self.killers[ply][0] = move
    
    def get_killers(self, ply):
        """Get killer moves for given ply"""
        if ply in self.killers:
            return [k for k in self.killers[ply] if k is not None]
        return []
    
    def update_history(self, player, move, depth):
        """Update history score for a move"""
        # Increase score based on depth (deeper = more important)
        self.history[player - 1][move] += depth * depth
        
        # Prevent overflow
        if self.history[player - 1][move] > 100000:
            # Halve all history scores
            for p in range(2):
                for m in range(7):
                    self.history[p][m] //= 2
    
    def get_history_score(self, player, move):
        """Get history score for a move"""
        return self.history[player - 1][move]
    
    def update_countermove(self, last_move, response):
        """Update countermove heuristic"""
        self.countermoves[last_move] = response
    
    def get_countermove(self, last_move):
        """Get best response to last move"""
        return self.countermoves.get(last_move, None)
    
    def order_moves(self, moves, player, ply, last_move=None, tt_move=None):
        """
        Order moves for better alpha-beta pruning
        Priority: TT move > Killers > Countermove > History > Center
        """
        scored_moves = []
        
        for move in moves:
            score = 0
            
            # Highest priority: TT move
            if move == tt_move:
                score += 1000000
            
            # Killer moves
            if move in self.get_killers(ply):
                score += 100000
            
            # Countermove
            if last_move is not None and move == self.get_countermove(last_move):
                score += 50000
            
            # History heuristic
            score += self.get_history_score(player, move)
            
            # Prefer center columns
            score += (3 - abs(move - 3)) * 10
            
            scored_moves.append((move, score))
        
        # Sort by score (descending)
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        return [move for move, _ in scored_moves]


# Test the transposition table
if __name__ == "__main__":
    print("Testing Transposition Table...")
    
    # Create table
    tt = TranspositionTable(size_mb=64)
    
    # Test basic operations
    test_board = [0] * 42
    test_board[35] = 1
    test_board[36] = 2
    
    hash1 = tt.compute_hash(test_board, 1)
    print(f"\nHash for position: {hash1}")
    
    # Store a position
    tt.store(hash1, depth=10, value=100, flag=TTFlag.EXACT, best_move=3)
    
    # Probe the position
    found, value, move = tt.probe(hash1, depth=8, alpha=-1000, beta=1000)
    print(f"Probe result: found={found}, value={value}, move={move}")
    
    # Test incremental hash
    test_board[37] = 1
    hash2_incremental = tt.incremental_hash(hash1, 37, 1)
    hash2_full = tt.compute_hash(test_board, 2)
    print(f"\nIncremental hash matches full hash: {hash2_incremental == hash2_full}")
    
    # Test move ordering
    print("\nTesting Move Ordering...")
    mot = MoveOrderingTable()
    
    # Update some moves
    mot.update_killers(5, 3)
    mot.update_killers(5, 4)
    mot.update_history(1, 3, 10)
    mot.update_history(1, 4, 5)
    mot.update_countermove(2, 3)
    
    # Order moves
    moves = [0, 1, 2, 3, 4, 5, 6]
    ordered = mot.order_moves(moves, player=1, ply=5, last_move=2, tt_move=4)
    print(f"Ordered moves: {ordered}")
    
    # Show statistics
    stats = tt.get_stats()
    print(f"\nTransposition Table Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
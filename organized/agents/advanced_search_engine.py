"""
Advanced Search Engine for Connect X
Integrates all components for maximum strength
"""

import time
import json
import pickle
import numpy as np
from enum import Enum
from advanced_bitboard_engine import AdvancedBitboardEngine
from transposition_table import TranspositionTable, TTFlag, MoveOrderingTable

class SearchEngine:
    """
    State-of-the-art search engine with:
    - Iterative deepening
    - Aspiration windows
    - Transposition tables
    - Advanced pruning (null move, LMR, futility)
    - Time management
    """
    
    def __init__(self, tt_size_mb=256, opening_book_file=None):
        # Core components
        self.bitboard = AdvancedBitboardEngine()
        self.tt = TranspositionTable(size_mb=tt_size_mb)
        self.move_ordering = MoveOrderingTable()
        
        # Search parameters
        self.max_depth = 20
        self.nodes_searched = 0
        self.time_limit = 0.5  # 500ms default
        self.start_time = 0
        
        # Opening book
        self.opening_book = {}
        if opening_book_file:
            self.load_opening_book(opening_book_file)
        
        # Pruning parameters
        self.null_move_enabled = True
        self.null_move_reduction = 2
        self.lmr_enabled = True
        self.lmr_threshold = 3  # Start LMR after this many moves
        self.futility_enabled = True
        self.futility_margin = 200
        
        # Statistics
        self.stats = {
            'nodes': 0,
            'tt_hits': 0,
            'null_move_cuts': 0,
            'lmr_reductions': 0,
            'futility_cuts': 0
        }
    
    def load_opening_book(self, filename):
        """Load opening book from file"""
        try:
            with open(filename, 'r') as f:
                book = json.load(f)
                # Convert string keys back to tuples
                self.opening_book = {}
                for key, value in book.items():
                    # Parse string representation of tuple
                    moves = eval(key) if key.startswith('(') else None
                    if moves:
                        self.opening_book[moves] = value
                print(f"Loaded opening book with {len(self.opening_book)} positions")
        except Exception as e:
            print(f"Could not load opening book: {e}")
    
    def get_opening_move(self, moves_played):
        """Get move from opening book if available"""
        if not self.opening_book:
            return None
        
        # Look for current position
        position = tuple(moves_played)
        
        # Find all possible next moves
        candidates = []
        for book_pos, stats in self.opening_book.items():
            if len(book_pos) == len(position) + 1:
                if book_pos[:-1] == position:
                    # This is a possible next move
                    move = book_pos[-1]
                    win_rate = stats.get('win_rate', 0.5)
                    total = stats.get('total', 0)
                    
                    if total >= 10:  # Minimum games threshold
                        candidates.append((move, win_rate, total))
        
        if not candidates:
            return None
        
        # Choose best move by win rate (with small random factor for diversity)
        candidates.sort(key=lambda x: x[1] + np.random.random() * 0.05, reverse=True)
        
        return candidates[0][0]
    
    def search(self, board, mark, time_limit=None):
        """
        Main search function with iterative deepening
        Returns best move
        """
        self.start_time = time.time()
        self.time_limit = time_limit if time_limit else 0.5
        self.nodes_searched = 0
        
        # Reset statistics
        self.stats = {
            'nodes': 0,
            'tt_hits': 0,
            'null_move_cuts': 0,
            'lmr_reductions': 0,
            'futility_cuts': 0
        }
        
        # Convert to bitboard
        position, mask = self.bitboard.encode_position(board, mark)
        
        # Check opening book first
        moves_played = self.get_moves_from_board(board)
        book_move = self.get_opening_move(moves_played)
        if book_move is not None:
            print(f"Opening book move: {book_move}")
            return book_move
        
        # Get valid moves
        valid_moves = self.bitboard.get_valid_moves(mask)
        
        # Quick check for forced moves
        for move in valid_moves:
            new_pos, new_mask = self.bitboard.make_move(position, mask, move)
            if self.bitboard.is_win(new_pos):
                return move
        
        # Check for forced blocks
        opponent = position ^ mask
        for move in valid_moves:
            new_opp, new_mask = self.bitboard.make_move(opponent, mask, move)
            if self.bitboard.is_win(new_opp):
                return move
        
        # Iterative deepening
        best_move = valid_moves[0] if valid_moves else 3
        best_score = -float('inf')
        
        # Aspiration window
        alpha = -float('inf')
        beta = float('inf')
        window_size = 50
        
        for depth in range(1, self.max_depth + 1):
            if self.time_up():
                break
            
            # Search with aspiration window
            score, move = self.alpha_beta(
                position, mask, depth, alpha, beta, 
                True, mark, 0, None
            )
            
            # Check for aspiration window fail
            if score <= alpha or score >= beta:
                # Research with full window
                alpha = -float('inf')
                beta = float('inf')
                score, move = self.alpha_beta(
                    position, mask, depth, alpha, beta,
                    True, mark, 0, None
                )
            
            # Update best move if we have one
            if move is not None:
                best_move = move
                best_score = score
                
                # Update aspiration window for next iteration
                alpha = score - window_size
                beta = score + window_size
            
            # Print search info
            elapsed = time.time() - self.start_time
            nps = self.nodes_searched / max(0.001, elapsed)
            
            print(f"Depth {depth}: score={score:.0f}, move={move}, "
                  f"nodes={self.nodes_searched}, nps={nps:.0f}, "
                  f"time={elapsed:.3f}s")
            
            # Check for mate score
            if abs(score) > 9000:
                print(f"Mate found!")
                break
        
        # Print statistics
        print(f"\nSearch statistics:")
        print(f"  Nodes: {self.stats['nodes']:,}")
        print(f"  TT hits: {self.stats['tt_hits']:,}")
        print(f"  Null move cuts: {self.stats['null_move_cuts']:,}")
        print(f"  LMR reductions: {self.stats['lmr_reductions']:,}")
        print(f"  Futility cuts: {self.stats['futility_cuts']:,}")
        
        return best_move
    
    def alpha_beta(self, position, mask, depth, alpha, beta, 
                   maximizing, mark, ply, last_move):
        """
        Alpha-beta search with enhancements
        """
        self.nodes_searched += 1
        self.stats['nodes'] += 1
        
        # Time check
        if self.time_up():
            return 0, None
        
        # Transposition table lookup
        hash_key = self.tt.compute_hash(
            self.bitboard.decode_position(position, mask), 
            1 if maximizing else 2
        )
        
        tt_hit, tt_value, tt_move = self.tt.probe(hash_key, depth, alpha, beta)
        if tt_hit:
            self.stats['tt_hits'] += 1
            return tt_value, tt_move
        
        # Terminal node checks
        if self.bitboard.is_win(position):
            score = 10000 - ply if maximizing else -10000 + ply
            return score, None
        
        opponent = position ^ mask
        if self.bitboard.is_win(opponent):
            score = -10000 + ply if maximizing else 10000 - ply
            return score, None
        
        valid_moves = self.bitboard.get_valid_moves(mask)
        if not valid_moves or depth == 0:
            score = self.bitboard.evaluate_position(position, mask, mark)
            return score, None
        
        # Null move pruning
        if (self.null_move_enabled and depth >= 3 and 
            not maximizing and ply > 0):
            
            # Make null move (pass)
            null_score, _ = self.alpha_beta(
                opponent, mask, depth - self.null_move_reduction - 1,
                -beta, -beta + 1, True, mark, ply + 1, None
            )
            null_score = -null_score
            
            if null_score >= beta:
                self.stats['null_move_cuts'] += 1
                return beta, None
        
        # Futility pruning
        if (self.futility_enabled and depth <= 2 and 
            abs(alpha) < 9000 and abs(beta) < 9000):
            
            static_eval = self.bitboard.evaluate_position(position, mask, mark)
            
            if maximizing and static_eval + self.futility_margin * depth < alpha:
                self.stats['futility_cuts'] += 1
                return alpha, None
            
            if not maximizing and static_eval - self.futility_margin * depth > beta:
                self.stats['futility_cuts'] += 1
                return beta, None
        
        # Order moves
        moves = self.move_ordering.order_moves(
            valid_moves, mark if maximizing else 3 - mark,
            ply, last_move, tt_move
        )
        
        best_move = moves[0] if moves else None
        best_score = -float('inf') if maximizing else float('inf')
        
        for i, move in enumerate(moves):
            # Make move
            new_pos, new_mask = self.bitboard.make_move(position, mask, move)
            
            # Late move reduction
            reduction = 0
            if (self.lmr_enabled and depth >= 3 and i >= self.lmr_threshold):
                reduction = 1
                if i >= 6:
                    reduction = 2
                self.stats['lmr_reductions'] += 1
            
            # Recursive search
            score, _ = self.alpha_beta(
                new_pos if maximizing else new_pos ^ new_mask,
                new_mask,
                depth - 1 - reduction,
                alpha, beta,
                not maximizing,
                mark,
                ply + 1,
                move
            )
            
            # Re-search if LMR failed high
            if reduction > 0 and score > alpha:
                score, _ = self.alpha_beta(
                    new_pos if maximizing else new_pos ^ new_mask,
                    new_mask,
                    depth - 1,
                    alpha, beta,
                    not maximizing,
                    mark,
                    ply + 1,
                    move
                )
            
            # Update best score
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)
            
            # Beta/Alpha cutoff
            if beta <= alpha:
                # Update killer moves
                self.move_ordering.update_killers(ply, move)
                self.move_ordering.update_history(
                    mark if maximizing else 3 - mark, 
                    move, depth
                )
                
                if last_move is not None:
                    self.move_ordering.update_countermove(last_move, move)
                
                break
        
        # Store in transposition table
        if best_score <= alpha:
            flag = TTFlag.UPPER_BOUND
        elif best_score >= beta:
            flag = TTFlag.LOWER_BOUND
        else:
            flag = TTFlag.EXACT
        
        self.tt.store(hash_key, depth, best_score, flag, best_move)
        
        return best_score, best_move
    
    def time_up(self):
        """Check if time limit exceeded"""
        return (time.time() - self.start_time) >= self.time_limit * 0.95
    
    def get_moves_from_board(self, board):
        """Extract move sequence from board position"""
        moves = []
        # This is a simplified version - would need full game history
        return moves


# Test the search engine
if __name__ == "__main__":
    print("Testing Advanced Search Engine...")
    
    engine = SearchEngine(tt_size_mb=128)
    
    # Test position
    test_board = [0] * 42
    test_board[35] = 1  # Bottom center
    test_board[36] = 2
    test_board[37] = 1
    test_board[38] = 2
    
    print("\nSearching position...")
    best_move = engine.search(test_board, mark=1, time_limit=2.0)
    
    print(f"\nBest move: {best_move}")
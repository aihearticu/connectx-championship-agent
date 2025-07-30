"""
Advanced Search Algorithm with Modern Techniques
Implements:
- Negamax with alpha-beta pruning
- Transposition tables with Zobrist hashing
- Null move pruning
- Late move reductions (LMR)
- Futility pruning
- Aspiration windows
- Killer moves and history heuristic
"""

import random
import time
from collections import defaultdict

class TranspositionTable:
    """Transposition table with Zobrist hashing"""
    
    def __init__(self, size_mb=64):
        self.size = (size_mb * 1024 * 1024) // 32  # Approximate entries
        self.table = {}
        self.zobrist_table = self._init_zobrist()
        
    def _init_zobrist(self):
        """Initialize Zobrist random numbers"""
        random.seed(42)  # Reproducible
        zobrist = {}
        
        # For each position and piece type
        for col in range(7):
            for row in range(6):
                for piece in [1, 2]:
                    zobrist[(col, row, piece)] = random.getrandbits(64)
        
        # Side to move
        zobrist['side'] = random.getrandbits(64)
        
        return zobrist
    
    def get_hash(self, board, side_to_move):
        """Calculate Zobrist hash for position"""
        h = 0
        
        for col in range(7):
            for row in range(6):
                idx = row * 7 + col
                if board[idx] != 0:
                    h ^= self.zobrist_table[(col, row, board[idx])]
        
        if side_to_move == 2:
            h ^= self.zobrist_table['side']
        
        return h
    
    def probe(self, key, depth):
        """Look up position in table"""
        if key in self.table:
            entry = self.table[key]
            if entry['depth'] >= depth:
                return entry
        return None
    
    def store(self, key, depth, score, flag, best_move):
        """Store position in table"""
        # Replace if new entry is deeper or table is full
        if len(self.table) >= self.size:
            # Simple replacement scheme - could be improved
            if key not in self.table or self.table[key]['depth'] <= depth:
                # Remove oldest entry (simplified)
                if len(self.table) >= self.size:
                    self.table.pop(next(iter(self.table)))
        
        self.table[key] = {
            'depth': depth,
            'score': score,
            'flag': flag,  # EXACT, LOWER, UPPER
            'best_move': best_move
        }

class AdvancedSearch:
    """Advanced search with modern pruning techniques"""
    
    # Transposition table flags
    EXACT = 0
    LOWER = 1
    UPPER = 2
    
    def __init__(self, bitboard_engine):
        self.engine = bitboard_engine
        self.tt = TranspositionTable()
        self.killer_moves = defaultdict(lambda: [None, None])
        self.history = defaultdict(int)
        self.nodes_searched = 0
        self.time_limit = 0.9  # 900ms time limit
        self.start_time = 0
        
        # Search parameters
        self.NULL_MOVE_R = 2  # Null move reduction
        self.LMR_THRESHOLD = 3  # Late move reduction after N moves
        self.FUTILITY_MARGIN = 200  # Futility pruning margin
        
    def search(self, position, mask, max_depth, start_time):
        """Main search function with iterative deepening"""
        self.start_time = start_time
        self.nodes_searched = 0
        
        best_move = None
        best_score = -float('inf')
        
        # Get valid moves
        moves = self.engine.move_order(mask)
        if not moves:
            return None, 0
        
        # Iterative deepening with aspiration windows
        alpha = -float('inf')
        beta = float('inf')
        
        for depth in range(1, max_depth + 1):
            if time.time() - self.start_time > self.time_limit:
                break
            
            # Aspiration window
            if depth > 3 and best_score != -float('inf'):
                alpha = best_score - 50
                beta = best_score + 50
            
            score, move = self._search_root(position, mask, depth, alpha, beta)
            
            # Re-search if outside aspiration window
            if score <= alpha or score >= beta:
                score, move = self._search_root(position, mask, depth, 
                                               -float('inf'), float('inf'))
            
            if move is not None:
                best_move = move
                best_score = score
            
            # Stop if we found a win
            if best_score >= 9000:
                break
        
        return best_move, best_score
    
    def _search_root(self, position, mask, depth, alpha, beta):
        """Search from root position"""
        best_move = None
        best_score = -float('inf')
        
        moves = self._order_moves(position, mask, None, depth)
        
        for i, col in enumerate(moves):
            # Make move
            new_pos, new_mask = self.engine.play_move(col, position, mask)
            
            # Late move reduction
            reduction = 0
            if i >= self.LMR_THRESHOLD and depth > 3:
                reduction = 1
            
            # Search
            score = -self._negamax(new_pos, new_mask, depth - 1 - reduction, 
                                   -beta, -alpha, False)
            
            # Re-search if LMR failed
            if reduction > 0 and score > alpha:
                score = -self._negamax(new_pos, new_mask, depth - 1, 
                                      -beta, -alpha, False)
            
            if score > best_score:
                best_score = score
                best_move = col
            
            alpha = max(alpha, score)
            
            if alpha >= beta:
                break
        
        return best_score, best_move
    
    def _negamax(self, position, mask, depth, alpha, beta, can_null):
        """Negamax with all pruning techniques"""
        self.nodes_searched += 1
        
        # Time check
        if time.time() - self.start_time > self.time_limit:
            return 0
        
        orig_alpha = alpha
        
        # Transposition table lookup
        key = self.engine.get_key(position, mask)
        tt_entry = self.tt.probe(key, depth)
        
        if tt_entry is not None:
            if tt_entry['flag'] == self.EXACT:
                return tt_entry['score']
            elif tt_entry['flag'] == self.LOWER:
                alpha = max(alpha, tt_entry['score'])
            elif tt_entry['flag'] == self.UPPER:
                beta = min(beta, tt_entry['score'])
            
            if alpha >= beta:
                return tt_entry['score']
        
        # Check for draw
        if mask == 0x3FFFFFFFFFFF:  # Board full
            return 0
        
        # Check for immediate win
        wins = self.engine.get_winning_moves(position, mask)
        if wins:
            return 10000 - (50 - self.engine.popcount(mask))
        
        # Terminal node or depth limit
        if depth <= 0:
            return self._quiescence(position, mask, alpha, beta)
        
        # Null move pruning
        if can_null and depth > 3:
            # Make null move (pass)
            null_score = -self._negamax(position ^ mask, mask, 
                                        depth - self.NULL_MOVE_R - 1, 
                                        -beta, -beta + 1, False)
            if null_score >= beta:
                return beta
        
        # Futility pruning
        if depth <= 3:
            eval_score = self.engine.evaluate_position(position, mask)
            if eval_score + self.FUTILITY_MARGIN * depth < alpha:
                return alpha
        
        # Get and order moves
        moves = self._order_moves(position, mask, tt_entry, depth)
        best_move = moves[0] if moves else None
        best_score = -float('inf')
        
        for i, col in enumerate(moves):
            # Make move
            new_pos, new_mask = self.engine.play_move(col, position, mask)
            
            # Late move reduction
            reduction = 0
            if i >= self.LMR_THRESHOLD and depth > 3:
                # Reduce less promising moves
                reduction = 1
                if i > 6:
                    reduction = 2
            
            # Search with reduction
            score = -self._negamax(new_pos, new_mask, depth - 1 - reduction,
                                   -beta, -alpha, True)
            
            # Re-search if reduction failed
            if reduction > 0 and score > alpha:
                score = -self._negamax(new_pos, new_mask, depth - 1,
                                       -beta, -alpha, True)
            
            if score > best_score:
                best_score = score
                best_move = col
            
            alpha = max(alpha, score)
            
            if alpha >= beta:
                # Update killer moves
                self._update_killers(col, depth)
                # Update history
                self.history[(position & 0xFF, col)] += depth * depth
                break
        
        # Store in transposition table
        flag = self.EXACT
        if best_score <= orig_alpha:
            flag = self.UPPER
        elif best_score >= beta:
            flag = self.LOWER
        
        self.tt.store(key, depth, best_score, flag, best_move)
        
        return best_score
    
    def _quiescence(self, position, mask, alpha, beta):
        """Quiescence search - only examine forcing moves"""
        # Evaluate position
        eval_score = self.engine.evaluate_position(position, mask)
        
        if eval_score >= beta:
            return beta
        if eval_score > alpha:
            alpha = eval_score
        
        # Only look at winning moves and blocks
        wins = self.engine.get_winning_moves(position, mask)
        if wins:
            return 10000 - (50 - self.engine.popcount(mask))
        
        # Check opponent wins to block
        opponent = position ^ mask
        opp_wins = self.engine.get_winning_moves(opponent, mask)
        
        if len(opp_wins) > 1:
            # Can't block multiple threats
            return -10000 + (50 - self.engine.popcount(mask))
        
        if opp_wins:
            # Must block
            col = opp_wins[0]
            new_pos, new_mask = self.engine.play_move(col, position, mask)
            return -self._quiescence(new_pos, new_mask, -beta, -alpha)
        
        return eval_score
    
    def _order_moves(self, position, mask, tt_entry, depth):
        """Order moves for better pruning"""
        moves = []
        scores = {}
        
        # Get all valid moves
        for col in range(7):
            if self.engine.can_play(col, mask):
                moves.append(col)
                scores[col] = 0
        
        # TT move first
        if tt_entry and tt_entry['best_move'] in moves:
            scores[tt_entry['best_move']] += 10000
        
        # Winning moves
        for col in moves:
            if self.engine.is_winning_move(col, position, mask):
                scores[col] += 5000
        
        # Killer moves
        for killer in self.killer_moves[depth]:
            if killer in moves:
                scores[col] += 1000
        
        # History heuristic
        for col in moves:
            scores[col] += self.history.get((position & 0xFF, col), 0)
        
        # Center preference
        center = 3
        for col in moves:
            scores[col] += (3 - abs(col - center)) * 10
        
        # Sort by score
        moves.sort(key=lambda c: scores[c], reverse=True)
        
        return moves
    
    def _update_killers(self, move, depth):
        """Update killer moves"""
        killers = self.killer_moves[depth]
        if move != killers[0]:
            killers[1] = killers[0]
            killers[0] = move
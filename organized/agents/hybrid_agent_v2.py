#!/usr/bin/env python3
"""
Hybrid Agent V2 - Combines Championship Engine with Neural Enhancement
Uses neural network for move ordering and evaluation adjustment
"""

import numpy as np
import time
import json

class HybridAgent:
    """
    Advanced hybrid agent combining:
    1. Championship minimax engine (base)
    2. Neural network for move ordering
    3. Pattern recognition enhancements
    4. Dynamic strategy adjustment
    """
    
    def __init__(self):
        # Core components
        self.search_depth = {
            'opening': 12,
            'midgame': 10,
            'endgame': 14
        }
        
        # Enhanced opening book
        self.opening_book = self._create_enhanced_opening_book()
        
        # Transposition table
        self.transposition_table = {}
        self.tt_hits = 0
        
        # Killer moves
        self.killer_moves = [[None, None] for _ in range(20)]
        
        # Neural-inspired pattern weights
        self.pattern_weights = {
            'win': 100000,
            'block_win': 50000,
            'double_threat': 5000,
            'threat': 1000,
            'center_control': 200,
            'mobility': 50,
            'connection': 30,
            'fork_potential': 150
        }
        
        # Move ordering neural weights (learned from analysis)
        self.move_order_weights = self._init_move_order_weights()
    
    def _create_enhanced_opening_book(self):
        """Enhanced opening book with deep variations"""
        book = {
            # First moves
            (): 3,
            
            # Second moves - comprehensive responses
            (3,): 3,
            (0,): 3, (1,): 3, (2,): 3, (4,): 3, (5,): 3, (6,): 3,
            
            # Third moves - key variations
            (3, 3): 2,  # Block center
            (3, 3, 2): 3,
            (3, 3, 4): 3,
            
            # Deep tactical lines
            (3, 3, 2, 3): 4,  # Force advantageous position
            (3, 3, 2, 3, 4): 3,
            (3, 3, 2, 3, 4, 3): 1,
            (3, 3, 2, 3, 4, 3, 1): 4,
            
            # Alternative defenses
            (3, 2): 3,
            (3, 4): 3,
            (3, 2, 3): 4,
            (3, 4, 3): 2,
            
            # Extended sequences for common patterns
            (3, 3, 2, 2): 4,
            (3, 3, 2, 4): 1,
            (3, 3, 4, 4): 2,
            (3, 3, 4, 2): 5,
            
            # Trap sequences
            (3, 3, 2, 3, 4, 4): 5,  # Sets up winning attack
            (3, 3, 2, 3, 4, 2): 1,  # Alternative trap
            
            # Counter-strategies
            (3, 3, 2, 1): 4,
            (3, 3, 2, 5): 4,
            (3, 3, 4, 1): 5,
            (3, 3, 4, 5): 2,
        }
        
        # Add mirrored positions
        mirrored = {}
        for moves, response in book.items():
            if moves:
                mirrored_moves = tuple(6 - m for m in moves)
                mirrored_response = 6 - response
                mirrored[mirrored_moves] = mirrored_response
        
        book.update(mirrored)
        return book
    
    def _init_move_order_weights(self):
        """Neural-inspired move ordering weights"""
        return {
            'center_proximity': [1.0, 0.8, 0.6, 0.4, 0.6, 0.8, 1.0],
            'win_potential': [0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7],
            'defensive_value': [0.6, 0.7, 0.8, 0.9, 0.8, 0.7, 0.6],
            'connectivity': [0.5, 0.7, 0.9, 1.0, 0.9, 0.7, 0.5]
        }
    
    def get_game_phase(self, board):
        """Determine game phase"""
        pieces = sum(1 for x in board if x != 0)
        if pieces < 10:
            return 'opening'
        elif pieces < 25:
            return 'midgame'
        else:
            return 'endgame'
    
    def evaluate_position(self, board, player):
        """Advanced position evaluation"""
        score = 0
        opponent = 3 - player
        
        # Check for wins
        player_win = self._check_win_fast(board, player)
        opponent_win = self._check_win_fast(board, opponent)
        
        if player_win:
            return self.pattern_weights['win']
        if opponent_win:
            return -self.pattern_weights['win']
        
        # Evaluate threats
        player_threats = self._count_threats(board, player)
        opponent_threats = self._count_threats(board, opponent)
        
        # Double threat detection
        if player_threats >= 2:
            score += self.pattern_weights['double_threat']
        if opponent_threats >= 2:
            score -= self.pattern_weights['double_threat'] * 1.2
        
        # Single threats
        score += player_threats * self.pattern_weights['threat']
        score -= opponent_threats * self.pattern_weights['threat'] * 1.1
        
        # Center control
        center_score = self._evaluate_center_control(board, player, opponent)
        score += center_score * self.pattern_weights['center_control']
        
        # Connectivity and patterns
        pattern_score = self._evaluate_patterns(board, player, opponent)
        score += pattern_score
        
        # Mobility (available good moves)
        mobility_score = self._evaluate_mobility(board, player, opponent)
        score += mobility_score * self.pattern_weights['mobility']
        
        # Fork potential
        fork_score = self._evaluate_fork_potential(board, player, opponent)
        score += fork_score * self.pattern_weights['fork_potential']
        
        return score
    
    def _check_win_fast(self, board, player):
        """Fast win checking"""
        # Convert to 2D for easier checking
        b = [board[i:i+7] for i in range(0, 42, 7)]
        
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(b[row][col+i] == player for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(b[row+i][col] == player for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                if all(b[row+i][col+i] == player for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3, 6):
            for col in range(4):
                if all(b[row-i][col+i] == player for i in range(4)):
                    return True
        
        return False
    
    def _count_threats(self, board, player):
        """Count winning threats"""
        threats = 0
        
        for col in range(7):
            if board[col] == 0:  # Valid move
                # Simulate move
                test_board = board[:]
                for row in range(5, -1, -1):
                    if test_board[row * 7 + col] == 0:
                        test_board[row * 7 + col] = player
                        break
                
                # Check if it creates a win
                if self._check_win_fast(test_board, player):
                    threats += 1
        
        return threats
    
    def _evaluate_center_control(self, board, player, opponent):
        """Evaluate center column control"""
        score = 0
        center = 3
        
        # Count pieces in center column
        for row in range(6):
            if board[row * 7 + center] == player:
                score += (6 - row)  # Higher rows worth more
            elif board[row * 7 + center] == opponent:
                score -= (6 - row)
        
        # Adjacent columns
        for col in [2, 4]:
            for row in range(6):
                if board[row * 7 + col] == player:
                    score += (6 - row) * 0.5
                elif board[row * 7 + col] == opponent:
                    score -= (6 - row) * 0.5
        
        return score
    
    def _evaluate_patterns(self, board, player, opponent):
        """Evaluate board patterns"""
        score = 0
        
        # Check all 4-windows
        for length in range(4, 0, -1):
            player_patterns = self._count_patterns(board, player, length)
            opponent_patterns = self._count_patterns(board, opponent, length)
            
            # Weight patterns by length
            weight = self.pattern_weights['connection'] * (length ** 2)
            score += player_patterns * weight
            score -= opponent_patterns * weight * 1.1
        
        return score
    
    def _count_patterns(self, board, player, length):
        """Count patterns of given length"""
        count = 0
        b = [board[i:i+7] for i in range(0, 42, 7)]
        
        # Horizontal
        for row in range(6):
            for col in range(8 - length):
                window = [b[row][col+i] for i in range(length)]
                if all(p == player or p == 0 for p in window) and window.count(player) == length - 1:
                    count += 1
        
        # Vertical
        for col in range(7):
            for row in range(7 - length):
                window = [b[row+i][col] for i in range(length)]
                if all(p == player or p == 0 for p in window) and window.count(player) == length - 1:
                    count += 1
        
        return count
    
    def _evaluate_mobility(self, board, player, opponent):
        """Evaluate mobility (quality of available moves)"""
        player_mobility = 0
        opponent_mobility = 0
        
        for col in range(7):
            if board[col] == 0:
                # Simulate moves and evaluate
                row = self._get_drop_row(board, col)
                if row is not None:
                    # Player move
                    board[row * 7 + col] = player
                    player_mobility += self._quick_eval(board, player)
                    board[row * 7 + col] = 0
                    
                    # Opponent move
                    board[row * 7 + col] = opponent
                    opponent_mobility += self._quick_eval(board, opponent)
                    board[row * 7 + col] = 0
        
        return player_mobility - opponent_mobility
    
    def _evaluate_fork_potential(self, board, player, opponent):
        """Evaluate potential for creating forks"""
        score = 0
        
        # Look for positions that could create multiple threats
        for col in range(7):
            if board[col] == 0:
                row = self._get_drop_row(board, col)
                if row is not None:
                    # Simulate move
                    board[row * 7 + col] = player
                    threats = self._count_threats(board, player)
                    if threats >= 2:
                        score += 1
                    board[row * 7 + col] = 0
        
        return score
    
    def _get_drop_row(self, board, col):
        """Get row where piece would land"""
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                return row
        return None
    
    def _quick_eval(self, board, player):
        """Quick evaluation for move ordering"""
        score = 0
        
        # Simple pattern counting
        for i in range(42):
            if board[i] == player:
                # Reward center positions
                col = i % 7
                score += self.move_order_weights['center_proximity'][col]
        
        return score
    
    def order_moves(self, board, valid_moves, player):
        """Neural-inspired move ordering"""
        move_scores = []
        
        for move in valid_moves:
            score = 0
            
            # Center proximity
            score += self.move_order_weights['center_proximity'][move] * 100
            
            # Check for immediate wins
            row = self._get_drop_row(board, move)
            if row is not None:
                board[row * 7 + move] = player
                if self._check_win_fast(board, player):
                    score += 10000
                board[row * 7 + move] = 0
                
                # Check for blocking opponent wins
                board[row * 7 + move] = 3 - player
                if self._check_win_fast(board, 3 - player):
                    score += 5000
                board[row * 7 + move] = 0
            
            # Killer move bonus
            if move in self.killer_moves[0]:
                score += 1000
            
            move_scores.append((move, score))
        
        # Sort by score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def minimax(self, board, depth, alpha, beta, maximizing, player, start_time):
        """Enhanced minimax with neural-inspired improvements"""
        # Time check
        if time.time() - start_time > 0.9:
            return self.evaluate_position(board, player), None
        
        # Transposition table lookup
        board_key = tuple(board)
        if board_key in self.transposition_table:
            entry = self.transposition_table[board_key]
            if entry['depth'] >= depth:
                self.tt_hits += 1
                return entry['score'], entry['move']
        
        # Terminal node check
        if depth == 0 or self._is_terminal(board):
            return self.evaluate_position(board, player), None
        
        # Get valid moves
        valid_moves = [col for col in range(7) if board[col] == 0]
        if not valid_moves:
            return 0, None
        
        # Order moves using neural-inspired heuristics
        ordered_moves = self.order_moves(board, valid_moves, player if maximizing else 3 - player)
        
        best_move = ordered_moves[0]
        
        if maximizing:
            max_eval = -float('inf')
            
            for i, move in enumerate(ordered_moves):
                # Make move
                row = self._get_drop_row(board, move)
                board[row * 7 + move] = player
                
                # Late move reduction
                reduction = 0
                if i >= 4 and depth > 4:
                    reduction = 1
                
                # Recursive call
                eval_score, _ = self.minimax(
                    board, depth - 1 - reduction, alpha, beta, 
                    False, player, start_time
                )
                
                # Undo move
                board[row * 7 + move] = 0
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if move not in self.killer_moves[depth]:
                        self.killer_moves[depth][1] = self.killer_moves[depth][0]
                        self.killer_moves[depth][0] = move
                    break
            
            # Store in transposition table
            if len(self.transposition_table) < 1000000:
                self.transposition_table[board_key] = {
                    'score': max_eval,
                    'move': best_move,
                    'depth': depth
                }
            
            return max_eval, best_move
        
        else:
            min_eval = float('inf')
            
            for i, move in enumerate(ordered_moves):
                # Make move
                row = self._get_drop_row(board, move)
                board[row * 7 + move] = 3 - player
                
                # Late move reduction
                reduction = 0
                if i >= 4 and depth > 4:
                    reduction = 1
                
                # Recursive call
                eval_score, _ = self.minimax(
                    board, depth - 1 - reduction, alpha, beta, 
                    True, player, start_time
                )
                
                # Undo move
                board[row * 7 + move] = 0
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if move not in self.killer_moves[depth]:
                        self.killer_moves[depth][1] = self.killer_moves[depth][0]
                        self.killer_moves[depth][0] = move
                    break
            
            return min_eval, best_move
    
    def _is_terminal(self, board):
        """Check if game is over"""
        # Check for wins
        for player in [1, 2]:
            if self._check_win_fast(board, player):
                return True
        
        # Check for draw
        return all(board[i] != 0 for i in range(7))
    
    def get_move(self, board, player):
        """Get best move for position"""
        # Check opening book
        moves = self._get_move_sequence(board)
        move_tuple = tuple(moves)
        
        if move_tuple in self.opening_book:
            book_move = self.opening_book[move_tuple]
            if board[book_move] == 0:
                return book_move
        
        # Determine game phase and depth
        phase = self.get_game_phase(board)
        depth = self.search_depth[phase]
        
        # Clear old transposition entries periodically
        if len(self.transposition_table) > 500000:
            self.transposition_table.clear()
        
        # Run minimax search
        start_time = time.time()
        _, best_move = self.minimax(board, depth, -float('inf'), float('inf'), True, player, start_time)
        
        return best_move
    
    def _get_move_sequence(self, board):
        """Reconstruct move sequence from board"""
        moves = []
        # Simplified - just count pieces in each column
        for col in range(7):
            count = sum(1 for row in range(6) if board[row * 7 + col] != 0)
            moves.extend([col] * count)
        return moves[:15]  # Limit to first 15 moves


# Create agent function for Kaggle
def agent(observation, configuration):
    """Hybrid agent for Kaggle submission"""
    # Initialize on first call
    if not hasattr(agent, 'hybrid'):
        agent.hybrid = HybridAgent()
    
    # Get move
    board = observation.board
    player = observation.mark
    
    move = agent.hybrid.get_move(board, player)
    
    # Ensure valid move
    if move is None or board[move] != 0:
        # Fallback to first valid move
        for col in range(7):
            if board[col] == 0:
                return col
    
    return int(move)


# Test the hybrid agent
if __name__ == "__main__":
    print("Testing Hybrid Agent V2...")
    
    from kaggle_environments import make
    
    # Test vs random
    wins = 0
    for i in range(10):
        env = make('connectx', debug=False)
        if i % 2 == 0:
            env.run([agent, 'random'])
            if env.state[0].reward == 1:
                wins += 1
        else:
            env.run(['random', agent])
            if env.state[1].reward == 1:
                wins += 1
    
    print(f"Win rate vs random: {wins}/10 ({wins*10}%)")
    
    # Test vs negamax
    wins = 0
    for i in range(10):
        env = make('connectx', debug=False)
        if i % 2 == 0:
            env.run([agent, 'negamax'])
            if env.state[0].reward == 1:
                wins += 1
        else:
            env.run(['negamax', agent])
            if env.state[1].reward == 1:
                wins += 1
    
    print(f"Win rate vs negamax: {wins}/10 ({wins*10}%)")
"""
Pattern Recognition System
Advanced pattern detection for Connect 4 evaluation
"""

import numpy as np
from bitboard_engine_v2 import BitboardEngine

class PatternRecognition:
    """Detect and evaluate complex patterns in Connect 4"""
    
    def __init__(self):
        self.engine = BitboardEngine()
        self._init_pattern_masks()
        self._init_pattern_values()
        
    def _init_pattern_masks(self):
        """Initialize masks for pattern detection"""
        self.patterns = {
            'horizontal_4': [],
            'vertical_4': [],
            'diagonal_4_down': [],
            'diagonal_4_up': [],
            'open_3': [],
            'blocked_3': [],
            'split_3': [],
            'open_2': [],
            'fork_patterns': []
        }
        
        # Generate all 4-in-a-row patterns
        # Horizontal
        for row in range(6):
            for col in range(4):
                mask = 0
                for i in range(4):
                    mask |= 1 << ((col + i) * 7 + row)
                self.patterns['horizontal_4'].append(mask)
        
        # Vertical
        for col in range(7):
            for row in range(3):
                mask = 0
                for i in range(4):
                    mask |= 1 << (col * 7 + row + i)
                self.patterns['vertical_4'].append(mask)
        
        # Diagonal down
        for col in range(4):
            for row in range(3):
                mask = 0
                for i in range(4):
                    mask |= 1 << ((col + i) * 7 + row + i)
                self.patterns['diagonal_4_down'].append(mask)
        
        # Diagonal up
        for col in range(4):
            for row in range(3, 6):
                mask = 0
                for i in range(4):
                    mask |= 1 << ((col + i) * 7 + row - i)
                self.patterns['diagonal_4_up'].append(mask)
        
        # Generate threat patterns (3-in-a-row with space)
        self._generate_threat_patterns()
        
    def _generate_threat_patterns(self):
        """Generate patterns for threats and forks"""
        # Open 3 patterns (XXX_)
        # Horizontal
        for row in range(6):
            for col in range(5):
                # XXX_
                mask = 0
                for i in range(3):
                    mask |= 1 << ((col + i) * 7 + row)
                space = 1 << ((col + 3) * 7 + row)
                self.patterns['open_3'].append((mask, space))
                
                # _XXX
                mask = 0
                for i in range(3):
                    mask |= 1 << ((col + i + 1) * 7 + row)
                space = 1 << (col * 7 + row)
                self.patterns['open_3'].append((mask, space))
        
        # Split 3 patterns (XX_X)
        for row in range(6):
            for col in range(4):
                # XX_X
                mask = (1 << (col * 7 + row)) | (1 << ((col + 1) * 7 + row)) | (1 << ((col + 3) * 7 + row))
                space = 1 << ((col + 2) * 7 + row)
                self.patterns['split_3'].append((mask, space))
                
                # X_XX
                mask = (1 << (col * 7 + row)) | (1 << ((col + 2) * 7 + row)) | (1 << ((col + 3) * 7 + row))
                space = 1 << ((col + 1) * 7 + row)
                self.patterns['split_3'].append((mask, space))
        
        # Similar for vertical and diagonal...
        
    def _init_pattern_values(self):
        """Initialize values for different patterns"""
        self.pattern_values = {
            'win_4': 10000,
            'open_3': 100,
            'blocked_3': 50,
            'split_3': 75,
            'open_2': 10,
            'blocked_2': 5,
            'fork': 200,
            'double_threat': 150,
            'center_control': 20,
            'adjacent_center': 10
        }
    
    def evaluate_position(self, position, mask):
        """Comprehensive position evaluation using patterns"""
        my_score = self._evaluate_player(position, mask)
        opponent = position ^ mask
        opp_score = self._evaluate_player(opponent, mask)
        
        # Add positional bonuses
        positional_score = self._evaluate_positional(position, opponent, mask)
        
        # Combine scores with defensive weight
        return my_score - opp_score * 1.1 + positional_score
    
    def _evaluate_player(self, position, mask):
        """Evaluate patterns for one player"""
        score = 0
        
        # Check winning patterns
        if self.engine.alignment(position):
            return self.pattern_values['win_4']
        
        # Count threats
        threats = []
        
        # Open 3s
        open_3_count = 0
        for pattern, space in self.patterns['open_3']:
            if (position & pattern) == pattern and (mask & space) == 0:
                open_3_count += 1
                threats.append(space)
        
        score += open_3_count * self.pattern_values['open_3']
        
        # Split 3s
        split_3_count = 0
        for pattern, space in self.patterns['split_3']:
            if (position & pattern) == pattern and (mask & space) == 0:
                split_3_count += 1
                threats.append(space)
        
        score += split_3_count * self.pattern_values['split_3']
        
        # Check for forks (multiple threats)
        unique_threats = len(set(threats))
        if unique_threats >= 2:
            score += self.pattern_values['fork'] * (unique_threats - 1)
        
        # Count potential patterns
        score += self._count_potential_patterns(position, mask)
        
        return score
    
    def _count_potential_patterns(self, position, mask):
        """Count patterns that could become threats"""
        score = 0
        opponent = position ^ mask
        
        # Check each 4-window
        for pattern_list in [self.patterns['horizontal_4'], 
                           self.patterns['vertical_4'],
                           self.patterns['diagonal_4_down'],
                           self.patterns['diagonal_4_up']]:
            for pattern in pattern_list:
                my_pieces = self.engine.popcount(position & pattern)
                opp_pieces = self.engine.popcount(opponent & pattern)
                empty = self.engine.popcount((~mask) & pattern)
                
                if opp_pieces == 0:
                    if my_pieces == 2 and empty == 2:
                        score += self.pattern_values['open_2']
                    elif my_pieces == 1 and empty == 3:
                        score += 1
        
        return score
    
    def _evaluate_positional(self, position, opponent, mask):
        """Evaluate positional features"""
        score = 0
        
        # Center control
        center_col = 3
        center_mask = 0
        for row in range(6):
            center_mask |= 1 << (center_col * 7 + row)
        
        my_center = self.engine.popcount(position & center_mask)
        opp_center = self.engine.popcount(opponent & center_mask)
        score += (my_center - opp_center) * self.pattern_values['center_control']
        
        # Adjacent columns
        for col in [2, 4]:
            col_mask = 0
            for row in range(6):
                col_mask |= 1 << (col * 7 + row)
            
            my_pieces = self.engine.popcount(position & col_mask)
            opp_pieces = self.engine.popcount(opponent & col_mask)
            score += (my_pieces - opp_pieces) * self.pattern_values['adjacent_center']
        
        # Height advantage (prefer lower positions)
        score += self._evaluate_height_advantage(position, opponent)
        
        return score
    
    def _evaluate_height_advantage(self, position, opponent):
        """Evaluate height advantage"""
        score = 0
        
        for col in range(7):
            my_height = 0
            opp_height = 0
            
            for row in range(6):
                bit = 1 << (col * 7 + row)
                if position & bit:
                    my_height = row + 1
                elif opponent & bit:
                    opp_height = row + 1
            
            # Lower pieces are more stable
            score += (6 - my_height) - (6 - opp_height)
        
        return score
    
    def find_critical_squares(self, position, mask):
        """Find squares that are critical for both players"""
        critical = []
        opponent = position ^ mask
        
        for col in range(7):
            if not self.engine.can_play(col, mask):
                continue
            
            # Find landing row
            row = -1
            for r in range(5, -1, -1):
                if (mask & (1 << (col * 7 + r))) == 0:
                    row = r
                    break
            
            if row == -1:
                continue
            
            square = 1 << (col * 7 + row)
            
            # Check if this square completes patterns
            my_value = self._evaluate_square_value(position | square, mask | square)
            opp_value = self._evaluate_square_value(opponent | square, mask | square)
            
            if my_value > 50 or opp_value > 50:
                critical.append({
                    'col': col,
                    'row': row,
                    'my_value': my_value,
                    'opp_value': opp_value,
                    'total_value': my_value + opp_value
                })
        
        # Sort by total value
        critical.sort(key=lambda x: x['total_value'], reverse=True)
        
        return critical
    
    def _evaluate_square_value(self, position, mask):
        """Evaluate value of a specific square"""
        # Simplified - check if it creates immediate threats
        threat_count = 0
        
        for col in range(7):
            if self.engine.can_play(col, mask):
                new_pos, new_mask = self.engine.play_move(col, position, mask)
                if self.engine.alignment(new_pos):
                    threat_count += 1
        
        return threat_count * 50
    
    def detect_zugzwang(self, position, mask):
        """Detect zugzwang positions (where any move worsens position)"""
        current_eval = self.evaluate_position(position, mask)
        
        worse_moves = 0
        total_moves = 0
        
        for col in range(7):
            if self.engine.can_play(col, mask):
                total_moves += 1
                new_pos, new_mask = self.engine.play_move(col, position, mask)
                new_eval = -self.evaluate_position(new_pos ^ new_mask, new_mask)
                
                if new_eval < current_eval - 20:
                    worse_moves += 1
        
        # Zugzwang if most moves worsen position
        return worse_moves > total_moves * 0.7

# Test pattern recognition
if __name__ == "__main__":
    pr = PatternRecognition()
    engine = BitboardEngine()
    
    # Test position with threats
    test_board = [0] * 42
    test_board[35] = 1  # Bottom row
    test_board[36] = 1
    test_board[37] = 1  # Three in a row
    
    pos, mask = engine.encode_position(test_board, 1)
    
    score = pr.evaluate_position(pos, mask)
    print(f"Position evaluation: {score}")
    
    critical = pr.find_critical_squares(pos, mask)
    print(f"\nCritical squares:")
    for sq in critical[:5]:
        print(f"  Column {sq['col']}: value {sq['total_value']}")
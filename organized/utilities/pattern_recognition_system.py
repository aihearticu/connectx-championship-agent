"""
Advanced Pattern Recognition System for Connect X
Identifies tactical patterns, threats, and strategic positions
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Set
from enum import Enum

class ThreatType(Enum):
    """Types of threats in Connect 4"""
    IMMEDIATE_WIN = 1000  # Can win next move
    FORK = 500           # Creates multiple threats
    FORCED_WIN = 300     # Win in forced sequence
    THREE_OPEN = 100     # Three in a row with both ends open
    THREE_SEMI = 50      # Three in a row with one end open
    TWO_OPEN = 20        # Two in a row with space
    POTENTIAL = 5        # Potential future threat

@dataclass
class Threat:
    """Represents a threat on the board"""
    threat_type: ThreatType
    positions: List[Tuple[int, int]]  # (row, col) positions
    winning_squares: Set[Tuple[int, int]]  # Squares that complete the threat
    player: int
    value: int

class PatternRecognition:
    """
    Advanced pattern recognition for Connect X
    Identifies complex tactical patterns and strategic positions
    """
    
    def __init__(self):
        self.WIDTH = 7
        self.HEIGHT = 6
        
        # Precompute all possible winning lines
        self._precompute_lines()
        
        # Pattern templates for quick matching
        self._init_patterns()
    
    def _precompute_lines(self):
        """Precompute all possible 4-in-a-row lines"""
        self.lines = []
        
        # Horizontal lines
        for row in range(self.HEIGHT):
            for col in range(self.WIDTH - 3):
                line = [(row, col + i) for i in range(4)]
                self.lines.append(line)
        
        # Vertical lines
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT - 3):
                line = [(row + i, col) for i in range(4)]
                self.lines.append(line)
        
        # Diagonal \ lines
        for row in range(self.HEIGHT - 3):
            for col in range(self.WIDTH - 3):
                line = [(row + i, col + i) for i in range(4)]
                self.lines.append(line)
        
        # Diagonal / lines
        for row in range(3, self.HEIGHT):
            for col in range(self.WIDTH - 3):
                line = [(row - i, col + i) for i in range(4)]
                self.lines.append(line)
    
    def _init_patterns(self):
        """Initialize pattern templates"""
        # Pattern: (player_count, opponent_count, empty_count) -> threat_type
        self.basic_patterns = {
            (3, 0, 1): ThreatType.THREE_SEMI,
            (2, 0, 2): ThreatType.TWO_OPEN,
            (1, 0, 3): ThreatType.POTENTIAL,
        }
        
        # Special patterns for open threats
        self.open_patterns = {
            'XXX_': ThreatType.THREE_SEMI,
            '_XXX': ThreatType.THREE_SEMI,
            'XX_X': ThreatType.THREE_SEMI,
            'X_XX': ThreatType.THREE_SEMI,
            '_XX_': ThreatType.TWO_OPEN,
            'X__X': ThreatType.TWO_OPEN,
        }
    
    def analyze_board(self, board, player):
        """
        Comprehensive board analysis
        Returns list of threats and strategic evaluation
        """
        threats = []
        opponent = 3 - player
        
        # Convert flat board to 2D for easier analysis
        board_2d = np.array(board).reshape(self.HEIGHT, self.WIDTH)
        
        # Analyze each line for threats
        for line in self.lines:
            line_values = [board_2d[r, c] for r, c in line]
            
            # Count pieces
            player_count = line_values.count(player)
            opp_count = line_values.count(opponent)
            empty_count = line_values.count(0)
            
            # Skip blocked lines
            if player_count > 0 and opp_count > 0:
                continue
            
            # Identify threat type
            if player_count == 3 and empty_count == 1:
                # Find the empty square
                for i, (r, c) in enumerate(line):
                    if board_2d[r, c] == 0:
                        # Check if it's playable (has support below)
                        if r == self.HEIGHT - 1 or board_2d[r + 1, c] != 0:
                            threat = Threat(
                                threat_type=ThreatType.IMMEDIATE_WIN,
                                positions=line,
                                winning_squares={(r, c)},
                                player=player,
                                value=ThreatType.IMMEDIATE_WIN.value
                            )
                            threats.append(threat)
                        else:
                            # It's a future threat
                            threat = Threat(
                                threat_type=ThreatType.THREE_SEMI,
                                positions=line,
                                winning_squares={(r, c)},
                                player=player,
                                value=ThreatType.THREE_SEMI.value
                            )
                            threats.append(threat)
            
            elif player_count == 2 and empty_count == 2:
                # Two with space - potential threat
                empty_squares = set()
                for r, c in line:
                    if board_2d[r, c] == 0:
                        empty_squares.add((r, c))
                
                threat = Threat(
                    threat_type=ThreatType.TWO_OPEN,
                    positions=line,
                    winning_squares=empty_squares,
                    player=player,
                    value=ThreatType.TWO_OPEN.value
                )
                threats.append(threat)
        
        # Detect forks (multiple winning threats)
        forks = self.detect_forks(board_2d, player)
        threats.extend(forks)
        
        # Detect zugzwang positions
        zugzwang = self.detect_zugzwang(board_2d, player)
        if zugzwang:
            threats.append(zugzwang)
        
        return threats
    
    def detect_forks(self, board_2d, player):
        """Detect fork opportunities (multiple threats)"""
        forks = []
        
        # Find all potential winning squares for player
        winning_squares = {}  # square -> list of threats
        
        for line in self.lines:
            line_values = [board_2d[r, c] for r, c in line]
            
            if line_values.count(player) == 2 and line_values.count(0) == 2:
                # This line could become a threat
                for r, c in line:
                    if board_2d[r, c] == 0:
                        if (r, c) not in winning_squares:
                            winning_squares[(r, c)] = []
                        winning_squares[(r, c)].append(line)
        
        # Find squares that create multiple threats
        for square, threat_lines in winning_squares.items():
            if len(threat_lines) >= 2:
                # This square creates a fork!
                r, c = square
                
                # Check if square is immediately playable
                if r == self.HEIGHT - 1 or board_2d[r + 1, c] != 0:
                    fork = Threat(
                        threat_type=ThreatType.FORK,
                        positions=sum(threat_lines, []),  # All positions involved
                        winning_squares={square},
                        player=player,
                        value=ThreatType.FORK.value * len(threat_lines)
                    )
                    forks.append(fork)
        
        return forks
    
    def detect_zugzwang(self, board_2d, player):
        """
        Detect zugzwang positions (odd/even parity)
        In Connect 4, controlling squares on odd rows gives first player advantage
        """
        # Count empty squares on each row
        odd_row_empties = 0
        even_row_empties = 0
        
        for row in range(self.HEIGHT):
            empties = np.sum(board_2d[row] == 0)
            if row % 2 == 0:  # Even row (0, 2, 4)
                even_row_empties += empties
            else:  # Odd row (1, 3, 5)
                odd_row_empties += empties
        
        # Determine who benefits from zugzwang
        total_pieces = np.sum(board_2d != 0)
        is_first_player = (total_pieces % 2 == 0 and player == 1) or (total_pieces % 2 == 1 and player == 2)
        
        if is_first_player and odd_row_empties > even_row_empties:
            # First player has zugzwang advantage
            return Threat(
                threat_type=ThreatType.FORCED_WIN,
                positions=[],
                winning_squares=set(),
                player=player,
                value=100 + (odd_row_empties - even_row_empties) * 10
            )
        elif not is_first_player and even_row_empties > odd_row_empties:
            # Second player has zugzwang advantage
            return Threat(
                threat_type=ThreatType.FORCED_WIN,
                positions=[],
                winning_squares=set(),
                player=player,
                value=100 + (even_row_empties - odd_row_empties) * 10
            )
        
        return None
    
    def evaluate_position(self, board, player):
        """
        Advanced position evaluation using pattern recognition
        Returns a score from player's perspective
        """
        my_threats = self.analyze_board(board, player)
        opp_threats = self.analyze_board(board, 3 - player)
        
        # Calculate threat scores
        my_score = sum(threat.value for threat in my_threats)
        opp_score = sum(threat.value for threat in opp_threats)
        
        # Special cases
        # Check for immediate wins
        my_wins = [t for t in my_threats if t.threat_type == ThreatType.IMMEDIATE_WIN]
        opp_wins = [t for t in opp_threats if t.threat_type == ThreatType.IMMEDIATE_WIN]
        
        if my_wins:
            return 100000  # We can win
        if opp_wins:
            if len(opp_wins) > 1:
                return -100000  # Opponent has unstoppable win
            else:
                return -50000  # Must block
        
        # Check for forks
        my_forks = [t for t in my_threats if t.threat_type == ThreatType.FORK]
        opp_forks = [t for t in opp_threats if t.threat_type == ThreatType.FORK]
        
        if my_forks and not opp_wins:
            return 50000  # We have a winning fork
        if opp_forks and not my_wins:
            return -25000  # Opponent has dangerous fork
        
        # Normal evaluation
        return my_score - opp_score
    
    def get_critical_squares(self, board, player):
        """
        Get squares that are critical for both players
        These should be prioritized in search
        """
        critical = set()
        
        threats = self.analyze_board(board, player)
        opp_threats = self.analyze_board(board, 3 - player)
        
        # Add all winning squares from high-value threats
        for threat in threats + opp_threats:
            if threat.value >= ThreatType.THREE_SEMI.value:
                critical.update(threat.winning_squares)
        
        return critical
    
    def suggest_move(self, board, player):
        """
        Suggest best move based on pattern analysis
        Returns (column, score, reason)
        """
        board_2d = np.array(board).reshape(self.HEIGHT, self.WIDTH)
        best_col = -1
        best_score = -float('inf')
        best_reason = ""
        
        for col in range(self.WIDTH):
            # Find landing row
            row = -1
            for r in range(self.HEIGHT - 1, -1, -1):
                if board_2d[r, col] == 0:
                    row = r
                    break
            
            if row == -1:
                continue  # Column full
            
            # Make temporary move
            board_2d[row, col] = player
            
            # Evaluate position
            score = self.evaluate_position(board_2d.flatten(), player)
            
            # Determine reason
            reason = "Strategic"
            if score >= 100000:
                reason = "Winning move!"
            elif score >= 50000:
                reason = "Creates winning fork"
            elif score >= 10000:
                reason = "Strong threat"
            elif score <= -50000:
                reason = "Blocks opponent win"
            elif score <= -25000:
                reason = "Blocks dangerous fork"
            
            if score > best_score:
                best_score = score
                best_col = col
                best_reason = reason
            
            # Undo move
            board_2d[row, col] = 0
        
        return best_col, best_score, best_reason


# Test the pattern recognition system
if __name__ == "__main__":
    print("Testing Pattern Recognition System...")
    
    recognizer = PatternRecognition()
    
    # Test 1: Fork detection
    print("\n1. FORK DETECTION TEST")
    board = [0] * 42
    board[35] = 1  # Bottom center
    board[36] = 1  # Next to it
    board[28] = 1  # Above-left
    
    threats = recognizer.analyze_board(board, 1)
    print(f"Found {len(threats)} threats")
    for threat in threats:
        print(f"  - {threat.threat_type.name}: value={threat.value}")
    
    # Test 2: Zugzwang detection
    print("\n2. ZUGZWANG TEST")
    board = [0] * 42
    # Fill some positions
    for i in range(35, 42):
        board[i] = 1 if i % 2 == 0 else 2
    
    threats = recognizer.analyze_board(board, 1)
    zugzwang = [t for t in threats if t.threat_type == ThreatType.FORCED_WIN]
    if zugzwang:
        print(f"Zugzwang detected: value={zugzwang[0].value}")
    
    # Test 3: Move suggestion
    print("\n3. MOVE SUGGESTION TEST")
    board = [0] * 42
    board[35] = 1
    board[36] = 1
    board[37] = 2
    board[38] = 2
    
    col, score, reason = recognizer.suggest_move(board, 1)
    print(f"Suggested move: Column {col}")
    print(f"Score: {score}")
    print(f"Reason: {reason}")
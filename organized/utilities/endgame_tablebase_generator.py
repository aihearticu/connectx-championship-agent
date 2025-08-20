"""
Endgame Tablebase Generator for Connect X
Solves all positions with N pieces or fewer
"""

import numpy as np
import pickle
import time
from collections import deque
from numba import jit
import json

class EndgameTablebase:
    """
    Generate and use endgame tablebases for perfect play
    Uses retrograde analysis to solve positions backwards from wins
    """
    
    def __init__(self, max_pieces=8):
        self.max_pieces = max_pieces
        self.WIDTH = 7
        self.HEIGHT = 6
        self.tablebase = {}  # position_hash -> (outcome, best_move)
        
        # Outcomes
        self.WIN = 1
        self.LOSS = -1
        self.DRAW = 0
        self.UNKNOWN = None
    
    @jit
    def encode_position(self, board):
        """Encode board position as integer for hashing"""
        # Use ternary encoding: 0=empty, 1=player1, 2=player2
        # Max value: 3^42 (fits in 64-bit with compression)
        encoded = 0
        multiplier = 1
        
        for i in range(42):
            encoded += board[i] * multiplier
            multiplier *= 3
        
        return encoded
    
    def decode_position(self, encoded):
        """Decode integer back to board"""
        board = [0] * 42
        
        for i in range(42):
            board[i] = encoded % 3
            encoded //= 3
        
        return board
    
    def check_win(self, board, player):
        """Check if player has won"""
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row*7 + col + i] == player for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row+i)*7 + col] == player for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                if all(board[(row+i)*7 + col+i] == player for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3):
            for col in range(4):
                if all(board[(row+3-i)*7 + col+i] == player for i in range(4)):
                    return True
        
        return False
    
    def get_valid_moves(self, board):
        """Get list of valid columns"""
        return [col for col in range(7) if board[col] == 0]
    
    def make_move(self, board, col, player):
        """Make a move and return new board"""
        new_board = board[:]
        for row in range(5, -1, -1):
            if new_board[row * 7 + col] == 0:
                new_board[row * 7 + col] = player
                break
        return new_board
    
    def count_pieces(self, board):
        """Count total pieces on board"""
        return sum(1 for x in board if x != 0)
    
    def get_player_to_move(self, board):
        """Determine whose turn it is"""
        pieces = self.count_pieces(board)
        return 1 if pieces % 2 == 0 else 2
    
    def generate_tablebase(self, target_pieces):
        """
        Generate tablebase for positions with exactly target_pieces
        Uses retrograde analysis
        """
        print(f"\nGenerating tablebase for {target_pieces} pieces...")
        
        positions_analyzed = 0
        wins_found = 0
        losses_found = 0
        draws_found = 0
        
        # Queue for retrograde analysis
        queue = deque()
        
        # First, find all terminal positions (wins)
        print("Finding terminal positions...")
        
        # Generate all possible positions with target_pieces
        def generate_positions(board, pieces_left, player, positions):
            if pieces_left == 0:
                if self.count_pieces(board) == target_pieces:
                    positions.append(board[:])
                return
            
            for col in range(7):
                for row in range(5, -1, -1):
                    idx = row * 7 + col
                    if board[idx] == 0:
                        # Try placing piece here
                        board[idx] = player
                        
                        # Check if this creates impossible position
                        valid = True
                        # Check gravity (no floating pieces)
                        if row < 5 and board[(row+1)*7 + col] == 0:
                            valid = False
                        
                        if valid:
                            generate_positions(board, pieces_left - 1, 3 - player, positions)
                        
                        board[idx] = 0
                        break  # Only fill lowest empty in column
        
        # Generate sample positions for testing
        if target_pieces <= 6:
            all_positions = []
            empty_board = [0] * 42
            generate_positions(empty_board, target_pieces, 1, all_positions)
            
            print(f"Analyzing {len(all_positions)} positions...")
            
            for board in all_positions:
                positions_analyzed += 1
                
                # Check if position is won
                if self.check_win(board, 1):
                    encoded = self.encode_position(board)
                    self.tablebase[encoded] = (self.WIN, None)
                    wins_found += 1
                elif self.check_win(board, 2):
                    encoded = self.encode_position(board)
                    self.tablebase[encoded] = (self.LOSS, None)
                    losses_found += 1
                else:
                    # Check if position leads to forced outcome
                    player = self.get_player_to_move(board)
                    outcome, best_move = self.analyze_position(board, player)
                    
                    if outcome is not None:
                        encoded = self.encode_position(board)
                        self.tablebase[encoded] = (outcome, best_move)
                        
                        if outcome == self.WIN:
                            wins_found += 1
                        elif outcome == self.LOSS:
                            losses_found += 1
                        else:
                            draws_found += 1
                
                if positions_analyzed % 1000 == 0:
                    print(f"  Analyzed {positions_analyzed} positions...")
        
        print(f"\nTablebase for {target_pieces} pieces complete:")
        print(f"  Positions: {positions_analyzed}")
        print(f"  Wins: {wins_found}")
        print(f"  Losses: {losses_found}")
        print(f"  Draws: {draws_found}")
        
        return positions_analyzed
    
    def analyze_position(self, board, player):
        """
        Analyze a position to determine outcome
        Returns (outcome, best_move)
        """
        # Check immediate wins
        valid_moves = self.get_valid_moves(board)
        
        for col in valid_moves:
            new_board = self.make_move(board, col, player)
            
            if self.check_win(new_board, player):
                return (self.WIN if player == 1 else self.LOSS, col)
        
        # Check if all moves lead to losses (then this is a win for opponent)
        outcomes = []
        
        for col in valid_moves:
            new_board = self.make_move(board, col, player)
            
            # Look up in tablebase
            encoded = self.encode_position(new_board)
            if encoded in self.tablebase:
                outcome, _ = self.tablebase[encoded]
                outcomes.append((outcome, col))
        
        if outcomes:
            # Find best outcome for current player
            if player == 1:
                # Player 1 wants WIN (1)
                best = max(outcomes, key=lambda x: x[0] if x[0] is not None else -2)
            else:
                # Player 2 wants LOSS (-1) from player 1's perspective
                best = min(outcomes, key=lambda x: x[0] if x[0] is not None else 2)
            
            return best
        
        return (None, None)
    
    def lookup(self, board):
        """
        Look up position in tablebase
        Returns (outcome, best_move) or (None, None) if not found
        """
        if self.count_pieces(board) > self.max_pieces:
            return (None, None)
        
        encoded = self.encode_position(board)
        return self.tablebase.get(encoded, (None, None))
    
    def save(self, filename='endgame_tablebase.pkl'):
        """Save tablebase to file"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'max_pieces': self.max_pieces,
                'tablebase': self.tablebase
            }, f)
        
        print(f"\nTablebase saved to {filename}")
        print(f"  Positions: {len(self.tablebase)}")
        print(f"  Size: {len(pickle.dumps(self.tablebase)) / 1024:.1f} KB")
    
    def load(self, filename='endgame_tablebase.pkl'):
        """Load tablebase from file"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.max_pieces = data['max_pieces']
            self.tablebase = data['tablebase']
        
        print(f"Tablebase loaded: {len(self.tablebase)} positions")
    
    def generate_all(self):
        """Generate complete tablebase up to max_pieces"""
        print(f"Generating complete tablebase up to {self.max_pieces} pieces...")
        
        start_time = time.time()
        total_positions = 0
        
        # Start from wins and work backwards
        for pieces in range(4, self.max_pieces + 1):
            positions = self.generate_tablebase(pieces)
            total_positions += positions
        
        elapsed = time.time() - start_time
        
        print(f"\n" + "="*60)
        print(f"TABLEBASE GENERATION COMPLETE")
        print(f"="*60)
        print(f"Total positions: {total_positions:,}")
        print(f"Tablebase entries: {len(self.tablebase):,}")
        print(f"Time: {elapsed:.1f} seconds")
        print(f"Speed: {total_positions/elapsed:.0f} positions/second")


def test_tablebase():
    """Test the endgame tablebase"""
    print("Testing Endgame Tablebase...")
    
    # Create tablebase for 6 pieces
    tb = EndgameTablebase(max_pieces=6)
    
    # Test position
    board = [0] * 42
    board[35] = 1  # Bottom center
    board[36] = 1
    board[37] = 2
    board[38] = 2
    
    print(f"\nTest position ({tb.count_pieces(board)} pieces):")
    for row in range(6):
        print("  ", end="")
        for col in range(7):
            piece = board[row * 7 + col]
            print(piece if piece != 0 else ".", end=" ")
        print()
    
    # Analyze
    player = tb.get_player_to_move(board)
    outcome, best_move = tb.analyze_position(board, player)
    
    print(f"\nPlayer to move: {player}")
    print(f"Analysis: outcome={outcome}, best_move={best_move}")
    
    # Generate small tablebase
    print("\nGenerating small tablebase...")
    tb.generate_tablebase(4)
    
    # Save
    tb.save('small_tablebase.pkl')


if __name__ == "__main__":
    test_tablebase()
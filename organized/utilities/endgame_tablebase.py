"""
Endgame Tablebase Generator
Creates perfect play database for endgame positions
"""

import pickle
import numpy as np
from bitboard_engine_v2 import BitboardEngine
from collections import deque

class EndgameTablebase:
    """Generate and query endgame tablebases"""
    
    def __init__(self):
        self.engine = BitboardEngine()
        self.tablebase = {}
        self.DTM = {}  # Distance to mate
        
    def generate_tablebase(self, max_pieces=8):
        """Generate tablebase for positions with N or fewer pieces"""
        print(f"Generating endgame tablebase for <= {max_pieces} pieces...")
        
        # Start with terminal positions (wins)
        self._find_terminal_positions()
        
        # Retrograde analysis
        self._retrograde_analysis(max_pieces)
        
        # Save tablebase
        self._save_tablebase()
        
        print(f"Tablebase complete with {len(self.tablebase)} positions")
    
    def _find_terminal_positions(self):
        """Find all winning positions"""
        print("Finding terminal positions...")
        
        # Generate all possible positions with 4-in-a-row
        # This is simplified - real implementation would be exhaustive
        
        # Iterate through all possible winning patterns
        winning_positions = []
        
        # Horizontal wins
        for row in range(6):
            for col in range(4):
                # Create winning position
                position = 0
                for i in range(4):
                    position |= 1 << ((col + i) * 7 + row)
                winning_positions.append(position)
        
        # Vertical wins
        for col in range(7):
            for row in range(3):
                position = 0
                for i in range(4):
                    position |= 1 << (col * 7 + row + i)
                winning_positions.append(position)
        
        # Diagonal wins - simplified
        # Real implementation would generate all possible
        
        # Mark all winning positions
        for pos in winning_positions:
            if self.engine.alignment(pos):
                # This is a win for the player
                self.tablebase[pos] = 'WIN'
                self.DTM[pos] = 0
    
    def _retrograde_analysis(self, max_pieces):
        """Work backwards from winning positions"""
        print("Performing retrograde analysis...")
        
        # Queue of positions to analyze
        queue = deque()
        
        # Add all known positions to queue
        for pos in self.tablebase:
            queue.append(pos)
        
        processed = set()
        
        while queue:
            position = queue.popleft()
            
            if position in processed:
                continue
            processed.add(position)
            
            # Get all positions that can lead to this position
            predecessors = self._get_predecessors(position)
            
            for pred_pos, pred_mask in predecessors:
                piece_count = self.engine.popcount(pred_mask)
                
                if piece_count > max_pieces:
                    continue
                
                # Analyze predecessor
                if pred_pos not in self.tablebase:
                    # Check if this is winning/losing/draw
                    result = self._analyze_position(pred_pos, pred_mask)
                    
                    if result != 'UNKNOWN':
                        self.tablebase[pred_pos] = result
                        if result in ['WIN', 'LOSS']:
                            self.DTM[pred_pos] = self.DTM.get(position, 0) + 1
                        queue.append(pred_pos)
    
    def _get_predecessors(self, position):
        """Get all positions that can lead to given position"""
        predecessors = []
        
        # For each possible last move
        for col in range(7):
            # Try to remove top piece from column
            col_mask = 0
            for row in range(6):
                col_mask |= 1 << (col * 7 + row)
            
            col_pieces = position & col_mask
            if col_pieces:
                # Find top piece
                top_piece = col_pieces & -col_pieces  # Isolate lowest bit
                # Remove it
                pred_pos = position ^ top_piece
                # Reconstruct mask (simplified)
                pred_mask = position | (position ^ (position - 1))
                predecessors.append((pred_pos, pred_mask))
        
        return predecessors
    
    def _analyze_position(self, position, mask):
        """Analyze a position to determine win/loss/draw"""
        # Check if position is winning
        if self.engine.alignment(position):
            return 'LOSS'  # Previous player lost
        
        # Check all possible moves
        can_win = False
        can_draw = False
        all_lose = True
        
        for col in range(7):
            if self.engine.can_play(col, mask):
                new_pos, new_mask = self.engine.play_move(col, position, mask)
                
                if new_pos in self.tablebase:
                    result = self.tablebase[new_pos]
                    if result == 'LOSS':
                        can_win = True
                        all_lose = False
                    elif result == 'DRAW':
                        can_draw = True
                        all_lose = False
                    elif result == 'WIN':
                        # Opponent wins after our move
                        pass
                else:
                    all_lose = False
        
        if can_win:
            return 'WIN'
        elif all_lose:
            return 'LOSS'
        elif can_draw:
            return 'DRAW'
        else:
            return 'UNKNOWN'
    
    def _save_tablebase(self):
        """Save tablebase to file"""
        data = {
            'tablebase': self.tablebase,
            'DTM': self.DTM
        }
        
        with open('endgame_tablebase.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved {len(self.tablebase)} positions to endgame_tablebase.pkl")
    
    def load_tablebase(self, filename='endgame_tablebase.pkl'):
        """Load tablebase from file"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        self.tablebase = data['tablebase']
        self.DTM = data['DTM']
    
    def probe(self, position, mask):
        """Look up position in tablebase"""
        # Normalize position (handle symmetries)
        normalized = self._normalize_position(position, mask)
        
        if normalized in self.tablebase:
            result = self.tablebase[normalized]
            dtm = self.DTM.get(normalized, None)
            return result, dtm
        
        return None, None
    
    def _normalize_position(self, position, mask):
        """Normalize position by considering symmetries"""
        # Check horizontal reflection
        mirrored_pos, mirrored_mask = self.engine.mirror_position(position, mask)
        
        # Return canonical form (smallest representation)
        if position < mirrored_pos:
            return position
        else:
            return mirrored_pos

class CompressedTablebase:
    """Compressed tablebase using advanced techniques"""
    
    def __init__(self):
        self.engine = BitboardEngine()
        self.index_map = {}
        self.data = None
        
    def build_index(self, positions):
        """Build index for position lookup"""
        print("Building compressed index...")
        
        # Sort positions by piece count and pattern
        sorted_positions = sorted(positions.items(), 
                                 key=lambda x: (self.engine.popcount(x[0]), x[0]))
        
        # Assign indices
        for idx, (pos, result) in enumerate(sorted_positions):
            self.index_map[pos] = idx
        
        # Create compressed data array
        # 2 bits per position: 00=unknown, 01=win, 10=loss, 11=draw
        num_positions = len(sorted_positions)
        self.data = np.zeros((num_positions + 3) // 4, dtype=np.uint8)
        
        result_map = {'WIN': 1, 'LOSS': 2, 'DRAW': 3}
        
        for idx, (pos, result) in enumerate(sorted_positions):
            if result in result_map:
                value = result_map[result]
                byte_idx = idx // 4
                bit_offset = (idx % 4) * 2
                self.data[byte_idx] |= value << bit_offset
        
        print(f"Compressed {num_positions} positions to {len(self.data)} bytes")
    
    def probe(self, position):
        """Look up position in compressed tablebase"""
        if position not in self.index_map:
            return None
        
        idx = self.index_map[position]
        byte_idx = idx // 4
        bit_offset = (idx % 4) * 2
        
        value = (self.data[byte_idx] >> bit_offset) & 0b11
        
        result_map = {0: None, 1: 'WIN', 2: 'LOSS', 3: 'DRAW'}
        return result_map[value]
    
    def save(self, filename):
        """Save compressed tablebase"""
        data = {
            'index_map': self.index_map,
            'data': self.data
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filename):
        """Load compressed tablebase"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        self.index_map = data['index_map']
        self.data = data['data']

# Generate sample tablebase
if __name__ == "__main__":
    # Generate tablebase
    tb = EndgameTablebase()
    tb.generate_tablebase(max_pieces=8)
    
    # Test compression
    compressed = CompressedTablebase()
    compressed.build_index(tb.tablebase)
    compressed.save('endgame_compressed.pkl')
    
    print("\nTablebase generation complete!")
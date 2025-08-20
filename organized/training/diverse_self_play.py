"""
Diverse Self-Play Generator
Creates varied games for robust opening book
"""

import numpy as np
import json
import time
from collections import defaultdict
import random
from numba import jit, types
import pickle

@jit(nopython=True)
def fast_check_win(board, row, col, mark):
    """Ultra-fast win detection"""
    # Horizontal
    count = 1
    c = col - 1
    while c >= 0 and board[row * 7 + c] == mark:
        count += 1
        c -= 1
    c = col + 1
    while c < 7 and board[row * 7 + c] == mark:
        count += 1
        c += 1
    if count >= 4:
        return True
    
    # Vertical
    count = 1
    r = row + 1
    while r < 6 and board[r * 7 + col] == mark:
        count += 1
        r += 1
    if count >= 4:
        return True
    
    # Diagonal \
    count = 1
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0 and board[r * 7 + c] == mark:
        count += 1
        r -= 1
        c -= 1
    r, c = row + 1, col + 1
    while r < 6 and c < 7 and board[r * 7 + c] == mark:
        count += 1
        r += 1
        c += 1
    if count >= 4:
        return True
    
    # Diagonal /
    count = 1
    r, c = row - 1, col + 1
    while r >= 0 and c < 7 and board[r * 7 + c] == mark:
        count += 1
        r -= 1
        c += 1
    r, c = row + 1, col - 1
    while r < 6 and c >= 0 and board[r * 7 + c] == mark:
        count += 1
        r += 1
        c -= 1
    if count >= 4:
        return True
    
    return False

@jit(nopython=True)
def evaluate_board_fast(board, player):
    """Fast board evaluation"""
    score = 0
    opp = 3 - player
    
    # Center column value
    for row in range(6):
        if board[row * 7 + 3] == player:
            score += 4 + (5 - row)
        elif board[row * 7 + 3] == opp:
            score -= 4 + (5 - row)
    
    # Adjacent columns
    for col in [2, 4]:
        for row in range(6):
            if board[row * 7 + col] == player:
                score += 2 + (5 - row) // 2
            elif board[row * 7 + col] == opp:
                score -= 2 + (5 - row) // 2
    
    return score

@jit(nopython=True)
def minimax_fast(board, depth, alpha, beta, maximizing, player):
    """Fast minimax for self-play"""
    # Get valid moves
    valid_moves = np.zeros(7, dtype=np.int32)
    valid_count = 0
    for col in range(7):
        if board[col] == 0:
            valid_moves[valid_count] = col
            valid_count += 1
    
    if valid_count == 0 or depth == 0:
        return evaluate_board_fast(board, player), -1
    
    best_col = valid_moves[0]
    
    if maximizing:
        max_eval = -99999
        
        for i in range(valid_count):
            col = valid_moves[i]
            
            # Make move
            row = -1
            for r in range(5, -1, -1):
                if board[r * 7 + col] == 0:
                    row = r
                    break
            
            if row >= 0:
                board[row * 7 + col] = player
                
                # Check win
                if fast_check_win(board, row, col, player):
                    board[row * 7 + col] = 0
                    return 10000, col
                
                eval_score, _ = minimax_fast(board, depth - 1, alpha, beta, False, player)
                board[row * 7 + col] = 0
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
        
        return max_eval, best_col
    
    else:
        min_eval = 99999
        
        for i in range(valid_count):
            col = valid_moves[i]
            
            # Make move
            row = -1
            for r in range(5, -1, -1):
                if board[r * 7 + col] == 0:
                    row = r
                    break
            
            if row >= 0:
                board[row * 7 + col] = 3 - player
                
                # Check win
                if fast_check_win(board, row, col, 3 - player):
                    board[row * 7 + col] = 0
                    return -10000, col
                
                eval_score, _ = minimax_fast(board, depth - 1, alpha, beta, True, player)
                board[row * 7 + col] = 0
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
        
        return min_eval, best_col

class DiverseSelfPlay:
    """Generate diverse self-play games"""
    
    def __init__(self):
        self.opening_book = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
        self.position_scores = {}  # Position -> average outcome
        
        # Different player styles for diversity
        self.styles = [
            {'name': 'aggressive', 'depth': 5, 'randomness': 0.1},
            {'name': 'defensive', 'depth': 6, 'randomness': 0.05},
            {'name': 'balanced', 'depth': 7, 'randomness': 0.15},
            {'name': 'random', 'depth': 3, 'randomness': 0.3},
            {'name': 'deep', 'depth': 8, 'randomness': 0.02},
        ]
    
    def get_diverse_move(self, board, player, style):
        """Get move with style-based diversity"""
        board_array = np.array(board, dtype=np.int32)
        
        # Random move with probability
        if random.random() < style['randomness']:
            valid = [c for c in range(7) if board[c] == 0]
            if valid:
                # Prefer center columns even in random
                weights = [4 - abs(c - 3) for c in valid]
                total = sum(weights)
                r = random.uniform(0, total)
                cumsum = 0
                for col, w in zip(valid, weights):
                    cumsum += w
                    if r <= cumsum:
                        return col
                return random.choice(valid)
        
        # Check immediate wins/blocks first
        for col in range(7):
            if board[col] == 0:
                row = -1
                for r in range(5, -1, -1):
                    if board[r * 7 + col] == 0:
                        row = r
                        break
                
                if row >= 0:
                    # Check win
                    board_array[row * 7 + col] = player
                    if fast_check_win(board_array, row, col, player):
                        return col
                    board_array[row * 7 + col] = 0
                    
                    # Check block
                    board_array[row * 7 + col] = 3 - player
                    if fast_check_win(board_array, row, col, 3 - player):
                        return col
                    board_array[row * 7 + col] = 0
        
        # Use minimax with style depth
        _, col = minimax_fast(board_array, style['depth'], -99999, 99999, True, player)
        
        if col == -1:
            # Fallback
            valid = [c for c in range(7) if board[c] == 0]
            return valid[0] if valid else 3
        
        return col
    
    def play_game(self, style1_idx, style2_idx):
        """Play one game between two styles"""
        style1 = self.styles[style1_idx]
        style2 = self.styles[style2_idx]
        
        board = [0] * 42
        moves = []
        current = 1
        
        for turn in range(42):
            style = style1 if current == 1 else style2
            move = self.get_diverse_move(board, current, style)
            moves.append(move)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = current
                    
                    # Check win
                    board_array = np.array(board, dtype=np.int32)
                    if fast_check_win(board_array, row, move, current):
                        return moves, current
                    break
            
            current = 3 - current
        
        return moves, 0  # Draw
    
    def generate_diverse_games(self, num_games=10000):
        """Generate games with style diversity"""
        print(f"Generating {num_games:,} diverse games...")
        
        start = time.time()
        games_data = []
        
        for game_num in range(num_games):
            # Select random styles
            style1 = random.randint(0, len(self.styles) - 1)
            style2 = random.randint(0, len(self.styles) - 1)
            
            moves, winner = self.play_game(style1, style2)
            
            games_data.append({
                'moves': moves,
                'winner': winner,
                'styles': (self.styles[style1]['name'], self.styles[style2]['name'])
            })
            
            # Update opening book
            for length in range(1, min(len(moves) + 1, 13)):
                position = tuple(moves[:length])
                self.opening_book[position]['total'] += 1
                
                if winner == 1:
                    self.opening_book[position]['wins'] += 1
                elif winner == 2:
                    self.opening_book[position]['losses'] += 1
                else:
                    self.opening_book[position]['draws'] += 1
            
            if (game_num + 1) % 1000 == 0:
                elapsed = time.time() - start
                rate = (game_num + 1) / elapsed
                print(f"  {game_num+1:,} games ({rate:.0f} games/sec)")
        
        elapsed = time.time() - start
        print(f"\nCompleted in {elapsed:.1f}s ({num_games/elapsed:.0f} games/sec)")
        
        # Analyze diversity
        self.analyze_diversity(games_data)
        
        return games_data
    
    def analyze_diversity(self, games_data):
        """Analyze game diversity"""
        print("\n" + "="*60)
        print("DIVERSITY ANALYSIS")
        print("="*60)
        
        # First move distribution
        first_moves = defaultdict(int)
        for game in games_data:
            if game['moves']:
                first_moves[game['moves'][0]] += 1
        
        print("\nFirst move distribution:")
        total = sum(first_moves.values())
        for col in range(7):
            count = first_moves[col]
            pct = count / total * 100 if total > 0 else 0
            print(f"  Column {col}: {count:,} ({pct:.1f}%)")
        
        # Unique openings (first 8 moves)
        unique_openings = set()
        for game in games_data:
            if len(game['moves']) >= 8:
                opening = tuple(game['moves'][:8])
                unique_openings.add(opening)
        
        print(f"\nUnique 8-move openings: {len(unique_openings):,}")
        
        # Win rate by style
        style_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0})
        for game in games_data:
            style1, style2 = game['styles']
            if game['winner'] == 1:
                style_stats[style1]['wins'] += 1
                style_stats[style2]['losses'] += 1
            elif game['winner'] == 2:
                style_stats[style1]['losses'] += 1
                style_stats[style2]['wins'] += 1
            else:
                style_stats[style1]['draws'] += 1
                style_stats[style2]['draws'] += 1
        
        print("\nPerformance by style:")
        for style, stats in style_stats.items():
            total = stats['wins'] + stats['losses'] + stats['draws']
            if total > 0:
                win_rate = stats['wins'] / total * 100
                print(f"  {style}: {win_rate:.1f}% win rate ({total} games)")
    
    def save_opening_book(self, filename='diverse_opening_book.json', min_games=20):
        """Save opening book to file"""
        filtered_book = {}
        
        for position, stats in self.opening_book.items():
            if stats['total'] >= min_games:
                win_rate = stats['wins'] / stats['total']
                score = (stats['wins'] - stats['losses']) / stats['total']
                
                filtered_book[str(position)] = {
                    'total': stats['total'],
                    'win_rate': win_rate,
                    'score': score,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'draws': stats['draws']
                }
        
        with open(filename, 'w') as f:
            json.dump(filtered_book, f, indent=2)
        
        print(f"\nSaved opening book: {len(filtered_book):,} positions")
        
        # Show top openings
        top_positions = sorted(
            filtered_book.items(),
            key=lambda x: (x[1]['total'], x[1]['score']),
            reverse=True
        )[:10]
        
        print("\nTop 10 most common positions:")
        for i, (pos_str, stats) in enumerate(top_positions, 1):
            print(f"  {i}. {pos_str[:20]}... - {stats['total']} games, "
                  f"{stats['win_rate']*100:.1f}% win rate")
    
    def save_games(self, games_data, filename='diverse_games.pkl'):
        """Save all game data"""
        with open(filename, 'wb') as f:
            pickle.dump(games_data, f)
        print(f"Saved {len(games_data):,} games to {filename}")


if __name__ == "__main__":
    print("="*60)
    print("DIVERSE SELF-PLAY GENERATOR")
    print("="*60)
    
    generator = DiverseSelfPlay()
    
    # Generate diverse games
    games = generator.generate_diverse_games(num_games=10000)
    
    # Save opening book
    generator.save_opening_book(min_games=20)
    
    # Save game data
    generator.save_games(games)
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
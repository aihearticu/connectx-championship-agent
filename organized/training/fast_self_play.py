"""
Fast Self-Play Generator using simplified evaluation
For rapid opening book generation
"""

import random
import json
from collections import defaultdict
import time

class FastSelfPlay:
    """Fast self-play for opening book generation"""
    
    def __init__(self):
        self.opening_book = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
        
    def fast_eval_agent(self, board, mark):
        """Very fast agent with good play"""
        
        # Quick win/block check
        for col in range(7):
            if board[col] == 0:
                # Check win
                test_board = board[:]
                for row in range(5, -1, -1):
                    if test_board[row * 7 + col] == 0:
                        test_board[row * 7 + col] = mark
                        if self.check_win_at(test_board, row, col, mark):
                            return col
                        test_board[row * 7 + col] = 0
                        break
                
                # Check block
                test_board = board[:]
                for row in range(5, -1, -1):
                    if test_board[row * 7 + col] == 0:
                        test_board[row * 7 + col] = 3 - mark
                        if self.check_win_at(test_board, row, col, 3 - mark):
                            return col
                        break
        
        # Prefer center with some randomness
        valid = [c for c in range(7) if board[c] == 0]
        if not valid:
            return 3
        
        # Weight center columns more
        weights = []
        for col in valid:
            weight = 4 - abs(col - 3)  # 4,3,2,1,1,2,3
            
            # Bonus for creating threats
            test_board = board[:]
            for row in range(5, -1, -1):
                if test_board[row * 7 + col] == 0:
                    test_board[row * 7 + col] = mark
                    # Count threats created
                    threats = 0
                    for c2 in range(7):
                        if c2 != col and test_board[c2] == 0:
                            for r2 in range(5, -1, -1):
                                if test_board[r2 * 7 + c2] == 0:
                                    test_board[r2 * 7 + c2] = mark
                                    if self.check_win_at(test_board, r2, c2, mark):
                                        threats += 1
                                    test_board[r2 * 7 + c2] = 0
                                    break
                    weight += threats * 2
                    break
            
            weights.append(weight)
        
        # Add randomness for diversity
        if random.random() < 0.2:  # 20% random
            return random.choice(valid)
        
        # Choose based on weights
        total = sum(weights)
        if total == 0:
            return random.choice(valid)
        
        r = random.uniform(0, total)
        cumsum = 0
        for col, weight in zip(valid, weights):
            cumsum += weight
            if r <= cumsum:
                return col
        
        return valid[-1]
    
    def check_win_at(self, board, row, col, mark):
        """Check if placing mark at row,col creates a win"""
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
    
    def play_game(self):
        """Play one fast game"""
        board = [0] * 42
        moves = []
        current = 1
        
        for turn in range(42):
            move = self.fast_eval_agent(board, current)
            moves.append(move)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = current
                    
                    if self.check_win_at(board, row, move, current):
                        return moves, current
                    break
            
            current = 3 - current
        
        return moves, 0  # Draw
    
    def generate_games(self, num_games=10000):
        """Generate many games quickly"""
        print(f"Generating {num_games:,} games...")
        
        start = time.time()
        
        for game_num in range(num_games):
            moves, winner = self.play_game()
            
            # Update opening book for all positions
            for length in range(1, min(len(moves) + 1, 13)):  # Up to 12 moves
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
                print(f"  {game_num+1:,} games completed ({rate:.0f} games/sec)")
        
        elapsed = time.time() - start
        print(f"\nCompleted {num_games:,} games in {elapsed:.1f}s")
        print(f"Speed: {num_games/elapsed:.0f} games/second")
        
        return self.opening_book
    
    def save_opening_book(self, min_games=20):
        """Save opening book to file"""
        # Filter positions with enough games
        filtered_book = {}
        
        for position, stats in self.opening_book.items():
            if stats['total'] >= min_games:
                win_rate = stats['wins'] / stats['total']
                filtered_book[str(position)] = {
                    'total': stats['total'],
                    'win_rate': win_rate,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'draws': stats['draws']
                }
        
        # Save to JSON
        with open('fast_opening_book.json', 'w') as f:
            json.dump(filtered_book, f, indent=2)
        
        print(f"\nSaved opening book with {len(filtered_book):,} positions")
        
        # Show top openings
        print("\nTop first moves by frequency:")
        first_moves = defaultdict(lambda: {'total': 0, 'wins': 0})
        
        for position, stats in self.opening_book.items():
            if len(position) == 1:
                first_moves[position[0]]['total'] = stats['total']
                first_moves[position[0]]['wins'] = stats['wins']
        
        for col in range(7):
            if col in first_moves:
                stats = first_moves[col]
                win_rate = stats['wins'] / stats['total'] * 100 if stats['total'] > 0 else 0
                print(f"  Column {col}: {stats['total']:,} games, {win_rate:.1f}% win rate")


if __name__ == "__main__":
    generator = FastSelfPlay()
    
    # Generate games
    opening_book = generator.generate_games(num_games=50000)
    
    # Save book
    generator.save_opening_book(min_games=50)
    
    print("\nDone! Opening book ready for use.")
"""
Ultra-fast self-play using numba JIT compilation
"""

import numpy as np
from numba import jit
import json
import time
from collections import defaultdict

@jit(nopython=True)
def check_win_fast(board, row, col, mark):
    """Ultra-fast win check with numba"""
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
def fast_agent(board, mark):
    """Ultra-fast agent with numba"""
    # Check wins and blocks
    for col in range(7):
        if board[col] == 0:
            # Find row
            row = -1
            for r in range(5, -1, -1):
                if board[r * 7 + col] == 0:
                    row = r
                    break
            
            if row >= 0:
                # Check win
                board[row * 7 + col] = mark
                if check_win_fast(board, row, col, mark):
                    board[row * 7 + col] = 0
                    return col
                board[row * 7 + col] = 0
                
                # Check block
                board[row * 7 + col] = 3 - mark
                if check_win_fast(board, row, col, 3 - mark):
                    board[row * 7 + col] = 0
                    return col
                board[row * 7 + col] = 0
    
    # Prefer center columns
    order = [3, 2, 4, 1, 5, 0, 6]
    for col in order:
        if board[col] == 0:
            return col
    
    return 3

@jit(nopython=True)
def play_game_fast():
    """Play one game with numba acceleration"""
    board = np.zeros(42, dtype=np.int32)
    moves = np.zeros(42, dtype=np.int32)
    current = 1
    
    for turn in range(42):
        move = fast_agent(board, current)
        moves[turn] = move
        
        # Make move
        for row in range(5, -1, -1):
            if board[row * 7 + move] == 0:
                board[row * 7 + move] = current
                
                if check_win_fast(board, row, move, current):
                    return moves[:turn+1], current
                break
        
        current = 3 - current
    
    return moves, 0

def generate_opening_book(num_games=10000):
    """Generate opening book quickly"""
    print(f"Generating {num_games:,} games with numba acceleration...")
    
    opening_book = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
    
    start = time.time()
    
    # Warm up JIT
    play_game_fast()
    
    for game_num in range(num_games):
        moves, winner = play_game_fast()
        
        # Convert to Python list
        moves = moves.tolist()
        
        # Update opening book
        for length in range(1, min(len(moves) + 1, 13)):
            position = tuple(moves[:length])
            opening_book[position]['total'] += 1
            
            if winner == 1:
                opening_book[position]['wins'] += 1
            elif winner == 2:
                opening_book[position]['losses'] += 1
            else:
                opening_book[position]['draws'] += 1
        
        if (game_num + 1) % 5000 == 0:
            elapsed = time.time() - start
            rate = (game_num + 1) / elapsed
            print(f"  {game_num+1:,} games ({rate:.0f} games/sec)")
    
    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.1f}s ({num_games/elapsed:.0f} games/sec)")
    
    # Save book
    filtered_book = {}
    for position, stats in opening_book.items():
        if stats['total'] >= 10:
            win_rate = stats['wins'] / stats['total']
            filtered_book[str(position)] = {
                'total': stats['total'],
                'win_rate': win_rate,
                'score': stats['wins'] - stats['losses']
            }
    
    with open('ultra_fast_opening_book.json', 'w') as f:
        json.dump(filtered_book, f)
    
    print(f"Saved {len(filtered_book):,} positions")
    
    # Show statistics
    print("\nFirst move statistics:")
    for col in range(7):
        key = (col,)
        if key in opening_book:
            stats = opening_book[key]
            wr = stats['wins'] / stats['total'] * 100
            print(f"  Column {col}: {stats['total']:,} games, {wr:.1f}% win rate")

if __name__ == "__main__":
    generate_opening_book(num_games=100000)
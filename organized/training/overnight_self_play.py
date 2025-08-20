"""
Overnight Self-Play Runner
Generates millions of games for opening book
"""

import time
import json
import pickle
import multiprocessing as mp
import numpy as np
from datetime import datetime
from collections import defaultdict

def minimax_player(board, mark, depth=5):
    """Simple minimax player for self-play"""
    
    def check_win(board, player):
        # Check horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row*7 + col + i] == player for i in range(4)):
                    return True
        
        # Check vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row+i)*7 + col] == player for i in range(4)):
                    return True
        
        # Check diagonals
        for row in range(3):
            for col in range(4):
                if all(board[(row+i)*7 + col+i] == player for i in range(4)):
                    return True
                if all(board[(row+3-i)*7 + col+i] == player for i in range(4)):
                    return True
        
        return False
    
    def evaluate(board, player):
        if check_win(board, player):
            return 10000
        if check_win(board, 3 - player):
            return -10000
        
        score = 0
        # Center preference
        for col in range(7):
            weight = 4 - abs(col - 3)
            for row in range(6):
                if board[row * 7 + col] == player:
                    score += weight * (6 - row)
                elif board[row * 7 + col] == 3 - player:
                    score -= weight * (6 - row)
        
        return score
    
    def minimax(board, depth, alpha, beta, maximizing, player):
        valid = [c for c in range(7) if board[c] == 0]
        
        if not valid or depth == 0:
            return evaluate(board, player), None
        
        # Order moves
        valid.sort(key=lambda x: abs(x - 3))
        
        best_move = valid[0]
        
        if maximizing:
            max_eval = -float('inf')
            for col in valid:
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = player
                        break
                
                if check_win(new_board, player):
                    return 10000, col
                
                eval_score, _ = minimax(new_board, depth-1, alpha, beta, False, player)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in valid:
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = 3 - player
                        break
                
                if check_win(new_board, 3 - player):
                    return -10000, col
                
                eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, player)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    # Add randomness for diversity
    if np.random.random() < 0.1:  # 10% random moves
        valid = [c for c in range(7) if board[c] == 0]
        if valid:
            weights = [4 - abs(c - 3) for c in valid]
            probs = np.array(weights) / sum(weights)
            return np.random.choice(valid, p=probs)
    
    _, move = minimax(board, depth, -float('inf'), float('inf'), True, mark)
    return move if move is not None else 3

def play_game(game_id, depth1=5, depth2=5):
    """Play a single game"""
    board = [0] * 42
    moves = []
    current = 1
    
    for turn in range(42):
        if current == 1:
            move = minimax_player(board, 1, depth1)
        else:
            move = minimax_player(board, 2, depth2)
        
        moves.append(move)
        
        # Make move
        for row in range(5, -1, -1):
            if board[row * 7 + move] == 0:
                board[row * 7 + move] = current
                
                # Check win
                if check_winner(board, row, move, current):
                    return {
                        'id': game_id,
                        'moves': moves,
                        'winner': current,
                        'length': turn + 1
                    }
                break
        
        current = 3 - current
    
    return {
        'id': game_id,
        'moves': moves,
        'winner': 0,
        'length': 42
    }

def check_winner(board, row, col, player):
    """Check if move at row,col wins for player"""
    # Horizontal
    count = 1
    c = col - 1
    while c >= 0 and board[row * 7 + c] == player:
        count += 1
        c -= 1
    c = col + 1
    while c < 7 and board[row * 7 + c] == player:
        count += 1
        c += 1
    if count >= 4:
        return True
    
    # Vertical
    count = 1
    r = row + 1
    while r < 6 and board[r * 7 + col] == player:
        count += 1
        r += 1
    if count >= 4:
        return True
    
    # Diagonal \
    count = 1
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0 and board[r * 7 + c] == player:
        count += 1
        r -= 1
        c -= 1
    r, c = row + 1, col + 1
    while r < 6 and c < 7 and board[r * 7 + c] == player:
        count += 1
        r += 1
        c += 1
    if count >= 4:
        return True
    
    # Diagonal /
    count = 1
    r, c = row - 1, col + 1
    while r >= 0 and c < 7 and board[r * 7 + c] == player:
        count += 1
        r -= 1
        c += 1
    r, c = row + 1, col - 1
    while r < 6 and c >= 0 and board[r * 7 + c] == player:
        count += 1
        r += 1
        c -= 1
    if count >= 4:
        return True
    
    return False

def worker_process(worker_id, num_games, result_queue):
    """Worker process for parallel game generation"""
    games = []
    
    # Vary depths for diversity
    depths = [(5, 5), (4, 6), (6, 4), (5, 6), (6, 5), (7, 7), (4, 4), (3, 5)]
    
    for i in range(num_games):
        depth1, depth2 = depths[i % len(depths)]
        game = play_game(worker_id * num_games + i, depth1, depth2)
        games.append(game)
        
        if (i + 1) % 100 == 0:
            result_queue.put(('progress', worker_id, i + 1))
    
    result_queue.put(('games', worker_id, games))

def generate_games_parallel(total_games=100000, num_workers=8):
    """Generate games in parallel"""
    print(f"\nGenerating {total_games:,} games using {num_workers} workers...")
    
    games_per_worker = total_games // num_workers
    result_queue = mp.Queue()
    
    # Start workers
    processes = []
    start_time = time.time()
    
    for i in range(num_workers):
        p = mp.Process(target=worker_process, args=(i, games_per_worker, result_queue))
        p.start()
        processes.append(p)
    
    # Collect results
    all_games = []
    workers_done = 0
    
    while workers_done < num_workers:
        msg_type, worker_id, data = result_queue.get()
        
        if msg_type == 'progress':
            print(f"Worker {worker_id}: {data}/{games_per_worker} games", end='\r')
        elif msg_type == 'games':
            all_games.extend(data)
            workers_done += 1
            print(f"\nWorker {worker_id} completed!")
    
    # Wait for all processes
    for p in processes:
        p.join()
    
    elapsed = time.time() - start_time
    print(f"\nGenerated {len(all_games):,} games in {elapsed:.1f}s")
    print(f"Speed: {len(all_games)/elapsed:.0f} games/second")
    
    return all_games

def build_opening_book(games, max_depth=12, min_games=10):
    """Build opening book from games"""
    print("\nBuilding opening book...")
    
    opening_book = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
    
    for game in games:
        moves = game['moves'][:max_depth]
        winner = game['winner']
        
        # Add all prefixes
        for length in range(1, min(len(moves) + 1, max_depth + 1)):
            position = tuple(moves[:length])
            opening_book[position]['total'] += 1
            
            if winner == 1:
                opening_book[position]['wins'] += 1
            elif winner == 2:
                opening_book[position]['losses'] += 1
            else:
                opening_book[position]['draws'] += 1
    
    # Filter by minimum games
    filtered_book = {}
    for position, stats in opening_book.items():
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
    
    print(f"Opening book: {len(filtered_book):,} positions")
    
    return filtered_book

def save_data(games, opening_book):
    """Save games and opening book"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save games
    games_file = f'self_play_games_{timestamp}.pkl'
    with open(games_file, 'wb') as f:
        pickle.dump(games, f)
    print(f"Saved games to {games_file}")
    
    # Save opening book
    book_file = f'opening_book_{timestamp}.json'
    with open(book_file, 'w') as f:
        json.dump(opening_book, f, indent=2)
    print(f"Saved opening book to {book_file}")
    
    # Also save as latest
    with open('latest_opening_book.json', 'w') as f:
        json.dump(opening_book, f, indent=2)
    print("Saved as latest_opening_book.json")

def main():
    """Main overnight runner"""
    print("="*70)
    print("OVERNIGHT SELF-PLAY RUNNER")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Phase 1: Generate initial batch
    print("\n📊 Phase 1: Initial batch (100k games)")
    games = generate_games_parallel(total_games=100000, num_workers=8)
    opening_book = build_opening_book(games)
    save_data(games, opening_book)
    
    # Phase 2: Generate large batch
    print("\n📊 Phase 2: Large batch (500k games)")
    games = generate_games_parallel(total_games=500000, num_workers=8)
    opening_book = build_opening_book(games)
    save_data(games, opening_book)
    
    # Phase 3: Mega batch (if time permits)
    print("\n📊 Phase 3: Mega batch (1M games)")
    games = generate_games_parallel(total_games=1000000, num_workers=8)
    opening_book = build_opening_book(games)
    save_data(games, opening_book)
    
    print("\n" + "="*70)
    print("OVERNIGHT GENERATION COMPLETE")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

if __name__ == "__main__":
    main()
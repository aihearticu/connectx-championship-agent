"""
Self-Play Game Generator for Connect X
Generates millions of games for opening book and training data
"""

import multiprocessing as mp
import numpy as np
import pickle
import time
import os
from collections import defaultdict
from datetime import datetime
import json

class SelfPlayEngine:
    """
    High-performance self-play engine for data generation
    - Parallel game generation
    - Progressive opening book building
    - Position evaluation and scoring
    """
    
    def __init__(self, search_depth=9, num_workers=None):
        self.search_depth = search_depth
        self.num_workers = num_workers or mp.cpu_count()
        
        # Statistics
        self.games_played = 0
        self.positions_evaluated = 0
        self.opening_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0})
        
        # Game outcomes by first move
        self.first_move_stats = {i: {'wins': 0, 'losses': 0, 'draws': 0} 
                                 for i in range(7)}
        
        print(f"Self-Play Engine initialized with {self.num_workers} workers")
    
    def minimax_agent(self, board, mark, depth=None):
        """Simple but strong minimax agent for self-play"""
        if depth is None:
            depth = self.search_depth
        
        def check_win(board, mark):
            # Check horizontal
            for row in range(6):
                for col in range(4):
                    if all(board[row*7 + col + i] == mark for i in range(4)):
                        return True
            
            # Check vertical
            for col in range(7):
                for row in range(3):
                    if all(board[(row+i)*7 + col] == mark for i in range(4)):
                        return True
            
            # Check diagonal \
            for row in range(3):
                for col in range(4):
                    if all(board[(row+i)*7 + col+i] == mark for i in range(4)):
                        return True
            
            # Check diagonal /
            for row in range(3):
                for col in range(4):
                    if all(board[(row+3-i)*7 + col+i] == mark for i in range(4)):
                        return True
            
            return False
        
        def evaluate(board, mark):
            """Fast evaluation function"""
            if check_win(board, mark):
                return 10000
            if check_win(board, 3 - mark):
                return -10000
            
            score = 0
            
            # Center column preference
            for row in range(6):
                if board[row * 7 + 3] == mark:
                    score += 3
                elif board[row * 7 + 3] == 3 - mark:
                    score -= 3
            
            # Pattern evaluation
            for row in range(6):
                for col in range(4):
                    window = [board[row*7 + col + i] for i in range(4)]
                    score += self.evaluate_window(window, mark)
            
            for col in range(7):
                for row in range(3):
                    window = [board[(row+i)*7 + col] for i in range(4)]
                    score += self.evaluate_window(window, mark)
            
            return score
        
        def minimax(board, depth, alpha, beta, maximizing, mark):
            # Get valid moves
            valid_moves = [c for c in range(7) if board[c] == 0]
            
            if not valid_moves or depth == 0:
                return evaluate(board, mark), None
            
            # Order moves (center first)
            valid_moves.sort(key=lambda x: abs(x - 3))
            
            best_move = valid_moves[0]
            
            if maximizing:
                max_eval = -float('inf')
                for col in valid_moves:
                    # Make move
                    new_board = board[:]
                    for row in range(5, -1, -1):
                        if new_board[row * 7 + col] == 0:
                            new_board[row * 7 + col] = mark
                            break
                    
                    # Check for immediate win
                    if check_win(new_board, mark):
                        return 10000, col
                    
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, False, mark)
                    
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = col
                    
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
                
                return max_eval, best_move
            else:
                min_eval = float('inf')
                for col in valid_moves:
                    # Make move
                    new_board = board[:]
                    for row in range(5, -1, -1):
                        if new_board[row * 7 + col] == 0:
                            new_board[row * 7 + col] = 3 - mark
                            break
                    
                    # Check for immediate loss
                    if check_win(new_board, 3 - mark):
                        return -10000, col
                    
                    eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, mark)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = col
                    
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
                
                return min_eval, best_move
        
        _, move = minimax(board, depth, -float('inf'), float('inf'), True, mark)
        return move if move is not None else 3
    
    def evaluate_window(self, window, mark):
        """Evaluate a 4-piece window"""
        my_count = window.count(mark)
        opp_count = window.count(3 - mark)
        empty = window.count(0)
        
        if my_count == 3 and empty == 1:
            return 50
        elif my_count == 2 and empty == 2:
            return 10
        elif my_count == 1 and empty == 3:
            return 1
        elif opp_count == 3 and empty == 1:
            return -50
        elif opp_count == 2 and empty == 2:
            return -10
        
        return 0
    
    def play_game(self, game_id=0, explore_prob=0.1):
        """Play a single self-play game"""
        board = [0] * 42
        moves = []
        current_player = 1
        
        for turn in range(42):
            # Add exploration for diversity
            if np.random.random() < explore_prob and turn < 10:
                # Random move with center bias
                valid = [c for c in range(7) if board[c] == 0]
                weights = [1.0 + (3 - abs(c - 3)) * 0.5 for c in valid]
                weights = np.array(weights) / sum(weights)
                move = np.random.choice(valid, p=weights)
            else:
                # Use minimax
                move = self.minimax_agent(board, current_player)
            
            moves.append(move)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = current_player
                    
                    # Check win
                    if self.check_winner(board, row, move, current_player):
                        return {
                            'game_id': game_id,
                            'moves': moves,
                            'winner': current_player,
                            'length': turn + 1
                        }
                    break
            
            current_player = 3 - current_player
        
        return {
            'game_id': game_id,
            'moves': moves,
            'winner': 0,  # Draw
            'length': 42
        }
    
    def check_winner(self, board, row, col, player):
        """Check if the last move created a win"""
        # Horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and board[row * 7 + c] == player:
            count += 1
            c -= 1
        # Check right
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
    
    def worker_process(self, worker_id, num_games, result_queue):
        """Worker process for parallel game generation"""
        games = []
        
        for i in range(num_games):
            game = self.play_game(
                game_id=worker_id * num_games + i,
                explore_prob=0.1 if i % 10 == 0 else 0.05  # More exploration every 10th game
            )
            games.append(game)
            
            if (i + 1) % 100 == 0:
                result_queue.put(('progress', worker_id, i + 1))
        
        result_queue.put(('games', worker_id, games))
    
    def generate_games(self, total_games=10000):
        """Generate games in parallel"""
        print(f"\nGenerating {total_games:,} self-play games...")
        print(f"Using {self.num_workers} workers")
        
        games_per_worker = total_games // self.num_workers
        remainder = total_games % self.num_workers
        
        # Create result queue
        result_queue = mp.Queue()
        
        # Start worker processes
        processes = []
        start_time = time.time()
        
        for i in range(self.num_workers):
            games_to_play = games_per_worker + (1 if i < remainder else 0)
            p = mp.Process(
                target=self.worker_process,
                args=(i, games_to_play, result_queue)
            )
            p.start()
            processes.append(p)
        
        # Collect results
        all_games = []
        workers_done = 0
        
        while workers_done < self.num_workers:
            msg_type, worker_id, data = result_queue.get()
            
            if msg_type == 'progress':
                # Progress update
                total_progress = sum(games_per_worker * workers_done for _ in range(workers_done))
                print(f"Worker {worker_id}: {data}/{games_per_worker} games", end='\r')
            
            elif msg_type == 'games':
                # Worker finished
                all_games.extend(data)
                workers_done += 1
                print(f"\nWorker {worker_id} finished!")
        
        # Wait for all processes
        for p in processes:
            p.join()
        
        elapsed = time.time() - start_time
        games_per_second = total_games / elapsed
        
        print(f"\nGenerated {len(all_games):,} games in {elapsed:.1f}s")
        print(f"Speed: {games_per_second:.0f} games/second")
        
        # Analyze games
        self.analyze_games(all_games)
        
        return all_games
    
    def analyze_games(self, games):
        """Analyze game statistics"""
        print("\n" + "="*60)
        print("GAME ANALYSIS")
        print("="*60)
        
        # Overall statistics
        total = len(games)
        p1_wins = sum(1 for g in games if g['winner'] == 1)
        p2_wins = sum(1 for g in games if g['winner'] == 2)
        draws = sum(1 for g in games if g['winner'] == 0)
        
        print(f"\nTotal games: {total:,}")
        print(f"Player 1 wins: {p1_wins:,} ({p1_wins/total*100:.1f}%)")
        print(f"Player 2 wins: {p2_wins:,} ({p2_wins/total*100:.1f}%)")
        print(f"Draws: {draws:,} ({draws/total*100:.1f}%)")
        
        # Game length statistics
        lengths = [g['length'] for g in games]
        print(f"\nAverage game length: {np.mean(lengths):.1f} moves")
        print(f"Shortest game: {min(lengths)} moves")
        print(f"Longest game: {max(lengths)} moves")
        
        # First move analysis
        first_moves = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0})
        
        for game in games:
            if game['moves']:
                first_move = game['moves'][0]
                if game['winner'] == 1:
                    first_moves[first_move]['wins'] += 1
                elif game['winner'] == 2:
                    first_moves[first_move]['losses'] += 1
                else:
                    first_moves[first_move]['draws'] += 1
        
        print("\nFirst move statistics (Player 1):")
        for col in range(7):
            stats = first_moves[col]
            total_col = stats['wins'] + stats['losses'] + stats['draws']
            if total_col > 0:
                win_rate = stats['wins'] / total_col * 100
                print(f"  Column {col}: {total_col:5} games, {win_rate:5.1f}% win rate")
        
        # Opening sequences (first 8 moves)
        openings = defaultdict(lambda: {'count': 0, 'p1_wins': 0, 'p2_wins': 0})
        
        for game in games:
            if len(game['moves']) >= 8:
                opening = tuple(game['moves'][:8])
                openings[opening]['count'] += 1
                if game['winner'] == 1:
                    openings[opening]['p1_wins'] += 1
                elif game['winner'] == 2:
                    openings[opening]['p2_wins'] += 1
        
        # Top 10 most common openings
        sorted_openings = sorted(openings.items(), 
                                key=lambda x: x[1]['count'], 
                                reverse=True)
        
        print("\nTop 10 most common opening sequences:")
        for i, (opening, stats) in enumerate(sorted_openings[:10]):
            win_rate = stats['p1_wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
            print(f"  {i+1}. {opening[:4]}... ({stats['count']} games, {win_rate:.1f}% P1 win)")
    
    def save_games(self, games, filename="self_play_games.pkl"):
        """Save games to file"""
        with open(filename, 'wb') as f:
            pickle.dump(games, f)
        print(f"\nSaved {len(games):,} games to {filename}")
    
    def save_opening_book(self, games, min_games=10, max_depth=12):
        """Extract and save opening book from games"""
        openings = defaultdict(lambda: {'count': 0, 'scores': []})
        
        for game in games:
            moves = game['moves'][:max_depth]
            
            # Track all prefixes
            for length in range(1, min(len(moves) + 1, max_depth + 1)):
                position = tuple(moves[:length])
                openings[position]['count'] += 1
                
                # Score: 1 for P1 win, 0 for draw, -1 for P2 win
                if game['winner'] == 1:
                    openings[position]['scores'].append(1)
                elif game['winner'] == 2:
                    openings[position]['scores'].append(-1)
                else:
                    openings[position]['scores'].append(0)
        
        # Filter and compute statistics
        book = {}
        for position, data in openings.items():
            if data['count'] >= min_games:
                scores = data['scores']
                book[position] = {
                    'count': data['count'],
                    'score': np.mean(scores),
                    'std': np.std(scores),
                    'win_rate': sum(1 for s in scores if s > 0) / len(scores)
                }
        
        # Save as JSON for readability
        # Convert tuples to lists for JSON serialization
        json_book = {str(k): v for k, v in book.items()}
        
        with open('opening_book.json', 'w') as f:
            json.dump(json_book, f, indent=2)
        
        print(f"\nSaved opening book with {len(book):,} positions")
        print(f"Positions with {min_games}+ games, up to depth {max_depth}")
        
        return book


# Main execution
if __name__ == "__main__":
    print("="*60)
    print("CONNECT X SELF-PLAY GENERATOR")
    print("="*60)
    
    # Create engine
    engine = SelfPlayEngine(search_depth=7, num_workers=8)
    
    # Generate games
    games = engine.generate_games(total_games=1000)
    
    # Save games
    engine.save_games(games)
    
    # Create opening book
    opening_book = engine.save_opening_book(games, min_games=5, max_depth=10)
    
    print("\n" + "="*60)
    print("SELF-PLAY GENERATION COMPLETE")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PST')}")
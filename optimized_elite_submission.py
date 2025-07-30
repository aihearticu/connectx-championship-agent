"""
Optimized Elite Connect X Agent - Targeting Top 3 Performance
Fast, efficient implementation with strategic depth
"""

import random
import math
import time

# Constants
WIN_SCORE = 100000
FOUR_SCORE = 5000
THREE_SCORE = 100
TWO_SCORE = 10

# Cache for transposition table
cache = {}

# Optimized opening book
OPENING_BOOK = {
    (): 3,
    (3,): 3,
    (3, 3): 2,
    (3, 2): 3,
    (3, 4): 3,
    (3, 3, 2): 4,
    (3, 3, 4): 2,
    (3, 2, 3): 4,
    (3, 4, 3): 2,
}

def agent(observation, configuration):
    """Main agent function - optimized for speed and performance"""
    global cache
    
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    my_mark = observation.mark
    
    # Clear cache if too large
    if len(cache) > 50000:
        cache.clear()
    
    # Quick opening book check
    moves = []
    for col in range(columns):
        for row in range(rows-1, -1, -1):
            if board[row * columns + col] != 0:
                moves.append(col)
                break
    
    if len(moves) < 8 and tuple(moves) in OPENING_BOOK:
        move = OPENING_BOOK[tuple(moves)]
        if board[move] == 0:
            return move
    
    # Get valid moves
    valid_moves = [col for col in range(columns) if board[col] == 0]
    if not valid_moves:
        return 3
    
    # Quick win/block check
    for col in valid_moves:
        # Check if we can win
        if check_move_wins(board, col, my_mark, rows, columns, configuration.inarow):
            return col
    
    for col in valid_moves:
        # Check if we need to block
        if check_move_wins(board, col, 3 - my_mark, rows, columns, configuration.inarow):
            return col
    
    # Use iterative deepening minimax
    best_move = valid_moves[len(valid_moves)//2]  # Default to center
    start_time = time.time()
    
    # Determine depth based on game phase
    move_count = sum(1 for x in board if x != 0)
    if move_count < 8:
        max_depth = 5
    elif move_count < 20:
        max_depth = 6
    else:
        max_depth = 7
    
    # Iterative deepening
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > 0.8:  # Time limit
            break
        
        alpha = -float('inf')
        beta = float('inf')
        
        # Order moves by promise (center first)
        center = columns // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        best_score = -float('inf')
        
        for col in valid_moves:
            new_board = make_move(board, col, my_mark, rows, columns)
            score = -minimax(new_board, depth-1, -beta, -alpha, 3-my_mark, rows, columns, configuration.inarow, start_time)
            
            if score > best_score:
                best_score = score
                best_move = col
            
            alpha = max(alpha, score)
            
            if time.time() - start_time > 0.85:
                break
    
    return best_move

def check_move_wins(board, col, mark, rows, columns, inarow):
    """Fast check if a move wins"""
    # Find landing row
    row = -1
    for r in range(rows-1, -1, -1):
        if board[r * columns + col] == 0:
            row = r
            break
    
    if row == -1:
        return False
    
    # Check all directions from this position
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        
        # Check positive direction
        r, c = row + dr, col + dc
        while 0 <= r < rows and 0 <= c < columns and board[r * columns + c] == mark:
            count += 1
            r += dr
            c += dc
        
        # Check negative direction
        r, c = row - dr, col - dc
        while 0 <= r < rows and 0 <= c < columns and board[r * columns + c] == mark:
            count += 1
            r -= dr
            c -= dc
        
        if count >= inarow:
            return True
    
    return False

def make_move(board, col, mark, rows, columns):
    """Make a move and return new board state"""
    new_board = list(board)
    for row in range(rows-1, -1, -1):
        if new_board[row * columns + col] == 0:
            new_board[row * columns + col] = mark
            break
    return tuple(new_board)

def minimax(board, depth, alpha, beta, mark, rows, columns, inarow, start_time):
    """Optimized minimax with alpha-beta pruning"""
    # Time check
    if time.time() - start_time > 0.85:
        return 0
    
    # Check cache
    if board in cache:
        cached_depth, cached_score = cache[board]
        if cached_depth >= depth:
            return cached_score
    
    # Terminal check
    score = evaluate_board(board, mark, rows, columns, inarow)
    if abs(score) > 50000 or depth == 0:
        return score
    
    valid_moves = [col for col in range(columns) if board[col] == 0]
    if not valid_moves:
        return 0
    
    # Move ordering
    center = columns // 2
    valid_moves.sort(key=lambda x: abs(x - center))
    
    best_score = -float('inf')
    
    for col in valid_moves:
        new_board = make_move(board, col, mark, rows, columns)
        score = -minimax(new_board, depth-1, -beta, -alpha, 3-mark, rows, columns, inarow, start_time)
        
        best_score = max(best_score, score)
        alpha = max(alpha, score)
        
        if alpha >= beta:
            break
    
    # Cache result
    cache[board] = (depth, best_score)
    
    return best_score

def evaluate_board(board, mark, rows, columns, inarow):
    """Fast board evaluation"""
    score = 0
    opponent = 3 - mark
    
    # Center column bonus
    center_col = columns // 2
    for row in range(rows):
        if board[row * columns + center_col] == mark:
            score += 3
        elif board[row * columns + center_col] == opponent:
            score -= 3
    
    # Evaluate all windows
    # Horizontal
    for row in range(rows):
        for col in range(columns - inarow + 1):
            window = [board[row * columns + col + i] for i in range(inarow)]
            score += evaluate_window(window, mark)
    
    # Vertical
    for col in range(columns):
        for row in range(rows - inarow + 1):
            window = [board[(row + i) * columns + col] for i in range(inarow)]
            score += evaluate_window(window, mark)
    
    # Positive diagonal
    for row in range(rows - inarow + 1):
        for col in range(columns - inarow + 1):
            window = [board[(row + i) * columns + (col + i)] for i in range(inarow)]
            score += evaluate_window(window, mark)
    
    # Negative diagonal
    for row in range(inarow - 1, rows):
        for col in range(columns - inarow + 1):
            window = [board[(row - i) * columns + (col + i)] for i in range(inarow)]
            score += evaluate_window(window, mark)
    
    return score

def evaluate_window(window, mark):
    """Evaluate a single window"""
    opponent = 3 - mark
    mark_count = window.count(mark)
    opp_count = window.count(opponent)
    empty_count = window.count(0)
    
    if mark_count == 4:
        return WIN_SCORE
    elif mark_count == 3 and empty_count == 1:
        return THREE_SCORE
    elif mark_count == 2 and empty_count == 2:
        return TWO_SCORE
    
    if opp_count == 4:
        return -WIN_SCORE
    elif opp_count == 3 and empty_count == 1:
        return -THREE_SCORE + 10  # Slightly favor blocking
    elif opp_count == 2 and empty_count == 2:
        return -TWO_SCORE
    
    return 0
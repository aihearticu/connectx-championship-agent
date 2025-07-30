"""
Elite Connect X Agent - Targeting Top 3 Performance
Combines advanced minimax, MCTS, pattern recognition, and strategic play
"""

import random
import math
import time
from collections import defaultdict

# Constants for evaluation
WIN_SCORE = 1000000
DRAW_SCORE = 0
LOSS_SCORE = -1000000

# Transposition table for memoization
transposition_table = {}

# Opening book based on optimal play analysis
OPENING_BOOK = {
    (): 3,  # Start center
    (3,): 3,  # Double center if possible
    (3, 3): 2,  # If center taken twice, go left-center
    (3, 2): 3,  # Continue center
    (3, 4): 3,  # Continue center
    (3, 3, 2): 4,  # Common trap setup
    (3, 3, 4): 2,  # Mirror response
    (3, 2, 3): 4,  # Strategic development
    (3, 4, 3): 2,  # Mirror strategic development
    # Extended opening sequences
    (3, 3, 2, 4): 3,
    (3, 3, 4, 2): 3,
    (3, 2, 3, 4, 3): 1,
    (3, 4, 3, 2, 3): 5,
}

def agent(observation, configuration):
    """Main agent function combining multiple strategies"""
    board = observation.board
    columns = configuration.columns
    rows = configuration.rows
    inarow = configuration.inarow
    my_mark = observation.mark
    
    # Convert board to 2D array for easier processing
    board_2d = [[board[row * columns + col] for col in range(columns)] for row in range(rows)]
    
    # Check opening book
    move_history = get_move_history(board, columns, rows)
    if len(move_history) < 10:  # Use opening book for first 10 moves
        opening_move = check_opening_book(move_history)
        if opening_move is not None and is_valid_move(board_2d, opening_move):
            return opening_move
    
    # Get valid moves
    valid_moves = get_valid_moves(board_2d)
    if not valid_moves:
        return 3  # Default center
    
    # Check for immediate wins or blocks
    for move in valid_moves:
        if is_winning_move(board_2d, move, my_mark, inarow):
            return move
    
    for move in valid_moves:
        if is_winning_move(board_2d, move, 3 - my_mark, inarow):
            return move
    
    # Time management
    start_time = time.time()
    time_limit = 0.9  # Use 90% of available time
    
    # Choose algorithm based on game phase
    move_count = sum(1 for cell in board if cell != 0)
    
    if move_count < 10:
        # Early game - use minimax with moderate depth
        best_move = minimax_search(board_2d, my_mark, inarow, depth=5, time_limit=time_limit, start_time=start_time)
    elif move_count < 25:
        # Mid game - use MCTS for strategic play
        best_move = mcts_search(board_2d, my_mark, inarow, time_limit=time_limit, start_time=start_time)
    else:
        # End game - deep minimax search
        best_move = minimax_search(board_2d, my_mark, inarow, depth=7, time_limit=time_limit, start_time=start_time)
    
    # Fallback to center-biased selection if timeout
    if best_move is None:
        center = columns // 2
        for offset in range(columns):
            col = center + (offset // 2) * (1 if offset % 2 == 0 else -1)
            if col in valid_moves:
                return col
        return valid_moves[0]
    
    return best_move

def get_move_history(board, columns, rows):
    """Extract move history from board state"""
    moves = []
    # Reconstruct move order (approximate)
    for col in range(columns):
        for row in range(rows - 1, -1, -1):
            if board[row * columns + col] != 0:
                moves.append(col)
    return tuple(moves[:10])  # Only use first 10 moves for opening book

def check_opening_book(move_history):
    """Check if current position is in opening book"""
    if move_history in OPENING_BOOK:
        return OPENING_BOOK[move_history]
    return None

def is_valid_move(board, col):
    """Check if a column is playable"""
    return board[0][col] == 0

def get_valid_moves(board):
    """Get all valid columns"""
    return [col for col in range(len(board[0])) if is_valid_move(board, col)]

def make_move(board, col, mark):
    """Make a move on the board (returns new board)"""
    new_board = [row[:] for row in board]
    for row in range(len(board) - 1, -1, -1):
        if new_board[row][col] == 0:
            new_board[row][col] = mark
            break
    return new_board

def is_winning_move(board, col, mark, inarow):
    """Check if a move wins the game"""
    test_board = make_move(board, col, mark)
    return check_win(test_board, mark, inarow)

def check_win(board, mark, inarow):
    """Check if the given mark has won"""
    rows = len(board)
    cols = len(board[0])
    
    # Horizontal
    for row in range(rows):
        for col in range(cols - inarow + 1):
            if all(board[row][col + i] == mark for i in range(inarow)):
                return True
    
    # Vertical
    for col in range(cols):
        for row in range(rows - inarow + 1):
            if all(board[row + i][col] == mark for i in range(inarow)):
                return True
    
    # Diagonal (positive slope)
    for row in range(rows - inarow + 1):
        for col in range(cols - inarow + 1):
            if all(board[row + i][col + i] == mark for i in range(inarow)):
                return True
    
    # Diagonal (negative slope)
    for row in range(inarow - 1, rows):
        for col in range(cols - inarow + 1):
            if all(board[row - i][col + i] == mark for i in range(inarow)):
                return True
    
    return False

def board_hash(board):
    """Create a hash of the board for transposition table"""
    return tuple(tuple(row) for row in board)

def evaluate_board(board, mark, inarow):
    """Advanced board evaluation function"""
    opponent = 3 - mark
    score = 0
    
    rows = len(board)
    cols = len(board[0])
    
    # Center column preference
    center_col = cols // 2
    for row in range(rows):
        if board[row][center_col] == mark:
            score += 3
        elif board[row][center_col] == opponent:
            score -= 3
    
    # Evaluate all windows
    score += evaluate_windows(board, mark, inarow)
    
    # Pattern recognition
    score += detect_threats(board, mark, inarow)
    
    return score

def evaluate_windows(board, mark, inarow):
    """Evaluate all possible winning windows"""
    score = 0
    opponent = 3 - mark
    rows = len(board)
    cols = len(board[0])
    
    # Helper function to score a window
    def score_window(window):
        if window.count(mark) == inarow:
            return 100000
        elif window.count(mark) == inarow - 1 and window.count(0) == 1:
            return 1000
        elif window.count(mark) == inarow - 2 and window.count(0) == 2:
            return 100
        elif window.count(opponent) == inarow - 1 and window.count(0) == 1:
            return -900
        elif window.count(opponent) == inarow - 2 and window.count(0) == 2:
            return -90
        return 0
    
    # Horizontal windows
    for row in range(rows):
        for col in range(cols - inarow + 1):
            window = [board[row][col + i] for i in range(inarow)]
            score += score_window(window)
    
    # Vertical windows
    for col in range(cols):
        for row in range(rows - inarow + 1):
            window = [board[row + i][col] for i in range(inarow)]
            score += score_window(window)
    
    # Positive diagonal windows
    for row in range(rows - inarow + 1):
        for col in range(cols - inarow + 1):
            window = [board[row + i][col + i] for i in range(inarow)]
            score += score_window(window)
    
    # Negative diagonal windows
    for row in range(inarow - 1, rows):
        for col in range(cols - inarow + 1):
            window = [board[row - i][col + i] for i in range(inarow)]
            score += score_window(window)
    
    return score

def detect_threats(board, mark, inarow):
    """Detect tactical threats and opportunities"""
    score = 0
    opponent = 3 - mark
    
    # Check for fork opportunities
    valid_moves = get_valid_moves(board)
    
    for move in valid_moves:
        test_board = make_move(board, move, mark)
        winning_moves = 0
        
        for next_move in get_valid_moves(test_board):
            if is_winning_move(test_board, next_move, mark, inarow):
                winning_moves += 1
        
        if winning_moves >= 2:
            score += 500  # Fork opportunity
    
    # Check for opponent forks to block
    for move in valid_moves:
        test_board = make_move(board, move, opponent)
        winning_moves = 0
        
        for next_move in get_valid_moves(test_board):
            if is_winning_move(test_board, next_move, opponent, inarow):
                winning_moves += 1
        
        if winning_moves >= 2:
            score -= 450  # Need to block fork
    
    return score

def minimax_search(board, mark, inarow, depth, time_limit, start_time):
    """Advanced minimax with alpha-beta pruning and transposition table"""
    
    def minimax(board, depth, alpha, beta, maximizing_player, mark):
        # Check time limit
        if time.time() - start_time > time_limit:
            return None, 0
        
        # Check transposition table
        board_key = board_hash(board)
        if board_key in transposition_table:
            stored_depth, stored_value = transposition_table[board_key]
            if stored_depth >= depth:
                return None, stored_value
        
        # Terminal node checks
        if check_win(board, mark, inarow):
            return None, WIN_SCORE - (10 - depth)
        if check_win(board, 3 - mark, inarow):
            return None, LOSS_SCORE + (10 - depth)
        
        valid_moves = get_valid_moves(board)
        if not valid_moves or depth == 0:
            return None, evaluate_board(board, mark, inarow)
        
        # Move ordering - try center columns first
        center = len(board[0]) // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        if maximizing_player:
            max_eval = -float('inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move(board, move, mark)
                _, eval_score = minimax(new_board, depth - 1, alpha, beta, False, mark)
                
                if eval_score is None:  # Timeout
                    return best_move, max_eval
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            # Store in transposition table
            transposition_table[board_key] = (depth, max_eval)
            return best_move, max_eval
        
        else:
            min_eval = float('inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move(board, move, 3 - mark)
                _, eval_score = minimax(new_board, depth - 1, alpha, beta, True, mark)
                
                if eval_score is None:  # Timeout
                    return best_move, min_eval
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            # Store in transposition table
            transposition_table[board_key] = (depth, min_eval)
            return best_move, min_eval
    
    # Clear old transposition table entries if it's getting too large
    if len(transposition_table) > 100000:
        transposition_table.clear()
    
    # Iterative deepening
    best_move = None
    for d in range(1, depth + 1):
        if time.time() - start_time > time_limit * 0.8:  # Leave some buffer
            break
        move, _ = minimax(board, d, -float('inf'), float('inf'), True, mark)
        if move is not None:
            best_move = move
    
    return best_move

class MCTSNode:
    """Node for Monte Carlo Tree Search"""
    def __init__(self, board, mark, inarow, parent=None, move=None):
        self.board = board
        self.mark = mark
        self.inarow = inarow
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = get_valid_moves(board)
        self.is_terminal = check_win(board, mark, inarow) or check_win(board, 3 - mark, inarow) or not self.untried_moves
    
    def select_child(self):
        """Select best child using UCB1"""
        c = 1.4  # Exploration constant
        return max(self.children, key=lambda child: 
                   child.wins / child.visits + c * math.sqrt(2 * math.log(self.visits) / child.visits))
    
    def expand(self):
        """Expand node by trying an untried move"""
        move = self.untried_moves.pop()
        new_board = make_move(self.board, move, self.mark)
        child = MCTSNode(new_board, 3 - self.mark, self.inarow, parent=self, move=move)
        self.children.append(child)
        return child
    
    def simulate(self):
        """Simulate random game from this position"""
        current_board = [row[:] for row in self.board]
        current_mark = self.mark
        
        while True:
            # Check for win
            if check_win(current_board, 3 - current_mark, self.inarow):
                return 1 if 3 - current_mark == self.mark else -1
            
            valid = get_valid_moves(current_board)
            if not valid:
                return 0  # Draw
            
            # Slightly favor center in rollouts
            if random.random() < 0.7:
                center = len(current_board[0]) // 2
                valid.sort(key=lambda x: abs(x - center))
                move = valid[0]
            else:
                move = random.choice(valid)
            
            current_board = make_move(current_board, move, current_mark)
            current_mark = 3 - current_mark
    
    def backpropagate(self, result):
        """Backpropagate simulation result"""
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(-result)

def mcts_search(board, mark, inarow, time_limit, start_time):
    """Monte Carlo Tree Search"""
    root = MCTSNode(board, mark, inarow)
    
    while time.time() - start_time < time_limit:
        node = root
        
        # Selection
        while node.children and not node.is_terminal:
            node = node.select_child()
        
        # Expansion
        if node.untried_moves and not node.is_terminal:
            node = node.expand()
        
        # Simulation
        if not node.is_terminal:
            result = node.simulate()
        else:
            # Terminal node
            if check_win(node.board, mark, inarow):
                result = 1
            elif check_win(node.board, 3 - mark, inarow):
                result = -1
            else:
                result = 0
        
        # Backpropagation
        node.backpropagate(result)
    
    # Return move of most visited child
    if root.children:
        return max(root.children, key=lambda child: child.visits).move
    return None
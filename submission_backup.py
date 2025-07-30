def my_agent(observation, configuration):
    """
    Connect X agent based on hybrid minimax/MCTS approach with tactical awareness.
    """
    import numpy as np
    import random
    import time
    import math
    
    # === Helper Functions ===
    
    def get_board_2d(board, rows, cols):
        """Convert flat board to 2D numpy array."""
        return np.array(board).reshape(rows, cols)
    
    def check_win(board, player, rows, cols, inarow):
        """Check if player has a winning position."""
        board_2d = get_board_2d(board, rows, cols)
        
        # Horizontal
        for r in range(rows):
            for c in range(cols - inarow + 1):
                if np.all(board_2d[r, c:c+inarow] == player):
                    return True
        
        # Vertical
        for r in range(rows - inarow + 1):
            for c in range(cols):
                if np.all(board_2d[r:r+inarow, c] == player):
                    return True
        
        # Diagonal (down-right)
        for r in range(rows - inarow + 1):
            for c in range(cols - inarow + 1):
                if np.all([board_2d[r+i, c+i] == player for i in range(inarow)]):
                    return True
        
        # Diagonal (up-right)
        for r in range(inarow-1, rows):
            for c in range(cols - inarow + 1):
                if np.all([board_2d[r-i, c+i] == player for i in range(inarow)]):
                    return True
        
        return False
    
    def make_move(board, col, player, rows, cols):
        """Make a move and return the new board state."""
        board_2d = get_board_2d(board, rows, cols)
        board_copy = board_2d.copy()
        
        for r in range(rows-1, -1, -1):
            if board_copy[r, col] == 0:
                board_copy[r, col] = player
                break
        
        return board_copy.flatten().tolist()
    
    def evaluate_position(board, player, rows, cols, inarow):
        """Evaluate board position for the given player."""
        board_2d = get_board_2d(board, rows, cols)
        score = 0
        opponent = 3 - player
        
        # Center control is valuable
        center_col = cols // 2
        center_count = 0
        for r in range(rows):
            if board_2d[r, center_col] == player:
                center_count += 1
        score += center_count * 3
        
        # Check for wins and near-wins in all directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for r in range(rows):
            for c in range(cols):
                if board_2d[r, c] == 0:  # Empty cell
                    continue
                    
                cell_player = board_2d[r, c]
                cell_score = 0
                
                for dr, dc in directions:
                    count = 0
                    empty_count = 0
                    
                    for i in range(1, inarow):
                        nr, nc = r + dr * i, c + dc * i
                        if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
                            break
                        
                        if board_2d[nr, nc] == cell_player:
                            count += 1
                        elif board_2d[nr, nc] == 0:
                            empty_count += 1
                            break
                        else:
                            break
                    
                    # Calculate score based on consecutive pieces
                    if cell_player == player:
                        if count == inarow - 1:  # One move from win
                            cell_score += 1000
                        elif count == inarow - 2 and empty_count >= 1:
                            cell_score += 100
                        elif count == inarow - 3 and empty_count >= 1:
                            cell_score += 10
                    else:  # Opponent
                        if count == inarow - 1:  # Block opponent win
                            cell_score -= 900
                        elif count == inarow - 2 and empty_count >= 1:
                            cell_score -= 90
                
                if cell_player == player:
                    score += cell_score
                else:
                    score -= cell_score
        
        return score
    
    def find_winning_move(board, player, rows, cols, inarow):
        """Find move that leads to immediate win."""
        valid_moves = [c for c in range(cols) if board[c] == 0]
        
        for move in valid_moves:
            new_board = make_move(board, move, player, rows, cols)
            if check_win(new_board, player, rows, cols, inarow):
                return move
        
        return None
    
    def find_blocking_move(board, player, rows, cols, inarow):
        """Find move that blocks opponent's win."""
        opponent = 3 - player
        valid_moves = [c for c in range(cols) if board[c] == 0]
        
        for move in valid_moves:
            new_board = make_move(board, move, opponent, rows, cols)
            if check_win(new_board, opponent, rows, cols, inarow):
                return move
        
        return None
    
    def find_fork_move(board, player, rows, cols, inarow):
        """Find move that creates a fork (two threats)."""
        valid_moves = [c for c in range(cols) if board[c] == 0]
        
        for move in valid_moves:
            new_board = make_move(board, move, player, rows, cols)
            
            # Check if this move creates multiple winning threats
            threats = 0
            for next_move in [c for c in range(cols) if c != move and new_board[c] == 0]:
                fork_board = make_move(new_board, next_move, player, rows, cols)
                if check_win(fork_board, player, rows, cols, inarow):
                    threats += 1
            
            if threats >= 2:
                return move
        
        return None
    
    def minimax(board, depth, alpha, beta, maximizing, player, rows, cols, inarow, start_time, time_limit=0.9):
        """Minimax algorithm with alpha-beta pruning."""
        # Time check
        if time.time() - start_time > time_limit:
            return evaluate_position(board, player, rows, cols, inarow), None
        
        # Check terminal states
        if depth == 0:
            return evaluate_position(board, player, rows, cols, inarow), None
        
        if check_win(board, player, rows, cols, inarow):
            return 10000, None
        
        if check_win(board, 3 - player, rows, cols, inarow):
            return -10000, None
        
        # Get valid moves
        valid_moves = [c for c in range(cols) if board[c] == 0]
        if not valid_moves:
            return 0, None  # Draw
        
        # Center column first
        center = cols // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        if maximizing:
            best_value = float('-inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move(board, move, player, rows, cols)
                value, _ = minimax(new_board, depth - 1, alpha, beta, False, 3 - player, rows, cols, inarow, start_time, time_limit)
                
                if value > best_value:
                    best_value = value
                    best_move = move
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            
            return best_value, best_move
        else:
            best_value = float('inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move(board, move, player, rows, cols)
                value, _ = minimax(new_board, depth - 1, alpha, beta, True, 3 - player, rows, cols, inarow, start_time, time_limit)
                
                if value < best_value:
                    best_value = value
                    best_move = move
                
                beta = min(beta, value)
                if beta <= alpha:
                    break
            
            return best_value, best_move
    
    class MCTSNode:
        """Monte Carlo Tree Search node."""
        
        def __init__(self, board, player, parent=None, move=None):
            self.board = board
            self.player = player
            self.parent = parent
            self.move = move
            self.wins = 0
            self.visits = 0
            self.children = []
            self.untried_moves = None
        
        def ucb_score(self, c=1.4):
            """Calculate UCB score for node selection."""
            if self.visits == 0:
                return float('inf')
            
            # UCB formula with center bias
            exploitation = self.wins / self.visits
            exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
            
            center_bias = 0
            if self.move is not None:
                # Slight bias toward center columns
                center_col = 3  # For 7 columns
                center_bias = 0.1 * (1 - abs(self.move - center_col) / center_col)
            
            return exploitation + exploration + center_bias
    
    def mcts_search(board, player, rows, cols, inarow, time_limit=0.9):
        """Monte Carlo Tree Search for finding the best move."""
        root = MCTSNode(board, player)
        root.untried_moves = [c for c in range(cols) if board[c] == 0]
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < time_limit and iterations < 1000:
            # Selection phase
            node = root
            temp_board = board.copy()
            
            # Find a node to expand
            while node.untried_moves is None or len(node.untried_moves) == 0:
                if len(node.children) == 0:
                    break
                
                node = max(node.children, key=lambda n: n.ucb_score())
                if node.move is not None:
                    temp_board = make_move(temp_board, node.move, node.player, rows, cols)
            
            # Expansion phase
            if node.untried_moves and len(node.untried_moves) > 0:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                
                temp_board = make_move(temp_board, move, node.player, rows, cols)
                child = MCTSNode(temp_board, 3 - node.player, node, move)
                child.untried_moves = [c for c in range(cols) if temp_board[c] == 0]
                node.children.append(child)
                node = child
            
            # Simulation phase
            current_player = node.player
            simulation_board = temp_board.copy()
            
            while True:
                # Check for end of game
                if check_win(simulation_board, 1, rows, cols, inarow):
                    result = 1 if player == 1 else 0
                    break
                if check_win(simulation_board, 2, rows, cols, inarow):
                    result = 1 if player == 2 else 0
                    break
                
                valid_moves = [c for c in range(cols) if simulation_board[c] == 0]
                if not valid_moves:
                    result = 0.5  # Draw
                    break
                
                # Use smart rollout instead of random
                # First check for winning moves
                winning_move = find_winning_move(simulation_board, current_player, rows, cols, inarow)
                if winning_move is not None:
                    sim_move = winning_move
                else:
                    # Check for blocking opponent's wins
                    blocking_move = find_blocking_move(simulation_board, current_player, rows, cols, inarow)
                    if blocking_move is not None:
                        sim_move = blocking_move
                    else:
                        # Otherwise prefer center
                        center = cols // 2
                        valid_moves.sort(key=lambda x: abs(x - center))
                        sim_move = valid_moves[0]
                
                simulation_board = make_move(simulation_board, sim_move, current_player, rows, cols)
                current_player = 3 - current_player
            
            # Backpropagation phase
            while node is not None:
                node.visits += 1
                if node.player != player:  # If node is opponent's turn
                    node.wins += result
                else:
                    node.wins += 1 - result
                node = node.parent
            
            iterations += 1
        
        # Choose the move with the most visits
        if len(root.children) == 0:
            return None
        
        return max(root.children, key=lambda n: n.visits).move
    
    # === Main Agent Logic ===
    
    board = observation.board
    player = observation.mark
    rows = configuration.rows
    cols = configuration.columns
    inarow = configuration.inarow
    
    # Get valid moves
    valid_moves = [c for c in range(cols) if board[c] == 0]
    if not valid_moves:
        return 0
    
    # Check for immediate win
    winning_move = find_winning_move(board, player, rows, cols, inarow)
    if winning_move is not None:
        return winning_move
    
    # Check for immediate block
    blocking_move = find_blocking_move(board, player, rows, cols, inarow)
    if blocking_move is not None:
        return blocking_move
    
    # Check for fork
    fork_move = find_fork_move(board, player, rows, cols, inarow)
    if fork_move is not None:
        return fork_move
    
    # Game phase-based decision making
    start_time = time.time()
    move_count = sum(1 for cell in board if cell != 0)
    
    if move_count < 10:
        # Early game: use minimax with low depth
        _, move = minimax(board, 4, float('-inf'), float('inf'), True, player, rows, cols, inarow, start_time, 0.9)
        if move is not None:
            return move
    else:
        # Mid-late game: use MCTS
        move = mcts_search(board, player, rows, cols, inarow, 0.9)
        if move is not None:
            return move
    
    # Fallback: choose center or closest to center
    center = cols // 2
    valid_moves.sort(key=lambda x: abs(x - center))
    return valid_moves[0]
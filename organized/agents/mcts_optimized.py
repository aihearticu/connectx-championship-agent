"""
Optimized Monte Carlo Tree Search Agent
High-performance MCTS implementation for top-tier Connect X play
"""

def agent(observation, configuration):
    """MCTS Agent - Optimized for Kaggle Environment"""
    import math
    import random
    
    board = observation.board
    mark = observation.mark
    
    class MCTSNode:
        """Node in the Monte Carlo Tree"""
        def __init__(self, board, mark, parent=None, action=None):
            self.board = board[:]
            self.mark = mark
            self.parent = parent
            self.action = action
            
            self.wins = 0
            self.visits = 0
            self.children = []
            self.untried_actions = [c for c in range(7) if board[c] == 0]
            
            # UCB1 constant
            self.c = math.sqrt(2)
        
        def select_child(self):
            """Select best child using UCB1"""
            return max(self.children, key=lambda c: c.ucb1())
        
        def ucb1(self):
            """Upper Confidence Bound 1 formula"""
            if self.visits == 0:
                return float('inf')
            
            exploitation = self.wins / self.visits
            exploration = self.c * math.sqrt(math.log(self.parent.visits) / self.visits)
            return exploitation + exploration
        
        def expand(self):
            """Expand node by adding a new child"""
            action = self.untried_actions.pop()
            
            # Create new board state
            new_board = self.board[:]
            for row in range(5, -1, -1):
                if new_board[row * 7 + action] == 0:
                    new_board[row * 7 + action] = self.mark
                    break
            
            child = MCTSNode(new_board, 3 - self.mark, parent=self, action=action)
            self.children.append(child)
            return child
        
        def update(self, result):
            """Update node statistics"""
            self.visits += 1
            self.wins += result
        
        def is_terminal(self):
            """Check if node is terminal (game over)"""
            return check_winner(self.board) != 0 or all(self.board[i] != 0 for i in range(7))
        
        def get_result(self, perspective_mark):
            """Get result from perspective of given mark"""
            winner = check_winner(self.board)
            if winner == perspective_mark:
                return 1
            elif winner == 3 - perspective_mark:
                return -1
            else:
                return 0
    
    def check_winner(board):
        """Fast winner checking"""
        # Horizontal
        for row in range(6):
            for col in range(4):
                if board[row*7 + col] != 0:
                    if all(board[row*7 + col + i] == board[row*7 + col] for i in range(4)):
                        return board[row*7 + col]
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if board[(row)*7 + col] != 0:
                    if all(board[(row+i)*7 + col] == board[row*7 + col] for i in range(4)):
                        return board[row*7 + col]
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                if board[row*7 + col] != 0:
                    if all(board[(row+i)*7 + col + i] == board[row*7 + col] for i in range(4)):
                        return board[row*7 + col]
        
        # Diagonal /
        for row in range(3, 6):
            for col in range(4):
                if board[row*7 + col] != 0:
                    if all(board[(row-i)*7 + col + i] == board[row*7 + col] for i in range(4)):
                        return board[row*7 + col]
        
        return 0
    
    def simulate(board, mark):
        """Fast random playout with smart moves"""
        sim_board = board[:]
        sim_mark = mark
        
        moves = 0
        while moves < 42:
            # Check for winning moves first
            valid_moves = [c for c in range(7) if sim_board[c] == 0]
            if not valid_moves:
                break
            
            # Smart simulation - check for wins/blocks
            move_found = False
            
            # Check for win
            for col in valid_moves:
                test_board = sim_board[:]
                for row in range(5, -1, -1):
                    if test_board[row * 7 + col] == 0:
                        test_board[row * 7 + col] = sim_mark
                        break
                
                if check_winner(test_board) == sim_mark:
                    move = col
                    move_found = True
                    break
            
            # Check for block if no win
            if not move_found:
                for col in valid_moves:
                    test_board = sim_board[:]
                    for row in range(5, -1, -1):
                        if test_board[row * 7 + col] == 0:
                            test_board[row * 7 + col] = 3 - sim_mark
                            break
                    
                    if check_winner(test_board) == 3 - sim_mark:
                        move = col
                        move_found = True
                        break
            
            # Random move with center preference if no tactical move
            if not move_found:
                # Prefer center columns
                weights = [abs(3 - c) + 1 for c in valid_moves]
                total = sum(weights)
                weights = [w/total for w in weights]
                
                r = random.random()
                cumsum = 0
                for i, w in enumerate(weights):
                    cumsum += w
                    if r < cumsum:
                        move = valid_moves[i]
                        break
                else:
                    move = valid_moves[-1]
            
            # Make move
            for row in range(5, -1, -1):
                if sim_board[row * 7 + move] == 0:
                    sim_board[row * 7 + move] = sim_mark
                    break
            
            # Check for winner
            winner = check_winner(sim_board)
            if winner != 0:
                return 1 if winner == mark else -1
            
            sim_mark = 3 - sim_mark
            moves += 1
        
        return 0  # Draw
    
    def mcts_search(board, mark, iterations=150):
        """Run MCTS search"""
        root = MCTSNode(board, mark)
        
        for _ in range(iterations):
            node = root
            
            # Selection - traverse tree using UCB1
            while node.untried_actions == [] and node.children != []:
                node = node.select_child()
            
            # Expansion - add new child if not terminal
            if node.untried_actions != [] and not node.is_terminal():
                node = node.expand()
            
            # Simulation - random playout
            if not node.is_terminal():
                result = simulate(node.board, node.mark)
            else:
                result = node.get_result(mark)
            
            # Backpropagation - update all nodes in path
            while node is not None:
                # Invert result for opponent's perspective
                if node.mark != mark:
                    node.update(-result)
                else:
                    node.update(result)
                node = node.parent
        
        # Choose most visited child
        if root.children:
            return max(root.children, key=lambda c: c.visits).action
        
        # Fallback to center
        return 3
    
    # Quick win/block check before MCTS
    def check_immediate(board, col, mark):
        """Check if move wins immediately"""
        if board[col] != 0:
            return False
        
        test_board = board[:]
        for row in range(5, -1, -1):
            if test_board[row * 7 + col] == 0:
                test_board[row * 7 + col] = mark
                break
        
        return check_winner(test_board) == mark
    
    # Check for immediate win
    for col in range(7):
        if check_immediate(board, col, mark):
            return col
    
    # Check for immediate block
    for col in range(7):
        if check_immediate(board, col, 3 - mark):
            return col
    
    # Adjust iterations based on game phase
    pieces = sum(1 for x in board if x != 0)
    
    if pieces < 8:
        iterations = 200  # More time in opening
    elif pieces < 20:
        iterations = 150  # Standard midgame
    else:
        iterations = 100  # Faster in endgame
    
    # Run MCTS
    return mcts_search(board, mark, iterations)
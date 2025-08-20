"""
Fixed Elite Top 5 Connect X Agent
Corrected implementation with proper minimax, evaluation, and move validation
Target: 1400-1600 ELO rating for top 5 placement
"""

import time
import random

class TopFiveAgentFixed:
    """Elite agent with all fixes applied"""
    
    def __init__(self):
        self.nodes_searched = 0
        self.max_depth_reached = 0
        
        # Transposition table (simplified but effective)
        self.tt = {}
        self.tt_hits = 0
        self.tt_lookups = 0
        
        # Killer moves for move ordering
        self.killer_moves = {}
        
        # Opening book with proven best moves
        self.opening_book = {
            (): 3,  # Start center
            (3,): 3,  # Mirror center
            (3, 3): 2,  # Take adjacent
            (3, 2): 3,
            (3, 4): 3,
            (3, 3, 2, 2): 4,
            (3, 3, 2, 3): 4,
        }
    
    def get_valid_moves(self, board):
        """Get list of valid columns"""
        return [col for col in range(7) if board[col] == 0]
    
    def make_move(self, board, col, mark):
        """Make a move on the board"""
        board = board.copy()
        for row in range(5, -1, -1):
            if board[row * 7 + col] == 0:
                board[row * 7 + col] = mark
                break
        return board
    
    def check_win(self, board, mark):
        """Check if mark has won"""
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row * 7 + col + i] == mark for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row + i) * 7 + col] == mark for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                if all(board[(row + i) * 7 + col + i] == mark for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3):
            for col in range(4):
                if all(board[(row + 3 - i) * 7 + col + i] == mark for i in range(4)):
                    return True
        
        return False
    
    def evaluate_window(self, window, mark):
        """Evaluate a 4-piece window"""
        score = 0
        opp_mark = 3 - mark
        
        if window.count(mark) == 4:
            score += 100
        elif window.count(mark) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(mark) == 2 and window.count(0) == 2:
            score += 2
        
        if window.count(opp_mark) == 3 and window.count(0) == 1:
            score -= 4
        
        return score
    
    def evaluate_position(self, board, mark):
        """Sophisticated evaluation function"""
        score = 0
        
        # Check for immediate wins
        for col in self.get_valid_moves(board):
            temp_board = self.make_move(board, col, mark)
            if self.check_win(temp_board, mark):
                return 10000
        
        # Check for immediate losses
        for col in self.get_valid_moves(board):
            temp_board = self.make_move(board, col, 3 - mark)
            if self.check_win(temp_board, 3 - mark):
                return -10000
        
        # Center column preference (column 3)
        center_array = [board[i * 7 + 3] for i in range(6)]
        center_count = center_array.count(mark)
        score += center_count * 6
        
        # Adjacent columns (2 and 4)
        for col in [2, 4]:
            col_array = [board[i * 7 + col] for i in range(6)]
            score += col_array.count(mark) * 3
        
        # Horizontal evaluation
        for row in range(6):
            row_array = [board[row * 7 + col] for col in range(7)]
            for col in range(4):
                window = row_array[col:col+4]
                score += self.evaluate_window(window, mark)
        
        # Vertical evaluation
        for col in range(7):
            col_array = [board[row * 7 + col] for row in range(6)]
            for row in range(3):
                window = col_array[row:row+4]
                score += self.evaluate_window(window, mark)
        
        # Diagonal \ evaluation
        for row in range(3):
            for col in range(4):
                window = [board[(row+i) * 7 + col+i] for i in range(4)]
                score += self.evaluate_window(window, mark)
        
        # Diagonal / evaluation
        for row in range(3):
            for col in range(4):
                window = [board[(row+3-i) * 7 + col+i] for i in range(4)]
                score += self.evaluate_window(window, mark)
        
        return score
    
    def get_move_order(self, board):
        """Get optimal move ordering for alpha-beta pruning"""
        # Start with center-first ordering
        base_order = [3, 4, 2, 5, 1, 6, 0]
        
        # Filter valid moves
        valid_moves = []
        for col in base_order:
            if col in self.get_valid_moves(board):
                valid_moves.append(col)
        
        # Add any missing valid moves
        for col in range(7):
            if board[col] == 0 and col not in valid_moves:
                valid_moves.append(col)
        
        return valid_moves
    
    def minimax(self, board, depth, alpha, beta, maximizing_player, mark, start_time):
        """Minimax with alpha-beta pruning"""
        self.nodes_searched += 1
        
        # Time check
        if time.time() - start_time > 0.8:
            return 0
        
        # Transposition table lookup
        board_key = tuple(board)
        if board_key in self.tt and self.tt[board_key][1] >= depth:
            self.tt_hits += 1
            return self.tt[board_key][0]
        self.tt_lookups += 1
        
        # Terminal node check
        valid_moves = self.get_valid_moves(board)
        
        # Check for win
        if self.check_win(board, 3 - mark if not maximizing_player else mark):
            value = -10000 + depth if maximizing_player else 10000 - depth
            self.tt[board_key] = (value, depth)
            return value
        
        # Draw or depth limit
        if depth == 0 or len(valid_moves) == 0:
            value = self.evaluate_position(board, mark)
            self.tt[board_key] = (value, depth)
            return value
        
        # Get move order
        move_order = self.get_move_order(board)
        
        if maximizing_player:
            max_eval = -float('inf')
            for col in move_order:
                new_board = self.make_move(board, col, mark)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False, mark, start_time)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            
            self.tt[board_key] = (max_eval, depth)
            return max_eval
        else:
            min_eval = float('inf')
            for col in move_order:
                new_board = self.make_move(board, col, 3 - mark)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True, mark, start_time)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            
            self.tt[board_key] = (min_eval, depth)
            return min_eval
    
    def get_best_move(self, board, mark, time_limit=0.9):
        """Get best move using iterative deepening"""
        start_time = time.time()
        valid_moves = self.get_valid_moves(board)
        
        if not valid_moves:
            return 0
        
        # Single valid move
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        # Try opening book
        move_count = sum(1 for x in board if x != 0)
        if move_count < 8:
            move_history = self._get_move_history(board)
            if move_history in self.opening_book:
                book_move = self.opening_book[move_history]
                if book_move in valid_moves:
                    return book_move
        
        # Check for immediate wins
        for col in valid_moves:
            temp_board = self.make_move(board, col, mark)
            if self.check_win(temp_board, mark):
                return col
        
        # Check for blocking opponent wins
        for col in valid_moves:
            temp_board = self.make_move(board, col, 3 - mark)
            if self.check_win(temp_board, 3 - mark):
                return col
        
        # Iterative deepening
        best_move = valid_moves[0]
        self.max_depth_reached = 0
        
        for depth in range(1, 12):
            if time.time() - start_time > time_limit * 0.7:
                break
            
            self.nodes_searched = 0
            self.max_depth_reached = depth
            
            # Evaluate each move
            move_scores = []
            for col in self.get_move_order(board):
                if time.time() - start_time > time_limit * 0.9:
                    break
                
                new_board = self.make_move(board, col, mark)
                score = self.minimax(new_board, depth - 1, -float('inf'), float('inf'), 
                                   False, mark, start_time)
                move_scores.append((score, col))
            
            # Select best move from this depth
            if move_scores:
                move_scores.sort(reverse=True)
                best_move = move_scores[0][1]
            
            # Early exit if we found a winning move
            if move_scores and move_scores[0][0] >= 9000:
                break
        
        return best_move
    
    def _get_move_history(self, board):
        """Extract move history for opening book (simplified)"""
        # This is a simplified version - would need proper reconstruction
        moves = []
        # Count moves per column
        for col in range(7):
            count = sum(1 for row in range(6) if board[row * 7 + col] != 0)
            for _ in range(count):
                moves.append(col)
        
        return tuple(moves[:8]) if len(moves) >= 8 else tuple(moves)

def agent(observation, configuration):
    """Kaggle submission function"""
    agent_instance = TopFiveAgentFixed()
    board = observation.board
    mark = observation.mark
    
    move = agent_instance.get_best_move(board, mark, time_limit=0.9)
    return move

# Self-contained testing
if __name__ == "__main__":
    import random
    
    def test_agent():
        """Quick test of the agent"""
        print("Testing Top 5 Agent (Fixed)")
        print("="*50)
        
        agent_instance = TopFiveAgentFixed()
        
        # Test 1: Empty board
        board = [0] * 42
        start = time.time()
        move = agent_instance.get_best_move(board, 1, time_limit=0.5)
        elapsed = time.time() - start
        
        print(f"Empty board: Move={move}, Time={elapsed:.3f}s")
        print(f"  Depth reached: {agent_instance.max_depth_reached}")
        print(f"  Nodes searched: {agent_instance.nodes_searched:,}")
        
        # Test 2: Complex position
        board = [0] * 42
        board[35] = 1  # Center bottom
        board[36] = 2  # Adjacent
        board[28] = 1  # Center second row
        board[29] = 2  # Adjacent second row
        
        start = time.time()
        move = agent_instance.get_best_move(board, 1, time_limit=0.5)
        elapsed = time.time() - start
        
        print(f"\nComplex position: Move={move}, Time={elapsed:.3f}s")
        print(f"  Depth reached: {agent_instance.max_depth_reached}")
        print(f"  Nodes searched: {agent_instance.nodes_searched:,}")
        
        # Test 3: Win detection
        board = [0] * 42
        board[35] = 1  # XXX_
        board[36] = 1
        board[37] = 1
        
        move = agent_instance.get_best_move(board, 1, time_limit=0.1)
        print(f"\nWin detection test: Move={move} (should be 3)")
        
        # Test 4: Block detection
        board = [0] * 42
        board[35] = 2  # OOO_
        board[36] = 2
        board[37] = 2
        
        move = agent_instance.get_best_move(board, 1, time_limit=0.1)
        print(f"Block detection test: Move={move} (should be 3)")
        
        print("\n✓ Agent tests completed")
    
    test_agent()
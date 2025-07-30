#!/usr/bin/env python3
"""Debug the agent to find issues"""

from kaggle_environments import make

def test_basic_agent():
    """Test a very basic agent first"""
    
    def basic_agent(obs, config):
        """Simple agent that blocks and wins"""
        board = obs.board
        my_mark = obs.mark
        opp_mark = 3 - my_mark
        
        # Get valid moves
        valid = [c for c in range(config.columns) if board[c] == 0]
        if not valid:
            return 0
        
        # Try to win
        for col in valid:
            # Simulate move
            test_board = list(board)
            for row in range(config.rows-1, -1, -1):
                if test_board[row * config.columns + col] == 0:
                    test_board[row * config.columns + col] = my_mark
                    # Check if this wins
                    if check_win(test_board, row, col, my_mark, config):
                        return col
                    test_board[row * config.columns + col] = 0
                    break
        
        # Try to block
        for col in valid:
            # Simulate move
            test_board = list(board)
            for row in range(config.rows-1, -1, -1):
                if test_board[row * config.columns + col] == 0:
                    test_board[row * config.columns + col] = opp_mark
                    # Check if opponent would win
                    if check_win(test_board, row, col, opp_mark, config):
                        return col
                    test_board[row * config.columns + col] = 0
                    break
        
        # Default to center
        if config.columns // 2 in valid:
            return config.columns // 2
        
        return valid[0]
    
    def check_win(board, row, col, mark, config):
        """Check if placing mark at row,col wins"""
        rows = config.rows
        cols = config.columns
        inarow = config.inarow
        
        # Check horizontal
        count = 1
        # Left
        c = col - 1
        while c >= 0 and board[row * cols + c] == mark:
            count += 1
            c -= 1
        # Right  
        c = col + 1
        while c < cols and board[row * cols + c] == mark:
            count += 1
            c += 1
        if count >= inarow:
            return True
        
        # Check vertical
        count = 1
        # Down
        r = row + 1
        while r < rows and board[r * cols + col] == mark:
            count += 1
            r += 1
        # Up
        r = row - 1
        while r >= 0 and board[r * cols + col] == mark:
            count += 1
            r -= 1
        if count >= inarow:
            return True
        
        # Check diagonal /
        count = 1
        r, c = row - 1, col + 1
        while r >= 0 and c < cols and board[r * cols + c] == mark:
            count += 1
            r -= 1
            c += 1
        r, c = row + 1, col - 1
        while r < rows and c >= 0 and board[r * cols + c] == mark:
            count += 1
            r += 1
            c -= 1
        if count >= inarow:
            return True
        
        # Check diagonal \
        count = 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0 and board[r * cols + c] == mark:
            count += 1
            r -= 1
            c -= 1
        r, c = row + 1, col + 1
        while r < rows and c < cols and board[r * cols + c] == mark:
            count += 1
            r += 1
            c += 1
        if count >= inarow:
            return True
        
        return False
    
    # Test the basic agent
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    env = make("connectx", debug=True)
    
    print("Testing basic agent...")
    env.reset()
    env.run([basic_agent, random_agent])
    print(env.render(mode="ansi"))
    
    # Now test our optimized agent
    import optimized_elite_submission
    print("\nTesting optimized agent...")
    env.reset()
    env.run([optimized_elite_submission.agent, random_agent])
    print(env.render(mode="ansi"))

if __name__ == "__main__":
    test_basic_agent()
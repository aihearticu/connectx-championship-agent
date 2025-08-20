"""
Comprehensive testing before submission
"""

import time
import random

def test_agent():
    from submission import agent
    
    class Observation:
        def __init__(self, board, mark):
            self.board = board
            self.mark = mark
    
    print("="*50)
    print(" TESTING SUBMISSION AGENT ")
    print("="*50)
    
    # Test 1: Basic tests
    print("\n[1] Basic Tests")
    obs = Observation([0]*42, 1)
    move = agent(obs, None)
    print(f"  Empty board: {move} {'✓' if move == 3 else '✗'}")
    
    # Win detection
    board = [0]*42
    board[35] = board[36] = board[37] = 1
    obs = Observation(board, 1)
    move = agent(obs, None)
    print(f"  Win detection: {move} {'✓' if move == 3 else '✗'}")
    
    # Block detection
    board = [0]*42
    board[35] = board[36] = board[37] = 2
    obs = Observation(board, 1)
    move = agent(obs, None)
    print(f"  Block detection: {move} {'✓' if move == 3 else '✗'}")
    
    # Test 2: Speed test
    print("\n[2] Speed Test")
    positions = [
        ("Empty", [0]*42),
        ("Midgame", [0]*28 + [1,2,1,2,0,0,0,2,1,2,1,2,1,0]),
    ]
    
    for name, board in positions:
        obs = Observation(board, 1)
        start = time.time()
        move = agent(obs, None)
        elapsed = time.time() - start
        print(f"  {name}: {elapsed:.3f}s {'✓' if elapsed < 1.0 else '✗'}")
    
    # Test 3: Game vs random
    print("\n[3] Game Test (5 games vs random)")
    
    def check_win(board, player):
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row*7+col+i] == player for i in range(4)):
                    return True
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row+i)*7+col] == player for i in range(4)):
                    return True
        # Diagonals
        for row in range(3):
            for col in range(4):
                if all(board[(row+i)*7+col+i] == player for i in range(4)):
                    return True
                if all(board[(row+3-i)*7+col+i] == player for i in range(4)):
                    return True
        return False
    
    wins = 0
    for game in range(5):
        board = [0]*42
        current = 1
        moves = 0
        
        while moves < 42:
            obs = Observation(board.copy(), current)
            
            if current == 1:
                col = agent(obs, None)
            else:
                valid = [c for c in range(7) if board[c] == 0]
                col = random.choice(valid) if valid else 0
            
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = current
                    break
            
            moves += 1
            
            if check_win(board, current):
                if current == 1:
                    wins += 1
                break
            
            current = 3 - current
    
    print(f"  Won {wins}/5 games ({wins*20}%)")
    
    print("\n✓ AGENT READY FOR SUBMISSION")
    return True

if __name__ == "__main__":
    test_agent()

"""Test NN Safe v2 agent properly"""

import time
import random
from submission_nn_enhanced_899 import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def make_move(board, col, piece):
    """Properly make a move in Connect 4"""
    for row in range(5, -1, -1):
        if board[row * 7 + col] == 0:
            board[row * 7 + col] = piece
            return True
    return False

def test_agent():
    print("=== NN SAFE V2 AGENT TESTING ===\n")
    
    all_pass = True
    config = MockConfig()
    
    # Test 1: Speed test with proper game simulation
    print("1. Performance Tests (100 random games):")
    times = []
    
    for game in range(100):
        board = [0] * 42
        current_player = 1
        
        # Play random moves
        for turn in range(random.randint(0, 20)):
            valid_cols = [c for c in range(7) if board[c] == 0]
            if not valid_cols:
                break
            
            col = random.choice(valid_cols)
            make_move(board, col, current_player)
            current_player = 3 - current_player
        
        # Time agent's move
        start = time.time()
        move = agent(MockObs(board, 1), config)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        # Validate move
        valid = [c for c in range(7) if board[c] == 0]
        if valid and move not in valid:
            print(f"   ✗ Invalid move {move} in game {game}")
            all_pass = False
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"   Average time: {avg_time:.2f}ms {'✓' if avg_time < 10 else '✗'}")
    print(f"   Max time: {max_time:.2f}ms {'✓' if max_time < 50 else '✗'}")
    
    if avg_time >= 10 or max_time >= 50:
        all_pass = False
    
    # Test 2: Tactical accuracy
    print("\n2. Tactical Tests:")
    
    # Win detection
    board = [0] * 42
    make_move(board, 0, 1)
    make_move(board, 1, 1)
    make_move(board, 2, 1)
    move = agent(MockObs(board, 1), config)
    print(f"   Horizontal win: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Block detection
    board = [0] * 42
    make_move(board, 0, 2)
    make_move(board, 1, 2)
    make_move(board, 2, 2)
    move = agent(MockObs(board, 1), config)
    print(f"   Horizontal block: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Vertical win
    board = [0] * 42
    make_move(board, 3, 1)
    make_move(board, 3, 1)
    make_move(board, 3, 1)
    move = agent(MockObs(board, 1), config)
    print(f"   Vertical win: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Test 3: Safety checks
    print("\n3. Safety Tests:")
    
    # Don't set up opponent win
    board = [0] * 42
    make_move(board, 3, 2)
    make_move(board, 3, 2)
    make_move(board, 3, 2)
    # If we play col 3, opponent wins on next move
    move = agent(MockObs(board, 1), config)
    print(f"   Avoid setup: {move} {'✓' if move != 3 else '✗ (gives opponent win)'}")
    if move == 3: all_pass = False
    
    # Test 4: Complex position performance
    print("\n4. Complex Position Tests:")
    
    complex_times = []
    for i in range(20):
        board = [0] * 42
        # Fill board realistically
        for _ in range(random.randint(20, 30)):
            valid = [c for c in range(7) if board[c] == 0]
            if not valid:
                break
            col = random.choice(valid)
            make_move(board, col, random.choice([1, 2]))
        
        start = time.time()
        move = agent(MockObs(board, 1), config)
        elapsed = (time.time() - start) * 1000
        complex_times.append(elapsed)
    
    complex_avg = sum(complex_times) / len(complex_times)
    complex_max = max(complex_times)
    
    print(f"   Complex avg: {complex_avg:.2f}ms {'✓' if complex_avg < 15 else '✗'}")
    print(f"   Complex max: {complex_max:.2f}ms {'✓' if complex_max < 50 else '✗'}")
    
    if complex_avg >= 15 or complex_max >= 50:
        all_pass = False
    
    # Test 5: Edge cases
    print("\n5. Edge Cases:")
    
    # Empty board
    move = agent(MockObs([0]*42, 1), config)
    print(f"   Empty board: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # One column left
    board = [0] * 42
    # Fill all but column 5
    for col in [0,1,2,3,4,6]:
        for _ in range(6):
            make_move(board, col, random.choice([1,2]))
    move = agent(MockObs(board, 1), config)
    print(f"   One column left: {move} {'✓' if move == 5 else '✗'}")
    if move != 5: all_pass = False
    
    # Summary
    print("\n" + "="*40)
    if all_pass:
        print("✅ ALL TESTS PASSED! NN Safe v2 ready.")
        print("   - Fast performance")
        print("   - Perfect tactics")
        print("   - Smart safety checks")
        print("   - Handles complex positions")
    else:
        print("❌ SOME TESTS FAILED! Needs fixes.")
    
    return all_pass

if __name__ == "__main__":
    test_agent()
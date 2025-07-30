"""Comprehensive verification of fast agent before submission"""

import time
import random
from submission_verified import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def test_agent():
    """Run comprehensive tests"""
    print("=== COMPREHENSIVE AGENT VERIFICATION ===\n")
    
    all_pass = True
    
    # Test 1: Basic functionality
    print("1. Basic Functionality Tests:")
    
    # Empty board
    move = agent(MockObs([0]*42, 1), MockConfig())
    print(f"   Empty board: {move} {'✓' if move == 3 else '✗ FAIL'}")
    if move != 3: all_pass = False
    
    # Test 2: Win detection
    print("\n2. Win Detection Tests:")
    
    # Horizontal win
    board = [0]*42
    board[35] = board[36] = board[37] = 1
    move = agent(MockObs(board, 1), MockConfig())
    print(f"   Horizontal win: {move} {'✓' if move == 3 else '✗ FAIL'}")
    if move != 3: all_pass = False
    
    # Vertical win
    board = [0]*42
    board[38] = board[31] = board[24] = 1
    move = agent(MockObs(board, 1), MockConfig())
    print(f"   Vertical win: {move} {'✓' if move == 3 else '✗ FAIL'}")
    if move != 3: all_pass = False
    
    # Test 3: Block detection
    print("\n3. Block Detection Tests:")
    
    # Must block horizontal
    board = [0]*42
    board[35] = board[36] = board[37] = 2
    move = agent(MockObs(board, 1), MockConfig())
    print(f"   Block horizontal: {move} {'✓' if move == 3 else '✗ FAIL'}")
    if move != 3: all_pass = False
    
    # Test 4: Speed test
    print("\n4. Performance Tests:")
    
    times = []
    for _ in range(1000):
        # Random board state
        board = [0]*42
        for _ in range(random.randint(5, 15)):
            col = random.randint(0, 6)
            for row in range(5, -1, -1):
                if board[row*7 + col] == 0:
                    board[row*7 + col] = random.choice([1, 2])
                    break
        
        start = time.time()
        move = agent(MockObs(board, 1), MockConfig())
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        # Verify move is valid
        if board[move] != 0:  # Column full
            print(f"   ✗ FAIL: Invalid move {move} on full column")
            all_pass = False
            break
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    print(f"   Average time: {avg_time:.3f}ms ✓")
    print(f"   Max time: {max_time:.3f}ms {'✓' if max_time < 10 else '✗ FAIL'}")
    if max_time >= 10: all_pass = False
    
    # Test 5: Edge cases
    print("\n5. Edge Case Tests:")
    
    # Almost full board
    board = [1,2,1,2,1,2,1,
             2,1,2,1,2,1,2,
             1,2,1,2,1,2,1,
             2,1,2,1,2,1,2,
             1,2,1,2,1,2,1,
             2,1,2,1,2,1,0]  # Only last spot open
    move = agent(MockObs(board, 1), MockConfig())
    print(f"   Almost full board: {move} {'✓' if move == 6 else '✗ FAIL'}")
    if move != 6: all_pass = False
    
    # Test 6: No crashes on various positions
    print("\n6. Stability Test (100 random games):")
    
    for i in range(100):
        board = [0]*42
        for turn in range(random.randint(0, 30)):
            piece = (turn % 2) + 1
            valid = [c for c in range(7) if board[c] == 0]
            if not valid:
                break
            
            try:
                move = agent(MockObs(board, piece), MockConfig())
                if move not in valid:
                    print(f"   ✗ FAIL: Invalid move {move} at game {i}")
                    all_pass = False
                    break
                
                # Make the move
                for r in range(5, -1, -1):
                    if board[r*7 + move] == 0:
                        board[r*7 + move] = piece
                        break
            except Exception as e:
                print(f"   ✗ FAIL: Crashed at game {i}: {e}")
                all_pass = False
                break
    else:
        print("   All 100 games completed successfully ✓")
    
    print("\n" + "="*40)
    if all_pass:
        print("✅ ALL TESTS PASSED! Agent is ready for submission.")
        print("   - Fast enough to avoid timeouts")
        print("   - Correctly detects wins/blocks")
        print("   - Handles edge cases")
        print("   - No crashes or errors")
    else:
        print("❌ SOME TESTS FAILED! Do not submit.")
    
    return all_pass

if __name__ == "__main__":
    test_agent()
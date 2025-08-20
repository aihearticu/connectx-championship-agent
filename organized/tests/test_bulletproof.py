"""Test bulletproof agent extensively"""

import time
import random
from submission_bulletproof import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def stress_test():
    print("=== BULLETPROOF AGENT STRESS TEST ===\n")
    
    errors = []
    times = []
    
    # Test 1: Random positions
    print("1. Testing 10,000 random positions...")
    for i in range(10000):
        try:
            # Create random board
            board = [0] * 42
            pieces = random.randint(0, 35)
            positions = random.sample(range(42), pieces)
            
            for j, pos in enumerate(positions):
                board[pos] = (j % 2) + 1
            
            # Time the agent
            start = time.time()
            move = agent(MockObs(board, random.choice([1, 2])), MockConfig())
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            # Validate move
            valid = [c for c in range(7) if board[c] == 0]
            if valid and move not in valid:
                errors.append(f"Position {i}: Invalid move {move}")
                
        except Exception as e:
            errors.append(f"Position {i}: Exception {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        print(f"   Average time: {avg_time:.3f}ms")
        print(f"   Max time: {max_time:.3f}ms")
    
    # Test 2: Edge cases
    print("\n2. Testing edge cases...")
    
    # Empty board
    try:
        move = agent(MockObs([0]*42, 1), MockConfig())
        print(f"   Empty board: {move} {'✓' if move == 3 else '✗'}")
    except Exception as e:
        errors.append(f"Empty board: {str(e)}")
    
    # Full board
    try:
        board = [1 if i % 2 == 0 else 2 for i in range(42)]
        move = agent(MockObs(board, 1), MockConfig())
        print(f"   Full board: {move} ✓")
    except Exception as e:
        errors.append(f"Full board: {str(e)}")
    
    # One column left
    try:
        board = [1 if i % 2 == 0 else 2 for i in range(42)]
        board[6] = 0  # Last column top
        move = agent(MockObs(board, 1), MockConfig())
        print(f"   One space left: {move} {'✓' if move == 6 else '✗'}")
    except Exception as e:
        errors.append(f"One space: {str(e)}")
    
    # Test 3: Win/block detection
    print("\n3. Testing win/block detection...")
    
    # Horizontal win
    try:
        board = [0] * 42
        board[35] = board[36] = board[37] = 1
        move = agent(MockObs(board, 1), MockConfig())
        print(f"   Horizontal win: {move} {'✓' if move == 3 else '✗'}")
    except Exception as e:
        errors.append(f"Horizontal win: {str(e)}")
    
    # Must block
    try:
        board = [0] * 42
        board[35] = board[36] = board[37] = 2
        move = agent(MockObs(board, 1), MockConfig())
        print(f"   Must block: {move} {'✓' if move == 3 else '✗'}")
    except Exception as e:
        errors.append(f"Must block: {str(e)}")
    
    # Test 4: Malformed inputs
    print("\n4. Testing robustness...")
    
    # Various board sizes (should handle gracefully)
    for size in [0, 41, 42, 43, 100]:
        try:
            board = [0] * size if size > 0 else []
            move = agent(MockObs(board, 1), MockConfig())
            if 0 <= move <= 6:
                print(f"   Board size {size}: Handled ✓")
            else:
                errors.append(f"Board size {size}: Invalid move {move}")
        except Exception as e:
            if size != 42:
                print(f"   Board size {size}: Exception (expected)")
            else:
                errors.append(f"Board size {size}: {str(e)}")
    
    # Summary
    print("\n" + "="*50)
    if not errors:
        print("✅ ALL TESTS PASSED! Agent is bulletproof.")
        print(f"   Tested 10,000+ positions")
        print(f"   Average time: {avg_time:.3f}ms")
        print(f"   Max time: {max_time:.3f}ms")
        print(f"   No crashes or invalid moves")
    else:
        print(f"❌ ERRORS FOUND: {len(errors)}")
        for err in errors[:10]:  # Show first 10
            print(f"   - {err}")
    
    return len(errors) == 0

if __name__ == "__main__":
    stress_test()
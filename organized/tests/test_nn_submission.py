"""Comprehensive testing for NN-enhanced submission"""

import time
import random
from submission_nn_fast_v1 import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def test_nn_agent():
    """Run comprehensive tests on NN agent"""
    print("=== NEURAL NETWORK AGENT VERIFICATION ===\n")
    
    all_pass = True
    config = MockConfig()
    
    # Test 1: Speed test with timing
    print("1. Performance Tests:")
    times = []
    
    for i in range(100):
        # Create random board state
        board = [0] * 42
        num_moves = random.randint(0, 25)
        
        # Place random pieces
        available_positions = list(range(42))
        for move_num in range(num_moves):
            if not available_positions:
                break
            pos = random.choice(available_positions)
            available_positions.remove(pos)
            board[pos] = (move_num % 2) + 1
        
        # Time the move
        start = time.time()
        move = agent(MockObs(board, 1), config)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        # Validate move
        if move < 0 or move >= 7:
            print(f"   ✗ Invalid move: {move}")
            all_pass = False
        elif board[move] != 0:  # Column full
            print(f"   ✗ Move {move} in full column")
            all_pass = False
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"   Average time: {avg_time:.2f}ms {'✓' if avg_time < 10 else '✗'}")
    print(f"   Max time: {max_time:.2f}ms {'✓' if max_time < 15 else '✗'}")
    print(f"   Min time: {min_time:.2f}ms")
    
    if avg_time >= 10 or max_time >= 15:
        all_pass = False
    
    # Test 2: Tactical accuracy
    print("\n2. Tactical Tests:")
    
    # Win detection
    board = [0] * 42
    board[35] = board[36] = board[37] = 1
    move = agent(MockObs(board, 1), config)
    print(f"   Win detection: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Block detection
    board = [0] * 42
    board[35] = board[36] = board[37] = 2
    move = agent(MockObs(board, 1), config)
    print(f"   Block detection: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Test 3: Opening moves
    print("\n3. Opening Tests:")
    
    # First move
    move = agent(MockObs([0]*42, 1), config)
    print(f"   First move: {move} {'✓' if move == 3 else '✗'}")
    if move != 3: all_pass = False
    
    # Second move
    board = [0] * 42
    board[38] = 2  # Opponent played center
    move = agent(MockObs(board, 1), config)
    print(f"   Second move response: {move} {'✓' if move in [2,3,4] else '✗'}")
    
    # Test 4: Stress test (complex positions)
    print("\n4. Stress Test (50 complex positions):")
    
    stress_times = []
    for i in range(50):
        # Create complex board
        board = [0] * 42
        for _ in range(random.randint(15, 30)):
            col = random.randint(0, 6)
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = random.choice([1, 2])
                    break
        
        start = time.time()
        move = agent(MockObs(board, 1), config)
        elapsed = (time.time() - start) * 1000
        stress_times.append(elapsed)
    
    stress_avg = sum(stress_times) / len(stress_times)
    stress_max = max(stress_times)
    
    print(f"   Complex position avg: {stress_avg:.2f}ms {'✓' if stress_avg < 10 else '✗'}")
    print(f"   Complex position max: {stress_max:.2f}ms {'✓' if stress_max < 15 else '✗'}")
    
    if stress_avg >= 10 or stress_max >= 15:
        all_pass = False
    
    # Test 5: Edge cases
    print("\n5. Edge Case Tests:")
    
    # Almost full board
    board = [1,2,1,2,1,2,1,
             2,1,2,1,2,1,2,
             1,2,1,2,1,2,1,
             2,1,2,1,2,1,2,
             1,2,1,2,1,2,1,
             2,1,2,1,2,1,0]
    move = agent(MockObs(board, 1), config)
    print(f"   Almost full board: {move} {'✓' if move == 6 else '✗'}")
    if move != 6: all_pass = False
    
    # Test 6: No crashes
    print("\n6. Stability Test:")
    
    crash_count = 0
    for i in range(100):
        board = [0] * 42
        # Random valid board
        for _ in range(random.randint(0, 35)):
            col = random.randint(0, 6)
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = random.choice([1, 2])
                    break
        
        try:
            move = agent(MockObs(board, random.choice([1, 2])), config)
            # Verify valid move
            valid = [c for c in range(7) if board[c] == 0]
            if valid and move not in valid:
                crash_count += 1
        except Exception as e:
            print(f"   ✗ Crash at game {i}: {e}")
            crash_count += 1
    
    print(f"   Completed without crashes: {100-crash_count}/100 {'✓' if crash_count == 0 else '✗'}")
    if crash_count > 0: all_pass = False
    
    # Summary
    print("\n" + "="*50)
    if all_pass:
        print("✅ ALL TESTS PASSED! NN agent ready for submission.")
        print("   - Fast enough (avg <10ms)")
        print("   - Tactically sound")
        print("   - No crashes")
        print("   - Handles edge cases")
    else:
        print("❌ SOME TESTS FAILED! Do not submit.")
    
    return all_pass

if __name__ == "__main__":
    test_nn_agent()
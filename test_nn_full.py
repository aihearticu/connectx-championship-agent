"""Comprehensive test of full NN agent"""

import time
import random
from submission_nn_full import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

def make_move(board, col, piece):
    """Make a move on board"""
    for row in range(5, -1, -1):
        if board[row * 7 + col] == 0:
            board[row * 7 + col] = piece
            return row
    return -1

def test_nn_agent():
    print("=== FULL NEURAL NETWORK AGENT TEST ===\n")
    
    all_pass = True
    
    # Test 1: Speed test on 10,000 positions
    print("1. Speed Test (10,000 positions):")
    times = []
    errors = 0
    
    for i in range(10000):
        board = [0] * 42
        # Create random valid position
        moves = random.randint(0, 35)
        for _ in range(moves):
            valid = [c for c in range(7) if board[c] == 0]
            if not valid:
                break
            col = random.choice(valid)
            piece = random.choice([1, 2])
            make_move(board, col, piece)
        
        try:
            start = time.time()
            move = agent(MockObs(board, random.choice([1, 2])), MockConfig())
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            # Validate move
            valid = [c for c in range(7) if board[c] == 0]
            if valid and move not in valid:
                errors += 1
                
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"   Error {i}: {str(e)}")
    
    avg_time = sum(times) / len(times) if times else 0
    max_time = max(times) if times else 0
    p99_time = sorted(times)[int(len(times) * 0.99)] if times else 0
    
    print(f"   Average: {avg_time:.3f}ms {'✓' if avg_time < 5 else '✗'}")
    print(f"   Maximum: {max_time:.3f}ms {'✓' if max_time < 20 else '✗'}")
    print(f"   99th percentile: {p99_time:.3f}ms {'✓' if p99_time < 10 else '✗'}")
    print(f"   Errors: {errors} {'✓' if errors == 0 else '✗'}")
    
    if avg_time >= 5 or max_time >= 20 or errors > 0:
        all_pass = False
    
    # Test 2: Tactical accuracy
    print("\n2. Tactical Tests:")
    
    test_cases = [
        ("Empty board", [0]*42, 1, 3),
        ("Horizontal win", None, 1, 3),
        ("Horizontal block", None, 1, 3),
        ("Vertical win", None, 1, 3),
    ]
    
    # Horizontal win setup
    board = [0] * 42
    make_move(board, 0, 1)
    make_move(board, 1, 1)
    make_move(board, 2, 1)
    test_cases[1] = ("Horizontal win", board[:], 1, 3)
    
    # Horizontal block setup
    board = [0] * 42
    make_move(board, 0, 2)
    make_move(board, 1, 2)
    make_move(board, 2, 2)
    test_cases[2] = ("Horizontal block", board[:], 1, 3)
    
    # Vertical win setup
    board = [0] * 42
    make_move(board, 3, 1)
    make_move(board, 3, 1)
    make_move(board, 3, 1)
    test_cases[3] = ("Vertical win", board[:], 1, 3)
    
    for name, board, mark, expected in test_cases:
        try:
            move = agent(MockObs(board, mark), MockConfig())
            print(f"   {name}: {move} {'✓' if move == expected else '✗'}")
            if move != expected:
                all_pass = False
        except Exception as e:
            print(f"   {name}: ERROR - {str(e)}")
            all_pass = False
    
    # Test 3: Stress test - 100 complete games
    print("\n3. Complete Game Test (100 games):")
    
    game_errors = 0
    game_times = []
    total_moves = 0
    
    for game in range(100):
        board = [0] * 42
        moves = 0
        current_player = 1
        
        while moves < 42:
            valid = [c for c in range(7) if board[c] == 0]
            if not valid:
                break
            
            try:
                start = time.time()
                if current_player == 1:
                    move = agent(MockObs(board, 1), MockConfig())
                else:
                    # Simple opponent
                    move = random.choice(valid)
                elapsed = (time.time() - start) * 1000
                
                if current_player == 1:
                    game_times.append(elapsed)
                
                if move not in valid:
                    game_errors += 1
                    break
                
                make_move(board, move, current_player)
                current_player = 3 - current_player
                moves += 1
                total_moves += 1
                
            except Exception as e:
                game_errors += 1
                break
    
    if game_times:
        game_avg = sum(game_times) / len(game_times)
        game_max = max(game_times)
        print(f"   Games completed: {100 - game_errors}/100 {'✓' if game_errors == 0 else '✗'}")
        print(f"   Average move: {game_avg:.3f}ms")
        print(f"   Max move: {game_max:.3f}ms")
        
        if game_errors > 0:
            all_pass = False
    
    # Test 4: Edge cases
    print("\n4. Edge Case Tests:")
    
    # Almost full board
    board = [1 if i % 2 == 0 else 2 for i in range(42)]
    board[6] = 0  # One space left
    try:
        move = agent(MockObs(board, 1), MockConfig())
        print(f"   One space left: {move} {'✓' if move == 6 else '✗'}")
        if move != 6:
            all_pass = False
    except:
        print(f"   One space left: ERROR")
        all_pass = False
    
    # Test 5: Performance under pressure
    print("\n5. Worst-case Performance (complex positions):")
    
    worst_times = []
    for _ in range(100):
        board = [0] * 42
        # Create complex position
        for _ in range(random.randint(25, 35)):
            valid = [c for c in range(7) if board[c] == 0]
            if not valid:
                break
            col = random.choice(valid)
            piece = random.choice([1, 2])
            make_move(board, col, piece)
        
        start = time.time()
        try:
            move = agent(MockObs(board, 1), MockConfig())
            elapsed = (time.time() - start) * 1000
            worst_times.append(elapsed)
        except:
            worst_times.append(1000)  # Penalty for crash
    
    worst_avg = sum(worst_times) / len(worst_times)
    worst_max = max(worst_times)
    
    print(f"   Complex avg: {worst_avg:.3f}ms {'✓' if worst_avg < 10 else '✗'}")
    print(f"   Complex max: {worst_max:.3f}ms {'✓' if worst_max < 20 else '✗'}")
    
    if worst_avg >= 10 or worst_max >= 20:
        all_pass = False
    
    # Summary
    print("\n" + "="*60)
    if all_pass:
        print("✅ FULL NN AGENT PASSED ALL TESTS!")
        print(f"   - Tested on 10,000+ positions")
        print(f"   - Average speed: {avg_time:.3f}ms")
        print(f"   - No crashes or timeouts")
        print(f"   - Perfect tactical play")
        print(f"   - Ready for Kaggle submission!")
        return True
    else:
        print("❌ FULL NN AGENT FAILED TESTS")
        print("   Issues found - do not submit")
        return False

if __name__ == "__main__":
    success = test_nn_agent()
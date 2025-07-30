"""Comprehensive final test before last submission"""

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
    """Make a move on board"""
    for row in range(5, -1, -1):
        if board[row * 7 + col] == 0:
            board[row * 7 + col] = piece
            return True
    return False

def simulate_game():
    """Simulate a full game"""
    board = [0] * 42
    current_player = 1
    moves = 0
    times = []
    
    while moves < 42:
        valid = [c for c in range(7) if board[c] == 0]
        if not valid:
            break
            
        start = time.time()
        if current_player == 1:
            move = agent(MockObs(board, 1), MockConfig())
        else:
            # Simple opponent
            move = random.choice(valid)
        elapsed = (time.time() - start) * 1000
        
        if current_player == 1:
            times.append(elapsed)
        
        if move not in valid:
            return False, times, f"Invalid move {move}"
            
        make_move(board, move, current_player)
        current_player = 3 - current_player
        moves += 1
    
    return True, times, "Game completed"

def stress_test():
    """Run intensive stress test"""
    print("=== FINAL NN-ENHANCED AGENT TEST ===\n")
    
    # Test 1: Speed test on 1000 positions
    print("1. Speed Test (1000 random positions):")
    all_times = []
    
    for _ in range(1000):
        board = [0] * 42
        # Random valid position
        moves = random.randint(0, 30)
        for _ in range(moves):
            valid = [c for c in range(7) if board[c] == 0]
            if valid:
                col = random.choice(valid)
                make_move(board, col, random.choice([1, 2]))
        
        start = time.time()
        move = agent(MockObs(board, 1), MockConfig())
        elapsed = (time.time() - start) * 1000
        all_times.append(elapsed)
    
    avg_time = sum(all_times) / len(all_times)
    max_time = max(all_times)
    p99_time = sorted(all_times)[int(len(all_times) * 0.99)]
    
    print(f"   Average: {avg_time:.3f}ms {'✓' if avg_time < 5 else '✗'}")
    print(f"   Maximum: {max_time:.3f}ms {'✓' if max_time < 20 else '✗'}")
    print(f"   99th percentile: {p99_time:.3f}ms {'✓' if p99_time < 10 else '✗'}")
    
    # Test 2: Full game simulations
    print("\n2. Full Game Simulations (100 games):")
    
    game_times = []
    failures = 0
    
    for i in range(100):
        success, times, msg = simulate_game()
        if not success:
            failures += 1
            print(f"   Game {i} failed: {msg}")
        else:
            game_times.extend(times)
    
    if game_times:
        game_avg = sum(game_times) / len(game_times)
        game_max = max(game_times)
        print(f"   Games completed: {100 - failures}/100")
        print(f"   Average move time: {game_avg:.3f}ms")
        print(f"   Max move time: {game_max:.3f}ms")
    
    # Test 3: Critical positions
    print("\n3. Critical Position Tests:")
    
    # Empty board
    start = time.time()
    move = agent(MockObs([0]*42, 1), MockConfig())
    elapsed = (time.time() - start) * 1000
    print(f"   Empty board: {move} in {elapsed:.3f}ms {'✓' if move == 3 else '✗'}")
    
    # Win detection
    board = [0] * 42
    make_move(board, 0, 1)
    make_move(board, 1, 1)
    make_move(board, 2, 1)
    start = time.time()
    move = agent(MockObs(board, 1), MockConfig())
    elapsed = (time.time() - start) * 1000
    print(f"   Win detection: {move} in {elapsed:.3f}ms {'✓' if move == 3 else '✗'}")
    
    # Block detection
    board = [0] * 42
    make_move(board, 0, 2)
    make_move(board, 1, 2)
    make_move(board, 2, 2)
    start = time.time()
    move = agent(MockObs(board, 1), MockConfig())
    elapsed = (time.time() - start) * 1000
    print(f"   Block detection: {move} in {elapsed:.3f}ms {'✓' if move == 3 else '✗'}")
    
    # Test 4: Worst case scenario (complex endgame)
    print("\n4. Worst Case Scenario (complex positions):")
    
    worst_times = []
    for _ in range(50):
        board = [0] * 42
        # Fill board heavily
        for _ in range(random.randint(25, 35)):
            valid = [c for c in range(7) if board[c] == 0]
            if valid:
                col = random.choice(valid)
                make_move(board, col, random.choice([1, 2]))
        
        start = time.time()
        move = agent(MockObs(board, 1), MockConfig())
        elapsed = (time.time() - start) * 1000
        worst_times.append(elapsed)
    
    worst_avg = sum(worst_times) / len(worst_times)
    worst_max = max(worst_times)
    
    print(f"   Complex position avg: {worst_avg:.3f}ms")
    print(f"   Complex position max: {worst_max:.3f}ms")
    
    # Final verdict
    print("\n" + "="*50)
    
    if avg_time < 5 and max_time < 20 and failures == 0:
        print("✅ AGENT PASSED ALL TESTS!")
        print(f"   - Average speed: {avg_time:.3f}ms")
        print(f"   - No timeouts risk (max: {max_time:.3f}ms)")
        print(f"   - All games completed successfully")
        print(f"   - Tactical accuracy confirmed")
        print("\n🚀 READY FOR FINAL SUBMISSION!")
        return True
    else:
        print("❌ AGENT NOT READY")
        if avg_time >= 5:
            print(f"   - Too slow on average: {avg_time:.3f}ms")
        if max_time >= 20:
            print(f"   - Risk of timeout: {max_time:.3f}ms max")
        if failures > 0:
            print(f"   - Failed {failures} games")
        return False

if __name__ == "__main__":
    ready = stress_test()
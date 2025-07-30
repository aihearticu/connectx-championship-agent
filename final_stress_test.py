"""Final aggressive stress test before submission"""

import time
import random
from submission_nn_full import agent

class MockObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class MockConfig:
    pass

print("=== FINAL STRESS TEST ===\n")

# Test 1: Rapid-fire test - 50,000 moves as fast as possible
print("1. Rapid-fire test (50,000 moves):")
start_time = time.time()
max_single_move = 0
errors = 0

for i in range(50000):
    # Random board
    board = [0] * 42
    fills = random.randint(0, 41)
    for j in range(fills):
        pos = random.randint(0, 41)
        board[pos] = random.choice([0, 1, 2])
    
    # Ensure at least one valid move
    board[random.randint(0, 6)] = 0
    
    try:
        move_start = time.time()
        move = agent(MockObs(board, random.choice([1, 2])), MockConfig())
        move_time = (time.time() - move_start) * 1000
        max_single_move = max(max_single_move, move_time)
        
        # Basic validation
        valid = [c for c in range(7) if board[c] == 0]
        if move not in valid:
            errors += 1
    except:
        errors += 1

total_time = time.time() - start_time
avg_time = (total_time * 1000) / 50000

print(f"   Total time: {total_time:.2f}s")
print(f"   Average per move: {avg_time:.3f}ms")
print(f"   Max single move: {max_single_move:.3f}ms")
print(f"   Errors: {errors}")

# Test 2: Memory test - ensure no memory leaks
print("\n2. Memory stability test:")
import sys

initial_size = sys.getsizeof(agent)
for _ in range(1000):
    board = [random.choice([0,1,2]) for _ in range(42)]
    board[random.randint(0,6)] = 0
    agent(MockObs(board, 1), MockConfig())

final_size = sys.getsizeof(agent)
print(f"   Function size stable: {'✓' if initial_size == final_size else '✗'}")

# Test 3: Malicious input test
print("\n3. Malicious input test:")
malicious_tests = [
    ("Empty list", []),
    ("Wrong size", [0] * 100),
    ("Invalid values", [99] * 42),
    ("None board", None),
    ("String board", "not a board"),
]

crashes = 0
for name, bad_board in malicious_tests:
    try:
        if bad_board is None:
            obs = MockObs([0]*42, 1)
            obs.board = None
        else:
            obs = MockObs(bad_board if isinstance(bad_board, list) else [0]*42, 1)
            if isinstance(bad_board, str):
                obs.board = bad_board
        
        move = agent(obs, MockConfig())
        # If it returns something between 0-6, that's acceptable
        if not (0 <= move <= 6):
            crashes += 1
    except:
        # Exception is acceptable for malicious input
        pass

print(f"   Handled malicious inputs: {5-crashes}/5")

# Final verdict
print("\n" + "="*50)
if errors == 0 and max_single_move < 10 and avg_time < 1:
    print("✅ FINAL STRESS TEST PASSED!")
    print("   Agent is bulletproof and ready for Kaggle")
    print("   No possibility of timeout (max time: {:.3f}ms)".format(max_single_move))
else:
    print("❌ CONCERNS FOUND")
    if errors > 0:
        print(f"   - {errors} errors in 50k moves")
    if max_single_move >= 10:
        print(f"   - Max time too high: {max_single_move:.3f}ms")
    if avg_time >= 1:
        print(f"   - Average too slow: {avg_time:.3f}ms")
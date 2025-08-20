#!/usr/bin/env python3
"""Final comprehensive test of Connect X agent"""

from kaggle_environments import make, evaluate
import submission
import time

print("=== FINAL COMPREHENSIVE TEST ===\n")

# Test 1: Manual games against random
print("Test 1: Manual games vs Random (50 games)")
wins = 0
start = time.time()

for i in range(50):
    env = make("connectx")
    env.reset()
    
    # Alternate who goes first
    if i % 2 == 0:
        env.run([submission.agent, "random"])
        if env.state[0].reward == 1:
            wins += 1
    else:
        env.run(["random", submission.agent])
        if env.state[1].reward == 1:
            wins += 1

elapsed = time.time() - start
print(f"Win rate: {wins}/50 ({wins*2}%)")
print(f"Time: {elapsed:.1f}s ({elapsed/50:.3f}s per game)")

# Test 2: Against negamax
print("\nTest 2: vs Negamax baseline (20 games)")
wins = 0
start = time.time()

for i in range(20):
    env = make("connectx")
    env.reset()
    
    if i % 2 == 0:
        env.run([submission.agent, "negamax"])
        if env.state[0].reward == 1:
            wins += 1
    else:
        env.run(["negamax", submission.agent])
        if env.state[1].reward == 1:
            wins += 1

elapsed = time.time() - start
print(f"Win rate: {wins}/20 ({wins*5}%)")
print(f"Time: {elapsed:.1f}s")

# Test 3: Win/block detection verification
print("\nTest 3: Tactical tests")
test_passed = 0

# Win in 1
board = [0]*42
board[35] = 1
board[36] = 1  
board[37] = 1
obs = type('', (), {'board': board, 'mark': 1})()
config = type('', (), {'rows': 6, 'columns': 7, 'inarow': 4})()
move = submission.agent(obs, config)
if move == 3:
    print("✓ Win detection: PASS")
    test_passed += 1
else:
    print("✗ Win detection: FAIL")

# Block in 1
board = [0]*42
board[35] = 2
board[36] = 2
board[37] = 2
obs.board = board
move = submission.agent(obs, config)
if move == 3:
    print("✓ Block detection: PASS")
    test_passed += 1
else:
    print("✗ Block detection: FAIL")

# Test 4: Sample games
print("\n" + "="*50)
print("Sample game (Agent vs Random):")
env = make("connectx")
env.reset()
env.run([submission.agent, "random"])
print(env.render(mode="ansi"))

# Performance summary
print("\n" + "="*50)
print("PERFORMANCE SUMMARY:")
print(f"- Win rate vs Random: {wins*2}%")
print(f"- Tactical tests: {test_passed}/2")

if wins >= 45:  # 90%+
    print("\n✓ EXCELLENT performance - Ready for TOP 3!")
    print("✓ Agent shows championship-level play")
elif wins >= 40:  # 80%+
    print("\n✓ GOOD performance - Competitive agent")
    print("⚠ May need fine-tuning for top 3")
else:
    print("\n✗ Performance needs improvement")
    print("✗ Not ready for submission")

# Leaderboard reference
print("\n" + "="*50)
print("LEADERBOARD REFERENCE:")
print("Top 3 scores: 1827.1, 1798.6, 1766.4")
print("To achieve top 3, agent needs consistent wins against strong opponents")
#!/usr/bin/env python3
"""Test agent from both sides"""

from kaggle_environments import evaluate
import submission
import time

print("Testing Connect X Agent Performance\n")

# Test as Player 1
print("As Player 1 (10 games):")
start = time.time()
results1 = evaluate("connectx", [submission.agent, "random"], num_episodes=10)
wins1 = sum(1 for r in results1[0] if r == 1)
time1 = time.time() - start
print(f"Wins: {wins1}/10 ({wins1*10}%)")
print(f"Time: {time1:.1f}s")

# Test as Player 2
print("\nAs Player 2 (10 games):")
start = time.time()
results2 = evaluate("connectx", ["random", submission.agent], num_episodes=10)
wins2 = sum(1 for r in results2[1] if r == 1)
time2 = time.time() - start
print(f"Wins: {wins2}/10 ({wins2*10}%)")
print(f"Time: {time2:.1f}s")

# Total
total_wins = wins1 + wins2
print(f"\nTotal: {total_wins}/20 ({total_wins*5}%)")
print(f"Average time per game: {(time1+time2)/20:.2f}s")

if total_wins >= 18:
    print("\n✓ Excellent performance!")
elif total_wins >= 15:
    print("\n✓ Good performance")
else:
    print("\n✗ Needs improvement")
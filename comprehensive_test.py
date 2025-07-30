#!/usr/bin/env python3
"""Comprehensive agent testing"""

from kaggle_environments import evaluate, make
import submission
import time

print("=== ConnectX Agent Comprehensive Testing ===\n")

# Test 1: Against random opponent
print("Test 1: Against Random (50 games)")
start = time.time()
results = evaluate("connectx", [submission.agent, "random"], num_episodes=50)
wins_as_p1 = sum(1 for r in results[0] if r == 1)
wins_as_p2 = sum(1 for r in results[1] if r == 1)
total_wins = wins_as_p1 + wins_as_p2
elapsed = time.time() - start

print(f"Playing as Player 1: {wins_as_p1}/50 wins")
print(f"Playing as Player 2: {wins_as_p2}/50 wins") 
print(f"Total win rate: {total_wins}/100 ({total_wins}%)")
print(f"Time: {elapsed:.1f}s ({elapsed/100:.3f}s per game)")

# Test 2: Against negamax baseline
print("\nTest 2: Against Negamax baseline (20 games)")
start = time.time()
results = evaluate("connectx", [submission.agent, "negamax"], num_episodes=10)
wins = sum(1 for r in results[0] if r == 1)
results2 = evaluate("connectx", ["negamax", submission.agent], num_episodes=10)
wins += sum(1 for r in results2[1] if r == 1)
elapsed = time.time() - start

print(f"Win rate: {wins}/20 ({wins*5}%)")
print(f"Time: {elapsed:.1f}s")

# Test 3: Sample games
print("\n" + "="*50)
print("Sample game 1: Agent (P1) vs Random (P2)")
env = make("connectx")
env.reset()
env.run([submission.agent, "random"])
print(env.render(mode="ansi"))

print("\nSample game 2: Random (P1) vs Agent (P2)")
env.reset()
env.run(["random", submission.agent])
print(env.render(mode="ansi"))

# Performance summary
print("\n" + "="*50)
print("PERFORMANCE SUMMARY:")
if total_wins >= 95:
    print("✓ Excellent performance against random (95%+)")
    print("✓ Ready for top-tier competition")
elif total_wins >= 85:
    print("✓ Good performance against random (85%+)")
    print("⚠ May need optimization for top 3")
else:
    print("✗ Performance needs improvement")
    print("✗ Not ready for submission")
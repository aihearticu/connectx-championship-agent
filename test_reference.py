#!/usr/bin/env python3
"""Test reference agents to verify test setup"""

from kaggle_environments import evaluate
import time

print("Testing Reference Agents\n")

# Test 1: Random vs Random (should be ~50/50)
print("Test 1: Random vs Random (20 games)")
start = time.time()
results = evaluate("connectx", ["random", "random"], num_episodes=20)
wins = sum(1 for r in results[0] if r == 1)
print(f"Player 1 wins: {wins}/20 ({wins*5}%)")
print(f"Time: {time.time() - start:.1f}s")

# Test 2: Negamax vs Random (should win most)
print("\nTest 2: Negamax vs Random (10 games each side)")
start = time.time()
results1 = evaluate("connectx", ["negamax", "random"], num_episodes=10)
wins1 = sum(1 for r in results1[0] if r == 1)
results2 = evaluate("connectx", ["random", "negamax"], num_episodes=10)
wins2 = sum(1 for r in results2[1] if r == 1)
total_negamax = wins1 + wins2
print(f"Negamax wins: {total_negamax}/20 ({total_negamax*5}%)")
print(f"Time: {time.time() - start:.1f}s")

# Test 3: My agent vs Random
print("\nTest 3: My agent vs Random (10 games each side)")
import submission
start = time.time()
results1 = evaluate("connectx", [submission.agent, "random"], num_episodes=10)
wins1 = sum(1 for r in results1[0] if r == 1)
results2 = evaluate("connectx", ["random", submission.agent], num_episodes=10)
wins2 = sum(1 for r in results2[1] if r == 1)
total_myagent = wins1 + wins2
print(f"My agent wins: {total_myagent}/20 ({total_myagent*5}%)")
print(f"Time: {time.time() - start:.1f}s")

# Test 4: Win/loss/draw breakdown
print("\nTest 4: Detailed results (My agent as Player 1 vs Random)")
results = evaluate("connectx", [submission.agent, "random"], num_episodes=10)
wins = sum(1 for r in results[0] if r == 1)
losses = sum(1 for r in results[0] if r == -1)
draws = sum(1 for r in results[0] if r == 0)
print(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")

# Show the actual results
print(f"Raw results: {results[0]}")
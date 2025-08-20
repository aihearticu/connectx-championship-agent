#!/usr/bin/env python3
"""Test the ultimate agent"""

from kaggle_environments import make
from ultimate_agent import agent as ultimate_agent
import submission
import time

print("=== Testing Ultimate Connect X Agent ===\n")

# Speed test
print("1. Speed test (100 positions)")
env = make("connectx")
max_time = 0
total_time = 0
positions_tested = 0

import random
for _ in range(100):
    env.reset()
    
    # Create random position
    moves = random.randint(0, 20)
    for _ in range(moves):
        if env.done:
            break
        valid = [c for c in range(7) if env.state[0].observation.board[c] == 0]
        if not valid:
            break
        env.step([random.choice(valid), None])
    
    if not env.done:
        obs = env.state[0].observation
        config = env.configuration
        
        start = time.time()
        move = ultimate_agent(obs, config)
        elapsed = time.time() - start
        
        total_time += elapsed
        max_time = max(max_time, elapsed)
        positions_tested += 1

if positions_tested > 0:
    print(f"Average time: {(total_time/positions_tested)*1000:.3f}ms")
    print(f"Max time: {max_time*1000:.3f}ms")
    print(f"✓ Fast enough!" if max_time < 0.01 else "⚠ May be too slow")

# Win rate test
print("\n2. Performance test (50 games)")
wins = 0
for i in range(50):
    env.reset()
    if i % 2 == 0:
        env.run([ultimate_agent, "random"])
        if env.state[0].reward == 1:
            wins += 1
    else:
        env.run(["random", ultimate_agent])
        if env.state[1].reward == 1:
            wins += 1

print(f"Win rate vs Random: {wins}/50 ({wins*2}%)")

# Test vs negamax
print("\n3. Test vs Negamax (10 games)")
negamax_wins = 0
for i in range(10):
    env.reset()
    if i % 2 == 0:
        env.run([ultimate_agent, "negamax"])
        if env.state[0].reward == 1:
            negamax_wins += 1
    else:
        env.run(["negamax", ultimate_agent])
        if env.state[1].reward == 1:
            negamax_wins += 1

print(f"Win rate vs Negamax: {negamax_wins}/10 ({negamax_wins*10}%)")

# Head to head vs current best
print("\n4. Head-to-head vs Ultra-Fast Agent (10 games)")
ultimate_wins = 0
for i in range(10):
    env.reset()
    if i % 2 == 0:
        env.run([ultimate_agent, submission.agent])
        if env.state[0].reward == 1:
            ultimate_wins += 1
    else:
        env.run([submission.agent, ultimate_agent])
        if env.state[1].reward == 1:
            ultimate_wins += 1

print(f"Ultimate Agent wins: {ultimate_wins}/10 ({ultimate_wins*10}%)")

# Tactical tests
print("\n5. Tactical tests")

# Win in 1
board = [0]*42
board[35] = 1
board[36] = 1
board[37] = 1
obs = type('', (), {'board': board, 'mark': 1})()
config = type('', (), {'rows': 6, 'columns': 7, 'inarow': 4})()
move = ultimate_agent(obs, config)
print(f"Win detection: {'✓ PASS' if move == 3 else '✗ FAIL'}")

# Block in 1
board = [0]*42
board[35] = 2
board[36] = 2
board[37] = 2
obs.board = board
move = ultimate_agent(obs, config)
print(f"Block detection: {'✓ PASS' if move == 3 else '✗ FAIL'}")

# Opening book test
board = [0]*42
board[38] = 1  # First move in center
board[39] = 2  # Response
board[40] = 1  # Continue center
obs.board = board
obs.mark = 2
move = ultimate_agent(obs, config)
print(f"Opening book: {'✓ Working' if move == 2 else '⚠ Not using book'} (played {move})")

# Summary
print("\n" + "="*50)
print("ULTIMATE AGENT SUMMARY:")
print(f"- Speed: {(total_time/positions_tested)*1000:.3f}ms avg, {max_time*1000:.3f}ms max")
print(f"- Win rate vs Random: {wins*2}%")
print(f"- Win rate vs Negamax: {negamax_wins*10}%")
print(f"- Head-to-head performance: {ultimate_wins*10}%")
print("\nReady for Top 3 championship submission!")
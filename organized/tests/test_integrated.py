"""Test Integrated Championship Agent"""

import time
from kaggle_environments import evaluate
from integrated_championship_agent import agent

print("="*60)
print("TESTING INTEGRATED CHAMPIONSHIP AGENT")
print("="*60)

# Basic test
class TestObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class TestConfig:
    def __init__(self):
        self.columns = 7
        self.rows = 6

# Test first move
obs = TestObs([0]*42, 1)
config = TestConfig()

print("\n1. BASIC TESTS")
move = agent(obs, config)
print(f"First move: {move} (should be 3)")

# Test win detection
obs.board = [0]*35 + [1,1,1,0,0,0,0]
move = agent(obs, config)
print(f"Win detection: {move} (should be 3)")

# Test block
obs.board = [0]*35 + [2,2,2,0,0,0,0]
move = agent(obs, config)
print(f"Block detection: {move} (should be 3)")

# Speed test
print("\n2. SPEED TEST")
positions = [
    ([0]*42, "Empty"),
    ([0]*35 + [1,2,1,2,1,2,0], "Early"),
    ([1,2,1,2,1,2,0]*3 + [0]*21, "Mid"),
]

for board, desc in positions:
    obs.board = board
    start = time.time()
    move = agent(obs, config)
    elapsed = time.time() - start
    print(f"{desc:10} - {elapsed:.4f}s - move: {move}")

# Performance test
print("\n3. PERFORMANCE (30 games)")

# vs Random
print("vs Random...")
wins = 0
for i in range(20):
    try:
        result = evaluate("connectx", [agent, "random"], num_episodes=1)
        if result[0][0] > result[0][1]:
            wins += 1
    except:
        pass

print(f"Win rate vs Random: {wins}/20 = {wins*5}%")

# vs Negamax
print("\nvs Negamax...")
wins = 0
for i in range(10):
    try:
        result = evaluate("connectx", [agent, "negamax"], num_episodes=1)
        if result[0][0] > result[0][1]:
            wins += 1
    except:
        pass

print(f"Win rate vs Negamax: {wins}/10 = {wins*10}%")

print("\n" + "="*60)
print("READY FOR SUBMISSION" if wins >= 7 else "NEEDS IMPROVEMENT")
print("="*60)
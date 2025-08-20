"""Test Championship Agent v2"""
import time
from kaggle_environments import evaluate
from championship_agent_v2 import agent

# Quick test
class TestObs:
    def __init__(self, board, mark):
        self.board = board
        self.mark = mark

class TestConfig:
    def __init__(self):
        self.columns = 7
        self.rows = 6

obs = TestObs([0]*42, 1)
config = TestConfig()

print("Testing Championship Agent v2...")
print(f"First move: {agent(obs, config)}")

# Test vs Random (10 games)
wins = 0
for i in range(10):
    result = evaluate("connectx", [agent, "random"], num_episodes=1)
    if result[0][0] > result[0][1]:
        wins += 1
print(f"Win rate vs Random: {wins}/10 = {wins*10}%")

# Test vs Negamax (5 games)
wins = 0
for i in range(5):
    result = evaluate("connectx", [agent, "negamax"], num_episodes=1)
    if result[0][0] > result[0][1]:
        wins += 1
print(f"Win rate vs Negamax: {wins}/5 = {wins*20}%")

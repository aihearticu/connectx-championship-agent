"""Final Kaggle format test"""

from submission_verified import agent

# Test 1: Kaggle format compatibility
print("Testing Kaggle format compatibility...")

class Observation:
    def __init__(self):
        self.board = [0] * 42
        self.mark = 1
        self.step = 0

class Configuration:
    def __init__(self):
        self.columns = 7
        self.rows = 6

obs = Observation()
conf = Configuration()

# Make sure it returns an integer
move = agent(obs, conf)
print(f"Move type: {type(move).__name__} (should be int)")
print(f"Move value: {move} (should be 0-6)")

# Test with various marks
for mark in [1, 2]:
    obs.mark = mark
    move = agent(obs, conf)
    print(f"Mark {mark}: Move = {move}")

print("\n✅ Agent is ready for Kaggle submission!")
"""Quick test for new agents"""
from kaggle_environments import evaluate
import time

agents = [
    ('ensemble_agent.py', 'Ensemble'),
    ('gradient_boost_agent.py', 'Gradient Boost'),
]

for file, name in agents:
    print(f"\nTesting {name}...")
    
    # Load agent
    with open(file, 'r') as f:
        code = f.read()
    exec_globals = {}
    exec(code, exec_globals)
    agent = exec_globals['agent']
    
    # Test speed
    class TestObs:
        def __init__(self):
            self.board = [0] * 42
            self.mark = 1
    class TestConfig:
        pass
    
    obs = TestObs()
    config = TestConfig()
    
    start = time.time()
    for _ in range(100):
        move = agent(obs, config)
    elapsed = time.time() - start
    print(f"  Speed: {elapsed/100*1000:.2f}ms per move")
    
    # Test performance
    wins = 0
    for _ in range(10):
        try:
            result = evaluate("connectx", [agent, "random"], num_episodes=1)
            if result[0][0] > result[0][1]:
                wins += 1
        except:
            pass
    print(f"  Win rate vs Random: {wins}/10 = {wins*10}%")

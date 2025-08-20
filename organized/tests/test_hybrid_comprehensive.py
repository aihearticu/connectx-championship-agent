"""Test all hybrid agents comprehensively"""

from kaggle_environments import evaluate
import time

agents = [
    ('championship_final.py', 'Championship'),
    ('advanced_ultimate_agent.py', 'Advanced Ultimate'),
    ('gradient_boost_agent.py', 'Gradient Boost'),
    ('ensemble_agent.py', 'Ensemble'),
]

print("="*70)
print("COMPREHENSIVE AGENT TESTING")
print("="*70)

for file, name in agents:
    print(f"\n{name} ({file})")
    print("-"*50)
    
    try:
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
        
        # Speed test
        times = []
        for _ in range(10):
            start = time.time()
            move = agent(obs, config)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times) * 1000
        max_time = max(times) * 1000
        print(f"  Speed: avg={avg_time:.2f}ms, max={max_time:.2f}ms")
        
        # Performance test
        wins = 0
        for _ in range(20):
            try:
                result = evaluate("connectx", [agent, "random"], num_episodes=1)
                if result[0][0] > result[0][1]:
                    wins += 1
            except:
                pass
        
        print(f"  vs Random: {wins}/20 = {wins*5}%")
        
        # vs Negamax (fewer games)
        wins = 0
        for _ in range(5):
            try:
                result = evaluate("connectx", [agent, "negamax"], num_episodes=1)
                if result[0][0] > result[0][1]:
                    wins += 1
            except:
                pass
        
        print(f"  vs Negamax: {wins}/5 = {wins*20}%")
        
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)

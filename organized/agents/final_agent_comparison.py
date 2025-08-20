"""
Final Agent Comparison and Testing
Evaluates all agents to find the best one
"""

import time
import json
from kaggle_environments import evaluate, make

# List of agents to test
AGENTS = [
    ('submission.py', 'Championship Final'),
    ('championship_final.py', 'Championship Final Alt'),
    ('integrated_championship_agent.py', 'Integrated Championship'),
    ('deep_rl_agent.py', 'Deep RL Agent'),
]

def test_agent_speed(agent_file):
    """Test agent execution speed"""
    try:
        # Import agent
        with open(agent_file, 'r') as f:
            code = f.read()
        
        exec_globals = {}
        exec(code, exec_globals)
        agent_func = exec_globals['agent']
        
        # Test positions
        test_boards = [
            [0] * 42,  # Empty
            [0]*35 + [1,2,1,2,1,2,0],  # Early game
            [1,2,1,2,1,2,0]*3 + [0]*21,  # Mid game
        ]
        
        class TestObs:
            def __init__(self, board, mark):
                self.board = board
                self.mark = mark
        
        class TestConfig:
            def __init__(self):
                self.columns = 7
                self.rows = 6
        
        times = []
        config = TestConfig()
        
        for board in test_boards:
            obs = TestObs(board, 1)
            
            start = time.time()
            move = agent_func(obs, config)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        return {
            'avg_time': avg_time,
            'max_time': max_time,
            'times': times
        }
    except Exception as e:
        return {
            'error': str(e),
            'avg_time': 999,
            'max_time': 999
        }

def test_agent_performance(agent_file, num_games=10):
    """Test agent win rate"""
    try:
        # Import agent
        with open(agent_file, 'r') as f:
            code = f.read()
        
        exec_globals = {}
        exec(code, exec_globals)
        agent_func = exec_globals['agent']
        
        # Test vs Random
        random_wins = 0
        for _ in range(num_games):
            try:
                result = evaluate("connectx", [agent_func, "random"], num_episodes=1)
                if result[0][0] > result[0][1]:
                    random_wins += 1
            except:
                pass
        
        # Test vs Negamax (fewer games)
        negamax_wins = 0
        for _ in range(5):
            try:
                result = evaluate("connectx", [agent_func, "negamax"], num_episodes=1)
                if result[0][0] > result[0][1]:
                    negamax_wins += 1
            except:
                pass
        
        return {
            'vs_random': random_wins / num_games * 100,
            'vs_negamax': negamax_wins / 5 * 100,
            'random_games': num_games,
            'negamax_games': 5
        }
    except Exception as e:
        return {
            'error': str(e),
            'vs_random': 0,
            'vs_negamax': 0
        }

def main():
    """Compare all agents"""
    print("="*70)
    print("FINAL AGENT COMPARISON")
    print("="*70)
    
    results = {}
    
    for agent_file, agent_name in AGENTS:
        print(f"\nTesting: {agent_name} ({agent_file})")
        print("-" * 50)
        
        # Test speed
        print("Testing speed...")
        speed_results = test_agent_speed(agent_file)
        
        if 'error' not in speed_results:
            print(f"  Average time: {speed_results['avg_time']*1000:.2f}ms")
            print(f"  Maximum time: {speed_results['max_time']*1000:.2f}ms")
        else:
            print(f"  Error: {speed_results['error']}")
        
        # Test performance
        print("Testing performance...")
        perf_results = test_agent_performance(agent_file, num_games=20)
        
        if 'error' not in perf_results:
            print(f"  vs Random: {perf_results['vs_random']:.1f}%")
            print(f"  vs Negamax: {perf_results['vs_negamax']:.1f}%")
        else:
            print(f"  Error: {perf_results['error']}")
        
        # Calculate score
        score = 0
        if 'error' not in speed_results:
            if speed_results['max_time'] < 0.01:
                score += 30
            elif speed_results['max_time'] < 0.05:
                score += 20
            elif speed_results['max_time'] < 0.1:
                score += 10
        
        if 'error' not in perf_results:
            score += perf_results['vs_random'] * 0.3
            score += perf_results['vs_negamax'] * 0.4
        
        results[agent_name] = {
            'file': agent_file,
            'speed': speed_results,
            'performance': perf_results,
            'score': score
        }
        
        print(f"  Overall Score: {score:.1f}/100")
    
    # Find best agent
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
    
    for rank, (name, data) in enumerate(sorted_results, 1):
        print(f"\n{rank}. {name}")
        print(f"   Score: {data['score']:.1f}/100")
        print(f"   File: {data['file']}")
    
    best_agent = sorted_results[0]
    print(f"\n✓ Best Agent: {best_agent[0]} ({best_agent[1]['file']})")

if __name__ == "__main__":
    main()

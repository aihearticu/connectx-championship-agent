#!/usr/bin/env python3
"""
Comprehensive testing suite for Connect X strategies
Tests multiple agent implementations to find the best approach
"""

from kaggle_environments import make, evaluate
import time
import numpy as np

# Import our agents
import submission  # Current ultra-fast agent
from top3_agent import agent as top3_agent

def test_agent_performance(agent_func, agent_name, num_games=50):
    """Test an agent's performance against various opponents"""
    print(f"\n{'='*60}")
    print(f"Testing: {agent_name}")
    print(f"{'='*60}")
    
    results = {
        'vs_random': {'wins': 0, 'games': 0, 'time': 0},
        'vs_negamax': {'wins': 0, 'games': 0, 'time': 0},
        'speed': {'total_time': 0, 'max_time': 0, 'moves': 0}
    }
    
    # Test vs Random
    print(f"\n1. Testing vs Random ({num_games} games)...")
    start_time = time.time()
    
    for i in range(num_games):
        env = make("connectx")
        env.reset()
        
        if i % 2 == 0:
            env.run([agent_func, "random"])
            if env.state[0].reward == 1:
                results['vs_random']['wins'] += 1
        else:
            env.run(["random", agent_func])
            if env.state[1].reward == 1:
                results['vs_random']['wins'] += 1
        
        results['vs_random']['games'] += 1
    
    results['vs_random']['time'] = time.time() - start_time
    win_rate = (results['vs_random']['wins'] / results['vs_random']['games']) * 100
    print(f"   Win rate: {results['vs_random']['wins']}/{results['vs_random']['games']} ({win_rate:.1f}%)")
    print(f"   Time: {results['vs_random']['time']:.2f}s")
    
    # Test vs Negamax
    print(f"\n2. Testing vs Negamax (20 games)...")
    start_time = time.time()
    
    for i in range(20):
        env = make("connectx")
        env.reset()
        
        if i % 2 == 0:
            env.run([agent_func, "negamax"])
            if env.state[0].reward == 1:
                results['vs_negamax']['wins'] += 1
        else:
            env.run(["negamax", agent_func])
            if env.state[1].reward == 1:
                results['vs_negamax']['wins'] += 1
        
        results['vs_negamax']['games'] += 1
    
    results['vs_negamax']['time'] = time.time() - start_time
    win_rate = (results['vs_negamax']['wins'] / results['vs_negamax']['games']) * 100
    print(f"   Win rate: {results['vs_negamax']['wins']}/{results['vs_negamax']['games']} ({win_rate:.1f}%)")
    print(f"   Time: {results['vs_negamax']['time']:.2f}s")
    
    # Speed test
    print(f"\n3. Speed test (100 random positions)...")
    env = make("connectx")
    max_time = 0
    total_time = 0
    moves_tested = 0
    
    import random
    for _ in range(100):
        env.reset()
        
        # Create random position
        for _ in range(random.randint(0, 20)):
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
            try:
                move = agent_func(obs, config)
                elapsed = time.time() - start
                total_time += elapsed
                max_time = max(max_time, elapsed)
                moves_tested += 1
            except Exception as e:
                print(f"   Error during speed test: {e}")
    
    if moves_tested > 0:
        avg_time = (total_time / moves_tested) * 1000
        max_time_ms = max_time * 1000
        print(f"   Average time: {avg_time:.3f}ms")
        print(f"   Max time: {max_time_ms:.3f}ms")
        print(f"   Moves tested: {moves_tested}")
    
    # Tactical tests
    print(f"\n4. Tactical tests...")
    tactical_passed = 0
    
    # Win in 1
    board = [0]*42
    board[35] = 1
    board[36] = 1
    board[37] = 1
    obs = type('', (), {'board': board, 'mark': 1})()
    config = type('', (), {'rows': 6, 'columns': 7, 'inarow': 4})()
    
    try:
        move = agent_func(obs, config)
        if move == 3:
            print(f"   ✓ Win detection: PASS")
            tactical_passed += 1
        else:
            print(f"   ✗ Win detection: FAIL (played {move})")
    except Exception as e:
        print(f"   ✗ Win detection: ERROR - {e}")
    
    # Block in 1
    board = [0]*42
    board[35] = 2
    board[36] = 2
    board[37] = 2
    obs.board = board
    
    try:
        move = agent_func(obs, config)
        if move == 3:
            print(f"   ✓ Block detection: PASS")
            tactical_passed += 1
        else:
            print(f"   ✗ Block detection: FAIL (played {move})")
    except Exception as e:
        print(f"   ✗ Block detection: ERROR - {e}")
    
    # Summary
    print(f"\n5. Summary for {agent_name}:")
    print(f"   - vs Random: {results['vs_random']['wins']}/{results['vs_random']['games']} ({(results['vs_random']['wins']/results['vs_random']['games']*100):.1f}%)")
    print(f"   - vs Negamax: {results['vs_negamax']['wins']}/{results['vs_negamax']['games']} ({(results['vs_negamax']['wins']/results['vs_negamax']['games']*100):.1f}%)")
    print(f"   - Speed: {avg_time:.3f}ms avg, {max_time_ms:.3f}ms max")
    print(f"   - Tactical: {tactical_passed}/2 tests passed")
    
    return results

def compare_agents_head_to_head(agent1_func, agent1_name, agent2_func, agent2_name, num_games=20):
    """Compare two agents directly against each other"""
    print(f"\n{'='*60}")
    print(f"Head-to-head: {agent1_name} vs {agent2_name}")
    print(f"{'='*60}")
    
    agent1_wins = 0
    agent2_wins = 0
    draws = 0
    
    for i in range(num_games):
        env = make("connectx")
        env.reset()
        
        try:
            if i % 2 == 0:
                env.run([agent1_func, agent2_func])
                if env.state[0].reward == 1:
                    agent1_wins += 1
                elif env.state[1].reward == 1:
                    agent2_wins += 1
                else:
                    draws += 1
            else:
                env.run([agent2_func, agent1_func])
                if env.state[0].reward == 1:
                    agent2_wins += 1
                elif env.state[1].reward == 1:
                    agent1_wins += 1
                else:
                    draws += 1
        except Exception as e:
            print(f"Error in game {i+1}: {e}")
    
    print(f"\nResults after {num_games} games:")
    print(f"{agent1_name}: {agent1_wins} wins ({agent1_wins/num_games*100:.1f}%)")
    print(f"{agent2_name}: {agent2_wins} wins ({agent2_wins/num_games*100:.1f}%)")
    print(f"Draws: {draws}")
    
    if agent1_wins > agent2_wins:
        print(f"\nWinner: {agent1_name}")
    elif agent2_wins > agent1_wins:
        print(f"\nWinner: {agent2_name}")
    else:
        print(f"\nResult: Draw")

if __name__ == "__main__":
    print("CONNECT X STRATEGY TESTING SUITE")
    print("="*60)
    
    # Test all agents
    agents_to_test = [
        (submission.agent, "Ultra-Fast Agent (current submission)"),
        (top3_agent, "Top 3 Agent (with opening book)")
    ]
    
    all_results = {}
    for agent_func, agent_name in agents_to_test:
        results = test_agent_performance(agent_func, agent_name, num_games=30)
        all_results[agent_name] = results
    
    # Head-to-head comparison
    if len(agents_to_test) >= 2:
        compare_agents_head_to_head(
            agents_to_test[0][0], agents_to_test[0][1],
            agents_to_test[1][0], agents_to_test[1][1],
            num_games=20
        )
    
    # Final recommendations
    print("\n" + "="*60)
    print("FINAL ANALYSIS AND RECOMMENDATIONS")
    print("="*60)
    
    # Determine best agent
    best_agent = None
    best_score = 0
    
    for agent_name, results in all_results.items():
        # Calculate overall score
        random_win_rate = results['vs_random']['wins'] / results['vs_random']['games']
        negamax_win_rate = results['vs_negamax']['wins'] / results['vs_negamax']['games']
        
        # Weight: 40% random, 60% negamax (harder opponent)
        overall_score = (random_win_rate * 0.4 + negamax_win_rate * 0.6) * 100
        
        print(f"\n{agent_name}:")
        print(f"  Overall score: {overall_score:.1f}")
        
        if overall_score > best_score:
            best_score = overall_score
            best_agent = agent_name
    
    print(f"\n🏆 RECOMMENDED AGENT: {best_agent}")
    print(f"   Score: {best_score:.1f}/100")
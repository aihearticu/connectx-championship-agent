#!/usr/bin/env python3
"""Test improved championship agent"""

import time
from kaggle_environments import make
from submission import agent

def test_agent(num_games=10):
    """Test agent performance"""
    
    opponents = ['random', 'negamax']
    results = {}
    
    for opponent in opponents:
        print(f"\nTesting vs {opponent} ({num_games} games)...")
        wins = 0
        total_time = 0
        
        for i in range(num_games):
            env = make('connectx', debug=False)
            
            start = time.time()
            if i % 2 == 0:
                env.run([agent, opponent])
                if env.state[0].reward == 1:
                    wins += 1
            else:
                env.run([opponent, agent])
                if env.state[1].reward == 1:
                    wins += 1
            
            game_time = time.time() - start
            total_time += game_time
            
            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{num_games} - Current win rate: {wins/(i+1)*100:.1f}%")
        
        win_rate = wins / num_games * 100
        avg_time = total_time / num_games
        
        print(f"\nResults vs {opponent}:")
        print(f"  Win rate: {wins}/{num_games} ({win_rate:.1f}%)")
        print(f"  Avg game time: {avg_time:.2f}s")
        
        results[opponent] = {
            'wins': wins,
            'games': num_games,
            'win_rate': win_rate,
            'avg_time': avg_time
        }
    
    # Overall assessment
    print("\n" + "="*50)
    print("OVERALL ASSESSMENT")
    print("="*50)
    
    random_wr = results['random']['win_rate']
    negamax_wr = results['negamax']['win_rate']
    
    if random_wr >= 98 and negamax_wr >= 80:
        print("✓ EXCELLENT - Ready for 1000+ score!")
    elif random_wr >= 95 and negamax_wr >= 70:
        print("✓ GOOD - Should achieve 900+ score")
    elif random_wr >= 90 and negamax_wr >= 60:
        print("⚡ DECENT - Likely 800+ score")
    else:
        print("✗ NEEDS IMPROVEMENT")
    
    print(f"\nExpected Kaggle score range: {int(600 + random_wr * 2 + negamax_wr * 3)}-{int(700 + random_wr * 2 + negamax_wr * 4)}")

if __name__ == "__main__":
    test_agent(20)  # Test with 20 games each
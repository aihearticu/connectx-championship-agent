"""
Self-Play Training System
Continuously improves agents through self-play
"""

import time
import json
import pickle
from datetime import datetime
from collections import defaultdict

def play_match(agent1, agent2, verbose=False):
    """Play a match between two agents"""
    board = [0] * 42
    current_player = 1
    moves = []
    
    class Obs:
        def __init__(self, board, mark):
            self.board = board
            self.mark = mark
    
    class Config:
        pass
    
    config = Config()
    
    for turn in range(42):
        obs = Obs(board[:], current_player)
        
        if current_player == 1:
            move = agent1(obs, config)
        else:
            move = agent2(obs, config)
        
        moves.append(move)
        
        # Make move
        for row in range(5, -1, -1):
            if board[row * 7 + move] == 0:
                board[row * 7 + move] = current_player
                
                # Check win
                if check_win(board, row, move, current_player):
                    return current_player, moves
                break
        
        current_player = 3 - current_player
    
    return 0, moves  # Draw

def check_win(board, row, col, player):
    """Check if move wins"""
    # Horizontal
    count = 1
    c = col - 1
    while c >= 0 and board[row * 7 + c] == player:
        count += 1
        c -= 1
    c = col + 1
    while c < 7 and board[row * 7 + c] == player:
        count += 1
        c += 1
    if count >= 4:
        return True
    
    # Vertical
    count = 1
    r = row + 1
    while r < 6 and board[r * 7 + col] == player:
        count += 1
        r += 1
    if count >= 4:
        return True
    
    # Diagonal \
    count = 1
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0 and board[r * 7 + c] == player:
        count += 1
        r -= 1
        c -= 1
    r, c = row + 1, col + 1
    while r < 6 and c < 7 and board[r * 7 + c] == player:
        count += 1
        r += 1
        c += 1
    if count >= 4:
        return True
    
    # Diagonal /
    count = 1
    r, c = row - 1, col + 1
    while r >= 0 and c < 7 and board[r * 7 + c] == player:
        count += 1
        r -= 1
        c += 1
    r, c = row + 1, col - 1
    while r < 6 and c >= 0 and board[r * 7 + c] == player:
        count += 1
        r += 1
        c -= 1
    if count >= 4:
        return True
    
    return False

def load_agent(filename):
    """Load agent from file"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        exec_globals = {}
        exec(code, exec_globals)
        return exec_globals['agent']
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def tournament(agents, num_rounds=10):
    """Run tournament between agents"""
    results = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'score': 0})
    
    for round_num in range(num_rounds):
        print(f"\nRound {round_num + 1}/{num_rounds}")
        
        for i, (name1, agent1) in enumerate(agents):
            for name2, agent2 in agents[i+1:]:
                # Play both colors
                winner1, _ = play_match(agent1, agent2)
                if winner1 == 1:
                    results[name1]['wins'] += 1
                    results[name2]['losses'] += 1
                elif winner1 == 2:
                    results[name2]['wins'] += 1
                    results[name1]['losses'] += 1
                else:
                    results[name1]['draws'] += 1
                    results[name2]['draws'] += 1
                
                winner2, _ = play_match(agent2, agent1)
                if winner2 == 1:
                    results[name2]['wins'] += 1
                    results[name1]['losses'] += 1
                elif winner2 == 2:
                    results[name1]['wins'] += 1
                    results[name2]['losses'] += 1
                else:
                    results[name1]['draws'] += 1
                    results[name2]['draws'] += 1
    
    # Calculate scores
    for name in results:
        results[name]['score'] = results[name]['wins'] * 3 + results[name]['draws']
    
    return results

def main():
    print("="*70)
    print("SELF-PLAY TRAINING SYSTEM")
    print("="*70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load agents
    agent_files = [
        ('championship_final.py', 'Championship'),
        ('ensemble_agent.py', 'Ensemble'),
        ('gradient_boost_agent.py', 'GradientBoost'),
        ('deep_rl_agent.py', 'DeepRL'),
    ]
    
    agents = []
    for filename, name in agent_files:
        agent = load_agent(filename)
        if agent:
            agents.append((name, agent))
            print(f"Loaded: {name}")
    
    if len(agents) < 2:
        print("Not enough agents loaded")
        return
    
    # Run tournament
    print(f"\nRunning tournament with {len(agents)} agents...")
    results = tournament(agents, num_rounds=5)
    
    # Display results
    print("\n" + "="*70)
    print("TOURNAMENT RESULTS")
    print("="*70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
    
    for rank, (name, stats) in enumerate(sorted_results, 1):
        print(f"\n{rank}. {name}")
        print(f"   Score: {stats['score']}")
        print(f"   Wins: {stats['wins']}, Losses: {stats['losses']}, Draws: {stats['draws']}")
        win_rate = stats['wins'] / (stats['wins'] + stats['losses'] + stats['draws']) * 100
        print(f"   Win Rate: {win_rate:.1f}%")
    
    # Save results
    with open('tournament_results.json', 'w') as f:
        json.dump(dict(results), f, indent=2)
    
    print("\n" + "="*70)
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Results saved to tournament_results.json")
    print("="*70)

if __name__ == "__main__":
    main()

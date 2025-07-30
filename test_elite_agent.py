#!/usr/bin/env python3
"""Test elite agent against various opponents"""

from kaggle_environments import make, evaluate
import elite_submission
import time

def test_elite_agent():
    """Comprehensive testing of elite agent"""
    
    # Test 1: Against random agent
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    # Test 2: Against negamax agent
    def negamax_agent(obs, config):
        """Simple negamax agent for testing"""
        def negamax(board, mark, depth):
            # Convert to 2D
            grid = []
            for r in range(config.rows):
                row = []
                for c in range(config.columns):
                    row.append(board[r * config.columns + c])
                grid.append(row)
            
            # Check terminal states
            for row in range(config.rows):
                for col in range(config.columns - config.inarow + 1):
                    window = [grid[row][col + i] for i in range(config.inarow)]
                    if window.count(mark) == config.inarow:
                        return None, 1000
                    if window.count(3 - mark) == config.inarow:
                        return None, -1000
            
            # Check valid moves
            valid = [c for c in range(config.columns) if grid[0][c] == 0]
            if not valid or depth == 0:
                return None, 0
            
            # Negamax search
            best_col = valid[0]
            best_score = -10000
            
            for col in valid:
                # Make move
                for row in range(config.rows - 1, -1, -1):
                    if grid[row][col] == 0:
                        grid[row][col] = mark
                        _, score = negamax([grid[r][c] for r in range(config.rows) for c in range(config.columns)], 
                                          3 - mark, depth - 1)
                        grid[row][col] = 0
                        score = -score
                        if score > best_score:
                            best_score = score
                            best_col = col
                        break
            
            return best_col, best_score
        
        col, _ = negamax(obs.board, obs.mark, 3)
        return col if col is not None else 3
    
    print("=== Testing Elite Connect X Agent ===\n")
    
    # Test vs Random
    print("Test 1: Elite Agent vs Random Agent")
    print("Testing as Player 1...")
    start = time.time()
    results_p1 = evaluate("connectx", [elite_submission.agent, random_agent], num_episodes=50)
    elapsed = time.time() - start
    wins_p1 = sum(1 for r in results_p1[0] if r == 1)
    losses_p1 = sum(1 for r in results_p1[0] if r == -1)
    draws_p1 = sum(1 for r in results_p1[0] if r == 0)
    
    print(f"As Player 1: {wins_p1}W-{losses_p1}L-{draws_p1}D ({wins_p1/50*100:.1f}% win rate)")
    print(f"Average time per game: {elapsed/50:.2f}s")
    
    print("\nTesting as Player 2...")
    start = time.time()
    results_p2 = evaluate("connectx", [random_agent, elite_submission.agent], num_episodes=50)
    elapsed = time.time() - start
    wins_p2 = sum(1 for r in results_p2[1] if r == 1)
    losses_p2 = sum(1 for r in results_p2[1] if r == -1)
    draws_p2 = sum(1 for r in results_p2[1] if r == 0)
    
    print(f"As Player 2: {wins_p2}W-{losses_p2}L-{draws_p2}D ({wins_p2/50*100:.1f}% win rate)")
    print(f"Average time per game: {elapsed/50:.2f}s")
    
    total_wins_random = wins_p1 + wins_p2
    print(f"\nTotal vs Random: {total_wins_random}/100 ({total_wins_random}% win rate)")
    
    # Test vs Negamax
    print("\n" + "="*50)
    print("Test 2: Elite Agent vs Negamax Agent")
    print("Testing as Player 1...")
    start = time.time()
    results_p1 = evaluate("connectx", [elite_submission.agent, negamax_agent], num_episodes=20)
    elapsed = time.time() - start
    wins_p1 = sum(1 for r in results_p1[0] if r == 1)
    losses_p1 = sum(1 for r in results_p1[0] if r == -1)
    draws_p1 = sum(1 for r in results_p1[0] if r == 0)
    
    print(f"As Player 1: {wins_p1}W-{losses_p1}L-{draws_p1}D ({wins_p1/20*100:.1f}% win rate)")
    print(f"Average time per game: {elapsed/20:.2f}s")
    
    print("\nTesting as Player 2...")
    start = time.time()
    results_p2 = evaluate("connectx", [negamax_agent, elite_submission.agent], num_episodes=20)
    elapsed = time.time() - start
    wins_p2 = sum(1 for r in results_p2[1] if r == 1)
    losses_p2 = sum(1 for r in results_p2[1] if r == -1)
    draws_p2 = sum(1 for r in results_p2[1] if r == 0)
    
    print(f"As Player 2: {wins_p2}W-{losses_p2}L-{draws_p2}D ({wins_p2/20*100:.1f}% win rate)")
    print(f"Average time per game: {elapsed/20:.2f}s")
    
    total_wins_negamax = wins_p1 + wins_p2
    print(f"\nTotal vs Negamax: {total_wins_negamax}/40 ({total_wins_negamax/40*100:.1f}% win rate)")
    
    # Sample game visualization
    print("\n" + "="*50)
    print("Sample Game (Elite Agent as Player 1 vs Random):")
    env = make("connectx", debug=True)
    env.reset()
    env.run([elite_submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    # Performance summary
    print("\n" + "="*50)
    print("PERFORMANCE SUMMARY:")
    print(f"Win rate vs Random: {total_wins_random}%")
    print(f"Win rate vs Negamax: {total_wins_negamax/40*100:.1f}%")
    
    if total_wins_random >= 95 and total_wins_negamax >= 30:
        print("\n✓ Agent shows STRONG performance - ready for submission!")
        return True
    else:
        print("\n✗ Agent needs improvement before submission")
        return False

if __name__ == "__main__":
    ready = test_elite_agent()
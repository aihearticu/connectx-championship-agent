#!/usr/bin/env python3
"""Validate agent for top 3 performance"""

from kaggle_environments import make, evaluate
import submission
import time

def validate_agent():
    """Comprehensive validation of agent performance"""
    
    print("=== ConnectX Agent Validation for Top 3 ===\n")
    
    # Test 1: Basic functionality
    print("Test 1: Agent functionality")
    env = make("connectx", debug=True)
    env.reset()
    obs = env.state[0].observation
    config = env.configuration
    
    try:
        move = submission.agent(obs, config)
        if 0 <= move < config.columns:
            print(f"✓ Agent returns valid move: {move}")
        else:
            print(f"✗ Invalid move: {move}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Win/Block detection
    print("\nTest 2: Win/Block detection")
    
    # Win in 1 test
    win_board = [0] * 42
    win_board[35] = 1  # Bottom row
    win_board[36] = 1
    win_board[37] = 1
    win_board[38] = 0  # Can win here
    
    win_obs = type('', (), {})()
    win_obs.board = win_board
    win_obs.mark = 1
    
    move = submission.agent(win_obs, config)
    if move == 3:
        print("✓ Correctly identifies win in 1")
    else:
        print(f"✗ Failed to win (played {move} instead of 3)")
    
    # Block test
    block_board = [0] * 42
    block_board[35] = 2  # Opponent threatening
    block_board[36] = 2
    block_board[37] = 2
    block_board[38] = 0
    block_board[39] = 1
    block_board[40] = 1
    
    block_obs = type('', (), {})()
    block_obs.board = block_board
    block_obs.mark = 1
    
    move = submission.agent(block_obs, config)
    if move == 3:
        print("✓ Correctly blocks opponent win")
    else:
        print(f"✗ Failed to block (played {move} instead of 3)")
    
    # Test 3: Performance against different opponents
    print("\nTest 3: Performance benchmarks")
    
    # Random agent
    def random_agent(obs, config):
        import random
        valid = [c for c in range(config.columns) if obs.board[c] == 0]
        return random.choice(valid) if valid else 0
    
    # Defensive agent
    def defensive_agent(obs, config):
        import random
        board = obs.board
        my_mark = obs.mark
        opp_mark = 3 - my_mark
        valid = [c for c in range(config.columns) if board[c] == 0]
        
        # Block opponent wins
        for col in valid:
            test_board = list(board)
            for row in range(config.rows-1, -1, -1):
                if test_board[row*config.columns+col] == 0:
                    test_board[row*config.columns+col] = opp_mark
                    # Check if opponent would win
                    if check_win_simple(test_board, row, col, opp_mark, config):
                        return col
                    break
        
        # Otherwise play center
        if config.columns // 2 in valid:
            return config.columns // 2
        return random.choice(valid)
    
    def check_win_simple(board, row, col, mark, config):
        """Simple win check"""
        # Horizontal
        count = 0
        for c in range(config.columns):
            if board[row*config.columns+c] == mark:
                count += 1
                if count >= config.inarow:
                    return True
            else:
                count = 0
        return False
    
    # Test against random
    print("\nAgainst Random Agent (20 games):")
    start = time.time()
    results1 = evaluate("connectx", [submission.agent, random_agent], num_episodes=10)
    results2 = evaluate("connectx", [random_agent, submission.agent], num_episodes=10)
    elapsed = time.time() - start
    
    wins = sum(1 for r in results1[0] if r == 1) + sum(1 for r in results2[1] if r == 1)
    print(f"Win rate: {wins}/20 ({wins*5}%)")
    print(f"Time: {elapsed:.1f}s ({elapsed/20:.3f}s per game)")
    
    # Test against defensive
    print("\nAgainst Defensive Agent (10 games):")
    start = time.time()
    results = evaluate("connectx", [submission.agent, defensive_agent], num_episodes=10)
    elapsed = time.time() - start
    
    wins = sum(1 for r in results[0] if r == 1)
    print(f"Win rate: {wins}/10 ({wins*10}%)")
    print(f"Time: {elapsed:.1f}s ({elapsed/10:.3f}s per game)")
    
    # Sample game
    print("\n" + "="*50)
    print("Sample game (Agent vs Random):")
    env.reset()
    env.run([submission.agent, random_agent])
    print(env.render(mode="ansi"))
    
    # Performance summary
    print("\n" + "="*50)
    print("PERFORMANCE SUMMARY:")
    
    total_wins = wins
    if wins >= 18:  # 90%+ against random
        print("✓ Shows STRONG performance characteristics")
        print("✓ Ready for competitive play")
        return True
    else:
        print("✗ Performance needs improvement")
        return False

if __name__ == "__main__":
    if validate_agent():
        print("\n✓ Agent validated for top-tier performance!")
    else:
        print("\n✗ Agent needs further optimization")
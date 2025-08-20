#!/usr/bin/env python3
"""Debug single game"""

from kaggle_environments import make
from submission_optimized_v2 import agent as optimized_agent

def test_single_game():
    """Test a single game with detailed output"""
    env = make("connectx", debug=True)
    
    # Run game
    result = env.run([optimized_agent, "random"])
    
    # Check result
    print("Game result:")
    for i, state in enumerate(result):
        if hasattr(state, 'reward'):
            print(f"Player {i}: reward={state.reward}, status={state.status}")
        else:
            print(f"Player {i}: reward={state.get('reward', 'N/A')}, status={state.get('status', 'N/A')}")
    
    # Check final board
    if hasattr(result[0], 'observation'):
        final_board = result[0].observation.board
    else:
        final_board = result[0]['observation']['board']
    print("\nFinal board:")
    for row in range(6):
        row_str = ""
        for col in range(7):
            val = final_board[(5-row) * 7 + col]
            if val == 0:
                row_str += ". "
            elif val == 1:
                row_str += "X "
            else:
                row_str += "O "
        print(row_str)
    
    # Check winner
    reward = result[0].reward if hasattr(result[0], 'reward') else result[0].get('reward', 0)
    if reward == 1:
        print("\nOptimized agent wins!")
    elif reward == -1:
        print("\nOptimized agent loses!")
    else:
        print("\nDraw!")
    
    return reward

if __name__ == "__main__":
    wins = 0
    for i in range(5):
        print(f"\n=== GAME {i+1} ===")
        reward = test_single_game()
        if reward == 1:
            wins += 1
    
    print(f"\n\nWon {wins}/5 games")
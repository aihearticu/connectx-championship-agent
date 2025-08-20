#!/usr/bin/env python3
"""Test minimax implementation in isolation"""

import time

def test_minimax():
    """Test minimax algorithm directly"""
    
    # Simple 4x4 board for testing
    board = [
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 1, 2, 0,
        1, 2, 1, 2
    ]
    
    def check_win_test(board, player):
        """Simple win check for 4x4"""
        # Check rows
        for r in range(4):
            for c in range(2):
                if all(board[r*4+c+i] == player for i in range(3)):
                    return True
        
        # Check columns
        for c in range(4):
            for r in range(2):
                if all(board[(r+i)*4+c] == player for i in range(3)):
                    return True
                    
        return False
    
    def make_move_test(board, col, player):
        """Make move on test board"""
        new_board = board.copy()
        for r in range(3, -1, -1):
            if new_board[r*4+col] == 0:
                new_board[r*4+col] = player
                break
        return new_board
    
    def evaluate_test(board, player):
        """Simple evaluation"""
        if check_win_test(board, player):
            return 1000
        if check_win_test(board, 3-player):
            return -1000
        return 0
    
    def minimax_test(board, depth, maximizing, player):
        """Simple minimax"""
        if depth == 0:
            return evaluate_test(board, player), None
            
        if check_win_test(board, 1) or check_win_test(board, 2):
            return evaluate_test(board, player), None
            
        valid_moves = [c for c in range(4) if board[c] == 0]
        if not valid_moves:
            return 0, None
            
        if maximizing:
            best_val = float('-inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move_test(board, move, player)
                val, _ = minimax_test(new_board, depth-1, False, player)
                if val > best_val:
                    best_val = val
                    best_move = move
                    
            return best_val, best_move
        else:
            best_val = float('inf')
            best_move = valid_moves[0]
            
            for move in valid_moves:
                new_board = make_move_test(board, move, 3-player)
                val, _ = minimax_test(new_board, depth-1, True, player)
                if val < best_val:
                    best_val = val
                    best_move = move
                    
            return best_val, best_move
    
    # Test the minimax
    print("Testing minimax algorithm...")
    print("Board state:")
    for r in range(4):
        print([board[r*4+c] for c in range(4)])
    
    print("\nPlayer 1's turn:")
    val, move = minimax_test(board, 3, True, 1)
    print(f"Best move: {move}, Value: {val}")
    
    # Make the move and check
    new_board = make_move_test(board, move, 1)
    print("\nAfter move:")
    for r in range(4):
        print([new_board[r*4+c] for c in range(4)])
    
    if check_win_test(new_board, 1):
        print("Player 1 wins!")

if __name__ == "__main__":
    test_minimax()
"""
Final validation for Top 5 submission agent
Comprehensive testing to ensure 1400-1600 ELO performance
"""

import time
import random
import sys

# Import the submission agent
from top5_submission_final import agent as elite_agent

class TestGame:
    """Game simulator for testing"""
    
    @staticmethod
    def check_win(board, player):
        """Check if player has won"""
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row*7+col+i] == player for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row+i)*7+col] == player for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(3):
            for col in range(4):
                if all(board[(row+i)*7+col+i] == player for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3, 6):
            for col in range(4):
                if all(board[(row-i)*7+col+i] == player for i in range(4)):
                    return True
        
        return False
    
    @staticmethod
    def play(agent1, agent2, verbose=False):
        """Play a game between two agents"""
        board = [0] * 42
        current = 1
        moves = 0
        
        class Obs:
            def __init__(self, b, m):
                self.board = b
                self.mark = m
        
        while moves < 42:
            obs = Obs(board.copy(), current)
            
            # Get move
            if current == 1:
                if agent1 == 'elite':
                    move = elite_agent(obs, None)
                else:
                    move = agent1(board, current)
            else:
                if agent2 == 'elite':
                    move = elite_agent(obs, None)
                else:
                    move = agent2(board, current)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = current
                    break
            
            moves += 1
            
            # Check win
            if TestGame.check_win(board, current):
                return current
            
            current = 3 - current
        
        return 0  # Draw

def random_agent(board, player):
    """Random baseline agent"""
    valid = [c for c in range(7) if board[c] == 0]
    return random.choice(valid) if valid else 0

def greedy_agent(board, player):
    """Simple greedy agent"""
    # Try to win
    for col in range(7):
        if board[col] == 0:
            temp = board.copy()
            for row in range(5, -1, -1):
                if temp[row * 7 + col] == 0:
                    temp[row * 7 + col] = player
                    break
            if TestGame.check_win(temp, player):
                return col
    
    # Block opponent
    for col in range(7):
        if board[col] == 0:
            temp = board.copy()
            for row in range(5, -1, -1):
                if temp[row * 7 + col] == 0:
                    temp[row * 7 + col] = 3 - player
                    break
            if TestGame.check_win(temp, 3 - player):
                return col
    
    # Prefer center
    if board[3] == 0:
        return 3
    
    # Random fallback
    return random_agent(board, player)

def minimax_agent(board, player, depth=5):
    """Minimax agent for stronger testing"""
    def evaluate(board, player):
        score = 0
        # Center preference
        for i in range(6):
            if board[i * 7 + 3] == player:
                score += 3
            elif board[i * 7 + 3] == 3 - player:
                score -= 3
        return score
    
    def minimax(board, depth, maximizing, player, alpha, beta):
        if TestGame.check_win(board, player):
            return 1000 if maximizing else -1000
        if TestGame.check_win(board, 3 - player):
            return -1000 if maximizing else 1000
        
        valid = [c for c in range(7) if board[c] == 0]
        if not valid or depth == 0:
            return evaluate(board, player)
        
        if maximizing:
            max_eval = -float('inf')
            for col in valid:
                new_board = board.copy()
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = player
                        break
                
                eval = minimax(new_board, depth - 1, False, player, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid:
                new_board = board.copy()
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = 3 - player
                        break
                
                eval = minimax(new_board, depth - 1, True, player, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    valid = [c for c in range(7) if board[c] == 0]
    if not valid:
        return 0
    
    best_move = valid[0]
    best_score = -float('inf')
    
    for col in valid:
        new_board = board.copy()
        for row in range(5, -1, -1):
            if new_board[row * 7 + col] == 0:
                new_board[row * 7 + col] = player
                break
        
        score = minimax(new_board, depth - 1, False, player, -float('inf'), float('inf'))
        if score > best_score:
            best_score = score
            best_move = col
    
    return best_move

def run_final_tests():
    """Run comprehensive final validation"""
    print("="*70)
    print(" FINAL TOP 5 AGENT VALIDATION ")
    print("="*70)
    
    results = {}
    
    # Test 1: vs Random (30 games)
    print("\n[1/5] Testing vs Random Agent")
    print("Target: 98%+ win rate for top 5 level")
    print("-"*50)
    
    wins = 0
    for game in range(30):
        if game % 2 == 0:
            result = TestGame.play('elite', random_agent)
            if result == 1:
                wins += 1
        else:
            result = TestGame.play(random_agent, 'elite')
            if result == 2:
                wins += 1
        
        if (game + 1) % 10 == 0:
            print(f"  Progress: {game+1}/30 games - Win rate: {wins/(game+1)*100:.1f}%")
    
    results['random'] = wins / 30 * 100
    print(f"  Final: {wins}/30 wins ({results['random']:.1f}%)")
    print(f"  {'✓ EXCELLENT' if results['random'] >= 98 else '✓ PASS' if results['random'] >= 95 else '✗ FAIL'}")
    
    # Test 2: vs Greedy (20 games)
    print("\n[2/5] Testing vs Greedy Agent")
    print("Target: 90%+ win rate")
    print("-"*50)
    
    wins = 0
    for game in range(20):
        if game % 2 == 0:
            result = TestGame.play('elite', greedy_agent)
            if result == 1:
                wins += 1
        else:
            result = TestGame.play(greedy_agent, 'elite')
            if result == 2:
                wins += 1
    
    results['greedy'] = wins / 20 * 100
    print(f"  Final: {wins}/20 wins ({results['greedy']:.1f}%)")
    print(f"  {'✓ PASS' if results['greedy'] >= 90 else '⚠ WARNING' if results['greedy'] >= 80 else '✗ FAIL'}")
    
    # Test 3: vs Minimax depth 3 (10 games)
    print("\n[3/5] Testing vs Minimax Depth 3")
    print("Target: 70%+ win rate")
    print("-"*50)
    
    wins = 0
    total_time = 0
    for game in range(10):
        start = time.time()
        if game % 2 == 0:
            result = TestGame.play('elite', lambda b, p: minimax_agent(b, p, 3))
            if result == 1:
                wins += 1
        else:
            result = TestGame.play(lambda b, p: minimax_agent(b, p, 3), 'elite')
            if result == 2:
                wins += 1
        total_time += time.time() - start
        print(f"  Game {game+1}: {'WIN' if ((game%2==0 and result==1) or (game%2==1 and result==2)) else 'LOSS' if result != 0 else 'DRAW'} ({time.time()-start:.2f}s)")
    
    results['minimax3'] = wins / 10 * 100
    print(f"  Final: {wins}/10 wins ({results['minimax3']:.1f}%)")
    print(f"  Avg time: {total_time/10:.2f}s")
    print(f"  {'✓ PASS' if results['minimax3'] >= 70 else '⚠ WARNING' if results['minimax3'] >= 60 else '✗ FAIL'}")
    
    # Test 4: vs Minimax depth 5 (10 games)
    print("\n[4/5] Testing vs Minimax Depth 5")
    print("Target: 60%+ win rate for top 5 level")
    print("-"*50)
    
    wins = 0
    total_time = 0
    for game in range(10):
        start = time.time()
        if game % 2 == 0:
            result = TestGame.play('elite', lambda b, p: minimax_agent(b, p, 5))
            if result == 1:
                wins += 1
        else:
            result = TestGame.play(lambda b, p: minimax_agent(b, p, 5), 'elite')
            if result == 2:
                wins += 1
        total_time += time.time() - start
        print(f"  Game {game+1}: {'WIN' if ((game%2==0 and result==1) or (game%2==1 and result==2)) else 'LOSS' if result != 0 else 'DRAW'} ({time.time()-start:.2f}s)")
    
    results['minimax5'] = wins / 10 * 100
    print(f"  Final: {wins}/10 wins ({results['minimax5']:.1f}%)")
    print(f"  Avg time: {total_time/10:.2f}s")
    print(f"  {'✓ PASS' if results['minimax5'] >= 60 else '⚠ WARNING' if results['minimax5'] >= 50 else '✗ FAIL'}")
    
    # Test 5: Speed test
    print("\n[5/5] Performance Speed Test")
    print("Target: Complete search within time limits")
    print("-"*50)
    
    test_positions = [
        ("Empty", [0] * 42),
        ("Early", [0]*35 + [1, 2, 0, 0, 0, 0, 0]),
        ("Mid", [0]*21 + [1,2,1,2,1,2,0] * 3),
    ]
    
    for name, board in test_positions:
        class Obs:
            def __init__(self):
                self.board = board
                self.mark = 1
        
        obs = Obs()
        start = time.time()
        move = elite_agent(obs, None)
        elapsed = time.time() - start
        
        print(f"  {name} position: Move {move} in {elapsed:.3f}s")
        
        if elapsed < 0.1:
            print(f"    ✓ Excellent speed")
        elif elapsed < 0.5:
            print(f"    ✓ Good speed")
        elif elapsed < 1.0:
            print(f"    ⚠ Acceptable speed")
        else:
            print(f"    ✗ Too slow")
    
    # Final summary
    print("\n" + "="*70)
    print(" FINAL ASSESSMENT ")
    print("="*70)
    
    print("\nWin Rates Summary:")
    print(f"  vs Random:    {results['random']:.1f}% (Target: 95%+)")
    print(f"  vs Greedy:    {results['greedy']:.1f}% (Target: 90%+)")
    print(f"  vs Minimax-3: {results['minimax3']:.1f}% (Target: 70%+)")
    print(f"  vs Minimax-5: {results['minimax5']:.1f}% (Target: 60%+)")
    
    # Calculate overall readiness
    score = 0
    if results['random'] >= 95: score += 25
    if results['greedy'] >= 90: score += 25
    if results['minimax3'] >= 70: score += 25
    if results['minimax5'] >= 60: score += 25
    
    print(f"\nReadiness Score: {score}/100")
    
    if score >= 90:
        print("\n✓✓✓ AGENT READY FOR TOP 5 COMPETITION ✓✓✓")
        print("Expected ELO: 1400-1600")
        print("Expected Rank: Top 5-10")
    elif score >= 75:
        print("\n✓ Agent ready for top 10-20")
        print("Expected ELO: 1200-1400")
    elif score >= 50:
        print("\n⚠ Agent needs optimization")
        print("Expected ELO: 1000-1200")
    else:
        print("\n✗ Agent not ready for competition")
        print("Significant improvements needed")
    
    print("\nRecommended submission file: top5_submission_final.py")

if __name__ == "__main__":
    run_final_tests()
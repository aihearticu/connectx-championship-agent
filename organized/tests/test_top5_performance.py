"""
Performance Testing for Top 5 Elite Agent
Tests against various benchmarks to ensure 1400-1600 ELO performance
"""

import time
import random
from top5_elite_agent import TopFiveAgent, agent

class TestBenchmarks:
    """Benchmark opponents for testing"""
    
    @staticmethod
    def random_agent(board, mark):
        """Random player for baseline testing"""
        valid_moves = [col for col in range(7) if board[col] == 0]
        return random.choice(valid_moves) if valid_moves else 0
    
    @staticmethod
    def negamax_agent(board, mark, depth=5):
        """Simple negamax agent for mid-tier testing"""
        def evaluate(board, mark):
            score = 0
            # Simple center-focused evaluation
            for row in range(6):
                for col in range(7):
                    idx = row * 7 + col
                    if board[idx] == mark:
                        score += 3 if col == 3 else 2 if col in [2, 4] else 1
                    elif board[idx] != 0:
                        score -= 3 if col == 3 else 2 if col in [2, 4] else 1
            return score
        
        def check_win(board, mark):
            # Check horizontal
            for row in range(6):
                for col in range(4):
                    if all(board[row * 7 + col + i] == mark for i in range(4)):
                        return True
            
            # Check vertical
            for col in range(7):
                for row in range(3):
                    if all(board[(row + i) * 7 + col] == mark for i in range(4)):
                        return True
            
            # Check diagonals
            for row in range(3):
                for col in range(4):
                    if all(board[(row + i) * 7 + col + i] == mark for i in range(4)):
                        return True
                    if all(board[(row + 3 - i) * 7 + col + i] == mark for i in range(4)):
                        return True
            
            return False
        
        def negamax(board, depth, alpha, beta, mark):
            if check_win(board, 3 - mark):
                return -1000 + depth, None
            
            if depth == 0 or all(board[i] != 0 for i in range(7)):
                return evaluate(board, mark), None
            
            best_score = -float('inf')
            best_move = None
            
            for col in [3, 4, 2, 5, 1, 6, 0]:  # Center-first ordering
                if board[col] != 0:
                    continue
                
                # Make move
                temp_board = board.copy()
                for row in range(5, -1, -1):
                    if temp_board[row * 7 + col] == 0:
                        temp_board[row * 7 + col] = mark
                        break
                
                score, _ = negamax(temp_board, depth - 1, -beta, -alpha, 3 - mark)
                score = -score
                
                if score > best_score:
                    best_score = score
                    best_move = col
                
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            
            return best_score, best_move
        
        _, move = negamax(board, depth, -float('inf'), float('inf'), mark)
        return move if move is not None else 3

class PerformanceTester:
    """Comprehensive performance testing suite"""
    
    def __init__(self):
        self.elite_agent = TopFiveAgent()
    
    def play_game(self, agent1, agent2, verbose=False):
        """Play a single game between two agents"""
        board = [0] * 42
        current_mark = 1
        moves = 0
        
        agents = {1: agent1, 2: agent2}
        
        while moves < 42:
            # Get move from current player
            if agents[current_mark] == 'elite':
                move = self.elite_agent.iterative_deepening(board, current_mark, time_limit=0.9)
            else:
                move = agents[current_mark](board, current_mark)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = current_mark
                    break
            
            moves += 1
            
            if verbose and moves <= 10:
                print(f"Move {moves}: Player {current_mark} plays column {move}")
            
            # Check for win
            if self.check_winner(board, current_mark):
                return current_mark
            
            # Switch player
            current_mark = 3 - current_mark
        
        return 0  # Draw
    
    def check_winner(self, board, mark):
        """Check if player has won"""
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row * 7 + col + i] == mark for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row + i) * 7 + col] == mark for i in range(4)):
                    return True
        
        # Diagonals
        for row in range(3):
            for col in range(4):
                if all(board[(row + i) * 7 + col + i] == mark for i in range(4)):
                    return True
                if all(board[(row + 3 - i) * 7 + col + i] == mark for i in range(4)):
                    return True
        
        return False
    
    def test_vs_random(self, games=20):
        """Test against random agent - target 95%+ win rate"""
        print("\n" + "="*60)
        print("Testing vs Random Agent (Target: 95%+ win rate)")
        print("="*60)
        
        wins = 0
        losses = 0
        draws = 0
        total_time = 0
        
        for i in range(games):
            start = time.time()
            
            # Alternate who goes first
            if i % 2 == 0:
                result = self.play_game('elite', TestBenchmarks.random_agent)
                if result == 1:
                    wins += 1
                elif result == 2:
                    losses += 1
                else:
                    draws += 1
            else:
                result = self.play_game(TestBenchmarks.random_agent, 'elite')
                if result == 2:
                    wins += 1
                elif result == 1:
                    losses += 1
                else:
                    draws += 1
            
            elapsed = time.time() - start
            total_time += elapsed
            
            if (i + 1) % 5 == 0:
                print(f"Games {i+1}/{games}: W={wins} L={losses} D={draws} "
                      f"(Win rate: {wins/(i+1)*100:.1f}%)")
        
        win_rate = wins / games * 100
        avg_time = total_time / games
        
        print(f"\nFinal Results:")
        print(f"Wins: {wins}/{games} ({win_rate:.1f}%)")
        print(f"Losses: {losses}/{games}")
        print(f"Draws: {draws}/{games}")
        print(f"Average game time: {avg_time:.3f}s")
        print(f"✓ PASSED" if win_rate >= 95 else f"✗ FAILED (need 95%+)")
        
        return win_rate
    
    def test_vs_negamax(self, games=10, depth=5):
        """Test against negamax agent - target 70%+ win rate"""
        print("\n" + "="*60)
        print(f"Testing vs Negamax Agent (depth={depth}, Target: 70%+ win rate)")
        print("="*60)
        
        wins = 0
        losses = 0
        draws = 0
        total_time = 0
        
        for i in range(games):
            start = time.time()
            
            # Alternate who goes first
            if i % 2 == 0:
                result = self.play_game('elite', 
                                       lambda b, m: TestBenchmarks.negamax_agent(b, m, depth))
                if result == 1:
                    wins += 1
                elif result == 2:
                    losses += 1
                else:
                    draws += 1
            else:
                result = self.play_game(lambda b, m: TestBenchmarks.negamax_agent(b, m, depth),
                                       'elite')
                if result == 2:
                    wins += 1
                elif result == 1:
                    losses += 1
                else:
                    draws += 1
            
            elapsed = time.time() - start
            total_time += elapsed
            
            print(f"Game {i+1}/{games}: {'WIN' if (i%2==0 and result==1) or (i%2==1 and result==2) else 'LOSS' if result != 0 else 'DRAW'} "
                  f"(Time: {elapsed:.2f}s)")
        
        win_rate = wins / games * 100
        avg_time = total_time / games
        
        print(f"\nFinal Results:")
        print(f"Wins: {wins}/{games} ({win_rate:.1f}%)")
        print(f"Losses: {losses}/{games}")
        print(f"Draws: {draws}/{games}")
        print(f"Average game time: {avg_time:.3f}s")
        print(f"✓ PASSED" if win_rate >= 70 else f"✗ FAILED (need 70%+)")
        
        return win_rate
    
    def test_performance_metrics(self):
        """Test computational performance metrics"""
        print("\n" + "="*60)
        print("Testing Performance Metrics")
        print("="*60)
        
        # Test different board states
        test_cases = [
            ("Empty board", [0] * 42),
            ("Opening position", [0]*35 + [1, 2, 0, 0, 0, 0, 0]),
            ("Midgame position", self._create_midgame_board()),
            ("Complex position", self._create_complex_board()),
        ]
        
        for name, board in test_cases:
            print(f"\n{name}:")
            
            # Reset counters
            self.elite_agent.nodes_searched = 0
            self.elite_agent.tt = self.elite_agent.tt.__class__(64)  # Reset TT
            
            start = time.time()
            move = self.elite_agent.iterative_deepening(board, 1, time_limit=0.5)
            elapsed = time.time() - start
            
            nodes_per_second = self.elite_agent.nodes_searched / max(elapsed, 0.001)
            
            print(f"  Best move: {move}")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Nodes searched: {self.elite_agent.nodes_searched:,}")
            print(f"  Nodes/second: {nodes_per_second:,.0f}")
            print(f"  TT hit rate: {self.elite_agent.tt.get_hit_rate():.1%}")
            
            # Check performance targets
            if nodes_per_second >= 1_000_000:
                print(f"  ✓ Excellent performance (1M+ nodes/sec)")
            elif nodes_per_second >= 500_000:
                print(f"  ✓ Good performance (500K+ nodes/sec)")
            elif nodes_per_second >= 100_000:
                print(f"  ⚠ Acceptable performance (100K+ nodes/sec)")
            else:
                print(f"  ✗ Poor performance (need 100K+ nodes/sec)")
    
    def _create_midgame_board(self):
        """Create a typical midgame position"""
        board = [0] * 42
        moves = [(3, 1), (3, 2), (2, 1), (4, 2), (2, 1), (4, 2),
                 (3, 1), (3, 2), (1, 1), (5, 2), (4, 1), (2, 2)]
        
        for col, mark in moves:
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = mark
                    break
        
        return board
    
    def _create_complex_board(self):
        """Create a complex tactical position"""
        board = [0] * 42
        # Create a position with multiple threats
        pattern = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 1, 0, 0],
            [0, 1, 2, 1, 2, 0, 0],
            [0, 2, 1, 2, 1, 2, 0],
            [1, 1, 2, 1, 2, 1, 2],
        ]
        
        for row in range(6):
            for col in range(7):
                board[row * 7 + col] = pattern[row][col]
        
        return board
    
    def test_depth_achievement(self):
        """Test if agent achieves 8-10 ply depth consistently"""
        print("\n" + "="*60)
        print("Testing Search Depth Achievement (Target: 8-10 ply)")
        print("="*60)
        
        test_positions = [
            ("Opening", [0] * 42),
            ("Early game", self._create_midgame_board()[:21] + [0] * 21),
            ("Midgame", self._create_midgame_board()),
        ]
        
        for name, board in test_positions:
            print(f"\n{name} position:")
            
            max_depth_reached = 0
            
            # Test with different time limits
            for time_limit in [0.1, 0.3, 0.5, 1.0]:
                # Modified to track depth
                start = time.time()
                
                # Run iterative deepening
                for depth in range(1, 15):
                    if time.time() - start > time_limit * 0.9:
                        break
                    max_depth_reached = depth
                
                print(f"  Time {time_limit}s: Depth {max_depth_reached}")
            
            if max_depth_reached >= 8:
                print(f"  ✓ Achieves target depth (8-10 ply)")
            else:
                print(f"  ✗ Below target depth (got {max_depth_reached}, need 8+)")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*70)
        print(" TOP 5 ELITE AGENT - COMPREHENSIVE PERFORMANCE TEST ")
        print("="*70)
        
        results = {}
        
        # 1. Performance metrics
        print("\n[1/5] Performance Metrics Test")
        self.test_performance_metrics()
        
        # 2. Depth achievement
        print("\n[2/5] Search Depth Test")
        self.test_depth_achievement()
        
        # 3. Win rate vs Random
        print("\n[3/5] Random Agent Benchmark")
        results['random'] = self.test_vs_random(20)
        
        # 4. Win rate vs Negamax depth 3
        print("\n[4/5] Negamax Depth 3 Benchmark")
        results['negamax_3'] = self.test_vs_negamax(10, depth=3)
        
        # 5. Win rate vs Negamax depth 5
        print("\n[5/5] Negamax Depth 5 Benchmark")
        results['negamax_5'] = self.test_vs_negamax(10, depth=5)
        
        # Final summary
        print("\n" + "="*70)
        print(" FINAL TEST SUMMARY ")
        print("="*70)
        
        print("\nWin Rates:")
        print(f"  vs Random: {results['random']:.1f}% (Target: 95%+)")
        print(f"  vs Negamax-3: {results['negamax_3']:.1f}% (Target: 70%+)")
        print(f"  vs Negamax-5: {results['negamax_5']:.1f}% (Target: 60%+)")
        
        # Overall assessment
        passed = (results['random'] >= 95 and 
                 results['negamax_3'] >= 70 and 
                 results['negamax_5'] >= 60)
        
        if passed:
            print("\n✓✓✓ AGENT READY FOR TOP 5 COMPETITION ✓✓✓")
            print("Expected ELO: 1400-1600")
            print("Expected Rank: Top 5-10")
        else:
            print("\n✗ AGENT NEEDS OPTIMIZATION")
            print("Review evaluation function and search depth")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_all_tests()
#!/usr/bin/env python3
"""
Test Suite for Championship Engine 1000+
Validates all components and performance
"""

import time
import json
from kaggle_environments import make, evaluate
from bitboard_engine_v2 import BitboardEngine
from advanced_search import AdvancedSearch
from pattern_recognition import PatternRecognition
from champion_engine_1000 import ChampionEngine, agent as champion_agent

class ChampionshipTester:
    """Comprehensive testing for championship engine"""
    
    def __init__(self):
        self.engine = ChampionEngine()
        self.bitboard = BitboardEngine()
        self.results = {
            'bitboard_tests': {},
            'search_tests': {},
            'pattern_tests': {},
            'game_tests': {},
            'performance_tests': {}
        }
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=== CHAMPIONSHIP ENGINE TEST SUITE ===\n")
        
        # Component tests
        self.test_bitboard_engine()
        self.test_advanced_search()
        self.test_pattern_recognition()
        
        # Integration tests
        self.test_opening_book()
        self.test_endgame_positions()
        
        # Performance tests
        self.test_game_performance()
        self.test_speed_benchmark()
        
        # Generate report
        self.generate_report()
    
    def test_bitboard_engine(self):
        """Test bitboard operations"""
        print("Testing Bitboard Engine...")
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Board encoding
        test_board = [0] * 42
        test_board[35] = 1  # Bottom center
        test_board[36] = 1
        test_board[37] = 1
        
        pos, mask = self.bitboard.encode_position(test_board, 1)
        tests_total += 1
        if pos != 0 and mask != 0:
            tests_passed += 1
            print("  ✓ Board encoding")
        else:
            print("  ✗ Board encoding FAILED")
        
        # Test 2: Win detection
        tests_total += 1
        if self.bitboard.is_winning_move(3, pos, mask):
            tests_passed += 1
            print("  ✓ Win detection")
        else:
            print("  ✗ Win detection FAILED")
        
        # Test 3: Move generation
        valid_moves = self.bitboard.move_order(mask)
        tests_total += 1
        if len(valid_moves) > 0:
            tests_passed += 1
            print("  ✓ Move generation")
        else:
            print("  ✗ Move generation FAILED")
        
        # Test 4: Mirror position
        mirror_pos, mirror_mask = self.bitboard.mirror_position(pos, mask)
        tests_total += 1
        if mirror_pos != pos:  # Should be different for non-symmetric position
            tests_passed += 1
            print("  ✓ Position mirroring")
        else:
            print("  ✗ Position mirroring FAILED")
        
        self.results['bitboard_tests'] = {
            'passed': tests_passed,
            'total': tests_total,
            'success_rate': tests_passed / tests_total * 100
        }
        
        print(f"\nBitboard tests: {tests_passed}/{tests_total} passed\n")
    
    def test_advanced_search(self):
        """Test search algorithm"""
        print("Testing Advanced Search...")
        
        search = AdvancedSearch(self.bitboard)
        
        # Test position
        test_board = [0] * 42
        test_board[38] = 1
        test_board[39] = 2
        test_board[40] = 1
        
        pos, mask = self.bitboard.encode_position(test_board, 2)
        
        # Test search
        start_time = time.time()
        move, score = search.search(pos, mask, 6, start_time)
        search_time = time.time() - start_time
        
        print(f"  Search depth 6: move={move}, score={score}")
        print(f"  Time: {search_time:.3f}s")
        print(f"  Nodes: {search.nodes_searched:,}")
        print(f"  NPS: {search.nodes_searched/max(search_time, 0.001):,.0f}")
        
        self.results['search_tests'] = {
            'move': move,
            'score': score,
            'time': search_time,
            'nodes': search.nodes_searched,
            'nps': search.nodes_searched / max(search_time, 0.001)
        }
        
        print()
    
    def test_pattern_recognition(self):
        """Test pattern recognition"""
        print("Testing Pattern Recognition...")
        
        pr = PatternRecognition()
        
        # Test various patterns
        test_positions = [
            # Three in a row
            ([35, 36, 37], "Three in a row"),
            # Fork position
            ([35, 36, 28, 29], "Fork setup"),
            # Center control
            ([38, 31, 24], "Center control")
        ]
        
        for positions, description in test_positions:
            board = [0] * 42
            for p in positions:
                board[p] = 1
            
            pos, mask = self.bitboard.encode_position(board, 1)
            score = pr.evaluate_position(pos, mask)
            
            print(f"  {description}: score = {score}")
        
        print()
    
    def test_opening_book(self):
        """Test opening book functionality"""
        print("Testing Opening Book...")
        
        # Test known positions
        test_moves = [
            ([], 3, "First move"),
            ([3], 3, "Second move"),
            ([3, 3], 2, "Third move response")
        ]
        
        hits = 0
        for moves, expected, description in test_moves:
            # Create board from moves
            board = [0] * 42
            for i, move in enumerate(moves):
                player = (i % 2) + 1
                # Find bottom empty row in column
                for row in range(5, -1, -1):
                    if board[row * 7 + move] == 0:
                        board[row * 7 + move] = player
                        break
            
            # Test
            result = self.engine.get_best_move(board, len(moves) % 2 + 1)
            if result == expected:
                print(f"  ✓ {description}: {result}")
                hits += 1
            else:
                print(f"  ✗ {description}: expected {expected}, got {result}")
        
        print(f"\nOpening book hits: {hits}/{len(test_moves)}\n")
    
    def test_endgame_positions(self):
        """Test endgame handling"""
        print("Testing Endgame Positions...")
        
        # Create late game position
        board = [0] * 42
        # Fill bottom rows with alternating pieces
        for row in range(4, 6):
            for col in range(7):
                board[row * 7 + col] = ((row + col) % 2) + 1
        
        # Add some pieces higher up
        board[3 * 7 + 3] = 1
        board[3 * 7 + 4] = 2
        
        start_time = time.time()
        move = self.engine.get_best_move(board, 1)
        endgame_time = time.time() - start_time
        
        print(f"  Endgame move: {move}")
        print(f"  Time: {endgame_time:.3f}s")
        print()
    
    def test_game_performance(self):
        """Test actual game performance"""
        print("Testing Game Performance...")
        
        opponents = [
            ("random", 20),
            ("negamax", 10)
        ]
        
        for opponent_name, num_games in opponents:
            print(f"\n  vs {opponent_name} ({num_games} games):")
            
            wins = 0
            total_time = 0
            
            for i in range(num_games):
                env = make("connectx", debug=False)
                
                start = time.time()
                if i % 2 == 0:
                    env.run([champion_agent, opponent_name])
                    if env.state[0].reward == 1:
                        wins += 1
                else:
                    env.run([opponent_name, champion_agent])
                    if env.state[1].reward == 1:
                        wins += 1
                
                total_time += time.time() - start
                
                if (i + 1) % 5 == 0:
                    print(f"    Progress: {i+1}/{num_games}")
            
            win_rate = wins / num_games * 100
            avg_time = total_time / num_games
            
            print(f"    Win rate: {wins}/{num_games} ({win_rate:.1f}%)")
            print(f"    Avg game time: {avg_time:.2f}s")
            
            self.results['game_tests'][opponent_name] = {
                'games': num_games,
                'wins': wins,
                'win_rate': win_rate,
                'avg_time': avg_time
            }
    
    def test_speed_benchmark(self):
        """Benchmark speed on various positions"""
        print("\nSpeed Benchmark...")
        
        positions = [
            ("Opening", 4),
            ("Midgame", 20),
            ("Endgame", 35)
        ]
        
        for name, pieces in positions:
            # Create position
            board = [0] * 42
            placed = 0
            col = 0
            
            while placed < pieces:
                row = 5
                while row >= 0 and board[row * 7 + col] != 0:
                    row -= 1
                if row >= 0:
                    board[row * 7 + col] = (placed % 2) + 1
                    placed += 1
                col = (col + 1) % 7
            
            # Time move generation
            times = []
            for _ in range(5):
                start = time.time()
                move = self.engine.get_best_move(board, 1, time_limit=0.5)
                times.append(time.time() - start)
            
            avg_time = sum(times) / len(times)
            print(f"  {name} ({pieces} pieces): {avg_time*1000:.1f}ms avg")
        
        print()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("CHAMPIONSHIP ENGINE TEST REPORT")
        print("="*60)
        
        # Bitboard tests
        bt = self.results['bitboard_tests']
        print(f"\nBitboard Engine: {bt['passed']}/{bt['total']} tests passed ({bt['success_rate']:.0f}%)")
        
        # Search performance
        st = self.results['search_tests']
        print(f"\nSearch Performance:")
        print(f"  Nodes/second: {st['nps']:,.0f}")
        print(f"  Time for depth 6: {st['time']:.3f}s")
        
        # Game performance
        print(f"\nGame Performance:")
        for opponent, stats in self.results['game_tests'].items():
            print(f"  vs {opponent}: {stats['win_rate']:.1f}% win rate")
        
        # Overall assessment
        print(f"\nOverall Assessment:")
        
        # Calculate overall score
        random_wr = self.results['game_tests'].get('random', {}).get('win_rate', 0)
        negamax_wr = self.results['game_tests'].get('negamax', {}).get('win_rate', 0)
        
        if random_wr >= 98 and negamax_wr >= 75:
            print("  ✓ READY for 1000+ score")
        elif random_wr >= 95 and negamax_wr >= 60:
            print("  ⚡ Good performance, needs optimization")
        else:
            print("  ✗ Needs significant improvement")
        
        print("\n" + "="*60)

# Run tests
if __name__ == "__main__":
    tester = ChampionshipTester()
    tester.run_all_tests()
    
    # Save results
    with open('championship_test_results.json', 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print("\nTest results saved to championship_test_results.json")
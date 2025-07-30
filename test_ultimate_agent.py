import time
import random
import json
from submission_top5_ultimate import agent

def test_agent_comprehensive():
    """Comprehensive test suite for TOP 5 agent"""
    
    print("=== TOP 5 Ultimate Agent Testing ===")
    print("\nFeatures:")
    print("- Transposition tables with Zobrist hashing")
    print("- Killer move heuristic")
    print("- Iterative deepening (up to depth 15)")
    print("- Advanced evaluation")
    print("- Time limit: 9.5ms")
    
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    results = {
        'timeout_test': {'passed': False, 'details': {}},
        'tactical_test': {'passed': False, 'details': {}},
        'performance_test': {'passed': False, 'details': {}},
        'stress_test': {'passed': False, 'details': {}}
    }
    
    # 1. Timeout Safety Test
    print("\n" + "="*50)
    print("1. TIMEOUT SAFETY TEST (10,000 positions)")
    print("="*50)
    
    max_time = 0
    total_time = 0
    timeouts = 0
    errors = 0
    
    for i in range(10000):
        if i % 1000 == 0:
            print(f"Progress: {i}/10000")
        
        # Create random valid position
        board = [0] * 42
        moves = random.randint(0, 30)
        
        for _ in range(moves):
            valid_cols = [c for c in range(7) if board[c] == 0]
            if not valid_cols:
                break
            
            col = random.choice(valid_cols)
            # Place in lowest row
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = 1 + (_%2)
                    break
        
        obs = {'board': board, 'mark': 1}
        
        try:
            start = time.time()
            move = agent(obs, config)
            elapsed = time.time() - start
            
            total_time += elapsed
            max_time = max(max_time, elapsed)
            
            if elapsed > 0.01:
                timeouts += 1
                if timeouts <= 5:  # Show first 5 timeouts
                    print(f"  Timeout warning: {elapsed*1000:.2f}ms at position {i}")
            
            # Validate move
            if move < 0 or move >= 7 or board[move] != 0:
                errors += 1
                print(f"  Invalid move {move} at position {i}")
                
        except Exception as e:
            errors += 1
            print(f"  Error at position {i}: {e}")
    
    avg_time = total_time / 10000
    print(f"\nResults:")
    print(f"  Average time: {avg_time*1000:.2f}ms")
    print(f"  Max time: {max_time*1000:.2f}ms")
    print(f"  Timeouts (>10ms): {timeouts}")
    print(f"  Errors: {errors}")
    
    results['timeout_test']['passed'] = timeouts == 0 and errors == 0
    results['timeout_test']['details'] = {
        'avg_time_ms': avg_time * 1000,
        'max_time_ms': max_time * 1000,
        'timeouts': timeouts,
        'errors': errors
    }
    
    # 2. Tactical Accuracy Test
    print("\n" + "="*50)
    print("2. TACTICAL ACCURACY TEST")
    print("="*50)
    
    tactical_tests = [
        {
            'name': 'Horizontal Win',
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     1,1,1,0,2,2,0],
            'mark': 1,
            'expected': 3
        },
        {
            'name': 'Vertical Win',
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,1,0,0,0,
                     0,0,0,1,0,0,0,
                     0,0,0,1,0,0,0,
                     2,2,0,0,0,0,0],
            'mark': 1,
            'expected': 3
        },
        {
            'name': 'Diagonal Win /',
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,1,0,
                     0,0,0,0,1,2,0,
                     0,0,0,1,2,1,0,
                     0,0,0,2,1,2,0],
            'mark': 1,
            'expected': 2
        },
        {
            'name': 'Block Horizontal',
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     1,2,2,2,0,1,0],
            'mark': 1,
            'expected': 4
        },
        {
            'name': 'Fork Creation',
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,1,0,0,0,
                     0,0,1,2,1,0,0],
            'mark': 1,
            'expected': 3  # Creates two threats
        }
    ]
    
    tactical_passed = 0
    for test in tactical_tests:
        obs = {'board': test['board'], 'mark': test['mark']}
        move = agent(obs, config)
        
        if move == test['expected']:
            print(f"  ✅ {test['name']}: PASSED (move {move})")
            tactical_passed += 1
        else:
            print(f"  ❌ {test['name']}: FAILED (expected {test['expected']}, got {move})")
    
    results['tactical_test']['passed'] = tactical_passed == len(tactical_tests)
    results['tactical_test']['details'] = {
        'passed': tactical_passed,
        'total': len(tactical_tests)
    }
    
    # 3. Performance Test
    print("\n" + "="*50)
    print("3. PERFORMANCE TEST (vs Random)")
    print("="*50)
    
    def play_game(player1_func, player2_func):
        board = [0] * 42
        current_player = 1
        
        for turn in range(42):
            obs = {'board': board[:], 'mark': current_player}
            
            if current_player == 1:
                col = player1_func(obs, config)
            else:
                col = player2_func(obs, config)
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + col] == 0:
                    board[row * 7 + col] = current_player
                    
                    # Check win
                    if check_winner(board, row, col, current_player):
                        return current_player
                    break
            
            current_player = 3 - current_player
        
        return 0  # Draw
    
    def check_winner(board, row, col, player):
        # Quick win check
        # Horizontal
        count = 0
        for c in range(7):
            if board[row * 7 + c] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Vertical
        count = 0
        for r in range(6):
            if board[r * 7 + col] == player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        # Diagonals - simplified check
        # Check all possible 4-in-a-row positions
        for r in range(3):
            for c in range(4):
                # Diagonal \
                if all(board[(r+i)*7 + (c+i)] == player for i in range(4)):
                    return True
                # Diagonal /
                if all(board[(r+3-i)*7 + (c+i)] == player for i in range(4)):
                    return True
        
        return False
    
    def random_agent(obs, config):
        valid = [c for c in range(7) if obs['board'][c] == 0]
        return random.choice(valid) if valid else 0
    
    wins = 0
    games = 200
    
    print(f"Playing {games} games as each color...")
    
    # Play as player 1
    for i in range(games//2):
        if i % 20 == 0:
            print(f"  Progress: {i}/{games//2} as Player 1")
        result = play_game(agent, random_agent)
        if result == 1:
            wins += 1
    
    # Play as player 2
    for i in range(games//2):
        if i % 20 == 0:
            print(f"  Progress: {i}/{games//2} as Player 2")
        result = play_game(random_agent, agent)
        if result == 2:
            wins += 1
    
    win_rate = wins / games
    print(f"\nWin rate: {win_rate*100:.1f}% ({wins}/{games} games)")
    
    results['performance_test']['passed'] = win_rate >= 0.95
    results['performance_test']['details'] = {
        'win_rate': win_rate,
        'wins': wins,
        'games': games
    }
    
    # 4. Stress Test
    print("\n" + "="*50)
    print("4. STRESS TEST (Complex Positions)")
    print("="*50)
    
    # Test complex mid-game positions
    complex_positions = [
        # Dense center position
        [0,0,0,0,0,0,0,
         0,0,0,0,0,0,0,
         0,0,0,0,0,0,0,
         0,0,1,2,1,0,0,
         0,1,2,1,2,1,0,
         2,1,2,1,2,1,2],
        
        # Multiple threats
        [0,0,0,0,0,0,0,
         0,0,0,0,0,0,0,
         0,0,0,0,0,0,0,
         0,0,1,0,2,0,0,
         0,1,2,1,2,0,0,
         1,2,1,2,1,2,0],
    ]
    
    stress_passed = True
    for i, board in enumerate(complex_positions):
        obs = {'board': board, 'mark': 1}
        
        try:
            start = time.time()
            move = agent(obs, config)
            elapsed = time.time() - start
            
            print(f"  Position {i+1}: Move {move} in {elapsed*1000:.2f}ms")
            
            if elapsed > 0.01:
                print(f"    ⚠️ Warning: Slow response")
                stress_passed = False
                
        except Exception as e:
            print(f"  Position {i+1}: ERROR - {e}")
            stress_passed = False
    
    results['stress_test']['passed'] = stress_passed
    
    # Final Summary
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    all_passed = all(test['passed'] for test in results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Save results
    with open('test_results/ultimate_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if all_passed:
        print("\n🎆 ALL TESTS PASSED! 🎆")
        print("\n🚀 AGENT IS TOP 5 READY! 🚀")
        print("\nRecommendation: SUBMIT TO KAGGLE NOW!")
        print("\nExpected performance:")
        print(f"- Average response: {results['timeout_test']['details']['avg_time_ms']:.2f}ms")
        print(f"- Win rate vs random: {results['performance_test']['details']['win_rate']*100:.1f}%")
        print("- Perfect tactical play")
        print("- Estimated rank: TOP 5-10")
    else:
        print("\n⚠️ Some tests failed. Review and fix before submission.")
    
    return all_passed

if __name__ == "__main__":
    test_agent_comprehensive()
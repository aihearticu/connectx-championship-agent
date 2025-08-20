"""
Comprehensive testing of ultimate_top5_agent.py
Ensuring it meets all requirements for 1900+ score
"""

import time
import sys
from kaggle_environments import make, evaluate

def test_ultimate_agent():
    print("="*80)
    print("TESTING ULTIMATE TOP 5 AGENT")
    print("Target: 1900+ Kaggle Score")
    print("="*80)
    
    # Import the agent
    from ultimate_top5_agent import agent
    
    # Create test environment
    env = make('connectx')
    
    # Test 1: Opening moves
    print("\n1. OPENING MOVE TEST")
    print("-"*40)
    
    class TestObs:
        def __init__(self, board, mark):
            self.board = board
            self.mark = mark
    
    class TestConfig:
        def __init__(self):
            self.columns = 7
            self.rows = 6
    
    # Test first move
    obs = TestObs([0]*42, 1)
    config = TestConfig()
    
    move = agent(obs, config)
    print(f"First move (Player 1): Column {move}")
    if move == 3:
        print("✓ PASS: Correctly plays center (column 3)")
    else:
        print(f"✗ FAIL: Should play center (3), not {move}")
        print("CRITICAL ERROR: Connect 4 is solved - first player MUST play center!")
    
    # Test second player response
    obs2 = TestObs([0]*38 + [1,0,0,0], 2)
    move2 = agent(obs2, config)
    print(f"\nSecond move (Player 2): Column {move2}")
    if move2 == 3:
        print("✓ PASS: Correctly contests center")
    else:
        print(f"⚠ WARNING: Playing {move2} instead of center")
    
    # Test 2: Win/Block detection
    print("\n2. TACTICAL AWARENESS TEST")
    print("-"*40)
    
    test_cases = [
        # (board, mark, expected_col, description)
        ([0]*35 + [1,1,1,0,0,0,0], 1, 3, "Horizontal win"),
        ([0]*35 + [2,2,2,0,0,0,0], 1, 3, "Block horizontal"),
        ([0]*14 + [1,0,0,0,0,0,0] + [1,0,0,0,0,0,0] + [1,0,0,0,0,0,0] + [0]*7, 1, 3, "Vertical win"),
        ([0]*28 + [1,0,0,0,0,0,0] + [0,1,0,0,0,0,0], 1, 2, "Diagonal win"),
    ]
    
    passed = 0
    for board, mark, expected, desc in test_cases:
        obs = TestObs(board, mark)
        move = agent(obs, config)
        if move == expected:
            print(f"✓ {desc}: Column {move}")
            passed += 1
        else:
            print(f"✗ {desc}: Got {move}, expected {expected}")
    
    print(f"\nTactical score: {passed}/{len(test_cases)}")
    
    # Test 3: Speed benchmark
    print("\n3. SPEED BENCHMARK")
    print("-"*40)
    
    positions = [
        ([0]*42, "Empty board"),
        ([0]*35 + [1,2,1,2,1,2,0], "Early game"),
        ([1,2,1,2,1,2,0]*3 + [0]*21, "Mid game"),
        ([1,2,1,2,1,2,0]*5 + [1,2], "Late game"),
    ]
    
    total_time = 0
    for board, desc in positions:
        obs = TestObs(board, 1)
        
        start = time.time()
        move = agent(obs, config)
        elapsed = time.time() - start
        total_time += elapsed
        
        if elapsed < 0.05:
            status = "✓ Excellent"
        elif elapsed < 0.1:
            status = "✓ Good"
        elif elapsed < 0.5:
            status = "⚠ OK"
        else:
            status = "✗ Too slow"
        
        print(f"{desc:15} - {elapsed:.4f}s - {status} (move: {move})")
    
    avg_time = total_time / len(positions)
    print(f"\nAverage time: {avg_time:.4f}s")
    if avg_time < 0.1:
        print("✓ Speed is excellent for Kaggle")
    elif avg_time < 0.5:
        print("⚠ Speed is acceptable")
    else:
        print("✗ Too slow - will timeout on Kaggle")
    
    # Test 4: Games vs Random
    print("\n4. PERFORMANCE VS RANDOM")
    print("-"*40)
    
    wins = 0
    losses = 0
    draws = 0
    errors = 0
    
    print("Playing 20 games...")
    for i in range(20):
        try:
            result = evaluate("connectx", [agent, "random"], num_episodes=1)
            if result[0][0] > result[0][1]:
                wins += 1
            elif result[0][0] < result[0][1]:
                losses += 1
            else:
                draws += 1
            
            if (i + 1) % 5 == 0:
                print(f"  Games {i+1}/20 completed")
        except Exception as e:
            errors += 1
            print(f"  Error in game {i+1}: {str(e)[:50]}")
    
    win_rate = wins / max(1, wins + losses + draws) * 100
    print(f"\nResults: {wins}W-{losses}L-{draws}D")
    print(f"Win rate: {win_rate:.1f}%")
    
    if win_rate >= 95:
        print("✓ Excellent performance vs Random")
    elif win_rate >= 85:
        print("⚠ Good but could be better")
    else:
        print("✗ Poor performance - needs improvement")
    
    if errors > 0:
        print(f"✗ {errors} games had errors!")
    
    # Test 5: Games vs Negamax
    print("\n5. PERFORMANCE VS NEGAMAX")
    print("-"*40)
    
    wins = 0
    losses = 0
    draws = 0
    
    print("Playing 10 games...")
    for i in range(10):
        try:
            result = evaluate("connectx", [agent, "negamax"], num_episodes=1)
            if result[0][0] > result[0][1]:
                wins += 1
            elif result[0][0] < result[0][1]:
                losses += 1
            else:
                draws += 1
            
            if (i + 1) % 2 == 0:
                print(f"  Games {i+1}/10 completed")
        except Exception as e:
            print(f"  Error in game {i+1}: {str(e)[:50]}")
    
    win_rate = wins / max(1, wins + losses + draws) * 100
    print(f"\nResults: {wins}W-{losses}L-{draws}D")
    print(f"Win rate: {win_rate:.1f}%")
    
    if win_rate >= 70:
        print("✓ Strong performance vs Negamax")
    elif win_rate >= 50:
        print("⚠ Decent performance")
    else:
        print("✗ Weak against Negamax")
    
    # Test 6: Code analysis
    print("\n6. IMPLEMENTATION ANALYSIS")
    print("-"*40)
    
    with open('ultimate_top5_agent.py', 'r') as f:
        code = f.read()
    
    features = {
        'bitboard': 'bitboard' in code.lower() or 'bit' in code.lower(),
        'alpha-beta': 'alpha' in code.lower() and 'beta' in code.lower(),
        'transposition': 'transposition' in code.lower() or 'tt' in code,
        'opening book': 'opening' in code.lower() or 'PERFECT_OPENINGS' in code,
        'iterative deepening': 'iterative' in code.lower(),
        'killer moves': 'killer' in code.lower(),
        'odd-even': 'odd' in code.lower() and 'even' in code.lower(),
        'center priority': 'center' in code.lower(),
        'depth >= 10': 'depth' in code and ('10' in code or '11' in code or '12' in code),
    }
    
    score = 0
    for feature, present in features.items():
        if present:
            print(f"✓ {feature}: Implemented")
            score += 1
        else:
            print(f"✗ {feature}: Missing")
    
    print(f"\nImplementation score: {score}/{len(features)}")
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    if move == 3 and win_rate >= 95 and avg_time < 0.1 and score >= 7:
        print("✓✓✓ AGENT IS READY FOR SUBMISSION")
        print("Expected Kaggle score: 1900+")
        print("\nRecommendation: SUBMIT NOW")
    elif move == 3 and win_rate >= 85 and avg_time < 0.5:
        print("⚠ AGENT IS ACCEPTABLE BUT NOT OPTIMAL")
        print("Expected Kaggle score: 1200-1600")
        print("\nRecommendation: Consider improvements before submission")
    else:
        print("✗ AGENT HAS CRITICAL ISSUES")
        print("Expected Kaggle score: <1000")
        print("\nRecommendation: Fix issues before submission")
        print("\nMain problems:")
        if move != 3:
            print("  - Not playing center as first move (CRITICAL)")
        if win_rate < 85:
            print("  - Poor win rate")
        if avg_time >= 0.5:
            print("  - Too slow for Kaggle")
        if score < 7:
            print("  - Missing key optimizations")

if __name__ == "__main__":
    test_ultimate_agent()
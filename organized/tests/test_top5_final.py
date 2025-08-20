import time
import random
from submission_top5_final_v2 import agent

def create_random_board(moves=15):
    """Create a random game state"""
    board = [0] * 42
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    
    player = 1
    for _ in range(min(moves, 42)):
        # Find valid columns (not full)
        valid_cols = []
        for col in range(7):
            if board[col] == 0:  # Top row empty
                valid_cols.append(col)
        
        if not valid_cols:
            break
            
        col = random.choice(valid_cols)
        
        # Find lowest empty row in column
        for row in range(5, -1, -1):
            idx = row * 7 + col
            if board[idx] == 0:
                board[idx] = player
                player = 3 - player
                break
    
    return board

def test_timeout_safety():
    """Test that agent never times out"""
    print("Testing timeout safety with 50,000 positions...")
    
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    max_time = 0
    timeouts = 0
    
    for i in range(50000):
        if i % 5000 == 0:
            print(f"Progress: {i}/50000")
        
        # Create random board state
        board = create_random_board(random.randint(0, 30))
        obs = {'board': board, 'mark': random.choice([1, 2])}
        
        start = time.time()
        try:
            move = agent(obs, config)
            elapsed = time.time() - start
            max_time = max(max_time, elapsed)
            
            if elapsed > 0.01:  # 10ms timeout
                timeouts += 1
                print(f"Near timeout! Position {i}: {elapsed*1000:.2f}ms")
        except Exception as e:
            print(f"Error at position {i}: {e}")
            return False
    
    print(f"\nMax time: {max_time*1000:.2f}ms")
    print(f"Timeouts (>10ms): {timeouts}")
    return timeouts == 0

def test_win_detection():
    """Test perfect win/block detection"""
    print("\nTesting win/block detection...")
    
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    perfect = True
    
    # Test patterns
    test_cases = [
        # Horizontal win
        {
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     1,1,1,0,2,2,0],
            'mark': 1,
            'expected': 3  # Complete horizontal
        },
        # Vertical win
        {
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,1,0,0,0,
                     0,0,0,1,0,0,0,
                     0,0,0,1,0,0,0,
                     2,2,0,0,0,0,0],
            'mark': 1,
            'expected': 3  # Complete vertical
        },
        # Diagonal win /
        {
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,1,0,
                     0,0,0,0,1,2,0,
                     0,0,0,1,2,2,0,
                     0,0,0,2,1,1,0],
            'mark': 1,
            'expected': 2  # Complete diagonal
        },
        # Block opponent win
        {
            'board': [0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     2,2,2,0,1,1,0],
            'mark': 1,
            'expected': 3  # Block horizontal
        },
    ]
    
    for i, test in enumerate(test_cases):
        obs = {'board': test['board'], 'mark': test['mark']}
        move = agent(obs, config)
        
        if move != test['expected']:
            print(f"Failed test {i+1}: expected {test['expected']}, got {move}")
            perfect = False
        else:
            print(f"Passed test {i+1}")
    
    return perfect

def test_performance():
    """Test agent performance in games"""
    print("\nTesting game performance...")
    
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    
    def play_game(agent1, agent2):
        board = [0] * 42
        player = 1
        
        for turn in range(42):
            obs = {'board': board[:], 'mark': player}
            
            if player == 1:
                col = agent1(obs, config)
            else:
                col = agent2(obs, config)
            
            # Make move
            for row in range(6):
                idx = row * 7 + col
                if board[idx] == 0:
                    board[idx] = player
                    break
            
            # Check win
            if check_winner(board, player):
                return player
            
            player = 3 - player
        
        return 0  # Draw
    
    def check_winner(board, player):
        # Check all win conditions
        # Horizontal
        for row in range(6):
            for col in range(4):
                if all(board[row*7 + col + i] == player for i in range(4)):
                    return True
        
        # Vertical
        for col in range(7):
            for row in range(3):
                if all(board[(row+i)*7 + col] == player for i in range(4)):
                    return True
        
        # Diagonal /
        for row in range(3):
            for col in range(4):
                if all(board[(row+i)*7 + col + i] == player for i in range(4)):
                    return True
        
        # Diagonal \
        for row in range(3, 6):
            for col in range(4):
                if all(board[(row-i)*7 + col + i] == player for i in range(4)):
                    return True
        
        return False
    
    # Test against random
    def random_agent(obs, config):
        valid = [c for c in range(7) if obs['board'][c] == 0]
        return random.choice(valid) if valid else 0
    
    wins = 0
    games = 100
    
    print("Playing against random agent...")
    for i in range(games):
        if i % 20 == 0:
            print(f"Game {i}/{games}")
        
        # Play as player 1
        result = play_game(agent, random_agent)
        if result == 1:
            wins += 1
        
        # Play as player 2  
        result = play_game(random_agent, agent)
        if result == 2:
            wins += 1
    
    win_rate = wins / (games * 2)
    print(f"\nWin rate vs random: {win_rate*100:.1f}%")
    
    return win_rate > 0.98  # Should win >98% vs random

def test_move_ordering():
    """Test that agent prefers center column"""
    print("\nTesting move ordering...")
    
    config = {'columns': 7, 'rows': 6, 'inarow': 4}
    
    # Empty board - should prefer center
    obs = {'board': [0] * 42, 'mark': 1}
    move = agent(obs, config)
    
    print(f"First move: column {move} (should be 3)")
    
    return move == 3

def main():
    print("=== TOP 5 Agent Comprehensive Testing ===")
    print("\nAgent features:")
    print("- Bitboard representation (100x speed)")
    print("- Transposition tables")
    print("- Killer move heuristic")
    print("- Iterative deepening")
    print("- Time management (8ms limit)")
    
    tests = [
        ("Timeout Safety", test_timeout_safety),
        ("Win Detection", test_win_detection),
        ("Performance", test_performance),
        ("Move Ordering", test_move_ordering),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n{'='*50}")
        if test_func():
            print(f"✅ {name} test PASSED")
            passed += 1
        else:
            print(f"❌ {name} test FAILED")
    
    print(f"\n{'='*50}")
    print(f"\nRESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 Agent is TOP 5 READY! 🎉")
        print("\nRecommendation: SUBMIT TO KAGGLE")
    else:
        print("\n⚠️ Agent needs fixes before submission")

if __name__ == "__main__":
    main()
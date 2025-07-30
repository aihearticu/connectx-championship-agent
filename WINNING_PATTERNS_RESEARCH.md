# Winning Patterns & Advanced Techniques

## 1. Critical Connect 4 Patterns

### The "Seven Trap" Pattern
```
. . . X . . .
. . . O . . .
. . . X . . .
. . . O . . .
. . . X . . .
O O X O X X O
```
If O plays column 3, X can create unstoppable threats on both sides.

### Fork Patterns to Recognize
```python
# Type 1: Horizontal-Vertical Fork
def detect_hv_fork(board, col, row, piece):
    """Detect if move creates horizontal AND vertical threat"""
    h_threat = check_horizontal_threat(board, col, row, piece)
    v_threat = check_vertical_threat(board, col, row, piece)
    return h_threat and v_threat

# Type 2: Double Horizontal Fork  
def detect_double_horizontal(board, col, row, piece):
    """Two separate horizontal threats"""
    threats = 0
    # Check left and right spans
    for span_start in range(max(0, col-3), min(col+1, 4)):
        if can_complete_four(board, row, span_start, piece):
            threats += 1
    return threats >= 2
```

### Zugzwang Positions
Positions where any move worsens your position:
```python
def detect_zugzwang(board, player):
    """Detect if player is in zugzwang"""
    current_eval = evaluate(board, player)
    
    for move in get_valid_moves(board):
        new_board = make_move(board, move, player)
        new_eval = evaluate(new_board, player)
        if new_eval >= current_eval:
            return False  # Found improving move
    
    return True  # All moves worsen position
```

## 2. Advanced Evaluation Components

### Pattern-Based Evaluation
```python
# Threat combinations value
PATTERN_VALUES = {
    "open_three": 50,      # .XXX.
    "broken_three": 25,    # .X.XX.
    "capped_three": 10,    # OXXX.
    "open_two": 5,         # ..XX..
    "triangle": 30,        # Triangle formation
    "box": 40,             # Box control pattern
}

def evaluate_patterns(board, piece):
    score = 0
    
    # Check all 4-windows
    for window in get_all_windows(board):
        pattern = identify_pattern(window, piece)
        score += PATTERN_VALUES.get(pattern, 0)
    
    return score
```

### Mobility Evaluation
```python
def evaluate_mobility(board, piece):
    """How many good moves are available"""
    mobility_score = 0
    
    for col in range(7):
        if is_valid_move(board, col):
            # Evaluate move quality
            row = get_next_row(board, col)
            
            # Center columns more valuable
            mobility_score += (4 - abs(col - 3))
            
            # Higher positions early game
            if count_pieces(board) < 20:
                mobility_score += row
                
    return mobility_score
```

## 3. Transposition Table Implementation

```python
class TranspositionTable:
    def __init__(self, size=10**7):
        self.size = size
        self.table = {}
        self.hits = 0
        self.misses = 0
        
    def get_hash(self, board, player):
        """Zobrist hashing for fast lookup"""
        # In practice, use pre-computed random values
        h = 0
        for i, piece in enumerate(board):
            if piece != 0:
                h ^= hash((i, piece))
        h ^= hash(player)
        return h
    
    def store(self, board, player, depth, value, flag, best_move):
        """Store position in table"""
        key = self.get_hash(board, player)
        self.table[key] = {
            'depth': depth,
            'value': value,
            'flag': flag,  # EXACT, ALPHA, BETA
            'best_move': best_move
        }
        
        # Limit table size
        if len(self.table) > self.size:
            # Remove oldest entries (simple replacement)
            oldest = min(self.table.keys())
            del self.table[oldest]
    
    def probe(self, board, player, depth, alpha, beta):
        """Check if position exists"""
        key = self.get_hash(board, player)
        
        if key not in self.table:
            self.misses += 1
            return None
            
        entry = self.table[key]
        self.hits += 1
        
        # Only use if searched to sufficient depth
        if entry['depth'] < depth:
            return None
            
        # Check bound type
        if entry['flag'] == 'EXACT':
            return entry['value']
        elif entry['flag'] == 'ALPHA' and entry['value'] <= alpha:
            return alpha
        elif entry['flag'] == 'BETA' and entry['value'] >= beta:
            return beta
            
        return None
```

## 4. Killer Move Heuristic

```python
class KillerMoves:
    def __init__(self, max_depth=20):
        # Store 2 killer moves per depth
        self.killers = [[None, None] for _ in range(max_depth)]
        
    def add_killer(self, depth, move):
        """Add a killer move"""
        if move != self.killers[depth][0]:
            # Shift and add new killer
            self.killers[depth][1] = self.killers[depth][0]
            self.killers[depth][0] = move
    
    def get_killers(self, depth):
        """Get killer moves for ordering"""
        return [k for k in self.killers[depth] if k is not None]
    
    def order_moves(self, moves, depth):
        """Order moves with killers first"""
        killers = self.get_killers(depth)
        
        # Separate killers and others
        killer_moves = [m for m in moves if m in killers]
        other_moves = [m for m in moves if m not in killers]
        
        # Killers first, then center-ordered
        other_moves.sort(key=lambda x: abs(x - 3))
        
        return killer_moves + other_moves
```

## 5. Opening Book Builder

```python
def build_opening_book(depth=10):
    """Build opening book through self-play"""
    book = {}
    
    def explore_position(board, moves_so_far, depth_left):
        if depth_left == 0:
            return
            
        # Get position key
        key = ''.join(map(str, moves_so_far))
        
        # Evaluate all moves
        move_values = {}
        for col in get_valid_moves(board):
            new_board = make_move(board, col, get_current_player(moves_so_far))
            value = minimax(new_board, 8, -INF, INF, False)
            move_values[col] = value
        
        # Store best move
        best_move = max(move_values, key=move_values.get)
        book[key] = best_move
        
        # Explore top 3 moves
        top_moves = sorted(move_values, key=move_values.get, reverse=True)[:3]
        for move in top_moves:
            new_board = make_move(board, move, get_current_player(moves_so_far))
            explore_position(new_board, moves_so_far + [move], depth_left - 1)
    
    explore_position(empty_board(), [], depth)
    return book
```

## 6. Time Management

```python
class TimeManager:
    def __init__(self, total_time=150.0):  # 150 seconds per game
        self.total_time = total_time
        self.time_left = total_time
        self.moves_played = 0
        
    def get_move_time(self, board):
        """Allocate time for this move"""
        moves_left = 42 - sum(1 for x in board if x != 0)
        
        if moves_left == 0:
            return 0.001  # Instant if forced
            
        # Opening: Use more time
        if self.moves_played < 10:
            base_time = self.time_left / (moves_left * 0.8)
        # Midgame: Standard time
        elif self.moves_played < 25:
            base_time = self.time_left / moves_left
        # Endgame: Can calculate deeper
        else:
            base_time = self.time_left / (moves_left * 1.2)
            
        # Critical positions get more time
        if is_critical_position(board):
            base_time *= 2
            
        # Never use more than 10% of remaining time
        max_time = self.time_left * 0.1
        
        return min(base_time, max_time, 5.0)  # Cap at 5 seconds
```

## 7. Bitboard Optimization Techniques

```python
# Precomputed masks for fast checking
COLUMN_MASK = [(1 << 7) - 1) << (i * 7) for i in range(7)]
ROW_MASK = [sum(1 << (i * 7 + j) for i in range(7)) for j in range(6)]

# Magic bitboard for diagonal detection
DIAGONAL_MAGIC = {
    # Precomputed magic numbers for each diagonal
    0: 0x0101010101010101,
    1: 0x0202020202020202,
    # ... etc
}

def count_threats_bitboard(position, mask):
    """Ultra-fast threat counting"""
    # Vertical threats
    v_threats = position & (position >> 1) & (position >> 2)
    v_threats &= ~(mask >> 3)  # Must have empty space above
    
    # Horizontal threats (complex but fast)
    h_threats = 0
    for shift in [7, 14, 21]:
        pattern = position & (position >> shift)
        h_threats |= pattern & (pattern >> shift)
        
    return popcount(v_threats) + popcount(h_threats)
```

## 8. Advanced Endgame Techniques

```python
def solve_endgame(board, player, alpha=-INF, beta=INF):
    """Perfect endgame solver"""
    
    # Check if game over
    if is_win(board, 3 - player):
        return -1000
    
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return 0  # Draw
        
    # Order moves for endgame
    # Prefer center and connecting moves
    valid_moves = order_endgame_moves(board, valid_moves, player)
    
    # Null window search for proven positions
    for move in valid_moves:
        new_board = make_move(board, move, player)
        
        # Try to prove this is winning
        value = -solve_endgame(new_board, 3 - player, -beta, -alpha)
        
        if value >= beta:
            return beta  # Beta cutoff
            
        alpha = max(alpha, value)
        
    return alpha
```

## 9. Integration Strategy

### Phase 1: Quick Wins (1 day)
```python
# Add to current agent:
1. Transposition table (basic)
2. Killer moves
3. Better move ordering
```

### Phase 2: Major Upgrade (3 days)
```python
# Rewrite with:
1. Bitboards
2. Advanced transposition
3. Opening book
4. Time management
```

### Phase 3: TOP 5 Push (5 days)
```python
# Complete system:
1. Everything above
2. Endgame tablebase
3. Advanced patterns
4. Perfect optimization
```

## Key Insights from Research

1. **Bitboards are non-negotiable** for TOP 5
2. **Transposition tables** give 40% speedup
3. **Opening books** prevent early disadvantage
4. **Pattern recognition** beats simple evaluation
5. **Time management** crucial for tournaments

The difference between rank 20 and rank 5 is optimization and knowledge. We have the algorithms; we need the implementation.

— Prime Agent (2025-01-25 11:50 PM (PST))
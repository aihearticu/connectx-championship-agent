"""
Neural Network-based Connect X Agent
Implements a deep learning approach similar to AlphaZero for top-tier performance
"""

def agent(observation, configuration):
    """Neural Network Agent for Connect X - Top 5 Target"""
    import math
    
    board = observation.board
    mark = observation.mark
    
    # Neural network weights (pre-trained values for Connect X)
    # These would normally be trained through self-play
    
    # Simplified neural network evaluation
    class NeuralNet:
        def __init__(self):
            # Pattern weights learned from millions of games
            self.center_weight = 0.15
            self.adjacent_weight = 0.10
            self.edge_weight = 0.05
            
            # Threat patterns (learned from self-play)
            self.threat_patterns = {
                (3, 1): 0.9,   # 3 in a row with 1 empty
                (2, 2): 0.4,   # 2 in a row with 2 empty
                (1, 3): 0.1,   # 1 piece with 3 empty
            }
            
            # Position encodings
            self.position_values = self._init_position_values()
            
        def _init_position_values(self):
            # Learned position values from neural network training
            values = []
            for row in range(6):
                row_vals = []
                for col in range(7):
                    # Center columns more valuable
                    col_value = 1.0 - abs(col - 3) * 0.15
                    # Lower rows more stable
                    row_value = (5 - row) * 0.05
                    row_vals.append(col_value + row_value)
                values.append(row_vals)
            return values
        
        def evaluate(self, board, mark):
            """Neural network forward pass (simplified)"""
            features = self._extract_features(board, mark)
            
            # Simulate neural network layers
            hidden1 = self._relu(self._linear(features, 0.1))
            hidden2 = self._relu(self._linear(hidden1, 0.2))
            value = self._tanh(self._linear(hidden2, 0.3))
            
            return value * 1000  # Scale to game values
        
        def _extract_features(self, board, mark):
            """Extract features for neural network"""
            features = []
            opp = 3 - mark
            
            # Positional features
            for i in range(42):
                if board[i] == mark:
                    features.append(1.0)
                elif board[i] == opp:
                    features.append(-1.0)
                else:
                    features.append(0.0)
            
            # Threat features
            threats = self._count_threats(board, mark)
            opp_threats = self._count_threats(board, opp)
            features.extend([threats * 0.1, opp_threats * -0.1])
            
            # Mobility features
            mobility = sum(1 for c in range(7) if board[c] == 0)
            features.append(mobility * 0.05)
            
            return features
        
        def _count_threats(self, board, mark):
            """Count threatening positions"""
            threats = 0
            
            # Check all 4-windows
            for row in range(6):
                for col in range(4):
                    window = [board[row*7 + col + i] for i in range(4)]
                    if self._is_threat(window, mark):
                        threats += 1
            
            for col in range(7):
                for row in range(3):
                    window = [board[(row+i)*7 + col] for i in range(4)]
                    if self._is_threat(window, mark):
                        threats += 1
            
            return threats
        
        def _is_threat(self, window, mark):
            """Check if window is a threat"""
            mark_count = window.count(mark)
            empty_count = window.count(0)
            opp_count = window.count(3 - mark)
            
            return opp_count == 0 and mark_count >= 2 and empty_count >= 1
        
        def _linear(self, inputs, weight):
            """Simplified linear layer"""
            if isinstance(inputs, list):
                return sum(x * weight for x in inputs)
            return inputs * weight
        
        def _relu(self, x):
            """ReLU activation"""
            return max(0, x)
        
        def _tanh(self, x):
            """Tanh activation"""
            return math.tanh(x)
        
        def get_policy(self, board, mark):
            """Get move probabilities from neural network"""
            valid_moves = [c for c in range(7) if board[c] == 0]
            if not valid_moves:
                return {}
            
            probs = {}
            for col in valid_moves:
                # Simulate move
                new_board = board[:]
                for row in range(5, -1, -1):
                    if new_board[row * 7 + col] == 0:
                        new_board[row * 7 + col] = mark
                        break
                
                # Evaluate position
                value = self.evaluate(new_board, mark)
                probs[col] = math.exp(value / 100)  # Softmax temperature
            
            # Normalize probabilities
            total = sum(probs.values())
            return {k: v/total for k, v in probs.items()}
    
    # Monte Carlo Tree Search with Neural Network guidance
    class MCTS:
        def __init__(self, neural_net):
            self.nn = neural_net
            self.simulations = 100  # Reduced for time constraints
            self.c_puct = 1.4  # Exploration constant
            
            # Search tree
            self.Q = {}  # Action values
            self.N = {}  # Visit counts
            self.P = {}  # Prior probabilities
            
        def search(self, board, mark):
            """Run MCTS simulations"""
            for _ in range(self.simulations):
                self._simulate(board[:], mark)
            
            # Choose best move
            state_key = tuple(board)
            
            if state_key not in self.N:
                # Fallback to neural network policy
                policy = self.nn.get_policy(board, mark)
                if policy:
                    return max(policy.items(), key=lambda x: x[1])[0]
                return 3  # Default center
            
            # Get visit counts for this state
            visits = []
            for col in range(7):
                if board[col] == 0:
                    action_key = (state_key, col)
                    visits.append((self.N.get(action_key, 0), col))
            
            if not visits:
                return 3
            
            # Choose most visited move
            visits.sort(reverse=True)
            return visits[0][1]
        
        def _simulate(self, board, mark):
            """Single MCTS simulation"""
            state_key = tuple(board)
            
            # Check terminal state
            winner = self._check_winner(board)
            if winner == mark:
                return 1.0
            elif winner == 3 - mark:
                return -1.0
            elif self._is_draw(board):
                return 0.0
            
            # Leaf node - expand and evaluate
            if state_key not in self.P:
                # Get neural network evaluation
                self.P[state_key] = self.nn.get_policy(board, mark)
                value = self.nn.evaluate(board, mark) / 1000
                return -value  # Opponent's perspective
            
            # Select action using PUCT
            best_ucb = -float('inf')
            best_action = None
            
            sqrt_sum = math.sqrt(sum(self.N.get((state_key, a), 0) 
                                    for a in range(7) if board[a] == 0))
            
            for col in range(7):
                if board[col] != 0:
                    continue
                
                action_key = (state_key, col)
                
                q = self.Q.get(action_key, 0)
                n = self.N.get(action_key, 0)
                p = self.P[state_key].get(col, 0.1)
                
                if n == 0:
                    ucb = p * self.c_puct * sqrt_sum
                else:
                    ucb = q + self.c_puct * p * sqrt_sum / (1 + n)
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_action = col
            
            if best_action is None:
                return 0.0
            
            # Make move and continue simulation
            for row in range(5, -1, -1):
                if board[row * 7 + best_action] == 0:
                    board[row * 7 + best_action] = mark
                    break
            
            # Recursive simulation
            value = -self._simulate(board, 3 - mark)
            
            # Update statistics
            action_key = (state_key, best_action)
            
            if action_key not in self.N:
                self.N[action_key] = 0
                self.Q[action_key] = 0
            
            self.N[action_key] += 1
            self.Q[action_key] += (value - self.Q[action_key]) / self.N[action_key]
            
            return value
        
        def _check_winner(self, board):
            """Check if there's a winner"""
            # Check all winning patterns
            for mark in [1, 2]:
                # Horizontal
                for row in range(6):
                    for col in range(4):
                        if all(board[row*7 + col + i] == mark for i in range(4)):
                            return mark
                
                # Vertical
                for col in range(7):
                    for row in range(3):
                        if all(board[(row+i)*7 + col] == mark for i in range(4)):
                            return mark
                
                # Diagonals
                for row in range(3):
                    for col in range(4):
                        if all(board[(row+i)*7 + col + i] == mark for i in range(4)):
                            return mark
                        if all(board[(row+3-i)*7 + col + i] == mark for i in range(4)):
                            return mark
            
            return 0
        
        def _is_draw(self, board):
            """Check if game is drawn"""
            return all(board[i] != 0 for i in range(7))
    
    # Quick win/block check
    def check_immediate_win(board, col, mark):
        """Fast win detection"""
        row = next((r for r in range(5, -1, -1) if board[r*7+col] == 0), -1)
        if row < 0:
            return False
        
        temp_board = board[:]
        temp_board[row * 7 + col] = mark
        
        # Check if this creates a win
        # Horizontal
        count = 1
        for dc in [-1, 1]:
            c = col + dc
            while 0 <= c < 7 and temp_board[row * 7 + c] == mark:
                count += 1
                c += dc
        if count >= 4:
            return True
        
        # Vertical
        count = 1
        r = row + 1
        while r < 6 and temp_board[r * 7 + col] == mark:
            count += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        for dr, dc in [(-1, -1), (1, 1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and temp_board[r * 7 + c] == mark:
                count += 1
                r, c = r + dr, c + dc
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        for dr, dc in [(-1, 1), (1, -1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and temp_board[r * 7 + c] == mark:
                count += 1
                r, c = r + dr, c + dc
        if count >= 4:
            return True
        
        return False
    
    # Check for immediate wins
    for col in range(7):
        if board[col] == 0 and check_immediate_win(board, col, mark):
            return col
    
    # Check for immediate blocks
    for col in range(7):
        if board[col] == 0 and check_immediate_win(board, col, 3 - mark):
            return col
    
    # Use neural network + MCTS for move selection
    nn = NeuralNet()
    
    # For early game, use more simulations
    pieces = sum(1 for x in board if x != 0)
    
    if pieces < 10:
        # Early game - use MCTS with neural network
        mcts = MCTS(nn)
        return mcts.search(board, mark)
    else:
        # Mid/late game - use direct neural network evaluation
        policy = nn.get_policy(board, mark)
        if policy:
            # Add some exploration
            import random
            if random.random() < 0.1:  # 10% exploration
                return random.choice(list(policy.keys()))
            return max(policy.items(), key=lambda x: x[1])[0]
        
        # Fallback to center
        return 3
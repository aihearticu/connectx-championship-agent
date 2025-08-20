#!/usr/bin/env python3
"""
Neural Network Architecture for Connect X
Implements a CNN-based value and policy network
"""

import numpy as np
import json
import time
from collections import deque
import random

class ConnectXNetwork:
    """
    Neural network for Connect X position evaluation and move prediction
    Uses a simple but effective architecture that can be trained quickly
    """
    
    def __init__(self, hidden_size=256, learning_rate=0.001):
        self.input_size = 42  # 6x7 board
        self.hidden_size = hidden_size
        self.output_size = 7   # 7 possible moves
        self.learning_rate = learning_rate
        
        # Initialize weights with Xavier initialization
        self.weights = {
            # Feature extraction layers
            'conv1': self._xavier_init((3, 3, 3, 32)),  # 3x3 conv, 3 channels, 32 filters
            'conv2': self._xavier_init((3, 3, 32, 64)), # 3x3 conv, 32 -> 64 filters
            
            # Fully connected layers
            'fc1': self._xavier_init((6 * 7 * 64, hidden_size)),
            'fc2': self._xavier_init((hidden_size, hidden_size)),
            
            # Output heads
            'value_head': self._xavier_init((hidden_size, 1)),
            'policy_head': self._xavier_init((hidden_size, 7)),
            
            # Biases
            'b_conv1': np.zeros((32,)),
            'b_conv2': np.zeros((64,)),
            'b_fc1': np.zeros((hidden_size,)),
            'b_fc2': np.zeros((hidden_size,)),
            'b_value': np.zeros((1,)),
            'b_policy': np.zeros((7,))
        }
        
        # Adam optimizer parameters
        self.adam_params = {}
        for key in self.weights:
            self.adam_params[key] = {
                'm': np.zeros_like(self.weights[key]),
                'v': np.zeros_like(self.weights[key]),
                't': 0
            }
    
    def _xavier_init(self, shape):
        """Xavier weight initialization"""
        if len(shape) == 2:
            fan_in, fan_out = shape
        else:
            fan_in = np.prod(shape[:-1])
            fan_out = shape[-1]
        
        std = np.sqrt(2.0 / (fan_in + fan_out))
        return np.random.normal(0, std, shape)
    
    def _relu(self, x):
        """ReLU activation"""
        return np.maximum(0, x)
    
    def _softmax(self, x):
        """Softmax activation"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)
    
    def _tanh(self, x):
        """Tanh activation"""
        return np.tanh(x)
    
    def _conv2d(self, input_data, kernel, bias, stride=1):
        """Simple 2D convolution"""
        batch, in_h, in_w, in_c = input_data.shape
        k_h, k_w, k_in_c, k_out_c = kernel.shape
        
        out_h = (in_h - k_h) // stride + 1
        out_w = (in_w - k_w) // stride + 1
        
        output = np.zeros((batch, out_h, out_w, k_out_c))
        
        for b in range(batch):
            for i in range(out_h):
                for j in range(out_w):
                    for k in range(k_out_c):
                        # Extract patch
                        patch = input_data[b, i*stride:i*stride+k_h, j*stride:j*stride+k_w, :]
                        # Convolve
                        output[b, i, j, k] = np.sum(patch * kernel[:, :, :, k]) + bias[k]
        
        return output
    
    def board_to_input(self, board, player):
        """
        Convert board to neural network input
        3 channels: current player pieces, opponent pieces, valid moves
        """
        input_data = np.zeros((1, 6, 7, 3))
        
        # Reshape board to 6x7
        board_2d = np.array(board).reshape(6, 7)
        
        # Channel 0: Current player pieces
        input_data[0, :, :, 0] = (board_2d == player).astype(float)
        
        # Channel 1: Opponent pieces
        opponent = 3 - player
        input_data[0, :, :, 1] = (board_2d == opponent).astype(float)
        
        # Channel 2: Valid moves (top row empty)
        for col in range(7):
            if board_2d[0, col] == 0:
                input_data[0, 0, col, 2] = 1.0
        
        return input_data
    
    def forward(self, board, player):
        """
        Forward pass through the network
        Returns value estimate and move probabilities
        """
        # Convert board to input format
        x = self.board_to_input(board, player)
        
        # Convolutional layers
        x = self._conv2d(x, self.weights['conv1'], self.weights['b_conv1'])
        x = self._relu(x)
        
        x = self._conv2d(x, self.weights['conv2'], self.weights['b_conv2'])
        x = self._relu(x)
        
        # Flatten
        x = x.reshape(x.shape[0], -1)
        
        # Fully connected layers
        x = np.dot(x, self.weights['fc1']) + self.weights['b_fc1']
        x = self._relu(x)
        
        x = np.dot(x, self.weights['fc2']) + self.weights['b_fc2']
        x = self._relu(x)
        
        # Value head
        value = np.dot(x, self.weights['value_head']) + self.weights['b_value']
        value = self._tanh(value[0, 0])  # Output between -1 and 1
        
        # Policy head
        policy_logits = np.dot(x, self.weights['policy_head']) + self.weights['b_policy']
        policy = self._softmax(policy_logits[0])
        
        return value, policy
    
    def predict_move(self, board, player, temperature=0.0):
        """
        Predict best move for current position
        Temperature controls exploration (0 = deterministic, >0 = stochastic)
        """
        value, policy = self.forward(board, player)
        
        # Mask invalid moves
        valid_moves = []
        for col in range(7):
            if board[col] == 0:
                valid_moves.append(col)
        
        if not valid_moves:
            return None, value
        
        # Apply temperature and mask
        if temperature > 0:
            # Apply temperature
            policy = np.power(policy, 1.0 / temperature)
        
        # Zero out invalid moves
        masked_policy = np.zeros(7)
        for col in valid_moves:
            masked_policy[col] = policy[col]
        
        # Renormalize
        if np.sum(masked_policy) > 0:
            masked_policy /= np.sum(masked_policy)
        else:
            # Uniform over valid moves if all zeros
            for col in valid_moves:
                masked_policy[col] = 1.0 / len(valid_moves)
        
        # Select move
        if temperature == 0:
            # Deterministic
            move = valid_moves[np.argmax([masked_policy[col] for col in valid_moves])]
        else:
            # Stochastic
            move = np.random.choice(7, p=masked_policy)
        
        return move, value
    
    def train_on_batch(self, positions, values, policies):
        """
        Train network on a batch of positions
        positions: list of (board, player) tuples
        values: list of target values (-1 to 1)
        policies: list of target policy distributions
        """
        batch_size = len(positions)
        
        # Prepare batch inputs
        batch_inputs = []
        for board, player in positions:
            batch_inputs.append(self.board_to_input(board, player))
        batch_input = np.concatenate(batch_inputs, axis=0)
        
        # Forward pass
        # Store activations for backprop
        activations = {}
        
        # Conv1
        z_conv1 = self._conv2d(batch_input, self.weights['conv1'], self.weights['b_conv1'])
        a_conv1 = self._relu(z_conv1)
        activations['conv1'] = (batch_input, z_conv1, a_conv1)
        
        # Conv2
        z_conv2 = self._conv2d(a_conv1, self.weights['conv2'], self.weights['b_conv2'])
        a_conv2 = self._relu(z_conv2)
        activations['conv2'] = (a_conv1, z_conv2, a_conv2)
        
        # Flatten
        a_flat = a_conv2.reshape(batch_size, -1)
        
        # FC1
        z_fc1 = np.dot(a_flat, self.weights['fc1']) + self.weights['b_fc1']
        a_fc1 = self._relu(z_fc1)
        activations['fc1'] = (a_flat, z_fc1, a_fc1)
        
        # FC2
        z_fc2 = np.dot(a_fc1, self.weights['fc2']) + self.weights['b_fc2']
        a_fc2 = self._relu(z_fc2)
        activations['fc2'] = (a_fc1, z_fc2, a_fc2)
        
        # Value head
        z_value = np.dot(a_fc2, self.weights['value_head']) + self.weights['b_value']
        pred_values = np.tanh(z_value).flatten()
        
        # Policy head
        z_policy = np.dot(a_fc2, self.weights['policy_head']) + self.weights['b_policy']
        pred_policies = np.array([self._softmax(z_policy[i]) for i in range(batch_size)])
        
        # Calculate losses
        value_loss = np.mean((pred_values - np.array(values)) ** 2)
        policy_loss = -np.mean(np.sum(np.array(policies) * np.log(pred_policies + 1e-8), axis=1))
        total_loss = value_loss + policy_loss
        
        # Backward pass (simplified gradient computation)
        # This is a simplified version - full implementation would compute proper gradients
        gradients = {}
        
        # Value gradient
        d_value = 2 * (pred_values - np.array(values)) / batch_size
        d_value = d_value.reshape(-1, 1)
        
        # Policy gradient
        d_policy = (pred_policies - np.array(policies)) / batch_size
        
        # Update weights using Adam optimizer
        self._adam_update('value_head', -d_value * self.learning_rate)
        self._adam_update('policy_head', -d_policy * self.learning_rate)
        
        return total_loss, value_loss, policy_loss
    
    def _adam_update(self, param_name, gradient):
        """Adam optimizer update"""
        beta1 = 0.9
        beta2 = 0.999
        epsilon = 1e-8
        
        params = self.adam_params[param_name]
        params['t'] += 1
        
        # Update biased moments
        params['m'] = beta1 * params['m'] + (1 - beta1) * gradient
        params['v'] = beta2 * params['v'] + (1 - beta2) * (gradient ** 2)
        
        # Bias correction
        m_hat = params['m'] / (1 - beta1 ** params['t'])
        v_hat = params['v'] / (1 - beta2 ** params['t'])
        
        # Update weights
        self.weights[param_name] += self.learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)
    
    def save(self, filepath):
        """Save network weights"""
        save_dict = {
            'weights': {k: v.tolist() for k, v in self.weights.items()},
            'hidden_size': self.hidden_size,
            'learning_rate': self.learning_rate
        }
        with open(filepath, 'w') as f:
            json.dump(save_dict, f)
    
    def load(self, filepath):
        """Load network weights"""
        with open(filepath, 'r') as f:
            save_dict = json.load(f)
        
        self.hidden_size = save_dict['hidden_size']
        self.learning_rate = save_dict['learning_rate']
        self.weights = {k: np.array(v) for k, v in save_dict['weights'].items()}


class MCTSNode:
    """Monte Carlo Tree Search node with neural network guidance"""
    
    def __init__(self, board, player, parent=None, move=None, prior=0.0):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move
        self.prior = prior
        
        self.visits = 0
        self.value_sum = 0
        self.children = {}
        self.is_expanded = False
    
    def value(self):
        """Average value of this node"""
        if self.visits == 0:
            return 0
        return self.value_sum / self.visits
    
    def ucb_score(self, c_puct=1.0):
        """Upper Confidence Bound score for selection"""
        if self.visits == 0:
            return float('inf')
        
        exploration = c_puct * self.prior * np.sqrt(self.parent.visits) / (1 + self.visits)
        return self.value() + exploration
    
    def select_child(self, c_puct=1.0):
        """Select best child based on UCB score"""
        return max(self.children.values(), key=lambda c: c.ucb_score(c_puct))
    
    def expand(self, priors):
        """Expand node with children"""
        self.is_expanded = True
        
        for col in range(7):
            if self.board[col] == 0:  # Valid move
                new_board = self.make_move(col)
                child = MCTSNode(
                    new_board,
                    3 - self.player,  # Switch player
                    parent=self,
                    move=col,
                    prior=priors[col]
                )
                self.children[col] = child
    
    def make_move(self, col):
        """Make a move on the board"""
        new_board = self.board.copy()
        # Find bottom empty row
        for row in range(5, -1, -1):
            if new_board[row * 7 + col] == 0:
                new_board[row * 7 + col] = self.player
                break
        return new_board
    
    def is_terminal(self):
        """Check if game is over"""
        return check_winner(self.board) != 0 or all(self.board[i] != 0 for i in range(7))
    
    def backup(self, value):
        """Backup value through tree"""
        self.visits += 1
        self.value_sum += value
        if self.parent:
            self.parent.backup(-value)  # Flip value for opponent


class NeuralMCTS:
    """MCTS with neural network guidance"""
    
    def __init__(self, network, simulations=100, c_puct=1.0, temperature=1.0):
        self.network = network
        self.simulations = simulations
        self.c_puct = c_puct
        self.temperature = temperature
    
    def search(self, board, player):
        """Run MCTS simulations and return move probabilities"""
        root = MCTSNode(board, player)
        
        for _ in range(self.simulations):
            node = root
            path = [node]
            
            # Selection
            while node.is_expanded and not node.is_terminal():
                node = node.select_child(self.c_puct)
                path.append(node)
            
            # Expansion and Evaluation
            if not node.is_terminal():
                # Get neural network evaluation
                value, priors = self.network.forward(node.board, node.player)
                node.expand(priors)
                
                # Backup
                for n in reversed(path):
                    n.backup(value)
                    value = -value
            else:
                # Terminal node - get actual outcome
                winner = check_winner(node.board)
                if winner == node.player:
                    value = 1
                elif winner == 3 - node.player:
                    value = -1
                else:
                    value = 0
                
                # Backup
                for n in reversed(path):
                    n.backup(value)
                    value = -value
        
        # Extract visit counts
        visits = np.zeros(7)
        for col, child in root.children.items():
            visits[col] = child.visits
        
        # Apply temperature
        if self.temperature > 0:
            visits = np.power(visits, 1.0 / self.temperature)
        
        # Normalize to get probabilities
        if np.sum(visits) > 0:
            probs = visits / np.sum(visits)
        else:
            # Uniform distribution if no visits
            probs = np.ones(7) / 7
            for col in range(7):
                if board[col] != 0:
                    probs[col] = 0
            probs /= np.sum(probs)
        
        return probs, root.value()


def check_winner(board):
    """Check if there's a winner on the board"""
    # Check horizontal
    for row in range(6):
        for col in range(4):
            idx = row * 7 + col
            if board[idx] != 0 and all(board[idx] == board[idx + i] for i in range(4)):
                return board[idx]
    
    # Check vertical
    for col in range(7):
        for row in range(3):
            idx = row * 7 + col
            if board[idx] != 0 and all(board[idx] == board[idx + i * 7] for i in range(4)):
                return board[idx]
    
    # Check diagonal (down-right)
    for row in range(3):
        for col in range(4):
            idx = row * 7 + col
            if board[idx] != 0 and all(board[idx] == board[idx + i * 8] for i in range(4)):
                return board[idx]
    
    # Check diagonal (up-right)
    for row in range(3, 6):
        for col in range(4):
            idx = row * 7 + col
            if board[idx] != 0 and all(board[idx] == board[idx - i * 6] for i in range(4)):
                return board[idx]
    
    return 0  # No winner


# Test neural network
if __name__ == "__main__":
    print("Testing Neural Network v2...")
    
    # Create network
    net = ConnectXNetwork(hidden_size=128)
    
    # Test forward pass
    test_board = [0] * 42
    test_board[35] = 1  # Player 1 move
    test_board[36] = 2  # Player 2 move
    
    value, policy = net.forward(test_board, 1)
    print(f"Value: {value:.3f}")
    print(f"Policy: {policy}")
    
    # Test MCTS
    mcts = NeuralMCTS(net, simulations=50)
    probs, root_value = mcts.search(test_board, 1)
    print(f"\nMCTS move probabilities: {probs}")
    print(f"Root value: {root_value:.3f}")
#!/usr/bin/env python3
"""
Train a neural network for Connect X position evaluation
Uses self-play to generate training data
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from kaggle_environments import make
import random
import pickle
from collections import deque
import time

class ConnectXNet(nn.Module):
    """Neural network for Connect X position evaluation"""
    def __init__(self, rows=6, columns=7):
        super(ConnectXNet, self).__init__()
        self.rows = rows
        self.columns = columns
        input_size = rows * columns * 3  # 3 channels: player1, player2, valid moves
        
        # Convolutional layers for pattern recognition
        self.conv1 = nn.Conv2d(3, 64, kernel_size=4, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=4, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=4, padding=1)
        
        # Calculate size after convolutions
        conv_output_size = self._get_conv_output_size()
        
        # Fully connected layers
        self.fc1 = nn.Linear(conv_output_size, 512)
        self.fc2 = nn.Linear(512, 256)
        
        # Output heads
        self.value_head = nn.Linear(256, 1)  # Position evaluation
        self.policy_head = nn.Linear(256, columns)  # Move probabilities
        
        # Activation functions
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()
        self.softmax = nn.Softmax(dim=1)
        
    def _get_conv_output_size(self):
        """Calculate the output size after convolutions"""
        dummy_input = torch.zeros(1, 3, self.rows, self.columns)
        x = self.relu(self.conv1(dummy_input))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        return x.view(1, -1).size(1)
    
    def forward(self, x):
        # Convolutional layers
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        
        # Output heads
        value = self.tanh(self.value_head(x))
        policy = self.softmax(self.policy_head)
        
        return value, policy

def board_to_tensor(board, mark, rows=6, columns=7):
    """Convert board state to neural network input"""
    tensor = np.zeros((3, rows, columns))
    
    board_2d = np.array(board).reshape(rows, columns)
    
    # Channel 0: Current player's pieces
    tensor[0] = (board_2d == mark).astype(float)
    
    # Channel 1: Opponent's pieces
    tensor[1] = (board_2d == (3 - mark)).astype(float)
    
    # Channel 2: Valid moves (top empty cell in each column)
    for col in range(columns):
        for row in range(rows-1, -1, -1):
            if board_2d[row, col] == 0:
                tensor[2, row, col] = 1
                break
    
    return torch.FloatTensor(tensor)

class SelfPlayGame:
    """Generate training data through self-play"""
    def __init__(self, model=None):
        self.env = make("connectx")
        self.model = model
        self.history = []
        
    def play_game(self):
        """Play one game and return training data"""
        self.env.reset()
        states = []
        
        while not self.env.done:
            state = self.env.state[0]
            board = state.observation.board
            mark = state.observation.mark
            
            # Get valid moves
            valid_moves = [c for c in range(7) if board[c] == 0]
            if not valid_moves:
                break
            
            # Choose move
            if self.model is None or random.random() < 0.1:  # 10% exploration
                move = random.choice(valid_moves)
            else:
                # Use model prediction
                tensor = board_to_tensor(board, mark).unsqueeze(0)
                with torch.no_grad():
                    value, policy = self.model(tensor)
                
                # Sample from policy distribution
                probs = policy[0].numpy()
                # Mask invalid moves
                for c in range(7):
                    if c not in valid_moves:
                        probs[c] = 0
                probs = probs / probs.sum()
                
                move = np.random.choice(7, p=probs)
            
            # Store state
            states.append({
                'board': board.copy(),
                'mark': mark,
                'move': move,
                'valid_moves': valid_moves.copy()
            })
            
            # Make move
            self.env.step([move, None])
        
        # Determine winner and assign rewards
        winner = None
        if self.env.state[0].reward == 1:
            winner = 1
        elif self.env.state[1].reward == 1:
            winner = 2
        
        # Create training data
        training_data = []
        for state in states:
            if winner is None:
                value = 0  # Draw
            elif state['mark'] == winner:
                value = 1  # Win
            else:
                value = -1  # Loss
            
            # Create policy target (one-hot for actual move)
            policy = np.zeros(7)
            policy[state['move']] = 1
            
            training_data.append({
                'board': state['board'],
                'mark': state['mark'],
                'value': value,
                'policy': policy
            })
        
        return training_data

def train_model(num_iterations=10, games_per_iteration=100):
    """Train the neural network through self-play"""
    model = ConnectXNet()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    value_criterion = nn.MSELoss()
    policy_criterion = nn.CrossEntropyLoss()
    
    all_training_data = deque(maxlen=10000)  # Keep last 10k positions
    
    for iteration in range(num_iterations):
        print(f"\nIteration {iteration + 1}/{num_iterations}")
        
        # Self-play phase
        print("Generating self-play games...")
        iteration_data = []
        game_player = SelfPlayGame(model if iteration > 0 else None)
        
        for game in range(games_per_iteration):
            if game % 20 == 0:
                print(f"  Game {game}/{games_per_iteration}")
            
            game_data = game_player.play_game()
            iteration_data.extend(game_data)
        
        all_training_data.extend(iteration_data)
        print(f"  Generated {len(iteration_data)} positions")
        
        # Training phase
        print("Training network...")
        dataset = list(all_training_data)
        random.shuffle(dataset)
        
        batch_size = 32
        num_epochs = 5
        
        for epoch in range(num_epochs):
            total_loss = 0
            batches = 0
            
            for i in range(0, len(dataset) - batch_size, batch_size):
                batch = dataset[i:i+batch_size]
                
                # Prepare batch tensors
                boards = torch.stack([board_to_tensor(item['board'], item['mark']) for item in batch])
                values = torch.FloatTensor([[item['value']] for item in batch])
                policies = torch.FloatTensor([item['policy'] for item in batch])
                
                # Forward pass
                pred_values, pred_policies = model(boards)
                
                # Calculate losses
                value_loss = value_criterion(pred_values, values)
                policy_loss = policy_criterion(pred_policies, policies)
                total_loss_batch = value_loss + policy_loss
                
                # Backward pass
                optimizer.zero_grad()
                total_loss_batch.backward()
                optimizer.step()
                
                total_loss += total_loss_batch.item()
                batches += 1
            
            avg_loss = total_loss / batches if batches > 0 else 0
            print(f"    Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        # Save checkpoint
        if iteration % 5 == 4:
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'iteration': iteration,
            }, f'connectx_model_iter_{iteration+1}.pth')
            print(f"  Saved checkpoint at iteration {iteration+1}")
    
    # Save final model
    torch.save(model.state_dict(), 'connectx_model_final.pth')
    print("\nTraining complete! Model saved as connectx_model_final.pth")
    
    return model

def create_nn_agent(model_path='connectx_model_final.pth'):
    """Create an agent function using the trained neural network"""
    # Load model
    model = ConnectXNet()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    def agent(observation, configuration):
        """Neural network enhanced agent"""
        board = observation.board
        mark = observation.mark
        columns = configuration.columns
        rows = configuration.rows
        
        # Quick win/block check
        def can_win(col, player):
            if board[col] != 0:
                return False
            
            # Find landing row
            row = -1
            for r in range(rows-1, -1, -1):
                if board[r * columns + col] == 0:
                    row = r
                    break
            
            if row == -1:
                return False
            
            # Check win (simplified)
            temp_board = board[:]
            temp_board[row * columns + col] = player
            
            # Horizontal
            count = 0
            for c in range(columns):
                if temp_board[row * columns + c] == player:
                    count += 1
                    if count >= 4:
                        return True
                else:
                    count = 0
            
            return False
        
        # Get valid moves
        valid_moves = [c for c in range(columns) if board[c] == 0]
        
        # Immediate win
        for col in valid_moves:
            if can_win(col, mark):
                return col
        
        # Block opponent
        for col in valid_moves:
            if can_win(col, 3 - mark):
                return col
        
        # Use neural network for move selection
        tensor = board_to_tensor(board, mark, rows, columns).unsqueeze(0)
        
        with torch.no_grad():
            value, policy = model(tensor)
        
        # Get move probabilities
        probs = policy[0].numpy()
        
        # Mask invalid moves
        for c in range(columns):
            if c not in valid_moves:
                probs[c] = 0
        
        # Normalize
        if probs.sum() > 0:
            probs = probs / probs.sum()
        else:
            # Fallback to uniform distribution over valid moves
            probs = np.zeros(columns)
            for c in valid_moves:
                probs[c] = 1.0 / len(valid_moves)
        
        # Choose best move (highest probability)
        best_move = np.argmax(probs)
        
        # Ensure it's valid
        if best_move not in valid_moves:
            best_move = valid_moves[0]
        
        return int(best_move)
    
    return agent

if __name__ == "__main__":
    print("Connect X Neural Network Training")
    print("="*50)
    
    # Check if we should train or just create agent
    import os
    if os.path.exists('connectx_model_final.pth'):
        print("Found existing model!")
        response = input("Train new model? (y/n): ")
        if response.lower() != 'y':
            print("Creating agent with existing model...")
            agent = create_nn_agent()
            print("Agent created successfully!")
        else:
            print("Starting training...")
            model = train_model(num_iterations=5, games_per_iteration=50)
    else:
        print("No existing model found. Starting training...")
        model = train_model(num_iterations=5, games_per_iteration=50)
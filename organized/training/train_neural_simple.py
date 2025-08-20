"""
Simple Neural Network Training
Trains on available self-play data
"""

import numpy as np
import pickle
import json
import glob
import time

class SimpleNN:
    """Simple 2-layer neural network"""
    
    def __init__(self):
        # Small network for speed
        self.w1 = np.random.randn(42, 128) * 0.1
        self.b1 = np.zeros((1, 128))
        self.w2 = np.random.randn(128, 1) * 0.1
        self.b2 = np.zeros((1, 1))
    
    def forward(self, X):
        """Forward pass"""
        self.z1 = np.dot(X, self.w1) + self.b1
        self.a1 = np.maximum(0, self.z1)  # ReLU
        self.z2 = np.dot(self.a1, self.w2) + self.b2
        return np.tanh(self.z2)
    
    def train_batch(self, X, y, lr=0.001):
        """Train on batch"""
        # Forward
        output = self.forward(X)
        
        # Backward
        m = X.shape[0]
        dz2 = (output - y) * (1 - output**2)
        dw2 = np.dot(self.a1.T, dz2) / m
        db2 = np.sum(dz2, axis=0, keepdims=True) / m
        
        da1 = np.dot(dz2, self.w2.T)
        dz1 = da1 * (self.z1 > 0)
        dw1 = np.dot(X.T, dz1) / m
        db1 = np.sum(dz1, axis=0, keepdims=True) / m
        
        # Update
        self.w1 -= lr * dw1
        self.b1 -= lr * db1
        self.w2 -= lr * dw2
        self.b2 -= lr * db2
        
        return np.mean((output - y)**2)

def prepare_data(games, max_positions=10000):
    """Prepare training data from games"""
    X, y = [], []
    
    for game in games[:min(len(games), 1000)]:  # Limit games
        moves = game['moves']
        winner = game['winner']
        
        board = [0] * 42
        
        for i, move in enumerate(moves):
            if len(X) >= max_positions:
                break
            
            player = 1 if i % 2 == 0 else 2
            
            # Make move
            for row in range(5, -1, -1):
                if board[row * 7 + move] == 0:
                    board[row * 7 + move] = player
                    break
            
            # Create features
            features = np.array(board, dtype=np.float32)
            features = np.where(features == 1, 1, np.where(features == 2, -1, 0))
            
            # Create target
            if winner == 0:
                target = 0
            elif winner == player:
                target = 0.5 + (i / len(moves)) * 0.5
            else:
                target = -0.5 - (i / len(moves)) * 0.5
            
            X.append(features)
            y.append([target])
    
    return np.array(X), np.array(y)

def main():
    print("="*60)
    print("NEURAL NETWORK TRAINING")
    print("="*60)
    
    # Try to load games
    game_files = glob.glob('self_play_games_*.pkl')
    
    if not game_files:
        print("No game files found. Creating sample data...")
        # Create sample games
        games = []
        for i in range(100):
            moves = [3, 3, 2, 4, 4, 2, 1, 5] + [i % 7 for _ in range(10)]
            winner = 1 if i % 3 == 0 else 2 if i % 3 == 1 else 0
            games.append({'moves': moves[:10], 'winner': winner})
    else:
        latest_file = sorted(game_files)[-1]
        print(f"Loading {latest_file}...")
        try:
            with open(latest_file, 'rb') as f:
                games = pickle.load(f)
            print(f"Loaded {len(games)} games")
        except:
            print("Error loading games, using sample data")
            games = []
            for i in range(100):
                moves = [3, 3, 2, 4, 4, 2, 1, 5] + [i % 7 for _ in range(10)]
                winner = 1 if i % 3 == 0 else 2 if i % 3 == 1 else 0
                games.append({'moves': moves[:10], 'winner': winner})
    
    # Prepare data
    print("\nPreparing training data...")
    X, y = prepare_data(games, max_positions=5000)
    print(f"Training on {len(X)} positions")
    
    # Create and train network
    nn = SimpleNN()
    
    print("\nTraining...")
    batch_size = 32
    epochs = 20
    
    for epoch in range(epochs):
        # Shuffle data
        indices = np.random.permutation(len(X))
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        total_loss = 0
        batches = 0
        
        for i in range(0, len(X), batch_size):
            X_batch = X_shuffled[i:i+batch_size]
            y_batch = y_shuffled[i:i+batch_size]
            
            loss = nn.train_batch(X_batch, y_batch)
            total_loss += loss
            batches += 1
        
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/batches:.6f}")
    
    # Save model
    model_data = {
        'w1': nn.w1,
        'b1': nn.b1,
        'w2': nn.w2,
        'b2': nn.b2
    }
    
    with open('simple_nn_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("\nModel saved to simple_nn_model.pkl")
    print("="*60)

if __name__ == "__main__":
    main()

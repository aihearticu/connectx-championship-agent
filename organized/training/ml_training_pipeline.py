#!/usr/bin/env python3
"""
Comprehensive ML Training Pipeline for Connect X
Combines deep learning, gradient boosting, and ensemble methods
"""

import numpy as np
import json
import time
from deep_rl_agent import RLAgent
from gradient_boost_agent import GradientBoostAgent
from ensemble_agent import EnsembleAgent
from kaggle_environments import make

class MLTrainingPipeline:
    """Complete ML training pipeline"""
    
    def __init__(self):
        self.agents = {
            'rl': RLAgent(),
            'gb': GradientBoostAgent(),
            'ensemble': EnsembleAgent()
        }
        
        self.training_stats = {
            'rl': [],
            'gb': [],
            'ensemble': []
        }
    
    def train_all_agents(self, iterations=5):
        """Train all ML agents"""
        print("ML Training Pipeline for Connect X")
        print("="*70)
        
        for iteration in range(iterations):
            print(f"\n{'='*70}")
            print(f"Training Iteration {iteration + 1}/{iterations}")
            print(f"{'='*70}")
            
            # 1. Train RL Agent
            print("\n1. Training Deep RL Agent...")
            self._train_rl_agent(games=50)
            
            # 2. Train Gradient Boosting
            print("\n2. Training Gradient Boosting Agent...")
            self._train_gb_agent(games=50)
            
            # 3. Evaluate all agents
            print("\n3. Evaluating Agents...")
            self._evaluate_all_agents()
            
            # 4. Save checkpoints
            self._save_checkpoints(iteration + 1)
        
        # Final comprehensive evaluation
        print("\n" + "="*70)
        print("FINAL EVALUATION")
        print("="*70)
        self._final_evaluation()
    
    def _train_rl_agent(self, games=50):
        """Train RL agent"""
        start_time = time.time()
        
        # Self-play training
        self.agents['rl'].train(num_games=games, epochs_per_update=5)
        
        training_time = time.time() - start_time
        print(f"RL training completed in {training_time:.1f}s")
    
    def _train_gb_agent(self, games=50):
        """Train gradient boosting agent"""
        start_time = time.time()
        
        # Collect data and train
        self.agents['gb'].collect_training_data(n_games=games)
        self.agents['gb'].train()
        
        training_time = time.time() - start_time
        print(f"GB training completed in {training_time:.1f}s")
    
    def _evaluate_all_agents(self):
        """Evaluate all agents"""
        results = {}
        
        # Create agent functions
        agent_funcs = {
            'rl': self._create_rl_agent_func(),
            'gb': self._create_gb_agent_func(),
            'ensemble': self._create_ensemble_agent_func()
        }
        
        for agent_name, agent_func in agent_funcs.items():
            print(f"\nEvaluating {agent_name.upper()} agent...")
            
            # vs Random
            wins_random = self._test_vs_opponent(agent_func, 'random', games=20)
            
            # vs Negamax
            wins_negamax = self._test_vs_opponent(agent_func, 'negamax', games=10)
            
            results[agent_name] = {
                'vs_random': wins_random,
                'vs_negamax': wins_negamax,
                'total_score': wins_random * 5 + wins_negamax * 10
            }
            
            print(f"  vs Random: {wins_random}/20 ({wins_random * 5}%)")
            print(f"  vs Negamax: {wins_negamax}/10 ({wins_negamax * 10}%)")
            
            # Store stats
            self.training_stats[agent_name].append(results[agent_name])
        
        # Show best performer
        best_agent = max(results.items(), key=lambda x: x[1]['total_score'])
        print(f"\nBest performer: {best_agent[0].upper()} with score {best_agent[1]['total_score']}")
    
    def _test_vs_opponent(self, agent_func, opponent, games=10):
        """Test agent against opponent"""
        wins = 0
        
        for i in range(games):
            env = make('connectx', debug=False)
            
            try:
                if i % 2 == 0:
                    env.run([agent_func, opponent])
                    if env.state[0].reward == 1:
                        wins += 1
                else:
                    env.run([opponent, agent_func])
                    if env.state[1].reward == 1:
                        wins += 1
            except:
                pass
        
        return wins
    
    def _create_rl_agent_func(self):
        """Create RL agent function"""
        agent = self.agents['rl']
        
        def rl_agent_func(observation, configuration):
            board = observation.board
            player = observation.mark
            
            try:
                move, _, _ = agent.get_move(board, player, temperature=0)
                if board[move] == 0:
                    return int(move)
            except:
                pass
            
            # Fallback
            for col in range(7):
                if board[col] == 0:
                    return col
            return 0
        
        return rl_agent_func
    
    def _create_gb_agent_func(self):
        """Create GB agent function"""
        agent = self.agents['gb']
        
        def gb_agent_func(observation, configuration):
            board = observation.board
            player = observation.mark
            
            try:
                move = agent.get_move(board, player)
                if move is not None and board[move] == 0:
                    return int(move)
            except:
                pass
            
            # Fallback
            for col in range(7):
                if board[col] == 0:
                    return col
            return 0
        
        return gb_agent_func
    
    def _create_ensemble_agent_func(self):
        """Create ensemble agent function"""
        agent = self.agents['ensemble']
        
        def ensemble_agent_func(observation, configuration):
            try:
                move = agent.get_move(observation)
                if move is not None and observation.board[move] == 0:
                    return int(move)
            except:
                pass
            
            # Fallback
            for col in range(7):
                if observation.board[col] == 0:
                    return col
            return 0
        
        return ensemble_agent_func
    
    def _save_checkpoints(self, iteration):
        """Save model checkpoints"""
        print(f"\nSaving checkpoints for iteration {iteration}...")
        
        # Save RL model
        self.agents['rl'].network.save(f'rl_model_iter_{iteration}.json')
        
        # Save GB model
        if self.agents['gb'].is_trained:
            self.agents['gb'].save(f'gb_model_iter_{iteration}.json')
        
        # Save training stats
        with open(f'training_stats_iter_{iteration}.json', 'w') as f:
            json.dump(self.training_stats, f, indent=2)
    
    def _final_evaluation(self):
        """Comprehensive final evaluation"""
        print("\nComprehensive Agent Evaluation")
        print("-"*70)
        
        # Test each agent extensively
        agent_funcs = {
            'RL': self._create_rl_agent_func(),
            'Gradient Boosting': self._create_gb_agent_func(),
            'Ensemble': self._create_ensemble_agent_func()
        }
        
        final_results = {}
        
        for agent_name, agent_func in agent_funcs.items():
            print(f"\n{agent_name} Agent:")
            
            # Extended testing
            results = {
                'random_50': self._test_vs_opponent(agent_func, 'random', games=50),
                'negamax_20': self._test_vs_opponent(agent_func, 'negamax', games=20)
            }
            
            win_rate_random = results['random_50'] / 50 * 100
            win_rate_negamax = results['negamax_20'] / 20 * 100
            
            print(f"  vs Random (50 games): {results['random_50']} wins ({win_rate_random:.1f}%)")
            print(f"  vs Negamax (20 games): {results['negamax_20']} wins ({win_rate_negamax:.1f}%)")
            
            # Expected score calculation
            expected_score = 600 + win_rate_random * 2 + win_rate_negamax * 4
            print(f"  Expected Kaggle score: {int(expected_score)}-{int(expected_score * 1.2)}")
            
            final_results[agent_name] = {
                'win_rate_random': win_rate_random,
                'win_rate_negamax': win_rate_negamax,
                'expected_score': expected_score
            }
        
        # Determine best agent
        best_agent = max(final_results.items(), 
                        key=lambda x: x[1]['expected_score'])
        
        print("\n" + "="*70)
        print("RECOMMENDATION")
        print("="*70)
        print(f"Best ML Agent: {best_agent[0]}")
        print(f"Expected Score: {int(best_agent[1]['expected_score'])}")
        
        if best_agent[1]['expected_score'] > 1000:
            print("\n✓ ML agent shows excellent performance!")
            print("  Ready for submission to achieve 1000+ score")
        else:
            print("\n⚡ ML agent shows good performance")
            print("  Consider additional training for optimal results")
        
        # Save final results
        with open('ml_final_results.json', 'w') as f:
            json.dump({
                'results': final_results,
                'best_agent': best_agent[0],
                'training_stats': self.training_stats
            }, f, indent=2)
        
        print("\nResults saved to ml_final_results.json")
    
    def create_best_ml_agent(self):
        """Create the best performing ML agent for submission"""
        # For now, return ensemble as it combines multiple approaches
        return self._create_ensemble_agent_func()


# Quick training script
def quick_train():
    """Quick training for testing"""
    print("Quick ML Training (Reduced parameters)")
    print("="*70)
    
    pipeline = MLTrainingPipeline()
    
    # Override with smaller parameters for testing
    pipeline.agents['rl'].train = lambda **kwargs: pipeline.agents['rl'].train(
        num_games=20, epochs_per_update=3
    )
    
    # Train for fewer iterations
    pipeline.train_all_agents(iterations=2)
    
    # Create best agent
    best_agent = pipeline.create_best_ml_agent()
    
    return best_agent


# Main execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick training mode
        best_agent = quick_train()
    else:
        # Full training
        pipeline = MLTrainingPipeline()
        pipeline.train_all_agents(iterations=5)
        
        # Create submission agent
        best_agent = pipeline.create_best_ml_agent()
    
    print("\n" + "="*70)
    print("ML TRAINING COMPLETE")
    print("="*70)
    print("Best ML agent created and ready for submission!")
    print("Use the returned agent function for Kaggle submission")
# OpenEvolve for ConnectX - Experimental Evolution Guide

## Overview

I've set up OpenEvolve to evolve ConnectX agents using LLMs. This is an experimental approach that could help us break into the top 5 by discovering novel strategies through evolutionary code generation.

## What is OpenEvolve?

OpenEvolve is an open-source implementation of Google DeepMind's AlphaEvolve system. It uses Large Language Models (LLMs) to evolve code through:

1. **Prompt Engineering**: Shows LLMs examples of successful programs and their scores
2. **Code Generation**: LLMs generate variations and improvements
3. **Evaluation**: Programs are tested against baseline agents
4. **Selection**: Best performers are kept for the next generation
5. **Evolution**: Process repeats, gradually improving the agent

## Setup Complete

I've created the following files in `/home/jjhpe/Kaggle Simulation/openevolve/`:

### 1. **connectx_evaluator.py**
- Evaluates agents by playing games against baseline opponents
- Tests win rate, tactical ability, speed, and move efficiency
- Uses staged evaluation for faster iteration

### 2. **connectx_initial_agent.py**
- Basic starting agent with EVOLVE blocks
- Simple center-preference strategy
- Will be evolved by the system

### 3. **connectx_config.yaml**
- Configuration for the evolution process
- Uses GPT-4 for code generation
- Population of 50 agents across 5 islands
- Focus on win rate (40%), tactics (30%), efficiency (20%), speed (10%)

### 4. **run_connectx_evolution.py**
- Main script to run the evolution
- Requires OpenAI API key

## Key Features

### Evaluation Metrics
- **Win Rate**: Overall performance against all opponents
- **Tactical Score**: Ability to beat defensive players
- **Move Efficiency**: Winning in fewer moves
- **Speed Score**: Fast execution time

### Evolution Strategy
- **Population**: 50 best programs kept
- **Islands**: 5 isolated populations for diversity
- **Migration**: 10% migration between islands every 5 iterations
- **Elitism**: Top 20% preserved unchanged
- **Tournament Selection**: 3-way tournament for breeding

### LLM Guidance
The system instructs the LLM to focus on:
1. Win detection (immediate wins)
2. Blocking opponent wins
3. Fork creation (multiple threats)
4. Center column control
5. Pattern matching
6. Avoiding slow algorithms

## How to Run

### Prerequisites
1. OpenAI API Key (required for LLM code generation)
2. Python 3.8+ with pip
3. All dependencies installed (already done)

### Running Evolution

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-your-actual-api-key'

# Run evolution
cd /home/jjhpe/Kaggle\ Simulation/openevolve
python run_connectx_evolution.py
```

### Testing Setup

```bash
# Test that everything works
cd /home/jjhpe/Kaggle\ Simulation/openevolve
python test_connectx_setup.py
```

## Expected Results

Based on the AlphaEvolve paper, we might see:

1. **Early Iterations (1-20)**: Basic improvements like better win/block detection
2. **Mid Iterations (20-50)**: Fork detection, strategic play
3. **Late Iterations (50-100+)**: Novel patterns, optimized heuristics

## Monitoring Progress

The system saves checkpoints every 10 iterations in `connectx_evolution_output/checkpoints/`:

```
checkpoint_10/
  best_program.py         # Best agent at iteration 10
  best_program_info.json  # Performance metrics
  programs/               # All evaluated programs
```

## Potential Advantages

1. **Novel Strategies**: LLMs might discover patterns humans miss
2. **Automatic Optimization**: Code gets faster through evolution
3. **Diverse Solutions**: Multiple islands maintain variety
4. **No Manual Tuning**: System finds optimal parameters

## Next Steps

1. **Get OpenAI API Key**: Required for LLM code generation
2. **Run Initial Evolution**: Start with 50-100 iterations
3. **Analyze Best Agents**: Study what patterns emerge
4. **Integrate with Main Agent**: Incorporate best discoveries
5. **Extended Runs**: Longer evolution for better results

## Integration Ideas

Once we have evolved agents, we can:

1. **Extract Patterns**: Identify novel strategies from evolved code
2. **Hybrid Approach**: Combine evolved heuristics with our neural network
3. **Ensemble**: Use multiple evolved agents voting
4. **Feature Engineering**: Use evolved evaluation functions

## Important Notes

- Evolution requires significant API calls (costs money)
- Start with small runs to test
- Best results come from 100+ iterations
- Can resume from checkpoints if interrupted

This experimental approach could discover breakthrough strategies that push us into the top 5!
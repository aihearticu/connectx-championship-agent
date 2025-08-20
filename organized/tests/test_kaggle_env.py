"""Test submission in Kaggle environment"""

from kaggle_environments import make, evaluate

# Test our submission
env = make("connectx", debug=True)

# Load our agent
with open("submission_robust.py", "r") as f:
    agent_code = f.read()

# Test the agent
try:
    print("Testing agent in Kaggle environment...")
    
    # Run a single step test
    trainer = env.train([None, "random"])
    obs = trainer.reset()
    
    # Create a test agent from our code
    exec(agent_code, globals())
    
    # Test basic functionality
    action = agent(obs, env.configuration)
    print(f"Agent returned action: {action}")
    
    # Run a full game
    print("\nRunning full game test...")
    results = env.run([agent, "random"])
    print(f"Game result: {results[-1]}")
    
    if results[-1][0]['reward'] == 1:
        print("✓ Agent won against random!")
    elif results[-1][0]['reward'] == 0:
        print("- Game was a draw")
    else:
        print("✗ Agent lost")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
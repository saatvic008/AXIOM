import os
import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
from axiom.rl.gym_wrapper import AxiomGymEnv

def env_creator(env_config):
    return AxiomGymEnv(env_config)

def train_rl_agent(iterations=10):
    print("[INFO] Initializing Ray RLlib for AXIOM...")
    
    # Initialize Ray
    ray.init(ignore_reinit_error=True)
    
    # Register the custom Mesa environment wrapper
    register_env("axiom_env", env_creator)
    
    # Configure PPO Algorithm
    config = (
        PPOConfig()
        .environment("axiom_env", env_config={"num_tf": 10, "num_c": 10})
        .framework("torch")
        # Run with 1 worker to keep computational load manageable on standard hardware
        .env_runners(num_env_runners=1)
        # Training batch configs
        .training(
            train_batch_size=500,
            minibatch_size=64,
            num_sgd_iter=10
        )
    )
    
    # Build the algorithm
    algo = config.build()
    
    os.makedirs("axiom/logs/checkpoints", exist_ok=True)
    
    print(f"[START] Starting PPO Training for {iterations} iterations...")
    for i in range(iterations):
        result = algo.train()
        reward = result.get('env_runners', {}).get('episode_return_mean', 0.0)
        print(f"Iteration {i+1}/{iterations}: Reward = {reward:.4f}")
        
        # Save a checkpoint every 5 iterations
        if (i + 1) % 5 == 0:
            checkpoint_dir = algo.save(checkpoint_dir=os.path.abspath("axiom/logs/checkpoints"))
            print(f"[SAVED] Checkpoint saved to {checkpoint_dir}")
            
    print("[DONE] Training Complete.")
    ray.shutdown()
    
if __name__ == "__main__":
    train_rl_agent(10)

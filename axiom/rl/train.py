import os
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
from axiom.rl.gym_wrapper import AxiomGymEnv

def env_creator(env_config):
    return AxiomGymEnv(env_config)

# Map agents to different policies to develop heterogeneous strategies
def policy_mapping_fn(agent_id, *args, **kwargs):
    if agent_id in ["RL_0", "RL_1"]:
        return "policy_1"
    else:
        return "policy_2"

def train_rl_agent(iterations=10):
    print("[INFO] Initializing Ray RLlib for AXIOM Phase 3 (Multi-Agent)...")
    
    ray.init(ignore_reinit_error=True)
    register_env("axiom_env", env_creator)
    
    # Create temporary env to extract spaces
    temp_env = AxiomGymEnv({"num_tf": 10, "num_c": 10, "num_rl": 4})
    obs_space = temp_env.observation_space["RL_0"]
    act_space = temp_env.action_space["RL_0"]
    
    # Configure PPO Algorithm for Multi-Agent
    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=False,
            enable_env_runner_and_connector_v2=False,
        )
        .environment("axiom_env", env_config={"num_tf": 10, "num_c": 10, "num_rl": 4})
        .framework("torch")
        .env_runners(num_env_runners=0)
        .training(
            train_batch_size=500,
            minibatch_size=64,
            num_sgd_iter=10
        )
        .multi_agent(
            policies={
                "policy_1": (None, obs_space, act_space, {}),
                "policy_2": (None, obs_space, act_space, {}),
            },
            policy_mapping_fn=policy_mapping_fn,
        )
    )
    
    algo = config.build()
    
    os.makedirs("axiom/logs/checkpoints", exist_ok=True)
    
    print(f"[START] Starting PPO Multi-Agent Training for {iterations} iterations...")
    for i in range(iterations):
        result = algo.train()
        
        reward = result.get('env_runners', {}).get('episode_reward_mean', 0.0)
        policy_rewards = result.get('env_runners', {}).get('policy_reward_mean', {})
        p1_reward = policy_rewards.get('policy_1', 0.0)
        p2_reward = policy_rewards.get('policy_2', 0.0)
        
        print(f"Iteration {i+1}/{iterations}: Mean = {reward:.4f} | P1 = {p1_reward:.4f} | P2 = {p2_reward:.4f}")
        
        if (i + 1) % 5 == 0:
            checkpoint_dir = algo.save(checkpoint_dir=os.path.abspath("axiom/logs/checkpoints"))
            print(f"[SAVED] Checkpoint saved to {checkpoint_dir}")
            
    print("[DONE] Training Complete.")
    ray.shutdown()
    
if __name__ == "__main__":
    train_rl_agent(10)

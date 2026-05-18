import gymnasium as gym
from gymnasium import spaces
import numpy as np
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from axiom.core.environment import AxiomModel

class AxiomGymEnv(MultiAgentEnv):
    """
    Ray RLlib MultiAgentEnv wrapper for the AXIOM Mesa Environment.
    Translates agent state into observation vectors and actions into market orders.
    Supports coalition formation via signaling actions.
    """
    def __init__(self, config=None):
        super().__init__()
        # Use default config if none provided
        self.num_tf = config.get("num_tf", 10) if config else 10
        self.num_c = config.get("num_c", 10) if config else 10
        self.num_rl = config.get("num_rl", 4) if config else 4
        
        # We need to define _agent_ids for MultiAgentEnv
        self._agent_ids = {f"RL_{i}" for i in range(self.num_rl)}
        
        self.model = AxiomModel(
            num_trend_followers=self.num_tf, 
            num_contrarians=self.num_c, 
            num_rl_agents=self.num_rl
        )
        
        # Action Space: [Direction, Quantity, Signal]
        # Direction: 0=Buy, 1=Hold, 2=Sell
        # Quantity: 1, 2, 3, 4, 5
        # Signal: 0=None, 1=Join Coal 1, 2=Join Coal 2, 3=Join Coal 3
        single_act_space = spaces.MultiDiscrete([3, 5, 4])
        self.action_space = spaces.Dict({
            aid: single_act_space for aid in self._agent_ids
        })
        
        # Observation Space: [own_wealth, market_price, moving_avg, neighbor_wealth_delta, sig1_count, sig2_count, sig3_count]
        single_obs_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(7,), 
            dtype=np.float32
        )
        self.observation_space = spaces.Dict({
            aid: single_obs_space for aid in self._agent_ids
        })

    def reset(self, *, seed=None, options=None):
        """Resets the simulation to the initial state."""
        super().reset(seed=seed)
        self.model = AxiomModel(
            num_trend_followers=self.num_tf, 
            num_contrarians=self.num_c, 
            num_rl_agents=self.num_rl
        )
        
        obs = {}
        for agent in self.model.schedule.agents:
            if agent.type == "RLAgent":
                obs[agent.unique_id] = self._get_obs(agent)
                
        return obs, {}

    def step(self, action_dict):
        """Processes RL actions (dictionary) and advances the simulation."""
        old_utilities = {}
        
        # 1. Translate RL actions to Market orders & signals
        for agent in self.model.schedule.agents:
            if agent.type == "RLAgent":
                old_utilities[agent.unique_id] = agent.get_utility()
                
                if agent.unique_id in action_dict:
                    action = action_dict[agent.unique_id]
                    direction, quantity_idx, signal = action
                    quantity = quantity_idx + 1 # 0-4 becomes 1-5
                    
                    # Update signaling state
                    agent.last_signal = signal
                    if signal > 0:
                        agent.coalition_id = f"Coalition_{signal}"
                    else:
                        agent.coalition_id = None
                        
                    current_price = self.model.market.last_price
                    
                    if direction == 0: # Buy
                        self.model.market.submit_order('buy', current_price * 1.01, quantity, agent.unique_id)
                    elif direction == 2: # Sell
                        if agent.inventory >= quantity:
                            self.model.market.submit_order('sell', current_price * 0.99, quantity, agent.unique_id)

        # 2. Advance the whole simulation (all rule-based agents act, market clears)
        self.model.step()
        
        # 3. Gather new observations and calculate rewards
        obs = {}
        rewards = {}
        terminateds = {}
        truncateds = {"__all__": False}
        
        is_done = self.model.schedule.steps >= 500
        terminateds["__all__"] = is_done
        
        # Pre-calculate coalition utilities
        coalition_utilities = {}
        coalition_counts = {}
        
        for agent in self.model.schedule.agents:
            if agent.type == "RLAgent" and agent.coalition_id:
                cid = agent.coalition_id
                u_change = agent.get_utility() - old_utilities[agent.unique_id]
                coalition_utilities[cid] = coalition_utilities.get(cid, 0.0) + u_change
                coalition_counts[cid] = coalition_counts.get(cid, 0) + 1
                
        # Generate return dicts
        for agent in self.model.schedule.agents:
            if agent.type == "RLAgent":
                obs[agent.unique_id] = self._get_obs(agent)
                terminateds[agent.unique_id] = is_done
                
                ind_u_change = agent.get_utility() - old_utilities[agent.unique_id]
                
                # Reward blending for game-theoretic dynamics
                if agent.coalition_id and coalition_counts[agent.coalition_id] > 1:
                    avg_coal_u = coalition_utilities[agent.coalition_id] / coalition_counts[agent.coalition_id]
                    # 70% own reward, 30% coalition average
                    reward = 0.7 * ind_u_change + 0.3 * avg_coal_u
                else:
                    reward = ind_u_change
                    
                rewards[agent.unique_id] = float(reward)
                
        return obs, rewards, terminateds, truncateds, {}

    def _get_obs(self, agent):
        """Helper to construct the 7-dim observation vector."""
        price = self.model.market.last_price
        avg_price = np.mean(self.model.price_history[-10:]) if self.model.price_history else price
        
        # Difference between my wealth and the average wealth
        avg_wealth = np.mean([a.wealth for a in self.model.schedule.agents])
        wealth_delta = agent.wealth - avg_wealth
        
        # Collect signals from other RL agents
        sig_counts = [0, 0, 0]
        for a in self.model.schedule.agents:
            if a.type == "RLAgent" and a.unique_id != agent.unique_id:
                if 1 <= a.last_signal <= 3:
                    sig_counts[a.last_signal - 1] += 1
                    
        return np.array([
            agent.wealth,
            price,
            avg_price,
            wealth_delta,
            sig_counts[0],
            sig_counts[1],
            sig_counts[2]
        ], dtype=np.float32)

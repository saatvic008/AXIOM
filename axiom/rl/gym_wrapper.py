import gymnasium as gym
from gymnasium import spaces
import numpy as np
from axiom.core.environment import AxiomModel

class AxiomGymEnv(gym.Env):
    """
    OpenAI Gym wrapper for the AXIOM Mesa Environment.
    Translates agent state into observation vectors and actions into market orders.
    """
    def __init__(self, config=None):
        super().__init__()
        # Use default config if none provided
        self.num_tf = config.get("num_tf", 10) if config else 10
        self.num_c = config.get("num_c", 10) if config else 10
        
        # Initialize the underlying Mesa model
        self.model = AxiomModel(num_trend_followers=self.num_tf, num_contrarians=self.num_c)
        
        # Action Space: [Direction, Quantity]
        # Direction: 0=Buy, 1=Hold, 2=Sell
        # Quantity: 1, 2, 3, 4, 5
        self.action_space = spaces.MultiDiscrete([3, 5])
        
        # Observation Space: [own_wealth, market_price, moving_avg, neighbor_wealth_delta]
        # We use box with low/high bounds
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(4,), 
            dtype=np.float32
        )

    def reset(self, *, seed=None, options=None):
        """Resets the simulation to the initial state."""
        super().reset(seed=seed)
        self.model = AxiomModel(num_trend_followers=self.num_tf, num_contrarians=self.num_c)
        
        # Get observation for the 'current' agent (index 0 for single-agent setup)
        obs = self._get_obs(self.model.schedule.agents[0])
        return obs, {}

    def step(self, action):
        """Processes one RL action and advances the simulation."""
        # 1. Translate RL action to Market order
        # For Phase 2, we control ONE agent (the first one)
        agent = self.model.schedule.agents[0]
        old_utility = agent.get_utility()

        direction, quantity_idx = action
        quantity = quantity_idx + 1 # 0-4 becomes 1-5
        
        current_price = self.model.market.last_price
        
        if direction == 0: # Buy
            self.model.market.submit_order('buy', current_price * 1.01, quantity, agent.unique_id)
        elif direction == 2: # Sell
            if agent.inventory >= quantity:
                self.model.market.submit_order('sell', current_price * 0.99, quantity, agent.unique_id)

        # 2. Advance the whole simulation (all other rule-based agents act here)
        self.model.step()
        
        # 3. Get new observation and reward
        new_obs = self._get_obs(agent)
        
        # Reward is change in utility
        reward = float(agent.get_utility() - old_utility)
        
        terminated = self.model.schedule.steps >= 500 # Episode limit
        truncated = False
        
        return new_obs, reward, terminated, truncated, {}

    def _get_obs(self, agent):
        """Helper to construct the 4-dim observation vector."""
        price = self.model.market.last_price
        avg_price = np.mean(self.model.price_history[-10:]) if self.model.price_history else price
        
        # Neighbor wealth delta (simplified for single-agent)
        # Difference between my wealth and the average wealth
        avg_wealth = np.mean([a.wealth for a in self.model.schedule.agents])
        wealth_delta = agent.wealth - avg_wealth
        
        return np.array([
            agent.wealth,
            price,
            avg_price,
            wealth_delta
        ], dtype=np.float32)

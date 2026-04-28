from mesa import Agent
import numpy as np

class AxiomAgent(Agent):
    """
    Base agent class for AXIOM. 
    Provides the interface for observation, action, and reward reception.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 100.0  # Initial starting wealth
        self.inventory = 0   # Units of the asset held
        self.last_reward = 0.0
        self.type = "Base"

    def observe(self):
        """
        Returns the agent's observation of the current state.
        To be implemented by subclasses or the environment wrapper.
        """
        # Week 3 will refine this into: [own_wealth, market_price, moving_avg, neighbor_wealth_delta]
        return {
            "wealth": self.wealth,
            "inventory": self.inventory,
            "id": self.unique_id
        }

    def act(self):
        """
        Decision making logic. 
        Rule-based agents will override this in Phase 1.
        RL agents will use the policy in Phase 2.
        """
        pass

    def receive_reward(self, reward):
        """
        Update the agent's internal state based on a reward signal.
        """
        self.last_reward = reward

    def step(self):
        """
        The Mesa step function. Called by the model scheduler.
        """
        self.act()

class TrendFollower(AxiomAgent):
    """
    Buys when price is going up, sells when price is going down.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "TrendFollower"
        self.lookback = 5

    def act(self):
        history = self.model.price_history
        if len(history) < self.lookback:
            return
        
        avg_price = sum(history[-self.lookback:]) / self.lookback
        current_price = self.model.market.last_price
        
        if current_price > avg_price:
            # Price is trending up, buy
            self.model.market.submit_order('buy', current_price * 1.01, 1, self.unique_id)
        elif current_price < avg_price:
            # Price is trending down, sell
            if self.inventory > 0:
                self.model.market.submit_order('sell', current_price * 0.99, 1, self.unique_id)

class Contrarian(AxiomAgent):
    """
    Buys when price is below average, sells when price is above average.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "Contrarian"
        self.lookback = 10

    def act(self):
        history = self.model.price_history
        if len(history) < self.lookback:
            return
        
        avg_price = sum(history[-self.lookback:]) / self.lookback
        current_price = self.model.market.last_price
        
        if current_price < avg_price:
            # Price is low, buy
            self.model.market.submit_order('buy', current_price * 1.01, 1, self.unique_id)
        elif current_price > avg_price:
            # Price is high, sell
            if self.inventory > 0:
                self.model.market.submit_order('sell', current_price * 0.99, 1, self.unique_id)

from mesa import Agent
import numpy as np

class AxiomAgent(Agent):
    """
    Base agent class for AXIOM. 
    Provides the interface for observation, action, and reward reception.
    """
    def __init__(self, unique_id, model, risk_type="RiskNeutral"):
        super().__init__(unique_id, model)
        self.wealth = 100.0  # Initial starting wealth
        self.inventory = 0   # Units of the asset held
        self.last_reward = 0.0
        self.type = "Base"
        self.risk_type = risk_type
        
        # Phase 3: Coalition and Signaling
        self.coalition_id = None
        self.last_signal = 0
        
        # CRRA Gamma parameter for risk awareness
        if self.risk_type == "RiskAverse":
            self.gamma = 2.0
        elif self.risk_type == "RiskSeeking":
            self.gamma = -1.0
        else: # RiskNeutral
            self.gamma = 0.0

    def get_utility(self):
        """
        Calculates the Constant Relative Risk Aversion (CRRA) utility.
        Used by RL agents to evaluate states based on their risk profile.
        """
        w = max(self.wealth, 0.01) # Avoid log(0) or division by zero
        if self.gamma == 1.0:
            return np.log(w)
        else:
            return (w ** (1 - self.gamma)) / (1 - self.gamma)

    def observe(self):
        """
        Returns the agent's observation of the current state.
        To be implemented by subclasses or the environment wrapper.
        """
        # Phase 3: Full observation vector is constructed in the MultiAgentEnv wrapper (gym_wrapper.py)
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

class RLAgent(AxiomAgent):
    """
    An agent controlled by Reinforcement Learning.
    Does not have an internal rule-based act() method.
    Action is provided externally via the Gym environment.
    """
    def __init__(self, unique_id, model, risk_type="RiskNeutral"):
        super().__init__(unique_id, model, risk_type)
        self.type = "RLAgent"

    def act(self):
        # Action is handled by the RL wrapper
        pass


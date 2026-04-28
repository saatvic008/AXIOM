from mesa import Model
from mesa.time import RandomActivation
from .agent import TrendFollower, Contrarian
from .market import Market
import pandas as pd
import os

class AxiomModel(Model):
    """
    The AXIOM Simulation Model.
    """
    def __init__(self, num_trend_followers=10, num_contrarians=10):
        super().__init__()
        self.num_agents = num_trend_followers + num_contrarians
        self.schedule = RandomActivation(self)
        self.market = Market()
        self.price_history = [100.0]
        self.trade_logs = []
        self.agent_logs = []

        # Create agents
        for i in range(num_trend_followers):
            a = TrendFollower(f"TF_{i}", self)
            self.schedule.add(a)

        for i in range(num_contrarians):
            a = Contrarian(f"C_{i}", self)
            self.schedule.add(a)

    def step(self):
        """
        Advance the simulation by one step.
        """
        # 1. Agents act (submit orders to market)
        self.schedule.step()

        # 2. Market clears
        trades = self.market.clear_double_auction()
        
        # 3. Update agent balances based on trades
        for trade in trades:
            buyer = self.schedule.agents[self.get_agent_index(trade['buyer_id'])]
            seller = self.schedule.agents[self.get_agent_index(trade['seller_id'])]
            
            # Buyer pays
            cost = trade['price'] * trade['quantity']
            buyer.wealth -= cost
            buyer.inventory += trade['quantity']
            
            # Seller receives
            seller.wealth += cost
            seller.inventory -= trade['quantity']
            
            # Log the trade
            self.trade_logs.append({
                "step": self.schedule.steps,
                **trade
            })

        # 4. Record current price
        self.price_history.append(self.market.last_price)

        # 5. Log agent wealth for Gini calculation later
        for agent in self.schedule.agents:
            self.agent_logs.append({
                "step": self.schedule.steps,
                "agent_id": agent.unique_id,
                "type": agent.type,
                "wealth": agent.wealth,
                "inventory": agent.inventory
            })

    def get_agent_index(self, agent_id):
        """Helper to find agent by ID in the scheduler."""
        for i, agent in enumerate(self.schedule.agents):
            if agent.unique_id == agent_id:
                return i
        return None

    def save_logs(self, run_id="latest"):
        """Save logs to CSV files."""
        os.makedirs("data/logs", exist_ok=True)
        pd.DataFrame(self.trade_logs).to_csv(f"data/logs/trades_{run_id}.csv", index=False)
        pd.DataFrame(self.agent_logs).to_csv(f"data/logs/agents_{run_id}.csv", index=False)
        print(f"Logs saved to data/logs/")

if __name__ == "__main__":
    # Test run
    model = AxiomModel()
    for i in range(50):
        model.step()
    model.save_logs()

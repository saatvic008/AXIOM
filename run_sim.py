from axiom.core.environment import AxiomModel
import time
import os

def run_simulation(steps=500, save_every=10):
    print("🚀 Starting AXIOM Simulation...")
    model = AxiomModel(num_trend_followers=15, num_contrarians=15)
    
    # Ensure logs directory exists
    os.makedirs("data/logs", exist_ok=True)
    
    for i in range(steps):
        model.step()
        
        if i % save_every == 0:
            print(f"Step {i}: Price = {model.market.last_price:.2f}")
            model.save_logs(run_id="latest")
            
    model.save_logs(run_id="latest")
    print("✅ Simulation Complete.")

if __name__ == "__main__":
    run_simulation()

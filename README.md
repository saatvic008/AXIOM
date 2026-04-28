# AXIOM — Autonomous Multi-Agent RL Economy

**AXIOM** is a high-fidelity simulation platform where dozens of autonomous Reinforcement Learning (RL) agents trade, form coalitions, and exhibit emergent market behaviors—without being programmed with the rules of economics.

> "You build the world; they invent the economy."

---

## 🚀 Vision
Most trading systems are reactive. AXIOM agents are **reasoning, negotiating, and self-organizing**. It is a living laboratory for emergent intelligence, designed for research in multi-agent systems and computational economics.

## 🧠 Key Features
- **Heterogeneous Agents:** Agents with varying utility functions (CRRA) and risk tolerances.
- **Emergent Price Discovery:** Market prices are derived from agent interactions, not hard-coded formulas.
- **Causal Policy Injection:** A "God Mode" sandbox to test economic interventions (taxes, shocks) mid-simulation.
- **Behavioral Phase Transitions:** Observe cooperation vs. defection under resource stress.

## 🛠️ Tech Stack
- **Engine:** Mesa (Agent-Based Modeling)
- **Intelligence:** Ray RLlib, PyTorch (PPO Algorithm)
- **Analytics:** NetworkX, Pandas, NumPy
- **Visualization:** Plotly Dash (Real-time), D3.js (Network Graphs)
- **API:** FastAPI

---

## 📈 Roadmap
- [x] **Phase 1: Simulation Foundation** — LOB, Double Auction, Walrasian clearing.
- [ ] **Phase 2: RL Intelligence Layer** — Integration with Ray RLlib & Multi-Agent training.
- [ ] **Phase 3: Emergent Complexity** — Coalition formation & Game Theoretic signaling.
- [ ] **Phase 4: Research-Grade Polish** — D3.js visualizations & statistical reporting.

---

## 🚦 Getting Started (Phase 1)

### 1. Install Dependencies
```bash
pip install mesa ray[rllib] torch networkx fastapi uvicorn dash pandas numpy plotly
```

### 2. Run the Simulation
```bash
python run_sim.py
```

### 3. Launch the Dashboard
```bash
python axiom/dashboard/app.py
```
View the live market at `http://127.0.0.1:8050`.

---

## 🔬 Research Focus
- Emergent price convergence in zero-intelligence vs. RL-based markets.
- Stability of coalitions under exogenous supply shocks.
- Impact of wealth redistribution policies on Gini coefficient dynamics.

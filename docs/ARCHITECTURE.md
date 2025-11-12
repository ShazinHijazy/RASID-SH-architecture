RASID-SH — Architecture Overview
================================

High-level components
---------------------
- `streamlit_app.py` — UI + orchestrator that runs the simulation and renders live plots.
- `environment.py` — Simulation environment class (`Environment`) that exposes `step(t)` and appends to `logs`.
- `agents.py` — Agent classes and state modeling (positions, reputations, messages).
- `managers.py` — Logic for leader election and task allocation (priority logic, message handling).
- `utils.py` — I/O helpers (save CSV) and `summarize_metrics(df)` used by the Streamlit UI.

Data flow
---------
1. The Streamlit UI creates `Environment(n_agents=..., seed=..., failure_prob=...)` and calls `env.step(t)` each timestep.
2. `env.step` updates agent positions, reputation states, message exchanges (subject to distance-based communication and drop/failure probabilities), and records events in `env.logs`.
3. `streamlit_app.py` builds a `pandas.DataFrame` from `env.logs` each step and feeds it to plotting functions and the metrics summarizer.
4. After the run, `utils.save_df_csv` writes logs to `results/rasid_sh_logs.csv` and Streamlit provides a download button.

Key algorithms
--------------
- Leader election: distance-aware scoring that ranks candidate leaders; manager code in `managers.py` computes scores and triggers leader changes.
- Reputation updates: Bayesian reputation updates applied to pairwise interactions; agent reputations are exposed in log columns with names like `{agent}_rep`.
- Communication model: message delivery depends on distance; messages may be dropped based on computed delivery probability and `failure_prob`.

Extending the system
--------------------
- To add new agent behaviours, modify or extend classes in `agents.py` and call them from `environment.py`.
- To change the leader election scoring formula, edit the manager functions in `managers.py` where scores are calculated.
- To store additional metrics in logs, update `Environment` to append extra fields to `env.logs`.

Testing & validation
--------------------
- Add unit tests that call `Environment.step` for a fixed seed and assert deterministic properties of the logs (e.g., reproducible leader IDs for the same seed).


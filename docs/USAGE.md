Usage — RASID-SH (Streamlit)
==============================

Overview
--------
This document explains how to set up and run the `streamlit_app.py` dashboard that visualizes the RASID-SH simulation.

Prerequisites
-------------
- macOS (tested)
- Homebrew (recommended) or other Python installer (pyenv, conda)
- Git (optional)

Recommended Python
------------------
Use Python 3.11 for best compatibility with binary wheels (notably `pyarrow`).

Quick setup (Homebrew + venv)
----------------------------
1. Install Homebrew (if needed):
   - https://brew.sh/

2. Install Python 3.11:

```bash
brew install python@3.11
```

3. Create a virtualenv in the repo root and activate it:

```bash
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Run the app
-----------
From the project root after activating the venv:

```bash
streamlit run streamlit_app.py
```

What the Streamlit UI does
--------------------------
- Sidebar: controls for number of agents, steps, failure probability, seed, and a low-priority swarm cutoff.
- Live visualization while the simulation runs:
  - Leader timeline
  - Reputation plots
  - Final agent positions
  - Recent logs (table)
  - Metrics summary (steps, leader changes, messages sent/dropped)
- A download button appears after the run that lets you get a CSV of the full logs.

Troubleshooting
---------------
- ModuleNotFoundError for `streamlit`: ensure the venv is activated and that pip installed packages into that venv.
- Pip build errors for `pyarrow`: use Python 3.11 to avoid source builds; otherwise install build deps (`cmake`, C++ toolchain) which is more involved.
- If the UI seems slow: reduce `steps` in the sidebar or the number of agents.

Files of interest
-----------------
- `streamlit_app.py` — front-end dashboard
- `environment.py`, `agents.py`, `managers.py` — simulation and agent logic
- `utils.py` — helpers (save logs, summarize metrics)



README Addendum — Quick start & Troubleshooting
===============================================

Quick start (macOS - recommended)
---------------------------------
Prefer creating a Python 3.11 virtual environment to avoid heavy wheel builds for some dependencies (e.g., `pyarrow`) on newer Python versions.

1. Install Homebrew (if you don't have it):
   - See https://brew.sh/ or run the installer script.

2. Install Python 3.11 via Homebrew:

```bash
brew install python@3.11
```

3. Create and activate a venv using the Homebrew python:

```bash
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

4. Run the Streamlit app from the project root:

```bash
streamlit run streamlit_app.py
```

Troubleshooting
---------------
- If you get `ModuleNotFoundError: No module named 'streamlit'`, ensure you activated the same venv where you installed packages.
- If pip fails building `pyarrow` (error mentions `cmake` or failed wheel build), use Python 3.11 as above — prebuilt wheels are available for 3.11 on macOS.
- If Homebrew isn't installed or you prefer another workflow, `pyenv` or `conda` are fine alternatives.


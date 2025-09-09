# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from environment import Environment
from utils import save_df_csv, summarize_metrics

st.set_page_config(page_title="RASID-SH Final", layout="wide")
st.title("RASID-SH — Final Prototype (Python + Streamlit)")
st.markdown("Improved modular implementation: distance-based comms, Bayesian reputation, live updates.")

# Sidebar controls
st.sidebar.header("Simulation Controls")
n_agents = st.sidebar.slider("Number of agents", 3, 80, 12, 1)
steps = st.sidebar.slider("Simulation steps", 10, 500, 150, 10)
failure_prob = st.sidebar.slider("Per-step failure probability (per agent)", 0.0, 0.5, 0.02, 0.01)
seed = st.sidebar.number_input("Random seed", 0, 9999, 42, 1)
low_cutoff = st.sidebar.number_input("Low priority cutoff (swarm size)", 5, 200, 20, 1)
run_button = st.sidebar.button("Run Simulation (live)")

# advanced
st.sidebar.markdown("---")
st.sidebar.markdown("Advanced options can be edited in `environment.py` / `managers.py`")

# placeholders for live plots
leader_placeholder = st.empty()
rep_placeholder = st.empty()
pos_placeholder = st.empty()
table_placeholder = st.empty()
metrics_placeholder = st.empty()

if run_button:
    env = Environment(n_agents=n_agents, area_size=(40, 40), seed=seed, failure_prob=failure_prob, low_priority_cutoff=low_cutoff)
    logs = []
    start_time = time.time()
    # prepare figure objects to reuse
    for t in range(steps):
        leader = env.step(t)
        df = pd.DataFrame(env.logs)

        # update metrics summary
        metrics = summarize_metrics(df)
        metrics_placeholder.metric("Steps", metrics["steps"])
        metrics_placeholder.metric("Leader changes", metrics["leader_changes"])
        metrics_placeholder.metric("Messages sent", metrics["messages_sent"])
        metrics_placeholder.metric("Messages dropped", metrics["messages_dropped"])

        # Leader timeline (last 80 steps)
        with leader_placeholder.container():
            st.subheader("Leader timeline (recent)")
            s = df["leader"].fillna(-1).astype(int)
            fig1, ax1 = plt.subplots(figsize=(10, 1.8))
            ax1.plot(s.index, s.values, drawstyle="steps-post")
            ax1.set_ylabel("Leader ID (-1 = none)")
            ax1.set_xlabel("Step")
            ax1.grid(True, alpha=0.3)
            st.pyplot(fig1)

        # Reputation plot (sample subset if many)
        rep_cols = [c for c in df.columns if c.endswith("_rep")]
        sample = rep_cols if len(rep_cols) <= 12 else rep_cols[:12]
        with rep_placeholder.container():
            st.subheader("Reputations (sample)")
            fig2, ax2 = plt.subplots(figsize=(10, 3))
            for col in sample:
                ax2.plot(df["step"], df[col], label=col.replace("_rep",""))
            ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
            ax2.set_xlabel("Step")
            ax2.set_ylabel("Reputation")
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)

        # Positions (final step)
        with pos_placeholder.container():
            st.subheader("Agent positions (final step snapshot)")
            pos_x = [df.iloc[-1][c] for c in df.columns if c.endswith("_pos_x")]
            pos_y = [df.iloc[-1][c] for c in df.columns if c.endswith("_pos_y")]
            names = [c.replace("_pos_x","") for c in df.columns if c.endswith("_pos_x")]
            pos_df = pd.DataFrame({"x": pos_x, "y": pos_y, "agent": names})
            fig3, ax3 = plt.subplots(figsize=(6,6))
            ax3.scatter(pos_df["x"], pos_df["y"])
            for i, txt in enumerate(pos_df["agent"]):
                ax3.annotate(txt, (pos_df["x"][i], pos_df["y"][i]), fontsize=8)
            ax3.set_xlim(0, env.area_size[0])
            ax3.set_ylim(0, env.area_size[1])
            ax3.set_xlabel("X")
            ax3.set_ylabel("Y")
            ax3.grid(True, alpha=0.3)
            st.pyplot(fig3)

        # Table of logs (last 20 rows)
        with table_placeholder.container():
            st.subheader("Logs (recent rows)")
            st.dataframe(df.tail(20))

        # tiny pause for live feel
        time.sleep(0.02)

    total_time = time.time() - start_time
    st.success(f"Simulation finished: {steps} steps in {total_time:.2f}s")
    final_df = pd.DataFrame(env.logs)
    csv_path = save_df_csv(final_df, path="results/rasid_sh_logs.csv")
    st.download_button("Download full logs CSV", data=open(csv_path,"rb"), file_name="rasid_sh_logs.csv", mime="text/csv")

# utils.py
import os
import pandas as pd

def save_df_csv(df, path="results/logs.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return path

def summarize_metrics(df):
    return {
        "steps": len(df),
        "leader_changes": int(df["leader_changes"].iloc[-1]) if "leader_changes" in df.columns else None,
        "messages_sent": int(df["messages_sent"].iloc[-1]) if "messages_sent" in df.columns else None,
        "messages_dropped": int(df["messages_dropped"].iloc[-1]) if "messages_dropped" in df.columns else None
    }

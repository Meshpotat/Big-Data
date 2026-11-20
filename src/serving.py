# -*- coding: utf-8 -*-
"""
Real-time inference & micro-batch file streaming helpers for the Streamlit dashboard.
Reuses canonical FEATURES and anti-leakage splits from src.pipeline_core.
"""

import glob
import json
import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.pipeline_core import DEFAULT_GAP_S, FEATURES, prepare_retailrocket_splits


def recommend_crm_action(prob: float, threshold: float = 0.5) -> tuple[str, str]:
    """Map predicted abandonment probability and active threshold to a CRM action and risk level."""
    if prob < threshold:
        return "Organic Buyer (No Interrupt)", "Low"
    if prob >= max(0.75, threshold + 0.20):
        return "High-Risk VIP Intervention", "Critical"
    if prob >= max(0.60, threshold + 0.10):
        return "Offer 5% Flash Coupon", "High"
    return "Send Reminder / Pop-Up", "Medium"


def score_single_session(
    model, session_inputs: dict, threshold: float = 0.5
) -> dict:
    """Score one session dict with a trained scikit-learn classifier and measure latency."""
    row = dict(session_inputs)
    if "price_log" not in row:
        price = float(row.get("price", 0.0))
        row["price_log"] = float(np.log1p(max(price, 0.0)))

    X = pd.DataFrame([{col: float(row[col]) for col in FEATURES}])
    t0 = time.perf_counter()
    prob = float(model.predict_proba(X)[0, 1])
    infer_ms = (time.perf_counter() - t0) * 1000.0

    crm_action, risk_level = recommend_crm_action(prob, threshold=threshold)
    return {
        "probability": prob,
        "predicted_abandoned": bool(prob >= threshold),
        "crm_action": crm_action,
        "risk_level": risk_level,
        "infer_ms": infer_ms,
        "price_log": float(X["price_log"].iloc[0]),
    }


def write_stream_chunk(
    df_chunk: pd.DataFrame, stream_dir: str, tmp_dir: str, chunk_idx: int
) -> str:
    """Write a micro-batch CSV to tmp_dir with write_ts and atomically rename into stream_dir."""
    os.makedirs(stream_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    payload = df_chunk.copy()
    payload["write_ts"] = time.time()
    filename = f"chunk_{chunk_idx:04d}.csv"
    tmp_path = os.path.join(tmp_dir, filename)
    final_path = os.path.join(stream_dir, filename)
    payload.to_csv(tmp_path, index=False)
    os.replace(tmp_path, final_path)
    return final_path


def _score_batch_columns(
    pdf: pd.DataFrame, model, prefix: str, threshold: float
) -> None:
    """Run batch prediction on pdf[FEATURES] and attach prefixed probability, action, and latency columns."""
    X_batch = pdf[FEATURES].astype(float)
    t0 = time.perf_counter()
    probs = model.predict_proba(X_batch)[:, 1]
    now = time.time()
    infer_ms = (time.perf_counter() - t0) * 1000.0

    actions = [recommend_crm_action(float(p), threshold=threshold) for p in probs]
    pdf[f"{prefix}_prob"] = probs
    pdf[f"{prefix}_pred"] = (probs >= threshold).astype(int)
    pdf[f"{prefix}_action"] = [a[0] for a in actions]
    pdf[f"{prefix}_risk"] = [a[1] for a in actions]
    pdf[f"{prefix}_infer_ms"] = infer_ms
    pdf[f"{prefix}_e2e_ms"] = np.maximum((now - pdf["write_ts"]) * 1000.0, infer_ms)


def consume_new_stream_chunks(
    model,
    stream_dir: str,
    processed_files: set[str],
    threshold: float = 0.5,
    lr_model=None,
) -> tuple[pd.DataFrame, list[str]]:
    """Poll stream_dir for unseen chunk_*.csv files, score with RF (and optional LR), and measure E2E latency."""
    candidates = sorted(glob.glob(os.path.join(stream_dir, "chunk_*.csv")))
    new_files = [f for f in candidates if f not in processed_files]
    if not new_files:
        return pd.DataFrame(), []

    dfs = [pd.read_csv(f) for f in new_files]
    pdf = pd.concat(dfs, ignore_index=True)

    _score_batch_columns(pdf, model, "rf", threshold)
    pdf["pred_abandoned"] = pdf["rf_pred"]
    pdf["crm_action"] = pdf["rf_action"]
    pdf["risk_level"] = pdf["rf_risk"]
    pdf["e2e_latency_ms"] = pdf["rf_e2e_ms"]
    pdf["batch_infer_ms"] = pdf["rf_infer_ms"]

    if lr_model is not None:
        _score_batch_columns(pdf, lr_model, "lr", threshold)

    pdf["scored_at"] = time.strftime("%H:%M:%S", time.localtime(time.time()))
    return pdf, new_files


def export_serving_artifacts(
    data_dir: str, out_dir: str, gap_s: int = DEFAULT_GAP_S
) -> dict:
    """
    Train Random Forest and Logistic Regression on chronological Retailrocket train split
    and save joblib models + real chronological test session pool for live dashboard serving.
    """
    os.makedirs(out_dir, exist_ok=True)
    train_df, test_df, meta = prepare_retailrocket_splits(
        data_dir, gap_s=gap_s, train_ratio=0.8
    )

    Xtr, ytr = train_df[FEATURES], train_df["abandoned"]

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    rf.fit(Xtr, ytr)

    lr = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )
    lr.fit(Xtr, ytr)

    rf_path = os.path.join(out_dir, "rf_model.joblib")
    lr_path = os.path.join(out_dir, "lr_model.joblib")
    pool_path = os.path.join(out_dir, "test_stream_pool.csv")
    meta_path = os.path.join(out_dir, "serving_meta.json")

    joblib.dump(rf, rf_path, compress=3)
    joblib.dump(lr, lr_path, compress=3)

    stream_cols = [
        "session_id",
        "visitorid",
        "cart_ts",
        "end_ts",
        "abandoned",
        "price",
        *FEATURES,
    ]
    test_df[stream_cols].to_csv(pool_path, index=False)

    serving_meta = {
        "features": FEATURES,
        "train_price_median": float(meta["train_price_median"]),
        "cat_freq_median": int(train_df["cat_freq"].median()),
        "cat_freq_max": int(train_df["cat_freq"].max()),
        "test_pool_rows": int(len(test_df)),
        "models": ["Random Forest", "Logistic Regression"],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(serving_meta, f, indent=2)

    return serving_meta


if __name__ == "__main__":
    summary = export_serving_artifacts(
        r"c:\Users\muham\Downloads\archive (5)",
        r"c:\Bafqi\Big Data\outputs",
    )
    print("Exported serving artifacts:", json.dumps(summary, indent=2))

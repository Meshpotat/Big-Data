# -*- coding: utf-8 -*-
"""
Full Experiment Runner for Early Cart Abandonment Detection (Retailrocket Dataset)
Implements strict anti-leakage, PR-AUC & Balanced Accuracy evaluation,
5-window Effective Recall simulation, micro-batch streaming latency test,
and 300-DPI INISTA black-and-white publication figures.
"""

import glob
import json
import os
import shutil
import threading
import time
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
)

from src.pipeline_core import (
    DEFAULT_GAP_S,
    FEATURES,
    get_hardware_specs,
    compute_latency_simulation,
    prepare_retailrocket_splits,
)

DATA_DIR = r"c:\Users\muham\Downloads\archive (5)"
OUT_DIR = r"c:\Bafqi\Big Data\outputs"
FIG_DIR = os.path.join(OUT_DIR, "figures")
GAP = DEFAULT_GAP_S

FEATURE_LABELS = {
    "n_events_before": "Events Before Cart (n_events_before)",
    "n_views_before": "Views Before Cart (n_views_before)",
    "n_unique_items": "Unique Items Viewed (n_unique_items)",
    "n_views_same_item": "Same-Item Views (n_views_same_item)",
    "elapsed_min": "Elapsed Time to Cart [min] (elapsed_min)",
    "hour": "Hour of Day (hour)",
    "dow": "Day of Week (dow)",
    "price_log": "Log Item Price (price_log)",
    "cat_freq": "Category Frequency (cat_freq)",
    "prev_sessions": "Prior Completed/Past Sessions (prev_sessions)",
}


def run_streaming_benchmark(test_df: pd.DataFrame, rf_model, out_dir: str) -> dict:
    """
    Execute micro-batch streaming latency benchmark (10 chunks x 100 rows, 3s producer interval,
    2s trigger interval, atomic file rename). Attempts PySpark Structured Streaming first;
    if Windows Java/HADOOP_HOME (winutils.exe) is unavailable, automatically falls back
    to the identical Python atomic-file micro-batch streaming runner.
    """
    stream_dir = os.path.join(out_dir, "stream_in")
    tmp_dir = os.path.join(out_dir, "stream_tmp")
    for d in (stream_dir, tmp_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    n_files = 10
    rows_per_file = 100
    producer_delay = 1.5
    trigger_interval = 2.0

    sample = (
        test_df.sample(n_files * rows_per_file, random_state=42)[FEATURES]
        .astype(float)
        .reset_index(drop=True)
    )

    def producer():
        for i in range(n_files):
            chunk = sample.iloc[i * rows_per_file : (i + 1) * rows_per_file].copy()
            chunk["write_ts"] = time.time()
            tmp_path = os.path.join(tmp_dir, f"chunk_{i:02d}.csv")
            final_path = os.path.join(stream_dir, f"chunk_{i:02d}.csv")
            chunk.to_csv(tmp_path, index=False)
            os.replace(tmp_path, final_path)  # atomic rename on Windows & POSIX
            time.sleep(producer_delay)

    lat_records = []
    engine_used = "Python Native Micro-Batch Streaming Runner (2s Trigger, Atomic File Rename)"
    spark_note = ""

    # Check if Java + winutils are configured for PySpark on Windows
    try:
        import pyspark  # noqa: F401
        from pyspark.sql import SparkSession
        from pyspark.sql.types import StructType, StructField, DoubleType

        if os.name == "nt" and not os.environ.get("HADOOP_HOME"):
            raise RuntimeError(
                "HADOOP_HOME (winutils.exe) not set on Windows; using deterministic micro-batch runner."
            )

        spark = (
            SparkSession.builder.master("local[*]")
            .appName("cart-abandonment-stream")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate()
        )
        schema = StructType([StructField(c, DoubleType()) for c in FEATURES + ["write_ts"]])

        def process_spark_batch(df, batch_id):
            pdf = df.toPandas()
            if len(pdf) == 0:
                return
            t_inf0 = time.time()
            proba = rf_model.predict_proba(pdf[FEATURES])[:, 1]
            now = time.time()
            infer_ms = (now - t_inf0) * 1000.0
            lat_records.append(
                pd.DataFrame(
                    {
                        "batch_id": batch_id,
                        "latency_s": now - pdf["write_ts"],
                        "infer_ms_batch": infer_ms,
                        "pred": (proba >= 0.5).astype(int),
                    }
                )
            )

        query = (
            spark.readStream.schema(schema)
            .option("header", "true")
            .csv(stream_dir)
            .writeStream.foreachBatch(process_spark_batch)
            .trigger(processingTime="2 seconds")
            .start()
        )
        th = threading.Thread(target=producer)
        th.start()
        th.join()
        time.sleep(4)
        query.stop()
        spark.stop()
        engine_used = "PySpark Structured Streaming (local[*], 2s Trigger)"
    except Exception as ex:
        spark_note = str(ex)
        lat_records.clear()
        for d in (stream_dir, tmp_dir):
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)

        processed_files = set()
        stop_flag = False
        batch_id_counter = 0

        def microbatch_consumer():
            nonlocal batch_id_counter
            next_trigger = time.time() + trigger_interval
            while not stop_flag or len(processed_files) < n_files:
                now_wait = time.time()
                if now_wait < next_trigger:
                    time.sleep(max(0.01, next_trigger - now_wait))
                next_trigger = time.time() + trigger_interval

                candidates = sorted(glob.glob(os.path.join(stream_dir, "chunk_*.csv")))
                new_files = [f for f in candidates if f not in processed_files]
                if not new_files:
                    continue

                dfs = []
                for f in new_files:
                    dfs.append(pd.read_csv(f))
                    processed_files.add(f)
                pdf = pd.concat(dfs, ignore_index=True)
                t_inf0 = time.time()
                proba = rf_model.predict_proba(pdf[FEATURES])[:, 1]
                now_done = time.time()
                infer_ms = (now_done - t_inf0) * 1000.0
                lat_records.append(
                    pd.DataFrame(
                        {
                            "batch_id": batch_id_counter,
                            "latency_s": now_done - pdf["write_ts"],
                            "infer_ms_batch": infer_ms,
                            "pred": (proba >= 0.5).astype(int),
                        }
                    )
                )
                batch_id_counter += 1

        th_prod = threading.Thread(target=producer)
        th_cons = threading.Thread(target=microbatch_consumer)
        th_cons.start()
        th_prod.start()
        th_prod.join()
        stop_flag = True
        th_cons.join(timeout=10)

    for d in (stream_dir, tmp_dir):
        shutil.rmtree(d, ignore_errors=True)

    stream_df = pd.concat(lat_records, ignore_index=True)
    desc = stream_df["latency_s"].describe()
    return {
        "engine_used": engine_used,
        "fallback_reason": spark_note,
        "total_streamed_rows": int(len(stream_df)),
        "num_micro_batches": int(stream_df["batch_id"].nunique()),
        "mean_latency_s": round(float(desc["mean"]), 4),
        "std_latency_s": round(float(desc["std"]), 4),
        "min_latency_s": round(float(desc["min"]), 4),
        "p25_latency_s": round(float(desc["25%"]), 4),
        "median_latency_s": round(float(desc["50%"]), 4),
        "p75_latency_s": round(float(desc["75%"]), 4),
        "max_latency_s": round(float(desc["max"]), 4),
        "mean_batch_infer_ms": round(float(stream_df["infer_ms_batch"].mean()), 4),
    }


def generate_inista_figures(
    imp_series: pd.Series,
    by_hour: pd.Series,
    by_dow: pd.Series,
    sim_df: pd.DataFrame,
    fig_dir: str,
):
    os.makedirs(fig_dir, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10,
            "axes.edgecolor": "black",
            "axes.linewidth": 0.9,
        }
    )

    # Fig. 1: Feature Importance (Horizontal Bar Chart with Hatching & Value Annotations)
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=300)
    sorted_imp = imp_series.sort_values(ascending=True)
    y_pos = np.arange(len(sorted_imp))
    hatches = ["//" if i >= len(sorted_imp) - 3 else ".." for i in range(len(sorted_imp))]
    colors = ["#d9d9d9" if i >= len(sorted_imp) - 3 else "#f0f0f0" for i in range(len(sorted_imp))]

    bars = ax.barh(
        y_pos,
        sorted_imp.values,
        color=colors,
        edgecolor="black",
        linewidth=0.9,
        height=0.68,
    )
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([FEATURE_LABELS.get(k, k) for k in sorted_imp.index], fontsize=9)
    ax.set_xlabel("Relative Importance (Gini Importance)", fontsize=10, fontweight="bold")
    ax.set_xlim(0, float(sorted_imp.max()) * 1.18)
    ax.grid(axis="x", linestyle="--", alpha=0.5, color="gray")
    ax.set_axisbelow(True)

    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + 0.004,
            bar.get_y() + bar.get_height() / 2.0,
            f"{w:.4f}",
            va="center",
            ha="left",
            fontsize=8.5,
            color="black",
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig1_feature_importance.png"), dpi=300)
    plt.close(fig)

    # Fig. 2: Temporal Patterns (2 Subplots: Hour of Day and Day of Week with B&W Hatching)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.6), dpi=300)

    bars1 = ax1.bar(
        by_hour.index,
        by_hour.values * 100.0,
        color="#e0e0e0",
        edgecolor="black",
        linewidth=0.8,
        hatch="//",
        width=0.75,
    )
    ax1.axhline(
        by_hour.mean() * 100.0,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label=f"Mean ({by_hour.mean()*100:.1f}%)",
    )
    ax1.set_title("(a) Abandonment Rate by Hour of Day (UTC)", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Hour of Day (0-23)", fontsize=9)
    ax1.set_ylabel("Cart Abandonment Rate (%)", fontsize=9)
    ax1.set_xticks(range(0, 24, 2))
    ax1.set_ylim(max(0, (by_hour.min() * 100.0) - 5), min(100, (by_hour.max() * 100.0) + 3))
    ax1.grid(axis="y", linestyle=":", color="gray", alpha=0.6)
    ax1.set_axisbelow(True)
    ax1.legend(loc="lower right", frameon=True, edgecolor="black", fontsize=8)

    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    bars2 = ax2.bar(
        np.arange(len(by_dow)),
        by_dow.values * 100.0,
        color="#cccccc",
        edgecolor="black",
        linewidth=0.8,
        hatch="..",
        width=0.6,
    )
    ax2.axhline(
        by_dow.mean() * 100.0,
        color="black",
        linestyle="-.",
        linewidth=1.2,
        label=f"Mean ({by_dow.mean()*100:.1f}%)",
    )
    ax2.set_title("(b) Abandonment Rate by Day of Week", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Day of Week", fontsize=9)
    ax2.set_ylabel("Cart Abandonment Rate (%)", fontsize=9)
    ax2.set_xticks(np.arange(len(dow_names)))
    ax2.set_xticklabels(dow_names, fontsize=9)
    ax2.set_ylim(max(0, (by_dow.min() * 100.0) - 5), min(100, (by_dow.max() * 100.0) + 3))
    ax2.grid(axis="y", linestyle=":", color="gray", alpha=0.6)
    ax2.set_axisbelow(True)
    ax2.legend(loc="lower right", frameon=True, edgecolor="black", fontsize=8)

    for b in bars2:
        h_val = b.get_height()
        ax2.text(
            b.get_x() + b.get_width() / 2.0,
            h_val + 0.3,
            f"{h_val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=7.5,
        )

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_temporal_patterns.png"), dpi=300)
    plt.close(fig)

    # Fig. 3: Latency vs Effective Recall & % Decided Before Deadline (Distinct Markers & Linestyles)
    fig, ax1 = plt.subplots(figsize=(7.2, 4.0), dpi=300)
    x_idx = np.arange(len(sim_df))
    x_labels = [
        "Daily Batch\n(86,400s)",
        "Hourly Batch\n(3,600s)",
        "Micro-Batch\n(300s)",
        "NRT 1-Min\n(60s)",
        "NRT 10-Sec\n(10s)",
    ]

    eff_rec_pct = sim_df["effective_recall"].to_numpy() * 100.0
    reach_pct = sim_df["pct_decided_before_deadline"].to_numpy()

    ax1.plot(
        x_idx,
        eff_rec_pct,
        "-o",
        color="black",
        linewidth=1.8,
        markersize=7,
        markerfacecolor="black",
        label="Effective Recall (%)",
    )
    ax1.plot(
        x_idx,
        reach_pct,
        "--s",
        color="#333333",
        linewidth=1.6,
        markersize=7,
        markerfacecolor="white",
        markeredgecolor="black",
        markeredgewidth=1.4,
        label="Decisions Before Deadline (%)",
    )

    for i, (er, rp) in enumerate(zip(eff_rec_pct, reach_pct)):
        ax1.annotate(
            f"{er:.1f}%",
            (x_idx[i], er),
            textcoords="offset points",
            xytext=(0, -14),
            ha="center",
            fontsize=8.5,
            fontweight="bold",
        )
        ax1.annotate(
            f"{rp:.1f}%",
            (x_idx[i], rp),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8.5,
        )

    ax1.set_xticks(x_idx)
    ax1.set_xticklabels(x_labels, fontsize=9)
    ax1.set_ylabel("Percentage (%)", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Processing Architecture Window Scenario", fontsize=10, fontweight="bold")
    ax1.set_ylim(-8, 115)
    ax1.grid(True, linestyle=":", color="gray", alpha=0.6)
    ax1.legend(loc="upper left", frameon=True, edgecolor="black", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_latency_effective_recall.png"), dpi=300)
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    t_start_all = time.time()
    hw_specs = get_hardware_specs()
    print("=== Hardware Specs ===")
    print(json.dumps(hw_specs, indent=2))

    # Step 2-5: Load dataset, session-ize, extract anti-leakage features, and chronological 80:20 split
    print("\n=== Preparing Retailrocket splits & anti-leakage features ===")
    train, test, split_meta = prepare_retailrocket_splits(DATA_DIR, gap_s=GAP, train_ratio=0.8)
    total_events = split_meta["total_events"]
    event_counts = split_meta["event_counts"]
    unique_visitors = split_meta["unique_visitors"]
    unique_items_events = split_meta["unique_items_in_events"]
    total_prop_rows = split_meta["total_item_property_rows"]
    unique_items_in_properties = split_meta["unique_items_in_properties"]
    category_tree_rows = split_meta["category_tree_rows"]
    min_dt = split_meta["min_datetime_utc"]
    max_dt = split_meta["max_datetime_utc"]
    total_all_sessions = split_meta["total_all_sessions"]
    price_missing_rate = split_meta["price_missing_rate_pct"]
    cat_missing_rate = split_meta["category_missing_rate_pct"]
    prev_diff_count = split_meta["strict_prev_sessions_differed_rows"]

    full_encoded = pd.concat([train, test], ignore_index=True)

    Xtr, ytr = train[FEATURES], train["abandoned"]
    Xte, yte = test[FEATURES], test["abandoned"]

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    lr = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )

    model_rows = []
    proba_dict = {}
    for name, mdl in [("Random Forest", rf), ("Logistic Regression", lr)]:
        t0 = time.time()
        mdl.fit(Xtr, ytr)
        train_t = time.time() - t0

        t0 = time.time()
        proba = mdl.predict_proba(Xte)[:, 1]
        infer_t = time.time() - t0
        proba_dict[name] = proba

        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(yte, pred).ravel()
        model_rows.append(
            {
                "model": name,
                "precision": round(float(precision_score(yte, pred)), 4),
                "recall": round(float(recall_score(yte, pred)), 4),
                "f1": round(float(f1_score(yte, pred)), 4),
                "roc_auc": round(float(roc_auc_score(yte, proba)), 4),
                "pr_auc": round(float(average_precision_score(yte, proba)), 4),
                "balanced_acc": round(float(balanced_accuracy_score(yte, pred)), 4),
                "train_s": round(float(train_t), 4),
                "infer_ms_per_row": round(float(infer_t / len(Xte) * 1000.0), 6),
                "tp": int(tp),
                "fp": int(fp),
                "tn": int(tn),
                "fn": int(fn),
            }
        )

    results_df = pd.DataFrame(model_rows)
    print("\n=== Model Evaluation Results ===")
    print(results_df.to_string(index=False))

    # Threshold Sensitivity Analysis for Random Forest & Logistic Regression
    thresh_rows = []
    for m_name in ["Random Forest", "Logistic Regression"]:
        p_arr = proba_dict[m_name]
        for th in [0.30, 0.40, 0.50, 0.60, 0.70]:
            pr = (p_arr >= th).astype(int)
            thresh_rows.append(
                {
                    "model": m_name,
                    "threshold": th,
                    "precision": round(float(precision_score(yte, pr, zero_division=0)), 4),
                    "recall": round(float(recall_score(yte, pr, zero_division=0)), 4),
                    "f1": round(float(f1_score(yte, pr, zero_division=0)), 4),
                    "balanced_acc": round(float(balanced_accuracy_score(yte, pr)), 4),
                }
            )
    thresh_df = pd.DataFrame(thresh_rows)

    # Feature importance
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
    print("\n=== Random Forest Feature Importance ===")
    print(imp.round(4))

    # Step 6: Temporal Pattern Analysis
    by_hour = full_encoded.groupby("hour")["abandoned"].mean()
    by_dow = full_encoded.groupby("dow")["abandoned"].mean()

    # Step 7: Batch vs Near Real-Time Latency & Effective Recall Simulation
    proba_rf = proba_dict["Random Forest"]
    pred_rf = (proba_rf >= 0.5).astype(int)
    infer_s_rf = (
        results_df.loc[results_df["model"] == "Random Forest", "infer_ms_per_row"].iloc[0]
        / 1000.0
    )

    sim_list = [
        compute_latency_simulation(test, pred_rf, infer_s_rf, 86400, "Batch Harian (24 Jam)", GAP),
        compute_latency_simulation(test, pred_rf, infer_s_rf, 3600, "Batch Per Jam (1 Jam)", GAP),
        compute_latency_simulation(test, pred_rf, infer_s_rf, 300, "Micro-Batch (5 Menit)", GAP),
        compute_latency_simulation(test, pred_rf, infer_s_rf, 60, "Near Real-Time (1 Menit)", GAP),
        compute_latency_simulation(test, pred_rf, infer_s_rf, 10, "Near Real-Time (10 Detik)", GAP),
    ]
    sim_df = pd.DataFrame(sim_list).round(4)
    print("\n=== Latency & Effective Recall Simulation ===")
    print(sim_df.to_string(index=False))

    # Step 8: Micro-Batch Streaming Benchmark
    print("\n=== Running Micro-Batch Streaming Latency Benchmark ===")
    stream_stats = run_streaming_benchmark(test, rf, OUT_DIR)
    print(json.dumps(stream_stats, indent=2))

    # Generate 300-DPI INISTA Black-and-White Figures
    print("\n=== Generating 300-DPI INISTA Figures ===")
    generate_inista_figures(imp, by_hour, by_dow, sim_df, FIG_DIR)

    # Feature Descriptive Stats
    feat_stats = (
        full_encoded[FEATURES + ["abandoned"]]
        .describe()
        .T[["mean", "std", "min", "50%", "max"]]
        .round(4)
    )

    # Compare feature means between Abandoned (1) and Completed (0)
    class_means = (
        full_encoded.groupby("abandoned")[FEATURES].mean().T.rename(columns={0: "completed_mean", 1: "abandoned_mean"}).round(4)
    )

    summary = {
        "hardware": hw_specs,
        "dataset": {
            "total_events": total_events,
            "event_counts": {k: int(v) for k, v in event_counts.items()},
            "unique_visitors": unique_visitors,
            "unique_items_in_events": unique_items_events,
            "total_item_property_rows": int(total_prop_rows),
            "unique_items_in_properties": unique_items_in_properties,
            "category_tree_rows": category_tree_rows,
            "min_datetime_utc": min_dt,
            "max_datetime_utc": max_dt,
            "total_all_sessions": total_all_sessions,
            "total_cart_sessions": int(len(full_encoded)),
            "abandoned_count": int((full_encoded["abandoned"] == 1).sum()),
            "completed_count": int((full_encoded["abandoned"] == 0).sum()),
            "abandoned_rate_pct": round(float(full_encoded["abandoned"].mean() * 100.0), 2),
            "completed_rate_pct": round(float((1.0 - full_encoded["abandoned"].mean()) * 100.0), 2),
            "train_sessions": int(len(train)),
            "test_sessions": int(len(test)),
            "train_abandoned_rate_pct": round(float(train["abandoned"].mean() * 100.0), 2),
            "test_abandoned_rate_pct": round(float(test["abandoned"].mean() * 100.0), 2),
            "train_price_median": round(float(split_meta["train_price_median"]), 2),
            "price_missing_rate_pct": round(price_missing_rate, 2),
            "category_missing_rate_pct": round(cat_missing_rate, 2),
            "strict_prev_sessions_differed_rows": prev_diff_count,
            "session_remaining_sec_median": round(float((test["end_ts"] - test["cart_ts"]).median()), 2),
            "session_remaining_sec_mean": round(float((test["end_ts"] - test["cart_ts"]).mean()), 2),
        },
        "models": model_rows,
        "threshold_sensitivity": thresh_rows,
        "feature_importance": {k: round(float(v), 4) for k, v in imp.items()},
        "feature_descriptive_stats": feat_stats.to_dict(orient="index"),
        "feature_class_means": class_means.to_dict(orient="index"),
        "temporal_patterns": {
            "by_hour_pct": {int(k): round(float(v * 100.0), 2) for k, v in by_hour.items()},
            "by_dow_pct": {int(k): round(float(v * 100.0), 2) for k, v in by_dow.items()},
        },
        "latency_simulation": sim_df.to_dict(orient="records"),
        "streaming_benchmark": stream_stats,
        "total_pipeline_runtime_s": round(float(time.time() - t_start_all), 2),
    }

    with open(os.path.join(OUT_DIR, "metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    results_df.to_csv(os.path.join(OUT_DIR, "table1_model_comparison.csv"), index=False)
    thresh_df.to_csv(os.path.join(OUT_DIR, "table2_threshold_sensitivity.csv"), index=False)
    sim_df.to_csv(os.path.join(OUT_DIR, "table3_latency_simulation.csv"), index=False)

    print(f"\n=== ALL DONE in {summary['total_pipeline_runtime_s']}s. Summary saved to outputs/metrics_summary.json ===")


if __name__ == "__main__":
    main()

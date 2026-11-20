# -*- coding: utf-8 -*-
"""
Live Operational Telemetry & Dual-Model Side-by-Side Inference Dashboard — Kelompok 15
Compares Random Forest and Logistic Regression side-by-side across:
  1) Live Atomic Micro-Batch File Stream (real Retailrocket chronological test sessions)
  2) Interactive Single-Session Predictor (unified input -> split RF vs LR output)
  3) Chronological Test Benchmarks & Threshold Sensitivity (split RF vs LR panels)
  4) Batch vs. Near Real-Time Effective Recall & Temporal EDA

Run via:
  streamlit run dashboard.py
"""

import importlib
import inspect
import json
import os
import shutil
import sys
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import src.serving as _serving  # noqa: E402

if "lr_model" not in inspect.signature(_serving.consume_new_stream_chunks).parameters:
    importlib.reload(_serving)

consume_new_stream_chunks = _serving.consume_new_stream_chunks
score_single_session = _serving.score_single_session
write_stream_chunk = _serving.write_stream_chunk

OUT_DIR = os.path.join(BASE_DIR, "outputs")
FIG_DIR = os.path.join(OUT_DIR, "figures")
SUMMARY_PATH = os.path.join(OUT_DIR, "metrics_summary.json")
SERVING_META_PATH = os.path.join(OUT_DIR, "serving_meta.json")
TEST_POOL_PATH = os.path.join(OUT_DIR, "test_stream_pool.csv")
RF_MODEL_PATH = os.path.join(OUT_DIR, "rf_model.joblib")
LR_MODEL_PATH = os.path.join(OUT_DIR, "lr_model.joblib")
LIVE_STREAM_DIR = os.path.join(OUT_DIR, "live_stream_in")
LIVE_TMP_DIR = os.path.join(OUT_DIR, "live_stream_tmp")

st.set_page_config(
    page_title="Real-Time Cart Abandonment Telemetry — Kelompok 15",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_static_data():
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)
    with open(SERVING_META_PATH, "r", encoding="utf-8") as f:
        serving_meta = json.load(f)
    test_pool = pd.read_csv(TEST_POOL_PATH)
    return summary, serving_meta, test_pool


@st.cache_resource
def load_models():
    return {
        "Random Forest": joblib.load(RF_MODEL_PATH),
        "Logistic Regression": joblib.load(LR_MODEL_PATH),
    }


def init_stream_state():
    if "stream_initialized" not in st.session_state:
        st.session_state.stream_initialized = True
        for d in (LIVE_STREAM_DIR, LIVE_TMP_DIR):
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)
    defaults = {
        "stream_running": False,
        "stream_cursor": 0,
        "chunk_idx": 0,
        "processed_files": set(),
        "live_history": pd.DataFrame(),
        "batch_latencies": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    hist = st.session_state.live_history
    if not hist.empty and "lr_prob" not in hist.columns:
        reset_live_stream()


def reset_live_stream():
    st.session_state.stream_running = False
    st.session_state.stream_cursor = 0
    st.session_state.chunk_idx = 0
    st.session_state.processed_files = set()
    st.session_state.live_history = pd.DataFrame()
    st.session_state.batch_latencies = []
    for d in (LIVE_STREAM_DIR, LIVE_TMP_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)


def execute_one_microbatch(rf_model, lr_model, test_pool: pd.DataFrame, batch_size: int, threshold: float):
    """Write one atomic CSV chunk of real Retailrocket test sessions and score with both RF & LR."""
    total_rows = len(test_pool)
    start = st.session_state.stream_cursor % total_rows
    end = start + batch_size
    if end <= total_rows:
        chunk_df = test_pool.iloc[start:end].copy()
    else:
        chunk_df = pd.concat(
            [test_pool.iloc[start:], test_pool.iloc[: end - total_rows]], ignore_index=True
        )

    st.session_state.stream_cursor = (start + batch_size) % total_rows
    chunk_id = st.session_state.chunk_idx
    st.session_state.chunk_idx += 1

    write_stream_chunk(chunk_df, LIVE_STREAM_DIR, LIVE_TMP_DIR, chunk_id)
    scored_df, new_files = consume_new_stream_chunks(
        rf_model,
        LIVE_STREAM_DIR,
        st.session_state.processed_files,
        threshold=threshold,
        lr_model=lr_model,
    )
    st.session_state.processed_files.update(new_files)

    if not scored_df.empty:
        scored_df["batch_id"] = chunk_id + 1
        scored_df["actual_label"] = scored_df["abandoned"].map(
            {1: "Abandoned (1)", 0: "Completed (0)"}
        )
        scored_df["rf_correct"] = scored_df["rf_pred"] == scored_df["abandoned"]
        scored_df["lr_correct"] = scored_df["lr_pred"] == scored_df["abandoned"]

        if st.session_state.live_history.empty:
            st.session_state.live_history = scored_df
        else:
            st.session_state.live_history = pd.concat(
                [scored_df, st.session_state.live_history], ignore_index=True
            ).head(250)

        st.session_state.batch_latencies.append(
            {
                "batch_id": chunk_id + 1,
                "RF E2E (ms)": round(float(scored_df["rf_e2e_ms"].mean()), 2),
                "LR E2E (ms)": round(float(scored_df["lr_e2e_ms"].mean()), 2),
                "RF Infer (ms)": round(float(scored_df["rf_infer_ms"].iloc[0]), 2),
                "LR Infer (ms)": round(float(scored_df["lr_infer_ms"].iloc[0]), 2),
            }
        )
        st.session_state.batch_latencies = st.session_state.batch_latencies[-40:]


def apply_predictor_preset(preset_values: dict):
    for key, val in preset_values.items():
        st.session_state[f"inp_{key}"] = val


def render_live_stream_half(col, hist: pd.DataFrame, model_title: str, prefix: str, threshold: float):
    """Render one half (RF or LR) of the unified live micro-batch stream comparison."""
    with col:
        st.markdown(f"#### {model_title}")
        mean_e2e = float(hist[f"{prefix}_e2e_ms"].mean())
        last_infer = float(hist[f"{prefix}_infer_ms"].iloc[0])
        risk_rate = float((hist[f"{prefix}_pred"] == 1).mean() * 100.0)
        acc_rate = float(hist[f"{prefix}_correct"].mean() * 100.0)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Live Accuracy", f"{acc_rate:.1f}%", "vs. Retailrocket")
        k2.metric("Flagged At-Risk", f"{risk_rate:.1f}%", f"τ = {threshold:.2f}")
        k3.metric("Mean E2E Latency", f"{mean_e2e:.2f} ms", "Write -> Predict")
        k4.metric("Last Batch Infer", f"{last_infer:.2f} ms", f"{len(hist):,} rows")

        cols = [
            "batch_id",
            "session_id",
            "prev_sessions",
            "elapsed_min",
            f"{prefix}_prob",
            f"{prefix}_action",
            "actual_label",
            f"{prefix}_e2e_ms",
        ]
        view_df = hist[cols].head(20).copy()
        view_df["elapsed_min"] = view_df["elapsed_min"].round(2)
        view_df[f"{prefix}_prob"] = view_df[f"{prefix}_prob"].round(4)
        view_df[f"{prefix}_e2e_ms"] = view_df[f"{prefix}_e2e_ms"].round(2)
        view_df = view_df.rename(
            columns={
                f"{prefix}_prob": "prob",
                f"{prefix}_action": "crm_action",
                f"{prefix}_e2e_ms": "e2e_ms",
            }
        )
        st.dataframe(view_df, use_container_width=True, hide_index=True)


def render_single_prediction_card(col, model_title: str, subtitle: str, pred_result: dict, threshold: float):
    """Render one half (RF or LR) of the unified single-session prediction output."""
    with col:
        with st.container(border=True):
            st.markdown(f"#### {model_title}")
            st.caption(subtitle)
            prob_pct = pred_result["probability"] * 100.0
            c_m1, c_m2 = st.columns(2)
            c_m1.metric("Abandonment Probability", f"{prob_pct:.2f}%", f"τ = {threshold:.2f}")
            c_m2.metric("Single-Row Inference", f"{pred_result['infer_ms']:.3f} ms", pred_result["risk_level"])
            st.progress(min(max(pred_result["probability"], 0.0), 1.0))

            if pred_result["predicted_abandoned"]:
                st.error(f"**AT RISK OF ABANDONING** — Action: {pred_result['crm_action']}")
            else:
                st.success(f"**LIKELY TO CHECKOUT** — Action: {pred_result['crm_action']}")


def render_model_benchmark_half(col, model_title: str, subtitle: str, row_dict: dict, th_sub_df: pd.DataFrame, active_thresh: float):
    """Render one half (RF or LR) of the unified chronological benchmark & threshold comparison."""
    with col:
        with st.container(border=True):
            st.markdown(f"#### {model_title}")
            st.caption(subtitle)

            r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
            r1_c1.metric("PR-AUC", f"{row_dict['pr_auc']:.4f}")
            r1_c2.metric("ROC-AUC", f"{row_dict['roc_auc']:.4f}")
            r1_c3.metric("Balanced Acc", f"{row_dict['balanced_acc']:.4f}")
            r1_c4.metric("F1-Score", f"{row_dict['f1']:.4f}")

            r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
            r2_c1.metric("Precision", f"{row_dict['precision']:.4f}")
            r2_c2.metric("Recall", f"{row_dict['recall']:.4f}")
            r2_c3.metric("Train Time", f"{row_dict['train_s']:.4f} s")
            r2_c4.metric("Infer / Row", f"{row_dict['infer_ms_per_row']:.6f} ms")

            st.markdown("**Confusion Matrix (Test N = 8,785, τ = 0.50)**")
            cm_df = pd.DataFrame(
                [
                    {"Actual \\ Pred": "Actual Abandoned (1)", "Pred Abandoned (1)": f"TP: {row_dict['tp']:,}", "Pred Completed (0)": f"FN: {row_dict['fn']:,}"},
                    {"Actual \\ Pred": "Actual Completed (0)", "Pred Abandoned (1)": f"FP: {row_dict['fp']:,}", "Pred Completed (0)": f"TN: {row_dict['tn']:,}"},
                ]
            )
            st.dataframe(cm_df, use_container_width=True, hide_index=True)

            st.markdown(f"**Threshold Sensitivity (Active τ = {active_thresh:.2f})**")
            th_display = th_sub_df[["threshold", "precision", "recall", "f1", "balanced_acc"]].copy()
            th_display["active"] = th_display["threshold"].apply(lambda t: "Active" if t == active_thresh else "")
            st.dataframe(th_display, use_container_width=True, hide_index=True)


# --- LOAD DATA & MODELS ---
artifacts_ready = all(
    os.path.exists(p)
    for p in (SUMMARY_PATH, SERVING_META_PATH, TEST_POOL_PATH, RF_MODEL_PATH, LR_MODEL_PATH)
)
if not artifacts_ready:
    st.error(
        "Serving artifacts not found in outputs/. Run `python -m src.serving` first to generate "
        "rf_model.joblib, lr_model.joblib, serving_meta.json, and test_stream_pool.csv."
    )
    st.stop()

summary, serving_meta, test_pool = load_static_data()
models_dict = load_models()
rf_model = models_dict["Random Forest"]
lr_model = models_dict["Logistic Regression"]
init_stream_state()

ds = summary["dataset"]
hw = summary["hardware"]
models_df = pd.DataFrame(summary["models"])
thresh_df = pd.DataFrame(summary["threshold_sensitivity"])
sim_df = pd.DataFrame(summary["latency_simulation"])
stream_bm = summary["streaming_benchmark"]

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### Kelompok 15 — Big Data")
    st.caption(
        "Arief Adhitya Ramadhan (J0403241055)\n\n"
        "Muhammad Bafqi (J0403241018)\n\n"
        "Zidan Dzulqarnain (J0403241032)"
    )
    st.divider()
    st.markdown("#### Dual-Model Serving Controls")
    st.caption("Both **Random Forest** and **Logistic Regression** run side-by-side in real time.")
    selected_thresh = st.select_slider(
        "Decision Threshold (τ)",
        options=[0.30, 0.40, 0.50, 0.60, 0.70],
        value=0.50,
    )
    selected_window = st.selectbox(
        "Architectural Benchmark Window",
        options=sim_df["mode"].tolist(),
        index=2,
    )
    st.divider()
    st.markdown("#### Micro-Batch Stream Settings")
    trigger_seconds = st.select_slider(
        "Stream Trigger Interval (seconds)",
        options=[1.0, 2.0, 3.0, 5.0],
        value=2.0,
    )
    batch_size = st.slider("Sessions per Micro-Batch", min_value=5, max_value=50, value=10, step=5)

    st.divider()
    st.markdown("#### Hardware Baseline")
    st.caption(
        f"**CPU:** {hw['cpu_name']} ({hw['physical_cores']}C/{hw['logical_threads']}T)\n\n"
        f"**RAM:** {hw['ram_gb']} GB | **Python:** {hw['python_version']}\n\n"
        f"**Test Stream Pool:** {len(test_pool):,} real sessions"
    )

# --- HEADER & KEY TELEMETRY ---
st.title("Real-Time Cart Abandonment Telemetry: Random Forest vs. Logistic Regression")
st.caption(
    f"Retailrocket Clickstream ({ds['min_datetime_utc']} to {ds['max_datetime_utc']}) · "
    f"Dual-Model Live Comparison · Threshold τ = {selected_thresh:.2f}"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Events", f"{ds['total_events']:,}", f"{ds['total_all_sessions']:,} sessions")
k2.metric("Cart Sessions", f"{ds['total_cart_sessions']:,}", f"Test Pool: {len(test_pool):,}")
k3.metric("Abandonment Rate", f"{ds['abandoned_rate_pct']}%", f"{ds['abandoned_count']:,} abandoned")
k4.metric("RF vs LR PR-AUC", "0.8574 vs 0.8420", "+1.54% RF advantage")
k5.metric("Median Remaining", f"{ds['session_remaining_sec_median']} s", "After 1st addtocart")
win_row = sim_df[sim_df["mode"] == selected_window].iloc[0]
k6.metric(
    "Effective Recall",
    f"{win_row['effective_recall']:.4f}",
    f"{win_row['pct_decided_before_deadline']:.1f}% on time",
)

st.divider()

tab_stream, tab_predictor, tab_compare, tab_eda = st.tabs(
    [
        "1. Live Micro-Batch Stream (RF vs. LR)",
        "2. Real-Time Single-Session Predictor (RF vs. LR)",
        "3. Model Benchmark & Batch vs. NRT Comparison",
        "4. Feature Importance & Temporal Behavior",
    ]
)

# --- TAB 1: LIVE ATOMIC MICRO-BATCH STREAMING (UNIFIED SPLIT IN TWO) ---
with tab_stream:
    def render_live_stream_panel():
        if st.session_state.stream_running:
            execute_one_microbatch(rf_model, lr_model, test_pool, batch_size, selected_thresh)

        c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4 = st.columns([1.2, 1.2, 1.0, 2.6])
        with c_ctrl1:
            if not st.session_state.stream_running:
                if st.button("Start Auto-Stream", type="primary", use_container_width=True):
                    st.session_state.stream_running = True
                    st.rerun()
            else:
                if st.button("Pause Auto-Stream", type="secondary", use_container_width=True):
                    st.session_state.stream_running = False
                    st.rerun()

        with c_ctrl2:
            if st.button("+1 Live Micro-Batch", use_container_width=True):
                execute_one_microbatch(rf_model, lr_model, test_pool, batch_size, selected_thresh)

        with c_ctrl3:
            if st.button("Reset Stream", use_container_width=True):
                reset_live_stream()
                st.rerun()

        with c_ctrl4:
            if st.session_state.stream_running:
                st.success(
                    f"LIVE DUAL-MODEL STREAM ACTIVE — Scoring {batch_size} sessions every {trigger_seconds:.0f}s "
                    "with both Random Forest and Logistic Regression simultaneously."
                )
            else:
                st.info(
                    "IDLE — Click **Start Auto-Stream** or **+1 Live Micro-Batch** to compare "
                    "Random Forest (left) vs. Logistic Regression (right) on the exact same incoming stream."
                )

        hist = st.session_state.live_history
        if hist.empty:
            st.caption("No live batches scored yet in this session. Trigger a batch above to begin.")
        else:
            st.caption(
                f"Total Scored: **{st.session_state.chunk_idx * batch_size:,} sessions** "
                f"across **{st.session_state.chunk_idx} micro-batches** (identical input stream for both models)."
            )
            col_rf, col_lr = st.columns(2, gap="medium")
            render_live_stream_half(
                col_rf,
                hist,
                "Random Forest (Primary · Non-Linear Ensemble)",
                "rf",
                selected_thresh,
            )
            render_live_stream_half(
                col_lr,
                hist,
                "Logistic Regression (Baseline · Linear Fast)",
                "lr",
                selected_thresh,
            )

            st.markdown("##### Live End-to-End Latency Comparison per Micro-Batch (ms)")
            lat_df = pd.DataFrame(st.session_state.batch_latencies)
            if not lat_df.empty:
                st.line_chart(
                    lat_df.set_index("batch_id")[["RF E2E (ms)", "LR E2E (ms)"]],
                    height=220,
                )

    run_interval = trigger_seconds if st.session_state.stream_running else None
    st.fragment(run_every=run_interval)(render_live_stream_panel)()

# --- TAB 2: INTERACTIVE REAL-TIME SINGLE-SESSION PREDICTOR (UNIFIED INPUT -> SPLIT OUTPUT) ---
with tab_predictor:
    st.subheader("Interactive Real-Time Shopper Risk Predictor (RF vs. LR)")
    st.caption(
        "Adjust shopper session attributes at the exact moment of the first `addtocart` event. "
        "Both **Random Forest** and **Logistic Regression** score the input side-by-side in real time."
    )

    p_col1, p_col2, p_col3, _ = st.columns([1, 1, 1, 1.5])
    with p_col1:
        st.button(
            "Preset: New Impulsive Visitor",
            use_container_width=True,
            on_click=apply_predictor_preset,
            args=({
                "prev_sessions": 0,
                "elapsed_min": 0.4,
                "price": 120000.0,
                "n_views_same_item": 1,
                "n_events_before": 2,
                "n_views_before": 1,
                "n_unique_items": 1,
                "cat_freq": 450,
                "hour": 9,
                "dow": 5,
            },),
        )
    with p_col2:
        st.button(
            "Preset: Returning Loyal Buyer",
            use_container_width=True,
            on_click=apply_predictor_preset,
            args=({
                "prev_sessions": 14,
                "elapsed_min": 11.5,
                "price": 45000.0,
                "n_views_same_item": 3,
                "n_events_before": 7,
                "n_views_before": 6,
                "n_unique_items": 3,
                "cat_freq": 180,
                "hour": 15,
                "dow": 2,
            },),
        )
    with p_col3:
        st.button(
            "Preset: High-Price Hesitation",
            use_container_width=True,
            on_click=apply_predictor_preset,
            args=({
                "prev_sessions": 1,
                "elapsed_min": 3.0,
                "price": 650000.0,
                "n_views_same_item": 2,
                "n_events_before": 4,
                "n_views_before": 3,
                "n_unique_items": 2,
                "cat_freq": 120,
                "hour": 12,
                "dow": 6,
            },),
        )

    c_in1, c_in2 = st.columns(2)
    with c_in1:
        prev_sessions = st.number_input("Prior Sessions (prev_sessions)", 0, 200, 0, key="inp_prev_sessions")
        elapsed_min = st.slider("Elapsed Time to First Cart [min]", 0.0, 60.0, 1.0, 0.2, key="inp_elapsed_min")
        price_val = st.number_input(
            "Item Price (Retailrocket property 790)",
            min_value=100.0,
            max_value=5000000.0,
            value=float(serving_meta["train_price_median"]),
            step=5000.0,
            key="inp_price",
        )
        n_views_same_item = st.slider("Views on Same Item", 0, 20, 1, key="inp_n_views_same_item")
        cat_freq = st.slider(
            "Category Frequency (cat_freq)",
            0,
            int(serving_meta["cat_freq_max"]),
            int(serving_meta["cat_freq_median"]),
            key="inp_cat_freq",
        )

    with c_in2:
        n_events_before = st.slider("Total Events Before Cart", 1, 50, 2, key="inp_n_events_before")
        n_views_before = st.slider("Total Views Before Cart", 0, 50, 1, key="inp_n_views_before")
        n_unique_items = st.slider("Unique Items Viewed", 1, 30, 1, key="inp_n_unique_items")
        hour_val = st.slider("Hour of Day (UTC)", 0, 23, 9, key="inp_hour")
        dow_names = ["Mon (0)", "Tue (1)", "Wed (2)", "Thu (3)", "Fri (4)", "Sat (5)", "Sun (6)"]
        dow_val = st.selectbox(
            "Day of Week",
            options=list(range(7)),
            format_func=lambda idx: dow_names[idx],
            index=5,
            key="inp_dow",
        )

    session_payload = {
        "n_events_before": n_events_before,
        "n_views_before": n_views_before,
        "n_unique_items": n_unique_items,
        "n_views_same_item": n_views_same_item,
        "elapsed_min": elapsed_min,
        "hour": hour_val,
        "dow": dow_val,
        "price": price_val,
        "cat_freq": cat_freq,
        "prev_sessions": prev_sessions,
    }
    rf_pred = score_single_session(rf_model, session_payload, threshold=selected_thresh)
    lr_pred = score_single_session(lr_model, session_payload, threshold=selected_thresh)

    st.markdown("#### Side-by-Side Real-Time Model Output")
    col_rf_out, col_lr_out = st.columns(2, gap="medium")
    render_single_prediction_card(
        col_rf_out,
        "Random Forest (Primary Model)",
        "200 trees, max_depth=12, class_weight='balanced'",
        rf_pred,
        selected_thresh,
    )
    render_single_prediction_card(
        col_lr_out,
        "Logistic Regression (Baseline Model)",
        "StandardScaler + linear classifier, class_weight='balanced'",
        lr_pred,
        selected_thresh,
    )
    prob_diff_pp = (rf_pred["probability"] - lr_pred["probability"]) * 100.0
    st.caption(
        f"Probability difference (RF − LR): **{prob_diff_pp:+.2f} percentage points** · "
        f"Computed `price_log` = `{rf_pred['price_log']:.4f}`"
    )

# --- TAB 3: UNIFIED RF vs LR BENCHMARK (SPLIT IN TWO) & BATCH vs NRT LATENCY ---
with tab_compare:
    st.subheader("Unified Model Comparison: Random Forest vs. Logistic Regression (Test N = 8,785)")
    st.caption(
        "Evaluated on the strict chronological 20% test split (`cart_ts`) under 73.16% abandoned class imbalance."
    )

    rf_row = models_df[models_df["model"] == "Random Forest"].iloc[0].to_dict()
    lr_row = models_df[models_df["model"] == "Logistic Regression"].iloc[0].to_dict()
    rf_th = thresh_df[thresh_df["model"] == "Random Forest"]
    lr_th = thresh_df[thresh_df["model"] == "Logistic Regression"]

    bm_col_rf, bm_col_lr = st.columns(2, gap="medium")
    render_model_benchmark_half(
        bm_col_rf,
        "Random Forest (Primary)",
        "Higher PR-AUC (0.8574), ROC-AUC (0.7030), Balanced Acc (0.6389), and Precision (0.8175)",
        rf_row,
        rf_th,
        selected_thresh,
    )
    render_model_benchmark_half(
        bm_col_lr,
        "Logistic Regression (Baseline)",
        "Faster training (0.0479s) & inference (0.000228 ms/row), higher Recall at τ=0.50 (0.7487)",
        lr_row,
        lr_th,
        selected_thresh,
    )

    st.divider()
    st.subheader("Architectural Processing Window vs. Effective Recall (Batch vs. Near Real-Time)")
    col_l, col_r = st.columns([1.25, 0.75])
    with col_l:
        st.markdown(
            "Comparison of 5 processing windows under intervention deadline "
            "$t_{\\text{deadline}} = t_{\\text{end}} + 1800\\text{ s}$:"
        )
        st.dataframe(
            sim_df[
                [
                    "mode",
                    "window_s",
                    "mean_latency_s",
                    "median_latency_s",
                    "pct_decided_before_deadline",
                    "tp_on_time",
                    "effective_recall",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    with col_r:
        fig3_path = os.path.join(FIG_DIR, "fig3_latency_effective_recall.png")
        if os.path.exists(fig3_path):
            st.image(fig3_path, caption="Fig. 3. Effective Recall vs. Architectural Window Size")
        st.metric(
            "Offline 1,000-Row Stream Benchmark",
            f"{stream_bm['mean_latency_s']} s mean",
            f"Median: {stream_bm['median_latency_s']} s",
        )

# --- TAB 4: FEATURE DRIVERS & TEMPORAL ---
with tab_eda:
    col_f, col_t = st.columns(2)
    with col_f:
        st.subheader("Random Forest Feature Importance (Gini)")
        fig1_path = os.path.join(FIG_DIR, "fig1_feature_importance.png")
        if os.path.exists(fig1_path):
            st.image(fig1_path, caption="Fig. 1. Relative Feature Importance at First Add-to-Cart")
        means_df = (
            pd.DataFrame(summary["feature_class_means"])
            .T.reset_index()
            .rename(columns={"index": "feature"})
        )
        st.dataframe(means_df, use_container_width=True, hide_index=True)

    with col_t:
        st.subheader("Empirical Temporal Abandonment Patterns")
        fig2_path = os.path.join(FIG_DIR, "fig2_temporal_patterns.png")
        if os.path.exists(fig2_path):
            st.image(fig2_path, caption="Fig. 2. Cart Abandonment Rate by Hour (UTC) and Day of Week")
        dow_df = pd.DataFrame(
            [
                {
                    "Day": d,
                    "Abandonment_Rate_Pct": summary["temporal_patterns"]["by_dow_pct"][str(i)],
                }
                for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            ]
        )
        st.dataframe(dow_df, use_container_width=True, hide_index=True)

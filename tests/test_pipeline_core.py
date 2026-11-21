import numpy as np
import pandas as pd
from src.pipeline_core import (
    compute_strict_prev_sessions,
    split_and_encode_features,
    compute_latency_simulation,
)


def test_strict_prev_sessions_excludes_overlapping_or_future_sessions():
    all_sess = pd.DataFrame({
        "session_id": [1, 2, 3],
        "visitorid": [10, 10, 10],
        "start_ts": [100, 500, 1000],
        "end_ts": [300, 900, 1200],
    })
    cart_sess = pd.DataFrame({
        "session_id": [1, 2, 3],
        "visitorid": [10, 10, 10],
        "cart_ts": [150, 600, 850],  # sess 3 cart_ts=850 occurs before sess 2 end_ts=900
    })
    prev = compute_strict_prev_sessions(all_sess, cart_sess)
    assert list(prev) == [0, 1, 1]


def test_split_and_encode_features_prevents_test_leakage():
    df = pd.DataFrame({
        "session_id": [1, 2, 3, 4, 5],
        "cart_ts": [10, 20, 30, 40, 50],
        "price": [100.0, 200.0, 300.0, np.nan, np.nan],
        "categoryid": [10, 10, 20, 20, 999],  # 999 only exists in test
        "n_events_before": [1, 2, 1, 3, 2],
        "n_views_before": [0, 1, 0, 2, 1],
        "n_unique_items": [1, 1, 1, 2, 1],
        "n_views_same_item": [0, 1, 0, 1, 1],
        "elapsed_min": [0.0, 1.0, 0.5, 2.0, 1.5],
        "hour": [10, 11, 12, 13, 14],
        "dow": [0, 1, 2, 3, 4],
        "prev_sessions": [0, 0, 1, 0, 2],
        "abandoned": [1, 0, 1, 1, 1],
    })
    train_df, test_df, meta = split_and_encode_features(df, train_ratio=0.8)
    assert len(train_df) == 4
    assert len(test_df) == 1
    assert meta["train_price_median"] == 200.0
    assert test_df["price"].iloc[0] == 200.0
    assert test_df["cat_freq"].iloc[0] == 0


def test_compute_latency_simulation_effective_recall():
    test_df = pd.DataFrame({
        "cart_ts": [100, 100, 100],
        "end_ts": [200, 200, 200],
        "abandoned": [1, 1, 0],
    })
    pred_te = np.array([1, 1, 0])
    # For window 3600s, decision_ts = 3600, whereas deadline = 200 + 1800 = 2000 (late)
    res_late = compute_latency_simulation(
        test_df, pred_te, infer_s=0.01, window_s=3600, label="Batch 1h", gap_s=1800
    )
    assert res_late["effective_recall"] == 0.0
    # For window 60s, decision_ts = 120 <= 2000 (on time)
    res_fast = compute_latency_simulation(
        test_df, pred_te, infer_s=0.01, window_s=60, label="NRT 1m", gap_s=1800
    )
    assert res_fast["effective_recall"] == 1.0


def test_inista_journal_abstract_and_format_compliance():
    import os
    import re

    journal_path = r"c:\Bafqi\Big Data\Draft_Jurnal_INISTA_Kelompok_15.md"
    assert os.path.exists(journal_path)
    with open(journal_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract abstract paragraph between '## ***Abstract***' and '**Keywords:**'
    m = re.search(r"## \*\*\*Abstract\*\*\*\s+(.*?)\s+\*\*Keywords:\*\*", text, re.DOTALL)
    assert m is not None
    abstract_body = m.group(1).strip().strip("*")
    words = abstract_body.split()
    assert len(words) <= 200, f"Abstract has {len(words)} words (exceeds 200 limit)"

    # Check keywords alphabetical order and count (4-8)
    km = re.search(r"\*\*Keywords:\*\*\s*\*(.*?)\*", text)
    assert km is not None
    keywords = [k.strip() for k in km.group(1).split(",")]
    assert 4 <= len(keywords) <= 8
    assert keywords == sorted(keywords, key=lambda s: s.lower())

    # Check Roman numeral headings and tables
    for section in [
        "## I. INTRODUCTION",
        "## II. LITERATURE REVIEW",
        "## III. RESEARCH METHOD",
        "## IV. RESULTS AND DISCUSSION",
        "## V. CONCLUSION",
        "TABLE I",
        "TABLE II",
        "TABLE III",
        "TABLE IV",
        "Fig. 1.",
        "Fig. 2.",
        "Fig. 3.",
    ]:
        assert section in text


def test_generated_docx_matches_jict_inista_template():
    import os
    import docx

    docx_path = r"c:\Bafqi\Big Data\Jurnal_JICT_INISTA_Kelompok_15.docx"
    assert os.path.exists(docx_path)
    doc = docx.Document(docx_path)

    # 1. Verify US Letter dimensions (215.9mm x 279.4mm) and 30mm margins
    for sec in doc.sections:
        assert abs(sec.page_width.mm - 215.9) < 0.5
        assert abs(sec.page_height.mm - 279.4) < 0.5
        assert abs(sec.top_margin.mm - 30.0) < 0.5
        assert abs(sec.bottom_margin.mm - 30.0) < 0.5
        assert abs(sec.left_margin.mm - 30.0) < 0.5
        assert abs(sec.right_margin.mm - 30.0) < 0.5

    # 2. Verify Title is 24 pt Times New Roman
    p_title = doc.paragraphs[0]
    assert "Comparative Analysis of Batch and Near Real-Time Processing" in p_title.text
    assert p_title.runs[0].font.size.pt == 24.0
    assert p_title.runs[0].font.name == "Times New Roman"

    # 3. Verify Authors are 11 pt Times New Roman
    p_auth = doc.paragraphs[1]
    assert "Arief Adhitya Ramadhan" in p_auth.text
    assert "Muhammad Bafqi" in p_auth.text
    assert "Zidan Dzulqarnain" in p_auth.text
    assert p_auth.runs[0].font.size.pt == 11.0

    # 4. Verify 4 Data Tables + 3 Equation Tables = 7 tables total
    assert len(doc.tables) == 7

    # 5. Verify 3 embedded figures (inline shapes)
    assert len(doc.inline_shapes) == 3


def test_dashboards_and_ipynb_exist_and_valid():
    import json
    import os

    html_path = r"c:\Bafqi\Big Data\dashboard.html"
    st_path = r"c:\Bafqi\Big Data\dashboard.py"
    ipynb_path = r"c:\Bafqi\Big Data\Project_Big_Data_Kelompok_15.ipynb"

    assert os.path.exists(html_path)
    assert os.path.exists(st_path)
    assert os.path.exists(ipynb_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_txt = f.read()
    assert "Early Cart Abandonment Telemetry" in html_txt
    assert "0.8574" in html_txt
    assert "0.7095" in html_txt
    assert "thresh-table-rf" in html_txt
    assert "thresh-table-lr" in html_txt
    # Verify WS2 6-Layer + Cross-Cutting Lambda Architecture alignment
    for token in ("tab-ws2", "Apache Kafka", "Debezium", "Snowflake/BigQuery", "Prometheus", "Grafana", "Power BI"):
        assert token in html_txt, f"Missing WS2 architecture token in dashboard.html: {token}"

    with open(ipynb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) >= 12


def test_score_single_session_and_crm_recommendation(tmp_path):
    from sklearn.ensemble import RandomForestClassifier
    from src.pipeline_core import FEATURES
    from src.serving import recommend_crm_action, score_single_session

    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.uniform(0, 10, size=(30, len(FEATURES))), columns=FEATURES)
    y = (X["prev_sessions"] < 5).astype(int)
    model = RandomForestClassifier(n_estimators=10, random_state=42).fit(X, y)

    session_input = {
        "n_events_before": 2,
        "n_views_before": 1,
        "n_unique_items": 1,
        "n_views_same_item": 1,
        "elapsed_min": 0.5,
        "hour": 9,
        "dow": 5,
        "price": 120000.0,
        "cat_freq": 250,
        "prev_sessions": 0,
    }
    res = score_single_session(model, session_input, threshold=0.5)
    assert 0.0 <= res["probability"] <= 1.0
    assert isinstance(res["predicted_abandoned"], bool)
    assert res["infer_ms"] >= 0.0
    assert res["crm_action"] in {
        "Organic Buyer (No Interrupt)",
        "Send Reminder / Pop-Up",
        "Offer 5% Flash Coupon",
        "High-Risk VIP Intervention",
    }

    action_low, level_low = recommend_crm_action(0.20, threshold=0.5)
    assert level_low == "Low"
    assert action_low == "Organic Buyer (No Interrupt)"
    action_high, level_high = recommend_crm_action(0.85, threshold=0.5)
    assert level_high == "Critical"


def test_atomic_microbatch_stream_write_and_consume(tmp_path):
    from sklearn.ensemble import RandomForestClassifier
    from src.pipeline_core import FEATURES
    from src.serving import write_stream_chunk, consume_new_stream_chunks

    rng = np.random.default_rng(7)
    X = pd.DataFrame(rng.uniform(0, 10, size=(20, len(FEATURES))), columns=FEATURES)
    y = np.array([0, 1] * 10)
    model = RandomForestClassifier(n_estimators=10, random_state=7).fit(X, y)

    stream_dir = tmp_path / "stream_in"
    tmp_dir = tmp_path / "stream_tmp"
    stream_dir.mkdir()
    tmp_dir.mkdir()

    chunk = X.iloc[:4].copy()
    chunk["session_id"] = [101, 102, 103, 104]
    chunk["visitorid"] = [1001, 1002, 1003, 1004]
    chunk["abandoned"] = [1, 0, 1, 1]

    written_path = write_stream_chunk(chunk, str(stream_dir), str(tmp_dir), chunk_idx=0)
    assert "chunk_0000.csv" in written_path

    processed = set()
    scored_df, newly_processed = consume_new_stream_chunks(
        model, str(stream_dir), processed, threshold=0.5
    )
    assert len(newly_processed) == 1
    assert len(scored_df) == 4
    assert "rf_prob" in scored_df.columns
    assert "e2e_latency_ms" in scored_df.columns
    assert (scored_df["e2e_latency_ms"] >= 0.0).all()

    # Re-polling without new files must return empty
    processed.update(newly_processed)
    scored_df_2, newly_2 = consume_new_stream_chunks(
        model, str(stream_dir), processed, threshold=0.5
    )
    assert len(newly_2) == 0
    assert scored_df_2.empty


def test_streamlit_dashboard_live_inference_end_to_end():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(r"c:\Bafqi\Big Data\dashboard.py", default_timeout=20)
    at.run()
    assert not at.exception, f"Dashboard raised exception on load: {at.exception}"

    # Verify single-session predictor renders both RF and LR side-by-side + WS2 Architecture tab metrics
    metric_labels = [m.label for m in at.metric]
    assert metric_labels.count("Abandonment Probability") == 2
    assert "Effective Recall" in metric_labels
    assert "Architecture Pattern" in metric_labels
    assert "Production Target" in metric_labels

    # Trigger +1 Live Micro-Batch button and verify real dual-model scoring ran cleanly
    step_btns = [b for b in at.button if b.label == "+1 Live Micro-Batch"]
    assert len(step_btns) == 1
    step_btns[0].click().run()
    assert not at.exception, f"Dashboard raised exception on +1 Live Micro-Batch: {at.exception}"

    metric_labels_after = [m.label for m in at.metric]
    assert metric_labels_after.count("Live Accuracy") == 2
    assert metric_labels_after.count("Mean E2E Latency") == 2
    live_hist = at.session_state["live_history"]
    assert not live_hist.empty
    assert "rf_prob" in live_hist.columns
    assert "lr_prob" in live_hist.columns


def test_dual_model_microbatch_stream_consume(tmp_path):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from src.pipeline_core import FEATURES
    from src.serving import write_stream_chunk, consume_new_stream_chunks

    rng = np.random.default_rng(11)
    X = pd.DataFrame(rng.uniform(0, 10, size=(30, len(FEATURES))), columns=FEATURES)
    y = (X["prev_sessions"] < 5).astype(int)
    rf = RandomForestClassifier(n_estimators=10, random_state=11).fit(X, y)
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=200)).fit(X, y)

    stream_dir = tmp_path / "stream_in"
    tmp_dir = tmp_path / "stream_tmp"
    stream_dir.mkdir()
    tmp_dir.mkdir()

    chunk = X.iloc[:5].copy()
    chunk["session_id"] = [1, 2, 3, 4, 5]
    chunk["visitorid"] = [10, 20, 30, 40, 50]
    chunk["abandoned"] = [1, 0, 1, 0, 1]
    write_stream_chunk(chunk, str(stream_dir), str(tmp_dir), chunk_idx=0)

    scored_df, new_files = consume_new_stream_chunks(
        rf, str(stream_dir), set(), threshold=0.5, lr_model=lr
    )
    assert len(new_files) == 1
    for col in ("rf_prob", "rf_pred", "rf_action", "rf_e2e_ms", "rf_infer_ms",
                "lr_prob", "lr_pred", "lr_action", "lr_e2e_ms", "lr_infer_ms"):
        assert col in scored_df.columns

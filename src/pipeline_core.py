import glob
import os
import platform
import subprocess
import sys
import numpy as np
import pandas as pd
import psutil
import sklearn
import matplotlib

DEFAULT_GAP_S = 30 * 60  # 1800 seconds (30 minutes)

FEATURES = [
    "n_events_before",
    "n_views_before",
    "n_unique_items",
    "n_views_same_item",
    "elapsed_min",
    "hour",
    "dow",
    "price_log",
    "cat_freq",
    "prev_sessions",
]


def get_hardware_specs() -> dict:
    cpu_name = platform.processor()
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
            text=True,
            timeout=5,
        ).strip()
        if out:
            cpu_name = out
    except Exception:
        pass

    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    return {
        "cpu_name": cpu_name,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_threads": psutil.cpu_count(logical=True),
        "ram_gb": ram_gb,
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python_version": sys.version.split()[0],
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "sklearn_version": sklearn.__version__,
        "matplotlib_version": matplotlib.__version__,
    }


def compute_strict_prev_sessions(
    all_sessions_df: pd.DataFrame, cart_sessions_df: pd.DataFrame
) -> pd.Series:
    """
    Strictly count past sessions of the same visitorid whose end_ts < current session's cart_ts.
    """
    sorted_all = all_sessions_df.sort_values(["visitorid", "end_ts"])
    end_ts_by_visitor = {
        vid: grp["end_ts"].to_numpy()
        for vid, grp in sorted_all.groupby("visitorid", sort=False)
    }

    counts = np.zeros(len(cart_sessions_df), dtype=np.int64)
    vids = cart_sessions_df["visitorid"].to_numpy()
    cart_ts_arr = cart_sessions_df["cart_ts"].to_numpy()

    for i in range(len(cart_sessions_df)):
        arr = end_ts_by_visitor.get(vids[i])
        if arr is not None:
            # searchsorted(side='left') returns count of elements strictly < cart_ts_arr[i]
            counts[i] = int(np.searchsorted(arr, cart_ts_arr[i], side="left"))

    return pd.Series(counts, index=cart_sessions_df.index, name="prev_sessions")


def split_and_encode_features(
    df: pd.DataFrame, train_ratio: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Sort chronologically by cart_ts, split into train (80%) and test (20%),
    and compute price median and category frequency strictly on train set.
    """
    ordered = df.sort_values("cart_ts").reset_index(drop=True)
    split_idx = int(len(ordered) * train_ratio)
    train_df = ordered.iloc[:split_idx].copy()
    test_df = ordered.iloc[split_idx:].copy()

    train_price_median = float(train_df["price"].median())
    if np.isnan(train_price_median):
        train_price_median = 0.0

    train_df["price"] = train_df["price"].fillna(train_price_median)
    test_df["price"] = test_df["price"].fillna(train_price_median)

    train_df["price_log"] = np.log1p(np.maximum(train_df["price"], 0.0))
    test_df["price_log"] = np.log1p(np.maximum(test_df["price"], 0.0))

    train_df["categoryid"] = train_df["categoryid"].fillna(-1)
    test_df["categoryid"] = test_df["categoryid"].fillna(-1)

    cat_counts = train_df["categoryid"].value_counts()
    train_df["cat_freq"] = train_df["categoryid"].map(cat_counts).fillna(0).astype(int)
    test_df["cat_freq"] = test_df["categoryid"].map(cat_counts).fillna(0).astype(int)

    meta = {
        "train_price_median": train_price_median,
        "train_size": len(train_df),
        "test_size": len(test_df),
        "cut_cart_ts": int(train_df["cart_ts"].max()) if len(train_df) > 0 else 0,
    }
    return train_df, test_df, meta


def compute_latency_simulation(
    test_df: pd.DataFrame,
    pred_te: np.ndarray,
    infer_s: float,
    window_s: int,
    label: str,
    gap_s: int = 1800,
) -> dict:
    """
    Simulate processing window delay and compute Effective Recall:
    Effective Recall = TP_detected_before_deadline / Total_Actual_Abandoned
    """
    cart_ts = test_df["cart_ts"].to_numpy(dtype=np.float64)
    end_ts = test_df["end_ts"].to_numpy(dtype=np.float64)
    actual_abandoned = (test_df["abandoned"].to_numpy() == 1)

    decision_ts = (np.floor(cart_ts / window_s) + 1.0) * window_s + infer_s
    latency = decision_ts - cart_ts
    deadline = end_ts + gap_s
    reachable = decision_ts <= deadline

    hit_before_deadline = (pred_te == 1) & actual_abandoned & reachable
    total_abandoned = int(actual_abandoned.sum())
    eff_recall = (
        float(hit_before_deadline.sum() / total_abandoned)
        if total_abandoned > 0
        else 0.0
    )

    return {
        "mode": label,
        "window_s": int(window_s),
        "mean_latency_s": float(np.mean(latency)),
        "median_latency_s": float(np.median(latency)),
        "pct_decided_before_deadline": float(np.mean(reachable) * 100.0),
        "effective_recall": eff_recall,
        "tp_on_time": int(hit_before_deadline.sum()),
        "total_actual_abandoned": total_abandoned,
    }


def prepare_retailrocket_splits(
    data_dir: str, gap_s: int = DEFAULT_GAP_S, train_ratio: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Load Retailrocket CSVs, run session-ization and strict anti-leakage
    feature extraction at first addtocart, and return chronological train/test splits + metadata.
    """
    events = pd.read_csv(os.path.join(data_dir, "events.csv"))
    events["ts"] = events["timestamp"] // 1000
    events = events.sort_values(["visitorid", "ts", "timestamp"]).reset_index(drop=True)
    events["row"] = np.arange(len(events))

    event_counts = {k: int(v) for k, v in events["event"].value_counts().to_dict().items()}
    total_events = int(len(events))
    unique_visitors = int(events["visitorid"].nunique())
    unique_items_events = int(events["itemid"].nunique())
    min_dt = pd.to_datetime(events["ts"].min(), unit="s", utc=True).strftime("%Y-%m-%d %H:%M:%S UTC")
    max_dt = pd.to_datetime(events["ts"].max(), unit="s", utc=True).strftime("%Y-%m-%d %H:%M:%S UTC")

    new_sess = (events["visitorid"] != events["visitorid"].shift()) | (events["ts"].diff() > gap_s)
    events["session_id"] = new_sess.cumsum()
    events["is_cart"] = (events["event"] == "addtocart").astype(int)
    events["is_tx"] = (events["event"] == "transaction").astype(int)
    events["is_view"] = (events["event"] == "view").astype(int)

    all_sess = (
        events.groupby("session_id")
        .agg(
            visitorid=("visitorid", "first"),
            start_ts=("ts", "min"),
            end_ts=("ts", "max"),
            has_cart=("is_cart", "max"),
            has_tx=("is_tx", "max"),
        )
        .reset_index()
    )
    total_all_sessions = int(len(all_sess))

    sess = all_sess[all_sess["has_cart"] == 1].copy().reset_index(drop=True)
    sess["abandoned"] = (sess["has_tx"] == 0).astype(int)

    carts = (
        events[events["is_cart"] == 1]
        .drop_duplicates("session_id", keep="first")[["session_id", "row", "ts", "itemid"]]
        .rename(columns={"row": "cart_row", "ts": "cart_ts", "itemid": "cart_item"})
    )
    sess = sess.merge(carts, on="session_id", how="inner")

    sess["prev_sessions"] = compute_strict_prev_sessions(all_sess, sess)
    naive_prev = all_sess.sort_values(["visitorid", "start_ts"]).groupby("visitorid").cumcount()
    all_sess["naive_prev"] = naive_prev
    sess = sess.merge(all_sess[["session_id", "naive_prev"]], on="session_id", how="left")
    prev_diff_count = int((sess["naive_prev"] != sess["prev_sessions"]).sum())

    m = events.merge(carts, on="session_id")
    m = m[m["row"] <= m["cart_row"]]

    pre = (
        m.groupby("session_id")
        .agg(
            n_events_before=("row", "size"),
            n_views_before=("is_view", "sum"),
            n_unique_items=("itemid", "nunique"),
        )
        .reset_index()
    )
    same_item = (
        m[(m["itemid"] == m["cart_item"]) & (m["is_view"] == 1)]
        .groupby("session_id")
        .size()
        .rename("n_views_same_item")
        .reset_index()
    )

    parts = []
    total_prop_rows = 0
    for f in sorted(glob.glob(os.path.join(data_dir, "item_properties_part*.csv"))):
        for ch in pd.read_csv(f, chunksize=2_000_000):
            total_prop_rows += len(ch)
            parts.append(ch[ch["property"].isin(["categoryid", "790"])])

    props = (
        pd.concat(parts, ignore_index=True)
        .sort_values("timestamp")
        .drop_duplicates(["itemid", "property"], keep="last")
    )
    item = props.pivot(index="itemid", columns="property", values="value").reset_index()
    item.columns.name = None
    item = item.rename(columns={"790": "price_raw"})
    item["price"] = pd.to_numeric(
        item["price_raw"].astype(str).str.lstrip("n"), errors="coerce"
    )
    item["categoryid"] = pd.to_numeric(item["categoryid"], errors="coerce")
    item = item[["itemid", "price", "categoryid"]]

    cat_tree = pd.read_csv(os.path.join(data_dir, "category_tree.csv"))

    data = (
        sess.merge(pre, on="session_id", how="left")
        .merge(same_item, on="session_id", how="left")
        .merge(item, left_on="cart_item", right_on="itemid", how="left")
    )
    data["n_views_same_item"] = data["n_views_same_item"].fillna(0)
    price_missing_rate = float(data["price"].isna().mean() * 100.0)
    cat_missing_rate = float(data["categoryid"].isna().mean() * 100.0)

    dt = pd.to_datetime(data["cart_ts"], unit="s", utc=True)
    data["hour"] = dt.dt.hour
    data["dow"] = dt.dt.day_of_week
    data["elapsed_min"] = (data["cart_ts"] - data["start_ts"]) / 60.0

    train_df, test_df, split_meta = split_and_encode_features(data, train_ratio=train_ratio)
    meta = {
        **split_meta,
        "total_events": total_events,
        "event_counts": event_counts,
        "unique_visitors": unique_visitors,
        "unique_items_in_events": unique_items_events,
        "total_item_property_rows": int(total_prop_rows),
        "unique_items_in_properties": int(item["itemid"].nunique()),
        "category_tree_rows": int(len(cat_tree)),
        "min_datetime_utc": min_dt,
        "max_datetime_utc": max_dt,
        "total_all_sessions": total_all_sessions,
        "price_missing_rate_pct": round(price_missing_rate, 2),
        "category_missing_rate_pct": round(cat_missing_rate, 2),
        "strict_prev_sessions_differed_rows": prev_diff_count,
    }
    return train_df, test_df, meta

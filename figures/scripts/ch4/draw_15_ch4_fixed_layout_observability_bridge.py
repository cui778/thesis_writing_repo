from __future__ import annotations

import re
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import (
    METRIC_COLORS,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
    style_heatmap_axes_plain,
)


"""
Scientific question:
Under the fixed Degree-N25 monitoring layout, does the spatial relationship
between the true defect node and the nearest monitoring node explain
localization difficulty?

Section: transition from Chapter 4 to Chapter 5
Figure role: bridge/backup figure. It links fixed-layout diagnosis limits to
the need for monitoring layout optimization.
"""


FIG_TAG = "15_CH4_fixed_layout_observability_bridge"
REPO_ROOT = Path(r"E:/11.16/thesis_writing_repo")
LOCAL_CH4_OUT = Path(r"E:/11.16/script2_new/chapter4_diagnosis_model/outputs")
SCRIPT2_ROOT = Path(r"E:/11.16/script2_new")
if str(SCRIPT2_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT2_ROOT))
from config import Config  # noqa: E402
from prep.inp_parser import UnifiedINPParser  # noqa: E402

TIER_FILE = LOCAL_CH4_OUT / "candidate_observability_tiers.csv"
PRED_DIR = LOCAL_CH4_OUT / "formal_ie_group"
OUT_DIR = ensure_out_dir(FIG_TAG)


def hop_label(hop: float) -> str:
    if hop <= 0:
        return "Direct\n0-hop"
    if hop == 1:
        return "Near\n1-hop"
    if hop == 2:
        return "Near\n2-hop"
    return "Far\n3+ hops"


def extract_seed(path: Path) -> int:
    m = re.search(r"_s(\d+)_event_predictions", path.name)
    return int(m.group(1)) if m else -1


def shortest_network_distances_to_monitors() -> pd.DataFrame:
    cfg = Config()
    network = UnifiedINPParser(cfg.inp_file).parse()
    links = network.links_df.copy()
    nodes = sorted(set(network.nodes_df["node_id"].astype(str)))
    adjacency: dict[str, list[tuple[str, float]]] = {node: [] for node in nodes}
    for row in links.itertuples(index=False):
        u = str(row.from_node)
        v = str(row.to_node)
        length = float(row.length_m) if float(row.length_m) > 0 else 1.0
        adjacency.setdefault(u, []).append((v, length))
        adjacency.setdefault(v, []).append((u, length))

    import heapq
    import json

    monitor_file = SCRIPT2_ROOT / "input_1" / "monitor_nodes_degree_N25.json"
    if not monitor_file.exists():
        monitor_file = Path(cfg.get_monitor_nodes_file("degree", 25))
    with open(monitor_file, "r", encoding="utf-8") as f:
        monitor_payload = json.load(f)
    if isinstance(monitor_payload, dict):
        monitors_raw = monitor_payload.get("monitor_nodes", [])
    else:
        monitors_raw = monitor_payload
    monitors = [str(v) for v in monitors_raw]
    if not monitors:
        raise ValueError(f"No monitor nodes found in {monitor_file}")

    dist = {node: np.inf for node in adjacency}
    nearest = {node: "" for node in adjacency}
    heap: list[tuple[float, str, str]] = []
    for monitor in monitors:
        if monitor not in dist:
            continue
        dist[monitor] = 0.0
        nearest[monitor] = monitor
        heapq.heappush(heap, (0.0, monitor, monitor))

    while heap:
        cur_dist, node, source = heapq.heappop(heap)
        if cur_dist > dist[node]:
            continue
        for nxt, weight in adjacency.get(node, []):
            cand = cur_dist + weight
            if cand < dist[nxt]:
                dist[nxt] = cand
                nearest[nxt] = source
                heapq.heappush(heap, (cand, nxt, source))

    out = pd.DataFrame(
        {
            "node_id": list(dist.keys()),
            "nearest_monitor_path_m": list(dist.values()),
            "nearest_monitor_by_length": [nearest[node] for node in dist.keys()],
        }
    )
    out.to_csv(OUT_DIR / f"{FIG_TAG}_nearest_monitor_path_distance.csv", index=False, encoding="utf-8-sig")
    return out


def load_data() -> pd.DataFrame:
    tiers = pd.read_csv(TIER_FILE, encoding="utf-8-sig")
    tiers = tiers[["node_id", "min_monitor_hop", "observability_tier", "nearest_monitors"]].copy()
    path_dist = shortest_network_distances_to_monitors()
    tiers = tiers.merge(path_dist, on="node_id", how="left")
    frames = []
    for path in sorted(PRED_DIR.glob("ch4_formal_ie_6h_s*_event_predictions.csv")):
        pred = pd.read_csv(path, encoding="utf-8-sig")
        pred["seed"] = extract_seed(path)
        frames.append(pred)
    if not frames:
        raise FileNotFoundError(f"No event prediction files found in {PRED_DIR}")
    df = pd.concat(frames, ignore_index=True)
    df = df[df["true_has_defect"] == 1].copy()
    df = df.merge(tiers, left_on="true_node_id", right_on="node_id", how="left")
    df["pred_true_node_rank"] = pd.to_numeric(df["pred_true_node_rank"], errors="coerce")
    df["reciprocal_rank"] = 1.0 / df["pred_true_node_rank"].clip(lower=1)
    df["hit_top1"] = (df["pred_true_node_rank"] <= 1).astype(int)
    df["hit_top3"] = (df["pred_true_node_rank"] <= 3).astype(int)
    df["hit_top5"] = (df["pred_true_node_rank"] <= 5).astype(int)
    df["hop_group"] = df["min_monitor_hop"].apply(hop_label)
    order = ["Direct\n0-hop", "Near\n1-hop", "Near\n2-hop", "Far\n3+ hops"]
    df["hop_group"] = pd.Categorical(df["hop_group"], categories=order, ordered=True)
    df["nearest_monitor_path_km"] = df["nearest_monitor_path_m"] / 1000.0
    df.to_csv(OUT_DIR / f"{FIG_TAG}_scenario_level.csv", index=False, encoding="utf-8-sig")
    return df


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("hop_group", observed=False)
        .agg(
            n_scenarios=("scenario_id", "count"),
            n_nodes=("true_node_id", "nunique"),
            mean_rr=("reciprocal_rank", "mean"),
            median_rank=("pred_true_node_rank", "median"),
            top1=("hit_top1", "mean"),
            top3=("hit_top3", "mean"),
            top5=("hit_top5", "mean"),
            mean_iou=("active_interval_iou", "mean"),
            mean_onset_error=("onset_error_hours", "mean"),
            mean_path_km=("nearest_monitor_path_km", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(OUT_DIR / f"{FIG_TAG}_hop_summary.csv", index=False, encoding="utf-8-sig")
    return summary


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300

    df = load_data()
    summary = build_summary(df)
    order = list(summary["hop_group"].astype(str))
    x_pos = np.arange(len(order))

    rng = np.random.default_rng(42)
    fig = plt.figure(figsize=(10.6, 5.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.18, 0.95])
    ax_scatter = fig.add_subplot(gs[0, 0])
    ax_hm = fig.add_subplot(gs[0, 1])

    for hit3, marker, color, label in [
        (1, "o", "#4E79A7", "Top-3 hit"),
        (0, "x", "#E15759", "Top-3 miss"),
    ]:
        sub = df[df["hit_top3"] == hit3]
        if sub.empty:
            continue
        xs = sub["hop_group"].cat.codes.to_numpy(dtype=float)
        xs = xs + rng.normal(0, 0.055, size=len(sub))
        ax_scatter.scatter(
            xs,
            sub["reciprocal_rank"],
            s=22 if hit3 else 30,
            marker=marker,
            color=color,
            alpha=0.56 if hit3 else 0.76,
            linewidths=0.9,
            label=label,
        )
    ax_scatter.plot(
        x_pos,
        summary["mean_rr"],
        color="#222222",
        marker="D",
        linewidth=2.0,
        markersize=5.5,
        label="Mean reciprocal rank",
        zorder=5,
    )
    for xx, row in zip(x_pos, summary.itertuples(index=False)):
        y_text = float(row.mean_rr) + 0.045
        if y_text > 0.985:
            y_text = float(row.mean_rr) - 0.080
        ax_scatter.text(
            xx,
            y_text,
            f"MRR {float(row.mean_rr):.2f}\nn={int(row.n_scenarios)}",
            ha="center",
            va="bottom" if y_text > float(row.mean_rr) else "top",
            fontsize=7.3,
            color="#222222",
        )
    ax_scatter.set_xticks(x_pos)
    ax_scatter.set_xticklabels(order)
    ax_scatter.set_ylim(0.0, 1.06)
    ax_scatter.set_ylabel("Reciprocal rank of true defect node")
    ax_scatter.set_xlabel("True defect node to nearest Degree-N25 monitor")
    ax_scatter.set_title("A. Fixed-layout observability vs localization rank", loc="left", fontweight="bold")
    style_axes_as_segments(ax_scatter, grid_axis="y")
    ax_scatter.legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0.0, -0.02), fontsize=7.4)

    heat_summary = summary[summary["hop_group"].astype(str) != "Near\n2-hop"].reset_index(drop=True)
    heat_cols = [("top1", "Top-1"), ("top3", "Top-3"), ("mean_rr", "MRR")]
    heat = heat_summary[[c for c, _ in heat_cols]].to_numpy(dtype=float)
    im = ax_hm.imshow(heat, cmap="YlGnBu", vmin=0.5, vmax=1.0, aspect="equal")
    ax_hm.set_xticks(np.arange(len(heat_cols)))
    ax_hm.set_xticklabels([label for _, label in heat_cols])
    y_labels = [
        f"{row.hop_group}\n{int(row.n_nodes)} nodes / {int(row.n_scenarios)} scenes"
        for row in heat_summary.itertuples(index=False)
    ]
    ax_hm.set_yticks(np.arange(len(heat_summary)))
    ax_hm.set_yticklabels(y_labels)
    ax_hm.set_title("B. Top-K score by monitor tier", loc="left", fontweight="bold")
    style_heatmap_axes_plain(ax_hm)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            color = "white" if heat[i, j] >= 0.70 else "#222222"
            ax_hm.text(j, i, f"{heat[i, j]:.2f}", ha="center", va="center", fontsize=8, color=color)
    cbar = fig.colorbar(im, ax=ax_hm, fraction=0.035, pad=0.03)
    cbar.set_ticks([0.5, 0.75, 1.0])
    cbar.set_label("Score")

    fig.suptitle("Fixed Degree-N25 layout: true-node observability and localization difficulty", x=0.01, ha="left", fontweight="bold")
    fig.text(
        0.01,
        -0.055,
        "Source: formal_ie_group event_predictions across seeds 7/42/123 + candidate_observability_tiers.csv | Tier is defined by the true defect node's nearest Degree-N25 monitor.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_true_node_monitor_hop_rank")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

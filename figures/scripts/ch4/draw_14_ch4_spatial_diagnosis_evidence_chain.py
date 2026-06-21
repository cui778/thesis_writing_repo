from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch4_style import (
    METRIC_COLORS,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
)


"""
Scientific question:
Where does the model place its window-level top candidates on the pipe network,
and how do success, temporal under-coverage, and spatial offset cases differ?

Section: 4.4.1, 4.4.2, 4.5.1
Figure role: spatial process-evidence figure; complements the time-profile
figure in draw_13.
"""


FIG_TAG = "14_CH4_spatial_diagnosis_evidence_chain"
OUT_DIR = ensure_out_dir(FIG_TAG)
TOPOLOGY_JSON = Path(r"E:/11.16/script2_new/input_1/parsed_inp_data.json")
WINDOW_PRED_FILE = Path(
    r"E:/11.16/script2_new/chapter4_diagnosis_model/outputs/formal_window_length/"
    r"ch4_formal_window_3h_s42_window_predictions.csv"
)
EVENT_PRED_FILE = Path(
    r"E:/11.16/script2_new/chapter4_diagnosis_model/outputs/formal_window_length/"
    r"ch4_formal_window_3h_s42_event_predictions.csv"
)

CASE_ORDER = [
    (316, "A  Success case\nstable temporal and spatial evidence"),
    (264, "B  Temporal under-coverage\ncorrect node, truncated interval"),
    (131, "C  Spatial offset\nactive detection, shifted top candidate"),
]


def load_topology() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = json.loads(TOPOLOGY_JSON.read_text(encoding="utf-8"))
    coords = pd.DataFrame.from_dict(data["coordinates"], orient="index").rename_axis("node_id").reset_index()
    coords["x_km"] = (coords["x"] - coords["x"].min()) / 1000.0
    coords["y_km"] = (coords["y"] - coords["y"].min()) / 1000.0
    conduits = (
        pd.DataFrame.from_dict(data["conduits"], orient="index")
        .rename_axis("link_id")
        .reset_index()[["link_id", "from_node", "to_node", "length"]]
    )
    return coords, conduits


def draw_network_base(ax: plt.Axes, coords: pd.DataFrame, conduits: pd.DataFrame) -> None:
    coord_map = coords.set_index("node_id")[["x_km", "y_km"]].to_dict("index")
    for _, row in conduits.iterrows():
        start = coord_map.get(row["from_node"])
        end = coord_map.get(row["to_node"])
        if start is None or end is None:
            continue
        ax.plot(
            [start["x_km"], end["x_km"]],
            [start["y_km"], end["y_km"]],
            color="#D3D8DE",
            linewidth=0.72,
            zorder=1,
        )
    ax.scatter(coords["x_km"], coords["y_km"], s=9, color="#EEF1F4", edgecolors="white", linewidths=0.25, zorder=2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def prepare_case_windows(windows: pd.DataFrame, event: pd.Series) -> pd.DataFrame:
    scene = windows[windows["scenario_id"].eq(int(event["scenario_id"]))].copy()
    for col in ["window_start_time", "window_end_time"]:
        scene[col] = pd.to_datetime(scene[col])
    true_start = pd.to_datetime(event["true_start"])
    scene["window_center"] = scene["window_start_time"] + (scene["window_end_time"] - scene["window_start_time"]) / 2
    scene["relative_hour"] = (scene["window_center"] - true_start).dt.total_seconds() / 3600.0
    scene["top_hit_true_node"] = scene["top_candidate_node"].astype(str).eq(str(event["true_node_id"]))
    return scene


def summarize_top_candidates(scene: pd.DataFrame, event: pd.Series) -> pd.DataFrame:
    active = scene[scene["pred_active"].eq(1)].copy()
    if active.empty:
        active = scene[scene["true_active"].eq(1)].copy()
    summary = (
        active.groupby("top_candidate_node")
        .agg(
            n_top_windows=("top_candidate_node", "size"),
            mean_relative_hour=("relative_hour", "mean"),
            max_p_active=("p_active", "max"),
            hit_true=("top_hit_true_node", "max"),
        )
        .reset_index()
        .rename(columns={"top_candidate_node": "node_id"})
    )
    summary["scenario_id"] = int(event["scenario_id"])
    summary["true_node_id"] = event["true_node_id"]
    summary["pred_top_node_id"] = event["pred_top_node_id"]
    return summary


def draw_case_map(
    ax: plt.Axes,
    coords: pd.DataFrame,
    conduits: pd.DataFrame,
    event: pd.Series,
    candidate_summary: pd.DataFrame,
    title: str,
    vmax_time: float,
) -> None:
    draw_network_base(ax, coords, conduits)
    merged = candidate_summary.merge(coords[["node_id", "x_km", "y_km"]], on="node_id", how="left").dropna(
        subset=["x_km", "y_km"]
    )
    if not merged.empty:
        sizes = 70 + 80 * np.sqrt(merged["n_top_windows"] / max(1, merged["n_top_windows"].max()))
        sc = ax.scatter(
            merged["x_km"],
            merged["y_km"],
            c=merged["mean_relative_hour"],
            cmap="YlGnBu",
            vmin=0,
            vmax=vmax_time,
            s=sizes,
            edgecolors="#222222",
            linewidths=0.55,
            zorder=5,
        )
    else:
        sc = None

    true_node = coords[coords["node_id"].eq(event["true_node_id"])]
    if not true_node.empty:
        ax.scatter(
            true_node["x_km"],
            true_node["y_km"],
            marker="*",
            s=250,
            color=METRIC_COLORS["temporal"],
            edgecolors="white",
            linewidths=0.8,
            zorder=7,
            label="True node",
        )
    pred_node = coords[coords["node_id"].eq(event["pred_top_node_id"])]
    if not pred_node.empty:
        pred_x = pred_node["x_km"].astype(float).to_numpy()
        pred_y = pred_node["y_km"].astype(float).to_numpy()
        if str(event["pred_top_node_id"]) == str(event["true_node_id"]):
            pred_x = pred_x + 0.05
            pred_y = pred_y - 0.05
        ax.scatter(
            pred_x,
            pred_y,
            marker="X",
            s=115,
            color=METRIC_COLORS["top1"],
            edgecolors="#222222",
            linewidths=0.6,
            zorder=8,
            label="Event top node",
        )

    ax.set_title(title, loc="left", fontweight="bold", fontsize=10.2, pad=4)
    text = (
        f"Scenario {int(event['scenario_id'])} ({event['defect_type']})\n"
        f"IoU={float(event['active_interval_iou']):.3f}, rank={float(event['pred_true_node_rank']):.0f}, "
        f"pred windows={int(event['n_pred_active_windows'])}"
    )
    ax.text(
        0.01,
        0.02,
        text,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.1,
        color=TEXT_GREY,
        bbox={"facecolor": "white", "edgecolor": "#DDDDDD", "alpha": 0.88, "pad": 3.0},
    )
    return sc


def draw_legend_panel(ax: plt.Axes) -> None:
    ax.axis("off")
    ax.text(0.0, 0.92, "How to read this figure", fontsize=11, fontweight="bold")
    ax.text(
        0.0,
        0.74,
        "Map markers are window-level top candidates during predicted-active windows.",
        fontsize=8.8,
        color=TEXT_GREY,
    )
    ax.scatter([0.05], [0.52], s=220, marker="*", color=METRIC_COLORS["temporal"], edgecolors="white")
    ax.text(0.12, 0.50, "true defect node", fontsize=9, va="center")
    ax.scatter([0.05], [0.34], s=115, marker="X", color=METRIC_COLORS["top1"], edgecolors="#222222")
    ax.text(0.12, 0.32, "event-level predicted top node", fontsize=9, va="center")
    ax.scatter([0.05], [0.16], s=140, color="#76B7B2", edgecolors="#222222")
    ax.text(0.12, 0.14, "node selected as window top candidate; size = frequency", fontsize=9, va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    coords, conduits = load_topology()
    windows = pd.read_csv(WINDOW_PRED_FILE, encoding="utf-8-sig")
    events = pd.read_csv(EVENT_PRED_FILE, encoding="utf-8-sig")
    event_map = events.set_index("scenario_id", drop=False)

    all_candidate_rows = []
    case_data = []
    for scenario_id, title in CASE_ORDER:
        event = event_map.loc[scenario_id]
        scene = prepare_case_windows(windows, event)
        summary = summarize_top_candidates(scene, event)
        all_candidate_rows.append(summary)
        case_data.append((event, summary, title))

    candidate_df = pd.concat(all_candidate_rows, ignore_index=True)
    vmax_time = max(1.0, float(candidate_df["mean_relative_hour"].quantile(0.95)))

    fig = plt.figure(figsize=(12.0, 5.9))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.28], left=0.04, right=0.93, top=0.83, bottom=0.15, wspace=0.08)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    legend_ax = fig.add_subplot(gs[1, :2])
    cbar_ax = fig.add_subplot(gs[1, 2])

    sc = None
    for ax, (event, summary, title) in zip(axes, case_data):
        sc = draw_case_map(ax, coords, conduits, event, summary, title, vmax_time)
    draw_legend_panel(legend_ax)
    if sc is not None:
        cbar = fig.colorbar(sc, cax=cbar_ax, orientation="horizontal")
        cbar.set_label("Mean relative hour of top-candidate selections")
        cbar.ax.tick_params(length=0)

    fig.suptitle(
        "14  Spatial diagnosis evidence chain: window-level top candidates on topology",
        x=0.01,
        y=0.965,
        ha="left",
        fontweight="bold",
        fontsize=12.5,
    )
    fig.text(
        0.01,
        0.02,
        "Source: formal_window_length 3h, seed42 window/event predictions. Candidate markers summarize predicted-active windows; no node-score logits are assumed.",
        color=TEXT_GREY,
        fontsize=8.2,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidate_df.to_csv(OUT_DIR / f"{FIG_TAG}_top_candidate_summary.csv", index=False, encoding="utf-8-sig")
    events[events["scenario_id"].isin([case[0] for case in CASE_ORDER])].to_csv(
        OUT_DIR / f"{FIG_TAG}_selected_events.csv", index=False, encoding="utf-8-sig"
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_top_candidate_topology")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

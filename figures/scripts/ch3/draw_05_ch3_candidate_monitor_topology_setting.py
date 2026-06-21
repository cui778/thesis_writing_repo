from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch3_style import (
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
)


OUT_TAG = "05_CH3_candidate_monitor_topology_setting"
BASENAME = "05_CH3_candidate_monitor_topology_setting"

TOPOLOGY_JSON = Path(r"E:/11.16/script2_new/input_1/parsed_inp_data.json")
CANDIDATE_JSON = Path(r"E:/11.16/script2_new/input_1/candidate_nodes_new.json")
MONITOR_JSON = Path(r"E:/11.16/script2_new/input_1/monitor_nodes_degree_N25.json")

COLORS = {
    "all": "#D5DAE0",
    "candidate": "#F28E2B",
    "monitor": "#4E79A7",
    "overlap": "#B07AA1",
    "pipe": "#CBD1D8",
}


def load_json(path: Path) -> dict:
    lowered = str(path).lower()
    if any(token in lowered for token in ("persistent", "fulltime", "legacy", "seedset10")):
        raise ValueError(f"Forbidden protocol token detected in path: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_topology() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = load_json(TOPOLOGY_JSON)
    coords = pd.DataFrame.from_dict(data["coordinates"], orient="index").rename_axis("node_id").reset_index()
    coords["x_km"] = (coords["x"] - coords["x"].min()) / 1000.0
    coords["y_km"] = (coords["y"] - coords["y"].min()) / 1000.0
    conduits = (
        pd.DataFrame.from_dict(data["conduits"], orient="index")
        .rename_axis("link_id")
        .reset_index()[["link_id", "from_node", "to_node", "length"]]
    )
    return coords, conduits


def load_node_sets() -> tuple[set[str], set[str], dict, dict]:
    candidate_data = load_json(CANDIDATE_JSON)
    monitor_data = load_json(MONITOR_JSON)
    candidates = set(candidate_data["candidate_nodes"])
    monitors = set(monitor_data["monitor_nodes"])
    if len(candidates) != int(candidate_data.get("k", len(candidates))):
        raise ValueError("Candidate node count does not match metadata k.")
    if len(monitors) != int(monitor_data.get("n", len(monitors))):
        raise ValueError("Monitor node count does not match metadata n.")
    return candidates, monitors, candidate_data, monitor_data


def classify_nodes(coords: pd.DataFrame, candidates: set[str], monitors: set[str]) -> pd.DataFrame:
    out = coords.copy()
    out["is_candidate"] = out["node_id"].isin(candidates)
    out["is_monitor"] = out["node_id"].isin(monitors)
    conditions = [
        out["is_candidate"] & out["is_monitor"],
        out["is_candidate"],
        out["is_monitor"],
    ]
    choices = ["overlap", "candidate", "monitor"]
    out["node_class"] = np.select(conditions, choices, default="all")
    return out


def draw_network_base(ax: plt.Axes, coords: pd.DataFrame, conduits: pd.DataFrame) -> None:
    coord_map = coords.set_index("node_id")[["x_km", "y_km"]].to_dict("index")
    for _, row in conduits.iterrows():
        start = coord_map.get(row["from_node"])
        end = coord_map.get(row["to_node"])
        if not start or not end:
            continue
        ax.plot(
            [start["x_km"], end["x_km"]],
            [start["y_km"], end["y_km"]],
            color=COLORS["pipe"],
            linewidth=0.8,
            zorder=1,
        )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_map(ax: plt.Axes, nodes: pd.DataFrame, conduits: pd.DataFrame) -> None:
    draw_network_base(ax, nodes, conduits)
    base = nodes[nodes["node_class"].eq("all")]
    ax.scatter(base["x_km"], base["y_km"], s=14, color=COLORS["all"], edgecolors="white", linewidths=0.25, zorder=2)

    candidate = nodes[nodes["node_class"].eq("candidate")]
    monitor = nodes[nodes["node_class"].eq("monitor")]
    overlap = nodes[nodes["node_class"].eq("overlap")]
    ax.scatter(
        candidate["x_km"],
        candidate["y_km"],
        s=42,
        color=COLORS["candidate"],
        edgecolors="white",
        linewidths=0.35,
        label="candidate only",
        zorder=3,
    )
    ax.scatter(
        monitor["x_km"],
        monitor["y_km"],
        s=54,
        marker="s",
        color=COLORS["monitor"],
        edgecolors="white",
        linewidths=0.35,
        label="monitor only",
        zorder=4,
    )
    ax.scatter(
        overlap["x_km"],
        overlap["y_km"],
        s=86,
        marker="D",
        color=COLORS["overlap"],
        edgecolors="#222222",
        linewidths=0.45,
        label="candidate + monitor",
        zorder=5,
    )

    label_nodes = overlap.copy()
    if len(label_nodes) < 8:
        label_nodes = pd.concat([label_nodes, candidate.head(8 - len(label_nodes))])
    for _, row in label_nodes.head(8).iterrows():
        ax.text(row["x_km"] + 0.035, row["y_km"] + 0.035, row["node_id"], fontsize=7.2, color="#1f2933")


def draw_single_layer(
    ax: plt.Axes,
    nodes: pd.DataFrame,
    conduits: pd.DataFrame,
    classes: list[str],
    title: str,
    color: str,
    marker: str = "o",
) -> None:
    draw_network_base(ax, nodes, conduits)
    base = nodes[~nodes["node_class"].isin(classes)]
    selected = nodes[nodes["node_class"].isin(classes)]
    ax.scatter(base["x_km"], base["y_km"], s=10, color="#E1E5EA", edgecolors="none", zorder=2)
    ax.scatter(
        selected["x_km"],
        selected["y_km"],
        s=48,
        marker=marker,
        color=color,
        edgecolors="white",
        linewidths=0.35,
        zorder=4,
    )
    ax.set_title(title, loc="left", fontsize=9.5, fontweight="bold")


def draw_summary(ax: plt.Axes, nodes: pd.DataFrame, candidate_data: dict, monitor_data: dict) -> None:
    counts = nodes["node_class"].value_counts().reindex(["candidate", "monitor", "overlap", "all"], fill_value=0)
    labels = ["Candidate only", "Monitor only", "Overlap", "Other nodes"]
    values = [counts["candidate"], counts["monitor"], counts["overlap"], counts["all"]]
    colors = [COLORS["candidate"], COLORS["monitor"], COLORS["overlap"], COLORS["all"]]
    y = np.arange(len(labels))
    ax.barh(y, values, color=colors, height=0.58)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Node count")
    ax.set_title("Node-set composition", loc="left", fontweight="bold")
    for i, value in enumerate(values):
        ax.text(value + 1.0, i, str(int(value)), va="center", fontsize=8.8)
    ax.set_xlim(0, max(values) * 1.22)
    style_axes_as_segments(ax, grid_axis="x")

    ax.text(
        0.0,
        -0.16,
        f"Candidate set: N={candidate_data.get('k', 'n/a')}; monitor layout: {monitor_data.get('strategy', 'n/a')} N={monitor_data.get('n', 'n/a')}.",
        transform=ax.transAxes,
        fontsize=8.4,
        color=TEXT_GREY,
        va="top",
    )


def write_outputs(out_dir: Path, nodes: pd.DataFrame, candidate_data: dict, monitor_data: dict) -> None:
    nodes[
        ["node_id", "x", "y", "x_km", "y_km", "is_candidate", "is_monitor", "node_class"]
    ].to_csv(out_dir / f"{BASENAME}_node_sets.csv", index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(
        [
            {"item": "all_nodes", "value": len(nodes)},
            {"item": "candidate_nodes", "value": int(nodes["is_candidate"].sum())},
            {"item": "monitor_nodes", "value": int(nodes["is_monitor"].sum())},
            {"item": "overlap_nodes", "value": int((nodes["is_candidate"] & nodes["is_monitor"]).sum())},
            {"item": "candidate_strategy", "value": candidate_data.get("strategy", "")},
            {"item": "monitor_strategy", "value": monitor_data.get("strategy", "")},
        ]
    )
    summary.to_csv(out_dir / f"{BASENAME}_summary.csv", index=False, encoding="utf-8-sig")


def draw(nodes: pd.DataFrame, conduits: pd.DataFrame, candidate_data: dict, monitor_data: dict, out_dir: Path) -> None:
    fig = plt.figure(figsize=(11.6, 7.0))
    gs = fig.add_gridspec(
        2,
        4,
        width_ratios=[1.35, 1.35, 0.95, 0.95],
        height_ratios=[1.0, 1.0],
        wspace=0.34,
        hspace=0.24,
        left=0.035,
        right=0.98,
        top=0.86,
        bottom=0.1,
    )
    ax_map = fig.add_subplot(gs[:, :2])
    ax_candidate = fig.add_subplot(gs[0, 2])
    ax_monitor = fig.add_subplot(gs[0, 3])
    ax_overlap = fig.add_subplot(gs[1, 2])
    ax_summary = fig.add_subplot(gs[1, 3])

    draw_map(ax_map, nodes, conduits)
    ax_map.set_title("A  Candidate defect nodes and Degree-N25 monitoring layout", loc="left", fontweight="bold")
    ax_map.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.0, -0.04), ncol=3, handletextpad=0.4)
    draw_single_layer(
        ax_candidate,
        nodes,
        conduits,
        ["candidate", "overlap"],
        "B  Candidate defect layer",
        COLORS["candidate"],
    )
    draw_single_layer(
        ax_monitor,
        nodes,
        conduits,
        ["monitor", "overlap"],
        "C  Monitoring layer",
        COLORS["monitor"],
        marker="s",
    )
    draw_single_layer(
        ax_overlap,
        nodes,
        conduits,
        ["overlap"],
        "D  Overlap layer",
        COLORS["overlap"],
        marker="D",
    )
    draw_summary(ax_summary, nodes, candidate_data, monitor_data)
    ax_summary.set_title("E  Node-set composition", loc="left", fontsize=9.5, fontweight="bold")

    fig.suptitle(
        "Experimental setting on sewer-network topology: defect candidates vs. monitoring nodes",
        x=0.02,
        y=0.97,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.018,
        "This setting figure should be read before defect-response examples: candidates define possible defect locations; monitors define observed nodes.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    save_figure(fig, out_dir, BASENAME)


def main() -> None:
    apply_style()
    coords, conduits = load_topology()
    candidates, monitors, candidate_data, monitor_data = load_node_sets()
    nodes = classify_nodes(coords, candidates, monitors)
    missing_candidates = candidates - set(coords["node_id"])
    missing_monitors = monitors - set(coords["node_id"])
    if missing_candidates or missing_monitors:
        raise ValueError(f"Missing coordinate nodes: candidates={missing_candidates}, monitors={missing_monitors}")
    out_dir = ensure_out_dir(OUT_TAG)
    write_outputs(out_dir, nodes, candidate_data, monitor_data)
    draw(nodes, conduits, candidate_data, monitor_data, out_dir)
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 08: spatial distribution of monitoring layouts.

Scientific question:
    Where do different layout strategies place sensors under different
    monitoring budgets, and do the selected nodes expand in different spatial
    patterns?

Source data:
    E:/11.16/script2_new/input_1/parsed_inp_data.json
    E:/11.16/script2_new/input_1/candidate_nodes_new.json
    E:/11.16/script2_new/chapter5_layout_optimization/outputs/layouts/*

Output directory:
    figures/ch5/generated_results/08_CH5_layout_spatial_distribution/

Generated figures:
    08_CH5_layout_spatial_distribution_budget_method_grid.png/.svg
    08_CH5_layout_spatial_distribution_N25_method_overview.png/.svg
    08_CH5_layout_spatial_distribution_budget_growth_path.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "figures" / "ch5" / "source_data").exists():
            return p
    raise FileNotFoundError("Cannot find thesis_writing_repo root.")


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = find_repo_root(SCRIPT_PATH)
WORKSPACE_ROOT = REPO_ROOT.parent

FIG_NO = "08"
FIG_TAG = f"{FIG_NO}_CH5_layout_spatial_distribution"

INPUT_DIR = WORKSPACE_ROOT / "script2_new" / "input_1"
LAYOUT_ROOT = (
    WORKSPACE_ROOT / "script2_new" / "chapter5_layout_optimization" / "outputs" / "layouts"
)

TOPOLOGY_JSON = INPUT_DIR / "parsed_inp_data.json"
CANDIDATE_JSON = INPUT_DIR / "candidate_nodes_new.json"

OUT_DIR = REPO_ROOT / "figures" / "ch5" / "generated_results" / FIG_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAVE_FORMATS = ["png", "svg"]

plt.rcParams["figure.dpi"] = 160
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"

METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

BUDGET_COLORS = {
    5: "#4E79A7",
    10: "#59A14F",
    15: "#F28E2B",
    20: "#E15759",
    25: "#B07AA1",
}

METHOD_LAYOUTS = {
    "Degree": {
        "dir": "degree",
        "file": "monitor_nodes_degree_N{budget}.json",
        "budgets": [5, 10, 15, 20, 25],
    },
    "Betweenness": {
        "dir": "betweenness",
        "file": "monitor_nodes_betweenness_N{budget}.json",
        "budgets": [5, 10, 15, 20, 25],
    },
    "Cand-Obs": {
        "dir": "candidate_observability",
        "file": "monitor_nodes_candidate_observability_N{budget}.json",
        "budgets": [5, 10, 15, 20, 25],
    },
    "Two-stage v1": {
        "dir": "two_stage_balanced_layout_v1",
        "file": "monitor_nodes_two_stage_balanced_layout_v1_N{budget}.json",
        "budgets": [5, 10, 15, 20, 25],
    },
    "Node-Feedback": {
        "dir": "learnable_layout_network_v0_scenario",
        "file": "monitor_nodes_learnable_layout_network_v0_scenario_N{budget}.json",
        "budgets": [25],
    },
    "Embedding-Guided": {
        "dir": "embedding_guided_clean_fixed",
        "file": "monitor_nodes_embedding_guided_clean_N{budget}.json",
        "budgets": [5, 10, 15, 20, 25],
    },
}

BUDGET_GRID_METHODS = ["Degree", "Betweenness", "Cand-Obs", "Two-stage v1", "Embedding-Guided"]
N25_METHODS = ["Degree", "Betweenness", "Cand-Obs", "Two-stage v1", "Node-Feedback", "Embedding-Guided"]
BUDGETS = [5, 10, 15, 20, 25]

COLORS = {
    "pipe": "#CCD3DB",
    "node": "#DDE2E8",
    "candidate": "#F5C48B",
    "candidate_edge": "#B96B18",
}


def load_json(path: Path) -> dict:
    lowered = str(path).lower()
    if any(token in lowered for token in ("persistent", "fulltime", "legacy", "seedset10")):
        raise ValueError(f"Forbidden protocol token detected in path: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_figure(fig: plt.Figure, basename: str) -> None:
    for ext in SAVE_FORMATS:
        fig.savefig(OUT_DIR / f"{basename}.{ext}", bbox_inches="tight", transparent=False)
    plt.close(fig)


def load_topology() -> Tuple[pd.DataFrame, pd.DataFrame]:
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


def load_candidates() -> set[str]:
    data = load_json(CANDIDATE_JSON)
    return set(str(node) for node in data["candidate_nodes"])


def layout_path(method: str, budget: int) -> Path:
    spec = METHOD_LAYOUTS[method]
    return LAYOUT_ROOT / spec["dir"] / spec["file"].format(budget=budget)


def load_layout(method: str, budget: int) -> Tuple[set[str], dict]:
    path = layout_path(method, budget)
    if not path.exists():
        return set(), {"missing": True, "path": str(path)}
    data = load_json(path)
    return set(str(node) for node in data["monitor_nodes"]), data


def draw_base_network(ax: plt.Axes, coords: pd.DataFrame, conduits: pd.DataFrame) -> None:
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
            linewidth=0.55,
            zorder=1,
        )
    ax.scatter(
        coords["x_km"],
        coords["y_km"],
        s=5.5,
        color=COLORS["node"],
        edgecolors="none",
        zorder=2,
    )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_candidates(ax: plt.Axes, coords: pd.DataFrame, candidates: set[str], size: float = 14.0) -> None:
    sub = coords[coords["node_id"].isin(candidates)]
    ax.scatter(
        sub["x_km"],
        sub["y_km"],
        s=size,
        color=COLORS["candidate"],
        edgecolors="white",
        linewidths=0.2,
        alpha=0.55,
        zorder=3,
    )


def draw_monitors(
    ax: plt.Axes,
    coords: pd.DataFrame,
    monitors: set[str],
    color: str,
    size: float = 34.0,
    marker: str = "o",
) -> None:
    sub = coords[coords["node_id"].isin(monitors)]
    ax.scatter(
        sub["x_km"],
        sub["y_km"],
        s=size,
        marker=marker,
        color=color,
        edgecolors="#222222",
        linewidths=0.35,
        zorder=5,
    )


def draw_single_layout(
    ax: plt.Axes,
    coords: pd.DataFrame,
    conduits: pd.DataFrame,
    candidates: set[str],
    monitors: set[str],
    method: str,
    budget: int,
    show_candidate: bool = True,
    title: bool = True,
) -> None:
    draw_base_network(ax, coords, conduits)
    if show_candidate:
        draw_candidates(ax, coords, candidates, size=10.0)
    draw_monitors(ax, coords, monitors, METHOD_COLORS[method], size=31.0 if budget <= 10 else 25.0)
    overlap = monitors & candidates
    if overlap:
        draw_monitors(ax, coords, overlap, METHOD_COLORS[method], size=43.0, marker="D")
    if title:
        ax.set_title(f"{method} | N={budget}", loc="left", fontsize=8.2, pad=2)


def collect_summary(candidates: set[str]) -> pd.DataFrame:
    rows = []
    for method, spec in METHOD_LAYOUTS.items():
        for budget in spec["budgets"]:
            monitors, data = load_layout(method, budget)
            if not monitors:
                continue
            metrics = data.get("layout_metrics", {})
            rows.append(
                {
                    "method": method,
                    "budget": budget,
                    "n_monitors": len(monitors),
                    "overlap_with_defect_nodes": len(monitors & candidates),
                    "layout_file": str(layout_path(method, budget)),
                    "direct": metrics.get("direct", np.nan),
                    "near": metrics.get("near", np.nan),
                    "far": metrics.get("far", np.nan),
                    "mean_hop": metrics.get("mean_hop", np.nan),
                    "max_hop": metrics.get("max_hop", np.nan),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / f"{FIG_TAG}_layout_spatial_summary.csv", index=False, encoding="utf-8-sig")
    return out


def draw_budget_method_grid(coords: pd.DataFrame, conduits: pd.DataFrame, candidates: set[str]) -> None:
    fig, axes = plt.subplots(
        len(BUDGET_GRID_METHODS),
        len(BUDGETS),
        figsize=(14.2, 12.4),
        sharex=True,
        sharey=True,
    )
    for r, method in enumerate(BUDGET_GRID_METHODS):
        for c, budget in enumerate(BUDGETS):
            ax = axes[r, c]
            monitors, _ = load_layout(method, budget)
            draw_single_layout(
                ax,
                coords,
                conduits,
                candidates,
                monitors,
                method,
                budget,
                show_candidate=True,
                title=False,
            )
            if r == 0:
                ax.text(
                    0.5,
                    1.12,
                    f"N={budget}",
                    transform=ax.transAxes,
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )
            if c == 0:
                ax.text(
                    -0.08,
                    0.5,
                    method,
                    transform=ax.transAxes,
                    rotation=90,
                    ha="right",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color=METHOD_COLORS[method],
                )
            ax.set_title("")

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["candidate"], markeredgecolor="white", markersize=6, label="Defect candidate"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#666666", markeredgecolor="#222222", markersize=6, label="Monitor"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#666666", markeredgecolor="#222222", markersize=6, label="Candidate + monitor"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("Spatial distribution of monitoring layouts across budgets", fontsize=14, y=0.995)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.955, bottom=0.055, wspace=0.03, hspace=0.05)
    save_figure(fig, f"{FIG_TAG}_budget_method_grid")


def draw_n25_overview(coords: pd.DataFrame, conduits: pd.DataFrame, candidates: set[str]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 7.7), sharex=True, sharey=True)
    for ax, method in zip(axes.ravel(), N25_METHODS):
        monitors, _ = load_layout(method, 25)
        draw_single_layout(ax, coords, conduits, candidates, monitors, method, 25, show_candidate=True)
        ax.set_title(method, loc="left", fontsize=10.5, fontweight="bold", color=METHOD_COLORS[method])
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["candidate"], markeredgecolor="white", markersize=6, label="Defect candidate"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#666666", markeredgecolor="#222222", markersize=6, label="Monitor"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#666666", markeredgecolor="#222222", markersize=6, label="Candidate + monitor"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("N=25 spatial comparison of six monitoring layout strategies", fontsize=14, y=0.985)
    fig.subplots_adjust(left=0.035, right=0.985, top=0.925, bottom=0.075, wspace=0.03, hspace=0.08)
    save_figure(fig, f"{FIG_TAG}_N25_method_overview")


def first_budget_by_node(method: str) -> Dict[str, int]:
    first: Dict[str, int] = {}
    for budget in BUDGETS:
        if budget not in METHOD_LAYOUTS[method]["budgets"]:
            continue
        monitors, _ = load_layout(method, budget)
        for node in monitors:
            first.setdefault(node, budget)
    return first


def draw_growth_path(coords: pd.DataFrame, conduits: pd.DataFrame, candidates: set[str]) -> None:
    methods = BUDGET_GRID_METHODS
    fig, axes = plt.subplots(1, len(methods), figsize=(15.0, 3.6), sharex=True, sharey=True)
    for ax, method in zip(axes, methods):
        draw_base_network(ax, coords, conduits)
        draw_candidates(ax, coords, candidates, size=9.0)
        first_map = first_budget_by_node(method)
        for budget in BUDGETS:
            nodes = {node for node, first_budget in first_map.items() if first_budget == budget}
            if not nodes:
                continue
            sub = coords[coords["node_id"].isin(nodes)]
            ax.scatter(
                sub["x_km"],
                sub["y_km"],
                s=37,
                color=BUDGET_COLORS[budget],
                edgecolors="#222222",
                linewidths=0.32,
                zorder=5 + budget,
            )
        ax.set_title(method, loc="left", fontsize=10, fontweight="bold", color=METHOD_COLORS[method])

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BUDGET_COLORS[b], markeredgecolor="#222222", markersize=6, label=f"first at N={b}")
        for b in BUDGETS
    ]
    fig.legend(handles=handles, frameon=False, ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.005))
    fig.suptitle("Budget growth path: when each selected monitoring node first appears", fontsize=13, y=0.99)
    fig.subplots_adjust(left=0.025, right=0.985, top=0.86, bottom=0.19, wspace=0.03)
    save_figure(fig, f"{FIG_TAG}_budget_growth_path")


def main() -> None:
    coords, conduits = load_topology()
    candidates = load_candidates()
    collect_summary(candidates)
    draw_budget_method_grid(coords, conduits, candidates)
    draw_n25_overview(coords, conduits, candidates)
    draw_growth_path(coords, conduits, candidates)
    print(f"[OK] wrote outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()

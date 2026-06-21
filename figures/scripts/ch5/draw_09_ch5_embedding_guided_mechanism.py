# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 09: Embedding-Guided mathematical mechanism.

This figure is a formal method-mechanism schematic, not a result chart.
It combines the real sewer-network topology with the mathematical logic of
Embedding-Guided monitor selection.

Outputs:
    09_CH5_embedding_guided_mechanism.png
    09_CH5_embedding_guided_mechanism.svg
    09_CH5_embedding_guided_mechanism_summary.csv
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
from matplotlib.lines import Line2D
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

FIG_NO = "09"
FIG_TAG = f"{FIG_NO}_CH5_embedding_guided_mechanism"

INPUT_DIR = WORKSPACE_ROOT / "script2_new" / "input_1"
TOPOLOGY_JSON = INPUT_DIR / "parsed_inp_data.json"
CANDIDATE_JSON = INPUT_DIR / "candidate_nodes_new.json"
EG_LAYOUT_JSON = (
    WORKSPACE_ROOT
    / "script2_new"
    / "chapter5_layout_optimization"
    / "outputs"
    / "layouts"
    / "embedding_guided_clean_fixed"
    / "monitor_nodes_embedding_guided_clean_N25.json"
)

OUT_DIR = REPO_ROOT / "figures" / "ch5" / "generated_results" / FIG_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAVE_FORMATS = ["png", "svg"]

plt.rcParams["figure.dpi"] = 160
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"

COLORS = {
    "pipe": "#CBD1D8",
    "node": "#DDE2E8",
    "candidate": "#F28E2B",
    "monitor": "#76B7B2",
    "monitor_edge": "#1F5F5B",
    "coverage": "#E15759",
    "model": "#B07AA1",
    "text": "#222222",
    "muted": "#667085",
    "box": "#F7F9FB",
    "box_edge": "#D9E0E8",
    "formula": "#F0F6F5",
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
    layout_data = load_json(EG_LAYOUT_JSON)
    return (
        set(str(x) for x in candidate_data["candidate_nodes"]),
        set(str(x) for x in layout_data["monitor_nodes"]),
        candidate_data,
        layout_data,
    )


def draw_network(ax: plt.Axes, coords: pd.DataFrame, conduits: pd.DataFrame, candidates: set[str], monitors: set[str]) -> None:
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
            linewidth=0.75,
            zorder=1,
        )

    ax.scatter(coords["x_km"], coords["y_km"], s=9, color=COLORS["node"], edgecolors="none", zorder=2)

    cand = coords[coords["node_id"].isin(candidates)]
    mon = coords[coords["node_id"].isin(monitors)]
    overlap = coords[coords["node_id"].isin(candidates & monitors)]

    ax.scatter(
        cand["x_km"],
        cand["y_km"],
        s=26,
        color=COLORS["candidate"],
        edgecolors="white",
        linewidths=0.25,
        alpha=0.55,
        zorder=3,
    )
    ax.scatter(
        mon["x_km"],
        mon["y_km"],
        s=54,
        color=COLORS["monitor"],
        edgecolors=COLORS["monitor_edge"],
        linewidths=0.55,
        zorder=4,
    )
    if not overlap.empty:
        ax.scatter(
            overlap["x_km"],
            overlap["y_km"],
            s=76,
            marker="D",
            color=COLORS["monitor"],
            edgecolors="#222222",
            linewidths=0.65,
            zorder=5,
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("真实管网拓扑与 E-G N=25 监测节点", loc="left", fontsize=12, fontweight="bold", color=COLORS["text"])


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    wh: tuple[float, float],
    title: str,
    body: Iterable[str],
    facecolor: str = "#F7F9FB",
    edgecolor: str = "#D9E0E8",
    title_color: str = "#222222",
) -> FancyBboxPatch:
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.1,
        transform=ax.transAxes,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x + 0.025, y + h - 0.052, title, transform=ax.transAxes, fontsize=10.8, fontweight="bold", color=title_color, va="top")
    yy = y + h - 0.118
    for line in body:
        ax.text(x + 0.03, yy, line, transform=ax.transAxes, fontsize=8.9, color=COLORS["text"], va="top")
        yy -= 0.048
    return patch


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#667085") -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        transform=ax.transAxes,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.2,
        color=color,
        shrinkA=3,
        shrinkB=3,
        zorder=3,
    )
    ax.add_patch(arrow)


def draw_embedding_mini(ax: plt.Axes, origin: tuple[float, float]) -> None:
    ox, oy = origin
    pts = [
        (ox, oy, COLORS["monitor"]),
        (ox + 0.045, oy + 0.03, COLORS["monitor"]),
        (ox + 0.08, oy - 0.02, COLORS["candidate"]),
        (ox + 0.14, oy + 0.04, COLORS["model"]),
        (ox + 0.18, oy - 0.01, COLORS["model"]),
        (ox + 0.22, oy + 0.035, COLORS["monitor"]),
    ]
    for x, y, c in pts:
        ax.add_patch(Circle((x, y), 0.012, transform=ax.transAxes, facecolor=c, edgecolor="white", linewidth=0.4, zorder=4))
    ax.plot([p[0] for p in pts[:3]], [p[1] for p in pts[:3]], transform=ax.transAxes, color=COLORS["monitor"], alpha=0.45, linewidth=1.0)
    ax.plot([p[0] for p in pts[3:]], [p[1] for p in pts[3:]], transform=ax.transAxes, color=COLORS["model"], alpha=0.45, linewidth=1.0)


def draw_score_bars(ax: plt.Axes, origin: tuple[float, float]) -> None:
    ox, oy = origin
    widths = [0.15, 0.11, 0.08]
    for i, width in enumerate(widths):
        y = oy - i * 0.038
        ax.add_patch(FancyBboxPatch((ox, y), width, 0.024, boxstyle="round,pad=0.002,rounding_size=0.006", facecolor=COLORS["monitor"], edgecolor="none", transform=ax.transAxes, alpha=0.78))


def draw_mechanism(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.0, 0.99, "Embedding-Guided 监测布局的数学机理", transform=ax.transAxes, fontsize=15, fontweight="bold", color=COLORS["text"], va="top")
    ax.text(
        0.0,
        0.94,
        "核心思想：用诊断模型学习到的节点响应表征定义监测节点价值，而不是只用拓扑距离定义覆盖。",
        transform=ax.transAxes,
        fontsize=9.5,
        color=COLORS["muted"],
        va="top",
    )

    add_box(
        ax,
        (0.02, 0.635),
        (0.44, 0.225),
        "A  诊断表征提取",
        [
            "G=(V,E),  C 为候选缺陷节点",
            "Z in R^{|V| x d},  z_v 为节点表征",
            "z_v = f_theta(x_S(t), G, mask, prior)",
        ],
        facecolor="#F7F4FA",
        edgecolor="#DECDE6",
        title_color=COLORS["model"],
    )
    draw_embedding_mini(ax, (0.31, 0.725))

    add_box(
        ax,
        (0.54, 0.635),
        (0.42, 0.225),
        "B  节点信息价值评分",
        [
            "q(v)= alpha r(v)+ beta u(v)+ gamma c(v)",
            "r(v)：定位贡献   u(v)：响应可观测性",
            "c(v)：候选相关性",
        ],
        facecolor=COLORS["formula"],
        edgecolor="#C7E1DE",
        title_color=COLORS["monitor_edge"],
    )
    draw_score_bars(ax, (0.84, 0.76))
    add_arrow(ax, (0.465, 0.748), (0.535, 0.748), color=COLORS["monitor_edge"])

    add_box(
        ax,
        (0.02, 0.355),
        (0.44, 0.22),
        "C  冗余抑制与互补选择",
        [
            "sim(i,j) = cos(z_i, z_j)",
            "penalty = sum sim(i,j)",
            "避免重复观测相似响应",
        ],
        facecolor="#FFF7ED",
        edgecolor="#F5D2A8",
        title_color=COLORS["candidate"],
    )
    draw_embedding_mini(ax, (0.31, 0.445))

    add_box(
        ax,
        (0.54, 0.355),
        (0.42, 0.22),
        "D  组合优化选点",
        [
            "S* = argmax_{|S|=N}",
            "sum q(v) - lambda sum sim(i,j)",
            "预算约束 |S|=N",
        ],
        facecolor="#F0F8F8",
        edgecolor="#C7E1DE",
        title_color=COLORS["monitor_edge"],
    )
    add_arrow(ax, (0.24, 0.635), (0.24, 0.58), color=COLORS["candidate"])
    add_arrow(ax, (0.465, 0.465), (0.535, 0.465), color=COLORS["monitor_edge"])

    add_box(
        ax,
        (0.02, 0.145),
        (0.44, 0.145),
        "结构覆盖导向",
        [
            "目标：min dist(c,S),  c in C",
            "逻辑：靠近缺陷候选节点",
        ],
        facecolor="#FFF1F1",
        edgecolor="#F3B8B8",
        title_color=COLORS["coverage"],
    )
    add_box(
        ax,
        (0.54, 0.145),
        (0.42, 0.145),
        "诊断表征导向 E-G",
        [
            "目标：max information(z_v) - redundancy(z_i,z_j)",
            "逻辑：选择诊断信息节点",
        ],
        facecolor="#EFF9F8",
        edgecolor="#B8DFDA",
        title_color=COLORS["monitor_edge"],
    )
    ax.text(
        0.5,
        0.052,
        "方法创新：将响应表征转化为节点价值函数，并在预算约束下选择互补信息节点",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color=COLORS["text"],
        bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.08", facecolor="#FFFFFF", edgecolor="#D9E0E8"),
    )


def write_summary(candidates: set[str], monitors: set[str], layout_data: dict) -> None:
    metrics = layout_data.get("layout_metrics", {})
    rows = [
        {"item": "candidate_nodes", "value": len(candidates)},
        {"item": "eg_monitors_N25", "value": len(monitors)},
        {"item": "candidate_monitor_overlap", "value": len(candidates & monitors)},
        {"item": "direct", "value": metrics.get("direct", "")},
        {"item": "near", "value": metrics.get("near", "")},
        {"item": "far", "value": metrics.get("far", "")},
        {"item": "mean_hop", "value": metrics.get("mean_hop", "")},
        {"item": "layout_file", "value": str(EG_LAYOUT_JSON)},
    ]
    pd.DataFrame(rows).to_csv(OUT_DIR / f"{FIG_TAG}_summary.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    coords, conduits = load_topology()
    candidates, monitors, _, layout_data = load_node_sets()
    write_summary(candidates, monitors, layout_data)

    fig = plt.figure(figsize=(15.8, 8.9))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[0.92, 1.38],
        left=0.035,
        right=0.985,
        top=0.94,
        bottom=0.075,
        wspace=0.08,
    )
    ax_net = fig.add_subplot(gs[0, 0])
    ax_mech = fig.add_subplot(gs[0, 1])

    draw_network(ax_net, coords, conduits, candidates, monitors)
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["candidate"], markeredgecolor="white", markersize=7, label="候选缺陷节点 C"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["monitor"], markeredgecolor=COLORS["monitor_edge"], markersize=7, label="E-G 监测节点 S*"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=COLORS["monitor"], markeredgecolor="#222222", markersize=7, label="候选+监测重合"),
    ]
    ax_net.legend(handles=handles, frameon=False, loc="lower left", bbox_to_anchor=(0.0, -0.03), fontsize=9.2)
    ax_net.text(
        0.0,
        -0.085,
        "真实管网底图用于说明 E-G 最终选择的空间节点；右侧公式说明其方法层选点逻辑。",
        transform=ax_net.transAxes,
        fontsize=9.2,
        color=COLORS["muted"],
        va="top",
    )

    draw_mechanism(ax_mech)

    save_figure(fig, FIG_TAG)
    print(f"[OK] wrote {OUT_DIR}")


if __name__ == "__main__":
    main()

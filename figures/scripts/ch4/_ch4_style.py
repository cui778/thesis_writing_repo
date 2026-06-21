from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(r"E:/11.16/thesis_writing_repo")
CH4_SOURCE = REPO_ROOT / "figures" / "ch4" / "source_data"
CH4_OUTPUT = REPO_ROOT / "figures" / "ch4" / "generated_results"

AXIS_COLOR = "#222222"
SPINE_WIDTH = 0.8
GRID_COLOR = "#B9C0C8"
TEXT_GREY = "#666666"

METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

METRIC_COLORS = {
    "mrr": "#4E79A7",
    "top1": "#F28E2B",
    "top3": "#59A14F",
    "top5": "#E15759",
    "event_top1": "#B07AA1",
    "event_top3": "#76B7B2",
    "event_top5": "#EDC948",
    "scene_f1": "#9C755F",
    "event": "#76B7B2",
    "temporal": "#E45756",
    "control": "#59A14F",
    "fpr": "#E15759",
    "gap": "#B07AA1",
    "mean_hop": "#76B7B2",
    "far": "#E15759",
}

MODEL_ORDER = [
    "gru_only",
    "gru_gcn",
    "lstm_graphsage_edge",
    "hydraulic_inverse",
    "hydraulic_inverse_deepattn",
]

MODEL_LABELS = {
    "gru_only": "GRU",
    "gru_gcn": "GRU-GCN",
    "lstm_graphsage_edge": "LSTM-GraphSAGE",
    "hydraulic_inverse": "Hydraulic-Inverse",
    "hydraulic_inverse_deepattn": "Hydraulic-Inverse\nDeepAttn",
}


def apply_style() -> None:
    plt.rcParams["figure.dpi"] = 160
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["font.size"] = 9.5
    plt.rcParams["axes.titlesize"] = 11
    plt.rcParams["axes.labelsize"] = 9.5
    plt.rcParams["xtick.labelsize"] = 8.5
    plt.rcParams["ytick.labelsize"] = 8.5
    plt.rcParams["legend.fontsize"] = 8.5
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def style_axes(ax: plt.Axes, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)
    ax.tick_params(axis="both", colors=AXIS_COLOR, length=3, width=0.8)
    if grid_axis:
        ax.grid(axis=grid_axis, linestyle="--", linewidth=0.5, alpha=0.32, color=GRID_COLOR)


def style_axes_as_segments(ax: plt.Axes, grid_axis: str = "y") -> None:
    style_axes(ax, grid_axis=grid_axis)
    try:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.spines["bottom"].set_bounds(xmin, xmax)
        ax.spines["left"].set_bounds(ymin, ymax)
    except Exception:
        pass


def style_heatmap_axes(ax: plt.Axes, n_rows: int, n_cols: int) -> None:
    style_axes(ax, grid_axis="")
    ax.set_xticks([i - 0.5 for i in range(n_cols + 1)], minor=True)
    ax.set_yticks([i - 0.5 for i in range(n_rows + 1)], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)


def style_heatmap_axes_plain(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)
    ax.tick_params(axis="both", which="both", length=0, colors=AXIS_COLOR)
    ax.grid(False)


def ensure_out_dir(tag: str) -> Path:
    out_dir = CH4_OUTPUT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_figure(fig: plt.Figure, out_dir: Path, basename: str) -> None:
    fig.savefig(out_dir / f"{basename}.png", bbox_inches="tight")
    fig.savefig(out_dir / f"{basename}.svg", bbox_inches="tight")
    plt.close(fig)

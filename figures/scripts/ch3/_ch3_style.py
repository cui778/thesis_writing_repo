from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(r"E:/11.16/thesis_writing_repo")
CH3_SOURCE = REPO_ROOT / "figures" / "ch3" / "source_data"
CH3_OUTPUT = REPO_ROOT / "figures" / "ch3" / "generated_results"

FORMAL_DATASET_DIR = Path(r"E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1")
FORMAL_MANIFEST = FORMAL_DATASET_DIR / "dataset_manifest.json"
FORMAL_SCENARIO_SUMMARY = FORMAL_DATASET_DIR / "scenario_summary.csv"
FORMAL_RESIDUAL_PARQUET = FORMAL_DATASET_DIR / "node_timeseries_with_residuals.parquet"
FORMAL_DEFECT_MATRIX = Path(
    r"E:/11.16/script2_new/input_1/defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv"
)

AXIS_COLOR = "#222222"
SPINE_WIDTH = 0.8
GRID_COLOR = "#B9C0C8"
TEXT_GREY = "#666666"

TYPE_COLORS = {
    "I": "#4E79A7",
    "E": "#E15759",
    "Normal": "#59A14F",
    "Baseline": "#9C755F",
}

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
    out_dir = CH3_OUTPUT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_figure(fig: plt.Figure, out_dir: Path, basename: str) -> None:
    fig.savefig(out_dir / f"{basename}.png", bbox_inches="tight")
    fig.savefig(out_dir / f"{basename}.svg", bbox_inches="tight")
    plt.close(fig)

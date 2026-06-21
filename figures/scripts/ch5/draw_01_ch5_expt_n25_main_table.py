# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 01: N25 main layout comparison.

Source data:
    figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv

Script location:
    figures/scripts/ch5/draw_01_ch5_expt_n25_main_table.py

Output directory:
    figures/ch5/generated_results/01_CH5_EXPT_N25/

Generated figures:
    01_CH5_EXPT_N25_mrr_forest_plot.png/.svg
    01_CH5_EXPT_N25_performance_fingerprint_heatmap.png/.svg
    01_CH5_EXPT_N25_family_main_metrics_point_errorbar.png/.svg

Notes:
    - No PDF output.
    - Main table: 6 layout methods × 3 diagnosis seeds.
    - Mean ± std uses sample standard deviation, ddof=1.
    - Heatmap is fixed to 6 × 6 by removing Top-5 from the fingerprint view.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 0. Path config
# ============================================================

def find_repo_root(start: Path) -> Path:
    """Find thesis_writing_repo root by walking upward."""
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "figures" / "ch5" / "source_data").exists():
            return p
    raise FileNotFoundError(
        "Cannot find repository root. Run this script inside thesis_writing_repo "
        "or check whether figures/ch5/source_data exists."
    )


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = find_repo_root(SCRIPT_PATH)

FIG_NO = "01"
FIG_TAG = f"{FIG_NO}_CH5_EXPT_N25"

DATA_FILE = (
    REPO_ROOT
    / "figures"
    / "ch5"
    / "source_data"
    / "CH5-EXPT_fixed_protocol_N25_main_table.csv"
)

OUT_DIR = (
    REPO_ROOT
    / "figures"
    / "ch5"
    / "generated_results"
    / FIG_TAG
)
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. Plot config
# ============================================================

SAVE_FORMATS = ["png", "svg"]

plt.rcParams["figure.dpi"] = 160
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"

# Fixed method palette: colorblind-friendly and consistent across CH5.
METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

# Fixed metric palette.
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

HEATMAP_CMAP = "YlGnBu"

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9

METHOD_ORDER = [
    "Degree",
    "Betweenness",
    "Cand-Obs",
    "Two-stage v1",
    "Node-Feedback",
    "Embedding-Guided",
]

METHOD_RENAME = {
    "Degree": "Degree",
    "Betweenness": "Betweenness",
    "Cand-Obs": "Cand-Obs",
    "Two-stage v1": "Two-stage v1",
    "Node-Feedback": "Node-Feedback",
    "Node-Feedback (val)": "Node-Feedback",
    "Embedding-Guided": "Embedding-Guided",
    "Embedding-Guided-new": "Embedding-Guided",
}

METHOD_FAMILY = {
    "Degree": "Topology rule",
    "Betweenness": "Topology rule",
    "Cand-Obs": "Coverage-oriented",
    "Two-stage v1": "Coverage-oriented",
    "Node-Feedback": "Diagnostic-driven",
    "Embedding-Guided": "Diagnostic-driven",
}

FAMILY_SPANS_X = [
    (-0.5, 1.5, "Topology rule"),
    (1.5, 3.5, "Coverage-oriented"),
    (3.5, 5.5, "Diagnostic-driven"),
]

FAMILY_SPANS_Y = [
    ("Topology rule", ["Degree", "Betweenness"]),
    ("Coverage-oriented", ["Cand-Obs", "Two-stage v1"]),
    ("Diagnostic-driven", ["Node-Feedback", "Embedding-Guided"]),
]

# For summary CSV, retain all important metrics.
SUMMARY_METRICS = [
    "mrr",
    "top1",
    "top3",
    "top5",
    "event_top1",
    "event_top3",
    "event_top5",
    "scene_f1",
]

# Fingerprint heatmap is intentionally 6 × 6.
FINGERPRINT_METRICS = [
    "mrr",
    "top1",
    "top3",
    "event_top1",
    "event_top3",
    "scene_f1",
]

FAMILY_POINT_METRICS = ["mrr", "top1", "top3", "top5"]

METRIC_LABELS = {
    "mrr": "MRR",
    "top1": "Top-1",
    "top3": "Top-3",
    "top5": "Top-5",
    "event_top1": "Event Top-1",
    "event_top3": "Event Top-3",
    "event_top5": "Event Top-5",
    "scene_f1": "Scene F1",
}

METRIC_MARKERS = {
    "mrr": "o",
    "top1": "s",
    "top3": "^",
    "top5": "D",
    "event_top1": "P",
    "event_top3": "X",
    "event_top5": "*",
    "scene_f1": "v",
}

METRIC_OFFSETS = {
    "mrr": -0.24,
    "top1": -0.08,
    "top3": 0.08,
    "top5": 0.24,
}


# ============================================================
# 2. Utility functions
# ============================================================

def save_figure(fig: plt.Figure, basename: str) -> None:
    """Save as PNG and SVG only."""
    for ext in SAVE_FORMATS:
        fig.savefig(
            OUT_DIR / f"{basename}.{ext}",
            bbox_inches="tight",
            transparent=False,
        )
    plt.close(fig)


def require_columns(df: pd.DataFrame, columns: set[str]) -> None:
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def method_mean_std(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Return method-level mean and sample std."""
    g = df.groupby("method_clean", sort=False)[metrics]
    mean = g.mean().reindex(METHOD_ORDER)
    std = g.std(ddof=1).reindex(METHOD_ORDER)

    rows = []
    for method in METHOD_ORDER:
        row = {
            "method": method,
            "family": METHOD_FAMILY[method],
        }
        for metric in metrics:
            row[f"{metric}_mean"] = mean.loc[method, metric]
            row[f"{metric}_std"] = std.loc[method, metric]
        rows.append(row)

    return pd.DataFrame(rows)

def style_axes_as_segments(
    ax: plt.Axes,
    use_full_xlim: bool = True,
    use_full_ylim: bool = True,
) -> None:
    """
    Use clean axis line segments along the full plotting area.

    Difference from the previous version:
    - Bottom spine spans the full x-axis plotting range.
    - Left spine spans the full y-axis plotting range.
    - It no longer stops at the first/last tick.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)

    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)

    ax.tick_params(
        axis="both",
        which="both",
        direction="out",
        width=TICK_WIDTH,
        length=3.5,
        color=AXIS_COLOR,
    )

    if use_full_xlim:
        x0, x1 = ax.get_xlim()
        ax.spines["bottom"].set_bounds(x0, x1)

    if use_full_ylim:
        y0, y1 = ax.get_ylim()
        ax.spines["left"].set_bounds(y0, y1)
        
def style_heatmap_axes(ax: plt.Axes, n_rows: int, n_cols: int) -> None:
    """
    Heatmap axes without cell gaps, cell borders, or tick marks.
    Axis lines span the full heatmap extent.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)

    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)

    # Full imshow image extent.
    ax.spines["bottom"].set_bounds(-0.5, n_cols - 0.5)
    ax.spines["left"].set_bounds(-0.5, n_rows - 0.5)

    # Keep tick labels, remove tick marks.
    ax.tick_params(
        axis="both",
        which="both",
        length=0,
        width=0,
        color=AXIS_COLOR,
        labelcolor="black",
    )

def add_family_background_y(ax: plt.Axes, y_positions: dict[str, int]) -> None:
    """Add horizontal family background bands and vertical family labels."""
    x_min, x_max = ax.get_xlim()
    x_text = x_min - 0.055 * (x_max - x_min)

    for idx, (family, methods) in enumerate(FAMILY_SPANS_Y):
        ys = [y_positions[m] for m in methods]
        y0 = min(ys) - 0.45
        y1 = max(ys) + 0.45

        ax.axhspan(
            y0,
            y1,
            color="0.95" if idx % 2 == 0 else "0.985",
            zorder=0,
        )

        ax.text(
            x_text,
            float(np.mean(ys)),
            family,
            ha="right",
            va="center",
            fontsize=8,
            color="0.35",
            rotation=90,
            clip_on=False,
        )


# ============================================================
# 3. Load and clean data
# ============================================================

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

required_cols = {
    "method",
    "diagnosis_seed",
    "mrr",
    "top1",
    "top3",
    "top5",
    "event_top1",
    "event_top3",
    "event_top5",
    "scene_f1",
}
require_columns(df, required_cols)

df["method_clean"] = df["method"].replace(METHOD_RENAME)
df["method_clean"] = pd.Categorical(
    df["method_clean"],
    categories=METHOD_ORDER,
    ordered=True,
)

df = df.sort_values(["method_clean", "diagnosis_seed"]).reset_index(drop=True)
df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned_seed_level.csv", index=False)

summary = method_mean_std(df, SUMMARY_METRICS)
summary.to_csv(OUT_DIR / f"{FIG_TAG}_summary_mean_std.csv", index=False)


# ============================================================
# 4. Figure 01-A:
#    MRR forest plot
# ============================================================

plot_methods = METHOD_ORDER[::-1]
y = np.arange(len(plot_methods))
y_positions = {method: pos for method, pos in zip(plot_methods, y)}

fig, ax = plt.subplots(figsize=(7.4, 4.9))
ax.set_xlim(0.76, 0.95)
add_family_background_y(ax, y_positions)

for method in plot_methods:
    yi = y_positions[method]
    row = summary[summary["method"] == method].iloc[0]
    mean = float(row["mrr_mean"])
    std = float(row["mrr_std"])

    ax.errorbar(
        mean,
        yi,
        xerr=std,
        fmt="o",
        markersize=6.8,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.3,
        color=METHOD_COLORS[method],
        ecolor=METHOD_COLORS[method],
        zorder=3,
    )

    ax.text(
        mean + std + 0.004,
        yi,
        f"{mean:.3f} ± {std:.3f}",
        ha="left",
        va="center",
        fontsize=8,
    )

for method_name, label_text in [
    ("Embedding-Guided", "main method"),
    ("Two-stage v1", "reference"),
]:
    yi = y_positions[method_name]
    row = summary[summary["method"] == method_name].iloc[0]
    val = float(row["mrr_mean"])

    ax.scatter(
        val,
        yi,
        s=130,
        facecolors="none",
        edgecolors="black",
        linewidths=1.6,
        zorder=4,
    )

    ax.text(
        val + 0.007,
        yi + 0.20,
        label_text,
        ha="left",
        va="center",
        fontsize=8,
        color="0.25",
    )

ax.set_yticks(y)
ax.set_yticklabels(plot_methods)
ax.set_xlabel("MRR")
ax.set_ylabel("Layout method")
ax.set_title(
    "N=25 layout comparison: MRR forest plot",
    fontsize=13,
    fontweight="bold",
)
ax.grid(axis="x", linestyle="--", linewidth=0.55, alpha=0.35)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_mrr_forest_plot")


# ============================================================
# 5. Figure 01-B:
#    6 × 6 performance fingerprint heatmap
# ============================================================

fingerprint = (
    summary.set_index("method")
    .loc[METHOD_ORDER, [f"{m}_mean" for m in FINGERPRINT_METRICS]]
)
fingerprint.columns = [METRIC_LABELS[m] for m in FINGERPRINT_METRICS]

values = fingerprint.to_numpy(dtype=float)

fig, ax = plt.subplots(figsize=(7.0, 7.0))

im = ax.imshow(
    values,
    aspect="equal",
    cmap=HEATMAP_CMAP,
    vmin=0.70,
    vmax=1.00,
    interpolation="nearest",
)

ax.set_aspect("equal")

ax.set_xticks(np.arange(len(fingerprint.columns)))
ax.set_xticklabels(fingerprint.columns, rotation=35, ha="right")
ax.set_yticks(np.arange(len(METHOD_ORDER)))
ax.set_yticklabels(METHOD_ORDER)

for i in range(values.shape[0]):
    for j in range(values.shape[1]):
        ax.text(
            j,
            i,
            f"{values[i, j]:.3f}",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
        )

ax.set_title(
    "N=25 performance fingerprint across layout methods",
    fontsize=13,
    fontweight="bold",
)

style_heatmap_axes(ax, n_rows=values.shape[0], n_cols=values.shape[1])

cbar = fig.colorbar(im, ax=ax, fraction=0.036, pad=0.035)
cbar.ax.set_ylabel("Score", rotation=90)
cbar.ax.tick_params(labelsize=8)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_performance_fingerprint_heatmap")


# ============================================================
# 6. Figure 01-C:
#    Family grouped point + errorbar plot
# ============================================================

x = np.arange(len(METHOD_ORDER))

fig, ax = plt.subplots(figsize=(10.8, 5.0))

# Family background bands
for idx, (left, right, label) in enumerate(FAMILY_SPANS_X):
    ax.axvspan(
        left,
        right,
        color="0.95" if idx % 2 == 0 else "0.985",
        zorder=0,
    )

    ax.text(
        (left + right) / 2,
        1.015,
        label,
        ha="center",
        va="bottom",
        fontsize=9,
        color="0.35",
    )

for metric in FAMILY_POINT_METRICS:
    means = []
    stds = []

    for method in METHOD_ORDER:
        row = summary[summary["method"] == method].iloc[0]
        means.append(float(row[f"{metric}_mean"]))
        stds.append(float(row[f"{metric}_std"]))

    ax.errorbar(
        x + METRIC_OFFSETS[metric],
        means,
        yerr=stds,
        fmt=METRIC_MARKERS[metric],
        markersize=6.2,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.3,
        color=METRIC_COLORS[metric],
        ecolor=METRIC_COLORS[metric],
        label=METRIC_LABELS[metric],
        zorder=3,
    )

# Mark main/reference labels, but do not over-emphasize.
for method_name, label_text in [
    ("Two-stage v1", "reference"),
    ("Embedding-Guided", "main method"),
]:
    i = METHOD_ORDER.index(method_name)
    ax.text(
        i,
        0.625,
        label_text,
        ha="center",
        va="bottom",
        fontsize=8,
        color="0.25",
        rotation=90,
    )

ax.set_xticks(x)
ax.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax.set_ylim(0.60, 1.04)
ax.set_ylabel("Score")
ax.set_title(
    "N=25 layout comparison by method family",
    fontsize=13,
    fontweight="bold",
)
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)

ax.legend(
    ncol=4,
    frameon=False,
    loc="lower right",
    fontsize=9,
)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_family_main_metrics_point_errorbar")


# ============================================================
# 7. Console report
# ============================================================

print("\nFinished Figure 01: CH5 N25 main table.")
print(f"Repository root: {REPO_ROOT}")
print(f"Source data:     {DATA_FILE}")
print(f"Output folder:   {OUT_DIR}")

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)
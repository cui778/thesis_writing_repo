# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 02: budget sweep analysis.

Source data:
    figures/ch5/source_data/CH5-budget_sweep_formal_seed42.csv

Script location:
    figures/scripts/ch5/draw_02_ch5_budget_sweep_seed42.py

Output directory:
    figures/ch5/generated_results/02_CH5_budget_sweep_seed42/

Generated figures:
    02_CH5_budget_sweep_seed42_mrr_budget_method_matrix.png/.svg
    02_CH5_budget_sweep_seed42_budget_response_by_method_facets.png/.svg

Notes:
    - No PDF output.
    - This formal table contains five methods under seed42.
    - Interpret as budget trend / boundary analysis, not multi-seed stability.
    - Ranking timeline is intentionally removed because rank can exaggerate small MRR gaps.
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

FIG_NO = "02"
FIG_TAG = f"{FIG_NO}_CH5_budget_sweep_seed42"

DATA_FILE = (
    REPO_ROOT
    / "figures"
    / "ch5"
    / "source_data"
    / "CH5-budget_sweep_formal_seed42.csv"
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

HEATMAP_CMAP = "YlGnBu"

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9

METHOD_ORDER = [
    "Degree",
    "Betweenness",
    "Cand-Obs",
    "Two-stage v1",
    "Embedding-Guided",
]

METHOD_RENAME = {
    "Degree": "Degree",
    "Betweenness": "Betweenness",
    "Cand-Obs": "Cand-Obs",
    "candidate_observability": "Cand-Obs",
    "Two-stage v1": "Two-stage v1",
    "Embedding-Guided": "Embedding-Guided",
    "Embedding-Guided-new": "Embedding-Guided",
}

BUDGET_ORDER = [5, 10, 15, 20, 25]

FACET_METRICS = ["mrr", "top1", "top3"]

METRIC_LABELS = {
    "mrr": "MRR",
    "top1": "Top-1",
    "top3": "Top-3",
    "top5": "Top-5",
    "event_top1": "Event Top-1",
    "event_top3": "Event Top-3",
    "active_recall": "Active Recall",
    "scene_f1": "Scene F1",
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


def pivot_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Return a budget × method matrix for one metric."""
    mat = (
        df.pivot(index="budget", columns="method_clean", values=metric)
        .reindex(index=BUDGET_ORDER, columns=METHOD_ORDER)
    )
    return mat.astype(float)

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
    Heatmap axes without cell gaps or cell borders.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)

    ax.spines["bottom"].set_bounds(0, n_cols - 1)
    ax.spines["left"].set_bounds(0, n_rows - 1)

    ax.tick_params(
        axis="both",
        which="both",
        direction="out",
        width=TICK_WIDTH,
        length=3.5,
        color=AXIS_COLOR,
    )


# ============================================================
# 3. Load and clean data
# ============================================================

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

required_cols = {
    "method",
    "budget",
    "mrr",
    "top1",
    "top3",
    "top5",
    "event_top1",
    "event_top3",
    "active_f1",
    "scene_f1",
}
require_columns(df, required_cols)

df["method_clean"] = df["method"].replace(METHOD_RENAME)
df["method_clean"] = pd.Categorical(
    df["method_clean"],
    categories=METHOD_ORDER,
    ordered=True,
)

df["budget"] = df["budget"].astype(int)
df = df[df["budget"].isin(BUDGET_ORDER)].copy()
df = df.sort_values(["method_clean", "budget"]).reset_index(drop=True)

df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)


# ============================================================
# 4. Derived tables
# ============================================================

mrr_mat = pivot_metric(df, "mrr")
mrr_mat.to_csv(OUT_DIR / f"{FIG_TAG}_mrr_budget_by_method.csv")

best_rows = []
for budget in BUDGET_ORDER:
    row = mrr_mat.loc[budget].sort_values(ascending=False)
    best_rows.append(
        {
            "budget": budget,
            "best_method": row.index[0],
            "best_mrr": float(row.iloc[0]),
            "second_method": row.index[1],
            "second_mrr": float(row.iloc[1]),
            "leader_margin": float(row.iloc[0] - row.iloc[1]),
        }
    )

best_df = pd.DataFrame(best_rows)
best_df.to_csv(OUT_DIR / f"{FIG_TAG}_best_method_by_budget.csv", index=False)

best_by_col = {
    int(row["budget"]): str(row["best_method"])
    for _, row in best_df.iterrows()
}


# ============================================================
# 5. Figure 02-A:
#    Budget × method MRR matrix
# ============================================================

plot_data = mrr_mat.T.reindex(METHOD_ORDER)
values = plot_data.to_numpy(dtype=float)

fig, ax = plt.subplots(figsize=(6.7, 5.6))

im = ax.imshow(
    values,
    aspect="equal",
    cmap=HEATMAP_CMAP,
    vmin=0.25,
    vmax=0.95,
    interpolation="nearest",
)

ax.set_aspect("equal")

ax.set_xticks(np.arange(len(BUDGET_ORDER)))
ax.set_xticklabels(BUDGET_ORDER)
ax.set_yticks(np.arange(len(METHOD_ORDER)))
ax.set_yticklabels(METHOD_ORDER)

ax.set_xlabel("Monitoring budget N")
ax.set_ylabel("Layout method")
ax.set_title(
    "Budget × method MRR matrix under seed42",
    fontsize=13,
    fontweight="bold",
)

for i, method in enumerate(METHOD_ORDER):
    for j, budget in enumerate(BUDGET_ORDER):
        val = values[i, j]
        is_best = best_by_col[budget] == method

        ax.text(
            j,
            i,
            f"{val:.3f}",
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold" if is_best else "normal",
            color="black",
        )

        # Mark best cell without drawing cell borders.
        if is_best:
            ax.text(
                j,
                i - 0.31,
                "best",
                ha="center",
                va="center",
                fontsize=7,
                fontweight="bold",
                color="black",
            )

style_heatmap_axes(ax, n_rows=values.shape[0], n_cols=values.shape[1])

cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.035)
cbar.ax.set_ylabel("MRR", rotation=90)
cbar.ax.tick_params(labelsize=8)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_mrr_budget_method_matrix")


# ============================================================
# 6. Figure 02-B:
#    Method-centered budget response facets
# ============================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(10.4, 7.1),
    sharex=True,
    sharey=True,
)

axes = axes.ravel()

for ax, method in zip(axes, METHOD_ORDER):
    sub = (
        df[df["method_clean"] == method]
        .sort_values("budget")
        .reset_index(drop=True)
    )

    for metric in FACET_METRICS:
        ax.plot(
            sub["budget"],
            sub[metric],
            marker="o",
            linewidth=1.9,
            markersize=5.5,
            color=METRIC_COLORS[metric],
            label=METRIC_LABELS[metric],
        )

    ax.set_title(method, fontsize=11, fontweight="bold")
    ax.set_xticks(BUDGET_ORDER)
    ax.set_ylim(0.20, 1.02)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.35)

    best_idx = sub["mrr"].idxmax()
    best_budget = int(sub.loc[best_idx, "budget"])
    best_mrr = float(sub.loc[best_idx, "mrr"])

    ax.scatter(
        [best_budget],
        [best_mrr],
        s=95,
        facecolors="none",
        edgecolors="black",
        linewidths=1.4,
        zorder=5,
    )

    ax.text(
        best_budget,
        best_mrr + 0.035,
        f"max MRR\n{best_mrr:.3f}",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="black",
    )

    style_axes_as_segments(ax)
    
axes[0].set_ylabel("Score")
axes[2].set_ylabel("Score")
axes[2].set_xlabel("Monitoring budget N")
axes[3].set_xlabel("Monitoring budget N")

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    ncol=3,
    frameon=False,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.01),
)

fig.suptitle(
    "Budget response by layout method under seed42",
    fontsize=13,
    fontweight="bold",
    y=1.05,
)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_budget_response_by_method_facets")


# ============================================================
# 7. Console report
# ============================================================

print("\nFinished Figure 02: CH5 budget sweep.")
print(f"Repository root: {REPO_ROOT}")
print(f"Source data:     {DATA_FILE}")
print(f"Output folder:   {OUT_DIR}")

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)

# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 06: pairwise Jaccard similarity analysis.

Source data:
    figures/ch5/source_data/CH5-N25_pairwise_jaccard.csv
    figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv

Script location:
    figures/scripts/ch5/draw_06_ch5_pairwise_jaccard.py

Output directory:
    figures/ch5/generated_results/06_CH5_pairwise_jaccard/

Generated figures:
    06_CH5_jaccard_similarity_heatmap.png/.svg
    06_CH5_jaccard_similarity_performance_coupling.png/.svg
    06_CH5_jaccard_embedding_guided_uniqueness_lollipop.png/.svg
    06_CH5_jaccard_clustered_matrix.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
    - Supports both:
        (1) square matrix format
        (2) long pairwise table format
    - Heatmaps use fixed color scale [0, 1].
    - Heatmap cells have no gaps and no borders.
    - Heatmap axes have no tick marks.
"""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Optional clustering support
try:
    from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
    from scipy.spatial.distance import squareform
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False


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

FIG_NO = "06"
FIG_TAG = f"{FIG_NO}_CH5_pairwise_jaccard"

SOURCE_DIR = REPO_ROOT / "figures" / "ch5" / "source_data"
JACCARD_FILE = SOURCE_DIR / "CH5-N25_pairwise_jaccard.csv"
MAIN_TABLE_FILE = SOURCE_DIR / "CH5-EXPT_fixed_protocol_N25_main_table.csv"

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
    "degree": "Degree",

    "Betweenness": "Betweenness",
    "betweenness": "Betweenness",

    "Cand-Obs": "Cand-Obs",
    "cand-obs": "Cand-Obs",
    "candidate_observability": "Cand-Obs",
    "Candidate-Observability": "Cand-Obs",

    "Two-stage": "Two-stage v1",
    "Two-stage v1": "Two-stage v1",
    "two_stage": "Two-stage v1",
    "two_stage_balanced_layout_v1": "Two-stage v1",

    "Node-Feedback": "Node-Feedback",
    "Node-Feedback (val)": "Node-Feedback",
    "node_feedback": "Node-Feedback",
    "learnable_layout_network_v0_scenario": "Node-Feedback",
    "NF": "Node-Feedback",

    "Embedding-Guided": "Embedding-Guided",
    "embedding_guided": "Embedding-Guided",
    "embedding_guided_clean_fixed": "Embedding-Guided",
    "Embedding-Guided-new": "Embedding-Guided",
    "EG": "Embedding-Guided",
}

METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

HEATMAP_CMAP = "YlGnBu"
DIAG_FACE = "0.92"
AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9


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


def normalize_name(s: str) -> str:
    """Normalize string for robust matching."""
    return re.sub(r"[^a-z0-9]+", "", str(s).strip().lower())


def canonical_method_name(x: str) -> str | None:
    """Map aliases to canonical method names."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s in METHOD_RENAME:
        return METHOD_RENAME[s]

    norm = normalize_name(s)
    for k, v in METHOD_RENAME.items():
        if normalize_name(k) == norm:
            return v

    for m in METHOD_ORDER:
        if normalize_name(m) == norm:
            return m

    return None


def find_col(df: pd.DataFrame, aliases: list[str], required: bool = True) -> str | None:
    """
    Find a column by aliases.
    Matching is case-insensitive and ignores punctuation/underscore/hyphen.
    """
    normalized = {normalize_name(c): c for c in df.columns}
    for alias in aliases:
        key = normalize_name(alias)
        if key in normalized:
            return normalized[key]
    if required:
        raise ValueError(
            f"Cannot find required column. Tried aliases={aliases}. "
            f"Existing columns={list(df.columns)}"
        )
    return None


def style_axes_as_segments(ax: plt.Axes) -> None:
    """Use clean axis line segments spanning the full plotting area."""
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

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.spines["bottom"].set_bounds(x0, x1)
    ax.spines["left"].set_bounds(y0, y1)


def style_heatmap_axes(ax: plt.Axes, n_rows: int, n_cols: int) -> None:
    """
    Heatmap axes:
    - no top/right spines
    - full bottom/left axis segments
    - no tick marks
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)

    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)

    ax.spines["bottom"].set_bounds(-0.5, n_cols - 0.5)
    ax.spines["left"].set_bounds(-0.5, n_rows - 0.5)

    ax.tick_params(
        axis="both",
        which="both",
        length=0,
        width=0,
        color=AXIS_COLOR,
        labelcolor="black",
    )


def summarize_mrr_from_main_table(main_df: pd.DataFrame) -> pd.DataFrame:
    """Compute method-level MRR mean/std from main table."""
    required_cols = {"method", "diagnosis_seed", "mrr"}
    missing = required_cols - set(main_df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in main table: {sorted(missing)}"
        )

    df = main_df.copy()
    df["method_clean"] = df["method"].map(canonical_method_name)
    missing_method_rows = df["method_clean"].isna().sum()
    if missing_method_rows > 0:
        bad_methods = sorted(df.loc[df["method_clean"].isna(), "method"].astype(str).unique().tolist())
        raise ValueError(f"Unrecognized methods in main table: {bad_methods}")

    df["method_clean"] = pd.Categorical(
        df["method_clean"],
        categories=METHOD_ORDER,
        ordered=True,
    )

    g = df.groupby("method_clean", sort=False)["mrr"]
    out = pd.DataFrame(
        {
            "method": METHOD_ORDER,
            "mrr_mean": g.mean().reindex(METHOD_ORDER).values,
            "mrr_std": g.std(ddof=1).reindex(METHOD_ORDER).values,
        }
    )
    return out


def matrix_long_from_square(matrix_df: pd.DataFrame) -> pd.DataFrame:
    """Convert square matrix into long pair list."""
    rows = []
    for i, a in enumerate(METHOD_ORDER):
        for j, b in enumerate(METHOD_ORDER):
            rows.append(
                {
                    "method_a": a,
                    "method_b": b,
                    "jaccard": float(matrix_df.loc[a, b]),
                }
            )
    return pd.DataFrame(rows)


def finalize_jaccard_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce:
    - METHOD_ORDER
    - symmetry
    - diagonal = 1
    """
    out = pd.DataFrame(index=METHOD_ORDER, columns=METHOD_ORDER, dtype=float)

    # Copy recognized values
    for r in matrix.index:
        rc = canonical_method_name(r)
        if rc is None:
            continue
        for c in matrix.columns:
            cc = canonical_method_name(c)
            if cc is None:
                continue
            try:
                val = pd.to_numeric(matrix.loc[r, c], errors="coerce")
            except Exception:
                val = np.nan
            out.loc[rc, cc] = val

    # Symmetrize
    for a in METHOD_ORDER:
        for b in METHOD_ORDER:
            if a == b:
                out.loc[a, b] = 1.0
                continue

            vab = out.loc[a, b]
            vba = out.loc[b, a]

            if pd.notna(vab) and pd.notna(vba):
                out.loc[a, b] = out.loc[b, a] = float((vab + vba) / 2.0)
            elif pd.notna(vab):
                out.loc[b, a] = float(vab)
            elif pd.notna(vba):
                out.loc[a, b] = float(vba)

    # Final checks
    if out.isna().any().any():
        missing_pairs = []
        for a in METHOD_ORDER:
            for b in METHOD_ORDER:
                if pd.isna(out.loc[a, b]):
                    missing_pairs.append((a, b))
        raise ValueError(
            "Resolved Jaccard matrix still contains missing values. "
            f"Missing entries: {missing_pairs}"
        )

    # Clip into [0, 1]
    out = out.clip(lower=0.0, upper=1.0)

    return out


def resolve_jaccard_table(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Resolve Jaccard table into:
      1) square matrix DataFrame (index/columns = METHOD_ORDER)
      2) long pairwise DataFrame

    Supports:
      - square matrix format
      - long pair list format
    """
    df = raw.copy()

    # --------------------------------------------------------
    # Case 1: square matrix style
    # --------------------------------------------------------
    recognized_method_cols = [
        c for c in df.columns if canonical_method_name(c) is not None
    ]

    if len(recognized_method_cols) >= 3:
        row_label_col = None
        for c in df.columns:
            if c not in recognized_method_cols:
                row_label_col = c
                break

        temp = pd.DataFrame(index=METHOD_ORDER, columns=METHOD_ORDER, dtype=float)

        if row_label_col is not None:
            row_methods = df[row_label_col].map(canonical_method_name)
        else:
            row_methods = pd.Series(df.index, index=df.index).map(canonical_method_name)

        for idx, row_method in row_methods.items():
            if row_method is None:
                continue
            for c in recognized_method_cols:
                col_method = canonical_method_name(c)
                val = pd.to_numeric(df.loc[idx, c], errors="coerce")
                temp.loc[row_method, col_method] = val

        matrix = finalize_jaccard_matrix(temp)
        long_df = matrix_long_from_square(matrix)
        return matrix, long_df

    # --------------------------------------------------------
    # Case 2: long format
    # --------------------------------------------------------
    col_a = find_col(
        df,
        [
            "method_a", "method_1", "method1", "layout_a", "source",
            "row_method", "left_method", "m1", "method_x"
        ],
        required=False,
    )
    col_b = find_col(
        df,
        [
            "method_b", "method_2", "method2", "layout_b", "target",
            "col_method", "right_method", "m2", "method_y"
        ],
        required=False,
    )
    val_col = find_col(
        df,
        [
            "jaccard", "jaccard_similarity", "pairwise_jaccard",
            "similarity", "score", "value"
        ],
        required=False,
    )

    if col_a is None or col_b is None or val_col is None:
        raise ValueError(
            "Cannot resolve Jaccard table. Expected either:\n"
            "  (1) square matrix with method columns\n"
            "  (2) long table with method_a / method_b / jaccard\n"
            f"Existing columns: {list(df.columns)}"
        )

    long_df = df[[col_a, col_b, val_col]].copy()
    long_df = long_df.rename(
        columns={
            col_a: "method_a",
            col_b: "method_b",
            val_col: "jaccard",
        }
    )
    long_df["method_a"] = long_df["method_a"].map(canonical_method_name)
    long_df["method_b"] = long_df["method_b"].map(canonical_method_name)
    long_df["jaccard"] = pd.to_numeric(long_df["jaccard"], errors="raise")

    bad_rows = long_df["method_a"].isna() | long_df["method_b"].isna()
    if bad_rows.any():
        bad_examples = long_df.loc[bad_rows].head(10).to_dict(orient="records")
        raise ValueError(
            "Some method names in Jaccard long table cannot be recognized. "
            f"Examples: {bad_examples}"
        )

    temp = pd.DataFrame(index=METHOD_ORDER, columns=METHOD_ORDER, dtype=float)
    for row in long_df.itertuples(index=False):
        temp.loc[row.method_a, row.method_b] = float(row.jaccard)
        temp.loc[row.method_b, row.method_a] = float(row.jaccard)

    matrix = finalize_jaccard_matrix(temp)
    long_df = matrix_long_from_square(matrix)
    return matrix, long_df


def estimate_shared_nodes_from_jaccard(j: np.ndarray | float, set_size: int = 25) -> np.ndarray | float:
    """
    If both sets have size N, and J = overlap / union,
    then overlap = 2*N*J / (1 + J).
    Here N = 25 -> overlap = 50*J/(1+J).
    """
    return (2.0 * set_size * j) / (1.0 + j)


def jaccard_from_estimated_shared_nodes(s: np.ndarray | float, set_size: int = 25) -> np.ndarray | float:
    """
    Inverse transform for secondary axis:
        s = 2*N*J / (1 + J)
        -> J = s / (2*N - s)
    """
    return s / (2.0 * set_size - s)


# ============================================================
# 3. Load and prepare data
# ============================================================

if not JACCARD_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {JACCARD_FILE}")

if not MAIN_TABLE_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {MAIN_TABLE_FILE}")

jaccard_raw = pd.read_csv(JACCARD_FILE)
main_raw = pd.read_csv(MAIN_TABLE_FILE)

jaccard_matrix, jaccard_long = resolve_jaccard_table(jaccard_raw)
mrr_summary = summarize_mrr_from_main_table(main_raw)

# Save cleaned data
jaccard_matrix.to_csv(OUT_DIR / f"{FIG_TAG}_matrix_cleaned.csv")
jaccard_long.to_csv(OUT_DIR / f"{FIG_TAG}_long_cleaned.csv", index=False)
mrr_summary.to_csv(OUT_DIR / f"{FIG_TAG}_mrr_summary_mean_std.csv", index=False)


# ============================================================
# 4. Figure 06-A:
#    Jaccard similarity heatmap
# ============================================================

heat_values = jaccard_matrix.loc[METHOD_ORDER, METHOD_ORDER].to_numpy(dtype=float)
n = len(METHOD_ORDER)

fig, ax = plt.subplots(figsize=(7.6, 7.6))

im = ax.imshow(
    heat_values,
    cmap=HEATMAP_CMAP,
    vmin=0.0,
    vmax=1.0,
    aspect="equal",
    interpolation="nearest",
)

# Soften diagonal visually
for i in range(n):
    ax.add_patch(
        Rectangle(
            (i - 0.5, i - 0.5),
            1.0,
            1.0,
            facecolor=DIAG_FACE,
            edgecolor="none",
            zorder=2,
        )
    )

# Re-draw numbers
for i in range(n):
    for j in range(n):
        val = heat_values[i, j]
        color = "black" if i == j or val < 0.55 else "white"
        ax.text(
            j,
            i,
            f"{val:.3f}",
            ha="center",
            va="center",
            fontsize=8.5,
            color=color,
            zorder=3,
        )

ax.set_xticks(np.arange(n))
ax.set_xticklabels(METHOD_ORDER, rotation=28, ha="right")
ax.set_yticks(np.arange(n))
ax.set_yticklabels(METHOD_ORDER)

ax.set_xlabel("Layout method")
ax.set_ylabel("Layout method")
ax.set_title(
    "Pairwise Jaccard similarity among N=25 layout methods",
    fontsize=13,
    fontweight="bold",
)

style_heatmap_axes(ax, n_rows=n, n_cols=n)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.set_ylabel("Jaccard similarity", rotation=90)
cbar.ax.tick_params(length=0, width=0, labelsize=8)

fig.tight_layout()
save_figure(fig, "06_CH5_jaccard_similarity_heatmap")


# ============================================================
# 5. Figure 06-B:
#    Jaccard heatmap + MRR coupling
# ============================================================

mrr_plot = mrr_summary.set_index("method").loc[METHOD_ORDER].reset_index()

fig = plt.figure(figsize=(12.8, 6.6))
gs = fig.add_gridspec(
    nrows=1,
    ncols=2,
    width_ratios=[1.15, 0.95],
    wspace=0.18,
)

ax_hm = fig.add_subplot(gs[0, 0])
ax_perf = fig.add_subplot(gs[0, 1])

# Left: heatmap
im = ax_hm.imshow(
    heat_values,
    cmap=HEATMAP_CMAP,
    vmin=0.0,
    vmax=1.0,
    aspect="equal",
    interpolation="nearest",
)

for i in range(n):
    ax_hm.add_patch(
        Rectangle(
            (i - 0.5, i - 0.5),
            1.0,
            1.0,
            facecolor=DIAG_FACE,
            edgecolor="none",
            zorder=2,
        )
    )

for i in range(n):
    for j in range(n):
        val = heat_values[i, j]
        color = "black" if i == j or val < 0.55 else "white"
        ax_hm.text(
            j,
            i,
            f"{val:.3f}",
            ha="center",
            va="center",
            fontsize=8,
            color=color,
            zorder=3,
        )

ax_hm.set_xticks(np.arange(n))
ax_hm.set_xticklabels(METHOD_ORDER, rotation=28, ha="right")
ax_hm.set_yticks(np.arange(n))
ax_hm.set_yticklabels(METHOD_ORDER)

ax_hm.set_title("Layout-set similarity", fontsize=11.5, fontweight="bold")
style_heatmap_axes(ax_hm, n_rows=n, n_cols=n)

cbar = fig.colorbar(im, ax=ax_hm, fraction=0.046, pad=0.04)
cbar.ax.set_ylabel("Jaccard", rotation=90)
cbar.ax.tick_params(length=0, width=0, labelsize=8)

# Right: horizontal forest plot for MRR
y = np.arange(n)

for yi, row in zip(y, mrr_plot.itertuples(index=False)):
    method = str(row.method)
    mean = float(row.mrr_mean)
    std = float(row.mrr_std)

    ax_perf.errorbar(
        mean,
        yi,
        xerr=std,
        fmt="o",
        markersize=7.0,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.2,
        color=METHOD_COLORS[method],
        ecolor=METHOD_COLORS[method],
        markeredgecolor="black",
        markeredgewidth=0.7,
        zorder=4,
    )

    ax_perf.text(
        mean + std + 0.004,
        yi,
        f"{mean:.3f}",
        ha="left",
        va="center",
        fontsize=8,
    )

ax_perf.set_yticks(y)
ax_perf.set_yticklabels(METHOD_ORDER)
ax_perf.invert_yaxis()  # top-to-bottom consistent with heatmap top row

xmin = float(mrr_plot["mrr_mean"].min() - mrr_plot["mrr_std"].max()) - 0.02
xmax = float(mrr_plot["mrr_mean"].max() + mrr_plot["mrr_std"].max()) + 0.04
ax_perf.set_xlim(max(0.0, xmin), min(1.02, xmax))

ax_perf.set_xlabel("MRR mean ± std")
ax_perf.set_title("Formal localization performance", fontsize=11.5, fontweight="bold")
ax_perf.grid(axis="x", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax_perf)

fig.suptitle(
    "Layout-set similarity and formal localization performance under N=25",
    fontsize=13,
    fontweight="bold",
    y=1.02,
)

fig.tight_layout()
save_figure(fig, "06_CH5_jaccard_similarity_performance_coupling")


# ============================================================
# 7. Figure 06-D:
#    Clustered Jaccard matrix
# ============================================================

if SCIPY_AVAILABLE:
    dist = 1.0 - heat_values
    np.fill_diagonal(dist, 0.0)
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method="average", optimal_ordering=True)
    order_idx = leaves_list(Z)
else:
    # Fallback: sort by average similarity (descending), keep output available
    avg_sim = pd.Series(heat_values.mean(axis=1), index=METHOD_ORDER)
    order_methods = avg_sim.sort_values(ascending=False).index.tolist()
    order_idx = np.array([METHOD_ORDER.index(m) for m in order_methods])

ordered_methods = [METHOD_ORDER[i] for i in order_idx]
ordered_mat = jaccard_matrix.loc[ordered_methods, ordered_methods].to_numpy(dtype=float)
n_ord = len(ordered_methods)

if SCIPY_AVAILABLE:
    fig = plt.figure(figsize=(9.2, 8.8))
    gs = fig.add_gridspec(
        nrows=2,
        ncols=2,
        width_ratios=[0.23, 1.0],
        height_ratios=[0.23, 1.0],
        wspace=0.02,
        hspace=0.02,
    )

    ax_empty = fig.add_subplot(gs[0, 0])
    ax_top = fig.add_subplot(gs[0, 1])
    ax_left = fig.add_subplot(gs[1, 0])
    ax_hm = fig.add_subplot(gs[1, 1])

    ax_empty.axis("off")

    dendrogram(
        Z,
        labels=ordered_methods,
        ax=ax_top,
        color_threshold=None,
        above_threshold_color="black",
        no_labels=True,
    )
    ax_top.set_xticks([])
    ax_top.set_yticks([])
    for sp in ax_top.spines.values():
        sp.set_visible(False)

    dendrogram(
        Z,
        labels=ordered_methods,
        orientation="left",
        ax=ax_left,
        color_threshold=None,
        above_threshold_color="black",
        no_labels=True,
    )
    ax_left.set_xticks([])
    ax_left.set_yticks([])
    for sp in ax_left.spines.values():
        sp.set_visible(False)

else:
    fig, ax_hm = plt.subplots(figsize=(7.8, 7.6))

im = ax_hm.imshow(
    ordered_mat,
    cmap=HEATMAP_CMAP,
    vmin=0.0,
    vmax=1.0,
    aspect="equal",
    interpolation="nearest",
)

for i in range(n_ord):
    ax_hm.add_patch(
        Rectangle(
            (i - 0.5, i - 0.5),
            1.0,
            1.0,
            facecolor=DIAG_FACE,
            edgecolor="none",
            zorder=2,
        )
    )

for i in range(n_ord):
    for j in range(n_ord):
        val = ordered_mat[i, j]
        color = "black" if i == j or val < 0.55 else "white"
        ax_hm.text(
            j,
            i,
            f"{val:.3f}",
            ha="center",
            va="center",
            fontsize=8.2,
            color=color,
            zorder=3,
        )

ax_hm.set_xticks(np.arange(n_ord))
ax_hm.set_xticklabels(ordered_methods, rotation=28, ha="right")
ax_hm.set_yticks(np.arange(n_ord))
ax_hm.set_yticklabels(ordered_methods)
style_heatmap_axes(ax_hm, n_rows=n_ord, n_cols=n_ord)

if SCIPY_AVAILABLE:
    title = "Clustered Jaccard similarity matrix"
else:
    title = "Clustered-style Jaccard matrix (fallback ordering)"

ax_hm.set_title(title, fontsize=12, fontweight="bold")

cbar = fig.colorbar(im, ax=ax_hm, fraction=0.046, pad=0.04)
cbar.ax.set_ylabel("Jaccard similarity", rotation=90)
cbar.ax.tick_params(length=0, width=0, labelsize=8)

fig.tight_layout()
save_figure(fig, "06_CH5_jaccard_clustered_matrix")


# ============================================================
# 8. Console report
# ============================================================

print("\nFinished Figure 06: CH5 pairwise Jaccard analysis.")
print(f"Repository root:     {REPO_ROOT}")
print(f"Jaccard source:      {JACCARD_FILE}")
print(f"Main-table source:   {MAIN_TABLE_FILE}")
print(f"Output folder:       {OUT_DIR}")
print(f"SciPy clustering:    {'available' if SCIPY_AVAILABLE else 'fallback ordering'}")

print("\nResolved Jaccard matrix:")
print(jaccard_matrix)

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)
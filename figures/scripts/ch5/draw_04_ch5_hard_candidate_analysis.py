# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 04: hard candidate analysis.

Source data:
    figures/ch5/source_data/CH5-N25_hard_candidate_analysis.csv

Script location:
    figures/scripts/ch5/draw_04_ch5_hard_candidate_analysis.py

Output directory:
    figures/ch5/generated_results/04_CH5_hard_candidate_analysis/

Generated figures:
    04_CH5_hard_candidate_top_gap_heatmap.png/.svg
    04_CH5_hard_candidate_gap_lollipop.png/.svg
    04_CH5_hard_candidate_method_distance_distribution.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
    - The table is candidate-level nearest-monitor hop distance under N=25.
    - method_gap is derived as max_hop - min_hop if no explicit gap column exists.
"""

from __future__ import annotations

from pathlib import Path
import re

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

FIG_NO = "04"
FIG_TAG = f"{FIG_NO}_CH5_hard_candidate"

DATA_FILE = (
    REPO_ROOT
    / "figures"
    / "ch5"
    / "source_data"
    / "CH5-N25_hard_candidate_analysis.csv"
)
MAIN_TABLE_FILE = (
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
    / f"{FIG_TAG}_analysis"
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

METHOD_SHORT = {
    "Degree": "Degree",
    "Betweenness": "Betweenness",
    "Cand-Obs": "Cand-Obs",
    "Two-stage v1": "Two-stage",
    "Node-Feedback": "NF",
    "Embedding-Guided": "EG",
}

METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

METHOD_RENAME = {
    "Degree": "Degree",
    "Betweenness": "Betweenness",
    "Cand-Obs": "Cand-Obs",
    "candidate_observability": "Cand-Obs",
    "Two-stage": "Two-stage v1",
    "Two-stage v1": "Two-stage v1",
    "two_stage_balanced_layout_v1": "Two-stage v1",
    "Node-Feedback": "Node-Feedback",
    "Node-Feedback (val)": "Node-Feedback",
    "learnable_layout_network_v0_scenario": "Node-Feedback",
    "Embedding-Guided": "Embedding-Guided",
    "Embedding-Guided-new": "Embedding-Guided",
    "embedding_guided_clean_fixed": "Embedding-Guided",
}

# Fixed heatmap palette for hop distance.
# Higher value means farther candidate from nearest monitor.
HEATMAP_CMAP = "YlOrRd"

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9

TOP_N = 15


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
    """Normalize column names for robust matching."""
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def find_col(df: pd.DataFrame, aliases: list[str], required: bool = True) -> str | None:
    """
    Find a column by a list of possible aliases.
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


def resolve_hard_candidate_table(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize hard candidate table to:
        candidate_node, Degree, Betweenness, Cand-Obs, Two-stage v1,
        Node-Feedback, Embedding-Guided
    plus derived min/max/mean/gap fields.
    """
    df = raw.copy()

    candidate_col = find_col(
        df,
        [
            "candidate_node",
            "candidate",
            "node_id",
            "defect_node",
            "true_node",
            "candidate_id",
        ],
        required=True,
    )

    method_aliases = {
    "Degree": [
        "Degree",
        "degree",
        "degree_hop",
        "Degree_hop",
        "hop_Degree",
        "hop_degree",
    ],
    "Betweenness": [
        "Betweenness",
        "betweenness",
        "betweenness_hop",
        "Betweenness_hop",
        "hop_Betweenness",
        "hop_betweenness",
    ],
    "Cand-Obs": [
        "Cand-Obs",
        "Cand Obs",
        "Cand_Obs",
        "cand_obs",
        "candidate_observability",
        "candidate_observability_hop",
        "hop_Cand-Obs",
        "hop_Cand_Obs",
        "hop_cand_obs",
        "hop_candidate_observability",
    ],
    "Two-stage v1": [
        "Two-stage v1",
        "Two-stage",
        "Two_stage",
        "two_stage",
        "two_stage_v1",
        "two_stage_balanced_layout_v1",
        "TS",
        "TS_hop",
        "hop_Two-stage",
        "hop_Two_stage",
        "hop_two_stage",
        "hop_two_stage_v1",
        "hop_two_stage_balanced_layout_v1",
    ],
    "Node-Feedback": [
        "Node-Feedback",
        "Node Feedback",
        "Node_Feedback",
        "node_feedback",
        "NF",
        "NF_hop",
        "learnable_layout_network_v0_scenario",
        "hop_Node-Feedback",
        "hop_Node_Feedback",
        "hop_node_feedback",
        "hop_NF",
        "hop_learnable_layout_network_v0_scenario",
    ],
    "Embedding-Guided": [
        "Embedding-Guided",
        "Embedding Guided",
        "Embedding_Guided",
        "embedding_guided",
        "EG",
        "EG_hop",
        "embedding_guided_clean_fixed",
        "hop_Embedding-Guided",
        "hop_Embedding_Guided",
        "hop_embedding_guided",
        "hop_EG",
        "hop_embedding_guided_clean_fixed",
    ],
    }

    out = pd.DataFrame()
    out["candidate_node"] = df[candidate_col].astype(str)

    for method, aliases in method_aliases.items():
        col = find_col(df, aliases, required=True)
        out[method] = pd.to_numeric(df[col], errors="raise")

    method_values = out[METHOD_ORDER]

    out["min_hop"] = method_values.min(axis=1)
    out["max_hop"] = method_values.max(axis=1)
    out["mean_hop"] = method_values.mean(axis=1)
    out["method_gap"] = out["max_hop"] - out["min_hop"]

    out["max_methods"] = method_values.apply(
        lambda r: ",".join([m for m in METHOD_ORDER if r[m] == r.max()]),
        axis=1,
    )
    out["min_methods"] = method_values.apply(
        lambda r: ",".join([m for m in METHOD_ORDER if r[m] == r.min()]),
        axis=1,
    )

    out = out.sort_values(
        ["method_gap", "mean_hop", "max_hop"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    return out

def summarize_mrr_from_main_table(main_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute method-level MRR mean/std from CH5-EXPT_fixed_protocol_N25_main_table.csv
    """
    required_cols = {"method", "diagnosis_seed", "mrr"}
    missing = required_cols - set(main_df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in main table: {sorted(missing)}"
        )

    df = main_df.copy()
    df["method_clean"] = df["method"].replace(METHOD_RENAME)
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

# ============================================================
# 3. Load and clean data
# ============================================================

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {DATA_FILE}")

if not MAIN_TABLE_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {MAIN_TABLE_FILE}")

raw = pd.read_csv(DATA_FILE)
main_raw = pd.read_csv(MAIN_TABLE_FILE)

df = resolve_hard_candidate_table(raw)
mrr_summary = summarize_mrr_from_main_table(main_raw)
mrr_summary.to_csv(OUT_DIR / f"{FIG_TAG}_mrr_summary_mean_std.csv", index=False)

df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned_candidate_hop_table.csv", index=False)

long_df = df.melt(
    id_vars=[
        "candidate_node",
        "min_hop",
        "max_hop",
        "mean_hop",
        "method_gap",
        "max_methods",
        "min_methods",
    ],
    value_vars=METHOD_ORDER,
    var_name="method",
    value_name="hop",
)

long_df.to_csv(OUT_DIR / f"{FIG_TAG}_candidate_hop_long.csv", index=False)

top_df = df.head(TOP_N).copy()
top_df.to_csv(OUT_DIR / f"{FIG_TAG}_top{TOP_N}_gap_candidates.csv", index=False)


# ============================================================
# 4. Figure 04-A:
#    Top-N hard candidate × method heatmap
# ============================================================

heat_values = top_df[METHOD_ORDER].to_numpy(dtype=float)
row_labels = top_df["candidate_node"].tolist()
col_labels = [METHOD_SHORT[m] for m in METHOD_ORDER]

n_rows, n_cols = heat_values.shape

# Keep the full figure less elongated, while the heatmap itself remains compact.
fig, ax = plt.subplots(figsize=(8.4, 8.4))

im = ax.imshow(
    heat_values,
    aspect="auto",
    cmap=HEATMAP_CMAP,
    vmin=0,
    vmax=max(15, float(np.nanmax(heat_values))),
    interpolation="nearest",
)

ax.set_xticks(np.arange(n_cols))
ax.set_xticklabels(col_labels, rotation=30, ha="right")
ax.set_yticks(np.arange(n_rows))
ax.set_yticklabels(row_labels)

for i in range(n_rows):
    for j in range(n_cols):
        val = heat_values[i, j]
        ax.text(
            j,
            i,
            f"{int(round(val))}",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
        )

ax.set_xlabel("Layout method")
ax.set_ylabel("Candidate node")
ax.set_title(
    f"Top-{TOP_N} hard candidates by cross-method hop gap",
    fontsize=13,
    fontweight="bold",
)

style_heatmap_axes(ax, n_rows=n_rows, n_cols=n_cols)

cbar = fig.colorbar(im, ax=ax, fraction=0.040, pad=0.035)
cbar.ax.set_ylabel("Nearest-monitor hop", rotation=90)
cbar.ax.tick_params(length=0, width=0, labelsize=8)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_top_gap_heatmap")


# ============================================================
# 5. Figure 04-B:
#    Top-N method gap lollipop
# ============================================================

gap_df = top_df.iloc[::-1].copy()
y = np.arange(len(gap_df))

fig, ax = plt.subplots(figsize=(8.8, 6.2))

gap_vals = gap_df["method_gap"].to_numpy(dtype=float)

for yi, gap, _, r in zip(y, gap_vals, gap_df["candidate_node"], gap_df.itertuples()):
    ax.hlines(
        yi,
        0,
        gap,
        color="0.55",
        linewidth=1.6,
        zorder=2,
    )
    ax.scatter(
        gap,
        yi,
        s=60,
        color="black",
        zorder=3,
    )

for yi, row in zip(y, gap_df.itertuples(index=False)):
    ax.text(
        float(row.method_gap) + 0.25,
        yi,
        f"{int(row.method_gap)}",
        ha="left",
        va="center",
        fontsize=8,
    )

    # Compact method contrast annotation.
    max_txt = str(row.max_methods).replace("Two-stage v1", "Two-stage").replace("Node-Feedback", "NF").replace("Embedding-Guided", "EG")
    min_txt = str(row.min_methods).replace("Two-stage v1", "Two-stage").replace("Node-Feedback", "NF").replace("Embedding-Guided", "EG")

    ax.text(
        0.15,
        yi,
        f"max: {max_txt} | min: {min_txt}",
        ha="left",
        va="center",
        fontsize=7.2,
        color="0.35",
    )

ax.set_yticks(y)
ax.set_yticklabels(gap_df["candidate_node"])
ax.set_xlim(0, max(16, float(gap_vals.max()) + 3))
ax.set_ylim(-0.5, len(gap_df) - 0.5)

ax.set_xlabel("Cross-method hop gap")
ax.set_ylabel("Candidate node")
ax.set_title(
    f"Top-{TOP_N} candidates with largest layout-dependent observability gap",
    fontsize=13,
    fontweight="bold",
)

ax.grid(axis="x", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_gap_lollipop")


# ============================================================
# 6. Figure 04-C:
#    Candidate-to-monitor hop distribution by method
# ============================================================

fig, ax = plt.subplots(figsize=(10.2, 5.8))

data_by_method = [
    long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    for method in METHOD_ORDER
]

positions = np.arange(len(METHOD_ORDER))

box = ax.boxplot(
    data_by_method,
    positions=positions,
    widths=0.48,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.4),
    whiskerprops=dict(color="black", linewidth=1.0),
    capprops=dict(color="black", linewidth=1.0),
    boxprops=dict(color="black", linewidth=1.0),
)

for patch, method in zip(box["boxes"], METHOD_ORDER):
    patch.set_facecolor(METHOD_COLORS[method])
    patch.set_alpha(0.28)

rng = np.random.default_rng(20260604)

for i, method in enumerate(METHOD_ORDER):
    vals = long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    jitter = rng.normal(loc=0.0, scale=0.055, size=len(vals))
    ax.scatter(
        np.full_like(vals, i, dtype=float) + jitter,
        vals,
        s=18,
        color=METHOD_COLORS[method],
        alpha=0.62,
        edgecolor="none",
        zorder=3,
    )

    # Mark mean as a diamond.
    mean_val = float(np.mean(vals))
    ax.scatter(
        i,
        mean_val,
        s=70,
        marker="D",
        color="black",
        edgecolor="white",
        linewidth=0.6,
        zorder=4,
    )
    ax.text(
        i,
        mean_val + 0.55,
        f"mean={mean_val:.2f}",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="black",
    )

ax.set_xticks(positions)
ax.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
ax.set_ylim(-0.5, max(16, float(long_df["hop"].max()) + 1))

ax.set_xlabel("Layout method")
ax.set_ylabel("Nearest-monitor hop across 50 candidates")
ax.set_title(
    "Candidate observability distance distribution by layout method",
    fontsize=13,
    fontweight="bold",
)

ax.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_method_distance_distribution")

# ============================================================
# 8. Figure 04-E:
#    Dual-axis: hop distribution + MRR
# ============================================================

fig, ax1 = plt.subplots(figsize=(10.8, 6.4))
ax2 = ax1.twinx()

positions = np.arange(len(METHOD_ORDER))

# ---------- Left axis: hop distribution ----------
data_by_method = [
    long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    for method in METHOD_ORDER
]

box = ax1.boxplot(
    data_by_method,
    positions=positions,
    widths=0.48,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.4),
    whiskerprops=dict(color="black", linewidth=1.0),
    capprops=dict(color="black", linewidth=1.0),
    boxprops=dict(color="black", linewidth=1.0),
)

for patch, method in zip(box["boxes"], METHOD_ORDER):
    patch.set_facecolor(METHOD_COLORS[method])
    patch.set_alpha(0.22)

rng = np.random.default_rng(20260605)
for i, method in enumerate(METHOD_ORDER):
    vals = long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    jitter = rng.normal(loc=0.0, scale=0.055, size=len(vals))
    ax1.scatter(
        np.full_like(vals, i, dtype=float) + jitter,
        vals,
        s=15,
        color=METHOD_COLORS[method],
        alpha=0.45,
        edgecolor="none",
        zorder=2,
    )

ax1.set_ylabel("Nearest-monitor hop")
ax1.set_ylim(-0.5, max(16, float(long_df['hop'].max()) + 1))
ax1.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.25)

# ---------- Right axis: MRR ----------
mrr_plot = mrr_summary.set_index("method").loc[METHOD_ORDER].reset_index()

ax2.plot(
    positions,
    mrr_plot["mrr_mean"].to_numpy(dtype=float),
    color="black",
    linewidth=1.5,
    marker="D",
    markersize=6.5,
    zorder=5,
)

for i, row in mrr_plot.iterrows():
    mean = float(row["mrr_mean"])
    ax2.text(
        i,
        mean + 0.004,
        f"{mean:.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
        color="black",
    )

ax2.set_ylabel("MRR")
ax2.set_ylim(0.60, 0.94)

# ---------- Shared x ----------
ax1.set_xticks(positions)
ax1.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax1.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
ax1.set_xlabel("Layout method")
ax1.set_title(
    "Candidate observability distance and localization performance under N=25",
    fontsize=13,
    fontweight="bold",
)

# Left axis style
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["bottom"].set_visible(True)
ax1.spines["left"].set_visible(True)
ax1.spines["bottom"].set_color(AXIS_COLOR)
ax1.spines["left"].set_color(AXIS_COLOR)
ax1.spines["bottom"].set_linewidth(SPINE_WIDTH)
ax1.spines["left"].set_linewidth(SPINE_WIDTH)
ax1.tick_params(
    axis="both",
    which="both",
    direction="out",
    width=TICK_WIDTH,
    length=3.5,
    color=AXIS_COLOR,
)

x0, x1 = ax1.get_xlim()
y0, y1 = ax1.get_ylim()
ax1.spines["bottom"].set_bounds(x0, x1)
ax1.spines["left"].set_bounds(y0, y1)

# Right axis style
ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["right"].set_visible(True)
ax2.spines["right"].set_color("black")
ax2.spines["right"].set_linewidth(SPINE_WIDTH)
ax2.tick_params(
    axis="y",
    which="both",
    direction="out",
    width=TICK_WIDTH,
    length=3.5,
    color="black",
    labelcolor="black",
)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_distance_vs_mrr_dual_axis")
# ============================================================
# 7. Figure 04-D:
#    Observability + performance coupling (two-panel)
# ============================================================

fig = plt.figure(figsize=(10.6, 8.0))
gs = fig.add_gridspec(
    nrows=2,
    ncols=1,
    height_ratios=[2.3, 1.2],
    hspace=0.10,
)

ax_top = fig.add_subplot(gs[0, 0])
ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax_top)

# ---------- Top panel: hop distribution ----------
data_by_method = [
    long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    for method in METHOD_ORDER
]

positions = np.arange(len(METHOD_ORDER))

box = ax_top.boxplot(
    data_by_method,
    positions=positions,
    widths=0.48,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.4),
    whiskerprops=dict(color="black", linewidth=1.0),
    capprops=dict(color="black", linewidth=1.0),
    boxprops=dict(color="black", linewidth=1.0),
)

for patch, method in zip(box["boxes"], METHOD_ORDER):
    patch.set_facecolor(METHOD_COLORS[method])
    patch.set_alpha(0.25)

rng = np.random.default_rng(20260604)
for i, method in enumerate(METHOD_ORDER):
    vals = long_df[long_df["method"] == method]["hop"].to_numpy(dtype=float)
    jitter = rng.normal(loc=0.0, scale=0.055, size=len(vals))
    ax_top.scatter(
        np.full_like(vals, i, dtype=float) + jitter,
        vals,
        s=18,
        color=METHOD_COLORS[method],
        alpha=0.60,
        edgecolor="none",
        zorder=3,
    )

    mean_val = float(np.mean(vals))
    ax_top.scatter(
        i,
        mean_val,
        s=72,
        marker="D",
        color="black",
        edgecolor="white",
        linewidth=0.6,
        zorder=4,
    )
    ax_top.text(
        i,
        mean_val + 0.55,
        f"{mean_val:.2f}",
        ha="center",
        va="bottom",
        fontsize=7.5,
    )

ax_top.set_ylabel("Nearest-monitor hop")
ax_top.set_ylim(-0.5, max(16, float(long_df["hop"].max()) + 1))
ax_top.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)
ax_top.set_title(
    "Candidate observability and formal localization performance under N=25",
    fontsize=13,
    fontweight="bold",
)

plt.setp(ax_top.get_xticklabels(), visible=False)
style_axes_as_segments(ax_top)

# ---------- Bottom panel: MRR ----------
mrr_plot = mrr_summary.set_index("method").loc[METHOD_ORDER].reset_index()

for i, row in mrr_plot.iterrows():
    method = row["method"]
    mean = float(row["mrr_mean"])
    std = float(row["mrr_std"])

    ax_bottom.errorbar(
        i,
        mean,
        yerr=std,
        fmt="o",
        markersize=7.0,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.2,
        color=METHOD_COLORS[method],
        ecolor=METHOD_COLORS[method],
        zorder=4,
    )

    ax_bottom.text(
        i,
        mean + std + 0.006,
        f"{mean:.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
    )

ax_bottom.plot(
    positions,
    mrr_plot["mrr_mean"].to_numpy(dtype=float),
    color="0.45",
    linewidth=1.1,
    zorder=2,
)

ax_bottom.set_xticks(positions)
ax_bottom.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax_bottom.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
ax_bottom.set_ylim(0.80, 0.94)
ax_bottom.set_ylabel("MRR")
ax_bottom.set_xlabel("Layout method")
ax_bottom.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax_bottom)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_observability_performance_coupling")

# ============================================================
# 7. Console report
# ============================================================

print("\nFinished Figure 04: CH5 hard candidate analysis.")
print(f"Repository root: {REPO_ROOT}")
print(f"Source data:     {DATA_FILE}")
print(f"Output folder:   {OUT_DIR}")

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)
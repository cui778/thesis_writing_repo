# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 03: layout structure and coverage-performance mechanism.

Source data:
    figures/ch5/source_data/CH5-N25_layout_structure.csv
    figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv

Script location:
    figures/scripts/ch5/draw_03_ch5_layout_structure.py

Output directory:
    figures/ch5/generated_results/03_CH5_layout_structure/

Generated figures:
    03_CH5_layout_structure_candidate_coverage_stack.png/.svg
    03_CH5_layout_structure_coverage_performance_coupling.png/.svg
    03_CH5_layout_structure_structure_performance_profile.png/.svg
    03_CH5_layout_structure_coverage_performance_quadrant.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
    - This script keeps the current color scheme, which can be unified later.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle

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

FIG_NO = "03"
FIG_TAG = f"{FIG_NO}_CH5_layout_structure"

SOURCE_DIR = REPO_ROOT / "figures" / "ch5" / "source_data"

STRUCTURE_FILE = SOURCE_DIR / "CH5-N25_layout_structure.csv"
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

METHOD_COLORS = {
    "Degree": "#4E79A7",
    "Betweenness": "#59A14F",
    "Cand-Obs": "#F28E2B",
    "Two-stage v1": "#E15759",
    "Node-Feedback": "#B07AA1",
    "Embedding-Guided": "#76B7B2",
}

COVERAGE_COLORS = {
    "direct": "#4E79A7",
    "near": "#59A14F",
    "far": "#E15759",
}

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9

FAMILY_SPANS_X = [
    (-0.5, 1.5, "Topology rule"),
    (1.5, 3.5, "Coverage-oriented"),
    (3.5, 5.5, "Diagnostic-driven"),
]


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


def require_columns(df: pd.DataFrame, columns: set[str], table_name: str) -> None:
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in {table_name}: {sorted(missing)}"
        )


def find_method_column(df: pd.DataFrame, table_name: str) -> str:
    candidates = ["method", "layout_method", "method_clean", "layout"]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(
        f"Cannot find method column in {table_name}. "
        f"Tried: {candidates}. Existing columns: {list(df.columns)}"
    )


def clean_method_column(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    method_col = find_method_column(df, table_name)
    out = df.copy()
    out["method_clean"] = out[method_col].replace(METHOD_RENAME)
    out["method_clean"] = pd.Categorical(
        out["method_clean"],
        categories=METHOD_ORDER,
        ordered=True,
    )
    out = out.sort_values("method_clean").reset_index(drop=True)

    missing_methods = set(METHOD_ORDER) - set(out["method_clean"].astype(str))
    if missing_methods:
        raise ValueError(
            f"{table_name} does not contain all expected methods: "
            f"{sorted(missing_methods)}"
        )

    return out


def style_axes_as_segments(ax: plt.Axes) -> None:
    """
    Use clean axis line segments spanning the full plotting area.
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

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.spines["bottom"].set_bounds(x0, x1)
    ax.spines["left"].set_bounds(y0, y1)


def add_family_bands_x(ax: plt.Axes, label_y_frac: float = 0.98) -> None:
    """
    Add family background bands along x-axis method groups.
    label_y_frac is in axes coordinates.
    """
    for idx, (left, right, label) in enumerate(FAMILY_SPANS_X):
        ax.axvspan(
            left,
            right,
            color="0.95" if idx % 2 == 0 else "0.985",
            zorder=0,
        )
        ax.text(
            (left + right) / 2,
            label_y_frac,
            label,
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=8.5,
            color="0.35",
        )


def summarize_mrr(main_df: pd.DataFrame) -> pd.DataFrame:
    """Compute MRR mean/std by method from seed-level main table."""
    require_columns(
        main_df,
        {"method", "diagnosis_seed", "mrr"},
        "CH5-EXPT_fixed_protocol_N25_main_table.csv",
    )

    df = clean_method_column(main_df, "CH5-EXPT_fixed_protocol_N25_main_table.csv")

    g = df.groupby("method_clean", sort=False)["mrr"]
    out = pd.DataFrame(
        {
            "method_clean": METHOD_ORDER,
            "mrr_mean": g.mean().reindex(METHOD_ORDER).values,
            "mrr_std": g.std(ddof=1).reindex(METHOD_ORDER).values,
        }
    )
    return out


# ============================================================
# 3. Load and prepare data
# ============================================================

if not STRUCTURE_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {STRUCTURE_FILE}")

if not MAIN_TABLE_FILE.exists():
    raise FileNotFoundError(f"Source data not found: {MAIN_TABLE_FILE}")

structure_raw = pd.read_csv(STRUCTURE_FILE)
main_raw = pd.read_csv(MAIN_TABLE_FILE)

require_columns(
    structure_raw,
    {"direct", "near", "far", "mean_hop", "max_hop", "overlap_count"},
    "CH5-N25_layout_structure.csv",
)

structure = clean_method_column(structure_raw, "CH5-N25_layout_structure.csv")

for col in ["direct", "near", "far", "mean_hop", "max_hop", "overlap_count"]:
    structure[col] = pd.to_numeric(structure[col], errors="raise")

mrr_summary = summarize_mrr(main_raw)

merged = (
    structure.merge(mrr_summary, on="method_clean", how="left")
    .sort_values("method_clean")
    .reset_index(drop=True)
)

if merged[["mrr_mean", "mrr_std"]].isna().any().any():
    raise ValueError("MRR summary failed to merge with layout structure table.")

# Export cleaned / derived tables
structure.to_csv(OUT_DIR / f"{FIG_TAG}_structure_cleaned.csv", index=False)
mrr_summary.to_csv(OUT_DIR / f"{FIG_TAG}_mrr_summary_mean_std.csv", index=False)
merged.to_csv(OUT_DIR / f"{FIG_TAG}_structure_performance_merged.csv", index=False)


# ============================================================
# 4. Figure 03-A:
#    Candidate coverage composition, horizontal stacked bar
# ============================================================

plot_methods = METHOD_ORDER[::-1]
plot_df = merged.set_index("method_clean").loc[plot_methods].reset_index()

y = np.arange(len(plot_methods))

fig, ax = plt.subplots(figsize=(9.6, 5.6))

left = np.zeros(len(plot_df))

for part in ["direct", "near", "far"]:
    vals = plot_df[part].to_numpy(dtype=float)
    ax.barh(
        y,
        vals,
        left=left,
        height=0.60,
        color=COVERAGE_COLORS[part],
        edgecolor="none",
        label=part,
        zorder=3,
    )

    for yi, x_left, val in zip(y, left, vals):
        if val >= 4:
            ax.text(
                x_left + val / 2,
                yi,
                f"{int(val)}",
                ha="center",
                va="center",
                fontsize=8,
                color="black",
            )

    left += vals

ax.set_yticks(y)
ax.set_yticklabels(plot_methods)
ax.set_xlim(0, 50)
ax.set_ylim(-0.5, len(plot_methods) - 0.5)

ax.set_xlabel("Number of candidate nodes")
ax.set_ylabel("Layout method")
ax.set_title(
    "Candidate coverage composition under N=25",
    fontsize=13,
    fontweight="bold",
)

ax.grid(axis="x", linestyle="--", linewidth=0.55, alpha=0.32)
ax.legend(
    ncol=3,
    frameon=False,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.08),
)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_candidate_coverage_stack")


# ============================================================
# 5. Figure 03-B:
#    Coverage-performance coupling
# ============================================================

x = np.arange(len(METHOD_ORDER))
couple_df = merged.set_index("method_clean").loc[METHOD_ORDER].reset_index()

fig = plt.figure(figsize=(11.8, 7.2))
gs = fig.add_gridspec(
    nrows=2,
    ncols=1,
    height_ratios=[2.25, 1.55],
    hspace=0.08,
)

ax_cov = fig.add_subplot(gs[0, 0])
ax_mrr = fig.add_subplot(gs[1, 0], sharex=ax_cov)

# Panel A: stacked coverage bars
bottom = np.zeros(len(couple_df))
for part in ["direct", "near", "far"]:
    vals = couple_df[part].to_numpy(dtype=float)
    ax_cov.bar(
        x,
        vals,
        bottom=bottom,
        width=0.62,
        color=COVERAGE_COLORS[part],
        edgecolor="none",
        label=part,
        zorder=3,
    )

    for xi, y_bottom, val in zip(x, bottom, vals):
        if val >= 4:
            ax_cov.text(
                xi,
                y_bottom + val / 2,
                f"{int(val)}",
                ha="center",
                va="center",
                fontsize=8,
                color="black",
            )

    bottom += vals

ax_cov.set_ylim(0, 50)
ax_cov.set_ylabel("Candidate count")
ax_cov.set_title(
    "Coverage structure and localization performance under N=25",
    fontsize=13,
    fontweight="bold",
)
ax_cov.grid(axis="y", linestyle="--", linewidth=0.55, alpha=0.32)
ax_cov.legend(frameon=False, ncol=3, loc="upper right")

plt.setp(ax_cov.get_xticklabels(), visible=False)
style_axes_as_segments(ax_cov)

# Panel B: MRR mean ± std
for idx, row in couple_df.iterrows():
    method = str(row["method_clean"])
    ax_mrr.errorbar(
        idx,
        float(row["mrr_mean"]),
        yerr=float(row["mrr_std"]),
        fmt="o",
        markersize=6.8,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.3,
        color=METHOD_COLORS[method],
        ecolor=METHOD_COLORS[method],
        zorder=4,
    )

    ax_mrr.text(
        idx,
        float(row["mrr_mean"]) + float(row["mrr_std"]) + 0.010,
        f"{float(row['mrr_mean']):.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
    )

ax_mrr.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
ax_mrr.set_ylim(0.7, 0.94)
ax_mrr.set_xticks(x)
ax_mrr.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax_mrr.set_ylabel("MRR")
ax_mrr.grid(axis="y", linestyle="--", linewidth=0.55, alpha=0.32)

add_family_bands_x(ax_mrr, label_y_frac=0.97)
style_axes_as_segments(ax_mrr)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_coverage_performance_coupling")


# ============================================================
# 6. Figure 03-C:
#    Structure-performance profile (replacing scatter)
# ============================================================

profile_df = merged.set_index("method_clean").loc[METHOD_ORDER].reset_index()
x = np.arange(len(METHOD_ORDER))

fig, axes = plt.subplots(
    2,
    2,
    figsize=(12.5, 6.8),
    sharex=True,
)

axes = axes.ravel()

profile_specs = [
    {
        "ax": axes[0],
        "metric": "far",
        "label": "Far candidate count",
        "title": "A. Far candidates",
        "higher_better": False,
        "use_errorbar": False,
    },
    {
        "ax": axes[1],
        "metric": "mean_hop",
        "label": "Mean nearest-monitor hop",
        "title": "B. Mean hop",
        "higher_better": False,
        "use_errorbar": False,
    },
    {
        "ax": axes[2],
        "metric": "max_hop",
        "label": "Max nearest-monitor hop",
        "title": "C. Max hop",
        "higher_better": False,
        "use_errorbar": False,
    },
    {
        "ax": axes[3],
        "metric": "mrr_mean",
        "label": "MRR",
        "title": "D. Spatial localization performance",
        "higher_better": True,
        "use_errorbar": True,
    },
]

for spec in profile_specs:
    ax = spec["ax"]
    metric = spec["metric"]
    vals = profile_df[metric].to_numpy(dtype=float)

    # Background family bands
    add_family_bands_x(ax, label_y_frac=0.97)

    # Thin neutral guide line
    ax.plot(
        x,
        vals,
        color="0.55",
        linewidth=1.2,
        zorder=2,
    )

    for i, method in enumerate(METHOD_ORDER):
        color = METHOD_COLORS[method]

        if spec["use_errorbar"]:
            err = float(profile_df.loc[i, "mrr_std"])
            ax.errorbar(
                i,
                vals[i],
                yerr=err,
                fmt="o",
                markersize=6.8,
                capsize=4,
                linewidth=1.4,
                elinewidth=1.2,
                color=color,
                ecolor=color,
                zorder=4,
            )
            ax.text(
                i,
                vals[i] + err + 0.006,
                f"{vals[i]:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        else:
            ax.scatter(
                i,
                vals[i],
                s=65,
                color=color,
                edgecolor="black",
                linewidth=0.6,
                zorder=4,
            )

            # Integer for counts, 2 decimals for hop
            if metric == "far":
                txt = f"{int(round(vals[i]))}"
                y_offset = 0.8
            else:
                txt = f"{vals[i]:.2f}"
                y_offset = 0.05

            ax.text(
                i,
                vals[i] + y_offset,
                txt,
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title(spec["title"], fontsize=11, fontweight="bold", loc="left")
    ax.set_ylabel(spec["label"])
    ax.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)

    # Axis ranges
    if metric == "far":
        ax.set_ylim(0, max(vals) + 4)
        note = "lower is better"
    elif metric == "mean_hop":
        ax.set_ylim(0, max(vals) + 0.45)
        note = "lower is better"
    elif metric == "max_hop":
        ax.set_ylim(0, max(vals) + 0.7)
        note = "lower is better"
    else:
        ax.set_ylim(0.80, 0.94)
        note = "higher is better"

    ax.text(
        0.02,
        0.06,
        note,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8,
        color="0.35",
    )

    ax.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
    style_axes_as_segments(ax)

# X tick labels only on bottom row
for ax in axes[:2]:
    plt.setp(ax.get_xticklabels(), visible=False)

for ax in axes[2:]:
    ax.set_xticks(x)
    ax.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")

fig.suptitle(
    "Structure-performance profile under N=25",
    fontsize=13,
    fontweight="bold",
    y=1.02,
)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_structure_performance_profile")


# ============================================================
# 7. Console report
# ============================================================

print("\nFinished Figure 03: CH5 layout structure.")
print(f"Repository root:        {REPO_ROOT}")
print(f"Structure source data:  {STRUCTURE_FILE}")
print(f"Main-table source data: {MAIN_TABLE_FILE}")
print(f"Output folder:          {OUT_DIR}")

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)


# ============================================================
# 7. Figure 03-D:
#    Coverage-performance quadrant
# ============================================================

quad_df = merged.set_index("method_clean").loc[METHOD_ORDER].reset_index()

# Quadrant coordinates
x_col = "mean_hop"
y_col = "mrr_mean"

x_vals = quad_df[x_col].to_numpy(dtype=float)
y_vals = quad_df[y_col].to_numpy(dtype=float)

# Thresholds:
# mean_hop = 2.0 corresponds to the near/far boundary.
# MRR threshold uses median to avoid an arbitrary high-performance cutoff.
x_thr = 2.0
y_thr = float(np.median(y_vals))

# Assign quadrants for traceability
quadrant_rows = []
for _, row in quad_df.iterrows():
    method = str(row["method_clean"])
    mean_hop = float(row["mean_hop"])
    mrr = float(row["mrr_mean"])

    if mean_hop <= x_thr and mrr >= y_thr:
        quadrant = "Q1: near coverage / high MRR"
    elif mean_hop <= x_thr and mrr < y_thr:
        quadrant = "Q2: near coverage / lower MRR"
    elif mean_hop > x_thr and mrr >= y_thr:
        quadrant = "Q3: far coverage / high MRR"
    else:
        quadrant = "Q4: far coverage / lower MRR"

    quadrant_rows.append(
        {
            "method": method,
            "mean_hop": mean_hop,
            "mrr_mean": mrr,
            "mrr_std": float(row["mrr_std"]),
            "far": float(row["far"]),
            "direct": float(row["direct"]),
            "near": float(row["near"]),
            "quadrant": quadrant,
        }
    )

quadrant_df = pd.DataFrame(quadrant_rows)
quadrant_df.to_csv(
    OUT_DIR / f"{FIG_TAG}_coverage_performance_quadrant_table.csv",
    index=False,
)

# Plot range
x_min = max(0.0, float(np.min(x_vals)) - 0.35)
x_max = float(np.max(x_vals)) + 0.45
y_min = float(np.min(y_vals)) - 0.035
y_max = float(np.max(y_vals)) + 0.035

fig, ax = plt.subplots(figsize=(8.8, 6.6))

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# Light quadrant backgrounds
# Quadrant backgrounds in data coordinates.
# This guarantees that the background blocks align exactly with x_thr and y_thr.
quad_patches = [
    # left-top: near coverage / high MRR
    (x_min, y_thr, x_thr - x_min, y_max - y_thr, "0.93"),

    # right-top: far coverage / high MRR
    (x_thr, y_thr, x_max - x_thr, y_max - y_thr, "0.97"),

    # left-bottom: near coverage / lower MRR
    (x_min, y_min, x_thr - x_min, y_thr - y_min, "0.985"),

    # right-bottom: far coverage / lower MRR
    (x_thr, y_min, x_max - x_thr, y_thr - y_min, "0.94"),
]

for x0, y0, width, height, color in quad_patches:
    ax.add_patch(
        Rectangle(
            (x0, y0),
            width,
            height,
            facecolor=color,
            edgecolor="none",
            zorder=0,
        )
    )

# Threshold lines
ax.axvline(
    x_thr,
    color="black",
    linestyle="--",
    linewidth=1.0,
    alpha=0.75,
    zorder=1,
)

ax.axhline(
    y_thr,
    color="black",
    linestyle="--",
    linewidth=1.0,
    alpha=0.75,
    zorder=1,
)

# Quadrant labels
ax.text(
    x_min + 0.05 * (x_max - x_min),
    y_max - 0.06 * (y_max - y_min),
    "Near coverage\nHigh MRR",
    ha="left",
    va="top",
    fontsize=9,
    color="0.25",
)

ax.text(
    x_thr + 0.05 * (x_max - x_min),
    y_max - 0.06 * (y_max - y_min),
    "Far coverage\nHigh MRR",
    ha="left",
    va="top",
    fontsize=9,
    color="0.25",
)

ax.text(
    x_min + 0.05 * (x_max - x_min),
    y_thr - 0.06 * (y_max - y_min),
    "Near coverage\nLower MRR",
    ha="left",
    va="top",
    fontsize=9,
    color="0.35",
)

ax.text(
    x_thr + 0.05 * (x_max - x_min),
    y_thr - 0.06 * (y_max - y_min),
    "Far coverage\nLower MRR",
    ha="left",
    va="top",
    fontsize=9,
    color="0.35",
)

# Manual label offsets to reduce overlap
LABEL_OFFSETS = {
    "Degree": (0.05, -0.006),
    "Betweenness": (0.05, 0.004),
    "Cand-Obs": (0.05, -0.006),
    "Two-stage v1": (0.05, 0.006),
    "Node-Feedback": (0.05, 0.003),
    "Embedding-Guided": (0.05, 0.004),
}

LABEL_SHORT = {
    "Degree": "Degree",
    "Betweenness": "Betweenness",
    "Cand-Obs": "Cand-Obs",
    "Two-stage v1": "Two-stage",
    "Node-Feedback": "Node-Feedback",
    "Embedding-Guided": "Embedding-Guided",
}

# Points
for _, row in quad_df.iterrows():
    method = str(row["method_clean"])
    mean_hop = float(row["mean_hop"])
    mrr = float(row["mrr_mean"])
    mrr_std = float(row["mrr_std"])

    ax.scatter(
    mean_hop,
    mrr,
    s=85,
    color=METHOD_COLORS[method],
    edgecolor="black",
    linewidth=0.7,
    zorder=4,
    )

    dx, dy = LABEL_OFFSETS.get(method, (0.05, 0.004))
    ax.text(
        mean_hop + dx,
        mrr + dy,
        LABEL_SHORT.get(method, method),
        ha="left",
        va="center",
        fontsize=8.5,
        color="black",
        zorder=5,
    )

# Threshold annotations
ax.text(
    x_thr,
    y_min + 0.025 * (y_max - y_min),
    "near / far boundary\nmean_hop = 2",
    ha="center",
    va="bottom",
    fontsize=8,
    color="0.30",
)

ax.text(
    x_max - 0.02 * (x_max - x_min),
    y_thr + 0.003,
    f"median MRR = {y_thr:.3f}",
    ha="right",
    va="bottom",
    fontsize=8,
    color="0.30",
)

ax.set_xlabel("Mean nearest-monitor hop")
ax.set_ylabel("MRR mean")
ax.set_title(
    "Coverage–performance quadrant under N=25",
    fontsize=13,
    fontweight="bold",
)

ax.grid(axis="both", linestyle="--", linewidth=0.45, alpha=0.25)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_coverage_performance_quadrant")
# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 05: defect-type (I/E) adaptability analysis.

Source data:
    figures/ch5/source_data/CH5-N25_by_defect_type_analysis.csv
    figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv

Script location:
    figures/scripts/ch5/draw_05_ch5_defect_type_analysis.py

Output directory:
    figures/ch5/generated_results/05_CH5_defect_type_analysis/

Generated figures:
    05_CH5_defect_type_ie_mrr_dumbbell.png/.svg
    05_CH5_defect_type_ie_gap_bar.png/.svg
    05_CH5_defect_type_performance_robustness_coupling.png/.svg
    05_CH5_defect_type_multimetric_ie_dumbbell_facets.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
    - This script supports both:
        (1) long format: method + defect_type + metric columns
        (2) wide format: one row per method with metric_I / metric_E columns
    - Default multimetric facet uses: MRR / Top-1 / Top-3 / Top-5
      If Top-5 is too saturated, you can delete "top5" from MULTI_METRICS below.
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

FIG_NO = "05"
FIG_TAG = f"{FIG_NO}_CH5_defect_type"

SOURCE_DIR = REPO_ROOT / "figures" / "ch5" / "source_data"

DATA_FILE = SOURCE_DIR / "CH5-N25_by_defect_type_analysis.csv"
MAIN_TABLE_FILE = SOURCE_DIR / "CH5-EXPT_fixed_protocol_N25_main_table.csv"

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

TYPE_COLORS = {
    "I": "#4E79A7",
    "E": "#E15759",
}

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9

# Only MRR is mandatory for this source table.
# Top-1 / Top-3 / Top-5 are used if present.
CORE_METRICS = ["mrr"]

MULTI_METRICS = ["mrr", "top1", "top3", "top5"]

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
    """Normalize string for flexible matching."""
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def find_col(df: pd.DataFrame, aliases: list[str], required: bool = True) -> str | None:
    """
    Find a column by a list of aliases.
    Matching is case-insensitive and ignores punctuation.
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


def clean_method_series(s: pd.Series) -> pd.Series:
    out = s.replace(METHOD_RENAME)
    out = pd.Categorical(out, categories=METHOD_ORDER, ordered=True)
    return out


def normalize_defect_type_value(x: str) -> str:
    s = normalize_name(str(x))
    if s.startswith("i"):
        return "I"
    if s.startswith("e"):
        return "E"
    raise ValueError(f"Cannot normalize defect type value: {x}")

def metric_base_aliases(metric: str) -> list[str]:
    """
    Flexible aliases for metric columns in long-format tables.
    Supports mrr, mrr_mean, mean_mrr, top1_mean, window_top1_mean, etc.
    """
    aliases = {
        "mrr": [
            "mrr",
            "mrr_mean",
            "mean_mrr",
            "window_mrr",
            "window_mrr_mean",
            "node_mrr",
            "node_mrr_mean",
            "loc_mrr",
            "localization_mrr",
        ],
        "top1": [
            "top1",
            "top_1",
            "top1_mean",
            "top_1_mean",
            "mean_top1",
            "window_top1",
            "window_top1_mean",
            "hit_top1",
            "hit_rate_top1",
        ],
        "top3": [
            "top3",
            "top_3",
            "top3_mean",
            "top_3_mean",
            "mean_top3",
            "window_top3",
            "window_top3_mean",
            "hit_top3",
            "hit_rate_top3",
        ],
        "top5": [
            "top5",
            "top_5",
            "top5_mean",
            "top_5_mean",
            "mean_top5",
            "window_top5",
            "window_top5_mean",
            "hit_top5",
            "hit_rate_top5",
        ],
    }
    return aliases.get(metric, [metric])


def metric_aliases(metric: str, defect_type: str) -> list[str]:
    """
    Flexible aliases for wide-format metric columns.

    Examples:
        mrr_I, I_mrr, mrr_mean_I, I_mrr_mean,
        top1_E, E_top1_mean, window_top3_mean_I, etc.
    """
    bases = metric_base_aliases(metric)
    type_aliases = {
        "I": ["I", "i", "type_I", "group_I", "inflow", "infiltration"],
        "E": ["E", "e", "type_E", "group_E", "exflow", "exfiltration"],
    }[defect_type]

    out = []
    for b in bases:
        for t in type_aliases:
            out.extend(
                [
                    f"{b}_{t}",
                    f"{t}_{b}",
                    f"{b}{t}",
                    f"{t}{b}",
                ]
            )
    return out


def resolve_by_defect_type_table(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize CH5-N25_by_defect_type_analysis.csv into wide format:

        method, mrr_I, mrr_E, top1_I, top1_E, ...

    Supports:
        1) long format:
            method | defect_type | mrr_mean | top1_mean | top3_mean | ...
        2) wide format:
            method | mrr_I | mrr_E | top1_I | top1_E | ...
    """
    df = raw.copy()

    method_col = find_col(
        df,
        ["method", "layout_method", "layout", "method_clean"],
        required=False,
    )

    type_col = find_col(
        df,
        [
            "defect_type",
            "type",
            "ie_type",
            "i_e_type",
            "IE_type",
            "group",
            "defect_group",
            "true_type",
            "true_defect_type",
            "label",
        ],
        required=False,
    )

    requested_metrics = ["mrr", "top1", "top3", "top5"]

    # ========================================================
    # Case 1: long format
    # ========================================================
    if method_col is not None and type_col is not None:
        value_map = {}

        for metric in requested_metrics:
            col = find_col(
                df,
                metric_base_aliases(metric),
                required=False,
            )
            if col is not None:
                value_map[metric] = col

        if "mrr" not in value_map:
            raise ValueError(
                "Long-format table detected, but cannot find MRR column. "
                f"Existing columns={list(df.columns)}. "
                "Expected one of: mrr, mrr_mean, mean_mrr, window_mrr_mean, etc."
            )

        long_df = df[[method_col, type_col, *value_map.values()]].copy()
        long_df["method_clean"] = clean_method_series(long_df[method_col])
        long_df["defect_type_clean"] = long_df[type_col].map(normalize_defect_type_value)

        for metric, col in value_map.items():
            long_df[metric] = pd.to_numeric(long_df[col], errors="raise")

        value_cols = list(value_map.keys())

        long_df = (
            long_df.groupby(["method_clean", "defect_type_clean"], observed=False)[value_cols]
            .mean()
            .reset_index()
        )

        wide = pd.DataFrame({"method": METHOD_ORDER})
        wide["method"] = pd.Categorical(
            wide["method"],
            categories=METHOD_ORDER,
            ordered=True,
        )

        for defect_type in ["I", "E"]:
            sub = long_df[long_df["defect_type_clean"] == defect_type].copy()
            sub = sub.rename(columns={"method_clean": "method"})
            keep_cols = ["method"] + value_cols
            sub = sub[keep_cols].copy()
            sub = sub.rename(
                columns={metric: f"{metric}_{defect_type}" for metric in value_cols}
            )
            wide = wide.merge(sub, on="method", how="left")

        wide = wide.sort_values("method").reset_index(drop=True)

        if wide[["mrr_I", "mrr_E"]].isna().any().any():
            raise ValueError(
                "MRR I/E values are missing after long-format conversion. "
                "Check whether defect_type values can be normalized to I/E."
            )

        return wide

    # ========================================================
    # Case 2: wide format
    # ========================================================
    if method_col is None:
        method_col = find_col(
            df,
            ["method", "layout_method", "layout", "method_clean"],
            required=True,
        )

    out = pd.DataFrame()
    out["method"] = clean_method_series(df[method_col])

    found_metrics = []

    for metric in requested_metrics:
        found_pair = True

        for defect_type in ["I", "E"]:
            col = find_col(
                df,
                metric_aliases(metric, defect_type),
                required=False,
            )
            if col is None:
                found_pair = False
                break

        if found_pair:
            for defect_type in ["I", "E"]:
                col = find_col(
                    df,
                    metric_aliases(metric, defect_type),
                    required=True,
                )
                out[f"{metric}_{defect_type}"] = pd.to_numeric(df[col], errors="raise")
            found_metrics.append(metric)

    if "mrr" not in found_metrics:
        raise ValueError(
            "Cannot resolve MRR from by-defect-type table. "
            f"Existing columns={list(df.columns)}. "
            "Expected long format with method + defect_type + mrr_mean, "
            "or wide format with mrr_I / mrr_E."
        )

    out = out.sort_values("method").reset_index(drop=True)
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
print("Raw defect-type columns:", list(raw.columns))

df = resolve_by_defect_type_table(raw)

# Validate mandatory metric: MRR
for metric in CORE_METRICS:
    for t in ["I", "E"]:
        col = f"{metric}_{t}"
        if col not in df.columns:
            raise ValueError(
                f"Required column missing after resolving table: {col}. "
                f"Resolved columns={list(df.columns)}"
            )

# Use all available I/E metrics.
available_multi_metrics = [
    m for m in MULTI_METRICS
    if f"{m}_I" in df.columns and f"{m}_E" in df.columns
]

if "mrr" not in available_multi_metrics:
    raise ValueError(
        f"MRR must be available for plotting. Resolved columns={list(df.columns)}"
    )

mrr_summary = summarize_mrr_from_main_table(main_raw)

# Derived I-E gaps for all available metrics.
for metric in available_multi_metrics:
    df[f"{metric}_gap"] = df[f"{metric}_I"] - df[f"{metric}_E"]

# Keep order fixed
df["method"] = pd.Categorical(df["method"], categories=METHOD_ORDER, ordered=True)
df = df.sort_values("method").reset_index(drop=True)

# Export cleaned tables
df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned_ie_table.csv", index=False)
mrr_summary.to_csv(OUT_DIR / f"{FIG_TAG}_overall_mrr_summary_mean_std.csv", index=False)

# Long table for multimetric plotting
long_rows = []
for _, row in df.iterrows():
    method = str(row["method"])
    for metric in available_multi_metrics:
        long_rows.append(
            {
                "method": method,
                "metric": metric,
                "defect_type": "I",
                "value": float(row[f"{metric}_I"]),
            }
        )
        long_rows.append(
            {
                "method": method,
                "metric": metric,
                "defect_type": "E",
                "value": float(row[f"{metric}_E"]),
            }
        )

long_df = pd.DataFrame(long_rows)
long_df.to_csv(OUT_DIR / f"{FIG_TAG}_multimetric_long.csv", index=False)


# ============================================================
# 4. Figure 05-A:
#    I/E MRR dumbbell plot
# ============================================================

plot_df = df.iloc[::-1].copy()
y = np.arange(len(plot_df))

fig, ax = plt.subplots(figsize=(8.8, 5.8))

for yi, row in zip(y, plot_df.itertuples(index=False)):
    mrr_i = float(row.mrr_I)
    mrr_e = float(row.mrr_E)

    ax.hlines(
        yi,
        xmin=min(mrr_i, mrr_e),
        xmax=max(mrr_i, mrr_e),
        color="0.55",
        linewidth=1.6,
        zorder=2,
    )

    ax.scatter(
        mrr_i,
        yi,
        s=58,
        color=TYPE_COLORS["I"],
        edgecolor="black",
        linewidth=0.6,
        zorder=4,
    )
    ax.scatter(
        mrr_e,
        yi,
        s=58,
        color=TYPE_COLORS["E"],
        edgecolor="black",
        linewidth=0.6,
        zorder=4,
    )

    ax.text(
        mrr_i + 0.004,
        yi + 0.14,
        f"{mrr_i:.3f}",
        ha="left",
        va="center",
        fontsize=7.5,
        color=TYPE_COLORS["I"],
    )
    ax.text(
        mrr_e + 0.004,
        yi - 0.14,
        f"{mrr_e:.3f}",
        ha="left",
        va="center",
        fontsize=7.5,
        color=TYPE_COLORS["E"],
    )

ax.set_yticks(y)
ax.set_yticklabels(plot_df["method"].astype(str).tolist())
ax.set_ylim(-0.5, len(plot_df) - 0.5)

x_min = min(df["mrr_I"].min(), df["mrr_E"].min()) - 0.03
x_max = max(df["mrr_I"].max(), df["mrr_E"].max()) + 0.05
ax.set_xlim(max(0.0, x_min), min(1.02, x_max))

ax.set_xlabel("MRR")
ax.set_ylabel("Layout method")
ax.set_title(
    "I/E defect-type localization performance: MRR dumbbell plot",
    fontsize=13,
    fontweight="bold",
)

legend_handles = [
    plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=TYPE_COLORS["I"],
               markeredgecolor="black", markersize=7, label="I-type"),
    plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=TYPE_COLORS["E"],
               markeredgecolor="black", markersize=7, label="E-type"),
]
ax.legend(handles=legend_handles, frameon=False, loc="lower right")

ax.grid(axis="x", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_ie_mrr_dumbbell")


# ============================================================
# 5. Figure 05-B:
#    I-E gap bar
# ============================================================

gap_df = df.copy().sort_values("mrr_gap", ascending=False).reset_index(drop=True)
gap_df = gap_df.iloc[::-1].copy()
y = np.arange(len(gap_df))

fig, ax = plt.subplots(figsize=(8.6, 5.6))

vals = gap_df["mrr_gap"].to_numpy(dtype=float)

for yi, row in zip(y, gap_df.itertuples(index=False)):
    v = float(row.mrr_gap)
    color = "#4E79A7" if v >= 0 else "#E15759"

    ax.hlines(
        yi,
        0,
        v,
        color="0.60",
        linewidth=1.2,
        zorder=1,
    )
    ax.scatter(
        v,
        yi,
        s=62,
        color=color,
        edgecolor="black",
        linewidth=0.6,
        zorder=3,
    )
    ax.text(
        v + (0.004 if v >= 0 else -0.004),
        yi,
        f"{v:+.3f}",
        ha="left" if v >= 0 else "right",
        va="center",
        fontsize=8,
        color="black",
    )

ax.axvline(0, color="black", linewidth=1.0, linestyle="--", alpha=0.7)

ax.set_yticks(y)
ax.set_yticklabels(gap_df["method"].astype(str).tolist())
ax.set_ylim(-0.5, len(gap_df) - 0.5)

pad = max(0.02, float(np.abs(vals).max()) * 0.25)
ax.set_xlim(float(vals.min()) - pad, float(vals.max()) + pad)

ax.set_xlabel("MRR gap (I - E)")
ax.set_ylabel("Layout method")
ax.set_title(
    "Defect-type robustness: I-E MRR gap by layout method",
    fontsize=13,
    fontweight="bold",
)

ax.grid(axis="x", linestyle="--", linewidth=0.50, alpha=0.30)

style_axes_as_segments(ax)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_ie_gap_bar")

# ============================================================
# 6. Figure 05-C:
#    Overall performance + I/E vertical dumbbell coupling
# ============================================================

mrr_plot = mrr_summary.set_index("method").loc[METHOD_ORDER].reset_index()
gap_plot = df.set_index("method").loc[METHOD_ORDER].reset_index()
x = np.arange(len(METHOD_ORDER))

fig = plt.figure(figsize=(11.2, 7.8))
gs = fig.add_gridspec(
    nrows=2,
    ncols=1,
    height_ratios=[1.35, 1.25],
    hspace=0.12,
)

ax_top = fig.add_subplot(gs[0, 0])
ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax_top)

# ------------------------------------------------------------
# Panel A: overall MRR mean ± std
# ------------------------------------------------------------

for i, row in mrr_plot.iterrows():
    method = str(row["method"])
    mean = float(row["mrr_mean"])
    std = float(row["mrr_std"])

    ax_top.errorbar(
        i,
        mean,
        yerr=std,
        fmt="o",
        markersize=7.2,
        capsize=4,
        linewidth=1.5,
        elinewidth=1.25,
        color=METHOD_COLORS[method],
        ecolor=METHOD_COLORS[method],
        markeredgecolor="black",
        markeredgewidth=0.7,
        zorder=4,
    )

    ax_top.text(
        i,
        mean + std + 0.006,
        f"{mean:.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
    )

# Neutral guide line, not a trend claim.
ax_top.plot(
    x,
    mrr_plot["mrr_mean"].to_numpy(dtype=float),
    color="0.45",
    linewidth=1.1,
    zorder=2,
)

ax_top.set_ylabel("Overall MRR")
ax_top.set_ylim(0.80, 0.94)
ax_top.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)

ax_top.set_title(
    "Overall localization performance and I/E defect-type adaptability under N=25",
    fontsize=13,
    fontweight="bold",
)

plt.setp(ax_top.get_xticklabels(), visible=False)
style_axes_as_segments(ax_top)


# ------------------------------------------------------------
# Panel B: vertical I/E dumbbell gap plot
# ------------------------------------------------------------

# Required columns:
#   mrr_I, mrr_E
# Optional derived column:
#   mrr_gap = mrr_I - mrr_E
if "mrr_gap" not in gap_plot.columns:
    gap_plot["mrr_gap"] = gap_plot["mrr_I"] - gap_plot["mrr_E"]

y_i = gap_plot["mrr_I"].to_numpy(dtype=float)
y_e = gap_plot["mrr_E"].to_numpy(dtype=float)
gaps = gap_plot["mrr_gap"].to_numpy(dtype=float)

# Vertical dumbbell lines: E -> I.
for i, row in gap_plot.iterrows():
    method = str(row["method"])
    val_i = float(row["mrr_I"])
    val_e = float(row["mrr_E"])

    ax_bottom.plot(
        [i, i],
        [val_e, val_i],
        color=METHOD_COLORS[method],
        linewidth=2.2,
        alpha=0.95,
        zorder=2,
    )

# E-type point: hollow marker.
ax_bottom.scatter(
    x,
    y_e,
    s=72,
    marker="o",
    facecolor="white",
    edgecolor="black",
    linewidth=1.0,
    zorder=4,
    label="E-type",
)

# I-type point: filled marker.
ax_bottom.scatter(
    x,
    y_i,
    s=78,
    marker="o",
    color=[METHOD_COLORS[m] for m in gap_plot["method"].astype(str)],
    edgecolor="black",
    linewidth=0.8,
    zorder=5,
    label="I-type",
)

# Gap annotations.
for i, val_i, val_e, gap in zip(x, y_i, y_e, gaps):
    y_mid = (val_i + val_e) / 2.0

    # Put label slightly to the right of each vertical dumbbell.
    ax_bottom.text(
        i + 0.08,
        y_mid,
        f"Δ={gap:.3f}",
        ha="left",
        va="center",
        fontsize=8.2,
        color="black",
    )

# Optional numeric labels for I/E endpoints.
# These are deliberately small to avoid clutter.
for i, val_i, val_e in zip(x, y_i, y_e):
    ax_bottom.text(
        i - 0.08,
        val_i + 0.002,
        f"{val_i:.3f}",
        ha="right",
        va="bottom",
        fontsize=7.2,
        color="0.25",
    )
    ax_bottom.text(
        i - 0.08,
        val_e - 0.002,
        f"{val_e:.3f}",
        ha="right",
        va="top",
        fontsize=7.2,
        color="0.25",
    )

ax_bottom.set_xticks(x)
ax_bottom.set_xticklabels(METHOD_ORDER, rotation=25, ha="right")
ax_bottom.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)

y_min = min(float(np.min(y_i)), float(np.min(y_e)))
y_max = max(float(np.max(y_i)), float(np.max(y_e)))
y_pad = max(0.018, (y_max - y_min) * 0.22)
ax_bottom.set_ylim(y_min - y_pad, y_max + y_pad)

ax_bottom.set_ylabel("I/E MRR")
ax_bottom.set_xlabel("Layout method")
ax_bottom.grid(axis="y", linestyle="--", linewidth=0.50, alpha=0.30)

ax_bottom.legend(
    frameon=False,
    loc="upper right",
    ncol=2,
    handletextpad=0.4,
    columnspacing=1.0,
)

# Add a light reference note.
ax_bottom.text(
    0.01,
    0.04,
    "Line length = I-E MRR gap",
    transform=ax_bottom.transAxes,
    ha="left",
    va="bottom",
    fontsize=8,
    color="0.35",
)

style_axes_as_segments(ax_bottom)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_performance_robustness_coupling")

# ============================================================
# 7. Figure 05-D:
#    Multi-metric I/E dumbbell facets
# ============================================================

facet_methods = METHOD_ORDER
facet_metrics = available_multi_metrics

fig, axes = plt.subplots(
    2,
    3,
    figsize=(12.8, 7.8),
    sharex=True,
)

axes = axes.ravel()

all_vals = []
for metric in facet_metrics:
    all_vals.extend(df[f"{metric}_I"].tolist())
    all_vals.extend(df[f"{metric}_E"].tolist())

x_min = max(0.0, min(all_vals) - 0.04)
x_max = min(1.02, max(all_vals) + 0.05)

for ax, method in zip(axes, facet_methods):
    sub = df[df["method"] == method].iloc[0]

    y_labels = facet_metrics[::-1]
    y = np.arange(len(y_labels))

    for yi, metric in zip(y, y_labels):
        val_i = float(sub[f"{metric}_I"])
        val_e = float(sub[f"{metric}_E"])

        ax.hlines(
            yi,
            xmin=min(val_i, val_e),
            xmax=max(val_i, val_e),
            color="0.60",
            linewidth=1.4,
            zorder=2,
        )

        ax.scatter(
            val_i,
            yi,
            s=52,
            color=TYPE_COLORS["I"],
            edgecolor="black",
            linewidth=0.6,
            zorder=4,
        )
        ax.scatter(
            val_e,
            yi,
            s=52,
            color=TYPE_COLORS["E"],
            edgecolor="black",
            linewidth=0.6,
            zorder=4,
        )

        # Short value annotations
        ax.text(
            val_i + 0.003,
            yi + 0.12,
            f"{val_i:.3f}",
            ha="left",
            va="center",
            fontsize=7.0,
            color=TYPE_COLORS["I"],
        )
        ax.text(
            val_e + 0.003,
            yi - 0.12,
            f"{val_e:.3f}",
            ha="left",
            va="center",
            fontsize=7.0,
            color=TYPE_COLORS["E"],
        )

    ax.set_title(method, fontsize=10.5, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([METRIC_LABELS[m] for m in y_labels])

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-0.5, len(y_labels) - 0.5)
    ax.grid(axis="x", linestyle="--", linewidth=0.45, alpha=0.25)

    style_axes_as_segments(ax)

# Top row no x tick labels
for ax in axes[:3]:
    plt.setp(ax.get_xticklabels(), visible=False)

for ax in axes[3:]:
    ax.set_xlabel("Score")

legend_handles = [
    plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=TYPE_COLORS["I"],
               markeredgecolor="black", markersize=7, label="I-type"),
    plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=TYPE_COLORS["E"],
               markeredgecolor="black", markersize=7, label="E-type"),
]
fig.legend(
    handles=legend_handles,
    frameon=False,
    loc="upper center",
    ncol=2,
    bbox_to_anchor=(0.5, 1.01),
)

fig.suptitle(
    "Multi-metric defect-type adaptability across layout methods",
    fontsize=13,
    fontweight="bold",
    y=1.03,
)

fig.tight_layout()
save_figure(fig, f"{FIG_TAG}_multimetric_ie_dumbbell_facets")


# ============================================================
# 8. Console report
# ============================================================

print("\nFinished Figure 05: CH5 defect-type analysis.")
print(f"Repository root: {REPO_ROOT}")
print(f"Defect-type table: {DATA_FILE}")
print(f"Main-table source: {MAIN_TABLE_FILE}")
print(f"Output folder: {OUT_DIR}")

print("\nResolved columns:")
print(list(df.columns))

print("\nGenerated files:")
for p in sorted(OUT_DIR.iterdir()):
    print(" -", p.name)
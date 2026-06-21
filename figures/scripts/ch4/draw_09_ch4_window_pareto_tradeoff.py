from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import (
    CH4_SOURCE,
    METRIC_COLORS,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
    style_heatmap_axes_plain,
)


"""
Scientific question:
How does input window length trade spatial localization, temporal boundary
recovery, and false-alarm control?

Section: 4.4.5
Figure role: mechanism-analysis main figure.
"""


FIG_TAG = "09_CH4_window_pareto_tradeoff"
DATA_FILE = CH4_SOURCE / "CH4-F09b_formal_time_window_length_eval_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)

SCORECARD_COLS = [
    ("scene_node_top1", "Scene Top-1", "higher"),
    ("scene_node_mrr", "Scene MRR", "higher"),
    ("scene_node_top3", "Scene Top-3", "higher"),
    ("active_interval_iou_mean", "Interval IoU", "higher"),
    ("onset_error_hours_mean", "Onset error", "lower"),
    ("normal_window_fpr", "Normal FPR", "lower"),
]


def column_score(values: np.ndarray, direction: str) -> np.ndarray:
    values = values.astype(float)
    if direction == "lower":
        values = values.max() - values
    span = values.max() - values.min()
    if span <= 1e-12:
        return np.full_like(values, 0.72, dtype=float)
    # Keep the heatmap in a useful visible range. Starting near zero made all
    # high-performing window scores collapse into similarly dark cells.
    return 0.22 + 0.78 * (values - values.min()) / span


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig").sort_values("window_hours").reset_index(drop=True)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)

    fig = plt.figure(figsize=(11.6, 5.3), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.02, 1.22])
    ax_scatter = fig.add_subplot(gs[0, 0])
    ax_hm = fig.add_subplot(gs[0, 1])

    x = df["onset_error_hours_mean"].to_numpy(dtype=float)
    y = df["scene_node_top1"].to_numpy(dtype=float)
    color_vals = df["normal_window_fpr"].to_numpy(dtype=float)
    size_vals = df["active_interval_iou_mean"].to_numpy(dtype=float)
    sizes = 420 + 900 * (size_vals - size_vals.min()) / max(size_vals.max() - size_vals.min(), 1e-9)
    sc = ax_scatter.scatter(
        x,
        y,
        c=color_vals,
        s=sizes,
        cmap="YlOrRd",
        edgecolor="#333333",
        linewidth=0.8,
        alpha=0.92,
    )
    for _, row in df.iterrows():
        ax_scatter.text(
            row["onset_error_hours_mean"] + 0.035,
            row["scene_node_top1"] + 0.006,
            f"{int(row['window_hours'])}h",
            fontsize=8.5,
            fontweight="bold",
        )
    ax_scatter.set_xlabel("Onset error (h); lower is better")
    ax_scatter.set_ylabel("Scene Top-1; higher is better")
    ax_scatter.set_title("A. Spatial-temporal Pareto view", loc="left", fontweight="bold")
    ax_scatter.set_xlim(max(0, x.min() - 0.25), x.max() + 0.45)
    ax_scatter.set_ylim(y.min() - 0.045, y.max() + 0.045)
    style_axes_as_segments(ax_scatter, grid_axis="both")
    cbar = fig.colorbar(sc, ax=ax_scatter, fraction=0.046, pad=0.035)
    cbar.set_label("")
    cbar.ax.set_title("FPR", fontsize=8, pad=4)

    raw_cols = [c for c, _, _ in SCORECARD_COLS]
    heat_raw = df[raw_cols].to_numpy(dtype=float)
    heat_cols = []
    for col, _, direction in SCORECARD_COLS:
        heat_cols.append(column_score(df[col].to_numpy(dtype=float), direction))
    heat = np.vstack(heat_cols).T
    im = ax_hm.imshow(heat, cmap="YlGnBu", vmin=0.20, vmax=1.00, aspect="equal")
    ax_hm.set_xticks(np.arange(len(SCORECARD_COLS)))
    ax_hm.set_xticklabels([label for _, label, _ in SCORECARD_COLS], rotation=30, ha="right")
    ax_hm.set_yticks(np.arange(len(df)))
    ax_hm.set_yticklabels([f"{int(v)}h" for v in df["window_hours"]])
    ax_hm.set_title("B. Relative scorecard by metric", loc="left", fontweight="bold")
    style_heatmap_axes_plain(ax_hm)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            metric = SCORECARD_COLS[j][0]
            raw = heat_raw[i, j]
            if metric == "normal_window_fpr":
                text = f"{raw:.4f}"
            elif metric == "onset_error_hours_mean":
                text = f"{raw:.2f}h"
            else:
                text = f"{raw:.3f}"
            color = "white" if heat[i, j] >= 0.66 else "#222222"
            ax_hm.text(j, i, text, ha="center", va="center", fontsize=6.7, color=color)
    cbar2 = fig.colorbar(im, ax=ax_hm, fraction=0.03, pad=0.025)
    cbar2.set_label("Within-metric relative score")

    fig.text(
        0.01,
        -0.05,
        "Source: CH4-F09b_formal_time_window_length_eval_summary.csv | Heatmap colors are column-normalized after aligning metric direction; raw values are printed in cells.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_pareto_fingerprint")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

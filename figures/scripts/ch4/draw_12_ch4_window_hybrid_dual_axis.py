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
)


"""
Scientific question:
Which window length best balances spatial localization, temporal boundary
recovery, and false-alarm control?

Section: 4.4.5
Figure role: thesis/PPT hybrid tradeoff figure. This version uses a two-panel
line layout: Panel A focuses on spatial localization (Top-1 + MRR + Top-3),
while Panel B focuses on temporal boundary recovery (Interval IoU + onset
error) with Normal FPR retained as a compact note.
"""


FIG_TAG = "12_CH4_window_hybrid_dual_axis"
DATA_FILE = CH4_SOURCE / "CH4-F09b_formal_time_window_length_eval_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig").sort_values("window_hours").reset_index(drop=True)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    x = np.arange(len(df))
    labels = [f"{int(v)}h" for v in df["window_hours"]]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), constrained_layout=True)
    ax_spatial, ax_temporal = axes
    ax_temporal_r = ax_temporal.twinx()

    # Panel A: Top-1 is more discriminative than Top-5 in this table; MRR
    # remains as the smoother rank-quality companion metric.
    line_top1 = ax_spatial.plot(
        x,
        df["scene_node_top1"],
        color=METRIC_COLORS["top1"],
        marker="s",
        linewidth=2.0,
        markersize=6,
        label="Scene Top-1",
        zorder=4,
    )[0]
    line_mrr = ax_spatial.plot(
        x,
        df["scene_node_mrr"],
        color=METRIC_COLORS["mrr"],
        marker="o",
        linewidth=2.1,
        markersize=6,
        label="Scene MRR",
        zorder=4,
    )[0]
    line_top3 = ax_spatial.plot(
        x,
        df["scene_node_top3"],
        color=METRIC_COLORS["top3"],
        marker="^",
        linewidth=1.7,
        markersize=5.5,
        linestyle="--",
        label="Scene Top-3",
        zorder=3,
        alpha=0.90,
    )[0]
    for xx, yy in zip(x, df["scene_node_top1"]):
        ax_spatial.text(xx, yy - 0.020, f"{yy:.3f}", ha="center", va="top", fontsize=7.5, color=METRIC_COLORS["top1"])
    for xx, yy in zip(x, df["scene_node_mrr"]):
        ax_spatial.text(xx, yy - 0.014, f"{yy:.3f}", ha="center", va="top", fontsize=7.5, color=METRIC_COLORS["mrr"])
    for xx, yy in zip(x, df["scene_node_top3"]):
        ax_spatial.text(xx, yy + 0.012, f"{yy:.3f}", ha="center", va="bottom", fontsize=7.5, color=METRIC_COLORS["top3"])
    ax_spatial.set_xticks(x)
    ax_spatial.set_xticklabels(labels)
    ax_spatial.set_ylim(0.50, 1.02)
    ax_spatial.set_xlabel("Input window length")
    ax_spatial.set_ylabel("Spatial localization score")
    ax_spatial.set_title("A. Spatial localization", loc="left", fontweight="bold")
    style_axes_as_segments(ax_spatial, grid_axis="y")
    ax_spatial.legend([line_top1, line_mrr, line_top3], ["Scene Top-1", "Scene MRR", "Scene Top-3"], frameon=False, loc="lower right")

    # Panel B: retain both temporal boundary metrics. IoU uses the left axis;
    # onset error has its own axis because lower is better and units are hours.
    line_iou = ax_temporal.plot(
        x,
        df["active_interval_iou_mean"],
        color=METRIC_COLORS["control"],
        marker="o",
        linewidth=2.1,
        markersize=6,
        label="Active interval IoU",
        zorder=4,
    )[0]
    line_onset = ax_temporal_r.plot(
        x,
        df["onset_error_hours_mean"],
        color=METRIC_COLORS["temporal"],
        marker="D",
        linewidth=2.0,
        markersize=5.5,
        linestyle="--",
        label="Onset error (h)",
        zorder=5,
    )[0]
    for xx, yy in zip(x, df["active_interval_iou_mean"]):
        ax_temporal.text(xx, yy + 0.012, f"{yy:.3f}", ha="center", va="bottom", fontsize=7.7, color=METRIC_COLORS["control"])
    for xx, yy in zip(x, df["onset_error_hours_mean"]):
        ax_temporal_r.text(xx + 0.04, yy + 0.055, f"{yy:.2f}h", ha="left", va="bottom", fontsize=7.5, color=METRIC_COLORS["temporal"])
    ax_temporal.set_xticks(x)
    ax_temporal.set_xticklabels(labels)
    ax_temporal.set_ylim(0.50, 0.94)
    ax_temporal_r.set_ylim(0.45, 2.45)
    ax_temporal.set_xlabel("Input window length")
    ax_temporal.set_ylabel("Active interval IoU")
    ax_temporal_r.set_ylabel("Onset error (h); lower is better")
    ax_temporal.set_title("B. Temporal boundary and false alarms", loc="left", fontweight="bold")
    style_axes_as_segments(ax_temporal, grid_axis="y")
    ax_temporal_r.grid(False)
    ax_temporal_r.spines["top"].set_visible(False)
    ax_temporal_r.spines["left"].set_visible(False)
    ax_temporal_r.spines["right"].set_color("#222222")
    ax_temporal_r.spines["right"].set_linewidth(0.8)
    ax_temporal_r.tick_params(axis="y", length=3, width=0.8)
    ymin_r, ymax_r = ax_temporal_r.get_ylim()
    ax_temporal_r.spines["right"].set_bounds(ymin_r, ymax_r)
    ax_temporal.legend([line_iou, line_onset], ["Active interval IoU", "Onset error (h)"], frameon=False, loc="upper right")

    fpr_note = "Normal FPR: " + " | ".join(f"{label}={fpr:.4f}" for label, fpr in zip(labels, df["normal_window_fpr"]))
    ax_temporal.text(
        0.02,
        0.045,
        fpr_note,
        transform=ax_temporal.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.5,
        color=METRIC_COLORS["fpr"],
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD", "alpha": 0.92},
    )

    fig.suptitle("CH4-F09b window-length tradeoff under the formal protocol", x=0.01, ha="left", fontweight="bold")
    fig.text(
        0.01,
        -0.055,
        "Source: CH4-F09b_formal_time_window_length_eval_summary.csv | Top-5 is omitted from the main panel because it is near saturated.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_dual_panel_tradeoff")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

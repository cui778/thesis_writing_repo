from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import CH4_SOURCE, METRIC_COLORS, TEXT_GREY, apply_style, ensure_out_dir, save_figure, style_axes


FIG_TAG = "04_CH4_window_length_tradeoff"
DATA_FILE = CH4_SOURCE / "CH4-F09b_formal_time_window_length_eval_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig").sort_values("window_hours").reset_index(drop=True)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    x = df["window_hours"].to_numpy(dtype=float)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.8), constrained_layout=True)
    series = [
        ("window_mrr", "Window MRR", METRIC_COLORS["mrr"], "o"),
        ("window_top5", "Window Top-5", METRIC_COLORS["top5"], "s"),
        ("scene_node_mrr", "Scene-node MRR", METRIC_COLORS["event"], "^"),
    ]
    for col, label, color, marker in series:
        y = df[col].to_numpy(dtype=float)
        ax1.plot(x, y, marker=marker, markersize=6, linewidth=1.9, color=color, label=label)
        for xx, yy in zip(x, y):
            ax1.text(xx, yy + 0.010, f"{yy:.3f}", ha="center", va="bottom", fontsize=7, color=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{int(v)}h" for v in x])
    ax1.set_ylim(0.60, 1.02)
    ax1.set_xlabel("Input window length")
    ax1.set_ylabel("Localization score")
    ax1.set_title("A. Spatial localization tradeoff", loc="left", fontweight="bold")
    style_axes(ax1)
    ax1.legend(frameon=False, loc="lower right")

    ax2b = ax2.twinx()
    iou = df["active_interval_iou_mean"].to_numpy(dtype=float)
    onset = df["onset_error_hours_mean"].to_numpy(dtype=float)
    l1 = ax2.plot(x, iou, marker="o", markersize=6, linewidth=1.9, color=METRIC_COLORS["control"], label="Interval IoU")[0]
    l2 = ax2b.plot(x, onset, marker="D", markersize=5.5, linewidth=1.8, linestyle="--", color=METRIC_COLORS["temporal"], label="Onset error")[0]
    for xx, yy in zip(x, iou):
        ax2.text(xx, yy + 0.010, f"{yy:.3f}", ha="center", va="bottom", fontsize=7, color=METRIC_COLORS["control"])
    for xx, yy in zip(x, onset):
        ax2b.text(xx, yy + 0.050, f"{yy:.2f}", ha="center", va="bottom", fontsize=7, color=METRIC_COLORS["temporal"])
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{int(v)}h" for v in x])
    ax2.set_ylim(0.60, 1.02)
    ax2.set_xlabel("Input window length")
    ax2.set_ylabel("Interval IoU")
    ax2b.set_ylabel("Onset error (h)")
    ax2b.set_ylim(0.65, max(onset) + 0.22)
    ax2.set_title("B. Temporal boundary recovery", loc="left", fontweight="bold")
    style_axes(ax2)
    ax2b.grid(False)
    ax2.legend([l1, l2], ["Interval IoU", "Onset error (h)"], frameon=False, loc="upper right")

    fig.text(
        0.01,
        -0.05,
        "Source: figures/ch4/source_data/CH4-F09b_formal_time_window_length_eval_summary.csv | Seed 42 trend analysis; used for scale tradeoff, not multi-seed stability.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_dual_panel_tradeoff")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

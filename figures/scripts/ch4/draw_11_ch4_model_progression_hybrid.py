from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import (
    CH4_SOURCE,
    METRIC_COLORS,
    MODEL_LABELS,
    MODEL_ORDER,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
)


"""
Scientific question:
As the diagnosis model moves from sequence-only to graph-aware and hydraulic
attention variants, do spatial ranking quality and false-alarm control improve
together?

Section: 4.4.3
Figure role: thesis/PPT model-progression figure; deliberately uses a hybrid
bar + line design instead of a heatmap.
"""


FIG_TAG = "11_CH4_model_progression_hybrid"
DATA_FILE = CH4_SOURCE / "CH4-F08_formal_model_comparison_multiseed_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df["model"] = pd.Categorical(df["model"], categories=MODEL_ORDER, ordered=True)
    df = df.sort_values("model").reset_index(drop=True)
    df["model_label"] = df["model"].astype(str).map(MODEL_LABELS)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)

    x = np.arange(len(df))
    width = 0.26
    fig, ax = plt.subplots(figsize=(11.2, 5.4), constrained_layout=True)
    ax2 = ax.twinx()

    bars_mrr = ax.bar(
        x - width / 2,
        df["mrr_mean"],
        yerr=df["mrr_std"],
        width=width,
        color=METRIC_COLORS["mrr"],
        capsize=3,
        label="MRR",
        error_kw={"elinewidth": 0.9, "capthick": 0.9, "ecolor": "#333333"},
    )
    bars_top1 = ax.bar(
        x + width / 2,
        df["top1_mean"],
        yerr=df["top1_std"],
        width=width,
        color=METRIC_COLORS["top1"],
        capsize=3,
        label="Top-1",
        error_kw={"elinewidth": 0.9, "capthick": 0.9, "ecolor": "#333333"},
    )
    line_top3 = ax.plot(
        x,
        df["top3_mean"],
        color=METRIC_COLORS["top3"],
        marker="o",
        markersize=6,
        linewidth=2.0,
        label="Top-3",
        zorder=4,
    )[0]
    line_fpr = ax2.plot(
        x,
        df["normal_window_fpr_mean"],
        color=METRIC_COLORS["fpr"],
        marker="D",
        markersize=5,
        linewidth=1.8,
        linestyle="--",
        label="Normal FPR",
        zorder=5,
    )[0]

    for bar in list(bars_mrr) + list(bars_top1):
        val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.018, f"{val:.2f}", ha="center", va="bottom", fontsize=7.2)
    for xx, yy in zip(x, df["top3_mean"]):
        ax.text(xx, yy + 0.018, f"{yy:.2f}", ha="center", va="bottom", fontsize=7.2, color=METRIC_COLORS["top3"])
    for xx, yy in zip(x, df["normal_window_fpr_mean"]):
        ax2.text(xx, yy + 0.0012, f"{yy:.4f}", ha="center", va="bottom", fontsize=7.1, color=METRIC_COLORS["fpr"])

    ax.set_xticks(x)
    ax.set_xticklabels(df["model_label"], rotation=18, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax2.set_ylim(0.0, max(0.050, float(df["normal_window_fpr_mean"].max()) * 1.25))
    ax.set_ylabel("Spatial localization score")
    ax2.set_ylabel("Normal Window FPR; lower is better")
    ax.set_title("CH4-F08 model progression: ranking quality vs false alarms", loc="left", fontweight="bold")
    style_axes_as_segments(ax, grid_axis="y")
    ax2.grid(False)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_color("#222222")
    ax2.spines["right"].set_linewidth(0.8)
    ax2.tick_params(axis="y", length=3, width=0.8)

    handles = [bars_mrr, bars_top1, line_top3, line_fpr]
    labels = ["MRR", "Top-1", "Top-3", "Normal FPR"]
    ax.legend(handles, labels, frameon=False, ncol=4, loc="upper left")

    fig.text(
        0.01,
        -0.055,
        "Source: CH4-F08_formal_model_comparison_multiseed_summary.csv | Bars/line show mean across seeds; error bars show sample std for MRR and Top-1.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_bar_line_dual_axis")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

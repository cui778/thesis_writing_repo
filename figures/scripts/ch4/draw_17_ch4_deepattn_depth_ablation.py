from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["savefig.dpi"] = 300

from _ch4_style import (
    CH4_SOURCE, METRIC_COLORS, TEXT_GREY, apply_style, ensure_out_dir,
    save_figure, style_axes_as_segments,
)

FIG_TAG = "17_CH4_deepattn_depth_ablation"
OUT_DIR = ensure_out_dir(FIG_TAG)
DATA_FILE = CH4_SOURCE / "CH4-F11_method_ablation_summary.csv"


def main() -> None:
    apply_style()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df = df[df["experiment"].eq("depth")].sort_values("layers").reset_index(drop=True)
    df["mrr_gain"] = df["mrr_mean"].diff()
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)

    x = df["layers"].to_numpy()
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(11.4, 4.8), gridspec_kw={"width_ratios": [1.45, 0.9]},
        constrained_layout=True,
    )
    for metric, label, marker in (
        ("mrr", "MRR", "o"), ("top1", "Top-1", "s"), ("top3", "Top-3", "^")
    ):
        ax_a.errorbar(
            x, df[f"{metric}_mean"], yerr=df[f"{metric}_std"],
            marker=marker, markersize=6, linewidth=1.9, capsize=3,
            color=METRIC_COLORS[metric], label=label,
        )
    ax_a.axvline(3, color="#4E79A7", linestyle="--", linewidth=1.0, alpha=0.7)
    ax_a.text(3.05, 0.34, "selected depth", color="#4E79A7", fontsize=8, rotation=90)
    ax_a.set_xticks(x)
    ax_a.set_ylim(0.18, 0.98)
    ax_a.set_xlabel("DeepAttn layers")
    ax_a.set_ylabel("Localization score")
    ax_a.set_title("A. Iterative aggregation improves ranking", loc="left", fontweight="bold")
    ax_a.legend(frameon=False, ncol=3, loc="lower right")
    style_axes_as_segments(ax_a, grid_axis="y")

    gains = df.dropna(subset=["mrr_gain"])
    colors = ["#59A14F" if value > 0.02 else "#A0A7AE" for value in gains["mrr_gain"]]
    ax_b.bar(gains["layers"].astype(str), gains["mrr_gain"], color=colors, width=0.55)
    for i, value in enumerate(gains["mrr_gain"]):
        ax_b.text(i, value + 0.008, f"+{value:.3f}", ha="center", fontsize=8)
    ax_b.set_ylim(0, max(0.36, gains["mrr_gain"].max() * 1.18))
    ax_b.set_xlabel("Added layer")
    ax_b.set_ylabel("Marginal MRR gain")
    ax_b.set_title("B. Gain saturates after L3", loc="left", fontweight="bold")
    style_axes_as_segments(ax_b, grid_axis="y")

    fig.text(
        0.01, -0.045,
        "Seeds 7/42/123. L4 improves mean MRR by only 0.006 over L3 while increasing Normal FPR; L3 remains the formal configuration.",
        fontsize=8, color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, FIG_TAG)


if __name__ == "__main__":
    main()

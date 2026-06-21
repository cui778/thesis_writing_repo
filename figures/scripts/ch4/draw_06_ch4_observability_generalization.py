from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import CH4_SOURCE, METRIC_COLORS, TEXT_GREY, apply_style, ensure_out_dir, save_figure, style_axes


FIG_TAG = "06_CH4_observability_generalization"
COUNTS_FILE = CH4_SOURCE / "CH4-F10b_candidate_observability_counts.csv"
PERF_FILE = CH4_SOURCE / "CH4-F10b_nodehold_observability_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    counts = pd.read_csv(COUNTS_FILE, encoding="utf-8-sig")
    perf = pd.read_csv(PERF_FILE, encoding="utf-8-sig")
    tier_order = ["direct", "near", "far"]
    colors = {"direct": METRIC_COLORS["control"], "near": METRIC_COLORS["event"], "far": METRIC_COLORS["temporal"]}
    counts["observability_tier"] = pd.Categorical(counts["observability_tier"], categories=tier_order, ordered=True)
    perf["observability_tier"] = pd.Categorical(perf["observability_tier"], categories=tier_order, ordered=True)
    counts = counts.sort_values("observability_tier")
    perf = perf.sort_values("observability_tier")
    counts.to_csv(OUT_DIR / f"{FIG_TAG}_candidate_counts.csv", index=False)
    perf.to_csv(OUT_DIR / f"{FIG_TAG}_nodehold_performance.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8), constrained_layout=True)
    x1 = np.arange(len(counts))
    ax1.bar(x1, counts["n_candidates"], color=[colors[t] for t in counts["observability_tier"].astype(str)], width=0.62)
    for x, val in zip(x1, counts["n_candidates"]):
        ax1.text(x, val + 0.7, f"{int(val)}", ha="center", va="bottom", fontsize=8)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(counts["observability_tier"].astype(str).str.title())
    ax1.set_ylabel("Number of candidate nodes")
    ax1.set_title("A. Candidate observability tiers", loc="left", fontweight="bold")
    style_axes(ax1)

    x2 = np.arange(len(perf))
    width = 0.22
    metrics = [("top1", "Top-1", METRIC_COLORS["top1"]), ("top3", "Top-3", METRIC_COLORS["top3"]), ("top5", "Top-5", METRIC_COLORS["top5"])]
    for offset, (col, label, color) in zip([-width, 0, width], metrics):
        vals = pd.to_numeric(perf[col], errors="coerce").to_numpy(dtype=float)
        bars = ax2.bar(x2 + offset, vals, width=width, color=color, label=label)
        for bar, val in zip(bars, vals):
            ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.018, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(perf["observability_tier"].astype(str).str.title())
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("Node-holdout hit rate")
    ax2.set_title("B. Node-holdout performance by tier", loc="left", fontweight="bold")
    style_axes(ax2)
    ax2.legend(frameon=False, ncol=3, loc="upper right")

    fig.text(
        0.01,
        -0.05,
        "Source: figures/ch4/source_data/CH4-F10b_candidate_observability_counts.csv and CH4-F10b_nodehold_observability_summary.csv | Recommended as backup/appendix evidence.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_tier_summary")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

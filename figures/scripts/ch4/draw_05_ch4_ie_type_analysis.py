from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import CH4_SOURCE, METRIC_COLORS, TEXT_GREY, apply_style, ensure_out_dir, save_figure, style_axes


FIG_TAG = "05_CH4_ie_type_analysis"
DATA_FILE = CH4_SOURCE / "CH4-F10a_formal_ie_type_group_multiseed_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df["defect_type"] = df["defect_type"].astype(str).str.upper()
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    wide = df.set_index("defect_type")

    panels = [
        ("Window-level", "window"),
        ("Event-level", "event"),
        ("Integrated scene-level", "integrated_scene"),
    ]
    colors = {"I": METRIC_COLORS["mrr"], "E": METRIC_COLORS["temporal"]}
    markers = {"I": "o", "E": "s"}

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.8), constrained_layout=True)
    x = np.array([1, 3, 5], dtype=float)
    for ax, (title, prefix) in zip(axes, panels):
        for defect_type in ["I", "E"]:
            means = np.array([wide.loc[defect_type, f"{prefix}_top{k}_mean"] for k in [1, 3, 5]], dtype=float)
            stds = np.array([wide.loc[defect_type, f"{prefix}_top{k}_std"] for k in [1, 3, 5]], dtype=float)
            ax.errorbar(
                x,
                means,
                yerr=stds,
                marker=markers[defect_type],
                markersize=6,
                linewidth=1.9,
                capsize=3,
                color=colors[defect_type],
                label=f"{defect_type} type",
            )
            for xx, yy in zip(x, means):
                ax.text(xx, yy + (0.012 if defect_type == "I" else -0.018), f"{yy:.3f}", ha="center", va="bottom" if defect_type == "I" else "top", fontsize=7, color=colors[defect_type])
        ax.set_xticks(x)
        ax.set_xticklabels(["Top-1", "Top-3", "Top-5"])
        ax.set_ylim(0.50, 1.03)
        ax.set_xlabel("Candidate list size K")
        ax.set_title(title, loc="left", fontweight="bold")
        style_axes(ax)
    axes[0].set_ylabel("Hit rate")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.04))
    fig.text(
        0.01,
        -0.05,
        "Source: figures/ch4/source_data/CH4-F10a_formal_ie_type_group_multiseed_summary.csv | Mean +/- std across seeds 7/42/123.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_topk_ladder")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

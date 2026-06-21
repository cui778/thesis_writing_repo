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

FIG_TAG = "18_CH4_path_prior_ablation"
OUT_DIR = ensure_out_dir(FIG_TAG)
DATA_FILE = CH4_SOURCE / "CH4-F11_method_ablation_summary.csv"
ORDER = ["Content-only", "Distance-only", "Full path prior"]


def main() -> None:
    apply_style()
    raw = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    rows = []
    mapping = {
        "deepattn_L3_content_only": "Content-only",
        "deepattn_L3_distance_only": "Distance-only",
        "deepattn_L3": "Full path prior",
    }
    for variant, label in mapping.items():
        row = raw[raw["variant"].eq(variant)].iloc[0].copy()
        row["label"] = label
        rows.append(row)
    df = pd.DataFrame(rows)
    df["label"] = pd.Categorical(df["label"], ORDER, ordered=True)
    df = df.sort_values("label").reset_index(drop=True)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)

    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(11.7, 4.8), gridspec_kw={"width_ratios": [1.45, 0.9]},
        constrained_layout=True,
    )
    y = np.arange(len(df))[::-1]
    offsets = {"mrr": 0.18, "top1": 0.0, "event_top1": -0.18}
    markers = {"mrr": "o", "top1": "s", "event_top1": "D"}
    labels = {"mrr": "MRR", "top1": "Top-1", "event_top1": "Event Top-1"}
    for metric in offsets:
        for i, row in df.iterrows():
            one_seed = int(row["n_seeds"]) == 1
            ax_a.errorbar(
                row[f"{metric}_mean"], y[i] + offsets[metric],
                xerr=None if one_seed else row[f"{metric}_std"],
                fmt=markers[metric], markersize=6,
                markerfacecolor="white" if one_seed else METRIC_COLORS[metric],
                markeredgecolor=METRIC_COLORS[metric],
                color=METRIC_COLORS[metric], capsize=2.5, linewidth=1.2,
                label=labels[metric] if i == 0 else None,
            )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(df["label"].astype(str))
    ax_a.set_xlim(0.58, 0.88)
    ax_a.set_xlabel("Ranking score")
    ax_a.set_title("A. Path information improves front-rank localization", loc="left", fontweight="bold")
    ax_a.legend(frameon=False, ncol=3, loc="upper left")
    style_axes_as_segments(ax_a, grid_axis="x")

    fpr = df["normal_window_fpr_mean"].to_numpy()
    ax_b.plot(fpr, y, color="#B7BDC5", linewidth=1.5)
    for i, row in df.iterrows():
        one_seed = int(row["n_seeds"]) == 1
        ax_b.plot(
            row["normal_window_fpr_mean"], y[i], "o", markersize=7,
            markerfacecolor="white" if one_seed else METRIC_COLORS["fpr"],
            markeredgecolor=METRIC_COLORS["fpr"],
        )
        ax_b.text(row["normal_window_fpr_mean"] + 0.00035, y[i], f"{row['normal_window_fpr_mean']:.4f}", va="center", fontsize=8)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(df["label"].astype(str))
    ax_b.set_xlim(0, 0.009)
    ax_b.set_xlabel("Normal Window FPR (lower is better)")
    ax_b.set_title("B. False-alarm control", loc="left", fontweight="bold")
    style_axes_as_segments(ax_b, grid_axis="x")

    fig.text(
        0.01, -0.045,
        "Filled markers: seeds 7/42/123. Hollow markers: seed42 mechanism probe only. Content-only retains physical reachability masking.",
        fontsize=8, color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, FIG_TAG)


if __name__ == "__main__":
    main()

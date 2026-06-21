from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import CH4_SOURCE, apply_style, ensure_out_dir, save_figure, style_axes, METRIC_COLORS, TEXT_GREY


FIG_TAG = "02_CH4_task_level_summary"
DATA_FILE = CH4_SOURCE / "CH4-F07_task_level_results_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def main() -> None:
    apply_style()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    formal = df.loc[df["section"].astype(str).eq("formal_mainline")].iloc[0]
    metrics = [
        ("active_f1", "Active F1", "Window detection", METRIC_COLORS["control"]),
        ("scene_f1", "Scene F1", "Scene alarm", METRIC_COLORS["control"]),
        ("mrr", "MRR", "Spatial ranking", METRIC_COLORS["mrr"]),
        ("top1", "Top-1", "Spatial ranking", METRIC_COLORS["top1"]),
        ("top3", "Top-3", "Spatial ranking", METRIC_COLORS["top3"]),
        ("top5", "Top-5", "Spatial ranking", METRIC_COLORS["top5"]),
    ]
    plot_df = pd.DataFrame(
        [{"metric": label, "family": family, "score": float(formal[col]), "color": color} for col, label, family, color in metrics]
    )
    plot_df.to_csv(OUT_DIR / f"{FIG_TAG}_formal_mainline.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
    x = np.arange(len(plot_df))
    bars = ax.bar(x, plot_df["score"], color=plot_df["color"], width=0.62)
    for bar, val in zip(bars, plot_df["score"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.014, f"{val:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["metric"], rotation=20, ha="right")
    ax.set_ylim(0.0, 1.06)
    ax.set_ylabel("Score")
    ax.set_title("CH4 formal mainline diagnosis summary", loc="left", fontweight="bold")
    style_axes(ax)
    fig.text(
        0.01,
        -0.05,
        "Source: figures/ch4/source_data/CH4-F07_task_level_results_summary.csv | Formal mainline only; historical and node-holdout rows are excluded.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_formal_mainline_bar")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

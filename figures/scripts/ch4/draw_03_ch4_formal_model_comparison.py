from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import (
    CH4_SOURCE,
    MODEL_LABELS,
    MODEL_ORDER,
    METRIC_COLORS,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes,
    style_heatmap_axes,
)


FIG_TAG = "03_CH4_formal_model_comparison"
DATA_FILE = CH4_SOURCE / "CH4-F08_formal_model_comparison_multiseed_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df["model"] = pd.Categorical(df["model"], categories=MODEL_ORDER, ordered=True)
    df = df.sort_values("model").reset_index(drop=True)
    df["model_label"] = df["model"].astype(str).map(MODEL_LABELS)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    return df


def plot_point_errorbar(df: pd.DataFrame) -> None:
    metrics = [("mrr", "MRR"), ("top1", "Top-1"), ("top3", "Top-3"), ("top5", "Top-5")]
    fig, ax = plt.subplots(figsize=(9.6, 5.0), constrained_layout=True)
    y = np.arange(len(df))[::-1]
    offsets = np.linspace(-0.18, 0.18, len(metrics))
    for offset, (metric, label) in zip(offsets, metrics):
        mean = pd.to_numeric(df[f"{metric}_mean"], errors="coerce")
        std = pd.to_numeric(df[f"{metric}_std"], errors="coerce")
        ax.errorbar(
            mean,
            y + offset,
            xerr=std,
            fmt="o",
            markersize=5.5,
            linewidth=1.2,
            capsize=3,
            color=METRIC_COLORS[metric],
            label=label,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(df["model_label"])
    ax.set_xlim(0.0, 1.02)
    ax.set_xlabel("Score")
    ax.set_title("CH4-F08 formal model comparison: spatial metrics", loc="left", fontweight="bold")
    style_axes(ax, grid_axis="x")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.63, -0.10))
    fig.text(
        0.01,
        -0.04,
        "Source: figures/ch4/source_data/CH4-F08_formal_model_comparison_multiseed_summary.csv | Mean +/- std across seeds under the formal protocol.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_spatial_point_errorbar")


def plot_heatmap(df: pd.DataFrame) -> None:
    cols = [
        ("mrr_mean", "MRR"),
        ("top1_mean", "Top-1"),
        ("top3_mean", "Top-3"),
        ("top5_mean", "Top-5"),
        ("event_top1_mean", "Event Top-1"),
        ("event_top3_mean", "Event Top-3"),
        ("event_top5_mean", "Event Top-5"),
        ("active_f1_mean", "Active F1"),
        ("scene_f1_mean", "Scene F1"),
    ]
    values = df[[c for c, _ in cols]].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(10.8, 4.7), constrained_layout=True)
    im = ax.imshow(values, aspect="auto", cmap="YlGnBu", vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels([label for _, label in cols], rotation=28, ha="right")
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df["model_label"])
    ax.set_title("CH4-F08 formal model comparison: performance fingerprint", loc="left", fontweight="bold")
    style_heatmap_axes(ax, values.shape[0], values.shape[1])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            color = "white" if values[i, j] >= 0.70 else "#222222"
            ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=7, color=color)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Score")
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_performance_heatmap")


def main() -> None:
    apply_style()
    df = load_data()
    plot_point_errorbar(df)
    plot_heatmap(df)
    print(OUT_DIR)


if __name__ == "__main__":
    main()

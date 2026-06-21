from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _ch4_style import CH4_SOURCE, apply_style, ensure_out_dir, save_figure, style_axes, METRIC_COLORS, TEXT_GREY


FIG_TAG = "01_CH4_main_model_multiseed"
DATA_FILE = CH4_SOURCE / "CH4-F06_main_model_multiseed.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        ("MRR", "MRR", "Spatial ranking"),
        ("Top-1", "Top-1", "Spatial ranking"),
        ("Top-3", "Top-3", "Spatial ranking"),
        ("Top-5", "Top-5", "Spatial ranking"),
        ("Event Top-1", "Event Top-1", "Event ranking"),
        ("Event Top-3", "Event Top-3", "Event ranking"),
        ("Event Top-5", "Event Top-5", "Event ranking"),
        ("active_f1", "Active F1", "Detection"),
        ("scene_f1", "Scene F1", "Detection"),
    ]
    rows = []
    for col, label, family in metrics:
        vals = pd.to_numeric(df[col], errors="coerce")
        rows.append({"metric": label, "family": family, "mean": vals.mean(), "std": vals.std(ddof=1)})
    fpr = 1.0 - pd.to_numeric(df["normal_window_fpr"], errors="coerce")
    rows.append({"metric": "1 - Normal FPR", "family": "Detection", "mean": fpr.mean(), "std": fpr.std(ddof=1)})
    return pd.DataFrame(rows)


def plot(summary: pd.DataFrame) -> None:
    color_map = {
        "Spatial ranking": METRIC_COLORS["mrr"],
        "Event ranking": METRIC_COLORS["event"],
        "Detection": METRIC_COLORS["control"],
    }
    summary.to_csv(OUT_DIR / f"{FIG_TAG}_summary_mean_std.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.8, 4.8), constrained_layout=True)
    x = np.arange(len(summary))
    colors = [color_map[v] for v in summary["family"]]
    bars = ax.bar(
        x,
        summary["mean"],
        yerr=summary["std"],
        capsize=3,
        color=colors,
        width=0.62,
        error_kw={"elinewidth": 0.9, "capthick": 0.9, "ecolor": "#333333"},
    )
    for bar, mean, std in zip(bars, summary["mean"], summary["std"]):
        ax.text(bar.get_x() + bar.get_width() / 2, mean + std + 0.012, f"{mean:.3f}", ha="center", va="bottom", fontsize=7.6)

    ax.set_xticks(x)
    ax.set_xticklabels(summary["metric"], rotation=28, ha="right")
    ax.set_ylim(0.0, 1.12)
    ax.set_ylabel("Score")
    ax.set_title("CH4 main model multi-seed performance", loc="left", fontweight="bold")
    style_axes(ax)
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[k]) for k in color_map]
    ax.legend(handles, list(color_map), frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0.0, 1.02))
    fig.text(
        0.01,
        -0.05,
        "Source: figures/ch4/source_data/CH4-F06_main_model_multiseed.csv | Seeds 7/42/123; error bars are sample standard deviation.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_performance_bar")


def main() -> None:
    apply_style()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    plot(summarize(df))
    print(OUT_DIR)


if __name__ == "__main__":
    main()

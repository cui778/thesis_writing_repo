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
    style_heatmap_axes_plain,
)


"""
Scientific question:
Does the fixed degree_N25 diagnosis protocol achieve low false alarms,
reliable scene alarms, and usable candidate localization at the same time?

Section: 4.4.1 and 4.4.2
Figure role: official main-result figure; preferred over ordinary bar snapshots.
"""


FIG_TAG = "07_CH4_main_result_fingerprint"
F06_FILE = CH4_SOURCE / "CH4-F06_main_model_multiseed.csv"
F07_FILE = CH4_SOURCE / "CH4-F07_task_level_results_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)

METRICS = [
    ("MRR", "MRR", "mrr", False),
    ("Top-1", "Top-1", "top1", False),
    ("Top-3", "Top-3", "top3", False),
    ("Event Top-1", "Event Top-1", "event_top1", False),
    ("Event Top-3", "Event Top-3", "event_top3", False),
    ("scene_f1", "Scene F1", "scene_f1", False),
    ("normal_window_fpr", "Normal FPR", "fpr", True),
]


def build_summary() -> pd.DataFrame:
    f06 = pd.read_csv(F06_FILE, encoding="utf-8-sig")
    f07 = pd.read_csv(F07_FILE, encoding="utf-8-sig")
    formal = f07.loc[f07["section"].astype(str).eq("formal_mainline")].iloc[0]
    rows = []
    for csv_col, label, color_key, lower_better in METRICS:
        vals = pd.to_numeric(f06[csv_col], errors="coerce")
        main_val = float(formal[csv_col]) if csv_col in formal.index and pd.notna(formal[csv_col]) else float(vals.mean())
        rows.append(
            {
                "metric": label,
                "mean": float(vals.mean()),
                "std": float(vals.std(ddof=1)),
                "formal_seed42": main_val,
                "lower_better": lower_better,
                "display_value": main_val,
                "heatmap_score": 1.0 - main_val if lower_better else main_val,
                "color": METRIC_COLORS[color_key],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / f"{FIG_TAG}_summary.csv", index=False)
    return out


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    summary = build_summary()

    value_map = summary.set_index("metric")
    heat = np.array(
        [
            [
                value_map.loc["MRR", "heatmap_score"],
                value_map.loc["Top-1", "heatmap_score"],
                value_map.loc["Top-3", "heatmap_score"],
            ],
            [
                value_map.loc["Scene F1", "heatmap_score"],
                value_map.loc["Event Top-1", "heatmap_score"],
                value_map.loc["Event Top-3", "heatmap_score"],
            ],
            [
                value_map.loc["Normal FPR", "heatmap_score"],
                np.nan,
                np.nan,
            ],
        ],
        dtype=float,
    )
    heat_cmap = plt.get_cmap("YlGnBu").copy()
    heat_cmap.set_bad("#F2F2F2")
    fig = plt.figure(figsize=(9.8, 5.2), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[0.95, 1.35])
    ax_hm = fig.add_subplot(gs[0, 0])
    ax_forest = fig.add_subplot(gs[0, 1])

    masked_heat = np.ma.masked_invalid(heat)
    im = ax_hm.imshow(masked_heat, cmap=heat_cmap, vmin=0.0, vmax=1.0, aspect="equal")
    ax_hm.set_xticks(np.arange(3))
    ax_hm.set_xticklabels(["Primary", "Top-1", "Top-3"])
    ax_hm.set_yticks(np.arange(3))
    ax_hm.set_yticklabels(["Window ranking", "Scene/event", "False alarm"])
    ax_hm.set_title("A. Diagnosis fingerprint", loc="left", fontweight="bold")
    style_heatmap_axes_plain(ax_hm)
    text_grid = [
        ["MRR\n0.825", "Top-1\n0.719", "Top-3\n0.919"],
        ["Scene F1\n0.992", "Event Top-1\n0.768", "Event Top-3\n0.951"],
        ["Normal FPR\n0.0005", "", ""],
    ]
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            if not text_grid[i][j]:
                ax_hm.text(j, i, "not used", ha="center", va="center", fontsize=7, color="#888888")
                continue
            color = "white" if heat[i, j] >= 0.70 else "#222222"
            ax_hm.text(j, i, text_grid[i][j], ha="center", va="center", fontsize=7.5, color=color)
    cbar = fig.colorbar(im, ax=ax_hm, fraction=0.046, pad=0.04)
    cbar.set_label("Transformed score")

    plot_df = summary.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot_df))
    xvals = plot_df["display_value"].to_numpy(dtype=float)
    xerr = plot_df["std"].fillna(0.0).to_numpy(dtype=float)
    for i, row in plot_df.iterrows():
        if row["metric"] == "Normal FPR":
            ax_forest.plot(row["display_value"], y[i], "o", color=row["color"], markersize=7)
            ax_forest.text(row["display_value"] + 0.018, y[i], f"{row['display_value']:.4f}", va="center", fontsize=8, color=row["color"])
        else:
            ax_forest.errorbar(
                xvals[i],
                y[i],
                xerr=xerr[i],
                fmt="o",
                capsize=3,
                color=row["color"],
                ecolor=row["color"],
                markersize=6,
                linewidth=1.1,
            )
            ax_forest.text(min(xvals[i] + xerr[i] + 0.025, 1.02), y[i], f"{xvals[i]:.3f}", va="center", fontsize=8, color=row["color"])
    ax_forest.axvline(0.80, color="#888888", linewidth=0.8, linestyle="--", alpha=0.55)
    ax_forest.set_yticks(y)
    ax_forest.set_yticklabels(plot_df["metric"])
    ax_forest.set_xlim(0.0, 1.05)
    ax_forest.set_xlabel("Raw metric value")
    ax_forest.set_title("B. Multi-seed summary and formal seed42", loc="left", fontweight="bold")
    style_axes_as_segments(ax_forest, grid_axis="x")

    fig.text(
        0.01,
        -0.05,
        "Source: CH4-F06_main_model_multiseed.csv and CH4-F07_task_level_results_summary.csv | Normal FPR is kept as a low-is-better raw value; heatmap uses 1-FPR.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_fingerprint_forest")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

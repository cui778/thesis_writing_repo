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
Do I/E defect-type gaps and direct/near/far observability jointly explain
localization difficulty and node-holdout generalization limits?

Sections: 4.4.6, 4.5.1, and 4.5.2
Figure role: mechanism-explanation figure for thesis and defense slides.
"""


FIG_TAG = "10_CH4_ie_observability_mechanism"
IE_FILE = CH4_SOURCE / "CH4-F10a_formal_ie_type_group_multiseed_summary.csv"
COUNTS_FILE = CH4_SOURCE / "CH4-F10b_candidate_observability_counts.csv"
OBS_FILE = CH4_SOURCE / "CH4-F10b_nodehold_observability_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)

IE_METRICS = [
    ("window_mrr_mean", "Window MRR", "mrr"),
    ("window_top1_mean", "Window Top-1", "top1"),
    ("window_top3_mean", "Window Top-3", "top3"),
    ("event_mrr_mean", "Event MRR", "event_top1"),
    ("event_top1_mean", "Event Top-1", "event_top1"),
    ("event_top3_mean", "Event Top-3", "event_top3"),
]


def build_ie_gap(ie: pd.DataFrame) -> pd.DataFrame:
    ie = ie.copy()
    ie["defect_type"] = ie["defect_type"].astype(str).str.upper()
    wide = ie.set_index("defect_type")
    rows = []
    for col, label, color_key in IE_METRICS:
        i_val = float(wide.loc["I", col])
        e_val = float(wide.loc["E", col])
        rows.append(
            {
                "metric": label,
                "I": i_val,
                "E": e_val,
                "gap_I_minus_E": i_val - e_val,
                "color": METRIC_COLORS[color_key],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / f"{FIG_TAG}_ie_gap.csv", index=False)
    return out


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    ie = pd.read_csv(IE_FILE, encoding="utf-8-sig")
    counts = pd.read_csv(COUNTS_FILE, encoding="utf-8-sig")
    obs = pd.read_csv(OBS_FILE, encoding="utf-8-sig")
    gap = build_ie_gap(ie)
    counts.to_csv(OUT_DIR / f"{FIG_TAG}_candidate_counts.csv", index=False)
    obs.to_csv(OUT_DIR / f"{FIG_TAG}_observability_performance.csv", index=False)

    fig = plt.figure(figsize=(12.0, 5.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0])
    ax_dumb = fig.add_subplot(gs[0, 0])
    ax_hm = fig.add_subplot(gs[0, 1])

    plot_gap = gap.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot_gap))
    for i, row in plot_gap.iterrows():
        ax_dumb.plot([row["E"], row["I"]], [y[i], y[i]], color=row["color"], linewidth=2.2, alpha=0.85)
        ax_dumb.plot(row["E"], y[i], "s", color="#E15759", markersize=6, label="E type" if i == 0 else None)
        ax_dumb.plot(row["I"], y[i], "o", color="#4E79A7", markersize=6, label="I type" if i == 0 else None)
        ax_dumb.text(max(row["E"], row["I"]) + 0.012, y[i], f"gap {row['gap_I_minus_E']:+.3f}", va="center", fontsize=7.5, color=row["color"])
    ax_dumb.set_yticks(y)
    ax_dumb.set_yticklabels(plot_gap["metric"])
    ax_dumb.set_xlim(0.60, 1.03)
    ax_dumb.set_xlabel("Localization score")
    ax_dumb.set_title("A. I/E localization gap", loc="left", fontweight="bold")
    style_axes_as_segments(ax_dumb, grid_axis="x")
    ax_dumb.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.70, -0.08))

    tier_order = ["direct", "near", "far"]
    obs = obs.copy()
    obs["observability_tier"] = pd.Categorical(obs["observability_tier"], categories=tier_order, ordered=True)
    obs = obs.sort_values("observability_tier")
    count_map = counts.set_index("observability_tier")["n_candidates"].to_dict()
    heat_cols = [("top1", "Top-1"), ("top3", "Top-3"), ("top5", "Top-5")]
    heat = obs[[c for c, _ in heat_cols]].to_numpy(dtype=float)
    im = ax_hm.imshow(heat, cmap="YlGnBu", vmin=0.0, vmax=1.0, aspect="equal")
    ax_hm.set_xticks(np.arange(len(heat_cols)))
    ax_hm.set_xticklabels([label for _, label in heat_cols])
    y_labels = [f"{str(t).title()} (n={int(count_map.get(str(t), 0))})" for t in obs["observability_tier"].astype(str)]
    ax_hm.set_yticks(np.arange(len(obs)))
    ax_hm.set_yticklabels(y_labels)
    ax_hm.set_title("B. Node-holdout observability fingerprint", loc="left", fontweight="bold")
    style_heatmap_axes_plain(ax_hm)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            color = "white" if heat[i, j] >= 0.70 else "#222222"
            ax_hm.text(j, i, f"{heat[i, j]:.2f}", ha="center", va="center", fontsize=8, color=color)
    cbar = fig.colorbar(im, ax=ax_hm, fraction=0.035, pad=0.03)
    cbar.set_label("Hit rate")

    fig.text(
        0.01,
        -0.05,
        "Source: CH4-F10a_formal_ie_type_group_multiseed_summary.csv, CH4-F10b_candidate_observability_counts.csv, and CH4-F10b_nodehold_observability_summary.csv.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_dumbbell_observability_heatmap")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

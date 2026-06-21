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

FIG_TAG = "16_CH4_grouped_model_comparison"
OUT_DIR = ensure_out_dir(FIG_TAG)
BASE_FILE = CH4_SOURCE / "CH4-F08_formal_model_comparison_multiseed_summary.csv"
ABL_FILE = CH4_SOURCE / "CH4-F11_method_ablation_summary.csv"

ORDER = [
    "GRU", "GRU-GCN", "LSTM-GraphSAGE",
    "Hydraulic-Inverse-GRU", "Hydraulic-Inverse-LSTM", "DeepAttn-L3",
]
GROUPS = {
    "Non-path references": ["GRU", "GRU-GCN", "LSTM-GraphSAGE"],
    "Single-layer path models": ["Hydraulic-Inverse-GRU", "Hydraulic-Inverse-LSTM"],
    "Proposed multi-layer model": ["DeepAttn-L3"],
}
COLORS = {
    "Non-path references": "#A7B8CC",
    "Single-layer path models": "#E6A15A",
    "Proposed multi-layer model": "#4E79A7",
}


def load_data() -> pd.DataFrame:
    base = pd.read_csv(BASE_FILE, encoding="utf-8-sig")
    rename = {
        "gru_only": "GRU",
        "gru_gcn": "GRU-GCN",
        "lstm_graphsage_edge": "LSTM-GraphSAGE",
        "hydraulic_inverse": "Hydraulic-Inverse-GRU",
        "hydraulic_inverse_deepattn": "DeepAttn-L3",
    }
    base["label"] = base["model"].map(rename)
    lstm = pd.read_csv(ABL_FILE, encoding="utf-8-sig")
    lstm = lstm[lstm["variant"].eq("hydraulic_inverse_LSTM")].copy()
    lstm["label"] = "Hydraulic-Inverse-LSTM"
    cols = [
        "label", "mrr_mean", "mrr_std", "top1_mean", "top1_std",
        "top3_mean", "top3_std", "event_top1_mean", "event_top1_std",
        "normal_window_fpr_mean", "normal_window_fpr_std",
    ]
    df = pd.concat([base[cols], lstm[cols]], ignore_index=True)
    df["label"] = pd.Categorical(df["label"], ORDER, ordered=True)
    df = df.sort_values("label").reset_index(drop=True)
    for group, labels in GROUPS.items():
        df.loc[df["label"].astype(str).isin(labels), "group"] = group
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    return df


def main() -> None:
    apply_style()
    df = load_data()
    y = np.arange(len(df))[::-1]
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(12.2, 5.5), gridspec_kw={"width_ratios": [1.05, 1.35]},
        constrained_layout=True,
    )

    for group, labels in GROUPS.items():
        idx = [i for i, label in enumerate(df["label"].astype(str)) if label in labels]
        yy = y[idx]
        ax_a.axhspan(yy.min() - 0.42, yy.max() + 0.42, color=COLORS[group], alpha=0.09)
        ax_b.axhspan(yy.min() - 0.42, yy.max() + 0.42, color=COLORS[group], alpha=0.09)
        ax_a.text(
            0.985, yy.max() + 0.27, group, ha="right", va="top",
            fontsize=7.4, color=COLORS[group], fontweight="bold",
        )

    for i, row in df.iterrows():
        color = COLORS[row["group"]]
        ax_a.errorbar(
            row["mrr_mean"], y[i], xerr=row["mrr_std"], fmt="o",
            color=color, ecolor=color, capsize=3, markersize=7, linewidth=1.3,
        )
        ax_a.text(row["mrr_mean"] + 0.018, y[i], f"{row['mrr_mean']:.3f}", va="center", fontsize=8)

    offsets = {"top1": -0.15, "top3": 0.15}
    markers = {"top1": "s", "top3": "^"}
    for metric in ("top1", "top3"):
        ax_b.errorbar(
            df[f"{metric}_mean"], y + offsets[metric],
            xerr=df[f"{metric}_std"], fmt=markers[metric],
            color=METRIC_COLORS[metric], ecolor=METRIC_COLORS[metric],
            capsize=2.5, markersize=6, linewidth=1.2,
            label=metric.replace("top", "Top-"),
        )

    for ax in (ax_a, ax_b):
        ax.set_yticks(y)
        ax.set_yticklabels(df["label"].astype(str))
        ax.set_xlim(0.10, 1.01)
        style_axes_as_segments(ax, grid_axis="x")

    ax_a.set_xlabel("MRR (mean ± std)")
    ax_a.set_title("A. Grouped model comparison", loc="left", fontweight="bold")
    ax_b.set_xlabel("Localization recall (mean ± std)")
    ax_b.set_title("B. Top-k ranking quality", loc="left", fontweight="bold")
    ax_b.legend(frameon=False, loc="lower right")

    fig.text(
        0.01, -0.045,
        "Groups encode evidence roles, not a single architectural ladder. All values use seeds 7/42/123 under the frozen formal protocol.",
        fontsize=8, color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, FIG_TAG)


if __name__ == "__main__":
    main()

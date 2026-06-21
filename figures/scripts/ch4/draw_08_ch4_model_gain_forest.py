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
    style_axes_as_segments,
    style_heatmap_axes_plain,
)


"""
Scientific question:
Where does hydraulic_inverse_deepattn gain over sequence-only and simpler
graph baselines under the formal protocol?

Section: 4.4.3
Figure role: official model-comparison core figure.
"""


FIG_TAG = "08_CH4_model_gain_forest"
DATA_FILE = CH4_SOURCE / "CH4-F08_formal_model_comparison_multiseed_summary.csv"
OUT_DIR = ensure_out_dir(FIG_TAG)

METRICS = [
    ("mrr", "MRR", "mrr", False),
    ("top1", "Top-1", "top1", False),
    ("top3", "Top-3", "top3", False),
    ("event_top1", "Event Top-1", "event_top1", False),
    ("event_top3", "Event Top-3", "event_top3", False),
    ("normal_window_fpr", "Normal FPR", "fpr", True),
]
MAIN_MODEL = "hydraulic_inverse_deepattn"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df["model"] = pd.Categorical(df["model"], categories=MODEL_ORDER, ordered=True)
    df = df.sort_values("model").reset_index(drop=True)
    df["model_label"] = df["model"].astype(str).map(MODEL_LABELS)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)
    return df


def build_delta(df: pd.DataFrame) -> pd.DataFrame:
    main = df.loc[df["model"].astype(str).eq(MAIN_MODEL)].iloc[0]
    others = df.loc[~df["model"].astype(str).eq(MAIN_MODEL)].copy()
    rows = []
    for base, label, color_key, lower_better in METRICS:
        mean_col = f"{base}_mean"
        std_col = f"{base}_std"
        if lower_better:
            best_idx = pd.to_numeric(others[mean_col], errors="coerce").idxmin()
            delta = float(others.loc[best_idx, mean_col]) - float(main[mean_col])
        else:
            best_idx = pd.to_numeric(others[mean_col], errors="coerce").idxmax()
            delta = float(main[mean_col]) - float(others.loc[best_idx, mean_col])
        rows.append(
            {
                "metric": label,
                "main_mean": float(main[mean_col]),
                "main_std": float(main.get(std_col, 0.0)),
                "best_non_main_model": str(others.loc[best_idx, "model"]),
                "best_non_main_mean": float(others.loc[best_idx, mean_col]),
                "delta_in_favor_of_main": delta,
                "lower_better": lower_better,
                "color": METRIC_COLORS[color_key],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / f"{FIG_TAG}_delta_vs_best_non_main.csv", index=False)
    return out


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    df = load_data()
    delta = build_delta(df)

    heat_cols = [f"{m[0]}_mean" for m in METRICS]
    heat = df[heat_cols].to_numpy(dtype=float)
    heat[:, -1] = 1.0 - heat[:, -1]

    fig = plt.figure(figsize=(12.0, 5.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0])
    ax_hm = fig.add_subplot(gs[0, 0])
    ax_delta = fig.add_subplot(gs[0, 1])

    im = ax_hm.imshow(heat, cmap="YlGnBu", vmin=0.0, vmax=1.0, aspect="equal")
    ax_hm.set_xticks(np.arange(len(METRICS)))
    ax_hm.set_xticklabels([m[1] for m in METRICS], rotation=28, ha="right")
    ax_hm.set_yticks(np.arange(len(df)))
    ax_hm.set_yticklabels(df["model_label"])
    ax_hm.set_title("A. Model x metric fingerprint", loc="left", fontweight="bold")
    style_heatmap_axes_plain(ax_hm)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            raw = df.iloc[i][heat_cols[j]]
            text = f"{raw:.4f}" if METRICS[j][3] else f"{raw:.2f}"
            color = "white" if heat[i, j] >= 0.70 else "#222222"
            ax_hm.text(j, i, text, ha="center", va="center", fontsize=6.8, color=color)
    cbar = fig.colorbar(im, ax=ax_hm, fraction=0.03, pad=0.025)
    cbar.set_label("Score; FPR transformed to 1-FPR")

    plot_delta = delta.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot_delta))
    for i, row in plot_delta.iterrows():
        ax_delta.plot([0, row["delta_in_favor_of_main"]], [y[i], y[i]], color=row["color"], linewidth=2.0)
        ax_delta.plot(row["delta_in_favor_of_main"], y[i], "o", color=row["color"], markersize=7)
        ax_delta.text(row["delta_in_favor_of_main"] + 0.012, y[i], f"{row['delta_in_favor_of_main']:+.3f}", va="center", fontsize=8, color=row["color"])
    ax_delta.axvline(0, color="#333333", linewidth=0.8)
    ax_delta.set_yticks(y)
    ax_delta.set_yticklabels(plot_delta["metric"])
    ax_delta.set_xlim(-0.04, max(0.12, float(delta["delta_in_favor_of_main"].max()) + 0.10))
    ax_delta.set_xlabel("Gain over best non-main baseline")
    ax_delta.set_title("B. DeepAttn advantage", loc="left", fontweight="bold")
    style_axes_as_segments(ax_delta, grid_axis="x")

    fig.text(
        0.01,
        -0.05,
        "Source: CH4-F08_formal_model_comparison_multiseed_summary.csv | Positive delta means hydraulic_inverse_deepattn is better; for Normal FPR, lower is better.",
        ha="left",
        va="top",
        fontsize=8,
        color=TEXT_GREY,
    )
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_fingerprint_delta_forest")
    print(OUT_DIR)


if __name__ == "__main__":
    main()

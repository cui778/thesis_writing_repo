from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_repo_root(start: Path) -> Path:
    for path in [start.resolve(), *start.resolve().parents]:
        if (path / "figures/ch5/source_data").exists():
            return path
    raise FileNotFoundError("Cannot find thesis_writing_repo")


REPO_ROOT = find_repo_root(Path(__file__))
FIG_TAG = "10_CH5_embedding_source_ablation"
DATA_FILE = REPO_ROOT / "figures/ch5/source_data/CH5-targeted_supplements_by_run.csv"
OUT_DIR = REPO_ROOT / "figures/ch5/generated_results" / FIG_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRIC_COLORS = {
    "mrr": "#4E79A7", "top1": "#F28E2B", "top3": "#59A14F",
    "event_top1": "#B07AA1",
}
ORDER = ["Topology-Diversity", "Coordinate-Diversity", "Embedding-Guided"]

plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 300, "font.family": "DejaVu Sans",
    "axes.unicode_minus": False, "svg.fonttype": "none", "font.size": 9.5,
})


def style_axes(ax: plt.Axes, grid_axis: str = "x") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=3, width=0.8)
    ax.grid(axis=grid_axis, linestyle="--", linewidth=0.5, alpha=0.3)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    ax.spines["bottom"].set_bounds(xmin, xmax)
    ax.spines["left"].set_bounds(ymin, ymax)


def save(fig: plt.Figure) -> None:
    fig.savefig(OUT_DIR / f"{FIG_TAG}.png", bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{FIG_TAG}.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df = df[df["experiment"].eq("embedding_source_ablation")].copy()
    df["method"] = pd.Categorical(df["method"], ORDER, ordered=True)
    df = df.sort_values("method").reset_index(drop=True)
    df["delta_mrr_vs_eg"] = df["mrr"] - float(df.loc[df["method"].astype(str).eq("Embedding-Guided"), "mrr"].iloc[0])
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False)

    y = np.arange(len(df))[::-1]
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(11.4, 4.6), gridspec_kw={"width_ratios": [1.45, 0.8]},
        constrained_layout=True,
    )
    offsets = {"mrr": 0.24, "top1": 0.08, "top3": -0.08, "event_top1": -0.24}
    markers = {"mrr": "o", "top1": "s", "top3": "^", "event_top1": "D"}
    labels = {"mrr": "MRR", "top1": "Top-1", "top3": "Top-3", "event_top1": "Event Top-1"}
    for metric in offsets:
        ax_a.scatter(
            df[metric], y + offsets[metric], s=44, marker=markers[metric],
            color=METRIC_COLORS[metric], label=labels[metric], zorder=3,
        )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(df["method"].astype(str))
    ax_a.set_xlim(0.63, 1.00)
    ax_a.set_xlabel("Localization score (seed42)")
    ax_a.set_title("A. Same selector, different node representations", loc="left", fontweight="bold")
    ax_a.legend(frameon=False, ncol=2, loc="lower right")
    style_axes(ax_a)

    eg = float(df.loc[df["method"].astype(str).eq("Embedding-Guided"), "mrr"].iloc[0])
    deltas = eg - df["mrr"]
    ax_b.axvline(0, color="#333333", linewidth=0.8)
    for i, value in enumerate(deltas):
        color = "#76B7B2" if value == 0 else "#A7B8CC"
        ax_b.plot([0, value], [y[i], y[i]], color=color, linewidth=2)
        ax_b.plot(value, y[i], "o", color=color, markersize=7)
        ax_b.text(value + 0.005, y[i], f"{value:+.3f}", va="center", fontsize=8)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(df["method"].astype(str))
    ax_b.set_xlim(-0.01, 0.11)
    ax_b.set_xlabel("E-G MRR advantage")
    ax_b.set_title("B. Diagnostic representation gain", loc="left", fontweight="bold")
    style_axes(ax_b)

    fig.text(
        0.01, -0.045,
        "All layouts use the identical max-min diversity rule and N=25; only the node representation is changed. Seed42 mechanism ablation.",
        fontsize=8, color="#666666",
    )
    save(fig)


if __name__ == "__main__":
    main()

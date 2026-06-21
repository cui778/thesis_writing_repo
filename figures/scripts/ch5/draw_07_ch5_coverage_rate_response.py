# -*- coding: utf-8 -*-
"""
Draw Chapter 5 Figure 07: coverage-rate controlled response.

Scientific question:
    Under the fixed Chapter-4 diagnosis protocol, does better structural
    coverage of defect nodes translate into better localization performance?

Source data:
    script2_new/chapter5_layout_optimization/outputs/coverage_rate_controlled/
        coverage_rate_controlled_layout_summary.csv
    script2_new/outputs/reports/last_run_metrics_<output_tag>.json

Output directory:
    figures/ch5/generated_results/07_CH5_coverage_rate_response/

Generated files:
    07_CH5_coverage_rate_response_cleaned.csv
    07_CH5_coverage_rate_response_coverage_vs_mrr.png/.svg
    07_CH5_coverage_rate_response_metric_facets.png/.svg

Notes:
    - No PDF output.
    - SVG text remains editable.
    - This is a mechanism validation figure, not a replacement for the
      multi-method main result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "figures" / "ch5" / "source_data").exists():
            return p
    raise FileNotFoundError("Cannot find thesis_writing_repo root.")


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = find_repo_root(SCRIPT_PATH)
WORKSPACE_ROOT = REPO_ROOT.parent

FIG_NO = "07"
FIG_TAG = f"{FIG_NO}_CH5_coverage_rate_response"

SOURCE_DIR = (
    WORKSPACE_ROOT
    / "script2_new"
    / "chapter5_layout_optimization"
    / "outputs"
    / "coverage_rate_controlled"
)
SUMMARY_FILE = SOURCE_DIR / "coverage_rate_controlled_layout_summary.csv"

OUT_DIR = REPO_ROOT / "figures" / "ch5" / "generated_results" / FIG_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAVE_FORMATS = ["png", "svg"]

plt.rcParams["figure.dpi"] = 160
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["svg.fonttype"] = "none"

LEVEL_COLORS = {
    "low": "#4E79A7",
    "mid": "#59A14F",
    "high": "#F28E2B",
    "very_high": "#E15759",
}

METRIC_COLORS = {
    "mrr": "#4E79A7",
    "top1": "#F28E2B",
    "top3": "#59A14F",
    "event_top1": "#B07AA1",
    "event_top3": "#76B7B2",
}

METRIC_LABELS = {
    "mrr": "MRR",
    "top1": "Top-1",
    "top3": "Top-3",
    "event_top1": "Event Top-1",
    "event_top3": "Event Top-3",
    "normal_window_fpr": "Normal FPR",
    "scene_f1": "Scene F1",
}

AXIS_COLOR = "black"
SPINE_WIDTH = 1.0
TICK_WIDTH = 0.9


def save_figure(fig: plt.Figure, basename: str) -> None:
    for ext in SAVE_FORMATS:
        fig.savefig(OUT_DIR / f"{basename}.{ext}", bbox_inches="tight", transparent=False)
    plt.close(fig)


def style_axes_as_segments(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_linewidth(SPINE_WIDTH)
    ax.spines["left"].set_linewidth(SPINE_WIDTH)
    ax.tick_params(axis="both", which="both", direction="out", width=TICK_WIDTH, length=3.5)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.spines["bottom"].set_bounds(x0, x1)
    ax.spines["left"].set_bounds(y0, y1)


def flatten_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    aliases = {
        "mrr": ["mrr"],
        "top1": ["topk_recall_1", "top1"],
        "top3": ["topk_recall_3", "top3"],
        "top5": ["topk_recall_5", "top5"],
        "event_top1": ["event_level_top1", "event_top1"],
        "event_top3": ["event_level_top3", "event_top3"],
        "event_top5": ["event_level_top5", "event_top5"],
        "normal_window_fpr": ["normal_window_fpr"],
        "scene_f1": ["scene_f1"],
        "active_f1": ["active_f1"],
    }

    def walk(obj: Any, out: Dict[str, Any]) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Preserve the first occurrence so top-level formal metrics are
                # not overwritten by scenario-level fields with the same name.
                out.setdefault(str(key), value)
                walk(value, out)
        elif isinstance(obj, list):
            for value in obj:
                walk(value, out)

    # The training report stores the formal aggregate metrics at the top
    # level. Seed the lookup with those values before recursively searching
    # optional nested summaries.
    flat: Dict[str, Any] = dict(data)
    walk(data, flat)
    metrics: Dict[str, float] = {}
    for dst, keys in aliases.items():
        for key in keys:
            if key in flat:
                try:
                    metrics[dst] = float(flat[key])
                    break
                except (TypeError, ValueError):
                    continue
    return metrics


def load_eval_table() -> pd.DataFrame:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Missing layout summary: {SUMMARY_FILE}\n"
            "Run build_coverage_rate_controlled_layouts.py first."
        )
    summary = pd.read_csv(SUMMARY_FILE)
    required = {
        "budget",
        "coverage_level",
        "variant",
        "coverage_rate",
        "far_ratio",
        "mean_hop",
        "output_tag",
        "metrics_file",
    }
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"Layout summary missing columns: {sorted(missing)}")

    rows = []
    missing_metrics = []
    for row in summary.itertuples(index=False):
        metrics_path = Path(str(getattr(row, "metrics_file")))
        if not metrics_path.exists():
            missing_metrics.append(metrics_path)
            continue
        metrics = flatten_metrics(json.loads(metrics_path.read_text(encoding="utf-8")))
        record = row._asdict()
        record.update(metrics)
        rows.append(record)

    if not rows:
        preview = "\n".join(str(p) for p in missing_metrics[:5])
        raise FileNotFoundError(
            "No coverage-rate controlled evaluation metrics were found.\n"
            "Run run_coverage_rate_controlled_eval.py first. Missing examples:\n"
            f"{preview}"
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(["budget", "coverage_rate", "coverage_level", "variant"]).reset_index(drop=True)
    df.to_csv(OUT_DIR / f"{FIG_TAG}_cleaned.csv", index=False, encoding="utf-8-sig")
    return df


def plot_coverage_vs_mrr(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    budgets = sorted(df["budget"].unique())
    markers = {budget: marker for budget, marker in zip(budgets, ["o", "s", "^", "D", "P"])}

    for level, sub in df.groupby("coverage_level"):
        for budget, ss in sub.groupby("budget"):
            ax.scatter(
                ss["coverage_rate"],
                ss["mrr"],
                s=80 + 25 * (1.0 - ss["far_ratio"].astype(float)),
                marker=markers.get(budget, "o"),
                color=LEVEL_COLORS.get(str(level), "#7F7F7F"),
                edgecolor="white",
                linewidth=0.7,
                alpha=0.88,
                label=f"{level}, N={budget}",
            )

    if len(df) >= 3:
        x = df["coverage_rate"].astype(float).to_numpy()
        y = df["mrr"].astype(float).to_numpy()
        coef = np.polyfit(x, y, deg=1)
        xp = np.linspace(max(0.0, x.min() - 0.03), min(1.0, x.max() + 0.03), 80)
        ax.plot(xp, coef[0] * xp + coef[1], color="#222222", lw=1.3, alpha=0.8, label="linear trend")

    ax.set_xlabel("Defect-node structural coverage rate")
    ax.set_ylabel("MRR")
    ax.set_xlim(0.0, 1.02)
    y_min = max(0.0, float(df["mrr"].min()) - 0.06)
    y_max = min(1.02, float(df["mrr"].max()) + 0.04)
    ax.set_ylim(y_min, y_max)
    ax.grid(axis="y", color="#E6E6E6", lw=0.8)
    ax.set_title("Coverage-rate controlled layout response", fontsize=12, pad=10)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="lower right")
    style_axes_as_segments(ax)
    save_figure(fig, f"{FIG_TAG}_coverage_vs_mrr")


def plot_metric_facets(df: pd.DataFrame) -> None:
    metrics = [m for m in ["mrr", "top1", "top3", "event_top1"] if m in df.columns]
    n = len(metrics)
    fig, axes = plt.subplots(1, n, figsize=(3.3 * n, 3.8), sharex=True)
    if n == 1:
        axes = [axes]

    for ax, metric in zip(axes, metrics):
        for level, sub in df.groupby("coverage_level"):
            ax.scatter(
                sub["coverage_rate"],
                sub[metric],
                s=48,
                color=LEVEL_COLORS.get(str(level), "#7F7F7F"),
                edgecolor="white",
                linewidth=0.6,
                alpha=0.86,
            )
        if len(df) >= 3:
            x = df["coverage_rate"].astype(float).to_numpy()
            y = df[metric].astype(float).to_numpy()
            coef = np.polyfit(x, y, deg=1)
            xp = np.linspace(max(0.0, x.min() - 0.03), min(1.0, x.max() + 0.03), 80)
            ax.plot(xp, coef[0] * xp + coef[1], color=METRIC_COLORS.get(metric, "#222222"), lw=1.2)
        ax.set_title(METRIC_LABELS.get(metric, metric), fontsize=10)
        ax.set_xlabel("Coverage rate")
        y_min = max(0.0, float(df[metric].min()) - 0.06)
        y_max = min(1.02, float(df[metric].max()) + 0.04)
        ax.set_ylim(y_min, y_max)
        ax.grid(axis="y", color="#E6E6E6", lw=0.8)
        style_axes_as_segments(ax)

    axes[0].set_ylabel("Metric value")
    fig.suptitle("Does structural coverage explain localization performance?", fontsize=12, y=1.02)
    save_figure(fig, f"{FIG_TAG}_metric_facets")


def main() -> None:
    df = load_eval_table()
    plot_coverage_vs_mrr(df)
    plot_metric_facets(df)
    print(f"[OK] wrote figures to {OUT_DIR}")


if __name__ == "__main__":
    main()

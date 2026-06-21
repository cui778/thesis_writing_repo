from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch4_style import (
    METRIC_COLORS,
    TEXT_GREY,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
)


"""
Scientific question:
For a representative formal defect scene, how does the model move from
window-level active probabilities to a scene-level diagnosis interval and
node-level localization?

Section: 4.4.1, 4.4.2
Figure role: process-evidence figure; complements aggregate performance plots.
"""


FIG_TAG = "13_CH4_single_scenario_diagnosis_profile"
OUT_DIR = ensure_out_dir(FIG_TAG)
WINDOW_PRED_FILE = Path(
    r"E:/11.16/script2_new/chapter4_diagnosis_model/outputs/formal_window_length/"
    r"ch4_formal_window_3h_s42_window_predictions.csv"
)
EVENT_PRED_FILE = Path(
    r"E:/11.16/script2_new/chapter4_diagnosis_model/outputs/formal_window_length/"
    r"ch4_formal_window_3h_s42_event_predictions.csv"
)
PREFERRED_SCENARIO_ID = 316


def select_representative_event(events: pd.DataFrame) -> pd.Series:
    if PREFERRED_SCENARIO_ID is not None:
        preferred = events[events["scenario_id"].eq(PREFERRED_SCENARIO_ID)]
        if preferred.empty:
            raise ValueError(f"Preferred scenario {PREFERRED_SCENARIO_ID} was not found.")
        return preferred.iloc[0]
    candidates = events[
        (events["pred_true_node_rank"].eq(1))
        & (events["active_interval_iou"].ge(0.85))
        & (events["false_alarm_before_start"].eq(0))
    ].copy()
    if candidates.empty:
        candidates = events[events["pred_has_defect"].eq(1)].copy()
    candidates["score"] = (
        candidates["active_interval_iou"].fillna(0)
        - 0.08 * candidates["onset_error_hours"].fillna(24)
        - 0.02 * candidates["duration_error_hours"].abs().fillna(24)
        + 0.05 * candidates["pred_true_node_rank"].eq(1).astype(float)
    )
    return candidates.sort_values("score", ascending=False).iloc[0]


def prepare_window_profile(windows: pd.DataFrame, event: pd.Series) -> pd.DataFrame:
    scene = windows[windows["scenario_id"].eq(int(event["scenario_id"]))].copy()
    if scene.empty:
        raise ValueError(f"No window predictions found for scenario {event['scenario_id']}")
    for col in ["window_start_time", "window_end_time"]:
        scene[col] = pd.to_datetime(scene[col])
    true_start = pd.to_datetime(event["true_start"])
    scene["window_center"] = scene["window_start_time"] + (scene["window_end_time"] - scene["window_start_time"]) / 2
    scene["relative_hour"] = (scene["window_center"] - true_start).dt.total_seconds() / 3600.0
    scene["top_hit_true_node"] = scene["top_candidate_node"].astype(str).eq(str(event["true_node_id"]))
    return scene.sort_values("relative_hour").reset_index(drop=True)


def interval_to_relative(event: pd.Series, start_col: str, end_col: str) -> tuple[float, float]:
    true_start = pd.to_datetime(event["true_start"])
    start = pd.to_datetime(event[start_col])
    end = pd.to_datetime(event[end_col])
    return (
        (start - true_start).total_seconds() / 3600.0,
        (end - true_start).total_seconds() / 3600.0,
    )


def draw_profile(scene: pd.DataFrame, event: pd.Series) -> None:
    fig = plt.figure(figsize=(11.2, 8.0))
    gs = fig.add_gridspec(4, 1, height_ratios=[2.1, 1.1, 1.35, 1.2], hspace=0.38)
    ax_p = fig.add_subplot(gs[0, 0])
    ax_i = fig.add_subplot(gs[1, 0], sharex=ax_p)
    ax_n = fig.add_subplot(gs[2, 0], sharex=ax_p)
    ax_s = fig.add_subplot(gs[3, 0])

    true_start, true_end = interval_to_relative(event, "true_start", "true_end")
    pred_start, pred_end = interval_to_relative(event, "pred_start", "pred_end")
    x = scene["relative_hour"].to_numpy()

    ax_p.axvspan(true_start, true_end, color=METRIC_COLORS["event"], alpha=0.16, label="True active")
    ax_p.axvspan(pred_start, pred_end, color=METRIC_COLORS["temporal"], alpha=0.10, label="Predicted interval")
    ax_p.plot(x, scene["p_active"], color=METRIC_COLORS["mrr"], linewidth=2.0, marker="o", markersize=4)
    ax_p.axhline(0.5, color="#555555", linewidth=0.9, linestyle="--")
    ax_p.set_ylim(-0.03, 1.03)
    ax_p.set_ylabel("p_active")
    ax_p.set_title("A  Window-level active probability aligned to the true defect start", loc="left", fontweight="bold")
    ax_p.legend(frameon=False, ncol=3, loc="upper left")
    style_axes_as_segments(ax_p, grid_axis="y")

    ax_i.broken_barh([(true_start, true_end - true_start)], (0.58, 0.28), color=METRIC_COLORS["event"], alpha=0.72)
    ax_i.broken_barh([(pred_start, pred_end - pred_start)], (0.16, 0.28), color=METRIC_COLORS["temporal"], alpha=0.72)
    ax_i.set_yticks([0.72, 0.30], ["True", "Predicted"])
    ax_i.set_ylim(0, 1)
    ax_i.set_ylabel("Interval")
    ax_i.set_title("B  Scene-level active interval recovery", loc="left", fontweight="bold")
    style_axes_as_segments(ax_i, grid_axis="x")

    hit = scene["top_hit_true_node"].astype(int).to_numpy()
    active = scene["true_active"].astype(int).to_numpy()
    colors = np.where(hit == 1, METRIC_COLORS["top1"], "#B9C0C8")
    ax_n.scatter(x, hit, s=42 + 34 * active, color=colors, edgecolors="white", linewidths=0.45, zorder=3)
    ax_n.plot(x, hit, color="#888888", linewidth=0.8, alpha=0.45, zorder=2)
    ax_n.set_yticks([0, 1], ["Other", "True node"])
    ax_n.set_ylim(-0.35, 1.35)
    ax_n.set_ylabel("Top candidate")
    ax_n.set_title("C  Whether the window top candidate is the true defect node", loc="left", fontweight="bold")
    style_axes_as_segments(ax_n, grid_axis="y")

    metrics = pd.DataFrame(
        [
            ("Active IoU", float(event["active_interval_iou"])),
            ("Onset error (h)", float(event["onset_error_hours"])),
            ("True-node rank", float(event["pred_true_node_rank"])),
            ("Pred active windows", float(event["n_pred_active_windows"])),
        ],
        columns=["metric", "value"],
    )
    ax_s.axis("off")
    summary_text = (
        f"Scenario {int(event['scenario_id'])} ({event['defect_type']}) | "
        f"true node: {event['true_node_id']} | predicted top node: {event['pred_top_node_id']}"
    )
    ax_s.text(0.0, 0.92, "D  Event-level diagnosis summary", fontweight="bold", fontsize=11, transform=ax_s.transAxes)
    ax_s.text(0.0, 0.70, summary_text, color=TEXT_GREY, fontsize=9.2, transform=ax_s.transAxes)
    x0 = 0.0
    for idx, row in metrics.iterrows():
        ax_s.text(x0 + idx * 0.24, 0.38, row["metric"], color=TEXT_GREY, fontsize=8.4, transform=ax_s.transAxes)
        value = row["value"]
        if row["metric"] == "Active IoU":
            label = f"{value:.3f}"
        elif row["metric"] == "Onset error (h)":
            label = f"{value:.2f}"
        elif row["metric"] == "True-node rank":
            label = f"{value:.0f}"
        else:
            label = f"{value:.0f}"
        ax_s.text(x0 + idx * 0.24, 0.10, label, fontsize=15, fontweight="bold", transform=ax_s.transAxes)

    xmin = max(-4.0, float(x.min()) - 0.5)
    xmax = min(max(true_end + 4.0, pred_end + 2.0), float(x.max()) + 0.5)
    ax_n.set_xlabel("Hours relative to true defect start")
    for ax in [ax_p, ax_i, ax_n]:
        ax.set_xlim(xmin, xmax)
    style_axes_as_segments(ax_p, grid_axis="y")
    style_axes_as_segments(ax_i, grid_axis="x")
    style_axes_as_segments(ax_n, grid_axis="y")

    fig.suptitle(
        "13  Single-scenario diagnosis profile from window probabilities to scene diagnosis",
        x=0.01,
        y=0.99,
        ha="left",
        fontweight="bold",
        fontsize=12.5,
    )
    fig.text(
        0.01,
        0.01,
        "Source: formal_window_length 3h, seed42 window/event predictions. Representative scene is selected automatically from high-IoU, rank-1, no-early-false-alarm events.",
        color=TEXT_GREY,
        fontsize=8.2,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scene.to_csv(OUT_DIR / f"{FIG_TAG}_selected_window_profile.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([event.to_dict()]).to_csv(OUT_DIR / f"{FIG_TAG}_selected_event.csv", index=False, encoding="utf-8-sig")
    save_figure(fig, OUT_DIR, f"{FIG_TAG}_diagnosis_profile")


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    windows = pd.read_csv(WINDOW_PRED_FILE, encoding="utf-8-sig")
    events = pd.read_csv(EVENT_PRED_FILE, encoding="utf-8-sig")
    event = select_representative_event(events)
    scene = prepare_window_profile(windows, event)
    draw_profile(scene, event)
    print(OUT_DIR)


if __name__ == "__main__":
    main()

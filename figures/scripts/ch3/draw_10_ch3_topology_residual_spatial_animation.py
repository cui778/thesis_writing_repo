from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter

from _ch3_style import TEXT_GREY, apply_style, ensure_out_dir
from draw_04_ch3_topology_residual_spatial_map import (
    compute_energy,
    draw_network_base,
    load_topology,
    nearest_time_frame,
    read_scene_and_normal,
    scatter_energy,
    select_gallery_scenes,
    verify_formal_sources,
)


OUT_TAG = "10_CH3_topology_residual_spatial_animation"
BASENAME = "10_CH3_topology_residual_spatial_animation"
RESPONSE_SUMMARY = (
    Path(r"E:/11.16/thesis_writing_repo/figures/ch3/generated_results/08_CH3_strength_stratified_event_response")
    / "08_CH3_strength_stratified_event_response_all_scenario_strength_response_summary.csv"
)
PRE_ACTIVE_BUFFER_H = 2.0
POST_ACTIVE_BUFFER_H = 4.0


def animation_hours(scene: pd.DataFrame, start: float, end: float) -> np.ndarray:
    view_start = max(0.0, start - PRE_ACTIVE_BUFFER_H)
    view_end = min(47.0, end + POST_ACTIVE_BUFFER_H)
    base_hours = np.arange(view_start, view_end + 0.01, 0.5)
    special = np.array([view_start, start, start + 0.5, (start + end) / 2.0, end, view_end])
    hours = np.unique(np.round(np.concatenate([base_hours, special]), 3))
    available = scene["hour"].drop_duplicates().to_numpy()
    snapped = np.array([available[np.argmin(np.abs(available - hour))] for hour in hours])
    return np.unique(snapped)


def draw_timeline(ax: plt.Axes, scene: pd.DataFrame, start: float, end: float, current_hour: float) -> None:
    hourly = scene.groupby("hour")["residual_energy"].max().reset_index()
    ax.plot(hourly["hour"], hourly["residual_energy"], color="#4E79A7", linewidth=1.8)
    ax.axvspan(start, end, color="#E15759", alpha=0.18, linewidth=0)
    ax.axvline(current_hour, color="#222222", linewidth=1.4)
    x_min = max(0.0, start - PRE_ACTIVE_BUFFER_H)
    x_max = min(48.0, end + POST_ACTIVE_BUFFER_H)
    ax.set_xlim(x_min, x_max)
    ymax = max(float(hourly["residual_energy"].quantile(0.99)) * 1.12, 1e-6)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Max residual energy")
    ax.set_title("Network response timeline", loc="left", fontsize=9.5, fontweight="bold")
    ax.grid(axis="y", color="#E7EAF0", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_bounds(0, ymax)
    ax.spines["bottom"].set_bounds(x_min, x_max)


def select_animation_scenes() -> pd.DataFrame:
    if not RESPONSE_SUMMARY.exists():
        gallery = select_gallery_scenes().copy()
        gallery["selection_reason"] = "fallback_from_draw04_gallery"
        return gallery
    summary = pd.read_csv(RESPONSE_SUMMARY, encoding="utf-8-sig")
    summary = summary[pd.to_numeric(summary["duration_h"], errors="coerce") >= 12].copy()
    summary["active_peak_response_index"] = pd.to_numeric(summary["active_peak_response_index"], errors="coerce")
    summary["duration_h"] = pd.to_numeric(summary["duration_h"], errors="coerce")
    summary = summary.sort_values(["active_peak_response_index", "duration_h"], ascending=[False, False])

    selected = []
    used_nodes: set[str] = set()
    for defect_type in ["I", "E"]:
        pool = summary[summary["defect_type"].eq(defect_type)]
        for _, row in pool.iterrows():
            if row["true_node"] in used_nodes:
                continue
            selected.append(row)
            used_nodes.add(str(row["true_node"]))
            break
    for _, row in summary.iterrows():
        if len(selected) >= 3:
            break
        if row["true_node"] in used_nodes:
            continue
        selected.append(row)
        used_nodes.add(str(row["true_node"]))
    out = pd.DataFrame(selected).copy()
    out = out.rename(columns={"scenario_id": "defect_id", "true_node": "node_id"})
    out["case_id"] = [f"case{i + 1:02d}" for i in range(len(out))]
    out["figure_prefix"] = [f"10{chr(ord('a') + i)}" for i in range(len(out))]
    out["selection_reason"] = "duration>=12h_top_active_peak_response_unique_nodes"
    return out


def make_animation(scene_row: pd.Series, coords: pd.DataFrame, conduits: pd.DataFrame, out_dir: Path) -> dict:
    scenario_id = int(scene_row["defect_id"])
    scene = compute_energy(read_scene_and_normal(scenario_id), scenario_id)
    start = float(scene_row["start_hour"])
    end = start + float(scene_row["duration_h"])
    active = scene[(scene["hour"] >= start) & (scene["hour"] < end)]
    active_max = active.groupby("node_id")["residual_energy"].max()
    vmax = max(float(active_max.quantile(0.98)), 1e-6)
    hours = animation_hours(scene, start, end)

    fig = plt.figure(figsize=(8.6, 7.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.34], hspace=0.18)
    ax_map = fig.add_subplot(gs[0, 0])
    ax_time = fig.add_subplot(gs[1, 0])

    def update(frame_idx: int):
        hour = float(hours[frame_idx])
        frame = nearest_time_frame(scene, hour)
        ax_map.clear()
        ax_time.clear()
        draw_network_base(ax_map, coords, conduits)
        scatter_energy(ax_map, frame, coords, scene_row, vmax, size_scale=115)
        active_label = "ACTIVE" if start <= hour < end else "inactive"
        ax_map.set_title(
            f"Spatial residual response | t = {hour:.1f} h ({active_label})",
            loc="left",
            fontsize=10.5,
            fontweight="bold",
        )
        draw_timeline(ax_time, scene, start, end, hour)
        fig.suptitle(
            f"Scenario {scenario_id} ({scene_row['defect_type']}), true node {scene_row['node_id']}",
            x=0.02,
            y=0.985,
            ha="left",
            fontsize=12.5,
            fontweight="bold",
        )
        fig.text(
            0.02,
            0.02,
            f"Star marks true defect node; timeline is cropped to active window {start:.0f}-{end:.0f} h plus context. "
            "Color encodes normalized residual energy.",
            fontsize=8.0,
            color=TEXT_GREY,
        )
        return []

    ani = FuncAnimation(fig, update, frames=len(hours), interval=360, blit=False)
    prefix = str(scene_row.get("figure_prefix", "10a")).replace("04", "10")
    case_id = str(scene_row.get("case_id", f"scene_{scenario_id}"))
    out_name = f"{prefix}_CH3_topology_residual_spatial_animation_{case_id}.gif"
    ani.save(out_dir / out_name, writer=PillowWriter(fps=3))
    plt.close(fig)
    return {
        "scenario_id": scenario_id,
        "case_id": case_id,
        "figure_prefix": prefix,
        "gif_file": out_name,
        "defect_type": scene_row["defect_type"],
        "true_node": scene_row["node_id"],
        "start_hour": start,
        "duration_h": float(scene_row["duration_h"]),
        "n_frames": len(hours),
        "selection_reason": scene_row.get("selection_reason", ""),
        "active_peak_response_index": scene_row.get("active_peak_response_index", np.nan),
    }


def main() -> None:
    apply_style()
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["savefig.dpi"] = 300
    verify_formal_sources()
    out_dir = ensure_out_dir(OUT_TAG)
    coords, conduits = load_topology()
    gallery_scenes = select_animation_scenes()
    records = [make_animation(row, coords, conduits, out_dir) for _, row in gallery_scenes.iterrows()]
    pd.DataFrame(records).to_csv(out_dir / f"{BASENAME}_animation_index.csv", index=False, encoding="utf-8-sig")
    print(f"Saved {len(records)} GIF animations to {out_dir}")
    print(f"Selection source: {RESPONSE_SUMMARY}")


if __name__ == "__main__":
    main()

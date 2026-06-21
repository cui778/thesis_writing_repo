from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch3_style import (
    TEXT_GREY,
    TYPE_COLORS,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
)
from draw_07_ch3_all_scenario_event_aligned_response import (
    CASES_PER_TYPE_DURATION,
    HOP_BANDS,
    BASENAME as DRAW07_BASENAME,
    build_event_aligned_raster,
    build_scenario_node_hops,
    draw_raster_panels,
    load_defects,
    load_graph,
    normal_energy_thresholds,
    order_scenarios,
    read_normal_timeseries,
    verify_formal_sources,
)


OUT_TAG = "08_CH3_strength_stratified_event_response"
BASENAME = "08_CH3_strength_stratified_event_response"

STRATA = [
    ("low", "08a_CH3_low_strength_balanced_response_raster", "low-strength"),
    ("mid", "08b_CH3_mid_strength_balanced_response_raster", "mid-strength"),
    ("high", "08c_CH3_high_strength_balanced_response_raster", "high-strength"),
]
DURATION_MARKERS = {
    6: "o",
    12: "s",
    18: "^",
    24: "D",
}


def select_strength_stratum(defects: pd.DataFrame, stratum: str) -> pd.DataFrame:
    parts = []
    for _, group in defects.groupby(["defect_type", "duration_h"], sort=True):
        group = group.sort_values("abs_flow", ascending=True).reset_index(drop=True)
        n = len(group)
        if stratum == "low":
            selected = group.head(CASES_PER_TYPE_DURATION)
        elif stratum == "high":
            selected = group.tail(CASES_PER_TYPE_DURATION)
        elif stratum == "mid":
            start = max(0, (n - CASES_PER_TYPE_DURATION) // 2)
            selected = group.iloc[start : start + CASES_PER_TYPE_DURATION]
        else:
            raise ValueError(f"Unknown strength stratum: {stratum}")
        parts.append(selected.copy())
    out = pd.concat(parts, ignore_index=True)
    expected = 2 * len(sorted(defects["duration_h"].unique())) * CASES_PER_TYPE_DURATION
    if len(out) != expected:
        counts = out.groupby(["defect_type", "duration_h"]).size().to_dict()
        raise ValueError(f"{stratum} selection failed: rows={len(out)}, counts={counts}")
    return out.sort_values(["defect_type", "duration_h", "abs_flow", "scenario_id"]).reset_index(drop=True)


def subset_raster(full_raster: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    keep = set(selected["scenario_id"].astype(int))
    raster = full_raster[full_raster["scenario_id"].isin(keep)].copy()
    drop_cols = [col for col in selected.columns if col in raster.columns and col != "scenario_id"]
    raster = raster.drop(columns=drop_cols).merge(selected, on="scenario_id", how="left")
    return raster


def active_peak_summary(full_raster: pd.DataFrame, defects: pd.DataFrame) -> pd.DataFrame:
    active = full_raster[full_raster["is_active"]].copy()
    by_hop = (
        active.groupby(["scenario_id", "hop_band"])["hydraulic_response_index_q90"]
        .max()
        .reset_index()
    )
    peak = (
        by_hop.sort_values("hydraulic_response_index_q90", ascending=False)
        .groupby("scenario_id", as_index=False)
        .first()
        .rename(
            columns={
                "hop_band": "dominant_hop_band",
                "hydraulic_response_index_q90": "active_peak_response_index",
            }
        )
    )
    wide = (
        by_hop.pivot(index="scenario_id", columns="hop_band", values="hydraulic_response_index_q90")
        .add_prefix("peak_")
        .reset_index()
    )
    out = defects.merge(peak, on="scenario_id", how="left").merge(wide, on="scenario_id", how="left")
    out["flow_rank_pct"] = out.groupby("defect_type")["abs_flow"].rank(pct=True)
    return out


def draw_strength_response_summary(summary: pd.DataFrame, out_dir: Path) -> None:
    durations = sorted(summary["duration_h"].unique())
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.4), sharex=True, sharey=True)
    axes = axes.ravel()
    marker_handles = []
    for ax, duration in zip(axes, durations):
        subset = summary[summary["duration_h"].eq(duration)]
        for defect_type, color in [("I", TYPE_COLORS["I"]), ("E", TYPE_COLORS["E"])]:
            cur = subset[subset["defect_type"].eq(defect_type)]
            ax.scatter(
                cur["abs_flow"],
                cur["active_peak_response_index"],
                s=26,
                marker=DURATION_MARKERS[int(duration)],
                color=color,
                alpha=0.58,
                linewidths=0,
                label=defect_type,
            )
        ax.set_title(f"{int(duration)} h duration", loc="left", fontweight="bold")
        ax.set_xscale("log")
        ax.set_ylim(-0.2, min(12.0, max(4.5, summary["active_peak_response_index"].quantile(0.98) * 1.08)))
        style_axes_as_segments(ax, grid_axis="y")
    for ax in axes[2:]:
        ax.set_xlabel("|flow| strength")
    axes[0].set_ylabel("Active-window peak hydraulic response index")
    axes[2].set_ylabel("Active-window peak hydraulic response index")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="upper right", bbox_to_anchor=(0.98, 0.96))
    fig.suptitle(
        "08d  Strength-response relationship across all formal defect scenarios",
        x=0.01,
        y=0.985,
        ha="left",
        fontweight="bold",
        fontsize=12.5,
    )
    fig.text(
        0.01,
        0.02,
        "Each point is one formal I/E scenario. Response uses hydraulic residuals only and is measured as the active-window peak over topology-distance bands.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.09, right=0.9, top=0.88, bottom=0.12, wspace=0.16, hspace=0.24)
    save_figure(fig, out_dir, "08d_CH3_all_scenario_strength_response_summary")


def write_audit(manifest: dict, summary: pd.DataFrame, out_dir: Path) -> None:
    summary.to_csv(out_dir / f"{BASENAME}_all_scenario_strength_response_summary.csv", index=False, encoding="utf-8-sig")
    audit = pd.DataFrame(
        [
            {
                "dataset_type": manifest["dataset_type"],
                "formal_defect_scenario_count": len(summary),
                "cases_per_type_duration_per_stratum": CASES_PER_TYPE_DURATION,
                "strata": "low;mid;high",
                "value_definition": "hydraulic_response_index_q90 = q90 hydraulic residual energy / node-wise normal20 q95",
                "residual_columns": "depth_residual;total_outflow_residual",
                "scenario_averaging": "none; each raster row is one selected scenario",
                "draw07_reference": DRAW07_BASENAME,
            }
        ]
    )
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    out_dir = ensure_out_dir(OUT_TAG)

    defects = load_defects()
    graph = load_graph()
    scenario_node_hops = build_scenario_node_hops(defects, graph)
    normal = read_normal_timeseries()
    scales, thresholds = normal_energy_thresholds(normal)
    full_raster = build_event_aligned_raster(defects, scenario_node_hops, scales, thresholds)
    summary = active_peak_summary(full_raster, defects)

    for stratum, basename, label in STRATA:
        selected = select_strength_stratum(defects, stratum)
        raster = subset_raster(full_raster, selected)
        row_order = order_scenarios(raster, selected)
        raster.to_csv(out_dir / f"{basename}_raster_long.csv", index=False, encoding="utf-8-sig")
        row_order.to_csv(out_dir / f"{basename}_scenario_row_order.csv", index=False, encoding="utf-8-sig")
        draw_raster_panels(
            raster,
            row_order,
            out_dir,
            value_col="hydraulic_response_index_q90",
            vmax=4.0,
            colorbar_label="Hydraulic response index q90 / normal q95",
            title=f"08 {label.capitalize()} balanced hydraulic response after defect onset",
            ylabel=f"{label.capitalize()} balanced scenarios",
            footer=(
                f"Rows are {label} I/E scenarios, uniformly sampled by duration "
                "with 8 cases per type-duration group. Values use hydraulic residuals only."
            ),
            basename=basename,
        )

    draw_strength_response_summary(summary, out_dir)
    write_audit(manifest, summary, out_dir)
    print(f"Saved {BASENAME} figures to {out_dir}")


if __name__ == "__main__":
    main()

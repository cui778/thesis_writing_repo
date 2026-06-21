from __future__ import annotations

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
    HOP_BANDS,
    build_event_aligned_raster,
    build_scenario_node_hops,
    load_defects,
    load_graph,
    normal_energy_thresholds,
    read_normal_timeseries,
    verify_formal_sources,
)


OUT_TAG = "09_CH3_response_peak_timing"
BASENAME = "09_CH3_response_peak_timing"

DURATION_MARKERS = {
    6: "o",
    12: "s",
    18: "^",
    24: "D",
}
HOP_COLORS = {
    "0-hop": "#4E79A7",
    "1-hop": "#76B7B2",
    "2-hop": "#F28E2B",
    "3+-hop": "#B07AA1",
}


def peak_timing_summary(full_raster: pd.DataFrame, defects: pd.DataFrame) -> pd.DataFrame:
    active = full_raster[full_raster["is_active"]].copy()
    active = active.sort_values(
        ["scenario_id", "hydraulic_response_index_q90", "relative_hour"],
        ascending=[True, False, True],
    )
    peak = (
        active.groupby("scenario_id", as_index=False)
        .first()[
            [
                "scenario_id",
                "relative_hour",
                "hop_band",
                "hydraulic_response_index_q90",
                "exceedance_rate",
            ]
        ]
        .rename(
            columns={
                "relative_hour": "time_to_peak_hours",
                "hop_band": "dominant_hop_band",
                "hydraulic_response_index_q90": "peak_response_index",
                "exceedance_rate": "peak_exceedance_rate",
            }
        )
    )
    out = defects.merge(peak, on="scenario_id", how="left")
    out["flow_rank_pct"] = out.groupby("defect_type")["abs_flow"].rank(pct=True)
    out["peak_phase"] = pd.cut(
        out["time_to_peak_hours"],
        bins=[-0.001, 2, 6, 12, np.inf],
        labels=["0-2 h", "2-6 h", "6-12 h", "12+ h"],
    )
    return out


def draw_timing_scatter(ax: plt.Axes, summary: pd.DataFrame) -> None:
    for duration, marker in DURATION_MARKERS.items():
        for defect_type, color in [("I", TYPE_COLORS["I"]), ("E", TYPE_COLORS["E"])]:
            cur = summary[summary["duration_h"].eq(duration) & summary["defect_type"].eq(defect_type)]
            sizes = 16 + 22 * np.sqrt(np.clip(cur["peak_response_index"], 0, 8) / 8)
            ax.scatter(
                cur["abs_flow"],
                cur["time_to_peak_hours"],
                s=sizes,
                marker=marker,
                color=color,
                alpha=0.58,
                linewidths=0,
                label=defect_type if duration == 6 else None,
            )
    ax.set_xscale("log")
    ax.set_ylim(-0.5, 14.5)
    ax.set_xlabel("|flow| strength")
    ax.set_ylabel("Time to peak response (h)")
    ax.set_title("A  Peak timing versus defect strength", loc="left", fontweight="bold")
    style_axes_as_segments(ax, grid_axis="y")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, frameon=False, loc="upper right", title="Type")


def draw_duration_distribution(ax: plt.Axes, summary: pd.DataFrame) -> None:
    durations = sorted(summary["duration_h"].unique())
    positions = np.arange(len(durations))
    width = 0.26
    rng = np.random.default_rng(42)
    for offset, defect_type, color in [(-width, "I", TYPE_COLORS["I"]), (width, "E", TYPE_COLORS["E"])]:
        data = [
            summary[summary["duration_h"].eq(duration) & summary["defect_type"].eq(defect_type)][
                "time_to_peak_hours"
            ].dropna()
            for duration in durations
        ]
        box = ax.boxplot(
            data,
            positions=positions + offset,
            widths=0.22,
            patch_artist=True,
            showfliers=False,
            manage_ticks=False,
        )
        for patch in box["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.22)
            patch.set_edgecolor(color)
        for median in box["medians"]:
            median.set_color("#222222")
            median.set_linewidth(1.1)
        for pos, values in zip(positions + offset, data):
            jitter = rng.normal(0, 0.028, size=len(values))
            ax.scatter(
                np.full(len(values), pos) + jitter,
                values,
                s=9,
                color=color,
                alpha=0.28,
                linewidths=0,
            )
    ax.set_xticks(positions, [f"{int(duration)} h" for duration in durations])
    ax.set_ylim(-0.5, 14.5)
    ax.set_xlabel("Defect duration")
    ax.set_ylabel("Time to peak response (h)")
    ax.set_title("B  Peak timing distribution by duration", loc="left", fontweight="bold")
    style_axes_as_segments(ax, grid_axis="y")


def draw_dominant_hop_stack(ax: plt.Axes, summary: pd.DataFrame) -> None:
    durations = sorted(summary["duration_h"].unique())
    hop_order = [name for name, _ in HOP_BANDS]
    counts = (
        summary.groupby(["duration_h", "dominant_hop_band"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=durations, columns=hop_order, fill_value=0)
    )
    proportions = counts.divide(counts.sum(axis=1), axis=0).fillna(0)
    bottom = np.zeros(len(durations))
    x = np.arange(len(durations))
    for hop in hop_order:
        vals = proportions[hop].to_numpy()
        ax.bar(x, vals, bottom=bottom, color=HOP_COLORS[hop], width=0.58, label=hop)
        bottom += vals
    ax.set_xticks(x, [f"{int(duration)} h" for duration in durations])
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Defect duration")
    ax.set_ylabel("Share of scenarios")
    ax.set_title("C  Topology band where peak response appears", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    style_axes_as_segments(ax, grid_axis="y")


def draw_phase_hop_matrix(ax: plt.Axes, summary: pd.DataFrame) -> None:
    hop_order = [name for name, _ in HOP_BANDS]
    phase_order = ["0-2 h", "2-6 h", "6-12 h", "12+ h"]
    matrix = (
        summary.groupby(["dominant_hop_band", "peak_phase"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(index=hop_order, columns=phase_order, fill_value=0)
    )
    matrix = matrix.divide(matrix.sum(axis=1), axis=0).fillna(0)
    image = ax.imshow(matrix.to_numpy(), cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(phase_order)), phase_order)
    ax.set_yticks(range(len(hop_order)), hop_order)
    ax.set_xlabel("Peak timing phase")
    ax.set_ylabel("Dominant topology band")
    ax.set_title("D  Timing phase within each peak-location band", loc="left", fontweight="bold")
    ax.tick_params(axis="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = plt.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("Share within hop band")
    cbar.ax.tick_params(length=0)


def draw_main_figure(summary: pd.DataFrame, out_dir) -> None:
    fig = plt.figure(figsize=(11.4, 8.4))
    gs = fig.add_gridspec(2, 2, left=0.08, right=0.96, top=0.88, bottom=0.11, hspace=0.32, wspace=0.26)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    draw_timing_scatter(ax_a, summary)
    draw_duration_distribution(ax_b, summary)
    draw_dominant_hop_stack(ax_c, summary)
    draw_phase_hop_matrix(ax_d, summary)
    fig.suptitle(
        "09  Response peak timing and topology location across formal defect scenarios",
        x=0.01,
        y=0.985,
        ha="left",
        fontweight="bold",
        fontsize=12.5,
    )
    fig.text(
        0.01,
        0.02,
        "Each formal defect scenario contributes one active-window peak, selected across 0-hop, 1-hop, 2-hop and 3+-hop bands using hydraulic residual response index.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    save_figure(fig, out_dir, BASENAME)


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
    summary = peak_timing_summary(full_raster, defects)
    summary.to_csv(out_dir / f"{BASENAME}_peak_timing_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {
                "dataset_type": manifest["dataset_type"],
                "formal_defect_scenario_count": len(summary),
                "residual_columns": "depth_residual;total_outflow_residual",
                "peak_definition": "max active-window hydraulic_response_index_q90 across topology bands and relative time",
                "time_window": "0-14 h after defect onset",
                "scenario_averaging": "none; one peak record per formal defect scenario",
            }
        ]
    ).to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")
    draw_main_figure(summary, out_dir)
    print(f"Saved {BASENAME} figure to {out_dir}")


if __name__ == "__main__":
    main()

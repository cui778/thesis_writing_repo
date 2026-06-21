from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch3_style import (
    FORMAL_DEFECT_MATRIX,
    FORMAL_MANIFEST,
    FORMAL_RESIDUAL_PARQUET,
    TEXT_GREY,
    TYPE_COLORS,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_heatmap_axes_plain,
)


OUT_TAG = "07_CH3_all_scenario_event_aligned_response"
BASENAME = "07_CH3_all_scenario_event_aligned_response"
TOPOLOGY_JSON = Path(r"E:/11.16/script2_new/input_1/parsed_inp_data.json")

NORMAL_SCENARIOS = list(range(800001, 800021))
BANNED_TOKENS = ("persistent", "fulltime", "legacy", "seedset10")
RESIDUAL_COLUMNS = [
    "depth_residual",
    "total_outflow_residual",
]
RELATIVE_HOURS = (0.0, 14.0)
CASES_PER_TYPE_DURATION = 8
RANDOM_SELECTION_SEED = 42
HOP_BANDS = [
    ("0-hop", "0-hop defect node"),
    ("1-hop", "1-hop neighborhood"),
    ("2-hop", "2-hop neighborhood"),
    ("3+-hop", "3+-hop distal nodes"),
]


def verify_formal_sources() -> dict:
    manifest = json.loads(FORMAL_MANIFEST.read_text(encoding="utf-8"))
    expected = {
        "dataset_type": "ie420_plus_normal20",
        "scenario_count": 441,
        "time_gated_count": 421,
        "persistent_count": 0,
        "normal_count": 20,
        "i_count_total": 250,
        "e_count_total": 170,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"Unexpected manifest {key}: {manifest.get(key)!r}, expected {value!r}")
    if Path(manifest["defect_csv_path"]).name != FORMAL_DEFECT_MATRIX.name:
        raise ValueError(f"Manifest does not point to formal defect matrix: {manifest['defect_csv_path']}")
    for path in [FORMAL_RESIDUAL_PARQUET, FORMAL_DEFECT_MATRIX, TOPOLOGY_JSON]:
        lowered = str(path).lower()
        if any(token in lowered for token in BANNED_TOKENS):
            raise ValueError(f"Forbidden protocol token detected in path: {path}")
    return manifest


def load_defects() -> pd.DataFrame:
    defects = pd.read_csv(FORMAL_DEFECT_MATRIX)
    counts = defects["defect_type"].value_counts().to_dict()
    if len(defects) != 420 or counts.get("I") != 250 or counts.get("E") != 170:
        raise ValueError(f"Unexpected formal defect matrix: rows={len(defects)}, counts={counts}")
    return defects[
        ["defect_id", "defect_type", "node_id", "start_hour", "duration_h", "flow"]
    ].rename(columns={"defect_id": "scenario_id", "node_id": "true_node"}).assign(
        abs_flow=lambda x: x["flow"].abs()
    )


def select_balanced_high_strength_defects(defects: pd.DataFrame) -> pd.DataFrame:
    selected = (
        defects.sort_values(["defect_type", "duration_h", "abs_flow"], ascending=[True, True, False])
        .groupby(["defect_type", "duration_h"], group_keys=False)
        .head(CASES_PER_TYPE_DURATION)
        .copy()
    )
    expected = 2 * len(sorted(defects["duration_h"].unique())) * CASES_PER_TYPE_DURATION
    if len(selected) != expected:
        counts = selected.groupby(["defect_type", "duration_h"]).size().to_dict()
        raise ValueError(f"Balanced high-strength selection failed: rows={len(selected)}, counts={counts}")
    return selected.reset_index(drop=True)


def select_balanced_random_defects(defects: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for (defect_type, duration_h), group in defects.groupby(["defect_type", "duration_h"], sort=True):
        parts.append(group.sample(n=CASES_PER_TYPE_DURATION, random_state=RANDOM_SELECTION_SEED).copy())
    selected = pd.concat(parts, ignore_index=True)
    expected = 2 * len(sorted(defects["duration_h"].unique())) * CASES_PER_TYPE_DURATION
    if len(selected) != expected:
        counts = selected.groupby(["defect_type", "duration_h"]).size().to_dict()
        raise ValueError(f"Balanced random selection failed: rows={len(selected)}, counts={counts}")
    return selected.sort_values(["defect_type", "duration_h", "start_hour", "scenario_id"]).reset_index(drop=True)


def load_graph() -> dict[str, set[str]]:
    data = json.loads(TOPOLOGY_JSON.read_text(encoding="utf-8"))
    nodes = set(data["coordinates"].keys())
    graph = {node: set() for node in nodes}
    for conduit in data["conduits"].values():
        a = conduit["from_node"]
        b = conduit["to_node"]
        if a in graph and b in graph:
            graph[a].add(b)
            graph[b].add(a)
    return graph


def shortest_hops(graph: dict[str, set[str]], source: str) -> dict[str, float]:
    dist = {source: 0.0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt in dist:
                continue
            dist[nxt] = dist[node] + 1.0
            queue.append(nxt)
    return {node: dist.get(node, np.inf) for node in graph}


def hop_band(hop: float) -> str:
    if not np.isfinite(hop):
        return "3+-hop"
    if hop <= 0:
        return "0-hop"
    if hop == 1:
        return "1-hop"
    if hop == 2:
        return "2-hop"
    return "3+-hop"


def build_scenario_node_hops(defects: pd.DataFrame, graph: dict[str, set[str]]) -> pd.DataFrame:
    rows = []
    hop_cache: dict[str, dict[str, float]] = {}
    for _, scene in defects.iterrows():
        true_node = str(scene["true_node"])
        if true_node not in hop_cache:
            hop_cache[true_node] = shortest_hops(graph, true_node)
        for node_id, hop in hop_cache[true_node].items():
            rows.append(
                {
                    "scenario_id": int(scene["scenario_id"]),
                    "node_id": node_id,
                    "hop": hop,
                    "hop_band": hop_band(hop),
                }
            )
    return pd.DataFrame(rows)


def read_normal_timeseries() -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyarrow is required for draw_07. Run with: "
            "conda run -n swmm_gpu python draw_07_ch3_all_scenario_event_aligned_response.py"
        ) from exc

    columns = ["scenario_id", "node_id", "time_step", *RESIDUAL_COLUMNS]
    parts: list[pd.DataFrame] = []
    parquet_file = pq.ParquetFile(FORMAL_RESIDUAL_PARQUET)
    for batch in parquet_file.iter_batches(batch_size=262_144, columns=columns):
        chunk = batch.to_pandas()
        keep = chunk["scenario_id"].isin(NORMAL_SCENARIOS)
        if keep.any():
            parts.append(chunk.loc[keep].copy())
    if not parts:
        raise ValueError("No normal20 residual rows found.")
    return pd.concat(parts, ignore_index=True)


def normal_energy_thresholds(normal: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    scales = normal[RESIDUAL_COLUMNS].abs().quantile(0.95).replace(0, np.nan).fillna(1.0)
    normalized = normal[RESIDUAL_COLUMNS].divide(scales, axis=1)
    normal = normal[["scenario_id", "node_id", "time_step"]].copy()
    normal["residual_energy"] = np.sqrt((normalized**2).mean(axis=1))
    thresholds = (
        normal.groupby("node_id")["residual_energy"]
        .quantile(0.95)
        .rename("node_hydraulic_normal_q95")
        .reset_index()
    )
    return scales, thresholds


def build_event_aligned_raster(
    defects: pd.DataFrame,
    scenario_node_hops: pd.DataFrame,
    scales: pd.Series,
    thresholds: pd.DataFrame,
) -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyarrow is required for draw_07. Run with: "
            "conda run -n swmm_gpu python draw_07_ch3_all_scenario_event_aligned_response.py"
        ) from exc

    defect_ids = set(defects["scenario_id"].astype(int))
    defect_meta = defects.set_index("scenario_id")[["defect_type", "true_node", "start_hour", "duration_h"]]
    columns = ["scenario_id", "node_id", "time_step", *RESIDUAL_COLUMNS]
    parts: list[pd.DataFrame] = []
    parquet_file = pq.ParquetFile(FORMAL_RESIDUAL_PARQUET)

    for batch in parquet_file.iter_batches(batch_size=262_144, columns=columns):
        chunk = batch.to_pandas()
        keep = chunk["scenario_id"].isin(defect_ids)
        if not keep.any():
            continue
        chunk = chunk.loc[keep].copy()
        meta = chunk["scenario_id"].map(defect_meta["start_hour"])
        chunk["hour"] = chunk["time_step"] * (10.0 / 60.0)
        chunk["relative_hour"] = chunk["hour"] - meta.astype(float)
        chunk = chunk[
            (chunk["relative_hour"] >= RELATIVE_HOURS[0])
            & (chunk["relative_hour"] <= RELATIVE_HOURS[1])
        ]
        if chunk.empty:
            continue

        normalized = chunk[RESIDUAL_COLUMNS].divide(scales, axis=1)
        chunk["residual_energy"] = np.sqrt((normalized**2).mean(axis=1))
        chunk = chunk.merge(thresholds, on="node_id", how="left")
        reference = chunk["node_hydraulic_normal_q95"].replace(0, np.nan)
        chunk["hydraulic_response_index"] = chunk["residual_energy"] / reference
        chunk["is_exceed"] = chunk["hydraulic_response_index"] > 1.0
        chunk = chunk.merge(scenario_node_hops, on=["scenario_id", "node_id"], how="left")

        grouped = (
            chunk.groupby(["scenario_id", "relative_hour", "hop_band"], observed=True)
            .agg(
                exceedance_rate=("is_exceed", "mean"),
                node_count=("node_id", "nunique"),
                residual_energy_q90=("residual_energy", lambda x: x.quantile(0.90)),
                hydraulic_response_index_q90=("hydraulic_response_index", lambda x: x.quantile(0.90)),
            )
            .reset_index()
        )
        parts.append(grouped)

    if not parts:
        raise ValueError("No defect event-aligned raster rows were created.")

    raster = pd.concat(parts, ignore_index=True)
    raster = raster.merge(defects, on="scenario_id", how="left")
    raster["is_active"] = (raster["relative_hour"] >= 0) & (
        raster["relative_hour"] < raster["duration_h"].astype(float)
    )
    raster["relative_hour"] = raster["relative_hour"].round(6)
    return raster


def order_scenarios(raster: pd.DataFrame, defects: pd.DataFrame) -> pd.DataFrame:
    active = raster[raster["is_active"]]
    active_score = (
        active.groupby("scenario_id")["hydraulic_response_index_q90"]
        .max()
        .rename("active_peak_response_index")
        .reset_index()
    )
    order = defects.merge(active_score, on="scenario_id", how="left").fillna({"active_peak_response_index": 0.0})
    order["type_rank"] = order["defect_type"].map({"I": 0, "E": 1}).fillna(2)
    order = order.sort_values(
        ["type_rank", "duration_h", "start_hour", "abs_flow"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)
    order["row_index"] = np.arange(len(order))
    return order[
        [
            "row_index",
            "scenario_id",
            "defect_type",
            "true_node",
            "start_hour",
            "duration_h",
            "flow",
            "abs_flow",
            "active_peak_response_index",
        ]
    ]


def matrix_for_band(
    raster: pd.DataFrame,
    row_order: pd.DataFrame,
    hop_band_name: str,
    value_col: str,
) -> tuple[np.ndarray, list[float]]:
    time_values = sorted(raster["relative_hour"].unique())
    row_map = row_order.set_index("scenario_id")["row_index"].to_dict()
    mat = np.full((len(row_order), len(time_values)), np.nan, dtype=float)
    time_map = {value: idx for idx, value in enumerate(time_values)}
    band = raster[raster["hop_band"].eq(hop_band_name)]
    for row in band.itertuples(index=False):
        ridx = row_map.get(int(row.scenario_id))
        cidx = time_map.get(float(row.relative_hour))
        if ridx is None or cidx is None:
            continue
        mat[ridx, cidx] = float(getattr(row, value_col))
    return mat, time_values


def draw_raster_panels(
    raster: pd.DataFrame,
    row_order: pd.DataFrame,
    out_dir: Path,
    *,
    value_col: str = "hydraulic_response_index_q90",
    vmax: float = 4.0,
    colorbar_label: str = "Hydraulic response index q90 / normal q95",
    title: str = "07  Event-aligned hydraulic response in balanced high-intensity defect scenarios",
    ylabel: str = "Balanced high-|flow| scenarios",
    footer: str = "Rows are balanced high-|flow| I/E scenarios, uniformly sampled by duration. Values use hydraulic residuals only; no averaging across scenarios.",
    basename: str = BASENAME,
) -> None:
    fig, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(11.2, 8.2),
        sharex=True,
        sharey=True,
    )
    fig.subplots_adjust(left=0.07, right=0.88, top=0.88, bottom=0.11, wspace=0.08, hspace=0.18)
    axes = axes.ravel()
    image = None
    time_values: list[float] = []
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("#EFEFEF")
    for ax, (band_name, band_label) in zip(axes, HOP_BANDS):
        matrix, time_values = matrix_for_band(raster, row_order, band_name, value_col)
        image = ax.imshow(
            matrix,
            cmap=cmap,
            vmin=0,
            vmax=vmax,
            interpolation="nearest",
            aspect="auto",
        )
        ax.set_title(band_label, loc="left", fontweight="bold")
        style_heatmap_axes_plain(ax)
        duration_boundaries = row_order.index[
            row_order[["defect_type", "duration_h"]]
            .ne(row_order[["defect_type", "duration_h"]].shift())
            .any(axis=1)
        ][1:]
        for boundary in duration_boundaries:
            ax.axhline(boundary - 0.5, color="#FFFFFF", linewidth=0.55, alpha=0.75)
        ax.axhline((row_order["defect_type"].eq("I")).sum() - 0.5, color="#222222", linewidth=0.9)

    xtick_hours = [0, 2, 4, 6, 8, 10, 12, 14]
    xtick_pos = [int(np.argmin(np.abs(np.asarray(time_values) - hour))) for hour in xtick_hours]
    for ax in axes:
        ax.set_xticks(xtick_pos, [str(hour) for hour in xtick_hours])
        ax.set_yticks([])
    axes[0].set_ylabel(ylabel)
    axes[2].set_ylabel(ylabel)
    axes[2].set_xlabel("Hours relative to defect start")
    axes[3].set_xlabel("Hours relative to defect start")
    axes[0].text(
        0.01,
        0.98,
        "I scenes",
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        color=TYPE_COLORS["I"],
        fontsize=8.5,
        fontweight="bold",
    )
    axes[2].text(
        0.01,
        0.05,
        "E scenes",
        transform=axes[2].transAxes,
        ha="left",
        va="bottom",
        color=TYPE_COLORS["E"],
        fontsize=8.5,
        fontweight="bold",
    )
    if image is not None:
        cbar = fig.colorbar(image, ax=axes.tolist(), fraction=0.025, pad=0.02)
        cbar.set_label(colorbar_label)
        cbar.ax.tick_params(length=0)
    fig.suptitle(title, x=0.01, y=0.985, ha="left", fontweight="bold", fontsize=12.5)
    fig.text(
        0.01,
        0.025,
        footer,
        color=TEXT_GREY,
        fontsize=8.5,
    )
    save_figure(fig, out_dir, basename)


def draw_peak_distribution(raster: pd.DataFrame, row_order: pd.DataFrame, out_dir: Path) -> None:
    active = raster[raster["is_active"]].copy()
    peaks = (
        active.groupby(["scenario_id", "hop_band"])["hydraulic_response_index_q90"]
        .max()
        .reset_index()
        .pivot(index="scenario_id", columns="hop_band", values="hydraulic_response_index_q90")
        .reset_index()
    )
    peaks = row_order.merge(peaks, on="scenario_id", how="left")
    x_positions = np.arange(len(HOP_BANDS))
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    rng = np.random.default_rng(42)
    for defect_type, color in [("I", TYPE_COLORS["I"]), ("E", TYPE_COLORS["E"])]:
        subset = peaks[peaks["defect_type"].eq(defect_type)]
        for xpos, (band_name, _) in zip(x_positions, HOP_BANDS):
            jitter = rng.normal(0, 0.055, size=len(subset))
            ax.scatter(
                np.full(len(subset), xpos) + jitter,
                subset[band_name],
                s=12,
                color=color,
                alpha=0.28,
                linewidths=0,
                label=defect_type if xpos == 0 else None,
            )
    medians = [peaks[band_name].median() for band_name, _ in HOP_BANDS]
    ax.plot(x_positions, medians, color="#222222", linewidth=1.4, marker="o", markersize=4, label="median")
    ax.set_xticks(x_positions, [band_name for band_name, _ in HOP_BANDS])
    ax.set_ylim(-0.1, 4.1)
    ax.set_ylabel("Active-window peak hydraulic response index")
    ax.set_xlabel("Topology distance band")
    ax.set_title("07b  Scenario-level peak response distribution", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    from _ch3_style import style_axes_as_segments

    style_axes_as_segments(ax, grid_axis="y")
    save_figure(fig, out_dir, "07b_CH3_all_scenario_peak_exceedance_distribution")
    peaks.to_csv(out_dir / f"{BASENAME}_active_peak_by_scenario.csv", index=False, encoding="utf-8-sig")


def write_outputs(
    manifest: dict,
    raster: pd.DataFrame,
    row_order: pd.DataFrame,
    out_dir: Path,
) -> None:
    raster.to_csv(out_dir / f"{BASENAME}_raster_long.csv", index=False, encoding="utf-8-sig")
    row_order.to_csv(out_dir / f"{BASENAME}_scenario_row_order.csv", index=False, encoding="utf-8-sig")
    audit = pd.DataFrame(
        [
            {
                "dataset_type": manifest["dataset_type"],
                "scenario_count": manifest["scenario_count"],
                "selected_defect_scenario_count": len(row_order),
                "cases_per_type_duration": CASES_PER_TYPE_DURATION,
                "normal_count": manifest["normal_count"],
                "defect_matrix": str(FORMAL_DEFECT_MATRIX),
                "residual_parquet": str(FORMAL_RESIDUAL_PARQUET),
                "topology_json": str(TOPOLOGY_JSON),
                "relative_hour_start": RELATIVE_HOURS[0],
                "relative_hour_end": RELATIVE_HOURS[1],
                "residual_columns": ";".join(RESIDUAL_COLUMNS),
                "normal_reference": "node-wise hydraulic residual energy q95 from normal20",
                "scenario_averaging": "none; each raster row is one formal defect scenario",
            }
        ]
    )
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def write_variant_outputs(
    raster: pd.DataFrame,
    row_order: pd.DataFrame,
    out_dir: Path,
    tag: str,
    selection_note: str,
) -> None:
    raster.to_csv(out_dir / f"{tag}_raster_long.csv", index=False, encoding="utf-8-sig")
    row_order.to_csv(out_dir / f"{tag}_scenario_row_order.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {
                "selection_note": selection_note,
                "selected_defect_scenario_count": len(row_order),
                "cases_per_type_duration": CASES_PER_TYPE_DURATION,
                "random_selection_seed": RANDOM_SELECTION_SEED,
                "residual_columns": ";".join(RESIDUAL_COLUMNS),
                "value_col": "exceedance_rate",
                "value_definition": "fraction of nodes with hydraulic residual energy above node-wise normal20 q95",
            }
        ]
    ).to_csv(out_dir / f"{tag}_source_audit.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    out_dir = ensure_out_dir(OUT_TAG)
    defects_all = load_defects()
    defects = select_balanced_high_strength_defects(defects_all)
    graph = load_graph()
    scenario_node_hops = build_scenario_node_hops(defects, graph)
    normal = read_normal_timeseries()
    scales, thresholds = normal_energy_thresholds(normal)
    raster = build_event_aligned_raster(defects, scenario_node_hops, scales, thresholds)
    row_order = order_scenarios(raster, defects)
    write_outputs(manifest, raster, row_order, out_dir)
    draw_raster_panels(raster, row_order, out_dir)
    draw_peak_distribution(raster, row_order, out_dir)

    random_defects = select_balanced_random_defects(defects_all)
    random_hops = build_scenario_node_hops(random_defects, graph)
    random_raster = build_event_aligned_raster(random_defects, random_hops, scales, thresholds)
    random_row_order = order_scenarios(random_raster, random_defects)
    random_tag = "07c_CH3_random_balanced_hydraulic_exceedance_raster"
    write_variant_outputs(
        random_raster,
        random_row_order,
        out_dir,
        random_tag,
        "Random balanced formal scenarios: 8 cases per defect type x duration group.",
    )
    draw_raster_panels(
        random_raster,
        random_row_order,
        out_dir,
        value_col="exceedance_rate",
        vmax=1.0,
        colorbar_label="Fraction of nodes above hydraulic normal q95",
        title="07c  Event-aligned hydraulic exceedance in random balanced defect scenarios",
        ylabel="Random balanced scenarios",
        footer="Rows are random I/E scenarios, uniformly sampled by duration. Values are original exceedance rates using hydraulic residuals only.",
        basename=random_tag,
    )
    print(f"Saved {BASENAME} figures to {out_dir}")


if __name__ == "__main__":
    main()

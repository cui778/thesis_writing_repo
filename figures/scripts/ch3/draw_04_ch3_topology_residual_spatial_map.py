from __future__ import annotations

import json
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
)


OUT_TAG = "04_CH3_topology_residual_spatial_map"
BASENAME = "04_CH3_topology_residual_spatial_map"

TOPOLOGY_JSON = Path(r"E:/11.16/script2_new/input_1/parsed_inp_data.json")
DRAW02_SELECTED = (
    Path(r"E:/11.16/thesis_writing_repo/figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual")
    / "02_CH3_normal_envelope_defect_residual_selected_pair.csv"
)
DRAW02_GALLERY_CASES = (
    Path(r"E:/11.16/thesis_writing_repo/figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual")
    / "02_CH3_normal_envelope_defect_residual_selected_gallery_cases.csv"
)

NORMAL_SCENARIOS = list(range(800001, 800021))
RESIDUAL_COLUMNS = [
    "depth_residual",
    "total_outflow_residual",
    "pollut_NH4_residual",
    "pollut_TSSs_residual",
]
BANNED_TOKENS = ("persistent", "fulltime", "legacy", "seedset10")


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


def select_scene() -> pd.Series:
    defects = pd.read_csv(FORMAL_DEFECT_MATRIX)
    if DRAW02_SELECTED.exists():
        pair = pd.read_csv(DRAW02_SELECTED).iloc[0]
        scenario_id = int(pair["I_scenario"])
    else:
        scenario_id = 136
    return defects[defects["defect_id"].eq(scenario_id)].iloc[0].copy()


def select_gallery_scenes() -> pd.DataFrame:
    defects = pd.read_csv(FORMAL_DEFECT_MATRIX)
    if DRAW02_GALLERY_CASES.exists():
        cases = pd.read_csv(DRAW02_GALLERY_CASES)
        rows = []
        for _, case in cases.iterrows():
            scenario_id = int(case["preferred_scenario_id"]) if "preferred_scenario_id" in case.index and not pd.isna(case["preferred_scenario_id"]) else int(case["I_scenario"])
            scene = defects[defects["defect_id"].eq(scenario_id)].iloc[0].copy()
            scene["case_id"] = case["case_id"]
            scene["figure_prefix"] = "04" + str(case["figure_prefix"])[2:]
            scene["source_02_prefix"] = case["figure_prefix"]
            scene["outside_ratio"] = case["outside_ratio"]
            scene["rank_metric"] = case["rank_metric"]
            rows.append(scene)
        return pd.DataFrame(rows)
    scene = select_scene()
    scene["case_id"] = "case01"
    scene["figure_prefix"] = "04a"
    scene["source_02_prefix"] = "02a"
    scene["outside_ratio"] = np.nan
    scene["rank_metric"] = ""
    return pd.DataFrame([scene])


def load_topology() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = json.loads(TOPOLOGY_JSON.read_text(encoding="utf-8"))
    coords = pd.DataFrame.from_dict(data["coordinates"], orient="index").rename_axis("node_id").reset_index()
    coords["x_km"] = (coords["x"] - coords["x"].min()) / 1000.0
    coords["y_km"] = (coords["y"] - coords["y"].min()) / 1000.0
    conduits = (
        pd.DataFrame.from_dict(data["conduits"], orient="index")
        .rename_axis("link_id")
        .reset_index()[["link_id", "from_node", "to_node", "length"]]
    )
    return coords, conduits


def read_scene_and_normal(scenario_id: int) -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyarrow is required for draw_04. Run with: "
            "conda run -n swmm_gpu python draw_04_ch3_topology_residual_spatial_map.py"
        ) from exc

    scenario_set = set([scenario_id, *NORMAL_SCENARIOS])
    columns = ["scenario_id", "defect_type", "node_id", "time_step", *RESIDUAL_COLUMNS]
    parts: list[pd.DataFrame] = []
    parquet_file = pq.ParquetFile(FORMAL_RESIDUAL_PARQUET)
    for batch in parquet_file.iter_batches(batch_size=262_144, columns=columns):
        chunk = batch.to_pandas()
        keep = chunk["scenario_id"].isin(scenario_set)
        if keep.any():
            parts.append(chunk.loc[keep].copy())
    if not parts:
        raise ValueError(f"No parquet rows extracted for scenario {scenario_id}.")
    out = pd.concat(parts, ignore_index=True)
    out["hour"] = out["time_step"] * (10.0 / 60.0)
    return out


def compute_energy(ts: pd.DataFrame, scenario_id: int) -> pd.DataFrame:
    normal = ts[ts["scenario_id"].isin(NORMAL_SCENARIOS)]
    scales = normal[RESIDUAL_COLUMNS].abs().quantile(0.95).replace(0, np.nan).fillna(1.0)
    scene = ts[ts["scenario_id"].eq(scenario_id)].copy()
    normalized = scene[RESIDUAL_COLUMNS].divide(scales, axis=1)
    scene["residual_energy"] = np.sqrt((normalized**2).mean(axis=1))
    return scene


def choose_time_slices(scene: pd.DataFrame, scene_row: pd.Series) -> list[tuple[str, float]]:
    start = float(scene_row["start_hour"])
    end = start + float(scene_row["duration_h"])
    active = scene[(scene["hour"] >= start) & (scene["hour"] < end)]
    peak_hour = float(active.groupby("hour")["residual_energy"].max().idxmax())
    return [
        ("pre-active", max(0.0, start - 1.0)),
        ("early-active", start + 0.5),
        ("peak-active", peak_hour),
        ("post-active", min(47.0, end + 1.0)),
    ]


def nearest_time_frame(scene: pd.DataFrame, target_hour: float) -> pd.DataFrame:
    hours = scene["hour"].drop_duplicates().to_numpy()
    hour = float(hours[np.argmin(np.abs(hours - target_hour))])
    return scene[scene["hour"].eq(hour)].copy()


def draw_network_base(ax: plt.Axes, coords: pd.DataFrame, conduits: pd.DataFrame) -> None:
    coord_map = coords.set_index("node_id")[["x_km", "y_km"]].to_dict("index")
    for _, row in conduits.iterrows():
        start = coord_map.get(row["from_node"])
        end = coord_map.get(row["to_node"])
        if not start or not end:
            continue
        ax.plot(
            [start["x_km"], end["x_km"]],
            [start["y_km"], end["y_km"]],
            color="#CBD1D8",
            linewidth=0.75,
            zorder=1,
        )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def scatter_energy(
    ax: plt.Axes,
    frame: pd.DataFrame,
    coords: pd.DataFrame,
    scene_row: pd.Series,
    vmax: float,
    size_scale: float = 105.0,
):
    merged = coords.merge(frame[["node_id", "residual_energy"]], on="node_id", how="left").fillna(
        {"residual_energy": 0.0}
    )
    sc = ax.scatter(
        merged["x_km"],
        merged["y_km"],
        c=merged["residual_energy"],
        cmap="YlGnBu",
        vmin=0,
        vmax=vmax,
        s=18 + size_scale * np.sqrt(np.clip(merged["residual_energy"], 0, vmax) / max(vmax, 1e-9)),
        edgecolors="white",
        linewidths=0.25,
        zorder=3,
    )
    true_node = scene_row["node_id"]
    true_coord = coords[coords["node_id"].eq(true_node)]
    if not true_coord.empty:
        ax.scatter(
            true_coord["x_km"],
            true_coord["y_km"],
            marker="*",
            s=170,
            color=TYPE_COLORS["E"],
            edgecolors="#222222",
            linewidths=0.55,
            zorder=5,
        )
    return sc


def draw(
    scene: pd.DataFrame,
    scene_row: pd.Series,
    coords: pd.DataFrame,
    conduits: pd.DataFrame,
    out_dir: Path,
    basename: str = BASENAME,
) -> None:
    start = float(scene_row["start_hour"])
    end = start + float(scene_row["duration_h"])
    active = scene[(scene["hour"] >= start) & (scene["hour"] < end)]
    active_max = active.groupby("node_id")["residual_energy"].max().reset_index()
    vmax = float(np.nanquantile(active_max["residual_energy"], 0.98))
    vmax = max(vmax, 1e-6)
    slices = choose_time_slices(scene, scene_row)

    fig = plt.figure(figsize=(11.2, 7.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.55, 1.0, 1.0], height_ratios=[1.0, 1.0], wspace=0.08, hspace=0.18)
    ax_main = fig.add_subplot(gs[:, 0])
    draw_network_base(ax_main, coords, conduits)
    main_frame = coords.merge(active_max, on="node_id", how="left").fillna({"residual_energy": 0.0})
    sc = scatter_energy(ax_main, main_frame, coords, scene_row, vmax, size_scale=130)
    ax_main.set_title("A  Maximum response during active window", loc="left", fontweight="bold")

    top_nodes = active_max.sort_values("residual_energy", ascending=False).head(3)
    coord_lookup = coords.set_index("node_id")
    for _, row in top_nodes.iterrows():
        if row["node_id"] not in coord_lookup.index:
            continue
        xy = coord_lookup.loc[row["node_id"]]
        ax_main.text(xy["x_km"] + 0.035, xy["y_km"] + 0.035, row["node_id"], fontsize=7.2, color="#1f2933")

    small_axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2])]
    for ax, (label, target_hour) in zip(small_axes, slices):
        frame = nearest_time_frame(scene, target_hour)
        draw_network_base(ax, coords, conduits)
        scatter_energy(ax, frame, coords, scene_row, vmax, size_scale=70)
        actual_hour = float(frame["hour"].iloc[0])
        ax.set_title(f"{label}  {actual_hour:.1f} h", loc="left", fontsize=9.5, fontweight="bold")

    cbar = fig.colorbar(sc, ax=[ax_main, *small_axes], fraction=0.025, pad=0.018)
    cbar.set_label("Normalized residual energy")
    cbar.ax.tick_params(length=0)

    fig.suptitle(
        f"Spatial-temporal residual response under formal {scene_row['defect_type']} scenario {int(scene_row['defect_id'])}",
        x=0.02,
        y=0.985,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.018,
        f"True defect node marked by star; active window {start:.0f}-{end:.0f} h; scene selected from draw_02 residual envelope-excess ranking.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.03, right=0.92, top=0.91, bottom=0.07)
    save_figure(fig, out_dir, basename)


def write_outputs(
    out_dir: Path,
    manifest: dict,
    scene_row: pd.Series,
    scene: pd.DataFrame,
    coords: pd.DataFrame,
    basename: str = BASENAME,
) -> None:
    start = float(scene_row["start_hour"])
    end = start + float(scene_row["duration_h"])
    active = scene[(scene["hour"] >= start) & (scene["hour"] < end)]
    active_max = (
        active.groupby("node_id")["residual_energy"]
        .agg(["max", "mean"])
        .reset_index()
        .rename(columns={"max": "active_max_energy", "mean": "active_mean_energy"})
        .merge(coords[["node_id", "x_km", "y_km"]], on="node_id", how="left")
        .sort_values("active_max_energy", ascending=False)
    )
    active_max.to_csv(out_dir / f"{basename}_active_node_energy.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([scene_row]).to_csv(out_dir / f"{basename}_selected_scene.csv", index=False, encoding="utf-8-sig")
    audit = pd.DataFrame(
        [
            {"check": "dataset_type", "expected": "ie420_plus_normal20", "actual": manifest["dataset_type"]},
            {"check": "persistent_count", "expected": 0, "actual": manifest["persistent_count"]},
            {"check": "scenario_id", "expected": "formal_scene", "actual": int(scene_row["defect_id"])},
            {"check": "coordinates", "expected": 128, "actual": len(coords)},
            {"check": "node_energy_rows", "expected": 128, "actual": active_max["node_id"].nunique()},
        ]
    )
    audit.to_csv(out_dir / f"{basename}_source_audit.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    gallery_scenes = select_gallery_scenes()
    scene_row = gallery_scenes.iloc[0]
    coords, conduits = load_topology()
    ts = read_scene_and_normal(int(scene_row["defect_id"]))
    scene = compute_energy(ts, int(scene_row["defect_id"]))
    out_dir = ensure_out_dir(OUT_TAG)
    write_outputs(out_dir, manifest, scene_row, scene, coords)
    draw(scene, scene_row, coords, conduits, out_dir)
    gallery_scenes.to_csv(out_dir / f"{BASENAME}_gallery_scenes.csv", index=False, encoding="utf-8-sig")
    for _, case_scene_row in gallery_scenes.iterrows():
        case_basename = f"{case_scene_row['figure_prefix']}_CH3_topology_residual_spatial_map_{case_scene_row['case_id']}"
        case_ts = read_scene_and_normal(int(case_scene_row["defect_id"]))
        case_scene = compute_energy(case_ts, int(case_scene_row["defect_id"]))
        write_outputs(out_dir, manifest, case_scene_row, case_scene, coords, basename=case_basename)
        draw(case_scene, case_scene_row, coords, conduits, out_dir, basename=case_basename)
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

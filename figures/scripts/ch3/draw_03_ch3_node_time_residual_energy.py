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
    style_heatmap_axes_plain,
)


OUT_TAG = "03_CH3_node_time_residual_energy"
BASENAME = "03_CH3_node_time_residual_energy"

NORMAL_SCENARIOS = list(range(800001, 800021))
DRAW02_SELECTED = (
    Path(r"E:/11.16/thesis_writing_repo/figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual")
    / "02_CH3_normal_envelope_defect_residual_selected_pair.csv"
)

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

    for path in [FORMAL_RESIDUAL_PARQUET, FORMAL_DEFECT_MATRIX]:
        lowered = str(path).lower()
        if any(token in lowered for token in BANNED_TOKENS):
            raise ValueError(f"Forbidden protocol token detected in path: {path}")
    return manifest


def select_scene() -> pd.Series:
    defects = pd.read_csv(FORMAL_DEFECT_MATRIX)
    if DRAW02_SELECTED.exists():
        selected = pd.read_csv(DRAW02_SELECTED).iloc[0]
        scenario_id = int(selected["I_scenario"])
        node_id = selected["node_id"]
    else:
        scenario_id = 136
        node_id = "HS1306571"

    row = defects[defects["defect_id"].eq(scenario_id)].iloc[0].copy()
    if row["node_id"] != node_id:
        row["node_id"] = node_id
    return row


def read_scene_and_normal(scenario_id: int) -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyarrow is required for draw_03. Run with: "
            "conda run -n swmm_gpu python draw_03_ch3_node_time_residual_energy.py"
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


def compute_energy(ts: pd.DataFrame, scenario_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    normal = ts[ts["scenario_id"].isin(NORMAL_SCENARIOS)]
    scales = normal[RESIDUAL_COLUMNS].abs().quantile(0.95).replace(0, np.nan).fillna(1.0)
    scene = ts[ts["scenario_id"].eq(scenario_id)].copy()
    normalized = scene[RESIDUAL_COLUMNS].divide(scales, axis=1)
    scene["residual_energy"] = np.sqrt((normalized**2).mean(axis=1))

    matrix = scene.pivot_table(index="node_id", columns="time_step", values="residual_energy", aggfunc="mean")
    node_order = (
        scene.groupby("node_id")["residual_energy"]
        .agg(["max", "mean"])
        .sort_values(["max", "mean"], ascending=[False, False])
        .index
    )
    matrix = matrix.reindex(node_order)
    matrix.columns = [float(c) * (10.0 / 60.0) for c in matrix.columns]

    scale_summary = scales.rename("normal_abs_q95").reset_index().rename(columns={"index": "metric"})
    return matrix, scale_summary


def draw(matrix: pd.DataFrame, scene_row: pd.Series, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 6.4))
    vmax = float(np.nanquantile(matrix.to_numpy(), 0.985))
    image = ax.imshow(matrix.to_numpy(), cmap="YlGnBu", aspect="auto", vmin=0, vmax=max(vmax, 1e-6))
    style_heatmap_axes_plain(ax)

    hours = matrix.columns.to_numpy(dtype=float)
    xticks = np.arange(0, len(hours), 36)
    ax.set_xticks(xticks, [f"{hours[i]:.0f}" for i in xticks])
    yticks = np.linspace(0, len(matrix.index) - 1, 7, dtype=int)
    ax.set_yticks(yticks, [str(i + 1) for i in yticks])
    ax.set_xlabel("Time since simulation start (h)")
    ax.set_ylabel("Nodes ranked by residual energy")

    true_node = scene_row["node_id"]
    if true_node in matrix.index:
        true_pos = int(np.where(matrix.index == true_node)[0][0])
        ax.axhline(true_pos, color=TYPE_COLORS["E"], linewidth=1.4, alpha=0.95)
        ax.text(3, true_pos - 1.8, "true node", va="center", fontsize=8.5, color=TYPE_COLORS["E"])

    start = float(scene_row["start_hour"])
    end = start + float(scene_row["duration_h"])
    ax.axvspan(start / (10.0 / 60.0), end / (10.0 / 60.0), color=TYPE_COLORS["I"], alpha=0.12, linewidth=0)

    cbar = fig.colorbar(image, ax=ax, fraction=0.026, pad=0.03)
    cbar.set_label("Normalized residual energy")
    cbar.ax.tick_params(length=0)

    ax.set_title(
        f"Node-time residual energy under formal I scenario {int(scene_row['defect_id'])}",
        loc="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.02,
        f"Active window: {start:.0f}-{end:.0f} h; true node: {true_node}; rows sorted by peak energy.",
        color=TEXT_GREY,
        fontsize=8.6,
    )
    fig.subplots_adjust(left=0.08, right=0.93, top=0.9, bottom=0.12)
    save_figure(fig, out_dir, BASENAME)


def write_outputs(
    out_dir: Path,
    manifest: dict,
    scene_row: pd.Series,
    matrix: pd.DataFrame,
    scale_summary: pd.DataFrame,
) -> None:
    matrix.to_csv(out_dir / f"{BASENAME}_energy_matrix.csv", encoding="utf-8-sig")
    scale_summary.to_csv(out_dir / f"{BASENAME}_normal_scale_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([scene_row]).to_csv(out_dir / f"{BASENAME}_selected_scene.csv", index=False, encoding="utf-8-sig")
    audit = pd.DataFrame(
        [
            {"check": "dataset_type", "expected": "ie420_plus_normal20", "actual": manifest["dataset_type"]},
            {"check": "persistent_count", "expected": 0, "actual": manifest["persistent_count"]},
            {"check": "scenario_id", "expected": "formal_I_scene", "actual": int(scene_row["defect_id"])},
            {"check": "node_count", "expected": 128, "actual": matrix.shape[0]},
            {"check": "time_points", "expected": 287, "actual": matrix.shape[1]},
        ]
    )
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    scene_row = select_scene()
    ts = read_scene_and_normal(int(scene_row["defect_id"]))
    matrix, scale_summary = compute_energy(ts, int(scene_row["defect_id"]))
    out_dir = ensure_out_dir(OUT_TAG)
    write_outputs(out_dir, manifest, scene_row, matrix, scale_summary)
    draw(matrix, scene_row, out_dir)
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

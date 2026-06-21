from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _ch3_style import (
    FORMAL_DEFECT_MATRIX,
    FORMAL_MANIFEST,
    TEXT_GREY,
    TYPE_COLORS,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
    style_heatmap_axes_plain,
)


OUT_TAG = "06_CH3_case_selection_map"
BASENAME = "06_CH3_case_selection_map"

DRAW02_GALLERY_CASES = (
    Path(r"E:/11.16/thesis_writing_repo/figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual")
    / "02_CH3_normal_envelope_defect_residual_selected_gallery_cases.csv"
)


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
    return manifest


def load_defects() -> pd.DataFrame:
    df = pd.read_csv(FORMAL_DEFECT_MATRIX)
    counts = df["defect_type"].value_counts().to_dict()
    if len(df) != 420 or counts.get("I") != 250 or counts.get("E") != 170:
        raise ValueError(f"Unexpected formal defect matrix: rows={len(df)}, counts={counts}")
    return df


def load_cases(defects: pd.DataFrame) -> pd.DataFrame:
    if not DRAW02_GALLERY_CASES.exists():
        raise FileNotFoundError(f"Run draw_02 first to create {DRAW02_GALLERY_CASES}")
    cases = pd.read_csv(DRAW02_GALLERY_CASES)
    if "preferred_scenario_id" not in cases.columns:
        cases["preferred_scenario_id"] = cases["I_scenario"]
    cases["scenario_id"] = cases["preferred_scenario_id"].astype(int)
    out = cases.merge(
        defects[
            [
                "defect_id",
                "defect_type",
                "node_id",
                "intensity_pct",
                "start_hour",
                "duration_h",
                "flow",
                "baseline_flow",
            ]
        ],
        left_on="scenario_id",
        right_on="defect_id",
        how="left",
        suffixes=("", "_formal"),
    )
    if out["defect_id"].isna().any():
        raise ValueError("Some selected cases are missing from the formal defect matrix.")
    out["source"] = np.where(out["rank_metric"].eq("manual"), "manual", "auto")
    for col in ["node_id", "defect_type", "intensity_pct", "start_hour", "duration_h", "flow", "baseline_flow"]:
        formal_col = f"{col}_formal"
        if formal_col in out.columns:
            out[col] = out[formal_col]
    return out


def make_protocol_matrix(defects: pd.DataFrame, defect_type: str) -> pd.DataFrame:
    subset = defects[defects["defect_type"].eq(defect_type)]
    durations = sorted(defects["duration_h"].unique())
    starts = sorted(defects["start_hour"].unique())
    matrix = pd.crosstab(subset["duration_h"], subset["start_hour"])
    matrix = matrix.reindex(index=durations, columns=starts, fill_value=0)
    matrix.index = [f"{int(v)}h" for v in matrix.index]
    matrix.columns = [f"{int(v)}h" for v in matrix.columns]
    return matrix


def draw_matrix_panel(ax: plt.Axes, matrix: pd.DataFrame, cases: pd.DataFrame, defect_type: str, title: str):
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("#EEF1F4")
    values = matrix.to_numpy(dtype=float)
    masked = np.ma.masked_where(values == 0, values)
    vmax = max(1.0, np.nanmax(values))
    image = ax.imshow(masked, cmap=cmap, aspect="equal", vmin=1, vmax=vmax)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel("Start hour")
    ax.set_ylabel("Duration")
    ax.set_xticks(np.arange(matrix.shape[1]), matrix.columns)
    ax.set_yticks(np.arange(matrix.shape[0]), matrix.index)
    style_heatmap_axes_plain(ax)

    for _, case in cases[cases["defect_type"].eq(defect_type)].iterrows():
        col_label = f"{int(case['start_hour'])}h"
        row_label = f"{int(case['duration_h'])}h"
        if col_label not in matrix.columns or row_label not in matrix.index:
            continue
        x = matrix.columns.get_loc(col_label)
        y = matrix.index.get_loc(row_label)
        marker = "*" if case["source"] == "auto" else "D"
        ax.scatter(x, y, s=155, marker=marker, color=TYPE_COLORS["E"], edgecolors="#222222", linewidths=0.55, zorder=5)
        ax.text(x + 0.18, y - 0.22, case["figure_prefix"], fontsize=8.4, fontweight="bold", color="#1f2933")
    return image


def draw_case_table(ax: plt.Axes, cases: pd.DataFrame) -> None:
    ax.axis("off")
    ax.set_title("C  Displayed cases", loc="left", fontweight="bold", pad=8)
    headers = ["Fig.", "Scene", "Type", "Node", "Start-Dur", "Source"]
    x_positions = [0.00, 0.12, 0.27, 0.40, 0.68, 0.86]
    y = 0.9
    for x, header in zip(x_positions, headers):
        ax.text(x, y, header, transform=ax.transAxes, fontsize=8.6, color=TEXT_GREY, fontweight="bold")
    y -= 0.11
    for _, case in cases.iterrows():
        values = [
            case["figure_prefix"],
            str(int(case["scenario_id"])),
            case["defect_type"],
            case["node_id"],
            f"{int(case['start_hour'])}-{int(case['start_hour'] + case['duration_h'])}h",
            case["source"],
        ]
        for x, value in zip(x_positions, values):
            ax.text(x, y, value, transform=ax.transAxes, fontsize=8.4, color="#1f2933")
        y -= 0.11
    ax.text(
        0.0,
        0.04,
        "Stars are auto-selected by residual envelope-excess; diamonds are manually requested cases.",
        transform=ax.transAxes,
        fontsize=8.2,
        color=TEXT_GREY,
    )


def draw_summary(ax: plt.Axes, defects: pd.DataFrame, cases: pd.DataFrame) -> None:
    summary = pd.DataFrame(
        [
            {"item": "Formal defect scenes", "value": len(defects)},
            {"item": "I scenes", "value": int((defects["defect_type"] == "I").sum())},
            {"item": "E scenes", "value": int((defects["defect_type"] == "E").sum())},
            {"item": "Displayed cases", "value": len(cases)},
        ]
    )
    y = np.arange(len(summary))
    ax.barh(y, summary["value"], color=["#D5DAE0", TYPE_COLORS["I"], TYPE_COLORS["E"], "#B07AA1"], height=0.56)
    ax.set_yticks(y, summary["item"])
    ax.invert_yaxis()
    ax.set_xlabel("Count")
    ax.set_title("D  Protocol scale", loc="left", fontweight="bold")
    for i, value in enumerate(summary["value"]):
        ax.text(value + 5, i, str(int(value)), va="center", fontsize=8.6)
    ax.set_xlim(0, max(summary["value"]) * 1.18)
    style_axes_as_segments(ax, grid_axis="x")


def write_outputs(out_dir: Path, defects: pd.DataFrame, cases: pd.DataFrame, manifest: dict) -> None:
    cases.to_csv(out_dir / f"{BASENAME}_selected_cases.csv", index=False, encoding="utf-8-sig")
    audit = pd.DataFrame(
        [
            {"check": "dataset_type", "expected": "ie420_plus_normal20", "actual": manifest["dataset_type"]},
            {"check": "persistent_count", "expected": 0, "actual": manifest["persistent_count"]},
            {"check": "formal_defect_rows", "expected": 420, "actual": len(defects)},
            {"check": "displayed_cases", "expected": ">=1", "actual": len(cases)},
        ]
    )
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def draw(defects: pd.DataFrame, cases: pd.DataFrame, out_dir: Path) -> None:
    matrix_i = make_protocol_matrix(defects, "I")
    matrix_e = make_protocol_matrix(defects, "E")
    fig = plt.figure(figsize=(11.4, 6.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.0, 1.24], height_ratios=[1.0, 1.0], wspace=0.34, hspace=0.32)
    ax_i = fig.add_subplot(gs[0, 0])
    ax_e = fig.add_subplot(gs[0, 1])
    ax_table = fig.add_subplot(gs[:, 2])
    ax_summary = fig.add_subplot(gs[1, :2])

    image = draw_matrix_panel(ax_i, matrix_i, cases, "I", "A  I protocol cells used by displayed cases")
    draw_matrix_panel(ax_e, matrix_e, cases, "E", "B  E protocol cells used by displayed cases")
    cbar = fig.colorbar(image, ax=[ax_i, ax_e], fraction=0.046, pad=0.03)
    cbar.set_label("Scheduled scenario count")
    cbar.ax.tick_params(length=0)

    draw_case_table(ax_table, cases)
    draw_summary(ax_summary, defects, cases)
    fig.suptitle(
        "Displayed response cases are anchored in the formal IE420 protocol matrix",
        x=0.02,
        y=0.985,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.018,
        "This figure documents where the response examples sit in the formal scenario protocol; it is not a feature-importance analysis.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.11)
    save_figure(fig, out_dir, BASENAME)


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    defects = load_defects()
    cases = load_cases(defects)
    out_dir = ensure_out_dir(OUT_TAG)
    write_outputs(out_dir, defects, cases, manifest)
    draw(defects, cases, out_dir)
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

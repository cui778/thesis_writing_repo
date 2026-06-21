from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize

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


OUT_TAG = "01_CH3_ie420_parameter_matrix"
BASENAME = "01_CH3_ie420_parameter_matrix"

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

    defect_path_in_manifest = Path(manifest["defect_csv_path"]).name
    if defect_path_in_manifest != FORMAL_DEFECT_MATRIX.name:
        raise ValueError(
            f"Manifest defect matrix is {defect_path_in_manifest}, expected {FORMAL_DEFECT_MATRIX.name}"
        )

    lowered = str(FORMAL_DEFECT_MATRIX).lower()
    if any(token in lowered for token in BANNED_TOKENS):
        raise ValueError(f"Forbidden protocol token detected in defect matrix path: {FORMAL_DEFECT_MATRIX}")

    return manifest


def load_defect_matrix() -> pd.DataFrame:
    df = pd.read_csv(FORMAL_DEFECT_MATRIX)
    required = {
        "defect_id",
        "defect_type",
        "node_id",
        "intensity_pct",
        "start_hour",
        "duration_h",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    counts = df["defect_type"].value_counts().to_dict()
    if len(df) != 420 or counts.get("I") != 250 or counts.get("E") != 170:
        raise ValueError(f"Unexpected formal matrix counts: rows={len(df)}, counts={counts}")
    if df.groupby(["defect_type", "node_id"]).size().nunique() != 1:
        raise ValueError("Expected each covered node within each defect type to have equal scenario count.")
    return df


def make_temporal_matrix(df: pd.DataFrame) -> pd.DataFrame:
    start_hours = sorted(df["start_hour"].unique())
    duration_hours = sorted(df["duration_h"].unique())
    rows = []
    labels = []
    for defect_type in ["I", "E"]:
        for duration in duration_hours:
            subset = df[(df["defect_type"] == defect_type) & (df["duration_h"] == duration)]
            counts = subset.groupby("start_hour").size().reindex(start_hours, fill_value=0)
            rows.append(counts.to_numpy())
            labels.append(f"{defect_type} | {duration}h")
    return pd.DataFrame(rows, index=labels, columns=[f"{int(h)}h" for h in start_hours])


def make_type_temporal_matrix(df: pd.DataFrame, defect_type: str) -> pd.DataFrame:
    start_hours = sorted(df["start_hour"].unique())
    duration_hours = sorted(df["duration_h"].unique())
    subset = df[df["defect_type"].eq(defect_type)]
    matrix = pd.crosstab(subset["duration_h"], subset["start_hour"])
    matrix = matrix.reindex(index=duration_hours, columns=start_hours, fill_value=0)
    matrix.index = [f"{int(v)}h" for v in matrix.index]
    matrix.columns = [f"{int(v)}h" for v in matrix.columns]
    return matrix


def make_node_coverage(df: pd.DataFrame) -> pd.DataFrame:
    coverage = (
        df.groupby(["node_id", "defect_type"])
        .size()
        .unstack("defect_type", fill_value=0)
        .reindex(columns=["I", "E"], fill_value=0)
    )
    coverage = coverage.assign(total=coverage["I"] + coverage["E"])
    coverage = coverage.sort_values(["E", "I", "total"], ascending=[False, False, False])
    return coverage[["I", "E"]]


def write_summaries(out_dir: Path, manifest: dict, df: pd.DataFrame) -> None:
    temporal = make_temporal_matrix(df)
    node_coverage = make_node_coverage(df)
    intensity = pd.crosstab(df["intensity_pct"], df["defect_type"]).reindex(columns=["I", "E"], fill_value=0)
    duration = pd.crosstab(df["duration_h"], df["defect_type"]).reindex(columns=["I", "E"], fill_value=0)

    temporal.to_csv(out_dir / f"{BASENAME}_temporal_matrix.csv", encoding="utf-8-sig")
    node_coverage.to_csv(out_dir / f"{BASENAME}_node_coverage.csv", encoding="utf-8-sig")
    intensity.to_csv(out_dir / f"{BASENAME}_intensity_summary.csv", encoding="utf-8-sig")
    duration.to_csv(out_dir / f"{BASENAME}_duration_summary.csv", encoding="utf-8-sig")

    audit = pd.DataFrame(
        [
            {"check": "dataset_type", "expected": "ie420_plus_normal20", "actual": manifest["dataset_type"]},
            {"check": "scenario_count", "expected": 441, "actual": manifest["scenario_count"]},
            {"check": "persistent_count", "expected": 0, "actual": manifest["persistent_count"]},
            {"check": "defect_rows", "expected": 420, "actual": len(df)},
            {"check": "I_count", "expected": 250, "actual": int((df["defect_type"] == "I").sum())},
            {"check": "E_count", "expected": 170, "actual": int((df["defect_type"] == "E").sum())},
            {"check": "I_nodes", "expected": 50, "actual": int(df[df["defect_type"] == "I"]["node_id"].nunique())},
            {"check": "E_nodes", "expected": 34, "actual": int(df[df["defect_type"] == "E"]["node_id"].nunique())},
        ]
    )
    audit["status"] = np.where(audit["expected"].astype(str) == audit["actual"].astype(str), "pass", "check")
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def draw(df: pd.DataFrame, out_dir: Path) -> None:
    temporal_i = make_type_temporal_matrix(df, "I")
    temporal_e = make_type_temporal_matrix(df, "E")
    intensity = pd.crosstab(df["intensity_pct"], df["defect_type"]).reindex(columns=["I", "E"], fill_value=0)
    node_coverage = make_node_coverage(df)

    fig = plt.figure(figsize=(11.2, 6.2))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.55, 1.0],
        height_ratios=[1.0, 1.05],
        hspace=0.5,
        wspace=0.48,
        left=0.07,
        right=0.96,
        bottom=0.09,
        top=0.82,
    )

    sub = gs[0, 0].subgridspec(1, 2, wspace=0.18)
    ax_i = fig.add_subplot(sub[0, 0])
    ax_e = fig.add_subplot(sub[0, 1])
    vmax = max(float(temporal_i.to_numpy().max()), float(temporal_e.to_numpy().max()))
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("#EEF1F4")
    image = None
    for ax, matrix, label in [(ax_i, temporal_i, "I"), (ax_e, temporal_e, "E")]:
        values = matrix.to_numpy(dtype=float)
        masked_values = np.ma.masked_where(values == 0, values)
        image = ax.imshow(masked_values, cmap=cmap, aspect="equal", vmin=1, vmax=vmax)
        ax.set_title(f"{label} scenarios", loc="left", fontsize=9.6, fontweight="bold")
        ax.set_xlabel("Start hour")
        ax.set_xticks(np.arange(matrix.shape[1]), matrix.columns)
        if label == "I":
            ax.set_ylabel("Active duration")
            ax.set_yticks(np.arange(matrix.shape[0]), matrix.index)
        else:
            ax.set_yticks(np.arange(matrix.shape[0]), [])
        style_heatmap_axes_plain(ax)
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                value = int(matrix.iat[row, col])
                if value == 0:
                    continue
                color = "white" if value >= vmax * 0.68 else "#1f2933"
                ax.text(col, row, str(value), ha="center", va="center", fontsize=8.2, color=color)
    ax_i.text(
        0.0,
        1.24,
        "A  Time-gated schedule coverage",
        transform=ax_i.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
    cbar = fig.colorbar(image, ax=[ax_i, ax_e], fraction=0.046, pad=0.03)
    cbar.set_label("Scheduled scenario count")
    cbar.ax.tick_params(length=0)

    ax_intensity = fig.add_subplot(gs[0, 1])
    x = np.arange(len(intensity.index))
    width = 0.34
    ax_intensity.bar(
        x - width / 2,
        intensity["I"],
        width=width,
        color=TYPE_COLORS["I"],
        label="I",
        alpha=0.9,
    )
    ax_intensity.bar(
        x + width / 2,
        intensity["E"],
        width=width,
        color=TYPE_COLORS["E"],
        label="E",
        alpha=0.9,
    )
    ax_intensity.set_title("B  Intensity balance", loc="left", fontweight="bold")
    ax_intensity.set_xlabel("Intensity (%)")
    ax_intensity.set_ylabel("Scenario count")
    ax_intensity.set_xticks(x, [f"{int(v)}" for v in intensity.index])
    ax_intensity.set_ylim(0, max(intensity.max()) * 1.18)
    ax_intensity.legend(frameon=False, loc="upper left", ncol=2, handlelength=1.2)
    for offset, label in [(-width / 2, "I"), (width / 2, "E")]:
        for i, value in enumerate(intensity[label]):
            ax_intensity.text(i + offset, value + 2, str(int(value)), ha="center", va="bottom", fontsize=8.2)
    style_axes_as_segments(ax_intensity, grid_axis="y")

    ax_node = fig.add_subplot(gs[1, 0])
    norm = Normalize(vmin=0, vmax=max(1, int(node_coverage.to_numpy().max())))
    node_image = ax_node.imshow(node_coverage.to_numpy(), cmap="YlGnBu", norm=norm, aspect="auto")
    ax_node.set_title("C  Node coverage fingerprint", loc="left", fontweight="bold")
    ax_node.set_xlabel("Defect type")
    ax_node.set_ylabel("Covered defect nodes")
    ax_node.set_xticks([0, 1], ["I", "E"])
    tick_positions = np.linspace(0, len(node_coverage) - 1, 6, dtype=int)
    ax_node.set_yticks(tick_positions, [str(i + 1) for i in tick_positions])
    style_heatmap_axes_plain(ax_node)
    cbar_node = fig.colorbar(node_image, ax=ax_node, fraction=0.046, pad=0.03)
    cbar_node.set_label("Scenarios per node")
    cbar_node.ax.tick_params(length=0)

    ax_summary = fig.add_subplot(gs[1, 1])
    ax_summary.axis("off")
    summary_lines = [
        ("Formal matrix", "420 defect scenarios"),
        ("I/E split", "250 I + 170 E"),
        ("Temporal grid", "8 starts x 4 durations"),
        ("Staggered starts", "I: 2/8/14/20h; E: 0/6/12/18h"),
        ("Intensity levels", "40%, 50%, 60%"),
        ("Node coverage", "50 I nodes, 34 E nodes"),
        ("Per-node balance", "5 scenarios per covered node/type"),
    ]
    ax_summary.set_title("D  Protocol audit", loc="left", fontweight="bold", pad=10)
    y = 0.92
    for key, value in summary_lines:
        ax_summary.text(0.0, y, key, fontsize=9.2, color=TEXT_GREY, va="top")
        ax_summary.text(0.42, y, value, fontsize=9.6, color="#1f2933", va="top", fontweight="bold")
        y -= 0.14
    ax_summary.text(
        0.0,
        0.02,
        "Source locked to ie420_plus_normal20_v1 and formal_conservative420_seed42.",
        fontsize=8.3,
        color=TEXT_GREY,
        va="bottom",
    )

    fig.suptitle(
        "IE420 formal defect protocol: coverage across type, timing, intensity, and nodes",
        x=0.02,
        y=0.97,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    save_figure(fig, out_dir, BASENAME)


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    df = load_defect_matrix()
    out_dir = ensure_out_dir(OUT_TAG)
    write_summaries(out_dir, manifest, df)
    draw(df, out_dir)
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

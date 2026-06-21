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
    CH3_SOURCE,
    TEXT_GREY,
    TYPE_COLORS,
    apply_style,
    ensure_out_dir,
    save_figure,
    style_axes_as_segments,
)


OUT_TAG = "02_CH3_normal_envelope_defect_residual"
BASENAME = "02_CH3_normal_envelope_defect_residual"
MANUAL_CASES = CH3_SOURCE / "CH3_MANUAL_CASES.csv"

NORMAL_SCENARIOS = list(range(800001, 800021))
BANNED_TOKENS = ("persistent", "fulltime", "legacy", "seedset10")

RESIDUAL_COLUMNS = [
    "depth_residual",
    "total_outflow_residual",
    "pollut_NH4_residual",
    "pollut_TSSs_residual",
]

METRIC_LABELS = {
    "depth_residual": "Depth residual",
    "total_outflow_residual": "Total outflow residual",
    "pollut_NH4_residual": "NH4 residual",
    "pollut_TSSs_residual": "TSSs residual",
}

RAW_LABELS = {
    "depth": "Depth",
    "total_outflow": "Total outflow",
    "pollut_NH4": "NH4",
}


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

    formal_name = FORMAL_DEFECT_MATRIX.name
    if Path(manifest["defect_csv_path"]).name != formal_name:
        raise ValueError(f"Manifest does not point to the formal defect matrix: {manifest['defect_csv_path']}")

    for path in [FORMAL_RESIDUAL_PARQUET, FORMAL_DEFECT_MATRIX]:
        lowered = str(path).lower()
        if any(token in lowered for token in BANNED_TOKENS):
            raise ValueError(f"Forbidden protocol token detected in path: {path}")
    return manifest


def load_defects() -> pd.DataFrame:
    df = pd.read_csv(FORMAL_DEFECT_MATRIX)
    counts = df["defect_type"].value_counts().to_dict()
    if len(df) != 420 or counts.get("I") != 250 or counts.get("E") != 170:
        raise ValueError(f"Unexpected formal defect matrix: rows={len(df)}, counts={counts}")
    return df


def select_candidate_pairs(defects: pd.DataFrame, top_n: int = 24) -> pd.DataFrame:
    candidates = []
    for node_id, group in defects.groupby("node_id"):
        if {"I", "E"} - set(group["defect_type"]):
            continue
        i_row = group[group["defect_type"] == "I"].assign(abs_flow=lambda x: x["flow"].abs())
        e_row = group[group["defect_type"] == "E"].assign(abs_flow=lambda x: x["flow"].abs())
        best_i = i_row.sort_values("abs_flow", ascending=False).iloc[0]
        best_e = e_row.sort_values("abs_flow", ascending=False).iloc[0]
        score = float(abs(best_i["flow"]) + abs(best_e["flow"]))
        candidates.append(
            {
                "matrix_flow_score": score,
                "node_id": node_id,
                "I_scenario": int(best_i["defect_id"]),
                "E_scenario": int(best_e["defect_id"]),
                "I_start_hour": float(best_i["start_hour"]),
                "I_duration_h": float(best_i["duration_h"]),
                "E_start_hour": float(best_e["start_hour"]),
                "E_duration_h": float(best_e["duration_h"]),
                "I_flow": float(best_i["flow"]),
                "E_flow": float(best_e["flow"]),
            }
        )
    if not candidates:
        raise ValueError("No node has both I and E scenarios in the formal defect matrix.")
    return pd.DataFrame(candidates).sort_values("matrix_flow_score", ascending=False).head(top_n)


def read_target_timeseries(node_ids: list[str], scenario_ids: list[int]) -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyarrow is required for draw_02. Run with the swmm_gpu conda environment: "
            "conda run -n swmm_gpu python draw_02_ch3_normal_envelope_defect_residual.py"
        ) from exc

    columns = [
        "datetime",
        "scenario_id",
        "defect_type",
        "node_id",
        "time_step",
        "depth",
        "total_outflow",
        "pollut_NH4",
        *RESIDUAL_COLUMNS,
    ]
    scenario_set = set(scenario_ids)
    node_set = set(node_ids)
    parts: list[pd.DataFrame] = []
    parquet_file = pq.ParquetFile(FORMAL_RESIDUAL_PARQUET)

    for batch in parquet_file.iter_batches(batch_size=262_144, columns=columns):
        chunk = batch.to_pandas()
        keep = chunk["node_id"].isin(node_set) & chunk["scenario_id"].isin(scenario_set)
        if keep.any():
            parts.append(chunk.loc[keep].copy())

    if not parts:
        raise ValueError(f"No residual rows found for nodes={node_ids}, scenarios={scenario_ids}")

    out = pd.concat(parts, ignore_index=True)
    out["hour"] = out["time_step"] * (10.0 / 60.0)
    return out.sort_values(["scenario_id", "time_step"]).reset_index(drop=True)


def envelope_excess_score(ts: pd.DataFrame, metric: str, scenario_ids: list[int]) -> dict:
    normal = ts[ts["scenario_id"].isin(NORMAL_SCENARIOS)]
    defect = ts[ts["scenario_id"].isin(scenario_ids)]
    envelope = (
        normal.groupby("time_step")
        .agg(
            q05=(metric, lambda x: x.quantile(0.05)),
            q95=(metric, lambda x: x.quantile(0.95)),
        )
        .reset_index()
    )
    merged = defect[["scenario_id", "time_step", metric]].merge(envelope, on="time_step", how="left")
    upper_excess = merged[metric] - merged["q95"]
    lower_excess = merged["q05"] - merged[metric]
    outside = np.maximum.reduce([upper_excess.to_numpy(), lower_excess.to_numpy(), np.zeros(len(merged))])
    width = (envelope["q95"] - envelope["q05"]).abs().replace(0, np.nan)
    normal_width_median = float(width.median()) if width.notna().any() else 0.0
    normal_abs_q95 = float(normal[metric].abs().quantile(0.95))
    defect_abs_peak = float(defect[metric].abs().max())
    return {
        "outside_peak": float(np.nanmax(outside)) if len(outside) else 0.0,
        "normal_width_median": normal_width_median,
        "outside_ratio": float(np.nanmax(outside) / max(normal_width_median, 1e-12)) if len(outside) else 0.0,
        "normal_abs_q95": normal_abs_q95,
        "defect_abs_peak": defect_abs_peak,
        "defect_abs_to_normal_q95": defect_abs_peak / max(normal_abs_q95, 1e-12),
    }


def score_candidate_pairs(ts_all: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, pair in pairs.iterrows():
        node_ts = ts_all[ts_all["node_id"].eq(pair["node_id"])]
        scenario_ids = [int(pair["I_scenario"]), int(pair["E_scenario"])]
        for metric in RESIDUAL_COLUMNS:
            score = envelope_excess_score(node_ts, metric, scenario_ids)
            rows.append(
                {
                    "node_id": pair["node_id"],
                    "I_scenario": int(pair["I_scenario"]),
                    "E_scenario": int(pair["E_scenario"]),
                    "metric": metric,
                    "label": METRIC_LABELS[metric],
                    **score,
                    "matrix_flow_score": float(pair["matrix_flow_score"]),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["outside_ratio", "defect_abs_to_normal_q95", "matrix_flow_score"],
        ascending=[False, False, False],
    )


def score_metrics(ts: pd.DataFrame, i_id: int, e_id: int) -> pd.DataFrame:
    rows = []
    for metric in RESIDUAL_COLUMNS:
        score = envelope_excess_score(ts, metric, [i_id, e_id])
        rows.append(
            {
                "metric": metric,
                "label": METRIC_LABELS[metric],
                **score,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["outside_ratio", "defect_abs_to_normal_q95"], ascending=[False, False]
    )


def make_envelope(ts: pd.DataFrame, metric: str) -> pd.DataFrame:
    normal = ts[ts["scenario_id"].isin(NORMAL_SCENARIOS)]
    envelope = (
        normal.groupby("time_step")
        .agg(
            hour=("hour", "first"),
            q05=(metric, lambda x: x.quantile(0.05)),
            q50=(metric, "median"),
            q95=(metric, lambda x: x.quantile(0.95)),
        )
        .reset_index()
    )
    return envelope


def make_raw_envelope(ts: pd.DataFrame, metric: str) -> pd.DataFrame:
    normal = ts[ts["scenario_id"].isin(NORMAL_SCENARIOS)]
    envelope = (
        normal.groupby("time_step")
        .agg(
            hour=("hour", "first"),
            q05=(metric, lambda x: x.quantile(0.05)),
            q50=(metric, "median"),
            q95=(metric, lambda x: x.quantile(0.95)),
        )
        .reset_index()
    )
    return envelope


def draw(ts: pd.DataFrame, selected: pd.DataFrame, pair: pd.Series, out_dir: Path, basename: str = BASENAME) -> None:
    top_metrics = selected["metric"].head(2).tolist()
    i_id = int(pair["I_scenario"])
    e_id = int(pair["E_scenario"])

    fig, axes = plt.subplots(2, 1, figsize=(10.8, 6.6), sharex=True)
    for ax, metric, letter in zip(axes, top_metrics, ["A", "B"]):
        envelope = make_envelope(ts, metric)
        i_curve = ts[ts["scenario_id"] == i_id].sort_values("time_step")
        e_curve = ts[ts["scenario_id"] == e_id].sort_values("time_step")

        hours = envelope["hour"].to_numpy()
        ax.fill_between(
            hours,
            envelope["q05"].to_numpy(),
            envelope["q95"].to_numpy(),
            color="#B9C0C8",
            alpha=0.34,
            linewidth=0,
            label="normal20 5-95% envelope",
        )
        ax.plot(hours, envelope["q50"].to_numpy(), color="#7A828A", linewidth=1.1, label="normal median")
        ax.plot(
            i_curve["hour"].to_numpy(),
            i_curve[metric].to_numpy(),
            color=TYPE_COLORS["I"],
            linewidth=1.8,
            label=f"I scenario {i_id}",
        )
        ax.plot(
            e_curve["hour"].to_numpy(),
            e_curve[metric].to_numpy(),
            color=TYPE_COLORS["E"],
            linewidth=1.8,
            label=f"E scenario {e_id}",
        )

        i_start = float(pair["I_start_hour"])
        i_end = i_start + float(pair["I_duration_h"])
        e_start = float(pair["E_start_hour"])
        e_end = e_start + float(pair["E_duration_h"])
        ax.axvspan(i_start, i_end, color=TYPE_COLORS["I"], alpha=0.09, linewidth=0)
        ax.axvspan(e_start, e_end, color=TYPE_COLORS["E"], alpha=0.09, linewidth=0)
        ax.set_title(f"{letter}  {METRIC_LABELS[metric]} relative to normal envelope", loc="left", fontweight="bold")
        ax.set_ylabel("Residual")
        ax.axhline(0, color="#333333", linewidth=0.7, alpha=0.65)
        style_axes_as_segments(ax, grid_axis="y")

    axes[-1].set_xlabel("Time since simulation start (h)")
    axes[0].legend(frameon=False, loc="upper right", ncol=2, handlelength=1.8)
    fig.suptitle(
        f"Normal envelope vs. I/E defect response at node {pair['node_id']}",
        x=0.02,
        y=0.98,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.012,
        "Representative node is selected automatically by residual envelope-excess score among formal same-node I/E candidates.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.1, hspace=0.34)
    save_figure(fig, out_dir, basename)


def draw_obvious_profile(
    ts: pd.DataFrame,
    selected: pd.DataFrame,
    pair: pd.Series,
    out_dir: Path,
    basename: str = "02_CH3_obvious_defect_profile",
) -> None:
    scenario_id = int(pair["I_scenario"])
    if "preferred_scenario_id" in pair.index and not pd.isna(pair["preferred_scenario_id"]):
        scenario_id = int(pair["preferred_scenario_id"])
    curve = ts[ts["scenario_id"].eq(scenario_id)].sort_values("time_step")
    if curve.empty:
        scenario_id = int(pair["E_scenario"])
        curve = ts[ts["scenario_id"].eq(scenario_id)].sort_values("time_step")

    start = float(pair["I_start_hour"] if scenario_id == int(pair["I_scenario"]) else pair["E_start_hour"])
    duration = float(pair["I_duration_h"] if scenario_id == int(pair["I_scenario"]) else pair["E_duration_h"])
    end = start + duration
    defect_type = "I" if scenario_id == int(pair["I_scenario"]) else "E"
    metric = selected["metric"].iloc[0]

    fig, axes = plt.subplots(4, 1, figsize=(11.0, 7.0), sharex=True, height_ratios=[1.0, 1.0, 1.0, 0.55])
    active_color = TYPE_COLORS[defect_type]

    panels = [
        (axes[0], "total_outflow", "A", "Total outflow profile"),
        (axes[2], "depth", "C", "Depth profile"),
    ]
    for ax, raw_metric, letter, title in panels:
        env = make_raw_envelope(ts, raw_metric)
        ax.fill_between(
            env["hour"].to_numpy(),
            env["q05"].to_numpy(),
            env["q95"].to_numpy(),
            color="#B9C0C8",
            alpha=0.28,
            linewidth=0,
            label="normal20 5-95% envelope",
        )
        ax.plot(env["hour"], env["q50"], color="#7A828A", linewidth=1.0, label="normal median")
        ax.plot(curve["hour"], curve[raw_metric], color="#2F5FD0", linewidth=1.55, label=f"scenario {scenario_id}")
        ax.axvspan(start, end, color=active_color, alpha=0.16, linewidth=0)
        ax.set_title(f"{letter}  {title}", loc="left", fontweight="bold")
        ax.set_ylabel(RAW_LABELS[raw_metric])
        style_axes_as_segments(ax, grid_axis="y")

    ax_res = axes[1]
    ax_res.axvspan(start, end, color=active_color, alpha=0.16, linewidth=0)
    ax_res.axhline(0, color="#333333", linewidth=0.7, alpha=0.7)
    ax_res.plot(curve["hour"], curve[metric], color="#2C8C3C", linewidth=1.25, label=METRIC_LABELS[metric])
    ax_res.set_title(f"B  Residual response ({METRIC_LABELS[metric]})", loc="left", fontweight="bold")
    ax_res.set_ylabel("Residual")
    style_axes_as_segments(ax_res, grid_axis="y")

    ax_mask = axes[3]
    hours = curve["hour"].to_numpy()
    mask = ((hours >= start) & (hours < end)).astype(float)
    ax_mask.fill_between(hours, 0, mask, step="mid", color=active_color, alpha=0.28, label="active window")
    ax_mask.plot(hours, mask, color=active_color, linewidth=1.0)
    ax_mask.set_ylim(-0.08, 1.08)
    ax_mask.set_yticks([0, 1], ["inactive", "active"])
    ax_mask.set_title("D  Defect active mask", loc="left", fontweight="bold")
    ax_mask.set_xlabel("Time since simulation start (h)")
    style_axes_as_segments(ax_mask, grid_axis="")

    for ax in axes:
        ax.set_xlim(0, 48)
    axes[0].legend(frameon=False, loc="upper right", ncol=3, handlelength=1.7)

    fig.suptitle(
        f"Formal time-gated {defect_type} defect profile at node {pair['node_id']}",
        x=0.02,
        y=0.985,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.012,
        f"Selected from formal IE420 by residual envelope-excess score; active window: {start:.0f}-{end:.0f} h.",
        color=TEXT_GREY,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.075, right=0.985, top=0.9, bottom=0.1, hspace=0.5)
    save_figure(fig, out_dir, basename)


def select_gallery_cases(
    candidate_scores: pd.DataFrame,
    pairs: pd.DataFrame,
    max_cases: int = 4,
    min_outside_ratio: float = 0.1,
) -> pd.DataFrame:
    selected = []
    used_nodes: set[str] = set()
    for _, score_row in candidate_scores.iterrows():
        if float(score_row["outside_ratio"]) < min_outside_ratio:
            continue
        node_id = score_row["node_id"]
        if node_id in used_nodes:
            continue
        pair = pairs[
            pairs["node_id"].eq(node_id)
            & pairs["I_scenario"].eq(score_row["I_scenario"])
            & pairs["E_scenario"].eq(score_row["E_scenario"])
        ]
        if pair.empty:
            continue
        out = pair.iloc[0].copy()
        out["rank_metric"] = score_row["metric"]
        out["rank_label"] = score_row["label"]
        out["outside_ratio"] = score_row["outside_ratio"]
        out["defect_abs_to_normal_q95"] = score_row["defect_abs_to_normal_q95"]
        out["preferred_scenario_id"] = int(out["I_scenario"])
        selected.append(out)
        used_nodes.add(node_id)
        if len(selected) >= max_cases:
            break
    if not selected:
        raise ValueError(f"No gallery cases selected with outside_ratio >= {min_outside_ratio}.")
    cases = pd.DataFrame(selected).reset_index(drop=True)
    cases.insert(0, "case_id", [f"case{i + 1:02d}" for i in range(len(cases))])
    cases.insert(1, "figure_prefix", [f"02{chr(ord('a') + i)}" for i in range(len(cases))])
    return cases


def load_manual_cases(defects: pd.DataFrame, existing_cases: pd.DataFrame) -> pd.DataFrame:
    if not MANUAL_CASES.exists():
        return pd.DataFrame()

    manual = pd.read_csv(MANUAL_CASES)
    if manual.empty:
        return pd.DataFrame()

    required = {"case_id", "figure_prefix", "scenario_id"}
    missing = required - set(manual.columns)
    if missing:
        raise ValueError(f"Manual cases missing columns: {sorted(missing)}")

    rows = []
    used_scenarios = set(existing_cases["I_scenario"].astype(int)).union(
        set(existing_cases["E_scenario"].astype(int))
    )
    for _, item in manual.iterrows():
        scenario_id = int(item["scenario_id"])
        if scenario_id in used_scenarios:
            continue
        scene = defects[defects["defect_id"].eq(scenario_id)]
        if scene.empty:
            raise ValueError(f"Manual scenario_id {scenario_id} not found in formal defect matrix.")
        scene = scene.iloc[0]
        if scene["defect_type"] == "I":
            i_scenario = scenario_id
            paired = defects[(defects["node_id"].eq(scene["node_id"])) & (defects["defect_type"].eq("E"))]
            e_scenario = int(paired.iloc[0]["defect_id"]) if not paired.empty else scenario_id
            i_start, i_duration, i_flow = float(scene["start_hour"]), float(scene["duration_h"]), float(scene["flow"])
            if not paired.empty:
                e_start, e_duration, e_flow = (
                    float(paired.iloc[0]["start_hour"]),
                    float(paired.iloc[0]["duration_h"]),
                    float(paired.iloc[0]["flow"]),
                )
            else:
                e_start, e_duration, e_flow = i_start, i_duration, i_flow
        else:
            e_scenario = scenario_id
            paired = defects[(defects["node_id"].eq(scene["node_id"])) & (defects["defect_type"].eq("I"))]
            i_scenario = int(paired.iloc[0]["defect_id"]) if not paired.empty else scenario_id
            e_start, e_duration, e_flow = float(scene["start_hour"]), float(scene["duration_h"]), float(scene["flow"])
            if not paired.empty:
                i_start, i_duration, i_flow = (
                    float(paired.iloc[0]["start_hour"]),
                    float(paired.iloc[0]["duration_h"]),
                    float(paired.iloc[0]["flow"]),
                )
            else:
                i_start, i_duration, i_flow = e_start, e_duration, e_flow

        rows.append(
            {
                "case_id": item["case_id"],
                "figure_prefix": item["figure_prefix"],
                "matrix_flow_score": abs(i_flow) + abs(e_flow),
                "node_id": scene["node_id"],
                "I_scenario": i_scenario,
                "E_scenario": e_scenario,
                "I_start_hour": i_start,
                "I_duration_h": i_duration,
                "E_start_hour": e_start,
                "E_duration_h": e_duration,
                "I_flow": i_flow,
                "E_flow": e_flow,
                "rank_metric": "manual",
                "rank_label": "manual",
                "outside_ratio": np.nan,
                "defect_abs_to_normal_q95": np.nan,
                "preferred_scenario_id": scenario_id,
                "note": item.get("note", ""),
            }
        )
    return pd.DataFrame(rows)


def merge_gallery_cases(auto_cases: pd.DataFrame, manual_cases: pd.DataFrame) -> pd.DataFrame:
    if manual_cases.empty:
        return auto_cases
    common = list(dict.fromkeys([*auto_cases.columns.tolist(), *manual_cases.columns.tolist()]))
    return pd.concat(
        [auto_cases.reindex(columns=common), manual_cases.reindex(columns=common)],
        ignore_index=True,
    )


def write_outputs(
    out_dir: Path,
    manifest: dict,
    ts: pd.DataFrame,
    scores: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    pairs: pd.DataFrame,
    pair: pd.Series,
    gallery_cases: pd.DataFrame,
) -> None:
    pd.DataFrame([pair]).to_csv(out_dir / f"{BASENAME}_selected_pair.csv", index=False, encoding="utf-8-sig")
    pairs.to_csv(out_dir / f"{BASENAME}_candidate_pairs.csv", index=False, encoding="utf-8-sig")
    candidate_scores.to_csv(out_dir / f"{BASENAME}_candidate_signal_scores.csv", index=False, encoding="utf-8-sig")
    scores.to_csv(out_dir / f"{BASENAME}_metric_signal_scores.csv", index=False, encoding="utf-8-sig")
    gallery_cases.to_csv(out_dir / f"{BASENAME}_selected_gallery_cases.csv", index=False, encoding="utf-8-sig")

    plot_metrics = scores["metric"].head(2).tolist()
    keep_cols = [
        "datetime",
        "scenario_id",
        "defect_type",
        "node_id",
        "time_step",
        "hour",
        "depth",
        "total_outflow",
        "pollut_NH4",
        *plot_metrics,
    ]
    ts[keep_cols].to_csv(out_dir / f"{BASENAME}_plot_timeseries.csv", index=False, encoding="utf-8-sig")

    envelopes = []
    for metric in plot_metrics:
        env = make_envelope(ts, metric)
        env.insert(0, "metric", metric)
        envelopes.append(env)
    pd.concat(envelopes, ignore_index=True).to_csv(
        out_dir / f"{BASENAME}_normal_envelope.csv", index=False, encoding="utf-8-sig"
    )

    audit = pd.DataFrame(
        [
            {"check": "dataset_type", "expected": "ie420_plus_normal20", "actual": manifest["dataset_type"]},
            {"check": "persistent_count", "expected": 0, "actual": manifest["persistent_count"]},
            {"check": "node_id", "expected": "auto_selected_by_residual_signal", "actual": pair["node_id"]},
            {"check": "I_scenario", "expected": "formal_matrix", "actual": int(pair["I_scenario"])},
            {"check": "E_scenario", "expected": "formal_matrix", "actual": int(pair["E_scenario"])},
            {"check": "normal_scenarios", "expected": 20, "actual": len(NORMAL_SCENARIOS)},
            {"check": "rows_extracted", "expected": "22 scenarios x 287", "actual": len(ts)},
        ]
    )
    audit.to_csv(out_dir / f"{BASENAME}_source_audit.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_style()
    manifest = verify_formal_sources()
    defects = load_defects()
    pairs = select_candidate_pairs(defects)
    candidate_scenarios = sorted(
        set(pairs["I_scenario"].astype(int)).union(set(pairs["E_scenario"].astype(int))).union(NORMAL_SCENARIOS)
    )
    ts_all = read_target_timeseries(sorted(pairs["node_id"].unique()), candidate_scenarios)
    candidate_scores = score_candidate_pairs(ts_all, pairs)
    auto_cases = select_gallery_cases(candidate_scores, pairs, max_cases=4)
    manual_cases = load_manual_cases(defects, auto_cases)
    gallery_cases = merge_gallery_cases(auto_cases, manual_cases)
    all_nodes = sorted(set(pairs["node_id"]).union(set(gallery_cases["node_id"])))
    all_scenarios = sorted(
        set(candidate_scenarios)
        .union(set(gallery_cases["I_scenario"].astype(int)))
        .union(set(gallery_cases["E_scenario"].astype(int)))
        .union(set(gallery_cases["preferred_scenario_id"].astype(int)))
    )
    if set(all_nodes) != set(pairs["node_id"]) or set(all_scenarios) != set(candidate_scenarios):
        ts_all = read_target_timeseries(all_nodes, all_scenarios)
    pair = gallery_cases.iloc[0]
    scenario_ids = [int(pair["I_scenario"]), int(pair["E_scenario"]), *NORMAL_SCENARIOS]
    ts = ts_all[ts_all["node_id"].eq(pair["node_id"]) & ts_all["scenario_id"].isin(scenario_ids)].copy()
    scores = score_metrics(ts, int(pair["I_scenario"]), int(pair["E_scenario"]))
    out_dir = ensure_out_dir(OUT_TAG)
    write_outputs(out_dir, manifest, ts, scores, candidate_scores, pairs, pair, gallery_cases)
    draw(ts, scores, pair, out_dir)
    draw_obvious_profile(ts, scores, pair, out_dir)
    for _, case in gallery_cases.iterrows():
        case_scenarios = [int(case["I_scenario"]), int(case["E_scenario"]), *NORMAL_SCENARIOS]
        case_ts = ts_all[
            ts_all["node_id"].eq(case["node_id"]) & ts_all["scenario_id"].isin(case_scenarios)
        ].copy()
        case_scores = score_metrics(case_ts, int(case["I_scenario"]), int(case["E_scenario"]))
        prefix = case["figure_prefix"]
        draw(
            case_ts,
            case_scores,
            case,
            out_dir,
            basename=f"{prefix}_CH3_normal_envelope_defect_residual_{case['case_id']}",
        )
        draw_obvious_profile(
            case_ts,
            case_scores,
            case,
            out_dir,
            basename=f"{prefix}_CH3_obvious_defect_profile_{case['case_id']}",
        )
    print(f"Saved {BASENAME}.png/.svg and summaries to {out_dir}")


if __name__ == "__main__":
    main()

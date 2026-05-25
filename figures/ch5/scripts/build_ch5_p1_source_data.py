from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(r"E:\11.16")
THESIS = ROOT / "thesis_writing_repo"
OUT_DIR = THESIS / "figures" / "ch5" / "source_data"

INPUT_DIR = ROOT / "script2_new" / "input_1"
LAYOUT_DIR = ROOT / "script2_new" / "chapter5_layout_optimization" / "outputs" / "layouts"

P0_RAW = OUT_DIR / "CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv"
CANDIDATE_NODES = INPUT_DIR / "candidate_nodes_new.json"
NODE_LIST = INPUT_DIR / "node_list.json"
GRAPH_FEATURES = INPUT_DIR / "graph_path_features.npz"

INF_HOP = 999

METHODS = [
    {
        "method_short": "Degree",
        "method": "degree",
        "layout_path": LAYOUT_DIR / "degree" / "monitor_nodes_degree_N25.json",
    },
    {
        "method_short": "Cand-Obs",
        "method": "candidate_observability",
        "layout_path": LAYOUT_DIR
        / "candidate_observability"
        / "monitor_nodes_candidate_observability_N25.json",
    },
    {
        "method_short": "Two-stage v1",
        "method": "two_stage_balanced_layout_v1",
        "layout_path": LAYOUT_DIR
        / "two_stage_balanced_layout_v1"
        / "monitor_nodes_two_stage_balanced_layout_v1_N25.json",
    },
    {
        "method_short": "v0_2 clean",
        "method": "learnable_layout_network_v0_2_clean_scenario",
        "layout_path": LAYOUT_DIR
        / "learnable_layout_network_v0_2_clean_scenario"
        / "monitor_nodes_learnable_layout_network_v0_2_clean_scenario_N25.json",
    },
    {
        "method_short": "v2_2 clean",
        "method": "learnable_layout_network_v2_2_clean_generalization",
        "layout_path": LAYOUT_DIR
        / "learnable_layout_network_v2_2_clean_generalization"
        / "monitor_nodes_learnable_layout_network_v2_2_clean_generalization_N25.json",
    },
]

METRICS = ["scenario_mrr", "scenario_top1", "scenario_top3", "scenario_top5"]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_list(path: Path, keys: Iterable[str]) -> list[str]:
    data = read_json(path)
    if isinstance(data, list):
        return [str(x) for x in data]
    if isinstance(data, dict):
        for key in keys:
            values = data.get(key)
            if isinstance(values, list):
                return [str(x) for x in values]
    raise ValueError(f"Unsupported JSON structure: {path}")


def sym_hop(shortest: np.ndarray, i: int, j: int) -> int:
    a = int(shortest[i, j])
    b = int(shortest[j, i])
    vals = [x for x in (a, b) if x < INF_HOP]
    return min(vals) if vals else INF_HOP


def tier_from_hop(hop: int) -> str:
    if hop == 0:
        return "direct"
    if 1 <= hop <= 2:
        return "near"
    return "far"


def summarize_candidate_hops(best_hops: np.ndarray) -> dict[str, float]:
    finite = best_hops[best_hops < INF_HOP]
    return {
        "direct": int((best_hops == 0).sum()),
        "near": int(((best_hops >= 1) & (best_hops <= 2)).sum()),
        "far": int((best_hops > 2).sum()),
        "mean_hop": float(finite.mean()) if finite.size else float("nan"),
        "max_hop": float(finite.max()) if finite.size else float("nan"),
    }


def validate_inputs() -> None:
    required = [P0_RAW, CANDIDATE_NODES, NODE_LIST, GRAPH_FEATURES]
    required.extend(spec["layout_path"] for spec in METHODS)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join(missing))


def build_layout_observability() -> tuple[pd.DataFrame, pd.DataFrame]:
    node_list = read_json_list(NODE_LIST, ("node_list", "nodes"))
    candidate_nodes = read_json_list(CANDIDATE_NODES, ("candidate_nodes", "nodes"))
    node_to_idx = {node: idx for idx, node in enumerate(node_list)}
    shortest = np.load(GRAPH_FEATURES)["shortest_dist"]

    detail_rows: list[dict] = []
    summary_rows: list[dict] = []

    for spec in METHODS:
        layout = read_json(spec["layout_path"])
        monitor_nodes = [str(x) for x in layout["monitor_nodes"]]
        monitor_indices = [node_to_idx[node] for node in monitor_nodes if node in node_to_idx]
        if len(monitor_indices) != len(monitor_nodes):
            missing = sorted(set(monitor_nodes) - set(node_to_idx))
            raise ValueError(f"Layout contains unknown monitor nodes: {spec['layout_path']} {missing}")

        best_hops: list[int] = []
        overlap_count = 0
        for candidate in candidate_nodes:
            if candidate not in node_to_idx:
                raise ValueError(f"Unknown candidate node: {candidate}")
            candidate_idx = node_to_idx[candidate]
            hop_pairs = [
                (sym_hop(shortest, candidate_idx, monitor_idx), monitor_node)
                for monitor_idx, monitor_node in zip(monitor_indices, monitor_nodes)
            ]
            min_hop, nearest_monitor = min(hop_pairs, key=lambda item: (item[0], item[1]))
            best_hops.append(min_hop)
            if candidate in monitor_nodes:
                overlap_count += 1
            detail_rows.append(
                {
                    "method_short": spec["method_short"],
                    "method": spec["method"],
                    "layout_file": str(spec["layout_path"]),
                    "monitor_budget_n": int(layout.get("n", len(monitor_nodes))),
                    "candidate_node_id": candidate,
                    "min_monitor_hop": min_hop,
                    "nearest_monitor": nearest_monitor,
                    "observability_tier_layout": tier_from_hop(min_hop),
                    "is_direct": min_hop == 0,
                    "is_near": 1 <= min_hop <= 2,
                    "is_far": min_hop > 2,
                }
            )

        best_hops_arr = np.asarray(best_hops, dtype=np.int16)
        summary = summarize_candidate_hops(best_hops_arr)
        summary_rows.append(
            {
                "method_short": spec["method_short"],
                "method": spec["method"],
                "layout_file": str(spec["layout_path"]),
                "monitor_budget_n": int(layout.get("n", len(monitor_nodes))),
                "candidate_count": len(candidate_nodes),
                "overlap_count": overlap_count,
                **summary,
                "json_direct": layout.get("layout_metrics", {}).get("direct"),
                "json_near": layout.get("layout_metrics", {}).get("near"),
                "json_far": layout.get("layout_metrics", {}).get("far"),
                "json_mean_hop": layout.get("layout_metrics", {}).get("mean_hop"),
                "json_max_hop": layout.get("layout_metrics", {}).get("max_hop"),
                "json_overlap_count": layout.get("layout_metrics", {}).get("overlap_count"),
            }
        )

    detail = pd.DataFrame(detail_rows)
    summary = pd.DataFrame(summary_rows)
    return detail, summary


def aggregate_by_seed(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        raw.groupby(group_cols, as_index=False)
        .agg(
            scenario_count=("scenario_id", "nunique"),
            row_count=("scenario_id", "size"),
            window_count=("n_windows", "sum"),
            scenario_mrr_mean=("scenario_mrr", "mean"),
            scenario_mrr_std=("scenario_mrr", "std"),
            scenario_top1_mean=("scenario_top1", "mean"),
            scenario_top3_mean=("scenario_top3", "mean"),
            scenario_top5_mean=("scenario_top5", "mean"),
        )
        .sort_values(group_cols)
    )


def summarize_across_seed(by_seed: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        by_seed.groupby(group_cols, as_index=False)
        .agg(
            seed_count=("seed", "nunique"),
            scenario_count_mean=("scenario_count", "mean"),
            scenario_count_min=("scenario_count", "min"),
            scenario_count_max=("scenario_count", "max"),
            scenario_mrr_mean=("scenario_mrr_mean", "mean"),
            scenario_mrr_std_across_seed=("scenario_mrr_mean", "std"),
            scenario_top1_mean=("scenario_top1_mean", "mean"),
            scenario_top1_std_across_seed=("scenario_top1_mean", "std"),
            scenario_top3_mean=("scenario_top3_mean", "mean"),
            scenario_top3_std_across_seed=("scenario_top3_mean", "std"),
            scenario_top5_mean=("scenario_top5_mean", "mean"),
            scenario_top5_std_across_seed=("scenario_top5_mean", "std"),
        )
        .sort_values(group_cols)
    )


def build_layout_specific_performance(
    raw: pd.DataFrame, layout_detail: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tiers = layout_detail[
        ["method_short", "method", "candidate_node_id", "min_monitor_hop", "nearest_monitor", "observability_tier_layout"]
    ].rename(columns={"candidate_node_id": "node_id"})
    merged = raw.drop(columns=["min_monitor_hop"], errors="ignore").merge(
        tiers,
        on=["method_short", "method", "node_id"],
        how="left",
        validate="many_to_one",
    )
    if merged["observability_tier_layout"].isna().any():
        bad = merged.loc[merged["observability_tier_layout"].isna(), ["method_short", "method", "node_id"]].drop_duplicates()
        raise ValueError("Missing layout-specific tiers:\n" + bad.to_string(index=False))

    group_cols = ["method_short", "method", "seed", "observability_tier_layout"]
    by_seed = aggregate_by_seed(merged, group_cols)
    summary = summarize_across_seed(
        by_seed,
        ["method_short", "method", "observability_tier_layout"],
    )
    return merged, by_seed, summary


def build_attribute_group_tables(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    for attr in ["defect_type", "intensity_pct", "duration_h", "start_hour"]:
        group_cols = ["method_short", "method", "seed", attr]
        by_seed = aggregate_by_seed(raw, group_cols)
        summary = summarize_across_seed(by_seed, ["method_short", "method", attr])
        outputs[f"{attr}_by_seed"] = by_seed
        outputs[f"{attr}_summary"] = summary
    return outputs


def build_hard_second_definition(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scenario_cols = [
        "scenario_id",
        "defect_type",
        "node_id",
        "link_id",
        "intensity_pct",
        "start_hour",
        "duration_h",
        "observability_tier",
        "is_hard_candidate",
    ]

    degree = raw[raw["method_short"].eq("Degree")]
    degree_scenario = (
        degree.groupby(scenario_cols, dropna=False, as_index=False)
        .agg(degree_mrr_mean=("scenario_mrr", "mean"), degree_seed_count=("seed", "nunique"))
        .sort_values(["degree_mrr_mean", "scenario_id"])
    )
    cutoff = float(degree_scenario["degree_mrr_mean"].quantile(0.25))
    degree_scenario["hard_far_current"] = degree_scenario["is_hard_candidate"].astype(bool)
    degree_scenario["hard_low_mrr_degree_q25"] = degree_scenario["degree_mrr_mean"].le(cutoff)
    degree_scenario["hard_far_and_low_mrr"] = (
        degree_scenario["hard_far_current"] & degree_scenario["hard_low_mrr_degree_q25"]
    )
    degree_scenario["degree_mrr_q25_cutoff"] = cutoff

    flag_cols = [
        "scenario_id",
        "hard_far_current",
        "hard_low_mrr_degree_q25",
        "hard_far_and_low_mrr",
        "degree_mrr_mean",
        "degree_seed_count",
        "degree_mrr_q25_cutoff",
    ]
    flagged = raw.merge(degree_scenario[flag_cols], on="scenario_id", how="left", validate="many_to_one")

    long_rows = []
    for flag_col, label in [
        ("hard_far_current", "far_hard_current"),
        ("hard_low_mrr_degree_q25", "low_mrr_degree_q25"),
        ("hard_far_and_low_mrr", "far_and_low_mrr"),
    ]:
        tmp = flagged.copy()
        tmp["hard_definition"] = label
        tmp["is_hard_under_definition"] = tmp[flag_col].astype(bool)
        long_rows.append(tmp)
    long = pd.concat(long_rows, ignore_index=True)

    group_cols = ["method_short", "method", "seed", "hard_definition", "is_hard_under_definition"]
    by_seed = aggregate_by_seed(long, group_cols)
    summary = summarize_across_seed(
        by_seed,
        ["method_short", "method", "hard_definition", "is_hard_under_definition"],
    )
    return degree_scenario, by_seed, summary


def check_formal_methods(raw: pd.DataFrame) -> None:
    expected = [spec["method_short"] for spec in METHODS]
    got = sorted(raw["method_short"].unique().tolist())
    if sorted(expected) != got:
        raise ValueError(f"Unexpected methods. expected={sorted(expected)} got={got}")
    seeds = sorted(int(x) for x in raw["seed"].unique())
    if seeds != [7, 42, 123]:
        raise ValueError(f"Unexpected seeds: {seeds}")


def check_layout_summary(summary: pd.DataFrame) -> None:
    for _, row in summary.iterrows():
        for col in ["direct", "near", "far", "overlap_count"]:
            json_col = f"json_{col}"
            if pd.notna(row[json_col]) and int(row[col]) != int(row[json_col]):
                raise AssertionError(
                    f"{row['method_short']} {col} mismatch: computed={row[col]} json={row[json_col]}"
                )
        for col in ["mean_hop", "max_hop"]:
            json_col = f"json_{col}"
            if pd.notna(row[json_col]) and abs(float(row[col]) - float(row[json_col])) > 1e-9:
                raise AssertionError(
                    f"{row['method_short']} {col} mismatch: computed={row[col]} json={row[json_col]}"
                )


def write_readme(outputs: list[Path], raw: pd.DataFrame, hard_definition: pd.DataFrame) -> None:
    text = f"""# CH5 P1 no-retrain source data

This batch only rebuilds tables from existing layout JSON files, graph topology
features, and P0 by-scenario metrics. It does not train models and does not
generate figures.

## Scope

- Formal methods: Degree, Cand-Obs, Two-stage v1, v0_2 clean, v2_2 clean.
- Evaluation seeds: 7, 42, 123. These are diagnosis evaluation seeds, not
  layout-generation seeds.
- Monitor budget: N=25.

## Definitions

- direct: candidate node has hop 0 to at least one monitor in the evaluated
  layout.
- near: candidate node has nearest-monitor hop 1 or 2.
- far: candidate node has nearest-monitor hop greater than 2.
- low-MRR hard: scenarios whose Degree mean scenario MRR is at or below the
  bottom 25% quantile across scenarios.
- far and low-MRR hard: scenarios satisfying both the current far-hard flag and
  the low-MRR hard flag.

## Data scale

- P0 raw rows: {len(raw)}
- methods: {raw['method_short'].nunique()}
- seeds: {raw['seed'].nunique()}
- unique scenarios: {raw['scenario_id'].nunique()}
- Degree low-MRR q25 cutoff: {hard_definition['degree_mrr_q25_cutoff'].iloc[0]:.6f}
- low-MRR hard scenarios: {int(hard_definition['hard_low_mrr_degree_q25'].sum())}
- far and low-MRR hard scenarios: {int(hard_definition['hard_far_and_low_mrr'].sum())}

## Outputs

{chr(10).join(f'- `{path.name}`' for path in outputs)}
"""
    readme_path = OUT_DIR / "CH5-P1_README.md"
    readme_path.write_text(text, encoding="utf-8")
    outputs.append(readme_path)


def main() -> None:
    validate_inputs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(P0_RAW)
    check_formal_methods(raw)

    outputs: list[Path] = []

    layout_detail, layout_summary = build_layout_observability()
    if len(layout_detail) != len(METHODS) * 50:
        raise AssertionError(f"Unexpected layout detail row count: {len(layout_detail)}")
    if len(layout_summary) != len(METHODS):
        raise AssertionError(f"Unexpected layout summary row count: {len(layout_summary)}")
    check_layout_summary(layout_summary)

    path = OUT_DIR / "CH5-P1_layout_specific_candidate_observability.csv"
    layout_detail.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    path = OUT_DIR / "CH5-P1_layout_specific_observability_summary.csv"
    layout_summary.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    merged, layout_perf_by_seed, layout_perf_summary = build_layout_specific_performance(raw, layout_detail)
    if len(merged) != len(raw):
        raise AssertionError(f"Merged raw row count changed: raw={len(raw)} merged={len(merged)}")

    path = OUT_DIR / "CH5-P1_layout_specific_raw_with_tiers.csv"
    merged.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    path = OUT_DIR / "CH5-P1_layout_specific_direct_near_far_performance_by_seed.csv"
    layout_perf_by_seed.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    path = OUT_DIR / "CH5-P1_layout_specific_direct_near_far_performance_summary.csv"
    layout_perf_summary.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    attr_tables = build_attribute_group_tables(raw)
    attr_alias = {
        "defect_type": "defect_type",
        "intensity_pct": "intensity",
        "duration_h": "duration",
        "start_hour": "start_hour",
    }
    for attr in ["defect_type", "intensity_pct", "duration_h", "start_hour"]:
        by_seed_path = OUT_DIR / f"CH5-P1_{attr}_performance_by_seed.csv"
        summary_path = OUT_DIR / f"CH5-P1_{attr}_performance_summary.csv"
        attr_tables[f"{attr}_by_seed"].to_csv(by_seed_path, index=False, encoding="utf-8-sig")
        attr_tables[f"{attr}_summary"].to_csv(summary_path, index=False, encoding="utf-8-sig")
        outputs.extend([by_seed_path, summary_path])
        alias = attr_alias[attr]
        if alias != attr:
            alias_by_seed_path = OUT_DIR / f"CH5-P1_{alias}_performance_by_seed.csv"
            alias_summary_path = OUT_DIR / f"CH5-P1_{alias}_performance_summary.csv"
            attr_tables[f"{attr}_by_seed"].to_csv(alias_by_seed_path, index=False, encoding="utf-8-sig")
            attr_tables[f"{attr}_summary"].to_csv(alias_summary_path, index=False, encoding="utf-8-sig")
            outputs.extend([alias_by_seed_path, alias_summary_path])

    hard_definition, hard_by_seed, hard_summary = build_hard_second_definition(raw)
    path = OUT_DIR / "CH5-P1_hard_candidate_second_definitions.csv"
    hard_definition.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    path = OUT_DIR / "CH5-P1_hard_candidate_second_definition_performance_by_seed.csv"
    hard_by_seed.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    path = OUT_DIR / "CH5-P1_hard_candidate_second_definition_performance_summary.csv"
    hard_summary.to_csv(path, index=False, encoding="utf-8-sig")
    outputs.append(path)

    write_readme(outputs, raw, hard_definition)

    print("Wrote CH5 P1 no-retrain source data:")
    for output in outputs:
        print(f"- {output}")


if __name__ == "__main__":
    main()

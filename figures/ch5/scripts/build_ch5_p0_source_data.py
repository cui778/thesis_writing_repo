from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"E:\11.16")
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"

CH5 = ROOT / "script2_new" / "chapter5_layout_optimization"
CH4 = ROOT / "script2_new" / "chapter4_diagnosis_model"
RAW_REPORTS = CH5 / "outputs" / "raw_metrics_from_main_reports_20260413"
LIVE_REPORTS = ROOT / "script2_new" / "outputs" / "reports"

DEFECT_MATRIX = ROOT / "script2_new" / "input_1" / "defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv"
CANDIDATE_TIERS = CH4 / "outputs" / "candidate_observability_tiers.csv"

METHODS = [
    {
        "method_short": "Degree",
        "method": "degree",
        "json_by_seed": {
            7: RAW_REPORTS / "last_run_metrics_ch5_thesis_degree_scen_N25_s7.json",
            42: RAW_REPORTS / "last_run_metrics_ch5_firstcmp_degree_N25_s42.json",
            123: RAW_REPORTS / "last_run_metrics_ch5_thesis_degree_scen_N25_s123.json",
        },
    },
    {
        "method_short": "Cand-Obs",
        "method": "candidate_observability",
        "json_by_seed": {
            7: RAW_REPORTS / "last_run_metrics_ch5_thesis_candidate_observability_scen_N25_s7.json",
            42: RAW_REPORTS / "last_run_metrics_ch5_firstcmp_candidate_observability_N25_s42.json",
            123: RAW_REPORTS / "last_run_metrics_ch5_thesis_candidate_observability_scen_N25_s123.json",
        },
    },
    {
        "method_short": "Two-stage v1",
        "method": "two_stage_balanced_layout_v1",
        "json_by_seed": {
            7: RAW_REPORTS / "last_run_metrics_ch5_thesis_two_stage_balanced_layout_v1_scen_N25_s7.json",
            42: RAW_REPORTS / "last_run_metrics_ch5_tsbal25_s42.json",
            123: RAW_REPORTS / "last_run_metrics_ch5_thesis_two_stage_balanced_layout_v1_scen_N25_s123.json",
        },
    },
    {
        "method_short": "v0_2 clean",
        "method": "learnable_layout_network_v0_2_clean_scenario",
        "json_by_seed": {
            7: LIVE_REPORTS / "last_run_metrics_ch5_thesis_learnable_layout_network_v0_2_clean_scenario_scen_N25_s7.json",
            42: LIVE_REPORTS / "last_run_metrics_ch5_llnv02clean_scen_N25_s42.json",
            123: LIVE_REPORTS / "last_run_metrics_ch5_thesis_learnable_layout_network_v0_2_clean_scenario_scen_N25_s123.json",
        },
    },
    {
        "method_short": "v2_2 clean",
        "method": "learnable_layout_network_v2_2_clean_generalization",
        "json_by_seed": {
            7: RAW_REPORTS / "last_run_metrics_ch5_thesis_learnable_layout_network_v2_2_clean_generalization_scen_N25_s7.json",
            42: RAW_REPORTS / "last_run_metrics_ch5_llnv22clean_gen_scen_N25_s42.json",
            123: RAW_REPORTS / "last_run_metrics_ch5_thesis_learnable_layout_network_v2_2_clean_generalization_scen_N25_s123.json",
        },
    },
]


def read_report(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def build_raw_by_scenario() -> pd.DataFrame:
    defects = pd.read_csv(DEFECT_MATRIX)
    tiers = pd.read_csv(CANDIDATE_TIERS)
    rows: list[dict] = []

    for spec in METHODS:
        for seed, path in spec["json_by_seed"].items():
            report = read_report(path)
            for scenario_id, metrics in report["by_scenario"].items():
                rows.append(
                    {
                        "method_short": spec["method_short"],
                        "method": spec["method"],
                        "seed": seed,
                        "monitor_budget_n": 25,
                        "scenario_id": int(scenario_id),
                        "n_windows": metrics.get("n_windows"),
                        "scenario_mrr": metrics.get("mrr"),
                        "scenario_top1": metrics.get("top1"),
                        "scenario_top3": metrics.get("top3"),
                        "scenario_top5": metrics.get("top5"),
                        "source_json": str(path),
                    }
                )

    raw = pd.DataFrame(rows)
    raw = raw.merge(defects, left_on="scenario_id", right_on="defect_id", how="left")
    raw = raw.merge(
        tiers[["node_id", "observability_tier", "min_monitor_hop", "nearest_monitors"]],
        on="node_id",
        how="left",
    )
    raw["is_hard_candidate"] = raw["observability_tier"].eq("far")
    raw = raw.sort_values(["method_short", "seed", "scenario_id"])
    return raw


def build_main_metrics(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for spec in METHODS:
        for seed, path in spec["json_by_seed"].items():
            report = read_report(path)
            sub = raw[(raw["method_short"] == spec["method_short"]) & (raw["seed"] == seed)]
            rows.append(
                {
                    "method_short": spec["method_short"],
                    "method": spec["method"],
                    "seed": seed,
                    "monitor_budget_n": 25,
                    "window_mrr_from_report": report.get("mrr"),
                    "window_top1_from_report": report.get("topk_recall_1"),
                    "window_top3_from_report": report.get("topk_recall_3"),
                    "window_top5_from_report": report.get("topk_recall_5"),
                    "event_mrr_mean_from_by_scenario": sub["scenario_mrr"].mean(),
                    "event_mrr_std_from_by_scenario": sub["scenario_mrr"].std(ddof=1),
                    "event_top1_mean_from_by_scenario": sub["scenario_top1"].mean(),
                    "event_top3_mean_from_by_scenario": sub["scenario_top3"].mean(),
                    "event_top5_mean_from_by_scenario": sub["scenario_top5"].mean(),
                    "scenario_count": sub["scenario_id"].nunique(),
                    "source_json": str(path),
                }
            )
    return pd.DataFrame(rows).sort_values(["method_short", "seed"])


def build_observability_group(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_seed = (
        raw.groupby(["method_short", "method", "seed", "observability_tier"], as_index=False)
        .agg(
            scenario_count=("scenario_id", "nunique"),
            window_count=("n_windows", "sum"),
            mrr_mean=("scenario_mrr", "mean"),
            mrr_std=("scenario_mrr", "std"),
            top1_mean=("scenario_top1", "mean"),
            top3_mean=("scenario_top3", "mean"),
            top5_mean=("scenario_top5", "mean"),
        )
        .sort_values(["method_short", "seed", "observability_tier"])
    )
    summary = (
        by_seed.groupby(["method_short", "method", "observability_tier"], as_index=False)
        .agg(
            seed_count=("seed", "nunique"),
            scenario_count_mean=("scenario_count", "mean"),
            mrr_mean=("mrr_mean", "mean"),
            mrr_std_across_seed=("mrr_mean", "std"),
            top1_mean=("top1_mean", "mean"),
            top1_std_across_seed=("top1_mean", "std"),
            top3_mean=("top3_mean", "mean"),
            top5_mean=("top5_mean", "mean"),
        )
        .sort_values(["method_short", "observability_tier"])
    )
    return by_seed, summary


def build_hard_candidates(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    hard_nodes = (
        raw[["node_id", "observability_tier", "min_monitor_hop", "nearest_monitors"]]
        .drop_duplicates()
        .query("observability_tier == 'far'")
        .sort_values(["min_monitor_hop", "node_id"], ascending=[False, True])
    )
    hard_scenarios = (
        raw[["scenario_id", "defect_type", "node_id", "intensity_pct", "start_hour", "duration_h"]]
        .drop_duplicates()
        .merge(hard_nodes[["node_id"]], on="node_id", how="inner")
        .sort_values(["node_id", "scenario_id"])
    )
    hard_definition = hard_scenarios.merge(
        hard_nodes[["node_id", "min_monitor_hop", "nearest_monitors"]],
        on="node_id",
        how="left",
    )

    by_seed = (
        raw.groupby(["method_short", "method", "seed", "is_hard_candidate"], as_index=False)
        .agg(
            scenario_count=("scenario_id", "nunique"),
            window_count=("n_windows", "sum"),
            mrr_mean=("scenario_mrr", "mean"),
            mrr_std=("scenario_mrr", "std"),
            top1_mean=("scenario_top1", "mean"),
            top3_mean=("scenario_top3", "mean"),
            top5_mean=("scenario_top5", "mean"),
        )
        .sort_values(["method_short", "seed", "is_hard_candidate"])
    )
    by_seed["candidate_group"] = by_seed["is_hard_candidate"].map({True: "hard_far", False: "other"})

    summary = (
        by_seed.groupby(["method_short", "method", "is_hard_candidate", "candidate_group"], as_index=False)
        .agg(
            seed_count=("seed", "nunique"),
            scenario_count_mean=("scenario_count", "mean"),
            mrr_mean=("mrr_mean", "mean"),
            mrr_std_across_seed=("mrr_mean", "std"),
            top1_mean=("top1_mean", "mean"),
            top1_std_across_seed=("top1_mean", "std"),
            top3_mean=("top3_mean", "mean"),
            top5_mean=("top5_mean", "mean"),
        )
        .sort_values(["method_short", "is_hard_candidate"])
    )
    return hard_definition, by_seed, summary


def write_readme(outputs: list[Path], raw: pd.DataFrame) -> None:
    text = f"""# 第5章 P0 结果数据说明

本批数据只整理结果，不画图、不重训。用途是支撑后续重新设计图形样式。

## 本轮完成的 P0 数据

1. 场景级 raw JSON 重绘主结果：
   - `CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`
   - `CH5-P0_main_metrics_from_raw_json_all_seeds.csv`

2. direct / near / far 性能分组：
   - `CH5-P0_direct_near_far_performance_by_seed.csv`
   - `CH5-P0_direct_near_far_performance_summary.csv`

3. hard candidates 场景性能对比：
   - `CH5-P0_hard_candidates_definition.csv`
   - `CH5-P0_hard_candidates_performance_by_seed.csv`
   - `CH5-P0_hard_candidates_performance_summary.csv`

## 口径

- 方法：Degree / Cand-Obs / Two-stage v1 / v0_2 clean / v2_2 clean。
- 种子：7 / 42 / 123。
- 预算：N=25。
- 数据来源：正式 clean 主线 raw metrics JSON、缺陷矩阵、候选可观测性分层表。
- 不包含旧 `v2_2`、`v1_1/v1_2/v1_3` 或非 clean 探索版本。

## 数据规模

- 场景级记录数：{len(raw)}
- 方法数：{raw['method_short'].nunique()}
- seed 数：{raw['seed'].nunique()}
- 场景数：{raw['scenario_id'].nunique()}
- hard candidate 场景数：{raw.loc[raw['is_hard_candidate'], 'scenario_id'].nunique()}

## 已写出文件

{chr(10).join(f'- `{path.name}`' for path in outputs)}
"""
    (OUT_DIR / "CH5-P0_README.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw = build_raw_by_scenario()
    main_metrics = build_main_metrics(raw)
    obs_by_seed, obs_summary = build_observability_group(raw)
    hard_definition, hard_by_seed, hard_summary = build_hard_candidates(raw)

    outputs = [
        OUT_DIR / "CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv",
        OUT_DIR / "CH5-P0_main_metrics_from_raw_json_all_seeds.csv",
        OUT_DIR / "CH5-P0_direct_near_far_performance_by_seed.csv",
        OUT_DIR / "CH5-P0_direct_near_far_performance_summary.csv",
        OUT_DIR / "CH5-P0_hard_candidates_definition.csv",
        OUT_DIR / "CH5-P0_hard_candidates_performance_by_seed.csv",
        OUT_DIR / "CH5-P0_hard_candidates_performance_summary.csv",
    ]

    frames = [
        raw,
        main_metrics,
        obs_by_seed,
        obs_summary,
        hard_definition,
        hard_by_seed,
        hard_summary,
    ]
    for frame, path in zip(frames, outputs):
        frame.to_csv(path, index=False, encoding="utf-8-sig")

    write_readme(outputs, raw)
    print(f"Wrote {len(outputs)} CSV files to {OUT_DIR}")


if __name__ == "__main__":
    main()

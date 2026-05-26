from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(r"E:\11.16")
SRC_BASE = ROOT / "script2_new"
CH5 = SRC_BASE / "chapter5_layout_optimization"
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"

SEEDS = [7, 42, 123]
LAYOUT_JSON = CH5 / "outputs" / "layouts" / "embedding_guided_clean" / "monitor_nodes_embedding_guided_clean_N25.json"
EMB_DIR = CH5 / "outputs" / "embedding_guided_clean" / "seed42"
P0_MAIN = OUT_DIR / "CH5-P0_main_metrics_from_raw_json_all_seeds.csv"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics_path(seed: int) -> Path:
    return SRC_BASE / "outputs" / "reports" / f"last_run_metrics_ch5_embedding_guided_clean_N25_scenario_s{seed}.json"


def history_path(seed: int) -> Path:
    return SRC_BASE / "outputs" / "model_checkpoints" / f"training_history_ch5_embedding_guided_clean_N25_scenario_s{seed}.csv"


def mean_std(frame: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    rows = []
    for method_short, group in frame.groupby("method_short", sort=False):
        row = {"method_short": method_short, "method": group["method"].iloc[0], "seed_count": group["seed"].nunique()}
        for col in value_cols:
            row[f"{col}_mean"] = group[col].mean()
            row[f"{col}_std"] = group[col].std(ddof=1) if len(group) > 1 else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    required = [
        LAYOUT_JSON,
        EMB_DIR / "layout_structure.csv",
        EMB_DIR / "selection_trace.csv",
        EMB_DIR / "metadata.json",
    ] + [metrics_path(seed) for seed in SEEDS]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required embedding-guided outputs:\n" + "\n".join(missing))

    layout = read_json(LAYOUT_JSON)
    metadata = read_json(EMB_DIR / "metadata.json")

    structure = pd.read_csv(EMB_DIR / "layout_structure.csv")
    structure.insert(0, "method_group", "embedding_guided_probe")
    structure.insert(1, "embedding_seed", 42)
    structure["layout_file"] = str(LAYOUT_JSON)
    structure["checkpoint"] = metadata.get("checkpoint")
    structure["encoder_model_type_resolved"] = metadata.get("encoder_model_type_resolved")
    structure["train_windows_used_for_embedding"] = metadata.get("train_windows_used")
    structure["embedding_shape"] = str(metadata.get("embedding_shape"))
    structure_path = OUT_DIR / "CH5-P2_embedding_guided_clean_layout_structure_seed42.csv"
    structure.to_csv(structure_path, index=False, encoding="utf-8-sig")

    trace = pd.read_csv(EMB_DIR / "selection_trace.csv")
    trace_path = OUT_DIR / "CH5-P2_embedding_guided_clean_selection_trace_seed42.csv"
    trace.to_csv(trace_path, index=False, encoding="utf-8-sig")

    eval_rows = []
    scenario_rows = []
    for seed in SEEDS:
        metrics = read_json(metrics_path(seed))
        by_scenario = metrics.get("by_scenario", {})
        scenario_mrr_mean = pd.Series([row.get("mrr") for row in by_scenario.values()], dtype="float64").mean()
        scenario_top1_mean = pd.Series([row.get("top1") for row in by_scenario.values()], dtype="float64").mean()
        scenario_top3_mean = pd.Series([row.get("top3") for row in by_scenario.values()], dtype="float64").mean()
        scenario_top5_mean = pd.Series([row.get("top5") for row in by_scenario.values()], dtype="float64").mean()

        eval_rows.append(
            {
                "method_short": "embedding-guided clean",
                "method": "embedding_guided_clean",
                "method_group": "embedding_guided_probe",
                "split": "scenario",
                "seed": seed,
                "embedding_seed": 42,
                "monitor_budget_n": 25,
                "mrr": metrics.get("mrr"),
                "top1": metrics.get("topk_recall_1"),
                "top3": metrics.get("topk_recall_3"),
                "top5": metrics.get("topk_recall_5"),
                "event_mrr_mean": scenario_mrr_mean,
                "event_top1": metrics.get("event_level_top1", scenario_top1_mean),
                "event_top3": metrics.get("event_level_top3", scenario_top3_mean),
                "event_top5": metrics.get("event_level_top5", scenario_top5_mean),
                "event_level_count": metrics.get("event_level_count", len(by_scenario)),
                "student_model_type": metrics.get("student_model_type"),
                "lambda_kd": metrics.get("lambda_kd"),
                "lambda_active_kd": metrics.get("lambda_active_kd"),
                "layout_file": str(LAYOUT_JSON),
                "metrics_file": str(metrics_path(seed)),
                "training_history_file": str(history_path(seed)) if history_path(seed).exists() else "",
                "encoder_checkpoint": metadata.get("checkpoint"),
                "encoder_model_type_resolved": metadata.get("encoder_model_type_resolved"),
            }
        )

        for scenario_id, row in by_scenario.items():
            scenario_rows.append(
                {
                    "method_short": "embedding-guided clean",
                    "method": "embedding_guided_clean",
                    "seed": seed,
                    "embedding_seed": 42,
                    "scenario_id": int(scenario_id),
                    "scenario_mrr": row.get("mrr"),
                    "scenario_top1": row.get("top1"),
                    "scenario_top3": row.get("top3"),
                    "scenario_top5": row.get("top5"),
                    "n_windows": row.get("n_windows"),
                }
            )

    eval_df = pd.DataFrame(eval_rows)
    eval_seed42_path = OUT_DIR / "CH5-P2_embedding_guided_clean_evaluation_seed42.csv"
    eval_df[eval_df["seed"].eq(42)].to_csv(eval_seed42_path, index=False, encoding="utf-8-sig")

    eval_all_path = OUT_DIR / "CH5-P2_embedding_guided_clean_evaluation_all_seeds.csv"
    eval_df.to_csv(eval_all_path, index=False, encoding="utf-8-sig")

    summary_cols = ["mrr", "top1", "top3", "top5", "event_mrr_mean", "event_top1", "event_top3", "event_top5"]
    summary = mean_std(eval_df, summary_cols)
    summary_path = OUT_DIR / "CH5-P2_embedding_guided_clean_seed_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    scenario_df = pd.DataFrame(scenario_rows).sort_values(["seed", "scenario_id"])
    scenario_seed42_path = OUT_DIR / "CH5-P2_embedding_guided_clean_by_scenario_seed42.csv"
    scenario_df[scenario_df["seed"].eq(42)].to_csv(scenario_seed42_path, index=False, encoding="utf-8-sig")
    scenario_all_path = OUT_DIR / "CH5-P2_embedding_guided_clean_by_scenario_all_seeds.csv"
    scenario_df.to_csv(scenario_all_path, index=False, encoding="utf-8-sig")

    comparison_rows = []
    if P0_MAIN.exists():
        p0 = pd.read_csv(P0_MAIN)
        for _, row in p0.iterrows():
            comparison_rows.append(
                {
                    "method_short": row["method_short"],
                    "method": row["method"],
                    "evidence_group": "formal_clean_all_seeds",
                    "seed": int(row["seed"]),
                    "monitor_budget_n": int(row["monitor_budget_n"]),
                    "mrr": row["window_mrr_from_report"],
                    "top1": row["window_top1_from_report"],
                    "top3": row["window_top3_from_report"],
                    "top5": row["window_top5_from_report"],
                    "event_mrr_mean": row["event_mrr_mean_from_by_scenario"],
                    "event_top1": row["event_top1_mean_from_by_scenario"],
                    "event_top3": row["event_top3_mean_from_by_scenario"],
                    "event_top5": row["event_top5_mean_from_by_scenario"],
                }
            )
    for _, row in eval_df.iterrows():
        comparison_rows.append(
            {
                "method_short": row["method_short"],
                "method": row["method"],
                "evidence_group": "embedding_guided_probe_all_seeds",
                "seed": int(row["seed"]),
                "monitor_budget_n": int(row["monitor_budget_n"]),
                "mrr": row["mrr"],
                "top1": row["top1"],
                "top3": row["top3"],
                "top5": row["top5"],
                "event_mrr_mean": row["event_mrr_mean"],
                "event_top1": row["event_top1"],
                "event_top3": row["event_top3"],
                "event_top5": row["event_top5"],
            }
        )

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_seed42_path = OUT_DIR / "CH5-P2_embedding_guided_clean_seed42_comparison.csv"
    comparison_df[comparison_df["seed"].eq(42)].sort_values("mrr", ascending=False).to_csv(
        comparison_seed42_path,
        index=False,
        encoding="utf-8-sig",
    )
    comparison_all_path = OUT_DIR / "CH5-P2_embedding_guided_clean_all_seed_comparison.csv"
    comparison_df.sort_values(["seed", "mrr"], ascending=[True, False]).to_csv(
        comparison_all_path,
        index=False,
        encoding="utf-8-sig",
    )

    comparison_summary = mean_std(comparison_df, summary_cols)
    comparison_summary = comparison_summary.sort_values("mrr_mean", ascending=False)
    comparison_summary_path = OUT_DIR / "CH5-P2_embedding_guided_clean_comparison_seed_summary.csv"
    comparison_summary.to_csv(comparison_summary_path, index=False, encoding="utf-8-sig")

    layout_copy_path = OUT_DIR / "CH5-P2_monitor_nodes_embedding_guided_clean_N25.json"
    shutil.copyfile(LAYOUT_JSON, layout_copy_path)

    summary_row = summary.iloc[0]
    readme = f"""# CH5 P2 embedding-guided clean

This batch records the embedding-guided clean layout and its diagnosis-seed
evaluation results.

Method role:
- This is a diagnosis-representation-guided layout probe.
- It reuses the trained diagnosis encoder checkpoint and does not learn from
  historical layout scores.
- The layout is generated once from the seed42 encoder and then evaluated under
  diagnosis seeds 7, 42, and 123. These seeds are diagnosis evaluation seeds,
  not layout-generation seeds.

Key protocol:
- Checkpoint: `{metadata.get('checkpoint')}`
- Resolved encoder type: `{metadata.get('encoder_model_type_resolved')}`
- Train windows used for embedding extraction: `{metadata.get('train_windows_used')}`
- Embedding shape: `{metadata.get('embedding_shape')}`
- Selection rule: max-min diversity on L2-normalized node embeddings.
- Evaluation: Chapter-5 sparse-observation scenario split, seeds {SEEDS}, 25 epochs.

Layout structure:
- overlap_count: {layout['layout_metrics'].get('overlap_count')}
- direct / near / far: {layout['layout_metrics'].get('direct')} / {layout['layout_metrics'].get('near')} / {layout['layout_metrics'].get('far')}

Multi-seed result:
- MRR mean/std: {summary_row['mrr_mean']:.6f} / {summary_row['mrr_std']:.6f}
- Top-1 mean/std: {summary_row['top1_mean']:.6f} / {summary_row['top1_std']:.6f}
- Top-3 mean/std: {summary_row['top3_mean']:.6f} / {summary_row['top3_std']:.6f}
- Top-5 mean/std: {summary_row['top5_mean']:.6f} / {summary_row['top5_std']:.6f}

Outputs:
- `CH5-P2_embedding_guided_clean_layout_structure_seed42.csv`
- `CH5-P2_embedding_guided_clean_selection_trace_seed42.csv`
- `CH5-P2_embedding_guided_clean_evaluation_seed42.csv`
- `CH5-P2_embedding_guided_clean_evaluation_all_seeds.csv`
- `CH5-P2_embedding_guided_clean_seed_summary.csv`
- `CH5-P2_embedding_guided_clean_by_scenario_seed42.csv`
- `CH5-P2_embedding_guided_clean_by_scenario_all_seeds.csv`
- `CH5-P2_embedding_guided_clean_seed42_comparison.csv`
- `CH5-P2_embedding_guided_clean_all_seed_comparison.csv`
- `CH5-P2_embedding_guided_clean_comparison_seed_summary.csv`
- `CH5-P2_monitor_nodes_embedding_guided_clean_N25.json`
"""
    readme_path = OUT_DIR / "CH5-P2_embedding_guided_clean_README.md"
    readme_path.write_text(readme, encoding="utf-8")

    print("Wrote embedding-guided clean source data:")
    for path in [
        structure_path,
        trace_path,
        eval_seed42_path,
        eval_all_path,
        summary_path,
        scenario_seed42_path,
        scenario_all_path,
        comparison_seed42_path,
        comparison_all_path,
        comparison_summary_path,
        layout_copy_path,
        readme_path,
    ]:
        print(f"- {path}")


if __name__ == "__main__":
    main()

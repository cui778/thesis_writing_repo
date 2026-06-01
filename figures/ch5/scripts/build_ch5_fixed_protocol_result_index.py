from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(r"E:\11.16")
REPORTS = ROOT / "script2_new" / "outputs" / "reports"
EXPERIMENTS = ROOT / "script2_new" / "experiments"
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"


MAIN_METHODS = [
    {
        "method": "Degree",
        "layout_id": "degree_N25",
        "budget": 25,
        "role": "fixed_protocol_reference",
        "metrics": REPORTS
        / "last_run_metrics_48h_control_ie420_normal20_raw_plus_residual_loc0p5_degree_N25_s42.json",
        "protocol": "IE420+normal20",
        "evidence_status": "formal_fixed_protocol_reference",
        "formal": "yes_reference_only",
    },
    {
        "method": "Cand-Obs",
        "layout_id": "candidate_observability_N25",
        "budget": 25,
        "role": "task_driven_baseline",
        "metrics": REPORTS
        / "last_run_metrics_ch5_core_candidate_observability_N25_scenario_s42.json",
        "protocol": "old_ch5_core_path",
        "evidence_status": "old_path_pending_alignment",
        "formal": "no",
    },
    {
        "method": "Two-stage v1",
        "layout_id": "two_stage_balanced_layout_v1_N25",
        "budget": 25,
        "role": "task_driven_optimization",
        "metrics": REPORTS
        / "last_run_metrics_ch5_core_two_stage_balanced_layout_v1_N25_scenario_s42.json",
        "protocol": "old_ch5_core_path",
        "evidence_status": "old_path_pending_alignment",
        "formal": "no",
    },
    {
        "method": "Node-Feedback",
        "layout_id": "v0_2_clean_scenario_N25",
        "budget": 25,
        "role": "external_feedback_node_level",
        "metrics": REPORTS
        / "last_run_metrics_ch5_core_v0_2_clean_scenario_N25_scenario_s42.json",
        "protocol": "old_ch5_core_path",
        "evidence_status": "old_path_pending_alignment",
        "formal": "no",
    },
    {
        "method": "Surrogate-Search",
        "layout_id": "v2_2_clean_generalization_N25",
        "budget": 25,
        "role": "external_feedback_layout_level",
        "metrics": REPORTS
        / "last_run_metrics_ch5_core_v2_2_clean_generalization_N25_scenario_s42.json",
        "protocol": "old_ch5_core_path",
        "evidence_status": "old_path_pending_alignment",
        "formal": "no",
    },
]

EMBEDDING_METRICS = [
    REPORTS / f"last_run_metrics_ch5_embedding_guided_clean_N25_scenario_s{s}.json"
    for s in (7, 42, 123)
]


def first_number(*values: object) -> float | None:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def flatten_metrics(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"metrics_exists": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # keep index robust against corrupted JSON
        return {"metrics_exists": True, "json_error": str(exc)}

    candidates: list[dict] = [data] if isinstance(data, dict) else []
    if isinstance(data, dict):
        for key in ("metrics", "test_metrics", "scenario_metrics", "event_metrics", "summary"):
            if isinstance(data.get(key), dict):
                candidates.append(data[key])

    def get(*names: str) -> float | None:
        vals = []
        for source in candidates:
            for name in names:
                vals.append(source.get(name))
        return first_number(*vals)

    return {
        "metrics_exists": True,
        "seed": get("seed", "diagnosis_seed"),
        "active_f1": get("active_f1", "active_f1_best", "test_active_f1"),
        "normal_window_fpr": get("normal_window_fpr", "test_normal_window_fpr"),
        "scene_recall": get("scene_recall", "test_scene_recall"),
        "scene_fpr": get("scene_fpr", "test_scene_fpr"),
        "scene_f1": get("scene_f1", "test_scene_f1"),
        "mrr": get("mrr", "test_mrr", "scenario_mrr"),
        "top1": get("top1", "top_1", "test_top1", "scenario_top1"),
        "top3": get("top3", "top_3", "test_top3", "scenario_top3"),
        "top5": get("top5", "top_5", "test_top5", "scenario_top5"),
        "event_top1": get("event_top1", "event_level_top1"),
        "event_top3": get("event_top3", "event_level_top3"),
        "event_top5": get("event_top5", "event_level_top5"),
    }


def read_bridge_budget_rows() -> list[dict[str, object]]:
    table = EXPERIMENTS / "tables" / "table_layout_budget_comparison.csv"
    if not table.exists():
        return []
    rows: list[dict[str, object]] = []
    with table.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "method": {
                        "degree": "Degree",
                        "two_stage_balanced": "Two-stage v1",
                    }.get(row.get("layout", ""), row.get("layout", "")),
                    "layout_id": f"{row.get('layout')}_N{int(float(row.get('budget', 0)))}",
                    "budget": int(float(row.get("budget", 0))),
                    "role": "bridge_or_budget_existing",
                    "protocol": "IE420+normal_multibaseline_seedset10",
                    "evidence_status": "bridge_pending_protocol_review",
                    "formal": "no",
                    "metrics_file": row.get("metrics_file", ""),
                    "seed": 42,
                    "feature_set": row.get("feature_set", ""),
                    "lambda_loc": row.get("lambda_loc", ""),
                    "active_f1": row.get("active_f1", ""),
                    "normal_window_fpr": row.get("normal_window_fpr", ""),
                    "scene_recall": row.get("scene_recall", ""),
                    "scene_fpr": row.get("scene_fpr", ""),
                    "scene_f1": row.get("scene_f1", ""),
                    "mrr": row.get("mrr", ""),
                    "top1": row.get("top1", ""),
                    "top3": row.get("top3", ""),
                    "top5": row.get("top5", ""),
                    "event_top1": row.get("event_top1", ""),
                    "event_top3": row.get("event_top3", ""),
                    "event_top5": row.get("event_top5", ""),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows: list[dict[str, object]] = []
    for spec in MAIN_METHODS:
        metrics = flatten_metrics(spec["metrics"])
        rows.append(
            {
                "method": spec["method"],
                "layout_id": spec["layout_id"],
                "budget": spec["budget"],
                "role": spec["role"],
                "protocol": spec["protocol"],
                "feature_set": "raw_plus_residual"
                if "normal20" in spec["protocol"]
                else "pending_review",
                "lambda_loc": 0.5 if "normal20" in spec["protocol"] else "pending_review",
                "diagnosis_seed": int(metrics.get("seed") or 42),
                "metrics_file": str(spec["metrics"]),
                "metrics_exists": metrics.get("metrics_exists", False),
                "evidence_status": spec["evidence_status"],
                "can_enter_formal_main_table": spec["formal"],
                **metrics,
            }
        )

    for path in EMBEDDING_METRICS:
        match = re.search(r"_s(\d+)\.json$", path.name)
        seed = int(match.group(1)) if match else ""
        metrics = flatten_metrics(path)
        rows.append(
            {
                "method": "Embedding-Guided",
                "layout_id": "embedding_guided_clean_N25",
                "budget": 25,
                "role": "internal_embedding_guided",
                "protocol": "old_embedding_guided_path",
                "feature_set": "pending_review",
                "lambda_loc": "pending_review",
                "diagnosis_seed": seed,
                "metrics_file": str(path),
                "metrics_exists": metrics.get("metrics_exists", False),
                "evidence_status": "old_path_pending_alignment",
                "can_enter_formal_main_table": "no",
                **metrics,
            }
        )

    bridge_rows = read_bridge_budget_rows()

    fieldnames = [
        "method",
        "layout_id",
        "budget",
        "role",
        "protocol",
        "feature_set",
        "lambda_loc",
        "diagnosis_seed",
        "metrics_file",
        "metrics_exists",
        "evidence_status",
        "can_enter_formal_main_table",
        "active_f1",
        "normal_window_fpr",
        "scene_recall",
        "scene_fpr",
        "scene_f1",
        "mrr",
        "top1",
        "top3",
        "top5",
        "event_top1",
        "event_top3",
        "event_top5",
    ]

    write_csv(OUT_DIR / "CH5-EXPT_fixed_protocol_result_index.csv", rows, fieldnames)
    write_csv(OUT_DIR / "CH5-EXPT_bridge_budget_existing_results.csv", bridge_rows, fieldnames)

    required_methods = [
        "Cand-Obs",
        "Two-stage v1",
        "Node-Feedback",
        "Surrogate-Search",
        "Embedding-Guided",
    ]
    missing_rows = []
    for method in required_methods:
        has_formal = any(
            r["method"] == method and r["can_enter_formal_main_table"] == "yes"
            for r in rows
        )
        missing_rows.append(
            {
                "method": method,
                "budget": 25,
                "diagnosis_seed": 42,
                "needed_for": "CH5 N25 optimization-method main table",
                "current_status": "available_old_or_bridge_only" if not has_formal else "formal_exists",
                "next_action": "run_or_verify_under_IE420_normal20_raw_plus_residual_loc0p5"
                if not has_formal
                else "none",
            }
        )
    write_csv(
        OUT_DIR / "CH5-EXPT_fixed_protocol_missing_main_runs.csv",
        missing_rows,
        ["method", "budget", "diagnosis_seed", "needed_for", "current_status", "next_action"],
    )

    readme = OUT_DIR / "CH5-EXPT_fixed_protocol_result_index_README.md"
    readme.write_text(
        "# CH5 fixed protocol result index\n\n"
        "This index separates strict Chapter 4 fixed-protocol evidence from bridge, old-path, and mechanism evidence.\n\n"
        "- `CH5-EXPT_fixed_protocol_result_index.csv`: N25 main-method evidence status.\n"
        "- `CH5-EXPT_bridge_budget_existing_results.csv`: existing 48h layout-budget path results, mostly `normal_multibaseline_seedset10`.\n"
        "- `CH5-EXPT_fixed_protocol_missing_main_runs.csv`: methods still needing strict `IE420 + normal20 / raw_plus_residual / lambda_loc=0.5` verification before formal CH5 ranking.\n\n"
        "Do not treat old-path rows as formal fixed-protocol ranking results.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

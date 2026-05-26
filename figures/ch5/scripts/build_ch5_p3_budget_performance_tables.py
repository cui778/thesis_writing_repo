from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"E:\11.16")
MANIFEST = ROOT / "script2_new" / "chapter5_layout_optimization" / "plans" / "CH5_CORE_BUDGET_PERFORMANCE_MANIFEST.csv"
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_layout_metrics(layout_file: str) -> dict:
    payload = read_json(Path(layout_file))
    metrics = payload.get("layout_metrics", {})
    return {
        "direct": metrics.get("direct"),
        "near": metrics.get("near"),
        "far": metrics.get("far"),
        "mean_hop": metrics.get("mean_hop"),
        "max_hop": metrics.get("max_hop"),
        "overlap_count": metrics.get("overlap_count"),
        "monitor_dispersion_mean_hop": metrics.get("monitor_dispersion_mean_hop"),
        "monitor_redundancy_mean_jaccard": metrics.get("monitor_redundancy_mean_jaccard"),
        "global_mean_hop": metrics.get("global_mean_hop"),
    }


def extract_report_metrics(metrics_file: str) -> dict:
    path = Path(metrics_file)
    if not path.exists():
        return {"metrics_status": "missing"}
    try:
        report = read_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"metrics_status": "corrupt"}
    by_scenario = report.get("by_scenario", {})
    event = {}
    if by_scenario:
        values = list(by_scenario.values())
        event = {
            "event_mrr_mean": sum(float(x.get("mrr", 0.0)) for x in values) / len(values),
            "event_top1_mean": sum(float(x.get("top1", 0.0)) for x in values) / len(values),
            "event_top3_mean": sum(float(x.get("top3", 0.0)) for x in values) / len(values),
            "event_top5_mean": sum(float(x.get("top5", 0.0)) for x in values) / len(values),
            "scenario_count": len(values),
        }
    return {
        "metrics_status": "available",
        "window_mrr": report.get("mrr"),
        "window_top1": report.get("topk_recall_1"),
        "window_top3": report.get("topk_recall_3"),
        "window_top5": report.get("topk_recall_5"),
        **event,
    }


def summarize(by_seed: pd.DataFrame) -> pd.DataFrame:
    available = by_seed[by_seed["metrics_status"].eq("available")].copy()
    metric_cols = [
        "window_mrr",
        "window_top1",
        "window_top3",
        "window_top5",
        "event_mrr_mean",
        "event_top1_mean",
        "event_top3_mean",
        "event_top5_mean",
        "direct",
        "near",
        "far",
        "mean_hop",
        "overlap_count",
    ]
    summary_cols = [
        "method_key",
        "method_short",
        "method",
        "budget",
        "diagnosis_seed_count",
    ]
    for col in metric_cols:
        summary_cols.extend([f"{col}_mean", f"{col}_std", f"{col}_min", f"{col}_max"])
    if available.empty:
        return pd.DataFrame(columns=summary_cols)
    return (
        available.groupby(["method_key", "method_short", "method", "budget"], as_index=False)
        .agg(
            diagnosis_seed_count=("diagnosis_seed", "nunique"),
            **{f"{col}_mean": (col, "mean") for col in metric_cols},
            **{f"{col}_std": (col, "std") for col in metric_cols},
            **{f"{col}_min": (col, "min") for col in metric_cols},
            **{f"{col}_max": (col, "max") for col in metric_cols},
        )
        .sort_values(["method_key", "budget"])
    )


def write_readme(outputs: list[Path], by_seed: pd.DataFrame) -> None:
    missing = int(by_seed["metrics_status"].eq("missing").sum())
    available = int(by_seed["metrics_status"].eq("available").sum())
    text = f"""# CH5 P3 budget performance tables

This batch summarizes budget-performance retraining results from
`CH5_CORE_BUDGET_PERFORMANCE_MANIFEST.csv`.

Status:

- available metrics rows: {available}
- missing metrics rows: {missing}
- expected rows: {len(by_seed)}

Important boundary:

- Missing rows mean the corresponding training command has not completed or
  its metrics JSON is not in the expected reports directory.
- Only scenario split is included. Node-holdout is not part of P3 main ranking.

Outputs:

{chr(10).join(f'- `{path.name}`' for path in outputs)}
"""
    path = OUT_DIR / "CH5-P3_budget_performance_README.md"
    path.write_text(text, encoding="utf-8")
    outputs.append(path)


def main() -> None:
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(MANIFEST)

    rows = []
    for _, row in manifest.iterrows():
        base = row.to_dict()
        base.update(extract_layout_metrics(str(row["layout_file"])))
        base.update(extract_report_metrics(str(row["metrics_file"])))
        rows.append(base)
    by_seed = pd.DataFrame(rows)
    summary = summarize(by_seed)
    join_cols = [
        "method_key",
        "method_short",
        "method",
        "budget",
        "direct",
        "near",
        "far",
        "mean_hop",
        "overlap_count",
        "monitor_dispersion_mean_hop",
        "monitor_redundancy_mean_jaccard",
        "global_mean_hop",
    ]
    structure_join = by_seed[join_cols].drop_duplicates().sort_values(["method_key", "budget"])
    if not summary.empty:
        structure_join = structure_join.merge(summary, on=["method_key", "method_short", "method", "budget"], how="left")

    outputs = []
    for name, df in [
        ("CH5-P3_budget_performance_by_seed.csv", by_seed),
        ("CH5-P3_budget_performance_summary.csv", summary),
        ("CH5-P3_budget_structure_performance_join.csv", structure_join),
    ]:
        path = OUT_DIR / name
        df.to_csv(path, index=False, encoding="utf-8-sig")
        outputs.append(path)
    write_readme(outputs, by_seed)

    print("Wrote CH5 P3 budget tables:")
    for path in outputs:
        print(f"- {path}")
    print(by_seed["metrics_status"].value_counts().to_string())


if __name__ == "__main__":
    main()

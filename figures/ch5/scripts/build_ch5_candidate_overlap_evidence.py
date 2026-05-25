from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"E:\11.16")
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"
RAW_REPORTS = ROOT / "script2_new" / "chapter5_layout_optimization" / "outputs" / "raw_metrics_from_main_reports_20260413"
LAYOUT_DIR = ROOT / "script2_new" / "chapter5_layout_optimization" / "outputs" / "layouts"

FORMAL_MAIN = OUT_DIR / "CH5-P0_main_metrics_from_raw_json_all_seeds.csv"
FORMAL_STRUCTURE = OUT_DIR / "CH5-P1_layout_specific_observability_summary.csv"

PROBE_SPECS = [
    {
        "method_short": "Overlap candidate-focus",
        "method": "overlap_controlled_candidate_focus",
        "layout_file": LAYOUT_DIR
        / "overlap_controlled_candidate_focus"
        / "monitor_nodes_overlap_controlled_candidate_focus_N25.json",
        "metrics_file": RAW_REPORTS / "last_run_metrics_ch5_probe_occf_N25_s42.json",
    },
    {
        "method_short": "Overlap balanced",
        "method": "overlap_controlled_balanced",
        "layout_file": LAYOUT_DIR
        / "overlap_controlled_balanced"
        / "monitor_nodes_overlap_controlled_balanced_N25.json",
        "metrics_file": RAW_REPORTS / "last_run_metrics_ch5_probe_ocb_N25_s42.json",
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_formal_overlap_table() -> pd.DataFrame:
    metrics = pd.read_csv(FORMAL_MAIN)
    structure = pd.read_csv(FORMAL_STRUCTURE)
    metric_summary = (
        metrics.groupby(["method_short", "method", "monitor_budget_n"], as_index=False)
        .agg(
            seed_count=("seed", "nunique"),
            seeds=("seed", lambda x: ",".join(str(int(v)) for v in sorted(x))),
            window_mrr_mean=("window_mrr_from_report", "mean"),
            window_top1_mean=("window_top1_from_report", "mean"),
            window_top3_mean=("window_top3_from_report", "mean"),
            window_top5_mean=("window_top5_from_report", "mean"),
            event_mrr_mean=("event_mrr_mean_from_by_scenario", "mean"),
            event_top1_mean=("event_top1_mean_from_by_scenario", "mean"),
            event_top3_mean=("event_top3_mean_from_by_scenario", "mean"),
            event_top5_mean=("event_top5_mean_from_by_scenario", "mean"),
        )
    )
    out = metric_summary.merge(
        structure[
            [
                "method_short",
                "method",
                "monitor_budget_n",
                "overlap_count",
                "direct",
                "near",
                "far",
                "mean_hop",
                "max_hop",
            ]
        ],
        on=["method_short", "method", "monitor_budget_n"],
        how="left",
        validate="one_to_one",
    )
    out["non_candidate_monitor_count"] = out["monitor_budget_n"] - out["overlap_count"]
    out["evidence_group"] = "formal_clean_mainline"
    return out


def build_probe_overlap_table() -> pd.DataFrame:
    rows = []
    for spec in PROBE_SPECS:
        layout = read_json(spec["layout_file"])
        report = read_json(spec["metrics_file"])
        by_scenario = report.get("by_scenario", {})
        event_mrr = None
        event_top1 = None
        event_top3 = None
        event_top5 = None
        if by_scenario:
            values = list(by_scenario.values())
            event_mrr = sum(float(x.get("mrr", 0.0)) for x in values) / len(values)
            event_top1 = sum(float(x.get("top1", 0.0)) for x in values) / len(values)
            event_top3 = sum(float(x.get("top3", 0.0)) for x in values) / len(values)
            event_top5 = sum(float(x.get("top5", 0.0)) for x in values) / len(values)

        lm = layout["layout_metrics"]
        rows.append(
            {
                "method_short": spec["method_short"],
                "method": spec["method"],
                "monitor_budget_n": int(layout["n"]),
                "seed_count": 1,
                "seeds": "42",
                "window_mrr_mean": report.get("mrr"),
                "window_top1_mean": report.get("topk_recall_1"),
                "window_top3_mean": report.get("topk_recall_3"),
                "window_top5_mean": report.get("topk_recall_5"),
                "event_mrr_mean": event_mrr,
                "event_top1_mean": event_top1,
                "event_top3_mean": event_top3,
                "event_top5_mean": event_top5,
                "overlap_count": int(lm["overlap_count"]),
                "direct": int(lm["direct"]),
                "near": int(lm["near"]),
                "far": int(lm["far"]),
                "mean_hop": float(lm["mean_hop"]),
                "max_hop": float(lm["max_hop"]),
                "non_candidate_monitor_count": int(layout["n"]) - int(lm["overlap_count"]),
                "evidence_group": "overlap_controlled_probe_seed42",
                "layout_file": str(spec["layout_file"]),
                "metrics_file": str(spec["metrics_file"]),
            }
        )
    return pd.DataFrame(rows)


def write_readme(table: pd.DataFrame) -> None:
    text = """# CH5 candidate-overlap evidence

This table supports the Chapter-5 claim that monitor layout optimization is not
equivalent to maximizing candidate-node overlap.

Two evidence groups are included:

1. `formal_clean_mainline`: formal five-method comparison averaged over
   diagnosis evaluation seeds 7, 42, and 123.
2. `overlap_controlled_probe_seed42`: existing seed-42 probe layouts with the
   same overlap count as Degree / v2_2 clean, used only as supplementary
   mechanism evidence.

Important boundary:

- The probe rows are not part of the formal main ranking.
- The table does not claim that candidate-only layouts have been fully trained
  and evaluated. It demonstrates that higher overlap_count is not sufficient to
  explain the best mainline performance, and that equal overlap_count can still
  produce different diagnostic performance.
"""
    (OUT_DIR / "CH5-P1_candidate_overlap_evidence_README.md").write_text(text, encoding="utf-8")


def main() -> None:
    formal = build_formal_overlap_table()
    probe = build_probe_overlap_table()
    table = pd.concat([formal, probe], ignore_index=True, sort=False)
    table = table.sort_values(["evidence_group", "window_mrr_mean"], ascending=[True, False])

    output = OUT_DIR / "CH5-P1_candidate_overlap_vs_performance_evidence.csv"
    table.to_csv(output, index=False, encoding="utf-8-sig")
    write_readme(table)

    print(f"Wrote {output}")
    print(table[["method_short", "evidence_group", "overlap_count", "non_candidate_monitor_count", "window_mrr_mean", "window_top1_mean", "event_mrr_mean", "event_top1_mean"]].to_string(index=False))


if __name__ == "__main__":
    main()

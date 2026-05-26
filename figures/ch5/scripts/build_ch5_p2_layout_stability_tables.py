from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import pandas as pd


ROOT = Path(r"E:\11.16")
STABILITY_DIR = ROOT / "script2_new" / "chapter5_layout_optimization" / "outputs" / "layout_stability"
OUT_DIR = ROOT / "thesis_writing_repo" / "figures" / "ch5" / "source_data"

INSTANCES_CSV = STABILITY_DIR / "layout_instances.csv"
STABILITY_BUDGET = 25
STABILITY_SEEDS = set(range(1, 11))


def read_layout_nodes(path: str) -> set[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(x) for x in payload.get("monitor_nodes", [])}


def build_jaccard(instances: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (method_key, budget), group in instances.groupby(["method_key", "budget"]):
        records = group.sort_values("layout_seed").to_dict("records")
        node_sets = {int(row["layout_seed"]): read_layout_nodes(row["layout_file"]) for row in records}
        for left, right in combinations(records, 2):
            a_seed = int(left["layout_seed"])
            b_seed = int(right["layout_seed"])
            a = node_sets[a_seed]
            b = node_sets[b_seed]
            union = a | b
            inter = a & b
            rows.append(
                {
                    "method_key": method_key,
                    "method_short": left["method_short"],
                    "method": left["method"],
                    "budget": int(budget),
                    "layout_seed_a": a_seed,
                    "layout_seed_b": b_seed,
                    "intersection_count": len(inter),
                    "union_count": len(union),
                    "jaccard": len(inter) / len(union) if union else 0.0,
                }
            )
    return pd.DataFrame(rows)


def build_node_frequency(instances: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in instances.iterrows():
        nodes = read_layout_nodes(row["layout_file"])
        for node in sorted(nodes):
            rows.append(
                {
                    "method_key": row["method_key"],
                    "method_short": row["method_short"],
                    "method": row["method"],
                    "budget": int(row["budget"]),
                    "layout_seed": int(row["layout_seed"]),
                    "node_id": node,
                }
            )
    long_df = pd.DataFrame(rows)
    freq = (
        long_df.groupby(["method_key", "method_short", "method", "budget", "node_id"], as_index=False)
        .agg(selection_count=("layout_seed", "nunique"))
        .sort_values(["method_key", "budget", "selection_count", "node_id"], ascending=[True, True, False, True])
    )
    seed_counts = (
        instances.groupby(["method_key", "budget"], as_index=False)
        .agg(layout_seed_count=("layout_seed", "nunique"))
    )
    freq = freq.merge(seed_counts, on=["method_key", "budget"], how="left", validate="many_to_one")
    freq["selection_frequency"] = freq["selection_count"] / freq["layout_seed_count"]
    return freq


def build_structure_summary(instances: pd.DataFrame, jaccard: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [
        "direct",
        "near",
        "far",
        "mean_hop",
        "max_hop",
        "overlap_count",
        "monitor_dispersion_mean_hop",
        "monitor_redundancy_mean_jaccard",
        "global_mean_hop",
    ]
    summary = (
        instances.groupby(["method_key", "method_short", "method", "budget"], as_index=False)
        .agg(
            layout_seed_count=("layout_seed", "nunique"),
            **{f"{col}_mean": (col, "mean") for col in metric_cols},
            **{f"{col}_std": (col, "std") for col in metric_cols},
            **{f"{col}_min": (col, "min") for col in metric_cols},
            **{f"{col}_max": (col, "max") for col in metric_cols},
        )
        .sort_values(["method_key", "budget"])
    )
    if not jaccard.empty:
        jac_summary = (
            jaccard.groupby(["method_key", "method_short", "method", "budget"], as_index=False)
            .agg(
                jaccard_pair_count=("jaccard", "size"),
                jaccard_mean=("jaccard", "mean"),
                jaccard_std=("jaccard", "std"),
                jaccard_min=("jaccard", "min"),
                jaccard_max=("jaccard", "max"),
            )
        )
        summary = summary.merge(jac_summary, on=["method_key", "method_short", "method", "budget"], how="left")
    return summary


def write_readme(outputs: list[Path], instances: pd.DataFrame, jaccard: pd.DataFrame) -> None:
    text = f"""# CH5 P2 learning layout stability tables

This batch summarizes layout-generation stability only. It does not train or
evaluate diagnosis models.

Scope:

- methods: v0_2 clean, v2_2 clean
- budget for stability: N=25
- layout seeds: 1..10

Data scale:

- layout instances: {len(instances)}
- Jaccard pairs: {len(jaccard)}

Important boundary:

- `layout_seed` is not diagnosis seed.
- These tables support generation stability, not diagnostic performance.

Outputs:

{chr(10).join(f'- `{path.name}`' for path in outputs)}
"""
    path = OUT_DIR / "CH5-P2_learning_layout_stability_README.md"
    path.write_text(text, encoding="utf-8")
    outputs.append(path)


def main() -> None:
    if not INSTANCES_CSV.exists():
        raise FileNotFoundError(INSTANCES_CSV)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_instances = pd.read_csv(INSTANCES_CSV)
    instances = all_instances[
        all_instances["budget"].eq(STABILITY_BUDGET)
        & all_instances["layout_seed"].isin(STABILITY_SEEDS)
        & all_instances["method_key"].isin(["v0_2_clean_scenario", "v2_2_clean_generalization"])
    ].copy()
    if len(instances) != 20:
        raise AssertionError(f"Expected 20 P2 stability instances, got {len(instances)}")

    jaccard = build_jaccard(instances)
    if len(jaccard) != 90:
        raise AssertionError(f"Expected 90 Jaccard pairs, got {len(jaccard)}")
    node_frequency = build_node_frequency(instances)
    structure_summary = build_structure_summary(instances, jaccard)

    outputs = []
    for name, df in [
        ("CH5-P2_learning_layout_stability_instances.csv", instances),
        ("CH5-P2_learning_layout_jaccard_pairs.csv", jaccard),
        ("CH5-P2_learning_layout_node_frequency.csv", node_frequency),
        ("CH5-P2_learning_layout_structure_summary.csv", structure_summary),
    ]:
        path = OUT_DIR / name
        df.to_csv(path, index=False, encoding="utf-8-sig")
        outputs.append(path)

    write_readme(outputs, instances, jaccard)
    print("Wrote CH5 P2 stability tables:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()

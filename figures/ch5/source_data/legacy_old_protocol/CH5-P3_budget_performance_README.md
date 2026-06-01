# CH5 P3 budget performance tables

This batch summarizes budget-performance retraining results from
`CH5_CORE_BUDGET_PERFORMANCE_MANIFEST.csv`.

Status:

- available metrics rows: 11
- missing metrics rows: 64
- expected rows: 75

Important boundary:

- Missing rows mean the corresponding training command has not completed or
  its metrics JSON is not in the expected reports directory.
- Only scenario split is included. Node-holdout is not part of P3 main ranking.

Outputs:

- `CH5-P3_budget_performance_by_seed.csv`
- `CH5-P3_budget_performance_summary.csv`
- `CH5-P3_budget_structure_performance_join.csv`

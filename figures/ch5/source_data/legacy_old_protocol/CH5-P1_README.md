# CH5 P1 no-retrain source data

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

- P0 raw rows: 945
- methods: 5
- seeds: 3
- unique scenarios: 165
- Degree low-MRR q25 cutoff: 0.513889
- low-MRR hard scenarios: 42
- far and low-MRR hard scenarios: 21

## Outputs

- `CH5-P1_layout_specific_candidate_observability.csv`
- `CH5-P1_layout_specific_observability_summary.csv`
- `CH5-P1_layout_specific_raw_with_tiers.csv`
- `CH5-P1_layout_specific_direct_near_far_performance_by_seed.csv`
- `CH5-P1_layout_specific_direct_near_far_performance_summary.csv`
- `CH5-P1_defect_type_performance_by_seed.csv`
- `CH5-P1_defect_type_performance_summary.csv`
- `CH5-P1_intensity_pct_performance_by_seed.csv`
- `CH5-P1_intensity_pct_performance_summary.csv`
- `CH5-P1_intensity_performance_by_seed.csv`
- `CH5-P1_intensity_performance_summary.csv`
- `CH5-P1_duration_h_performance_by_seed.csv`
- `CH5-P1_duration_h_performance_summary.csv`
- `CH5-P1_duration_performance_by_seed.csv`
- `CH5-P1_duration_performance_summary.csv`
- `CH5-P1_start_hour_performance_by_seed.csv`
- `CH5-P1_start_hour_performance_summary.csv`
- `CH5-P1_hard_candidate_second_definitions.csv`
- `CH5-P1_hard_candidate_second_definition_performance_by_seed.csv`
- `CH5-P1_hard_candidate_second_definition_performance_summary.csv`

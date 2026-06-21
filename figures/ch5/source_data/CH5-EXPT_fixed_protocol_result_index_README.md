# CH5 fixed protocol result index

This index separates strict Chapter 4 fixed-protocol evidence from bridge, old-path, and mechanism evidence.

- `CH5-EXPT_fixed_protocol_result_index.csv`: N25 main-method evidence status.
- `CH5-EXPT_bridge_budget_existing_results.csv`: existing 48h layout-budget path results, mostly `normal_multibaseline_seedset10`.
- `CH5-EXPT_fixed_protocol_missing_main_runs.csv`: unresolved strict-protocol runs. The current file contains only the header, which records that the formal N25 main table is complete.

Do not treat old-path rows as formal fixed-protocol ranking results.

## Added mechanism validation experiment

- Experiment: coverage-rate controlled layout response.
- Layout generator: `E:\11.16\script2_new\chapter5_layout_optimization\scripts\build_coverage_rate_controlled_layouts.py`.
- Evaluation runner: `E:\11.16\script2_new\chapter5_layout_optimization\scripts\run_coverage_rate_controlled_eval.py`.
- Drawing script: `E:\11.16\thesis_writing_repo\figures\scripts\ch5\draw_07_ch5_coverage_rate_response.py`.
- Layout summary: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\coverage_rate_controlled\coverage_rate_controlled_layout_summary.csv`.
- Run manifest: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\coverage_rate_controlled\coverage_rate_controlled_run_manifest.csv`.
- Planned output directory: `E:\11.16\thesis_writing_repo\figures\ch5\generated_results\07_CH5_coverage_rate_response`.

Status:

- Layouts and run manifest have been generated for fixed N=25.
- Four structural coverage levels are included: low, mid, high, very_high.
- Each level contains 3 layout variants.
- Evaluation metrics are pending; do not use this as a formal result figure before running the manifest.

Purpose:

- This is a mechanism validation experiment, not a new layout-method ranking.
- It isolates defect-node structural coverage rate under the fixed diagnosis protocol.
- It tests whether localization performance is mainly explained by structural coverage, or whether diagnostic representation and response propagation are also needed to explain the Chapter-5 results.

## Added spatial layout visualization

- Figure script: `E:\11.16\thesis_writing_repo\figures\scripts\ch5\draw_08_ch5_layout_spatial_distribution.py`.
- Output directory: `E:\11.16\thesis_writing_repo\figures\ch5\generated_results\08_CH5_layout_spatial_distribution`.
- Source topology: `E:\11.16\script2_new\input_1\parsed_inp_data.json`.
- Source layouts: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts`.

Generated figures:

- `08_CH5_layout_spatial_distribution_budget_method_grid.png/.svg`: Degree, Betweenness, Cand-Obs, Two-stage v1, and Embedding-Guided under N=5/10/15/20/25.
- `08_CH5_layout_spatial_distribution_N25_method_overview.png/.svg`: N=25 six-method spatial overview, including Node-Feedback.
- `08_CH5_layout_spatial_distribution_budget_growth_path.png/.svg`: budget growth path showing the budget at which each selected monitor first appears.

Purpose:

- This figure series is intended for PPT and mechanism explanation.
- It shows where the monitoring nodes are actually placed on the sewer network.
- It should be used together with performance tables, structure metrics, and Jaccard analysis; it is not a standalone performance ranking figure.

## Added Embedding-Guided mechanism figure

- Figure script: `E:\11.16\thesis_writing_repo\figures\scripts\ch5\draw_09_ch5_embedding_guided_mechanism.py`.
- Output directory: `E:\11.16\thesis_writing_repo\figures\ch5\generated_results\09_CH5_embedding_guided_mechanism`.
- Source topology: `E:\11.16\script2_new\input_1\parsed_inp_data.json`.
- Source candidate nodes: `E:\11.16\script2_new\input_1\candidate_nodes_new.json`.
- Source E-G layout: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\embedding_guided_clean_fixed\monitor_nodes_embedding_guided_clean_N25.json`.

Generated figures:

- `09_CH5_embedding_guided_mechanism.png/.svg`: real network topology plus method-level mathematical mechanism of Embedding-Guided layout selection.
- `09_CH5_embedding_guided_mechanism_summary.csv`: node counts and E-G layout structural summary.

Purpose:

- This is a method-mechanism schematic, not a performance result chart.
- It explains how diagnostic node representations can define monitor-node value, with redundancy suppression and budget-constrained selection.
- Formula notation is intentionally schematic and should be aligned with the final written method description before being used as a formal equation in the thesis text.

## Formal monitoring-budget experiment pipeline

- Manifest builder: `E:\11.16\script2_new\chapter5_layout_optimization\scripts\build_ch5_budget_sweep_manifest.py`.
- Sequential runner: `E:\11.16\script2_new\chapter5_layout_optimization\scripts\run_ch5_budget_sweep.py`.
- Metrics collector: `E:\11.16\script2_new\chapter5_layout_optimization\scripts\collect_ch5_budget_sweep.py`.
- Output directory: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\budget_sweep_formal`.

Fixed protocol:

- Dataset: `ie420_plus_normal20_v1`.
- Split: `scenario`.
- Features: `raw_plus_residual`.
- Diagnosis model: `hydraulic_inverse_deepattn`.
- Localization weight: `lambda_loc=0.5`.

Current seed42 status:

- Methods with complete N=5/10/15/20/25 results: Degree, Betweenness, Two-stage v1, Embedding-Guided.
- Cand-Obs N=25 is complete.
- Cand-Obs N=5/10/15/20 remains pending.
- Node-Feedback is excluded from the budget sweep because complete layouts currently exist only for N=25.

The existing `CH5-budget_sweep_seed42.csv` is therefore a completed four-method
trend table, but not yet a complete five-method formal budget experiment.

---
name: thesis-figure-result-analyst
description: Use when interpreting, auditing, classifying, or writing thesis/PPT result analysis for existing generated figures under figures/ch3/generated_results, figures/ch4/generated_results, and figures/ch5/generated_results. Produces evidence-based conclusions, figure roles, slide-ready analysis, and backup/main-figure recommendations.
---

# Thesis Figure Result Analyst

Use this skill when the user asks what an existing figure means, whether a figure should be used, how to analyze it in PPT/thesis text, or how to classify generated figures.

Scope:

- `E:/11.16/thesis_writing_repo/figures/ch3/generated_results`
- `E:/11.16/thesis_writing_repo/figures/ch4/generated_results`
- `E:/11.16/thesis_writing_repo/figures/ch5/generated_results`

This skill analyzes **existing generated figures**. It does not create new figures. For drawing, use `thesis-figure-studio`. For turning analyses into full slide text, use `thesis-ppt-writing`.

## Required Workflow

For any figure-specific question:

1. Open or preview the figure. If SVG cannot be previewed, open the same-name PNG.
2. Read adjacent CSV files in the same output directory.
3. Identify the script/output family by directory name and numeric prefix.
4. Explain:
   - what the figure plots
   - what each axis/panel/color/value means
   - what result it supports
   - what it cannot prove
   - whether it is main figure, supporting figure, PPT visual, or backup/defense
5. Write slide-ready analysis when requested.

Never infer performance from a structural figure unless the figure or adjacent CSV actually includes performance metrics.

## Analysis Depth Standard

Do not stop at reading numbers.

A good analysis has:

1. Observation: visible pattern or numeric result.
2. Contrast: what differs across methods, scenarios, stages, or groups.
3. Interpretation: what simple explanation is supported or ruled out.
4. Thesis role: what claim this figure supports.
5. Boundary: what the figure cannot establish.

Weak analysis:

> E-G 与 Two-stage 的 Jaccard 约为 0.064，说明重合度低。

Strong analysis:

> E-G 与 Two-stage/Cand-Obs 的 Jaccard 很低，说明 E-G 没有复刻结构覆盖导向布局。结合 N=25 主结果，相近性能并非来自同一批监测节点，而是来自不同结构路径。该图不能单独解释性能高低，但能排除“E-G 只是复制 Two-stage”的简单解释。

## Output Template

Use this concise format for direct figure explanations:

```markdown
这张图画的是：...

读图方式：
- 横轴：...
- 纵轴：...
- 颜色/大小/数字：...

它能说明：
- ...

它不能说明：
- ...

建议定位：
- 正式主图 / 支撑图 / PPT直观图 / 备答图 / 建议降级

可上屏结论：
- ...
```

For PPT-ready analysis, add:

```markdown
图片画的是什么：...
图片反映的问题：...
图片结果分析：...
图片如何支撑结论：...
使用注意：...
```

## Chapter 3 Figure Map

Chapter 3 purpose: prove formal simulation data are credible, observable, and useful for downstream diagnosis.

Generated result directories:

- `01_CH3_ie420_parameter_matrix`: parameter matrix; currently not recommended as formal main figure because it exposes I/E sampling imbalance and start-time pattern.
- `02_CH3_normal_envelope_defect_residual`: strong main evidence; compares defect residual against normal20 envelope.
- `04_CH3_topology_residual_spatial_map`: strong spatial evidence; shows residual response on topology for selected scenarios.
- `05_CH3_candidate_monitor_topology_setting`: setting/support figure; useful when split into layers.
- `07_CH3_all_scenario_event_aligned_response`: exploratory; dense all-scenario raster can be hard to read.
- `08_CH3_strength_stratified_event_response`: useful evidence; stratified event-aligned response and all-scenario strength-response summary.
- `09_CH3_response_peak_timing`: useful evidence; peak response timing and dominant hop after defect onset.
- `10_CH3_topology_residual_spatial_animation`: PPT visual support; GIFs for spatial response evolution.

Chapter 3 interpretation language:

- `normal20 envelope` is the normal disturbance reference band.
- `reference` is residual alignment baseline.
- `IE420` is the formal defect scenario set.
- Stronger residual response during active interval supports data observability.
- If water-quality residual is weak, describe it as auxiliary multivariable information, not failed data.
- Do not claim every defect is visually obvious.

## Chapter 4 Figure Map

Chapter 4 purpose: show diagnosis model performance, process evidence, temporal-scale tradeoffs, and fixed-layout boundaries.

Generated result directories:

- `01_CH4_main_model_multiseed`: main model multi-seed performance; formal main result.
- `02_CH4_task_level_summary`: task-level summary; can support metric explanation.
- `03_CH4_formal_model_comparison`: older model comparison; use if clearer than newer hybrid plot.
- `04_CH4_window_length_tradeoff`: older window tradeoff; use carefully.
- `05_CH4_ie_type_analysis`: I/E type analysis; support/backup.
- `06_CH4_observability_generalization`: observability/generalization; support/backup.
- `07_CH4_main_result_fingerprint`: compact main-model fingerprint; formal/PPT candidate.
- `08_CH4_model_gain_forest`: model gain forest; formal detailed comparison.
- `09_CH4_window_pareto_tradeoff`: window Pareto; formal/backup depending on readability.
- `10_CH4_ie_observability_mechanism`: I/E and observability mechanism; support/backup, avoid overclaiming.
- `11_CH4_model_progression_hybrid`: preferred PPT model comparison if readable.
- `12_CH4_window_hybrid_dual_axis`: preferred PPT window tradeoff if revised cleanly.
- `13_CH4_single_scenario_diagnosis_profile`: process evidence; selected scenario diagnosis timeline.
- `14_CH4_spatial_diagnosis_evidence_chain`: spatial evidence chain; use cautiously because it can expose limitations.
- `15_CH4_fixed_layout_observability_bridge`: bridge to Chapter 5; true defect node to monitor hop vs rank.

Important Chapter 4 numeric anchors:

- Main model multi-seed: MRR about 0.825, Top-1 about 0.719, Top-3 about 0.919.
- Scene F1 about 0.997, `1 - Normal FPR` about 0.999.
- Event Top-1 about 0.768, Event Top-3 about 0.951.
- GRU/GRU-GCN have much lower MRR than `hydraulic_inverse_deepattn`; this supports structure design for spatial ranking.
- Window tradeoff: 2h has lower onset error and higher Active IoU; 3h has strong scene-node MRR; 6h has low Normal FPR but coarser time boundary.
- Fixed Degree-N25 layout: far 3+ hop group has lower Top-1/MRR but can retain high Top-3; this motivates layout optimization without reducing the result to "closer is always better".

Chapter 4 interpretation boundaries:

- Do not say every scene is perfectly diagnosed.
- Do not turn limitation cases into main result unless framed as diagnosis boundary.
- Do not present `draw_14` spatial offsets as failure without explaining observability and neighboring-response effects.

## Chapter 5 Figure Map

Chapter 5 purpose: show layout optimization changes diagnosis performance, and explain why similar MRR can arise from different structural paths.

Generated result directories:

- `01_CH5_EXPT_N25`: main N=25 multi-seed performance; primary main result.
- `02_CH5_budget_sweep_seed42`: budget trend; support/backup, seed42 only.
- `03_CH5_layout_structure`: key mechanism figure; coverage-performance coupling.
- `04_CH5_hard_candidate_analysis`: structural boundary/hard candidate figures; mostly backup.
- `05_CH5_defect_type_analysis`: I/E type adaptation; support/backup.
- `06_CH5_pairwise_jaccard`: key structure-independence support for E-G.
- `CH5_EXPT_N25`: old/duplicate family; check before using.

Preferred Chapter 5 story:

1. Degree baseline is lower; optimized layouts improve spatial localization.
2. Two-stage v1, Node-Feedback, and Embedding-Guided are close in MRR.
3. Small differences among strong methods should not be overclaimed.
4. Two-stage proves explicit near-defect coverage can be strong.
5. Cand-Obs shows near-defect coverage alone is not sufficient.
6. Embedding-Guided achieves similar performance with different selected nodes.
7. Jaccard confirms E-G does not simply copy Two-stage/Cand-Obs.

Important Chapter 5 numeric anchors:

- Degree MRR about 0.825.
- Betweenness MRR about 0.868.
- Cand-Obs MRR about 0.878.
- Two-stage v1 MRR about 0.905.
- Node-Feedback MRR about 0.896.
- Embedding-Guided MRR about 0.897.
- Two-stage v1: Direct=18, Near=31, Far=1.
- Cand-Obs: Direct=15, Near=34, Far=1.
- Embedding-Guided: Direct=10, Near=21, Far=19.
- E-G vs Degree Jaccard about 0.042.
- E-G vs Cand-Obs and Two-stage v1 Jaccard about 0.064.

Preferred Chapter 5 terminology:

- `缺陷节点结构覆盖`
- `显式近邻覆盖`
- `显式缺陷节点覆盖约束`
- `诊断表征驱动`
- `结构路径差异`

Avoid:

- `候选覆盖偏好`
- `机制分组`
- "全面最优"
- "覆盖导向缺乏全局视野" unless backed by a specific figure

### How To Explain Key Chapter 5 Figures

`01_CH5_EXPT_N25`:

- Shows main performance under N=25.
- Use to claim layout optimization improves localization over Degree.
- Do not use to claim E-G is absolutely best.

`03_CH5_layout_structure_coverage_performance_coupling.svg`:

- Shows Direct/Near/Far structural coverage and MRR.
- Key conclusion: near-defect coverage is effective but not sufficient.
- Two-stage is strong; Cand-Obs has strong coverage but lower MRR; E-G has weaker coverage yet similar MRR.

`04_CH5_hard_candidate_distance_vs_mrr_dual_axis`:

- Shows candidate-node nearest-monitor hop distribution plus method-level MRR.
- Backup figure due to dual-axis explanation cost.
- Use to show distance coverage is helpful but not a full causal explanation.

`04_CH5_hard_candidate_top_gap_heatmap`:

- Structural heatmap, not performance heatmap.
- Rows are candidate defect nodes with largest cross-method hop gaps.
- Columns are layout methods.
- Cell values are hop distances from that candidate defect node to the nearest monitor under that method.
- Use to show different layouts protect/cover different candidate nodes.
- Do not claim nodes with high hop are always low-performance unless performance data are linked.

`05_CH5_defect_type_analysis`:

- Shows layout performance under I/E types.
- Use to argue layout effects depend partly on defect response type.
- Do not describe as I/E classification.

`06_CH5_pairwise_jaccard`:

- Shows selected-node overlap across methods.
- Key use: E-G does not copy Degree, Cand-Obs, or Two-stage.
- Pair with N=25 performance to argue similar MRR can arise from different selected-node sets.

`02_CH5_budget_sweep_seed42`:

- Shows budget trend under seed42.
- Use as support for budget sensitivity.
- Always state it is seed42 trend, not multi-seed stable law.

## Figure Role Classification

Classify each figure as one of:

- Formal main figure: should appear in thesis/PPT core.
- Support figure: useful after main figure to explain mechanism or boundary.
- PPT visual figure: easy for audience, may be less formal.
- Backup/defense figure: useful if asked, not main story.
- Demote/delete: unclear, duplicate, exposes irrelevant weakness, or uses old protocol.

Main figures should be few and aligned with the story. Backup figures can be numerous but must be labeled.

## Common Misread Prevention

If a figure is structural:

- Do not describe it as performance.
- Explain what distance, hop, direct/near/far, or Jaccard means.

If a figure is performance:

- Do not invent mechanism unless another figure supports it.
- Separate MRR, Top-1, Top-3, Event Top-K, Normal FPR.

If a figure has saturated metrics:

- Downplay Top-5 or Scene F1 unless the saturation itself is the point.

If a figure has tiny differences:

- Do not overstate ranking.
- Use it to motivate structure, stability, or boundary analysis.

## Validation Checklist

Before answering:

1. The figure was actually opened or same-name PNG was viewed.
2. Adjacent CSV was checked when interpretation depends on values.
3. The answer distinguishes structure from performance.
4. The analysis includes what the figure can and cannot prove.
5. The recommendation states main/support/PPT/backup/demote.
6. The wording avoids meta-instructions unless explicitly giving editing advice.

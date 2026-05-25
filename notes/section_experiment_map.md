# 小节级实验映射表

本文件用于把“章节/小节 -> 具体实验 -> 结果表 -> 图件 -> 过程记录 -> 写作边界”固定下来。

使用方式：

1. 先读 `notes/chapter_reading_routes.md` 确认本章主线材料。
2. 再来本文件定位当前小节的具体实验。
3. 只读取当前小节需要的结果表、图件和过程记录，不要把相邻小节的实验混在一起。
4. 小节计划和正文都应引用本文件中的条目。

---

## 第4章 面向缺陷定位的时空图诊断模型研究

### 第4.1节 连续场景下的缺陷诊断任务定义

本节核心问题：

第4章如何把 IE420 连续缺陷场景组织成“窗口级证据、场景级活跃期定位、场景级空间定位、综合诊断”的任务链？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\monitor_nodes_degree_N25.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\dataset_manifest.json
```

主要使用：

- 正式协议和任务边界。
- IE420 正式缺陷矩阵。
- degree N25 固定监测布局。
- `V=128`、`S=25`、`C=50`、`D` 四类集合。
- time-gated 场景、`sequence_length=36`、`window_stride=6`。

不要混入：

- 主实验数值结果。
- 模型对比结果。
- 窗口长度结果。
- 第5章布局优化结果。

### 第4.2节 稀疏观测图输入与时空诊断模型

本节核心问题：

第4章主模型如何接收全图拓扑与稀疏观测输入，三个输出头又如何转化为窗口级和场景级诊断证据？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\models\anomaly_detection_model.py
E:\11.16\script2_new\scripts\train_privileged_teacher_student.py
E:\11.16\script2_new\scripts\README.md
```

主要使用：

- full-graph sparse-observation 输入协议。
- `logits_has_defect` -> `p_active(t)`。
- `logits_node` -> `node_scores(t)`。
- `logits_defect_type` 存在但不进入正式类型分类指标。

不要混入：

- 具体性能数字。
- I/E 自动分类结论。
- 第5章布局优化方法。

### 第4.3节 训练协议与评价指标

本节核心问题：

第4章每个任务层级分别用什么标签、什么输出和什么指标评价？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\utils\evaluation.py
E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py
E:\11.16\script2_new\scripts\summarize_time_window_length_eval.py
```

主要使用：

- `scenario split` 和 `node_holdout` 的定位。
- Active Accuracy、Active Recall。
- MRR、Top-1、Top-3、Top-5。
- Event Top-K。
- onset error、±1/±2/±3 窗口命中、interval IoU。
- predicted-active scene Top-K 与 true-active Event Top-K 的区别。

不要混入：

- 主实验结果表。
- 模型优劣结论。
- 第5章结果。

### 第4.4节 缺陷诊断主实验结果

本节核心问题：

固定 degree N25 布局下，主模型窗口级证据、场景级事件定位、模型对比、窗口长度和 I/E 分组结果如何？

必须读取：

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\CH4_RESULT_AUDIT_FOR_WRITING.md
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_long.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_ie_type_group_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv
```

建议图件：

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_main_multiseed.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_model_comparison_multiseed.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_ie_type_group.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_tradeoff.png
```

允许写：

- 主模型 seed 7/42/123 多种子结果。
- 窗口级 MRR、Top-K、Active Recall。
- 场景级 Event Top-K。
- `hydraulic_inverse_deepattn`
- `lstm_graphsage_edge`
- `hydraulic_inverse`
- `gru_gcn`
- seed 7/42/123 多种子均值和标准差。
- 2h/3h/4h/6h 窗口长度对时间段定位和空间定位的影响。
- I/E 分组定位结果。

不要混入：

- node_holdout。
- 第5章布局优化结果。
- 旧 time_pos/trend/always_on 探索作为正式主图。

### 第4.5节 泛化边界、可观测性与综合分析

本节核心问题：

node_holdout、direct/near/far 可观测性和 predicted-active 综合诊断分别揭示了哪些模型边界？

必须读取：

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_nodehold_observability_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_candidate_observability_counts.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv
```

建议图件：

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_split_vs_nodehold.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_observability_analysis.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_timeline_case.png
```

允许写：

- node_holdout 的压力测试结果。
- 泛化边界。
- direct/near/far 可观测性影响。
- predicted-active scene Top-K 是更严格综合诊断审查。

不要写成：

- 已解决未见节点泛化。
- 正式主排名。
- predicted-active scene Top-K 等同于纯空间定位能力。

---

## 第5章 诊断反馈驱动的监测节点布局优化

### 第5.1节 监测节点布局优化问题定义

本节核心问题：

为什么第5章要把研究变量收束为监测节点集合 `S`，并讨论不同布点方案对空间定位能力的影响？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
```

主要使用：

- 固定第3章母数据。
- 固定第4章诊断任务、模型结构、窗口设置和评价协议。
- 只改变监测节点集合 `S` 与 observed mask。
- 全图节点 `V=128`、候选节点 `C=50`、监测预算默认 `N=25`。

不要混入：

- 具体布局方法优劣。
- `node_holdout` 主排名。
- 第4章场景级活跃期定位指标作为第5章主指标。

### 第5.2节 固定诊断协议下的布局评价闭环

本节核心问题：

如何保证不同布局之间的比较只反映监测节点集合变化，而不是数据、模型或评价协议变化？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\README.md
```

允许写：

- 统一数据来源、统一候选空间、统一训练与评价协议。
- 第5章不是共用同一个 checkpoint，而是在相同诊断协议下比较不同 observed mask。
- 主排名指标为 MRR、Top-1、Top-3、Top-5 和 event-level 空间定位 Top-K。
- 活跃期定位指标可作为第4章时间证据背景，不进入第5章布局主排名。

不要混入：

- “固定诊断模型权重”的说法。
- 把 onset error、interval IoU 写成布局优化主指标。

### 第5.3节 人工规则与任务驱动布局基线

本节核心问题：

哪些非学习型布局可以作为第5章的干净基线，它们分别代表什么人工规则或任务驱动假设？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\degree\monitor_nodes_degree_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\candidate_observability\monitor_nodes_candidate_observability_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\two_stage_balanced_layout_v1\monitor_nodes_two_stage_balanced_layout_v1_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

建议组织：

- `Degree`：拓扑中心性规则基线。
- `Cand-Obs`：候选可观测性任务驱动基线。
- `Two-stage v1`：候选覆盖与结构平衡结合的两阶段基线。

不要混入：

- `v0_2 clean` 和 `v2_2 clean` 的学习机制。
- 旧探索版本。
- 大段性能结果，结果应留到第5.5节。

### 第5.4节 诊断反馈驱动的学习型布局方法

本节核心问题：

第5章的学习型创新如何从“人工规则选点”推进到“诊断结果反馈指导布点”？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\structural_innovation\learnable_layout_network_v0_2_clean_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\structural_innovation\learnable_layout_network_v2_2_clean_summary.csv
```

允许写：

- `v0_2 clean`：节点级诊断反馈学习，回答“哪些节点值得被选”。
- `v2_2 clean`：布局级代理驱动搜索，回答“哪些节点组合整体更优”。
- 二者共同构成 clean 双层学习型主线。
- 学习信号来自第4章诊断结果和第5章统一评价闭环。

可作为边界备注：

- `v0_2 generalization` 只作为性能参考或内部记录，不作为中期正式主线。

不要写入正式主线：

- 旧 `v2_2`。
- `v1_1/v1_2/v1_3` 图上下文探索。
- 非 clean 版本或口径不干净的调参摸索。

### 第5.5节 不同布局方案的空间定位结果

本节核心问题：

在相同诊断协议下，不同布局方案对候选节点空间定位指标的影响如何？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary_with_event_topk.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\ch5_thesis_main_results_by_seed.csv
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

过程记录：

```text
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
```

建议图件：

```text
E:\11.16\script2_new\chapter5_layout_optimization\figures\ch5_fig_5_1_main_scenario_performance_mean_std.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\ch5_fig_5_2_layout_structure_metrics.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_main_spatial_performance_event_topk.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_learning_level_comparison.png
```

允许写：

- `Degree / Cand-Obs / Two-stage v1 / v0_2 clean / v2_2 clean` 的 MRR、Top-1、Top-3、Top-5、event-level Top-K。
- 均值和标准差，优先呈现多 seed 结果。
- `v2_2 clean` 可作为布局级学习搜索的主展示方法，`v0_2 clean` 用于说明节点级反馈学习的稳定性和机制差异。

已完成补强：

- 已由 `ch5_thesis_main_results_by_seed.csv` 补齐 event Top-3、event Top-5 成品表，不需要重训。

不要混入：

- node_holdout 结果作为主排名。
- 第4章时间活跃期定位指标。
- 旧探索版本的横向排名。

### 第5.6节 预算、难点候选与泛化边界分析

本节核心问题：

学习型布局在哪些条件下有效，哪些候选节点或泛化设置构成边界？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_6_budget_observability_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_7_layout_jaccard_similarity.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_8_surrogate_prediction_quality.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_9_hard_candidate_definition.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_4_node_holdout_boundary_seed42.csv
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
```

建议图件：

```text
E:\11.16\script2_new\chapter5_layout_optimization\figures\ch5_fig_5_3_scenario_node_holdout_gap.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_budget_observability_curve.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_direct_near_far_stack.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_layout_jaccard_heatmap.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_surrogate_prediction_scatter.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_node_holdout_boundary.png
```

已完成可写：

- `node_holdout` 作为边界测试，只说明未见节点压力与外推限制。
- 预算结构趋势、direct / near / far 结构、Jaccard 相似度、surrogate 可信度和 hard candidates 定义清单已经完成。

待补证据空位：

- 多预算空间定位性能训练。
- direct / near / far 分组性能。
- hard candidates 性能分层分析。
- 关键节点替换或 leave-one-out 贡献实验。

不要写成：

- 第5章已经证明严格外部泛化。
- `node_holdout` 已证明严格外部泛化。
- 图上下文探索是正式主方法。

### 第5.7节 本章小结

本节核心问题：

第5章可以稳定支持哪些结论，哪些只能写成后续补实验或方法边界？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
E:\11.16\thesis_writing_repo\notes\evidence_map.md
```

允许写：

- 监测节点布局会显著影响空间定位表现。
- 从人工规则选点走向诊断反馈布点，是第5章的核心方法主线。
- `v0_2 clean` 与 `v2_2 clean` 分别提供节点级和布局级学习视角。
- 预算、难点候选、相似度和代理可信度仍需作为后续补实验完善。

不要新增：

- 本章正文没有展开证明的优势。
- 对第4章主结果的反向改写。

# 小节级实验映射表

本文件用于把“章节/小节 -> 具体实验 -> 结果表 -> 图件 -> 过程记录 -> 写作边界”固定下来。

使用方式：

1. 先读 `notes/chapter_reading_routes.md` 确认本章主线材料。
2. 再来本文件定位当前小节的具体实验。
3. 只读取当前小节需要的结果表、图件和过程记录，不要把相邻小节的实验混在一起。
4. 小节计划和正文都应引用本文件中的条目。

---

## 第4章 固定监测布局下的诊断模型

### 第4.1节 实验任务与协议

本节核心问题：

在固定 degree N25 监测布局下，第4章的正式任务、数据口径、输入输出边界和评价协议是什么？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter4_diagnosis_model\docs\CH4_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260414.md
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42
```

主要使用：

- 正式协议和任务边界。
- IE420 正式缺陷矩阵。
- degree N25 固定监测布局。
- full-graph sparse-observation 输入方式。

不要混入：

- 主实验数值结果。
- 模型对比结果。
- 时间维度消融结果。
- 第5章布局优化结果。

### 第4.2节 模型输入、输出与结构

本节核心问题：

第4章主模型在固定布局下如何接收全网拓扑与稀疏观测输入，并对 50 个候选缺陷节点进行排序定位？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter4_diagnosis_model\docs\CH4_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260414.md
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
```

按需补读：

```text
E:\11.16\script2_new\group_meeting_figures
E:\11.16\script2_new\outputs\reports\figures
E:\11.16\process_diagnosis_revision_20260321\109_chapter1_complete_closure_20260403.md
```

主要使用：

- 模型任务定义。
- 输入输出形式。
- full-graph sparse-observation 的表述口径。

不要混入：

- 具体性能数字。
- 布局优化方法。

### 第4.3节 主实验结果

本节核心问题：

固定 degree N25 布局下，正式 IE420 协议的 scenario split 主实验结果如何？

必须读取：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_fullgraph_degree_ie420_multiseed.csv
E:\11.16\script2_new\outputs\reports\chapter1_task_level_results_summary.csv
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
```

过程记录：

```text
E:\11.16\process_diagnosis_revision_20260321\109_chapter1_complete_closure_20260403.md
E:\11.16\process_diagnosis_revision_20260321\111_chapter4_formal_experiment_closure_20260414.md
```

建议图件：

```text
E:\11.16\script2_new\outputs\reports\figures\chapter1_restart_split_compare.png
E:\11.16\script2_new\outputs\reports\figures\chapter1_restart_loss_curves_seed42.png
```

允许写：

- scenario split 主结果。
- MRR、Top-1、Top-3、Top-5。
- active period recall、event-level Top-K。
- 主结果意义与边界。

不要混入：

- 模型对比实验。
- 时间维度消融。
- node_holdout。
- 第5章布局优化结果。

### 第4.4节 模型对比实验

本节核心问题：

在同一正式协议下，不同诊断模型的性能差异如何？

必须读取：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_model_comparison_seed42.csv
```

过程记录：

```text
E:\11.16\process_diagnosis_revision_20260321\102_chapter1_restart_model_comparison_seed42_20260403.md
E:\11.16\process_diagnosis_revision_20260321\109_chapter1_complete_closure_20260403.md
```

建议图件：

```text
E:\11.16\script2_new\outputs\reports\figures\chapter1_restart_model_comparison_seed42.png
```

允许写：

- `hydraulic_inverse_deepattn`
- `lstm_graphsage_edge`
- `hydraulic_inverse`
- `gru_gcn`

不要混入：

- 主实验多 seed 汇总结果。
- 时间维度消融。
- node_holdout。
- 第5章布局优化结果。

### 第4.5节 时间维度与全过程诊断分析

本节核心问题：

time-gated 机制和时间维度相关设置对全过程诊断与定位表现有何影响？

必须读取：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_time_dimension_seed42.csv
```

过程记录：

```text
E:\11.16\process_diagnosis_revision_20260321\106_chapter1_time_dimension_formal420_seed42_20260403.md
E:\11.16\process_diagnosis_revision_20260321\111_chapter4_formal_experiment_closure_20260414.md
```

建议图件：

```text
E:\11.16\script2_new\outputs\reports\figures\chapter1_restart_time_dimension_seed42.png
```

允许写：

- `time_gated baseline`
- `no time position`
- `trend feature`
- `always_on`
- 时间维度相关的正反结果分析。

不要混入：

- 布局优化。
- 主实验多 seed 排名。
- 模型对比。

### 第4.6节 未见节点压力测试与边界分析

本节核心问题：

在未见缺陷节点条件下，模型的定位能力边界和主要误差模式是什么？

必须读取：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_nodehold_multiseed.csv
```

过程记录：

```text
E:\11.16\process_diagnosis_revision_20260321\104_chapter1_restart_nodehold_multiseed_20260403.md
E:\11.16\process_diagnosis_revision_20260321\107_node_generalization_confusion_analysis_20260403.md
```

建议图件：

```text
E:\11.16\script2_new\outputs\reports\figures\chapter1_restart_nodehold_analysis.png
```

允许写：

- node_holdout 的压力测试结果。
- 泛化边界。
- 典型错误模式和原因。

不要写成：

- 已解决未见节点泛化。
- 正式主排名。

---

## 第5章 监测点布局优化

### 第5.1节 引言

本节核心问题：

为什么第5章要在固定第3章母数据和第4章诊断评价器的前提下，单独研究监测点布局？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
```

主要使用：

- 第5章任务定位。
- 主评价口径。
- 与第4章的关系边界。

不要混入：

- 具体结果表中的数值细节。

### 第5.2节 监测点布局优化问题与评价闭环

本节核心问题：

第5章的布局变量、统一评价协议和正式比较闭环是什么？

必须读取：

```text
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

按需读取：

```text
E:\11.16\script2_new\CH5_INNOVATION_TO_EXPERIMENT_MAP.md
E:\11.16\script2_new\PROPOSAL_VS_CURRENT_AND_CH5_INNOVATION_20260403.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
```

允许写：

- 固定 evaluator、固定任务、固定母数据。
- 只改变监测节点集合与 observed mask。
- `scenario` 为主、`node_holdout` 为边界分析。

不要混入：

- 具体方法优劣结论。
- 第4章模型实验的重新定义。

### 第5.3节 监测点布局优化方法

本节核心问题：

第5章比较了哪些布局方法，它们分别代表什么思路？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
E:\11.16\script2_new\CH5_INNOVATION_TO_EXPERIMENT_MAP.md
```

按需读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_3_method_supplement_seed42.csv
```

建议组织：

- 拓扑基线：`degree`
- 任务驱动基线：`candidate_observability`
- 两阶段方法：`two_stage_balanced_layout_v1`
- 学习型布局：`learnable_layout_network_v0_2_generalization`
- 代理驱动 clean 版本：`learnable_layout_network_v2_2_clean_generalization`

不要混入：

- 旧 `v2_2` exploratory version 作为正式主线。
- 结果数值大段展开。

### 第5.4节 监测布局定位效果评价

本节核心问题：

不同布局方法在主评价协议下的定位性能差异如何？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_3_method_supplement_seed42.csv
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
```

允许写：

- `degree` 与任务驱动布局的差距。
- `candidate_observability` 的提升。
- `two_stage_balanced_layout_v1` 的可解释性与表现。
- `v0_2` 的稳定性。
- `v2_2_clean` 的探索价值与方差边界。

不要混入：

- node_holdout 结果作为主排名。
- 第4章固定布局主结果口径。

### 第5.5节 布局机制与方法边界讨论

本节核心问题：

布局效果背后的机制是什么？主要边界在哪里？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_4_node_holdout_boundary_seed42.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_5_graph_context_mechanism_seed42.csv
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
```

建议图件：

```text
E:\11.16\script2_new\chapter5_layout_optimization\figures\ch5_fig_5_3_scenario_node_holdout_gap.png
```

允许写：

- `scenario` 与 `node_holdout` 的差异。
- 图上下文增强与约束强化的反例分析。
- evaluator-aware 布局方法的反馈依赖边界。

不要写成：

- 第5章已经证明严格外部泛化。
- 旧探索版本就是正式主方法。

### 第5.6节 本章小结

本节核心问题：

第5章可以稳定支持哪些结论，哪些只能写成边界和展望？

必须读取：

```text
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
E:\11.16\thesis_writing_repo\notes\evidence_map.md
```

允许写：

- 布局变量显著影响定位性能。
- 候选可观测性机制成立。
- 两阶段方法具有可解释性。
- 学习型与代理驱动方法有潜力，但需限定反馈来源与泛化边界。

不要新增：

- 本章正文没有展开证明的优势。
- 对第4章主结果的反向改写。

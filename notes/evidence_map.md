# 论文证据地图

本文件用于记录“论文结论 -> 数据来源 -> 可写边界 -> 禁止越界内容”的对应关系。每写一个小节，先补充或检查对应证据。

## 第4章第4.1节 实验任务与协议

### 本节要支撑的表述

在固定 degree N25 监测布局下，本文保留全网 128 节点拓扑结构，仅对 25 个监测节点提供动态观测输入，并在 50 个候选缺陷节点范围内进行排序定位。

### 可写事实

- 正式缺陷类型：I/E。
- 正式缺陷矩阵：IE420。
- 图输入范围：全网 128 节点拓扑。
- 第4章固定监测布局：degree N25。
- 定位范围：50 个候选缺陷节点。
- 第4章主任务：固定监测布局下的全过程缺陷检测与候选节点定位。
- 第5章任务：在固定诊断任务与评价器下优化监测点布局。

### 数据与文件来源

```text
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\04_DO_NOT_USE_AND_TERMINOLOGY.md
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42
```

### 禁止越界

- 不能写成在 128 个节点中自由定位缺陷。
- 不能把 P 类水质污染源定位写成本论文已完成任务。
- 不能把 node_holdout 写成已经解决未见节点泛化。
- 不能使用旧 `v2e_dense_ie` 或旧 `MRR>=0.91` 结果作为正式主证据。

## 第4章第4.3节 主实验结果

### 待补充

完成 4.3 写作前，读取以下文件并补齐主结果证据：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_fullgraph_degree_ie420_multiseed.csv
E:\11.16\script2_new\outputs\reports\chapter1_task_level_results_summary.csv
```

## 第5章 监测点布局优化

### 待补充

完成第5章写作前，读取以下闭环文件并补齐正式表格索引：

```text
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

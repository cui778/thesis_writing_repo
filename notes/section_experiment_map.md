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

固定 degree N25 布局下，主模型窗口级证据、场景级事件定位、特征组合分析、窗口长度和 I/E 分组结果如何？

正式协议：ie420+normal20 / raw_plus_residual / lambda_loc=0.5 / hydraulic_inverse_deepattn / degree_N25 / scenario split / seeds=7/42/123

必须读取：

```text
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F06_main_model_multiseed.csv          — 正式协议多 seed（Degree_N25_formal）
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F07_task_level_results_summary.csv    — 正式主结果表（formal_mainline 行）
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F08_feature_set_comparison.csv        — 特征组合对照（历史 seedset10，标注 HISTORICAL）
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F09b_time_window_length_eval_summary.csv — 窗口长度（旧协议，趋势参考）
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F10a_ie_type_group_summary.csv        — I/E 分组（旧协议，趋势参考）
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_long.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_ie_type_group_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv
```

建议图件：

```text
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F06_main_model_multiseed.csv    — 正式协议三种子，待重绘
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F07_task_level_results_summary.csv — 正式主结果，待重绘
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F08_feature_set_comparison.csv   — 历史调参依据，标注 HISTORICAL
E:\11.16\thesis_writing_repo\figures\ch4\data_plots\CH4-F09b_time_window_length_tradeoff.png — 旧协议，趋势参考
E:\11.16\thesis_writing_repo\figures\ch4\data_plots\CH4-F10a_ie_type_group.png            — 旧协议，趋势参考
```

数据来源说明：

- F06、F07：来自正式 ie420+normal20 协议，可作为正式证据。
- F08（特征组合）、F09b（窗口长度）、F10a（I/E 分组）：来自旧 seedset10 数据集或旧协议，标注为历史/趋势参考，不作为正式协议性能表。

允许写：

- 正式协议 seed 7/42/123 多种子结果（来自 F06）。
- seed42 主结果（来自 F07 formal_mainline 行）。
- 窗口级 MRR、Top-K、Active F1、Normal Window FPR、Scene F1。
- 场景级 Event Top-K。
- 特征组合对照（标注为历史调参依据）。
- 2h/3h/4h/6h 窗口长度对时间段定位和空间定位的影响（标注为旧协议趋势参考）。
- I/E 分组定位结果（标注为旧协议趋势参考）。

不要混入：

- node_holdout。
- 第5章布局优化结果。
- 旧 time_pos/trend/always_on 探索作为正式主图。
- 将旧 seedset10 数据写成正式 normal20 协议性能。

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

## 第5章 融合诊断反馈与节点表征的排水管网监测布局优化

> **方法命名：** Degree / Betweenness / Cand-Obs / Two-stage v1 / Node-Feedback / Embedding-Guided
> **协议：** IE420+normal20 / raw_plus_residual / lambda_loc=0.5 / hydraulic_inverse_deepattn / scenario split
> **全部实验已完成（2026-06-01）。**

### 第5.1节 监测布局优化问题与固定实验协议

本节核心问题：

为什么要把监测节点集合 `S` 从固定输入条件转化为待优化变量？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
```

主要使用：

- 固定第3章母数据（IE420 + normal20）。
- 固定第4章诊断任务、模型结构、窗口设置和评价协议。
- 只改变监测节点集合 `S` 与 observed mask。
- 全图节点 `V=128`、候选节点 `C=50`、监测预算默认 `N=25`。

不要混入：

- 具体布局方法优劣。
- 第4章场景级活跃期定位指标作为第5章主指标。

### 第5.2节 固定诊断协议下的布局评价闭环

本节核心问题：

如何保证不同布局之间的比较只反映监测节点集合变化？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

允许写：

- 统一数据来源、统一候选空间、统一训练与评价协议。
- 第5章不是共用同一个 checkpoint，而是在相同诊断协议下比较不同 observed mask。
- 主排名指标为 MRR、Top-1、Top-3、Top-5 和 event-level 空间定位 Top-K。
- 多 seed 评价口径：诊断 seed 7/42/123，mean ± std（ddof=1）。
- 实验分组：纯拓扑基线 → 覆盖导向基线 → 诊断表征驱动方法。

不要混入：

- “固定诊断模型权重”的说法。
- 把 onset error、interval IoU 写成布局优化主指标。

### 第5.3节 对比方法：拓扑规则、覆盖导向与诊断表征

本节核心问题：

六种布局方法按”诊断信息介入程度”排列，分别代表什么信息来源？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_layout_structure.csv
```

三个信息层次：

- **层次一（规则驱动）：** Degree、Betweenness — 无诊断信息，纯拓扑规则。
- **层次二（覆盖导向）：** Cand-Obs、Two-stage v1 — 任务设计经验（候选位置 + 仿真响应）。
- **层次三（诊断表征驱动）：** Node-Feedback、Embedding-Guided — 诊断模型的外部评价或内部表征。

关键定位约束：

- **Two-stage v1** 定位为”离线仿真信息充分条件下的任务导向启发式参考”，不作为本文创新。
- **Node-Feedback** 定位为”探索性反馈学习方法”，训练数据仅来自 3 种布局 × 3 种子 = 9 组。
- **Embedding-Guided** 定位为正文主方法，利用诊断编码器节点嵌入的 max-min diversity 选点。

不要混入：

- Surrogate-Search（已从主表移除）。
- 旧版本名（v0_2 clean、v2_2 clean、v0_scenario、v0_generalization 等旧命名）。用正式表中 `Node-Feedback (val)`、`Embedding-Guided-new`。

### 第5.4节 不同布局方法的定位性能对比

本节核心问题：

在 N=25、3 种子条件下，6 种布局方法的空间定位性能如何？

必须读取：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_table.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_layout_structure.csv
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

允许写：

- 6 方法的 MRR、Top-1、Top-3、Top-5、Event Top-1、Event Top-3、Scene F1（表 5-1）。
- 结构特征对比：direct / near / far / mean_hop / overlap_count（表 5-2）。
- 所有 mean±std 使用 ddof=1。

叙事主线（不是排行榜）：

1. 纯拓扑布局仍有优化空间（Degree MRR=0.825±0.037）。
2. 覆盖邻近并不是唯一有效策略（Cand-Obs 0.878±0.034，Two-stage 0.905±0.027）。
3. Embedding-Guided 是正文主方法（MRR 0.897±0.017，三条独立证据）。
4. 结论落点：诊断表征能够提供不同于拓扑和覆盖规则的布局依据。
5. 所有数值来自 CH5-EXPT_fixed_protocol_N25_main_table.csv，方法名为表格中正式命名。

不要混入：

- node_holdout 结果作为主排名。
- 第4章时间活跃期定位指标。
- 把 Two-stage v1 写成”普通规则基线”或本文创新。

### 第5.5节 预算约束下的性能变化

本节核心问题：

不同预算下各方法的性能趋势如何？是否存在交叉点？

必须读取：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-budget_sweep_seed42.csv
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

允许写：

- 4 方法 × 5 预算（N5/10/15/20/25）的 MRR 趋势（表 5-3）。
- 交叉点分析：N=5 时 EG 最高（0.607），N≥10 时 Two-stage 最高。
- 必须标注”仅 seed 42，趋势参考，不用于稳定性结论”。

不要写成：

- 多 seed 稳定性结论（预算曲线仅 seed 42）。

### 第5.6节 机制分析

本节核心问题：

困难观测区域、I/E 缺陷类型适应性、布局相似度分别说明什么？

必须读取：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_hard_candidate_analysis.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_by_defect_type_analysis.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_pairwise_jaccard.csv
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

三个子分析：

- **5.6.1 困难候选：** 0 个候选在所有布局下均 far，7 个候选在所有布局下均 near/direct。措辞用”在当前六类布局下，没有候选节点始终处于远距离观测状态”。
- **5.6.2 I/E 类型：** EG 的 I-E gap 最小（0.009），Degree 最大（0.066）。
- **5.6.3 Jaccard：** EG 与所有其他方法的 Jaccard ≤ 0.136，与 Degree 仅 0.042。NF 与 Degree 高度重叠（0.563）。

不要写成：

- “没有候选节点天生不可观测”（过度泛化）。
- EG “完全独立于候选机制”（应写”不显式依赖候选节点覆盖目标”）。

### 第5.7节 本章小结与局限性

本节核心问题：

第5章可以稳定支持哪些结论？局限性是什么？

必须读取：

```text
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
E:\11.16\thesis_writing_repo\notes\evidence_map.md
```

允许写四个主结论：

1. 纯拓扑中心性布局不是诊断任务的最优选择。
2. 覆盖邻近并不是唯一有效策略。
3. 诊断表征能够提供不同于拓扑中心性和邻近覆盖规则的布局依据（EG 三条独立证据）。
4. 预算敏感性存在交叉点。

四个局限性：

1. Node-Feedback 训练数据仅 9 组，布局结构多样性有限。
2. Two-stage v1 利用全部缺陷场景仿真响应，属于信息充分参考。
3. 预算曲线仅 seed 42，趋势结论有待多 seed 验证。
4. 所有实验在同一管网（128 节点）上进行，跨管网泛化性待验证。

不要新增：

- 本章正文没有展开证明的优势。
- 对第4章主结果的反向改写。

可写：

- Node-Feedback 与 Embedding-Guided 在 layout seed 变化下保持较稳定的 direct/near/far、mean_hop 和 overlap_count。
- Jaccard 均值约为 0.87，表明节点集合高度相似但不完全一致。

不要写：

- 诊断性能对 layout seed 稳定。
- P2 替代多 seed 诊断评价。

#### 预算性能重训

建议放入：

- 第5.6.1 监测预算变化实验。
- 后续图件：预算-性能曲线、预算-结构-性能联合图。

当前可写：

- 核心 5 方法、5 个预算、3 个诊断 seed 的训练清单已经生成。
- P3 结果整理脚本已经具备，等待训练输出 JSON。

当前不要写：

- 预算增加提升 MRR 或 Top-K。
- 学习型布局在所有预算下最优。

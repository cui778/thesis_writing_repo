# 章节阅读路线图

本文件是每次写论文前的主入口。不要凭记忆找材料；先按本路线图确定“主线必读”和“按需证据”，再写小节。

固定工作流：

```text
选章节/小节
-> 打开本阅读路线图
-> 读取全局口径
-> 读取本章主线 README/closure 文档
-> 打开 notes/section_experiment_map.md 找到当前小节对应实验
-> 根据小节目标读取按需证据
-> 用 prompts/plan_one_section.md 让 AI 先输出小节计划
-> 用 prompts/write_one_section.md 写正文
-> 用 prompts/review_one_section.md 审查事实
-> 更新 notes/evidence_map.md
-> Git 提交
```

## 0. 全局每次必读

每次开始写作前先读：

```text
E:\11.16\script2_new\thesis_writing_package\README.md
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\04_DO_NOT_USE_AND_TERMINOLOGY.md
E:\11.16\script2_new\thesis_writing_package\05_TABLE_FIGURE_INDEX.md
```

用途：

- `README.md`：确认写作包的使用规则。
- `00_GLOBAL_THESIS_CONTEXT.md`：确认论文总结构、正式数据口径、正式任务边界。
- `04_DO_NOT_USE_AND_TERMINOLOGY.md`：确认禁用旧结果和统一术语。
- `05_TABLE_FIGURE_INDEX.md`：确认图表和结果文件索引。

注意：如果其他文档或提示词里出现重复路径 `script2_new\script2_new`，统一修正为 `E:\11.16\script2_new\...`。

此外，真正决定“当前小节该读哪张表、哪份闭环、哪张图”的文件是：

```text
E:\11.16\thesis_writing_repo\notes\section_experiment_map.md
```

本路线图负责“章级导航”，`section_experiment_map.md` 负责“小节级实验映射”。

## 1. 第1章 绪论

写作时机：第3/4/5章基本稳定后再写。

先读：

```text
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\04_DO_NOT_USE_AND_TERMINOLOGY.md
```

按需读：

```text
E:\11.16\script2_new\thesis_writing_package\01_CH3_WRITING_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
```

写作重点：

- 研究背景与工程意义。
- 排水管网缺陷诊断的核心问题。
- 本文围绕第3/4/5章形成的主要工作概括。

禁止：

- 不要提前夸大第4章和第5章结论。
- 不能写成本论文已经完成 P 类水质污染源定位。
- 不能在绪论中新增正文主体章节没有证明过的贡献。

## 2. 第2章 理论基础与相关研究

写作时机：第3/4/5章主体稳定后补写。

先读：

```text
E:\11.16\script2_new\thesis_writing_package\00_GLOBAL_THESIS_CONTEXT.md
```

按需读：

```text
E:\11.16\script2_new\docs
E:\11.16\script2_new\README.md
E:\11.16\script2_new\docs\ROADMAP_ALIGN_TO_PROPOSAL.md
```

写作重点：

- SWMM 与排水管网仿真基础。
- 排水管网缺陷诊断问题。
- 时序建模与图神经网络。
- 监测点布设优化相关方法。

禁止：

- 不要把第2章写成实验结果章。
- 不要使用第4/5章结果来替代理论和相关工作梳理。

## 3. 第3章 数据构建与任务定义

先读本章主线文件：

```text
E:\11.16\script2_new\thesis_writing_package\01_CH3_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter3_data_generation\docs\CH3_OUTLINE_AND_DATA_AUDIT_20260414.md
E:\11.16\script2_new\chapter3_data_generation\docs\CH3_VISUALIZATION_GUIDE_20260414.md
```

按需读取结果表：

```text
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_formal_dataset_statistics.csv
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_node_set_relationships.csv
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_residual_energy_by_scenario.csv
```

按需读取图件目录：

```text
E:\11.16\script2_new\chapter3_data_generation\figures
```

按需读取正式输入数据：

```text
E:\11.16\input_data\2_tuned_v3_merged1.inp
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42
```

写作重点：

- SWMM 管网建模与全网图结构。
- IE420 缺陷矩阵构建。
- 候选缺陷节点、监测节点和缺陷节点之间的关系。
- 全网时序、残差特征和 time-gated 样本构建。
- 数据合理性验证，包括缺陷响应、活跃期响应和可观测性差异。

禁止：

- 不要写第4章模型性能结果。
- 不要把水质伴随残差写成 P 类水质污染源定位。
- 不能声称 SWMM 模型已经实测校准，除非另有实测校准证据；当前更稳妥的表述是检查连通性、仿真稳定性、时间序列完整性和缺陷响应合理性。

## 4. 第4章 固定监测布局下的诊断模型

先读本章主线文件：

```text
E:\11.16\script2_new\thesis_writing_package\02_CH4_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter4_diagnosis_model\docs\CH4_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260414.md
```

按需读取正式结果表：

```text
E:\11.16\script2_new\outputs\reports\chapter1_restart_fullgraph_degree_ie420_multiseed.csv
E:\11.16\script2_new\outputs\reports\chapter1_restart_model_comparison_seed42.csv
E:\11.16\script2_new\outputs\reports\chapter1_restart_time_dimension_seed42.csv
E:\11.16\script2_new\outputs\reports\chapter1_restart_nodehold_multiseed.csv
E:\11.16\script2_new\outputs\reports\chapter4_ie_type_group_metrics.csv
E:\11.16\script2_new\outputs\reports\chapter1_task_level_results_summary.csv
```

按需读取图件目录：

```text
E:\11.16\script2_new\outputs\reports\figures
```

写作重点：

- degree N25 固定监测布局。
- full-graph sparse-observation 输入方式。
- `hydraulic_inverse_deepattn` 主模型。
- scenario split 主结果。
- 模型对比、时间维度消融、I/E 分类型结果。
- node_holdout 作为未见缺陷节点压力测试和边界分析。

禁止：

- 不要写成监测点布局优化章节。
- 不能使用旧 `MRR>=0.91` 结果。
- 不能把 node_holdout 写成已经解决未见节点泛化。
- 不能把 50 个候选节点定位写成 128 节点自由定位。

## 5. 第5章 监测点布局优化

先读本章主线文件：

```text
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

按需读取创新与路线文件：

```text
E:\11.16\script2_new\CH5_INNOVATION_TO_EXPERIMENT_MAP.md
E:\11.16\script2_new\PROPOSAL_VS_CURRENT_AND_CH5_INNOVATION_20260403.md
```

按需读取结果目录：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables
E:\11.16\script2_new\chapter5_layout_optimization\outputs\structural_innovation
```

写作重点：

- 在第3章正式母数据和第4章诊断评价器固定的前提下优化监测点布局。
- 只改变监测节点集合、observed mask 和布局策略。
- 比较不同布局对 I/E 缺陷定位性能的影响。
- 分析布局优化对 scenario split 和 node_holdout 的差异影响。

禁止：

- 不要重新定义缺陷矩阵。
- 不要重建母数据。
- 不要把第5章优化布局结果倒灌回第4章固定布局主结果。
- 不要把第5章写成重新训练或重新定义诊断任务的章节。

## 6. 第6章 总结与展望

写作时机：第3/4/5章完成后。

先读：

```text
E:\11.16\thesis_writing_repo\notes\evidence_map.md
E:\11.16\thesis_writing_repo\chapters\ch3_data_generation.md
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

写作重点：

- 总结第3章数据构建、第4章诊断模型、第5章布局优化三条主体贡献。
- 客观写出任务边界和不足。
- 展望 P 类水质污染源定位、严格未见节点泛化、更真实工况验证等后续方向。

禁止：

- 不要在总结中新增正文没有证明过的贡献。
- 不要把展望写成本文已经完成的工作。

## 7. 小节写作前检查清单

每写一个小节前，先回答：

- 本小节属于哪一章？
- 本章主线文件是否已读？
- `notes/section_experiment_map.md` 中对应小节的实验条目是否已读？
- 本小节要用哪些结果表、图或过程记录？
- 对应证据是否已经写入 `notes/evidence_map.md`？
- 本小节最容易越界的地方是什么？
- 本节是“数据构建”“模型实验”“布局优化”“总结包装”中的哪一种？

# 第5章实验规划：诊断反馈驱动的监测节点布局优化

## 1. 当前主线

第5章主线收束为“从人工规则选点走向诊断结果反馈指导布点”。本章不再把多个实验版本并列铺开，而是围绕以下递进关系组织：

```text
传统拓扑布局
→ 候选可观测性与两阶段平衡布局
→ 节点级诊断反馈学习
→ 布局级代理驱动搜索
```

正式学习型方法采用 clean 双层口径：

- `v0_2 clean`：节点级诊断反馈学习，回答“哪些节点值得被选”。
- `v2_2 clean`：布局级代理驱动搜索，回答“哪些节点组合整体更优”。

`Degree`、`Cand-Obs` 和 `Two-stage v1` 保留为人工规则与任务驱动基线。旧 `v2_2`、`v1_1/v1_2/v1_3` 图上下文探索、非 clean 学习版本不进入中期正式答辩主线。

## 2. 已完成实验

| 实验 | 方法 | 当前角色 | 主要用途 |
|---|---|---|---|
| 拓扑基线 | `Degree` | 对照基线 | 说明传统拓扑中心性布局不是定位任务最优 |
| 候选可观测性基线 | `Cand-Obs` | 任务驱动基线 | 说明候选近邻可观测性是重要机制 |
| 两阶段平衡布局 | `Two-stage v1` | 可解释规则框架 | 兼顾候选覆盖、空间平衡和冗余控制 |
| 节点级反馈学习 | `v0_2 clean` | clean 学习型方法一 | 学习单个节点的布设价值 |
| 布局级代理搜索 | `v2_2 clean` | clean 学习型方法二 | 搜索整体更优的节点组合 |
| 未见节点压力测试 | `node_holdout` | 边界实验 | 说明分布内提升不等于严格未见节点泛化 |
| 无重训补充分析 | 表格重建与现有结果整理 | 论文证据补强 | 补齐 Event Top-K、预算结构、direct/near/far 分组性能、hard candidates 性能、Jaccard 和 surrogate |

主评价协议：

- 固定第3章 IE420 母数据；
- 固定第4章诊断任务、模型结构、窗口设置和评价协议；
- 只改变监测节点集合 `S` 与 observed mask；
- 第5章主排名只看空间定位指标：MRR、Top-1、Top-3、Top-5、event-level Top-K。

本轮无重训补强已经生成以下成品表和图件：

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary_with_event_topk.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_6_budget_observability_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_7_layout_jaccard_similarity.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_8_surrogate_prediction_quality.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_9_hard_candidate_definition.csv
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_main_spatial_performance_event_topk.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_learning_level_comparison.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_budget_observability_curve.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_direct_near_far_stack.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_layout_jaccard_heatmap.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_surrogate_prediction_scatter.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_node_holdout_boundary.png
```

当前写作仓库中另有 P0 结果数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_main_metrics_from_raw_json_all_seeds.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_direct_near_far_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_direct_near_far_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_hard_candidates_definition.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_hard_candidates_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_hard_candidates_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_result_review.md
```

其中 `CH5-P0_result_review.md` 为内部结果审查报告，不直接作为正文，但其中的指标口径、分组结论和边界判断已经吸收到 `ch5_layout_optimization.md` 的 5.6 节。

## 2.1 多 seed 口径说明

当前第5章主结果中的 seed 7、42、123 用于复核同一布局方法在不同 `scenario split`、诊断模型初始化和训练随机性下的评价稳定性。正式布局文件由方法名与监测预算 `N=25` 确定，例如：

```text
monitor_nodes_degree_N25.json
monitor_nodes_candidate_observability_N25.json
monitor_nodes_two_stage_balanced_layout_v1_N25.json
monitor_nodes_learnable_layout_network_v0_2_clean_scenario_N25.json
monitor_nodes_learnable_layout_network_v2_2_clean_generalization_N25.json
```

因此，当前多 seed 主表可以写作“诊断评价多 seed 均值与标准差”，不应写作“布局生成过程多 seed 稳定性”。若要验证学习型布局生成过程本身的稳定性，需要另行生成多组 `v0_2 clean` 和 `v2_2 clean` 布局实例，并比较节点集合和结构指标的波动。

## 3. 待补实验优先级

### P0：必须补齐

1. 补齐 `event Top-3 / event Top-5` 成品表。
   - 性质：表格视图补齐，不重训。
   - 来源：`E:\11.16\script2_new\chapter5_layout_optimization\outputs\ch5_thesis_main_results_by_seed.csv`
   - 目的：让第5章主表与第4章 Event Top-K 口径一致。
   - 当前状态：已完成，见 `table_5_2_main_scenario_seed_summary_with_event_topk.csv`。

2. 预算实验 `N=5/10/15/20/25`。
   - 性质：正式论文需要写入。
   - 当前可先画结构趋势：`far`、`mean_hop`、`direct/near/far` 随预算变化。
   - 若后续有训练结果，再补空间定位性能曲线。
   - 当前状态：已完成无重训结构趋势；尚未补多预算性能训练。

3. 场景级 raw JSON 主结果整理。
   - 性质：无重训结果整理。
   - 来源：正式方法 raw metrics JSON、缺陷矩阵和候选可观测性分层表。
   - 输出：`CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`、`CH5-P0_main_metrics_from_raw_json_all_seeds.csv`。
   - 当前状态：已完成。

### P1：建议补齐

1. direct / near / far 分组性能实验。
   - 目的：把结构机制和诊断性能连起来。
   - 输出：不同布局在 direct、near、far 候选上的 MRR / Top-K。
   - 当前状态：已完成基于 P0 raw JSON 的候选难度分组性能表，见 `CH5-P0_direct_near_far_performance_by_seed.csv` 和 `CH5-P0_direct_near_far_performance_summary.csv`。
   - 边界：当前分组来自候选可观测性分层，用于候选难度解释；若要得到“每种布局自身的 direct/near/far”，需基于各布局 `monitor_nodes_*.json` 重新计算。

2. hard candidates 分层实验。
   - 目的：证明学习型布局是否改善难定位候选，而不是只提升 easy cases。
   - 分层方式：可用 `Degree` 下低排名候选、far 候选、或历史低 MRR 候选定义 hard group。
   - 当前状态：已完成 far 候选定义下的 hard group 性能表，见 `CH5-P0_hard_candidates_definition.csv`、`CH5-P0_hard_candidates_performance_by_seed.csv` 和 `CH5-P0_hard_candidates_performance_summary.csv`。
   - 后续可补：基于低 MRR 场景或 far 且低 MRR 场景的第二种 hard 定义。

3. 布局相似度 Jaccard 热力图。
   - 目的：证明学习型布局不是简单复制 `Cand-Obs` 或 `Two-stage v1`。
   - 输出：不同布局监测节点集合之间的 Jaccard overlap。
   - 当前状态：已完成。

4. I/E 类型与场景属性分组实验。
   - 目的：检查布局收益是否集中在某类缺陷或特定场景属性上。
   - 分组方式：`defect_type`、`intensity_pct`、`duration_h`、`start_hour`。
   - 数据来源：`CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`。
   - 当前状态：尚未整理，属于无重训可补实验。

### P2：可选增强

1. surrogate 预测质量散点图。
   - 目的：解释 `v2_2 clean` 的代理搜索可信度。
   - 输出：代理预测布局质量 vs 真实 MRR / Top-1。
   - 当前状态：已完成正式方法可比子集散点图；旧探索版本不进入图件。

2. 关键节点替换或 leave-one-out 贡献实验。
   - 目的：说明哪些监测节点对定位贡献更大。
   - 成本较高，可作为后续论文增强或附录实验。

3. 学习型布局生成多 seed 稳定性。
   - 目的：检验 `v0_2 clean` 和 `v2_2 clean` 布局生成过程本身是否稳定。
   - 推荐先做无重训结构稳定性：多次生成布局实例，比较 Jaccard、节点选择频率、direct/near/far、mean_hop 和 overlap_count。
   - 若进一步做性能稳定性，则需要对每个布局实例重新训练或重新评价诊断模型，工作量明显增加。
   - 当前状态：尚未开展，本轮先不做。

## 3.1 下一步执行顺序

后续实验先从无重训补充开始，优先补齐机制口径，再考虑重训类实验。

1. **P1-1：每种布局自身 direct / near / far 重新计算**
   - 性质：无重训结构计算。
   - 输入：各正式布局的 `monitor_nodes_*.json`、候选缺陷节点集合和管网拓扑。
   - 输出：每种布局下候选节点到最近监测节点的 `min_monitor_hop`、`nearest_monitor`、`direct/near/far` 分组和结构汇总表。
   - 用途：把当前候选难度分组与每种布局自身结构分组区分开，使 5.6 的可观测性口径更干净。

2. **P1-2：I/E 类型与场景属性分组**
   - 性质：无重训结果整理。
   - 输入：`CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`。
   - 输出：I/E 分组性能、`intensity_pct` 分组性能、`duration_h` 分组性能和必要的场景计数表。
   - 用途：检验布局收益是否依赖缺陷类型、强度或持续时间，补充第5章机制分析。

3. **P1-3：hard candidates 第二定义**
   - 性质：无重训结果整理。
   - 输入：P0 场景级 raw 结果和当前 far hard 定义。
   - 输出：low-MRR hard、far 且 low-MRR hard、当前 far hard 的对照表。
   - 用途：避免 hard candidates 仅由距离分组定义，提高困难场景分析的稳健性。

4. **P2：学习型布局生成多 seed 稳定性**
   - 性质：后续增强，当前不做。
   - 推荐顺序：先做无重训结构稳定性，再考虑性能重训。
   - 输出：多布局实例的 Jaccard、节点选择频率、direct/near/far、mean_hop 和 overlap_count。
   - 用途：检验 `v0_2 clean` 和 `v2_2 clean` 的布局生成过程是否稳定。

5. **P2/P3：预算 `N=5/10/15/20/25` 性能重训**
   - 性质：重训类实验，当前不做。
   - 当前边界：已有预算结构趋势只能写“预算改变候选可观测性结构”，不能写“预算提升诊断性能”。
   - 后续条件：若需要预算-性能曲线，应为不同预算布局生成 observed mask，并按第4章固定诊断协议重新训练或重新评价。

## 4. 图件计划

| 图件 | 支撑主张 | 图型 | 证据来源 | 位置 |
|---|---|---|---|---|
| 实验闭环图 | 固定诊断协议，只改变布局 | 流程图 | 本章实验协议 | 正文/答辩 |
| 布局拓扑叠加图 | 学习型布局不是简单复制人工规则布局 | 管网拓扑叠加 | 各布局 `monitor_nodes_*.json` | 正文 |
| direct / near / far 堆叠图 | 候选观测盲区减少 | 堆叠柱状图 | `table_5_1_layout_structure.csv` | 正文 |
| direct / near / far 分组性能图 | 不同候选难度下布局性能不同 | 小多图点图 | `CH5-P0_direct_near_far_performance_summary.csv` | 正文 |
| 主性能误差棒图 | 布局优化提升空间定位性能 | 均值±标准差点图 | `table_5_2_main_scenario_seed_summary.csv` | 正文 |
| 预算-可观测性曲线 | 预算变化下布局趋势 | 折线图 | `layout_summary.csv` | 正文/补充 |
| 节点级 vs 布局级反馈对比图 | 两类 clean 学习方法层次不同 | 双栏对比图 | `v0_2 clean`、`v2_2 clean` 结果 | 答辩 |
| node_holdout 边界图 | 未见节点泛化仍有边界 | 对比柱状图 | `table_5_4_node_holdout_boundary_seed42.csv` | 正文/备答 |
| Jaccard 热力图 | 不同布局选择集合存在差异 | 热力图 | 各布局 monitor nodes | 补充 |
| hard candidates 分组图 | 整体最优与困难候选保护不完全一致 | hard vs other gap plot | `CH5-P0_hard_candidates_performance_summary.csv` | 正文/补充 |
| I/E 类型分组图 | 检查布局收益是否依赖缺陷类型 | 双面板点图 | 待补 I/E 分组表 | 补充 |
| 布局生成稳定性图 | 学习型布局生成过程是否稳定 | Jaccard / 节点频率图 | 待补多布局实例 | 后续 |

## 5. 中期答辩口径

中期答辩只讲 clean 双层学习型主线：

```text
Degree / Cand-Obs / Two-stage v1
→ v0_2 clean：节点级反馈学习
→ v2_2 clean：布局级代理搜索
```

不讲：

- 旧 `v2_2`；
- `v1_1/v1_2/v1_3` 图上下文探索；
- 非 clean 学习版本作为正式主线；
- `node_holdout` 主排名。

`node_holdout` 只用于说明边界：

> 当前布局优化能提升主协议下的空间定位效果，但严格未见缺陷节点泛化仍需后续研究。

## 6. 正文保留空位

正式正文可以先留以下空位，后续补实验后填入：

- 多预算性能曲线；
- 每种布局自身的 direct / near / far 重新计算；
- hard candidates 第二定义；
- I/E 类型与场景属性分组；
- 学习型布局生成多 seed 稳定性；
- Jaccard 布局相似度；
- surrogate 可信度分析；
- 典型布局案例图。

## 7. 不进入正式主线的内容

- 旧 `learnable_layout_network_v2_2_generalization`：只作为历史探索，不进入中期正式答辩。
- `learnable_layout_network_v0_2_generalization`：可作为性能参考或内部记录，不作为 clean 主线。
- `v1_1/v1_2/v1_3` 图上下文版本：不作为正式方法，只可在内部记录中说明探索失败。
- 旧高分口径、旧矩阵、旧 `v2e_dense_ie`：禁止作为第5章正式证据。

## 8. P1 无重训补充实验执行记录

本轮已完成 3.1 中的前三项无重训实验。实验仅使用现有布局 JSON、管网拓扑特征和 P0 场景级结果表，不启动模型训练，也不生成图件。

### 8.1 P1-1 每种布局自身 direct / near / far 重新计算

执行脚本：

```text
E:\11.16\thesis_writing_repo\figures\ch5\scripts\build_ch5_p1_source_data.py
```

输入数据：

```text
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\graph_path_features.npz
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\degree\monitor_nodes_degree_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\candidate_observability\monitor_nodes_candidate_observability_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\two_stage_balanced_layout_v1\monitor_nodes_two_stage_balanced_layout_v1_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\learnable_layout_network_v0_2_clean_scenario\monitor_nodes_learnable_layout_network_v0_2_clean_scenario_N25.json
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\learnable_layout_network_v2_2_clean_generalization\monitor_nodes_learnable_layout_network_v2_2_clean_generalization_N25.json
```

输出数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_layout_specific_candidate_observability.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_layout_specific_observability_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_layout_specific_raw_with_tiers.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_layout_specific_direct_near_far_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_layout_specific_direct_near_far_performance_summary.csv
```

结构汇总如下：

| 方法 | direct | near | far | mean_hop | max_hop | overlap_count |
|---|---:|---:|---:|---:|---:|---:|
| Degree | 12 | 21 | 17 | 3.48 | 15.0 | 12 |
| Cand-Obs | 15 | 34 | 1 | 0.94 | 3.0 | 15 |
| Two-stage v1 | 18 | 31 | 1 | 0.92 | 4.0 | 18 |
| v0_2 clean | 14 | 25 | 11 | 1.92 | 15.0 | 14 |
| v2_2 clean | 12 | 35 | 3 | 1.24 | 4.0 | 12 |

写作边界：该结果用于区分“候选节点原始可观测性分组”和“每种布局自身可观测性分组”。正文中可写为结构机制分析，不应写成新增训练实验。

### 8.2 P1-2 I/E 类型与场景属性分组

输入数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv
```

输出数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_defect_type_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_defect_type_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_intensity_pct_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_intensity_pct_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_intensity_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_intensity_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_duration_h_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_duration_h_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_duration_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_duration_performance_summary.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_start_hour_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_start_hour_performance_summary.csv
```

分组指标包括 `scenario_mrr`、`scenario_top1`、`scenario_top3` 和 `scenario_top5`。seed 7、42、123 仍表示诊断评价多 seed，不表示布局生成多 seed。

写作边界：该结果用于检验布局收益是否集中于特定缺陷类型、缺陷强度、持续时间或发生时刻。若分组样本数较少，正文中只做现象描述，不做过强机制归因。

### 8.3 P1-3 hard candidates 第二定义

输出数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_hard_candidate_second_definitions.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_hard_candidate_second_definition_performance_by_seed.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_hard_candidate_second_definition_performance_summary.csv
```

定义口径：

- `far_hard_current`：沿用当前基于 far 候选的 hard 定义。
- `low_mrr_degree_q25`：以 Degree 布局下场景平均 MRR 的后 25% 作为困难场景。
- `far_and_low_mrr`：同时满足 far hard 与 Degree 低 MRR。

本轮阈值和数量：

| 定义 | 数量 |
|---|---:|
| Degree MRR 后 25% 阈值 | 0.513889 |
| far hard 场景 | 53 |
| low-MRR hard 场景 | 42 |
| far 且 low-MRR hard 场景 | 21 |

写作边界：该结果用于避免 hard candidates 只由空间距离定义。正文中可比较不同 hard 定义下各布局表现是否一致，但不应把 Degree 低 MRR 定义解释为唯一困难性标准。

### 8.4 本轮校验

- 脚本语法检查通过。
- P1-1 候选可观测性明细为 250 行，即 5 种布局 × 50 个候选节点。
- P1-1 结构汇总为 5 行，并与布局 JSON 内 `layout_metrics` 对齐。
- 合并后的 P1 raw 表为 945 行，与 P0 raw 场景结果行数一致。
- 输出结果只包含 `Degree / Cand-Obs / Two-stage v1 / v0_2 clean / v2_2 clean`。
- 本轮未生成图片，未启动重训。

### 8.5 后续衔接

下一步应先审查 P1 分组结果是否能支撑正文判断，再决定是否更新 `ch5_layout_optimization.md` 和 `part5_layout_optimization_ppt_text.md` 的实验结果段落。P2 学习型布局生成多 seed 稳定性和多预算性能重训仍保留为后续增强实验，不影响当前 P1 结果链。

## 9. 候选节点重合度控制补充实验

本轮补充了“候选节点重合度不是唯一目标”的机制证据，用于回应“是否直接在 50 个候选缺陷节点中选取监测点即可”的问题。该实验不新增训练，基于正式主线结果和已有 overlap-controlled seed42 探针结果整理。

执行脚本：

```text
E:\11.16\thesis_writing_repo\figures\ch5\scripts\build_ch5_candidate_overlap_evidence.py
```

输出数据：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_candidate_overlap_vs_performance_evidence.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-P1_candidate_overlap_evidence_README.md
```

核心结果：

| 方法 | overlap_count | 非候选监测点数 | MRR | Top-1 |
|---|---:|---:|---:|---:|
| Degree | 12 | 13 | 0.7778 | 0.6426 |
| Cand-Obs | 15 | 10 | 0.8664 | 0.7827 |
| Two-stage v1 | 18 | 7 | 0.8715 | 0.7811 |
| v0_2 clean | 14 | 11 | 0.8658 | 0.7725 |
| v2_2 clean | 12 | 13 | 0.8856 | 0.8070 |

写作口径：

- 可写：`v2_2 clean` 的候选节点重合数并不高于 `Cand-Obs` 和 `Two-stage v1`，但总体 MRR 和 Top-1 更高，说明布局收益不能由候选节点重合数单独解释。
- 可写：已有 overlap-controlled 探针在相同 `overlap_count=12` 下仍出现性能差异，说明非候选监测点的补点位置和全图结构覆盖会影响诊断性能。
- 不可写：当前尚未完成 candidate-only 布局的多 seed 正式训练，因此不能声称“candidate-only 一定更差”。本节结论应限定为“候选节点重合数不是充分条件，布局优化不应等同于候选节点重合最大化”。

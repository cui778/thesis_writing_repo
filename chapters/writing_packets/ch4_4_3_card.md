# 第4章 4.3 模型性能与方法机制验证 写作卡

## 当前小节任务

- 目标章节：4.3 模型性能与方法机制验证
- 章节总纲：`E:\11.16\thesis_writing_repo\chapters\writing_packets\ch4_master.md`
- 科学问题：DeepAttn-L3 的定位增益是否确实来自多层路径引导聚合与完整水力路径先验，而非普通图建模、时序编码器差异或单次路径注意力？
- 本节核心结论：多层路径引导聚合构成主模型的主要性能来源；三层后收益趋于饱和；完整路径先验进一步改善前位排序、事件级首位定位和误报控制。
- 在全章故事线中的位置：承接4.2的方法定义，通过主模型对比与消融完成方法有效性验证，是第4章的核心证据节。
- 与上一节的关系：4.2 已定义稀疏观测输入、水力路径先验和多层注意力结构，本节对这些设计逐项进行实验验证。
- 向下一节交付：确定 DeepAttn-L3 为固定正式模型，使 4.4 仅分析窗口长度、空间条件和诊断过程，不再重复证明模型结构有效性。
- 目标篇幅：3000-4000 字。

## 必读证据

- `E:\11.16\thesis_writing_repo\chapters\CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- `E:\11.16\thesis_writing_repo\chapters\CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md`
- `E:\11.16\thesis_writing_repo\figures\ch4\generated_results\CH4_OFFICIAL_FIGURE_INDEX.md`
- `E:\11.16\thesis_writing_repo\figures\DATA_SOURCE_POLICY.md`

## 证据矩阵

| 证据ID | 等级 | 类型 | 文件/图表 | 正式口径 | 可支持结论 | 不可支持结论 |
|---|---|---|---|---|---|---|
| E01 | E1 | 正式多 seed 模型对比 | `CH4-F11_method_ablation_summary.csv`；`16_CH4_grouped_model_comparison` | IE420+normal20、Degree-N25、scenario split、seeds 7/42/123 | DeepAttn-L3 相对纯时序、普通图和单层路径模型具有明确定位增益 | 不能将 GRU-GCN 与 GraphSAGE 的差值归因于单一模块 |
| E02 | E2 | 深度消融 | `CH4-F11_method_ablation_summary.csv`；`17_CH4_deepattn_depth_ablation` | 相同正式协议、L1-L4、3 seeds | L1-L3 持续增益，L4 进入平台且误报上升，支持选择 L3 | 不能写 L4 性能下降；其 MRR 略高 |
| E03 | E2 | 路径先验消融 | `CH4-F11_method_ablation_summary.csv`；`18_CH4_path_prior_ablation` | Content-only 与 Full 为3 seeds | 完整路径先验提高 MRR、Top-1、Event Top-1并降低FPR | 不能把全部增益归因于最短距离 |
| E04 | E3 | Distance-only机制探针 | `CH4-F11_method_ablation_summary.csv` | 仅 seed42 | 距离信息可支持候选覆盖，完整先验的前位排序更好 | 不能形成多 seed 稳定性结论 |
| E05 | E2 | 编码器控制 | Hydraulic-Inverse-GRU/LSTM 多 seed结果 | 相同数据和布局 | LSTM改善单层模型但不能解释DeepAttn主要增益 | 不能宣称LSTM无贡献 |

## 正文段落安排

| 顺序 | 段落任务 | 证据ID | 局部结论 |
|---:|---|---|---|
| P1-P2 | 说明本节验证目标、统一实验协议与模型分组原则 | E01、E05 | 对比对象按非路径、单层路径和多层路径组织 |
| P3-P5 | 分析模型对比的MRR、Top-1和Top-3 | E01 | 多层路径聚合构成主要性能来源 |
| P6-P8 | 分析L1-L4累计收益、边际收益与误报变化 | E02 | 三层是性能、误报与复杂度的折中点 |
| P9-P12 | 分析Content、Distance和Full路径先验，并排除编码器解释 | E03、E04、E05 | 完整路径先验获得独立机制证据 |
| P13 | 汇总本节结论并交付4.4固定模型 | E01-E05 | DeepAttn-L3作为后续分析的正式模型 |

## 图表计划

| 图表 | 身份 | 画的是什么 | 需要报告的结果 | 支撑结论 | 使用边界 |
|---|---|---|---|---|---|
| `16_CH4_grouped_model_comparison` | 正式主图 | 非路径、单层路径与DeepAttn-L3的MRR及Top-K | DeepAttn-L3 MRR=0.825；最强单层模型0.485 | 多层路径聚合带来主要增益 | 不按模型名称简单排名，应按验证角色组织 |
| `17_CH4_deepattn_depth_ablation` | 正式消融图 | L1-L4定位性能和边际MRR增益 | L1=0.384、L2=0.696、L3=0.825、L4=0.831 | L3前增益持续，L4平台化 | L4并非所有指标更差 |
| `18_CH4_path_prior_ablation` | 正式机制图 | Content-only、Distance-only和Full路径先验 | Full相对Content MRR +0.050，Event Top-1 +0.090 | 完整路径先验改善前位排序和误报 | Distance-only仅seed42 |

## 事实与结论核查

- [ ] 所有数值可追溯
- [ ] 多 seed 与单 seed 已区分
- [ ] 正式结果与历史口径未混合
- [ ] 每张图均有实质结果分析
- [ ] 机制解释具有消融或结构证据
- [ ] 禁止结论未进入正文
- [ ] 术语与全章一致

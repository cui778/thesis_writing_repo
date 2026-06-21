# PPT 材料交接文档（第3、4、5章）

## 正式协议

```
数据集：ie420_plus_normal20_v1（441 场景 = 421 IE420 + 20 normal）
业务时序特征集：raw_plus_residual（4 raw + 4 residual + 4 relative residual = 12 维）
模型动态输入张量：12 维业务时序特征 + 2 维小时周期编码 + 1 维 observed mask = 15 维
lambda_loc：0.5
模型：hydraulic_inverse_deepattn
布局：degree_N25（25 监测节点，全网 128 节点）
划分：scenario split
诊断种子：7 / 42 / 123
```

### 特征维度明细

| 类别 | 变量 | 维度 |
|---|---|---:|
| 原始水力 | depth, total_outflow | 2 |
| 原始水质 | pollut_NH4, pollut_TSSs | 2 |
| 绝对残差 | depth_residual, total_outflow_residual, pollut_NH4_residual, pollut_TSSs_residual | 4 |
| 相对残差 | depth_residual_rel, total_outflow_residual_rel, pollut_NH4_residual_rel, pollut_TSSs_residual_rel | 4 |
| **合计** | | **12** |

### 辅助输入与静态结构先验

| 类别 | 变量 | 维度 | 说明 |
|---|---|---:|---|
| 时间辅助通道 | sin(hour), cos(hour) | 2 | 数据加载阶段自动追加 |
| 稀疏观测掩码 | observed_mask | 1 | 标记当前布局中的监测节点 |
| **动态输入张量合计** | 12 维业务时序 + 3 维辅助通道 | **15** | 作为时序编码器输入 |
| 节点对静态路径先验 | shortest_dist, pipe_length_dist, flow_direction, elevation_diff | 4 | 作为液压逆向注意力关系输入，不计入节点动态特征维度 |

正式配置不追加趋势通道或传播延迟通道。`head` 与 `volume` 可由 SWMM 输出，但不进入正式诊断输入。

---

## 第3章：数据生成

### 可用图源

| 图号 | 内容 | 状态 | 路径 |
|---|---|---|---|
| CH3-F01 | 数据集协议概要 | source_data 就绪 | `figures/ch3/source_data/CH3-F01_dataset_protocol_summary.csv` |
| CH3-F02 | IE420 缺陷矩阵统计 | source_data 就绪 | `figures/ch3/source_data/CH3-F02_ie420_defect_matrix_summary.csv` |
| CH3-F03 | 正常工况层参数 | source_data 就绪 | `figures/ch3/source_data/CH3-F03_normal_condition_layer_summary.csv` |
| CH3-F04 | 采样与记录数统计 | source_data 就绪 | `figures/ch3/source_data/CH3-F04_sampling_and_record_count.csv` |
| CH3-F05 | 残差特征定义 | source_data 就绪 | `figures/ch3/source_data/CH3-F05_residual_feature_definition.csv` |
| CH3-F06 | 数据完整性审计 | source_data 就绪 | `figures/ch3/source_data/CH3-F06_dataset_integrity_audit.csv` |
| CH3-S01 | SWMM 管网截图 | 等待人工截图 | `figures/ch3/screenshots_needed/` |

> 注：以上为图源 CSV 数据就绪，正式 PNG 仍需后续绘制。

### 核心数据口径

- IE420 母数据：1 正常参照 + 250 I + 170 E = 421 场景
- normal20：20 个无缺陷正常扰动场景
- 正式组合：421 + 20 = 441 场景
- 每场景：128 节点 x 287 时刻 = 36736 条节点记录

### 关键说明

- 正常场景与缺陷场景处于同一数据层级
- reference 响应用于残差对齐，normal 扰动场景用于表征正常波动
- 48 h 是统一观测窗口，不是缺陷寿命假设

---

## 第4章：诊断模型

### 可用图源

| 图号 | 内容 | 状态 | 数据来源 |
|---|---|---|---|
| CH4-F00 | 诊断主线流程图 | diagrams/ 就绪 | 示意图 |
| CH4-F01 | 滑动窗口与场景聚合 | diagrams/ 就绪 | 示意图 |
| CH4-F02 | V/S/C/D 节点关系 | diagrams/ 就绪 | 示意图 |
| CH4-F03 | time-gated 窗口标签 | diagrams/ 就绪 | 示意图 |
| CH4-F04 | 输出头到指标链条 | diagrams/ 就绪 | 示意图 |
| CH4-F05 | 模型结构图 | diagrams/ 就绪 | 示意图 |
| CH4-F06 | 多 seed 稳定性 | **正式协议数据就绪，待重绘** | ie420+normal20 |
| CH4-F07 | 主诊断结果表 | **正式协议数据就绪，待重绘** | ie420+normal20 |
| CH4-F08 | 特征组合对照 | **历史 - seedset10 数据集** | 旧协议，调参依据 |
| CH4-F09a | 时间边界审查 | 历史 - 旧协议 | 备答 |
| CH4-F09b | 窗口长度影响 | 历史 - 旧协议 | 趋势参考 |
| CH4-F10a | I/E 分组定位 | 历史 - 旧协议 | 趋势参考 |
| CH4-F10b | 可观测性分析 | 历史 - 旧协议 | 趋势参考 |
| CH4-F11 | Ch4 到 Ch5 衔接 | diagrams/ 就绪 | 示意图 |
| CH4-S01 | 管网监测节点截图 | 等待人工截图 | |

### 正式主结果（seed42, ie420+normal20）

| 指标 | 值 |
|---|---|
| MRR | 0.8457 |
| Top-1 | 0.7728 |
| Top-3 | 0.8973 |
| Top-5 | 0.9463 |
| Active F1 | 0.9790 |
| Normal Window FPR | 0.0005 |
| Scene F1 | 0.9917 |

### 多 seed 结果（Degree_N25_formal）

| seed | MRR | Top-1 | Top-3 | Event Top-1 | Scene F1 |
|---|---|---|---|---|---|
| 7 | 0.8477 | 0.7413 | 0.9443 | 0.7969 | 1.0000 |
| 42 | 0.8457 | 0.7728 | 0.8973 | 0.8197 | 0.9917 |
| 123 | 0.7827 | 0.6425 | 0.9161 | 0.6885 | 1.0000 |

### 关键说明

- 模型只有两个窗口级输出：`p_active(t)` 和 `node_scores(t)`
- 场景级报警、活跃期定位和空间定位均为聚合结果
- CH4-F08 特征组合和 CH4-F09b/F10a 来自旧 seedset10 数据集，不作为正式协议性能
- `node_holdout` 是泛化压力测试，不替代正式 scenario split 主结果

---

## 第5章：布局优化

### 可用图源

| 图号 | 内容 | 状态 | 路径 |
|---|---|---|---|
| CH5-F02 | 核心实验结果矩阵 | source_data 就绪，待绘图 | `figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv` |
| CH5-F04 | 布局方案多 seed 对比 | source_data 就绪，待绘图 | `figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv` |
| CH5-budget | 预算曲线 | source_data 就绪 | `figures/ch5/source_data/CH5-budget_sweep_seed42.csv` |
| CH5-hard | 困难候选分析 | source_data 就绪 | `figures/ch5/source_data/CH5-N25_hard_candidate_analysis.csv` |
| CH5-defect_type | I/E 类型分析 | source_data 就绪 | `figures/ch5/source_data/CH5-N25_by_defect_type_analysis.csv` |
| CH5-jaccard | 布局相似度 | source_data 就绪 | `figures/ch5/source_data/CH5-N25_pairwise_jaccard.csv` |
| CH5-structure | 布局结构特征 | source_data 就绪 | `figures/ch5/source_data/CH5-N25_layout_structure.csv` |

### 核心结论

1. 纯拓扑中心性布局（Degree）不是诊断任务最优
2. 覆盖邻近并不是唯一有效策略
3. Embedding-Guided 是正文主方法（MRR 0.897 +/- 0.017）
4. 预算敏感性存在交叉点

---

## 图源目录索引

```
thesis_writing_repo/figures/
  ch3/
    source_data/     — CH3-F01 ~ CH3-F06 CSV（数据就绪，PNG 待绘）
    diagrams/        — 待生成
    screenshots_needed/ — CH3-S01, CH3-S02
  ch4/
    source_data/     — CH4-F06 ~ CH4-F10b CSV
    source_data/legacy_old_protocol/ — 旧版 F06
    data_plots/      — 现有 PNG（F09a/F09b/F10a/F10b 为历史协议）
    data_plots/legacy_old_protocol/ — 旧协议 PNG
    diagrams/        — CH4-F00 ~ CH4-F05, CH4-F11
    screenshots_needed/ — CH4-S01
  ch5/
    source_data/     — CH5-EXPT/budget/jaccard/structure 等正式 CSV
    source_data/legacy_old_protocol/ — 旧版图源
    source_data/legacy_old_pipeline/ — 旧管线图源
    data_plots/      — 待生成
```

## 内部索引

- 正式协议冻结：`script2_new/chapter3_data_generation/plans/CH3_PROTOCOL_FREEZE.md`
- 正式协议冻结：`script2_new/chapter4_diagnosis_model/plans/CH4_PROTOCOL_FREEZE.md`
- 第4章结果证据矩阵：`thesis_writing_repo/chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- 第5章结果证据矩阵：`thesis_writing_repo/chapters/CH5_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- 第4、5章结果逻辑：`thesis_writing_repo/chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md`
- 网页端写作入口：`thesis_writing_repo/WEB_WRITING_START_HERE.md`
- 正式图件索引（Ch3）：`thesis_writing_repo/figures/ch3/generated_results/CH3_OFFICIAL_FIGURE_INDEX.md`
- 正式图件索引（Ch4）：`thesis_writing_repo/figures/ch4/generated_results/CH4_OFFICIAL_FIGURE_INDEX.md`
- 正式图件索引（Ch5）：`thesis_writing_repo/figures/ch5/generated_results/CH5_OFFICIAL_FIGURE_INDEX.md`

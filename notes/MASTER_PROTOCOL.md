# 正式实验协议总索引

本文件是第3至5章唯一口径来源，所有正文、PPT 和答辩内容以本文件口径为准。

## 第3章：数据生成

### 正式协议

```
母数据：time_gated_full_ie_v4_formal_conservative420_seed42
正常层：normal_multibaseline_v2_seedset20
正式组合：ie420_plus_normal20_v1
场景统计：1 reference + 250 I + 170 E = 421 缺陷 + 20 normal = 441 场景
采样：48 h / 10 min = 287 时刻 / 128 节点 = 36736 记录/场景
```

### 正式数据集清单

| 数据集 | 状态 | 场景数 | 用途 |
|---|---|---|---|
| `time_gated_full_ie_v4_formal_conservative420_seed42` | formal | 421 | IE420 缺陷母数据 |
| `normal_multibaseline_v2_seedset20` | formal | 21 | 正常工况层（1 reference + 20 扰动） |
| `ie420_plus_normal20_v1` | formal | 441 | 第4、5章正式训练组合 |

### 正式图源

| 图号 | 路径 | 状态 |
|---|---|---|
| CH3-F01 | `figures/ch3/source_data/CH3-F01_dataset_protocol_summary.csv` | data_ready |
| CH3-F02 | `figures/ch3/source_data/CH3-F02_ie420_defect_matrix_summary.csv` | data_ready |
| CH3-F03 | `figures/ch3/source_data/CH3-F03_normal_condition_layer_summary.csv` | data_ready |
| CH3-F04 | `figures/ch3/source_data/CH3-F04_sampling_and_record_count.csv` | data_ready |
| CH3-F05 | `figures/ch3/source_data/CH3-F05_residual_feature_definition.csv` | data_ready |
| CH3-F06 | `figures/ch3/source_data/CH3-F06_dataset_integrity_audit.csv` | data_ready |

---

## 第4章：诊断模型

### 正式协议

```
数据集：ie420_plus_normal20_v1
特征集：raw_plus_residual（4 raw + 4 residual + 4 relative residual = 12 维）
lambda_loc：0.5
模型：hydraulic_inverse_deepattn
布局：degree_N25（25 监测节点，全网 128 节点）
候选空间：C=50
划分：scenario split
诊断种子：7 / 42 / 123
窗口：sequence_length=36 (~6h)，window_stride=6 (~1h)
```

### 正式主结果（seed42）

| 指标 | 值 | 来源 |
|---|---|---|
| MRR | 0.8457 | `last_run_metrics_48h_control_ie420_normal20_raw_plus_residual_loc0p5_degree_N25_s42.json` |
| Top-1 | 0.7728 | 同上 |
| Top-3 | 0.8973 | 同上 |
| Top-5 | 0.9463 | 同上 |
| Active F1 | 0.9790 | 同上 |
| Normal Window FPR | 0.0005 | 同上 |
| Scene F1 | 0.9917 | 同上 |

### 正式多 seed 结果（Degree_N25_formal）

| seed | MRR | Top-1 | Top-3 | Top-5 | Event Top-1 | Event Top-3 | Scene F1 |
|---|---|---|---|---|---|---|
| 7 | 0.8477 | 0.7413 | 0.9443 | 0.9741 | 0.7969 | 0.9688 | 1.0000 |
| 42 | 0.8457 | 0.7728 | 0.8973 | 0.9463 | 0.8197 | 0.9508 | 0.9917 |
| 123 | 0.7827 | 0.6425 | 0.9161 | 0.9759 | 0.6885 | 0.9344 | 1.0000 |

来源：`CH5-EXPT_fixed_protocol_N25_main_table.csv` Degree 行

### 正式图源

| 图号 | 路径 | 状态 | 口径 |
|---|---|---|---|
| CH4-F06 | `figures/ch4/source_data/CH4-F06_main_model_multiseed.csv` | data_ready | 正式 normal20 |
| CH4-F07 | `figures/ch4/source_data/CH4-F07_task_level_results_summary.csv` | data_ready | 正式 normal20（formal_mainline 行）|
| CH4-F08 | `figures/ch4/source_data/CH4-F08_feature_set_comparison.csv` | historical | 旧 seedset10，调参依据 |
| CH4-F09a | `figures/ch4/source_data/CH4-F09a_time_boundary_audit_summary.csv` | historical | 旧协议 |
| CH4-F09b | `figures/ch4/source_data/CH4-F09b_time_window_length_eval_summary.csv` | historical | 旧协议 |
| CH4-F10a | `figures/ch4/source_data/CH4-F10a_ie_type_group_summary.csv` | historical | 旧协议 |
| CH4-F10b | `figures/ch4/source_data/CH4-F10b_nodehold_observability_summary.csv` | historical | 旧协议 |

### 非正式实验（不放主结论）

- node_holdout：泛化压力测试
- model_comparison：模型消融
- lambda sweep / feature ablation：来自旧 seedset10，调参依据
- persistent / mixed / process_diagnosis：legacy

---

## 第5章：布局优化

### 正式协议

```
数据集：ie420_plus_normal20_v1
特征集：raw_plus_residual
lambda_loc：0.5
模型：hydraulic_inverse_deepattn
候选空间：C=50
划分：scenario split
诊断种子：7 / 42 / 123
主预算：N=25
唯一变量：监测节点集合 S + observed mask
```

### 6 种布局方法

| 正式命名 | 层次 | 方法说明 |
|---|---|---|
| Degree | 拓扑规则 | 节点度中心性 |
| Betweenness | 拓扑规则 | 介数中心性 |
| Cand-Obs | 覆盖导向 | 候选可观测性最大化 |
| Two-stage v1 | 覆盖导向 | 两阶段平衡布局 |
| Node-Feedback (val) | 诊断表征 | 诊断反馈学习（scenario val 口径）|
| Embedding-Guided-new | 诊断表征 | 编码器节点嵌入 max-min diversity |

### 正式 N25 主结果（3 seed mean±std, ddof=1）

| 方法 | MRR | Top-1 | Top-3 | Top-5 | Event Top-1 | Event Top-3 | Scene F1 |
|---|---|---|---|---|---|---|---|
| Degree | 0.825±0.037 | 0.719±0.069 | 0.919±0.024 | 0.965±0.016 | 0.768±0.070 | 0.951±0.017 | 0.997±0.005 |
| Betweenness | 0.868±0.009 | 0.772±0.011 | 0.961±0.019 | 0.990±0.009 | 0.785±0.016 | 0.973±0.024 | 0.994±0.010 |
| Cand-Obs | 0.878±0.034 | 0.795±0.053 | 0.951±0.022 | 0.983±0.010 | 0.807±0.044 | 0.979±0.024 | 0.997±0.005 |
| Two-stage v1 | 0.905±0.027 | 0.832±0.043 | 0.974±0.018 | 0.989±0.014 | 0.855±0.024 | 0.984±0.027 | 1.000±0.000 |
| Node-Feedback (val) | 0.896±0.032 | 0.815±0.058 | 0.970±0.013 | 0.996±0.002 | 0.856±0.082 | 0.974±0.032 | 1.000±0.000 |
| Embedding-Guided-new | 0.897±0.017 | 0.818±0.029 | 0.981±0.008 | 0.999±0.002 | 0.828±0.041 | 0.978±0.010 | 0.997±0.005 |

来源：`CH5-EXPT_fixed_protocol_N25_main_table.csv`

### 正式图源

| 数据文件 | 内容 | 状态 |
|---|---|---|
| `CH5-EXPT_fixed_protocol_N25_main_table.csv` | 6 方法 x 3 种子完整指标 | data_ready |
| `CH5-budget_sweep_seed42.csv` | 预算曲线（seed42 单种子）| data_ready |
| `CH5-N25_layout_structure.csv` | 布局结构特征 | data_ready |
| `CH5-N25_hard_candidate_analysis.csv` | 困难候选分析 | data_ready |
| `CH5-N25_by_defect_type_analysis.csv` | I/E 类型分组 | data_ready |
| `CH5-N25_pairwise_jaccard.csv` | 布局 Jaccard 相似度 | data_ready |

### 核心结论

1. 纯拓扑中心性不是诊断任务的最优选择（Degree MRR=0.825）
2. 覆盖邻近并非唯一有效策略（Two-stage 0.905 高于 Cand-Obs 0.878）
3. Embedding-Guided 是正文主方法（MRR 0.897±0.017，三条独立证据）
4. 预算敏感性存在交叉点（N=5 时 EG 占优，N≥10 时 Two-stage 领先）

### 局限性

1. Node-Feedback 训练数据仅 9 组
2. Two-stage v1 利用全部缺陷场景仿真响应
3. 预算曲线仅 seed 42
4. 所有实验在同一管网（128 节点）

---

## 章节图源总览

| 章节 | 正式图源数 | 历史图源 | 待截图 | 待绘图 |
|---|---|---|---|---|
| Ch3 | 6 CSV | 0 | 1 (S01) | F01-F06 的 PNG |
| Ch4 | 2 formal CSV + 5 historical CSV | 已归档至 legacy_old_protocol/ | 1 (S01) | F06,F07 待重绘 |
| Ch5 | 6 CSV | 已归档至 legacy_old_protocol/ 和 legacy_old_pipeline/ | 0 | 主表待绘图 |

---

## 内部索引文件

| 文件 | 用途 |
|---|---|
| `notes/MASTER_PROTOCOL.md` | 本文件 — 唯一口径来源 |
| `notes/evidence_map.md` | 论文结论到数据来源的映射 |
| `notes/section_experiment_map.md` | 小节级实验映射 |
| `ch3_data_generation/plans/CH3_PROTOCOL_FREEZE.md` | 第3章协议冻结 |
| `ch4_diagnosis_model/plans/CH4_PROTOCOL_FREEZE.md` | 第4章协议冻结 |
| `docs/PPT_MATERIAL_HANDOFF_CH3_CH4_CH5.md` | PPT 材料交接 |

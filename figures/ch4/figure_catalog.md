# 第4章图件目录

## 正式证据图（来自 ie420+normal20 正式协议）

### CH4-F06 多 seed 稳定性结果（正式协议，已回填）

源数据：`source_data/CH4-F06_main_model_multiseed.csv`

- 数据来源：Degree_N25_formal，种子 7/42/123，来自 CH5-EXPT_fixed_protocol_N25_main_table.csv
- 协议：ie420+normal20 / degree_N25 / scenario split
- 旧版数据已移至 `legacy_old_protocol/CH4-F06_main_model_multiseed_OLD.csv`

### CH4-F07 IE420+normal20 主诊断结果表

源数据：`source_data/CH4-F07_task_level_results_summary.csv`

- `formal_mainline` 行为正式主结果（seed42, MRR=0.8457）
- `historical_multiseed`、`strict_generalization`、`time_dimension` 行为历史/备查数据

### CH4-F08 模型结构多 seed 对比图（正式协议）

源数据：`source_data/CH4-F08_formal_model_comparison_multiseed_summary.csv`

- 来源：`ie420_plus_normal20_v1 / raw_plus_residual / lambda_loc=0.5 / degree_N25 / scenario split / seeds=7,42,123`
- 用途：展示从纯时序、通用图模型、边关系建模到深层液压注意力模型的结构递进

### CH4-F09b 窗口长度敏感性图（正式协议）

源数据：`source_data/CH4-F09b_formal_time_window_length_eval_summary.csv`

- 来源：正式 normal20 协议，seed42，仅改变输入窗口长度
- 用途：说明输入尺度对检测、排序定位和粗粒度时间恢复的影响

### CH4-F10a I/E 类型分组定位结果图（正式协议）

源数据：`source_data/CH4-F10a_formal_ie_type_group_multiseed_summary.csv`

- 来源：正式 normal20 协议，种子 7/42/123
- 用途：按真实缺陷类型事后分层统计窗口级和事件级定位表现，不表示自动类型分类

## 历史证据图（来自旧 seedset10 数据集或旧协议）

> 以下图源均来自 `ie420_plus_normal_multibaseline_v1_seedset10` 或旧 scenario split 协议，
> 不属于正式 `ie420_plus_normal20_v1` 协议。保留为调参依据记录或答辩备查。

### CH4-F08h 特征组合对照结果图（历史）

源数据：`source_data/CH4-F08_feature_set_comparison.csv`

- 来源：seedset10 数据集，非正式 normal20 协议
- 用途：历史调参依据（raw vs residual vs combined 选择依据）

### CH4-F09a 场景级时间边界审查图（历史）

源数据：`source_data/CH4-F09a_time_boundary_audit_summary.csv`

- 来源：旧协议数据
- 用途：备答或正文小节

### CH4-F10b 可观测性分析图（历史）

源数据：`source_data/CH4-F10b_nodehold_observability_summary.csv`

- 来源：旧协议数据
- 用途：候选节点机制备查

## 示意图（无数据来源争议）

| 图号 | 图名 | 状态 |
|---|---|---|
| CH4-F00 | 第4章全过程诊断主线图 | diagrams/ 下，可直接使用 |
| CH4-F01 | 连续场景滑动窗口与场景级聚合示意图 | diagrams/ 下，可直接使用 |
| CH4-F02 | V/S/C/D 节点集合关系图 | diagrams/ 下，可直接使用 |
| CH4-F03 | time-gated 场景与滑动窗口标签图 | diagrams/ 下，可直接使用 |
| CH4-F04 | 模型输出头到评价指标计算链条图 | diagrams/ 下，可直接使用 |
| CH4-F05 | 模型结构示意图 | diagrams/ 下，可直接使用 |
| CH4-F11 | 第4章到第5章衔接图 | diagrams/ 下，可直接使用 |

## 补充图

| 图号 | 图名 | 状态 |
|---|---|---|
| CH4-F12 | scenario split 与 node_holdout 泛化边界图 | 备答/正文附图 |
| CH4-S01 | 监测节点与候选节点空间分布截图 | 等待人工截图 |

## 旧版数据归档

`legacy_old_protocol/` 目录下保存已替换的旧版数据：
- `CH4-F06_main_model_multiseed_OLD.csv` — 旧协议多 seed 数据
- `CH4-F09b_time_window_length_eval_summary.csv` — 旧协议窗口长度结果
- `CH4-F10a_ie_type_group_summary.csv` — 旧协议 I/E 分组结果

## 需要你截图的图

详见 [screenshot_request_list.md](E:\11.16\thesis_writing_repo\figures\screenshot_request_list.md)。

## image gen 备选图

详见 [imagegen_prompts.md](E:\11.16\thesis_writing_repo\figures\imagegen_prompts.md)。

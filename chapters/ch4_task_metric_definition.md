# 第4章任务定义与评估指标说明

本文档用于统一第4章“任务链、标签、指标和结果文件”的口径。正文中可择要引用，本文件更适合作为写作备查、PPT 备注和答辩问答依据。

## 1. 总体任务链

第4章面向连续 I/E 缺陷场景，采用如下诊断链：

```text
IE420 连续缺陷场景
→ 滑动窗口样本构建
→ 窗口级诊断证据提取
→ 场景级活跃期定位
→ 场景级空间定位
→ 场景级综合诊断
→ 泛化边界与可观测性分析
```

该链条的核心不是把所有问题都混成一个指标，而是分层回答三个工程问题：

| 问题 | 对应任务 | 输出 |
|---|---|---|
| 是否存在缺陷响应 | 窗口级 active 识别 | `p_active(t)` |
| 缺陷大致发生在哪段时间 | 场景级活跃期定位 | 预测 active 时间段 |
| 缺陷更可能位于哪里 | 窗口级/场景级节点定位 | 候选节点 Top-K |

其中，窗口级 active 识别是证据提取任务；场景级活跃期定位才对应“缺陷大致发生时间段”的评价；场景级空间定位才对应最终候选节点排查清单。

## 2. 数据、标签与输入协议

### 2.1 数据来源

正式数据为第3章生成的 IE420 time-gated 连续缺陷场景。time-gated 表示每个缺陷场景具有 `start_hour` 和 `duration_h`，缺陷只在场景内某一时间段激活。

### 2.2 滑动窗口

正式空间定位基线使用：

| 参数 | 数值 | 含义 |
|---|---:|---|
| sampling interval | 10 min | 原始时序采样间隔 |
| `sequence_length` | 36 | 每个输入窗口约 6 h |
| `window_stride` | 6 | 每约 1 h 形成一个窗口判断点 |

窗口长度影响实验另外比较 `sequence_length=12/18/24/36`，对应约 2h/3h/4h/6h，`window_stride` 均固定为 6。

### 2.3 标签

| 标签 | 来源 | 用途 |
|---|---|---|
| `active_label` | 窗口与真实 active 时段的 overlap ratio | 训练窗口级 active 识别 |
| `target_node_idx` | 缺陷矩阵中的真实缺陷节点 | 训练和评价节点定位 |
| `start_hour` | 缺陷矩阵 | 场景级活跃期起点评价 |
| `duration_h` | 缺陷矩阵 | 场景级活跃区间评价 |
| `defect_type` | 缺陷矩阵中的 I/E 类型 | I/E 分组统计分析 |

### 2.4 输入协议

正式训练入口为：

`E:\11.16\script2_new\scripts\train_privileged_teacher_student.py`

正式协议为 full-graph sparse-observation：

- 保留 128 节点完整拓扑；
- 保留 observed mask，使模型知道哪些节点有传感器；
- 非观测节点的节点特征不作为可见动态观测；
- 定位输出限制在 50 个候选缺陷节点空间。

## 3. 任务与指标

### 3.0 模型输出头到评价指标的计算链条

第4章模型前向输出包含三个头：

| 输出头 | 张量含义 | 直接解释 | 当前正式用途 |
|---|---|---|---|
| `logits_has_defect` | 图级/窗口级二分类 logits | 当前窗口是否存在缺陷活跃响应 | active 识别、场景级活跃期定位 |
| `logits_node` | 节点级二分类 logits | 每个节点作为缺陷节点的得分 | 窗口级节点定位、场景级空间定位 |
| `logits_defect_type` | 图级三分类 logits | 缺陷类型相关输出 | 当前不进入正式主指标，仅保留为结构输出 |

三个输出头并不是分别对应三个完整论文任务。正式任务链主要使用前两个输出头：

```text
logits_has_defect
→ softmax 得到 p_active(t)
→ 窗口级 active 识别
→ 按 scenario_id 和窗口时间排序
→ 场景级活跃期定位
→ onset error / ±k窗口命中 / interval IoU

logits_node
→ 取缺陷类 logit 或 softmax 分数作为 node_scores(t)
→ candidate_mask 限制到 C=50 候选节点
→ 窗口级 MRR / Top-K
→ 在场景内聚合窗口 node_scores(t)
→ Event Top-K / scene-level Top-K
```

`logits_defect_type` 的代码输出维度为 3，可对应类型相关表征；但正式训练入口中 `lambda_type=0.0`，类型头不作为正式监督损失。因此，第4章正文不把 I/E 类型自动分类写成已完成任务。当前 I/E 结果来自按真实 `defect_type` 对定位指标做分组统计，而不是根据 `logits_defect_type` 评价分类准确率。

#### 3.0.1 `logits_has_defect` 如何得到 active 与时间段指标

对每个窗口，模型输出 `logits_has_defect=[logit_inactive, logit_active]`。通过 softmax 得到：

```text
p_active(t) = softmax(logits_has_defect)[active_class]
```

窗口级 active 识别的计算方式为：

```text
pred_active(t) = 1, if p_active(t) >= threshold
pred_active(t) = 0, otherwise
```

其中 threshold 通常取 0.5。将 `pred_active(t)` 与窗口真实 `active_label` 比较，得到 Active Accuracy、Active Recall 等窗口级指标。

场景级活跃期定位的计算方式为：

1. 按 `scenario_id` 对窗口分组。
2. 在每个场景内按 `window_start_time` 排序。
3. 得到该场景的 `p_active(t)` 时间序列。
4. 根据阈值和连续窗口规则得到预测 active 区间。
5. 将预测 active 区间与真实 `start_hour`、`duration_h` 对应的 active 区间比较。

由此得到：

| 指标 | 计算来源 | 含义 |
|---|---|---|
| `onset_error_hours_mean` | 预测起点 vs 真实起点 | 平均起点误差 |
| `onset_accuracy_within_1_window` | 起点误差是否小于等于 1 个窗口步长 | 较严格起点命中 |
| `onset_accuracy_within_2_windows` | 起点误差是否小于等于 2 个窗口步长 | 中等宽松起点命中 |
| `onset_accuracy_within_3_windows` | 起点误差是否小于等于 3 个窗口步长 | 粗粒度起点命中 |
| `active_interval_iou_mean` | 预测 active 区间与真实 active 区间 | 时间段整体重叠程度 |
| `duration_error_hours_mean` | 预测持续时间 vs 真实持续时间 | 持续时间误差 |

因此，`logits_has_defect` 的作用不仅是回答“这个窗口有没有缺陷”，也为“整条场景中缺陷大致发生在哪段时间”提供时间证据。

#### 3.0.2 `logits_node` 如何得到节点定位指标

对每个窗口，模型输出 `logits_node`，形状可理解为：

```text
[batch_size, num_nodes, 2]
```

其中第 2 类通常表示“该节点为缺陷节点”的分数。评价时取：

```text
node_scores(t, i) = logits_node[t, i, defect_class]
```

再使用 `candidate_mask` 将排序空间限制到 50 个候选节点 `C`：

```text
只在 C=50 候选节点内排序 node_scores(t, i)
```

窗口级节点定位指标计算方式为：

1. 仅对真实 active 窗口评价节点定位。
2. 在 50 个候选节点内按 `node_scores(t, i)` 从高到低排序。
3. 找到真实缺陷节点 `target_node_idx` 的排名。
4. 根据排名计算 MRR、Top-1、Top-3、Top-5。

对应关系为：

| 指标 | 计算方式 | 工程含义 |
|---|---|---|
| MRR | 真实节点排名倒数的平均值 | 排序整体质量 |
| Top-1 | 真实节点排名是否为第 1 | 精确定位 |
| Top-3 | 真实节点是否进入前 3 | 小范围排查 |
| Top-5 | 真实节点是否进入前 5 | 候选清单可用性 |

场景级空间定位进一步将同一 `scenario_id` 下多个窗口的 `node_scores(t)` 聚合：

```text
scene_score(i) = aggregate_t node_scores(t, i)
```

聚合窗口可以有两种来源：

| 聚合窗口 | 来源 | 指标含义 |
|---|---|---|
| 真实 active 窗口 | 使用标签确定 active 窗口 | 衡量空间定位能力，即 Event Top-K |
| 预测 active 窗口 | 使用 `p_active(t)` 预测 active 区间 | 衡量完整综合诊断能力 |

使用真实 active 窗口聚合时，得到 Event Top-1、Event Top-3、Event Top-5，是第4章空间定位主结果。使用预测 active 窗口聚合时，得到 predicted-active scene Top-K，同时受到时间段定位和节点分数聚合影响，作为综合诊断审查指标。

#### 3.0.3 `logits_defect_type` 的当前作用

模型结构中存在 `logits_defect_type`，可输出图级三分类类型相关 logits。代码层面该头可以服务于 I/E/P 类型相关建模或 type-conditioned node head。

但当前正式训练配置中：

```text
lambda_type = 0.0
```

这意味着类型头不参与正式类型分类监督损失，第4章也没有以 `logits_defect_type` 计算 Type Accuracy、Type F1 等正式分类指标。因此，当前论文中涉及 I/E 的结果应表述为：

```text
按真实 I/E 类型对节点定位指标进行分组统计。
```

而不应表述为：

```text
模型完成了 I/E 类型分类。
```

如果后续要把 I/E 类型判断作为正式任务，需要补充：

1. 启用类型分类损失，例如设置 `lambda_type > 0`。
2. 明确类型标签空间，例如 I/E 二分类，或 baseline/I/E 三分类。
3. 报告 Type Accuracy、Macro-F1、I/E 混淆矩阵。
4. 说明类型判断与节点定位之间是并行多任务还是两阶段诊断。

### 3.1 窗口级 active 识别

任务问题：给定一个滑动窗口，判断该窗口是否存在缺陷活跃响应。

输入：一个窗口的稀疏观测时空图。

输出：`p_active(t)` 或 active/inactive 分类结果。

主要标签：`active_label`。

主要指标：

| 指标 | 含义 | 论文用途 |
|---|---|---|
| Active Accuracy | 窗口 active/inactive 分类准确率 | 说明窗口证据提取能力 |
| Active Recall | 真实 active 窗口被识别出的比例 | 说明缺陷响应覆盖能力 |
| Active-period Recall | 从过程角度统计 active 阶段覆盖情况 | 支撑后续时间和空间聚合 |

对应代码：

- `E:\11.16\script2_new\utils\evaluation.py`
- `E:\11.16\script2_new\scripts\train_privileged_teacher_student.py`

对应结果：

- `E:\11.16\script2_new\outputs\reports\last_run_metrics_*.json`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv`

### 3.2 窗口级节点定位

任务问题：给定一个 active 窗口，在 50 个候选节点中判断真实缺陷节点的排序位置。

输入：active 窗口的模型节点分数 `node_scores(t)`。

输出：候选节点排序。

主要标签：`target_node_idx`。

主要指标：

| 指标 | 含义 | 论文用途 |
|---|---|---|
| MRR | 真实节点排名倒数的平均值 | 衡量整体排序质量 |
| Top-1 | 真实节点是否排第 1 | 衡量精确定位能力 |
| Top-3 | 真实节点是否进入前 3 | 衡量小范围排查能力 |
| Top-5 | 真实节点是否进入前 5 | 衡量工程候选清单可用性 |

对应代码：

- `E:\11.16\script2_new\utils\evaluation.py`

对应结果：

- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_summary.csv`

### 3.3 场景级活跃期定位

任务问题：给定一条完整缺陷场景，判断缺陷大致发生在哪段时间。

输入：同一 `scenario_id` 下按时间排序的窗口级 `p_active(t)`。

输出：预测 active 时间段。

主要标签：`start_hour` 和 `duration_h`。

推荐正文指标：

| 指标 | 含义 | 推荐程度 |
|---|---|---|
| `onset_error_hours_mean` | 预测起点与真实起点的平均小时误差 | 主文 |
| `onset_accuracy_within_1_window` | 起点落在真实起点 ±1 个窗口步长内 | 主文 |
| `onset_accuracy_within_2_windows` | 起点落在真实起点 ±2 个窗口步长内 | 主文或补充 |
| `onset_accuracy_within_3_windows` | 起点落在真实起点 ±3 个窗口步长内 | 适合粗粒度说明 |
| `active_interval_iou_mean` | 预测 active 区间与真实区间的 IoU | 主文 |

附表或备答指标：

| 指标 | 含义 |
|---|---|
| `duration_error_hours_mean` | 预测持续时间与真实持续时间误差 |
| `false_alarm_before_start_rate` | 真实开始前提前报警比例 |
| `missed_detection_rate` | 未检测到 active 区间的比例 |

注意：场景级活跃期定位不是分钟级起止时间回归。本章按约 1 h 的窗口步长进行粗粒度评价。由于缺陷矩阵中最短持续时间约为 6 h，`±3` 窗口可作为宽松但有工程意义的时间段命中指标。

对应代码：

- `E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py`
- `E:\11.16\script2_new\scripts\summarize_time_window_length_eval.py`

对应结果：

- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\CH4_TIME_WINDOW_LENGTH_EVAL_SUMMARY.md`

### 3.4 场景级空间定位

任务问题：给定一条缺陷场景，最终能否把真实缺陷节点排进候选节点 Top-K。

输入：同一 `scenario_id` 下的窗口级 `node_scores(t)`。

输出：场景级候选节点排序。

主要标签：真实缺陷节点。

主要指标：

| 指标 | 含义 | 说明 |
|---|---|---|
| Event Top-1 | 真实节点是否排入事件级 Top-1 | 场景级精确定位 |
| Event Top-3 | 真实节点是否排入事件级 Top-3 | 小范围排查 |
| Event Top-5 | 真实节点是否排入事件级 Top-5 | 工程候选清单 |

需要区分两种口径：

| 口径 | 含义 | 论文位置 |
|---|---|---|
| true active 聚合 | 使用真实 active 窗口聚合节点分数 | 空间定位主结果 |
| predicted active 聚合 | 使用预测 active 时间段聚合节点分数 | 综合诊断审查 |

true active 聚合主要衡量空间定位能力；predicted active 聚合同时受时间段选择和节点分数融合影响，更严格但不适合作为唯一主指标。

对应代码：

- true active 聚合：`E:\11.16\script2_new\utils\evaluation.py`
- predicted active 聚合：`E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py`

对应结果：

- true active 聚合：`E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv`
- predicted active 聚合：`E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv`

### 3.5 场景级综合诊断

任务问题：是否能够同时给出较合理的缺陷时间段和候选节点排序。

输入：预测 active 时间段和该时间段内聚合的节点分数。

输出：缺陷大致时间段 + 候选节点 Top-K。

指标示例：

| 指标 | 含义 | 论文用途 |
|---|---|---|
| `onset_within_1_window_and_node_top3` | 起点在 ±1 窗口内且节点进入 Top-3 | 严格综合审查 |
| `onset_within_2_windows_and_node_top5` | 起点在 ±2 窗口内且节点进入 Top-5 | 综合诊断审查 |
| `onset_within_3_windows_and_node_top5` | 起点在 ±3 窗口内且节点进入 Top-5 | 粗粒度综合诊断 |

这类指标更接近完整工程流程，但会同时受到 active 段预测、窗口长度、节点分数聚合方式影响。因此正文可作为补充说明，不建议替代主实验中的 MRR、Top-K 和 Event Top-K。

### 3.6 I/E 分组分析

任务问题：I 类和 E 类缺陷的定位难度是否存在差异。

输入：测试集中真实 `defect_type` 与定位结果。

输出：I/E 两组的 MRR、Top-K。

注意：该任务不是 I/E 自动分类，而是按真实类型进行分组统计。

对应结果：

- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_ie_type_group_summary.csv`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_ie_type_group.png`

### 3.7 泛化边界与可观测性分析

任务问题：模型在哪些空间条件下表现更好，在哪些条件下容易下降。

分析维度：

| 分析 | 含义 | 结果用途 |
|---|---|---|
| `scenario split` vs `node_holdout` | 新场景泛化与未见节点泛化对比 | 说明泛化边界 |
| direct / near / far | 候选节点与监测节点拓扑距离分层 | 说明可观测性影响 |
| candidate mechanism | V/S/C/D 集合关系 | 说明候选空间设计 |

对应结果：

- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_nodehold_observability_summary.csv`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_candidate_observability_counts.csv`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_split_vs_nodehold.png`
- `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_observability_analysis.png`

## 4. 正文和 PPT 推荐呈现顺序

正文和 PPT 的顺序应与任务链一致，但结果呈现要突出主贡献：

1. 先讲连续场景如何切成滑动窗口。
2. 再讲模型如何输出窗口级 `p_active(t)` 和 `node_scores(t)`。
3. 然后讲窗口级 active 与节点定位结果，证明窗口证据有效。
4. 接着讲场景级 Event Top-K，证明完整场景可以形成可靠候选节点清单。
5. 再讲窗口长度实验，说明时间段定位与空间定位存在尺度权衡。
6. 最后讲模型对比、I/E 分组、node_holdout 和可观测性分析。

这样安排的好处是：技术流程符合“先时间证据、再空间定位”的逻辑，主实验又不会被 6h 窗口的时间边界误差喧宾夺主。

## 5. 第5章应固定的第4章版本

第5章布局优化需要固定第4章空间诊断基线，建议采用：

| 项目 | 固定设置 |
|---|---|
| 数据 | IE420 time-gated |
| 图空间 | `V=128` |
| 监测布局 | `degree N25` 作为基线 |
| 候选定位空间 | `C=50` |
| 模型 | `hydraulic_inverse_deepattn` |
| 输入协议 | full-graph sparse-observation |
| 窗口 | `sequence_length=36`，约 6 h |
| 步长 | `window_stride=6`，约 1 h |
| 主指标 | MRR、Top-1、Top-3、Top-5、Event Top-K |
| 支撑指标 | Active Recall、I/E 分组、可观测性分层 |

2h/3h 窗口实验可作为第4章时间段定位补充分析，不建议作为第5章布局优化的主基线。

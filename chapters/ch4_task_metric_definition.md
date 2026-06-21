# 第4章诊断任务、输出与评价指标统一说明

本文档用于固定第4章及第5章沿用的诊断任务、模型输出、聚合方式和评价指标。正式正文以 `ch4_model_diagnosis.md` 为准，本文件作为公式、表格、图注和答辩问答的统一口径。

## 1. 正式实验协议

```text
dataset      = ie420_plus_normal20_v1
defect matrix= defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
layout       = degree_N25
feature_set  = raw_plus_residual
split        = scenario split
lambda_loc   = 0.5
window       = sequence_length 36 / stride 6
seeds        = 7, 42, 123
main model   = DeepAttn-L3
```

`ie420_plus_normal20_v1` 共包含 441 个场景：1 个 reference、420 个 time-gated I/E 缺陷场景和 20 个 normal 扰动场景。reference 用于 residual 对齐；normal20 用于描述无缺陷波动并约束误报；IE420 用于提供缺陷类型、位置和 active 区间标签。不得将 persistent、fulltime、legacy 或 seedset10 数据混入正式结果。

## 2. 节点集合与输入边界

| 集合 | 含义 | 数量 | 作用 |
|---|---|---:|---|
| \(V\) | 全网节点集合 | 128 | 保留完整管网拓扑 |
| \(S\) | 监测节点集合 | 25 | 提供可见动态观测 |
| \(C\) | 缺陷节点定位集合 | 50 | 模型空间排序范围 |
| \(d\) | 单个场景的真实缺陷节点 | 1 | 空间定位标签 |

正式输入采用 full-graph sparse-observation 协议。全网拓扑始终保留，仅 \(S\) 中节点的动态特征可见，其他节点通过 observed mask 标记为未观测。第4章固定 Degree-N25；第5章固定诊断模型与数据协议，仅改变 \(S\)。

## 3. 正式任务链

```text
连续场景
-> 滑动窗口
-> p_active(t) + node_scores(t)
-> 场景级报警与活跃区间
-> 场景级缺陷节点排序
```

第4章的直接模型输出只有两类正式诊断证据：

| 窗口输出 | 含义 | 后续用途 |
|---|---|---|
| `p_active(t)` | 当前窗口存在缺陷活跃响应的概率 | 窗口识别、场景报警、active 区间恢复 |
| `node_scores(t)` | 当前窗口内各缺陷节点的定位分数 | 窗口排序、事件级节点排序 |

场景级报警、时间定位和 Event Top-K 均为窗口输出的聚合结果，不是三个独立模型头。

模型代码保留 `logits_defect_type`，但正式训练设置 `lambda_type=0.0`。因此，本文没有完成 I/E 自动分类任务；I/E 结果仅表示按真实类型对定位指标进行分组统计。

## 4. 滑动窗口与标签

采样间隔为 10 min。正式窗口 `sequence_length=36`，覆盖约 6 h；`window_stride=6`，约每 1 h 产生一个窗口判断点。

| 标签 | 来源 | 用途 |
|---|---|---|
| `active_label` | 窗口与真实 active 区间的重叠关系 | active 识别 |
| `target_node_idx` | 缺陷矩阵中的真实缺陷节点 | 节点定位 |
| `start_hour` | 正式缺陷矩阵 | 起点误差 |
| `duration_h` | 正式缺陷矩阵 | 区间 IoU |
| `defect_type` | 正式缺陷矩阵 | I/E 补充分组 |

48 h 是统一观察窗口，不表示缺陷持续 48 h。缺陷仅在 `[start_hour, start_hour + duration_h)` 内生效。

## 5. 窗口级评价

### 5.1 Active 识别

由 `logits_has_defect` 经 softmax 得到：

\[
p_{\mathrm{active}}(t)
=\operatorname{softmax}(\mathbf{z}^{active}_t)_1.
\]

主要指标：

- Active F1：active 与 inactive 窗口的综合识别质量；
- Active Recall：真实 active 窗口的检出率；
- Normal Window FPR：normal20 窗口被误判为 active 的比例。

Normal Window FPR 是误报控制指标，不与 Scene FPR 混用。

### 5.2 缺陷节点排序

对 50 个缺陷节点的 `node_scores(t)` 降序排列，设真实节点在第 \(i\) 个 active 窗口中的排名为 \(r_i\)，则：

\[
\mathrm{MRR}
=\frac{1}{N_{\mathrm{active}}}
\sum_{i=1}^{N_{\mathrm{active}}}\frac{1}{r_i}.
\]

| 指标 | 含义 | 正文地位 |
|---|---|---|
| MRR | 真实节点平均前位排序质量 | 核心指标 |
| Top-1 | 真实节点位于首位的比例 | 核心指标 |
| Top-3 | 真实节点进入前三的比例 | 核心指标 |
| Top-5 | 真实节点进入前五的比例 | 补充；部分实验接近饱和 |

## 6. 场景级评价

### 6.1 场景报警

将同一 `scenario_id` 的窗口概率按 `top-k mean` 等规则聚合得到场景分数，用于计算 Scene Recall、Scene FPR 和 Scene F1。该组指标评价完整场景是否需要报警。

### 6.2 活跃区间恢复

将窗口按时间排序，以 `p_active(t)` 阈值和连续窗口规则恢复预测区间。主要指标为：

| 指标 | 定义 | 含义 |
|---|---|---|
| Onset error | 预测起点与真实起点的小时差 | 起点定位误差 |
| Onset within \(k\) strides | 起点误差是否不超过 \(k\) 个步长 | 粗粒度起点命中 |
| Active IoU | 预测区间与真实区间交并比 | 整体时间覆盖质量 |

时间定位按约 1 h 步长评价，不等同于分钟级起止时间回归。

### 6.3 事件级空间定位

将同一场景内窗口节点分数聚合后计算 Event Top-1、Event Top-3 和 Event Top-5。

需要区分：

- **true-active 聚合**：使用真实 active 窗口，主要评价空间定位能力；
- **predicted-active 聚合**：使用预测 active 区间，同时受时间恢复和空间排序影响，属于综合诊断审查。

第4章空间主结果优先使用 true-active Event Top-K。predicted-active 指标不替代 MRR 和窗口 Top-K。

## 7. 指标与科学问题对应关系

| 科学问题 | 首选指标 | 不宜作为核心指标 |
|---|---|---|
| 正常扰动是否造成误报 | Normal Window FPR、Scene FPR | Top-5 |
| 真实缺陷节点是否排在前列 | MRR、Top-1 | Scene F1 |
| 工程排查清单是否可用 | Top-3、Event Top-3 | 接近饱和的 Top-5 |
| active 起点是否准确 | Onset error | Active Accuracy |
| active 区间是否覆盖完整 | Active IoU | 单一窗口 Recall |
| 模型是否稳定 | 多 seed mean ± std | 单 seed 最优值 |

## 8. 正式模型验证结构

第4章模型有效性由三组证据共同建立：

1. **分组模型对比**：纯时序、普通图、单层路径与 DeepAttn-L3；
2. **深度消融**：L1-L4，验证多层聚合与三层饱和点；
3. **路径先验消融**：Content-only、Distance-only、Full path prior。

Distance-only 仅有 seed42，用作机制探针。不得据此形成多 seed 稳定性结论。

## 9. 补充分析边界

- I/E 分组受类型样本构成影响，仅作补充观察；
- node-holdout 是未见缺陷节点压力测试，不替代 scenario split 主结果；
- 真实缺陷节点到最近监测节点的 hop 或管网距离用于关联分析，不将距离直接等同于水力可观测性；
- 单场景时间或空间证据图用于解释诊断过程，不代表全部场景。

## 10. 当前正式文件

| 内容 | 文件 |
|---|---|
| 第4章正文 | `chapters/ch4_model_diagnosis.md` |
| 第4章证据矩阵 | `chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md` |
| 第4/5章结果逻辑 | `chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md` |
| 第4章图件索引 | `figures/ch4/generated_results/CH4_OFFICIAL_FIGURE_INDEX.md` |
| 模型消融汇总 | `figures/ch4/source_data/CH4-F11_method_ablation_summary.csv` |

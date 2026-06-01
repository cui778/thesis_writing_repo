# 第5章 P0 结果审查报告

本报告只审查已经整理出的 P0 结果数据，不新增绘图、不启动重训。审查对象为 `figures/ch5/source_data` 下的 P0 CSV 文件。

## 1. 数据口径

本轮 P0 数据固定以下口径：

- 方法：`Degree`、`Cand-Obs`、`Two-stage v1`、`v0_2 clean`、`v2_2 clean`。
- 种子：`7 / 42 / 123`。
- 预算：`N=25`。
- 数据来源：正式 clean 主线 raw metrics JSON、缺陷矩阵、候选可观测性分层表。
- 输出位置：`E:\11.16\thesis_writing_repo\figures\ch5\source_data`。

注意：不同 seed 的 scenario split 场景集合并不完全相同，因此 raw 场景表中 union 后共有 165 个不同 `scenario_id`；每个方法、每个 seed 仍为 63 个测试场景。

## 2. 主结果可写结论

从 `CH5-P0_main_metrics_from_raw_json_all_seeds.csv` 看，5 个方法的跨 seed 平均表现为：

| 方法 | window MRR | window Top-1 | event MRR | event Top-1 | event Top-3 | event Top-5 |
|---|---:|---:|---:|---:|---:|---:|
| Degree | 0.7778 | 0.6426 | 0.7716 | 0.6329 | 0.9041 | 0.9511 |
| Cand-Obs | 0.8664 | 0.7827 | 0.8628 | 0.7791 | 0.9327 | 0.9684 |
| Two-stage v1 | 0.8715 | 0.7811 | 0.8611 | 0.7666 | 0.9489 | 0.9831 |
| v0_2 clean | 0.8658 | 0.7725 | 0.8610 | 0.7660 | 0.9551 | 0.9924 |
| v2_2 clean | 0.8856 | 0.8070 | 0.8773 | 0.7944 | 0.9631 | 0.9911 |

可以写：

- 相比单纯拓扑度数布局 `Degree`，任务相关布局均显著提升空间定位表现。
- `v2_2 clean` 在主协议下取得最高的 window MRR、window Top-1、event MRR、event Top-1 和 event Top-3。
- `v0_2 clean` 的 event Top-5 最高，说明节点级反馈学习对候选范围收敛也有价值。
- `Cand-Obs`、`Two-stage v1`、`v0_2 clean` 的均值接近，说明第五章不能只写“某一个方法绝对碾压”，更适合写成“从人工规则到诊断反馈的任务对齐改进”。

不建议写：

- 不建议说 `v0_2 clean` 全面优于 `Cand-Obs` 或 `Two-stage v1`。从均值看三者差距很小。
- 不建议说 `v2_2 clean` 在所有场景类型上都最优。后面的 hard candidates 结果不支持这个说法。
- 不建议把 `Top-5` 的接近满分写成强创新点，因为多种方法在 Top-5 上都已经较高。

推荐图形：

- 主图：横向 dot + error bar，展示 MRR、Top-1、event Top-1 或 event Top-K。
- 备选图：方法排名 slope chart，连接 Degree 到学习型方法，突出“任务对齐”而不是单点冠军。
- 附图：场景级 MRR 分布图，用于展示均值背后的尾部差异。

## 3. direct / near / far 分组审查

从 `CH5-P0_direct_near_far_performance_summary.csv` 看，候选可观测性分组具有明显解释价值。

关键现象：

- `Degree` 在 far 组表现最低，far 组 MRR 约为 0.6492，Top-1 约为 0.4133。
- `Two-stage v1` 在 far 组 MRR 约为 0.8614，是 far 组中最强结果。
- `v0_2 clean` 在 far 组 MRR 约为 0.8343，明显高于 `Degree`，但低于 `Two-stage v1`。
- `v2_2 clean` 总体主结果最强，但 far 组 MRR 约为 0.8033，低于 `Two-stage v1` 和 `v0_2 clean`。
- `v2_2 clean` 在 direct 与 near 组表现很好，尤其 near 组 MRR 约为 0.9115。

可以写：

- direct / near / far 分组揭示了布局方法的作用机制：人工拓扑布局在远离监测点的候选上存在明显短板。
- `Two-stage v1` 对 far 组更稳，说明显式覆盖与空间平衡约束对难观测候选有帮助。
- `v2_2 clean` 的优势更体现在总体排序质量和 direct / near 候选上，而不是 hard/far 场景的绝对最优。
- 这组结果可以支撑第五章的“人工规则 → 任务驱动 → 诊断反馈学习”的递进叙事，但需要承认不同方法改善的候选类型不同。

不建议写：

- 不建议把 `v2_2 clean` 写成“解决 far 盲区”的唯一方法。
- 不建议把 direct / near / far 直接解释为每个布局自己的监测距离结构；当前分组来自候选可观测性分层表，更适合作为候选难度分组。

推荐图形：

- 主图：direct / near / far 三个小面板，每个面板用 dot plot 比较方法 MRR 或 Top-1。
- 不推荐继续使用拥挤的 grouped bar，因为方法多、组别多，PPT 上不容易读。
- 如果想突出机制，可画“Degree 到 Two-stage / v0_2 / v2_2 的 far 组增益”差值图。

## 4. hard candidates 审查

从 `CH5-P0_hard_candidates_performance_summary.csv` 看，hard candidates 结果非常适合作为边界与机制分析，而不是简单胜负排名。

hard group 定义：

- 当前 hard candidates 来自候选可观测性分层中的 `far` 候选。
- 每个 seed 中 hard 场景约 20 个，other 场景约 43 个。

关键结果：

| 方法 | other MRR | hard MRR | other Top-1 | hard Top-1 |
|---|---:|---:|---:|---:|
| Degree | 0.8274 | 0.6492 | 0.7334 | 0.4133 |
| Cand-Obs | 0.8708 | 0.8469 | 0.7948 | 0.7471 |
| Two-stage v1 | 0.8626 | 0.8614 | 0.7655 | 0.7755 |
| v0_2 clean | 0.8755 | 0.8343 | 0.7873 | 0.7264 |
| v2_2 clean | 0.9132 | 0.8033 | 0.8506 | 0.6781 |

可以写：

- `Degree` 在 hard candidates 上下降最明显，说明单纯拓扑中心性并不能保证缺陷定位可观测性。
- `Two-stage v1` 在 hard candidates 上最稳，hard MRR 几乎不低于 other 组，说明显式覆盖和平衡策略对困难候选有效。
- `v2_2 clean` 总体表现最好，但在 hard candidates 上存在性能回落，说明代理驱动布局仍可能偏向总体收益，而非专门保护尾部困难场景。
- hard candidates 可以作为第五章的“可观测性边界”分析，而不是推翻学习型主线。

不建议写：

- 不建议说学习型布局在 hard candidates 上全面最优。
- 不建议把 hard candidates 写成主排名指标；它更适合放在 5.6 的机制与边界分析。

推荐图形：

- 主图：hard vs other paired gap plot，每个方法一条线，显示 hard 组相对 other 组的下降幅度。
- 备选图：只画 hard candidates 的 MRR / Top-1 排名，作为附图。
- 若用于 PPT，建议突出一句：`v2_2 clean wins overall, Two-stage v1 protects hard candidates better`，中文可写为“代理布局主结果更强，两阶段布局对困难候选更稳”。

## 5. 第5章主线建议

根据 P0 审查，建议第五章不要写成“提出一个唯一最优布局方法”，而写成更稳、更有研究味道的主线：

> 从人工规则选点走向诊断结果反馈指导布点，并进一步分析不同布局机制对整体定位收益与困难候选保护的差异。

这样可以同时容纳：

- `v2_2 clean`：主协议总体最优，代表布局级代理驱动搜索。
- `v0_2 clean`：节点级反馈学习，证明诊断结果可以转化为布点优先级。
- `Two-stage v1`：困难候选保护更稳，作为任务驱动规则基线具有解释价值。
- `Degree`：拓扑基线，提供反差。
- `Cand-Obs`：候选可观测性基线，连接布点结构和定位表现。

## 6. 下一步建议

优先级建议如下：

1. 先基于本报告确定正式图型，不急着画图。
2. 正式图建议先做三张：
   - 主结果图：整体空间定位性能。
   - direct / near / far 分组图：机制解释。
   - hard candidates gap 图：边界与困难场景分析。
3. 图型确认后，再统一美化配色、字体、图例和 PPT 版式。
4. 预算 `N=5/10/15/20/25` 重训放在 P1。它很有价值，但应在 P0 证据链稳定后再做。

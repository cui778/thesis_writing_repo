# 第5章实验规划与完成状态

## 固定协议

```
dataset = IE420 + normal20
teacher_subdir = ie420_plus_normal20_v1
feature_set = raw_plus_residual
lambda_loc = 0.5
model = hydraulic_inverse_deepattn
split = scenario
diagnosis_seed = 7 / 42 / 123
budget = N25（主表）, N5/N10/N15/N20（预算曲线）
```

## 实验完成状态

所有实验已完成（2026-06-01）。

### 主表：6 方法 × 3 种子 = 18 行

| 方法 | seed 7 | seed 42 | seed 123 | 状态 |
|---|---|---|---|---|
| Degree | ✅ | ✅ | ✅ | 完成 |
| Betweenness | ✅ | ✅ | ✅ | 完成 |
| Cand-Obs | ✅ | ✅ | ✅ | 完成 |
| Two-stage v1 | ✅ | ✅ | ✅ | 完成 |
| Node-Feedback | ✅ | ✅ | ✅ | 完成 |
| Embedding-Guided | ✅ | ✅ | ✅ | 完成 |

### 预算曲线：4 方法 × 5 预算 × seed 42 = 20 行

| 方法 | N5 | N10 | N15 | N20 | N25 |
|---|---|---|---|---|---|
| Degree | ✅ | ✅ | ✅ | ✅ | ✅ |
| Betweenness | ✅ | ✅ | ✅ | ✅ | ✅ |
| Two-stage v1 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Embedding-Guided | ✅ | ✅ | ✅ | ✅ | ✅ |

### 机制分析

| 分析项 | 状态 | 源数据 |
|---|---|---|
| 困难候选分析 | ✅ | CH5-N25_hard_candidate_analysis.csv |
| I/E 缺陷类型分组 | ✅ | CH5-N25_by_defect_type_analysis.csv |
| Jaccard 相似度 | ✅ | CH5-N25_pairwise_jaccard.csv |
| 布局结构指标 | ✅ | CH5-N25_layout_structure.csv |

## 源数据文件

| 文件 | 行数 | 用途 |
|---|---|---|
| `CH5-EXPT_fixed_protocol_N25_main_table.csv` | 18 | 主表 |
| `CH5-budget_sweep_seed42.csv` | 20 | 预算曲线 |
| `CH5-N25_hard_candidate_analysis.csv` | 50 | 困难候选 |
| `CH5-N25_by_defect_type_analysis.csv` | 12 | I/E 分组 |
| `CH5-N25_pairwise_jaccard.csv` | 36 | Jaccard 相似度 |
| `CH5-N25_layout_structure.csv` | 6 | 结构指标 |
| `layout_quality_dataset_wide_fixed_normal20_clean_v1.csv` | 9 | NF 训练输入 |

## 正文章节结构

```text
5.1 监测布局优化问题与固定实验协议
5.2 固定诊断协议下的布局评价闭环
5.3 对比方法：拓扑规则、覆盖导向与诊断表征
5.4 不同布局方法的定位性能对比
5.5 预算约束下的性能变化
5.6 机制分析
5.7 本章小结与局限性
```

## 叙事主线

1. 纯拓扑布局仍有优化空间（Degree MRR=0.825，Betweenness 0.868）
2. 覆盖邻近并不是唯一有效策略（Cand-Obs 0.878，Two-stage 0.905）
3. Embedding-Guided 是正文主方法（MRR 0.897±0.017，三条独立证据）
4. 结论落点：诊断表征能够提供不同于拓扑和覆盖规则的布局依据

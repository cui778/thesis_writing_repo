# 技术路线图 S2-SKETCH-EXPLORE 草图清单

## 1. 阶段说明

本阶段仅生成低保真 raster 草图，用于比较结构方向。未执行优劣筛选，未进入正式候选图生成。

生成方式：

```text
内置 image_gen raster generation
每张草图单独生成
```

## 2. 草图文件

| ID | 结构方向 | 文件 |
|---|---|---|
| `SKETCH-A` | 纵向三层章节路线 | `figures/technical_route/s2_sketches/SKETCH-A_vertical-three-layer.png` |
| `SKETCH-B` | 纵向三层，强化第 4 章诊断核心 | `figures/technical_route/s2_sketches/SKETCH-B_diagnosis-core.png` |
| `SKETCH-C` | 纵向三层，强化诊断到布局优化桥梁 | `figures/technical_route/s2_sketches/SKETCH-C_diagnosis-layout-bridge.png` |
| `SKETCH-D` | 左到右数据到决策主线，辅以三层泳道 | `figures/technical_route/s2_sketches/SKETCH-D_horizontal-swimlanes.png` |

## 3. 事实覆盖检查

四张草图均覆盖：

- `SWMM` 基础模型；
- `PySWMM` 批量仿真；
- 正常工况与 `I/E` 缺陷场景；
- 原始特征与 `residual` 派生特征；
- 水力约束时空图诊断；
- 时间编码、空间聚合与水力传播关联；
- 活跃响应与节点评分；
- 场景级聚合；
- 固定布局评价；
- 监测节点布局优化；
- 从拓扑结构布局到诊断信息驱动布局的方法演进；
- 机制分析与最终优化方案。

## 4. 视觉检查

| ID | 检查记录 |
|---|---|
| `SKETCH-A` | 三层纵向结构完整，适合作为章节递进基准方向。 |
| `SKETCH-B` | 第二层占比增加，突出水力传播关联，并加入候选节点到稀疏监测节点的简化传播示意。 |
| `SKETCH-C` | 使用醒目的单向桥梁强调“诊断评价驱动布局优化”。 |
| `SKETCH-D` | 使用横向泳道表达数据到决策路径，保留三阶段含义。 |

说明：

- 当前为低保真探索图，个别文本排版和细节不作为最终交付标准。
- 本阶段不评选草图，不记录推荐排序。
- 正式候选阶段需继续保持短标签，并校核全部中文术语。


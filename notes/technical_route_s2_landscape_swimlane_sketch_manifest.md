# 技术路线图 S2-SKETCH-EXPLORE：横向画布三泳道草图清单

## 1. 阶段边界

本轮仅执行 `S2-SKETCH-EXPLORE`。

- 已生成 4 张独立低保真 raster 草图。
- 未拼接候选板。
- 未执行方向筛选。
- 未进入 `S3-DIRECTION-SELECT`。

本轮替代旧版纵向构图探索，统一采用：

```text
横向画布
+ 三条从左到右排列的竖向泳道
+ 泳道内部自上而下阅读
```

## 2. 事实底座

本轮草图基于：

- `E:\11.16\thesis_writing_repo\notes\technical_route_s0_research_foundation.md`
- `E:\11.16\thesis_writing_repo\notes\technical_route_s1_figure_strategy_landscape_swimlanes.md`

四张草图保持相同事实底座：

```text
第 3 章 SWMM/PySWMM 多场景仿真数据生成
-> 第 4 章 水力约束时空图缺陷诊断
-> 第 5 章 诊断导向监测布局优化
```

图内统一保留：

- `SWMM` 与 `PySWMM`；
- 正常工况与 `I/E 缺陷场景`；
- `residual 派生特征`；
- `水力传播关联建模`；
- `场景级聚合`；
- `固定布局评价`；
- `诊断评价驱动布局优化`；
- `监测节点布局优化`；
- 布局方法演进与机制分析。

## 3. 草图清单

### LSKETCH-A：横向泳道基准方案

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_landscape_swimlane_sketches\LSKETCH-A_landscape-swimlane-baseline.png`

探索重点：

- 三条并排竖向泳道；
- 中间诊断泳道略宽；
- 三章流程密度较均衡；
- 作为横向构图的稳定基准。

### LSKETCH-B：强化诊断核心

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_landscape_swimlane_sketches\LSKETCH-B_diagnosis-core.png`

探索重点：

- 中间泳道显著加宽；
- 将 `水力约束时空图诊断模型` 画为内部机制盒；
- 强化 `水力传播关联建模`；
- 增加简化管网传播示意。

### LSKETCH-C：强化跨泳道交接

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_landscape_swimlane_sketches\LSKETCH-C_cross-lane-handoffs.png`

探索重点：

- 强化蓝灰色交接箭头：
  `residual 特征 -> 稀疏观测时空图输入`；
- 强化橙色交接箭头：
  `固定布局评价 -> 诊断评价驱动布局优化`；
- 检查三章依赖关系是否一眼可读。

### LSKETCH-D：强化布局方法演进

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_landscape_swimlane_sketches\LSKETCH-D_layout-method-progression.png`

探索重点：

- 右侧泳道采用明显的阶梯式方法演进；
- 展示 `拓扑结构布局 -> 诊断导向规则布局 -> 诊断信息驱动布局`；
- 将 `布局性能评价与机制分析` 作为汇聚模块；
- 展示机制分析的紧凑标签。

## 4. S3 比较提示

进入 `S3-DIRECTION-SELECT` 时，重点比较：

1. 三章递进关系是否清晰；
2. `residual` 特征交接是否准确；
3. `水力传播关联建模` 是否足够醒目；
4. 固定布局诊断评价如何驱动右侧优化是否清楚；
5. 右侧方法演进是否紧凑且不挤压全图；
6. 后续正式重绘时箭头落点、文字密度与页面尺度是否容易修订。

本清单不作方向推荐。

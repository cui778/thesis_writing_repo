# 技术路线图 S2-SKETCH-EXPLORE：上横下一纵草图清单

## 1. 阶段边界

本轮仅执行 `S2-SKETCH-EXPLORE`。

- 已生成 4 张独立低保真 raster 草图；
- 未拼接候选板；
- 未执行方向筛选；
- 未进入 `S3-DIRECTION-SELECT`。

本轮草图统一采用：

```text
上层：第 3 章横向数据底座
下层左侧：第 4 章竖向诊断泳道
下层右侧：第 5 章竖向优化泳道
```

## 2. 事实底座

本轮基于：

- `E:\11.16\thesis_writing_repo\notes\technical_route_s0_research_foundation.md`
- `E:\11.16\thesis_writing_repo\notes\technical_route_s1_figure_strategy_top-horizontal_lower-vertical.md`

四张草图均保留：

- `SWMM` 与 `PySWMM`；
- 正常工况与 `I/E 缺陷场景`；
- `residual 派生特征`；
- 稀疏观测时空图输入；
- `水力传播关联建模`；
- `p_active(t)` 与 `node_scores(t)`；
- 场景级聚合；
- 固定布局评价；
- 诊断评价驱动布局优化；
- 监测节点布局优化；
- 布局方法演进与机制分析。

## 3. 草图清单

### TSKETCH-A：均衡基准方案

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_top-horizontal_lower-vertical_sketches\TSKETCH-A_balanced-baseline.png`

探索重点：

- 上层横向数据生成链和下层两泳道比例均衡；
- 上层展示输入汇聚、场景分叉和时序汇聚；
- 左下展示输入汇聚、机制链、双输出和结果分叉；
- 右下展示方法演进与机制分析。

### TSKETCH-B：强化上层数据底座

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_top-horizontal_lower-vertical_sketches\TSKETCH-B_upper-data-foundation.png`

探索重点：

- 上层泳道更高，数据底座更突出；
- 正常工况内部展示 `参照响应` 与 `正常扰动`；
- I/E 场景内部展示 `渗入`、`渗漏` 与 `时间门控`；
- residual 向下交付使用显著蓝灰箭头。

### TSKETCH-C：强化诊断模型内部结构

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_top-horizontal_lower-vertical_sketches\TSKETCH-C_diagnosis-structure.png`

探索重点：

- 左下诊断泳道显著加宽；
- 诊断模型内部使用机制卡片和轻量示意图；
- `水力传播关联建模` 为深绿色视觉锚点；
- 双输出、场景级聚合与三类结果分叉清楚。

### TSKETCH-D：强化诊断到布局优化桥梁

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s2_top-horizontal_lower-vertical_sketches\TSKETCH-D_diagnosis-layout-bridge.png`

探索重点：

- 固定布局诊断验证到监测节点布局优化的橙色桥梁明显；
- 右侧采用三阶阶梯式方法演进；
- 机制分析标签紧凑；
- 各区域均使用较多局部示意图。

## 4. 低保真检查记录

本阶段不筛选方向，仅记录后续比较时需要关注的事项：

1. 上层数据底座已经形成输入汇聚、场景分叉和数据汇聚，不再是单线目录。
2. 左下诊断区已经形成输入汇聚、机制链、双输出、场景级聚合和结果分叉。
3. 右下优化区已经形成多输入汇聚、方法演进和机制分析。
4. 个别草图中，`residual` 向下交付箭头的视觉落点偏右；正式候选应明确落入第 4 章的稀疏观测输入区。
5. 个别草图中，诊断评价桥梁的落点靠近最终输出；正式候选应明确落入 `监测节点布局优化`。
6. 图标数量和文字密度存在差异，后续需要在完整性与论文页面可读性之间取舍。

## 5. S3 比较维度

进入 `S3-DIRECTION-SELECT` 时，重点比较：

1. 上层共享数据底座是否清楚；
2. 上层场景分叉与汇聚是否准确；
3. residual 向下交付是否落入第 4 章输入区；
4. 左下诊断模型内部机制是否完整但不过密；
5. 双输出、场景级聚合和三类结果分叉是否清楚；
6. 固定布局评价到监测节点布局优化的桥梁是否准确；
7. 右侧阶梯式方法演进是否清楚；
8. 后续正式重绘时是否容易修订。

本清单不作方向推荐。

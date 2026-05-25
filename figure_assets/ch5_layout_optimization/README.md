# 第5章图件资产包

本目录用于集中管理第5章“诊断反馈驱动的学习型监测布局”相关图片、重绘数据和 PPT 插图索引。后续 PPT 和正文插图优先引用这里的统一编号，避免同一张图在不同文档中名称不一致。

## 目录结构

- `figure_index.csv`: 总索引，记录图号、类别、PPT 页码、正文小节、来源和状态。
- `ppt_insert_index.md`: 面向 PPT 的插图索引，按幻灯片页码组织。
- `raw_data_catalog.md`: 原始结果数据与生成中间表说明。
- `data/`: 从原始 JSON/CSV 整理出的可重绘中间数据。
- `figures/data_redraw/`: 基于原始结果数据重绘的证据图。
- `figures/generated_schematic/`: 用脚本生成的机制示意图。
- `figures/screenshot_needed/`: 需要人工截图后放入的图片。
- `figures/imagegen_prompted/`: 适合用 imagegen 生成的概念图提示词和后续成图。
- `scripts/`: 图件资产包生成脚本。

## 图件类别

### A. 数据重绘图

由已有原始结果数据生成，属于论文和答辩中的实验性证据图。

当前已生成：

- `F5-D01`: 主协议空间定位表现点图。
- `F5-D02`: 场景级 MRR 分布。
- `F5-D03`: direct / near / far 分组性能。
- `F5-D04`: hard candidates 场景性能。
- `F5-D05`: 预算变化下可观测性结构。
- `F5-D06`: 布局节点集合 Jaccard 相似度。

这类图如果觉得不够美观，优先基于 `data/` 中的中间 CSV 或 `raw_data_catalog.md` 中的原始文件重新设计样式。

### B. 截图类图

这类图需要从 SWMM、GIS、管网可视化脚本或你自己的布局检查界面截图，主要用于展示真实管网背景和监测点落位，不作为量化性能证据。

当前预留：

- `F5-S01`: 管网背景中的监测节点布局截图。

建议截图后保存为：

`figures/screenshot_needed/F5_S01_network_layout_screenshot.png`

### C. 生成式图片

这类图用于章节封面或过渡页的主题视觉，不作为实验数据证据。

当前预留：

- `F5-I01`: 第5章概念封面图。

提示词见：

`figures/imagegen_prompted/imagegen_prompts.md`

### D. 机制示意图

这类图不是原始实验数据，但由脚本确定性生成，可用于解释研究闭环和方法结构。

当前已生成：

- `F5-G01`: 固定诊断协议下的布局评价闭环。
- `F5-G02`: 从人工规则到双层学习型布局。

## 重新生成

在仓库根目录运行：

```powershell
python E:\11.16\thesis_writing_repo\figure_assets\ch5_layout_optimization\scripts\build_ch5_figure_asset_pack.py
```

脚本会更新 `data/`、`figure_index.csv`、`ppt_insert_index.md` 和当前已定义的图件。若只是调整图的字体、配色或版式，优先修改该脚本。

## 使用边界

- 第5章主排名只使用 scenario split 空间定位指标。
- `node_holdout` 只作为边界分析，不进入主排名。
- `F5-D05` 只说明预算变化对可观测性结构的影响，不说明多预算诊断性能提升。
- 截图类和 imagegen 类图片只用于展示与叙事，不替代实验结果图。

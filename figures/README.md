# 论文与PPT图件整理说明

本目录用于集中管理第3、4、5章论文正文和PPT中使用的图件、源数据、截图清单和生成图提示词。

## 目录结构

- `ch3/data_plots/`：第3章由数据或统计结果生成的图。
- `ch3/source_data/`：第3章图件对应的源数据。
- `ch3/screenshots_needed/`：需要人工截图或外部软件导出的图。
- `ch3/diagrams/`：流程图、机制图、结构示意图。
- `ch3/generated_assets/`：可由 image gen 生成的背景图或概念图。
- `ch4/data_plots/`：第4章由实验结果生成的正式图。
- `ch4/source_data/`：第4章正式图对应的源 CSV。
- `ch4/screenshots_needed/`：第4章需要人工截图的图。
- `ch4/diagrams/`：第4章任务链、模型结构、集合关系等示意图。
- `ch4/generated_assets/`：第4章可由 image gen 生成的辅助视觉素材。
- `ch5/data_plots/`：第5章由布局实验结果生成的图。
- `ch5/source_data/`：第5章图件对应的源 CSV。
- `ch5/screenshots_needed/`：第5章需要人工截图的图。
- `ch5/diagrams/`：第5章布局优化框架图。
- `ch5/generated_assets/`：第5章可由 image gen 生成的辅助视觉素材。
- `scripts/`：后续统一重绘图表的脚本。

## 图件类型

| 类型 | 说明 | 处理方式 |
|---|---|---|
| `data_plot_existing` | 已由实验结果生成并复制到本目录 | 可直接插入 PPT 或论文 |
| `data_plot_to_make` | 需要根据现有 CSV 重新绘制 | 由脚本生成，源数据放入 `source_data/` |
| `diagram_to_draw` | 任务链、模型结构、集合关系等机制图 | 优先用程序绘制，保证学术风格统一 |
| `screenshot_needed` | SWMM、网络结构、程序界面等需要人工截图 | 由你截图后放入对应 `screenshots_needed/` |
| `imagegen_asset` | 概念性背景图或标题页视觉图 | 可用 image gen 生成，不用于替代实验图 |

## 使用原则

1. 实验结果图必须能追溯到源 CSV 或 metrics 文件。
2. PPT 插图编号与 `figure_index.csv` 中的 `ppt_slide` 保持一致。
3. 正文图可从 PPT 图件中筛选，但正文图题需要重新学术化命名。
4. image gen 只用于概念视觉、背景图或示意性封面，不用于伪造实验曲线、管网结果或模型输出。


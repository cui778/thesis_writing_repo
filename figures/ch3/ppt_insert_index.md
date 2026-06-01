# 第3章 PPT 插图索引

## 第3章幻灯片

| 幻灯片 | 图件编号 | 图件名称 | 状态 | 文件路径 |
|---|---|---|---|---|
| 3-0 | CH3-S01 | 研究区域与SWMM管网建模 | 需截图 | `figures/ch3/diagrams/CH3-S01_study_area_screenshot.png` |
| 3-1 | CH3-F01 | 数据集协议总览 | 可用 | `figures/ch3/data_plots/CH3-F01_dataset_protocol_summary.png` |
| 3-2 | CH3-F02 | IE420缺陷矩阵统计 | 可用 | `figures/ch3/data_plots/CH3-F02_ie420_defect_matrix_summary.png` |
| 3-3 | CH3-F03 | 正常工况层参数 | 可用 | `figures/ch3/data_plots/CH3-F03_normal_condition_layer.png` |
| 3-4 | CH3-F04 | 采样与记录统计 | 可用 | `figures/ch3/data_plots/CH3-F04_sampling_record_count.png` |
| 3-5 | CH3-F05 | 残差特征定义 | 可用 | `figures/ch3/data_plots/CH3-F05_residual_feature_definition.png` |
| 3-6 | CH3-F06 | 数据完整性审计 | 可用 | `figures/ch3/data_plots/CH3-F06_dataset_integrity_audit.png` |
| 3-1b | CH3-S02 | PySWMM批量仿真输出 | 可选 | `figures/ch3/data_plots/CH3-S02_pyswmm_output_screenshot.png` |

## 状态说明

- **可用 (ready)**: 图件已生成，可直接使用
- **数据就绪 (data_ready)**: 源数据 CSV 已准备好，需绘制图件
- **需截图 (waiting)**: 等待用户提供截图
- **可选 (optional)**: 非必须图件

## 口径说明

- 所有图源数据来自正式协议（IE420 + normal20 → ie420_plus_normal20_v1）
- 不使用 persistent、mixed 或 fulltime 探索数据
- 48 h 是连续观测窗口，不是缺陷寿命
- 正常场景与缺陷场景处于同一层级

# 第3章图源目录说明

本目录存放第3章"SWMM仿真数据生成"的论文图源和索引。

## 目录结构

```text
figures/ch3/
  README.md                — 本文件
  figure_index.csv         — 图件索引
  ppt_insert_index.md      — PPT 插图索引
  source_data/             — 正式图源 CSV
  diagrams/                — 流程图和示意图
  data_plots/              — 数据可视化图
  legacy_exploration/      — 探索性图源
```

## source_data/ 文件清单

| 文件 | 内容 | 数据来源 |
|---|---|---|
| CH3-F01_dataset_protocol_summary.csv | IE420、normal20、正式组合统计 | dataset_manifest.json |
| CH3-F02_ie420_defect_matrix_summary.csv | I/E 类型、节点覆盖、强度、持续时间 | defect_matrix CSV |
| CH3-F03_normal_condition_layer_summary.csv | 正常场景 seed 与扰动参数 | normal20 manifest |
| CH3-F04_sampling_and_record_count.csv | 48 h、10 min、287 时刻、128 节点 | scenario_summary.csv |
| CH3-F05_residual_feature_definition.csv | 原始特征、残差、相对残差 | pipeline definition |
| CH3-F06_dataset_integrity_audit.csv | 场景完整性、时间一致性、节点覆盖性 | cross-dataset verification |

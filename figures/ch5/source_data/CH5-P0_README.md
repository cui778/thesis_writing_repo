# 第5章 P0 结果数据说明

本批数据只整理结果，不画图、不重训。用途是支撑后续重新设计图形样式。

## 本轮完成的 P0 数据

1. 场景级 raw JSON 重绘主结果：
   - `CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`
   - `CH5-P0_main_metrics_from_raw_json_all_seeds.csv`

2. direct / near / far 性能分组：
   - `CH5-P0_direct_near_far_performance_by_seed.csv`
   - `CH5-P0_direct_near_far_performance_summary.csv`

3. hard candidates 场景性能对比：
   - `CH5-P0_hard_candidates_definition.csv`
   - `CH5-P0_hard_candidates_performance_by_seed.csv`
   - `CH5-P0_hard_candidates_performance_summary.csv`

## 口径

- 方法：Degree / Cand-Obs / Two-stage v1 / v0_2 clean / v2_2 clean。
- 种子：7 / 42 / 123。
- 预算：N=25。
- 数据来源：正式 clean 主线 raw metrics JSON、缺陷矩阵、候选可观测性分层表。
- 不包含旧 `v2_2`、`v1_1/v1_2/v1_3` 或非 clean 探索版本。

## 数据规模

- 场景级记录数：945
- 方法数：5
- seed 数：3
- 场景数：165
- hard candidate 场景数：53

## 已写出文件

- `CH5-P0_raw_by_scenario_formal_clean_all_seeds.csv`
- `CH5-P0_main_metrics_from_raw_json_all_seeds.csv`
- `CH5-P0_direct_near_far_performance_by_seed.csv`
- `CH5-P0_direct_near_far_performance_summary.csv`
- `CH5-P0_hard_candidates_definition.csv`
- `CH5-P0_hard_candidates_performance_by_seed.csv`
- `CH5-P0_hard_candidates_performance_summary.csv`

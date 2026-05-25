# 第5章图件原始数据说明

本文件说明图件资产包中每类图的证据来源。数据图优先使用 raw metrics JSON、defect matrix 和候选可观测性分层表，不使用旧探索版本作为正式主线。

## 原始来源

- raw metrics JSON: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\raw_metrics_from_main_reports_20260413`
- live clean v0_2 metrics: `E:\11.16\script2_new\outputs\reports`
- defect matrix: `E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv`
- candidate observability tiers: `E:\11.16\script2_new\chapter4_diagnosis_model\outputs\candidate_observability_tiers.csv`
- thesis tables: `E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables`

## 生成数据

- `data/ch5_seed42_by_scenario_raw_metrics.csv`: seed42 下正式方法逐场景定位结果，已合并缺陷类型和 direct/near/far 分组。
- `data/ch5_seed42_observability_group_performance.csv`: direct/near/far 分组后的 MRR 与 Top-1。
- `data/ch5_seed42_hard_candidate_performance.csv`: Degree N25 下 far 候选定义的 hard group 与其他场景对比。

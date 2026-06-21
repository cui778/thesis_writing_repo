# 当前排水管网硕士论文项目配置

## 1. 项目路径

```text
论文仓库：E:\11.16\thesis_writing_repo
实验仓库：E:\11.16\script2_new
章节正文：E:\11.16\thesis_writing_repo\chapters
正式图件：E:\11.16\thesis_writing_repo\figures\ch*\generated_results
绘图证据包：E:\11.16\thesis_writing_repo\figures\ch*\source_data
```

## 2. 数据边界

第3章正式缺陷数据必须为：

- `ie420_plus_normal20_v1`
- `formal_conservative420_seed42` 缺陷矩阵

禁止自动回退到：

- persistent；
- fulltime；
- legacy；
- seedset10；
- 其他自动搜索得到的 defect matrix。

数据管理规则：

`E:\11.16\thesis_writing_repo\figures\DATA_SOURCE_POLICY.md`

## 3. 第4章正式协议

```text
dataset      = ie420_plus_normal20_v1
layout       = degree_N25
feature_set  = raw_plus_residual
split        = scenario split
lambda_loc   = 0.5
seeds        = 7, 42, 123
main model   = DeepAttn-L3
```

证据文件：

- `chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- `chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md`
- `figures/ch4/generated_results/CH4_OFFICIAL_FIGURE_INDEX.md`

正式方法证据：

- 分组模型对比：`16_CH4_grouped_model_comparison`
- 深度消融：`17_CH4_deepattn_depth_ablation`
- 路径先验消融：`18_CH4_path_prior_ablation`

Distance-only 仅为 seed42 机制探针。

## 4. 第5章正式协议

固定第4章 DeepAttn-L3，仅改变监测节点集合和 observed mask。主结果为 N=25、seeds 7/42/123。

证据文件：

- `chapters/CH5_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- `chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md`
- `figures/ch5/generated_results/CH5_OFFICIAL_FIGURE_INDEX.md`

核心结论：

- Two-stage v1 在 N=25 取得最高 MRR；
- E-G 的 MRR 接近最高、Top-3 最高、节点集合具有独立性；
- E-G 表征来源消融证明诊断嵌入优于拓扑与坐标表征；
- N=5 时 E-G 不具有 MRR 最优结论；
- I/E 分组仅作补充观察；
- 覆盖率实验仅为 seed42 机制探针。

## 5. 写作禁区

- 不将 Two-stage v1 称为普通基线；
- 不写 E-G 全面最优；
- 不写 E-G 在极低预算下 MRR 最优；
- 不用 I/E gap 证明类型适应性最优；
- 不将低 Jaccard 本身写成性能优势；
- 不用第五章结果反向削弱或解释第四章模型贡献；
- 不把旧协议表和正式结果混入同一论证。

## 6. 正文文件

- `chapters/ch3_data_generation.md` 或当前第3章正式文件；
- `chapters/ch4_model_diagnosis.md`；
- `chapters/ch5_layout_optimization.md`。

正式扩写前先读取目标章节现有内容，不重新设计与已确认故事线冲突的目录。


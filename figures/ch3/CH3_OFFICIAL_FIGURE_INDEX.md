# 第3章正式图件索引（初版）

本索引用于固定第3章绘图口径。第3章优先绘制真实数据证据图，不先绘制实验流程或机理示意图。所有正式图件必须读取 `ie420_plus_normal20_v1` 与 `formal_conservative420_seed42` 缺陷矩阵，禁止自动转用 `persistent`、`fulltime`、`legacy` 或 `seedset10` 数据。

## 正式数据锁定

- 正式组合数据集：`E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1`
- 正式缺陷矩阵：`E:/11.16/script2_new/input_1/defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv`
- 正式 residual 明细：`E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/node_timeseries_with_residuals.parquet`
- 正式场景汇总：`E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/scenario_summary.csv`
- 正式 manifest：`E:/11.16/script2_new/training_data_new/ie420_plus_normal20_v1/dataset_manifest.json`
- 拓扑与节点：`E:/11.16/input_data/2_tuned_v3_merged1.inp`，`E:/11.16/script2_new/input_1/parsed_inp_data.json`

## 首批图件


| 推荐编号    | 脚本名                                                  | 输出目录                                         | 科学问题                                                                                            | 支撑章节        | 图件身份                            | 数据源                                                              | 图型建议                                                                                     | 状态                                                   |
| ------- | ---------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------- | ------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| draw_01 | `draw_01_ch3_ie420_parameter_matrix.py`              | `01_CH3_ie420_parameter_matrix`              | 原计划展示 IE420 正式缺陷协议覆盖情况，但参数矩阵会突出 I/E 起始时刻错位与样本不均衡问题，容易偏离“数据可信度”主叙事。                              | 3.3.3，3.6.1 | 不推荐正文使用；保留脚本与输出备查               | 正式缺陷矩阵                                                           | 参数矩阵 / compact heatmap + 边际分布                                                            | 已降级；不作为正式主图                                          |
| draw_02 | `draw_02_ch3_normal_envelope_defect_residual.py`     | `02_CH3_normal_envelope_defect_residual`     | 典型 I/E 缺陷响应是否显著超出 normal20 正常扰动包络？                                                              | 3.5.3，3.6.2 | 正式主图 / 数据可信度图                   | residual parquet + scenario_summary                              | normal envelope + I/E residual 曲线；另输出单场景 obvious defect profile；支持 02a/02b 强案例 gallery   | 已绘制，profile 版优先；当前推荐 02a/02b                         |
| draw_03 | `draw_03_ch3_node_time_residual_energy.py`           | `03_CH3_node_time_residual_energy`           | 原计划表达单个缺陷场景的全网节点-时间 residual 能量结构，但 128 节点热力图缺少拓扑/节点语义，正文解释成本过高。                                | 3.5.3，3.6.2 | 删除候选/备答，不作为正式图                  | residual parquet + 正式缺陷矩阵                                        | 128 节点 × 时间 residual energy heatmap                                                      | 不纳入正式正文/PPT；脚本和输出仅保留复核                               |
| draw_04 | `draw_04_ch3_topology_residual_spatial_map.py`       | `04_CH3_topology_residual_spatial_map`       | residual 响应是否沿管网拓扑呈现与缺陷位置相关的空间传播格局，并随 active window 出现和回落？                                      | 3.2.4，3.6.2 | 正文/PPT主图候选                      | residual parquet + parsed topology + 正式缺陷矩阵                      | 管网空间 residual 主图 + pre/active/peak/post 小图；读取 draw_02 强案例清单生成 04a/04b 空间 gallery         | 已绘制，当前推荐 04a/04b                                     |
| draw_05 | `draw_05_ch3_candidate_monitor_topology_setting.py`  | `05_CH3_candidate_monitor_topology_setting`  | 缺陷候选节点与 Degree-N25 监测节点在管网拓扑中分别位于哪些位置，二者重叠程度如何？                                                 | 3.3.1，3.4.3 | 实验设置主图，正文顺序应提前                  | parsed topology + candidate_nodes_new + monitor_nodes_degree_N25 | 管网拓扑底图 + candidate/monitor/overlap 节点集合图                                                 | 已绘制                                                  |
| draw_06 | `draw_06_ch3_case_selection_map.py`                  | `06_CH3_case_selection_map`                  | 原计划把 02/04 典型案例放回 IE420 参数矩阵中解释案例来源，但会再次突出协议矩阵的不均衡结构。                                           | 3.5.3，3.6.2 | 试绘图/备查，不推荐正文或 PPT 使用            | draw_02 强案例清单 + 正式缺陷矩阵                                           | 典型案例在参数矩阵中的位置图                                                                           | 已降级；不作为正式图                                           |
| draw_07 | `draw_07_ch3_all_scenario_event_aligned_response.py` | `07_CH3_all_scenario_event_aligned_response` | 高强度且 I/E、duration 均衡的缺陷场景在对齐缺陷开始时间后，水力 residual 是否相对 normal20 reference 出现可观测响应，且这种响应是否与拓扑距离有关？ | 3.5.3，3.6.2 | 均衡子集数据可信度候选图；不替代 02/04，作为总体证据补充 | residual parquet + normal20 + 正式缺陷矩阵 + parsed topology           | event-aligned hydraulic response raster；每行保留一个场景，不跨场景平均；仅使用 depth/total_outflow residual | 已重绘；64 个高 abs(flow) 场景，I/E 与 6/12/18/24h duration 均衡 |
| draw_08 | `draw_08_ch3_strength_stratified_event_response.py`  | `08_CH3_strength_stratified_event_response`  | 缺陷强度如何影响水力 residual 的可观测性，弱/中/强缺陷是否呈现不同的时空响应强度？                                                 | 3.5.3，3.6.2 | 强度分层数据可信度主候选图；与 02/04 互补        | residual parquet + normal20 + 正式缺陷矩阵 + parsed topology           | 低/中/高强度均衡场景 event-aligned raster + 全 420 场景 strength-response scatter                    | 已绘制；08a/08b/08c 各 64 个均衡场景，08d 覆盖全 420 缺陷场景          |
| draw_09 | `draw_09_ch3_response_peak_timing.py`                | `09_CH3_response_peak_timing`                | 缺陷发生后水力 residual 响应通常在第几个小时达到峰值，峰值响应主要出现在 0-hop、1-hop、2-hop 还是远端拓扑距离层？                          | 3.5.3，3.6.2 | 响应动态过程主候选图；补充 08d 的“强度-幅值”关系    | residual parquet + normal20 + 正式缺陷矩阵 + parsed topology           | 峰值时滞散点 + duration 分布 + dominant hop 堆叠条形图 + peak phase heatmap                           | 已绘制；覆盖全 420 缺陷场景，每个场景保留一个 active-window peak         |


## 暂缓图件


| 图件                  | 暂缓原因                       | 后续条件                              |
| ------------------- | -------------------------- | --------------------------------- |
| 缺陷节点距离分层响应衰减图       | 需要先验证距离分层是否有稳定趋势，避免为了机制而机制 | draw_03/draw_04 完成后，用同一场景或多场景抽样复核 |
| 实验流程图/机理示意图         | 当前阶段优先真实数据图                | 第3章正式数据证据图完成后再考虑                  |
| 大规模全场景 residual 总览图 | parquet 体量大，容易牺牲解释性        | 需要先建立轻量抽样或聚合缓存                    |


## 每图绘制前置检查

1. 确认 `dataset_manifest.json` 中 `dataset_type=ie420_plus_normal20`，`persistent_count=0`，`scenario_count=441`。
2. 确认缺陷矩阵为 `defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv`，I/E 数量为 250/170。
3. 对 parquet 图件只读取所需列、所需场景、所需节点，不全量载入 2.94GB 明细。
4. 脚本输出仅允许 PNG、SVG 和必要 cleaned/summary CSV；不输出 PDF。
5. SVG 必须保持文字可编辑：`plt.rcParams["svg.fonttype"] = "none"`。
6. 若图件不能回答明确科学问题，降级为备答或暂缓。


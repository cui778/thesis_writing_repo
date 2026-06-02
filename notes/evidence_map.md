# 论文证据地图

本文件用于记录“论文结论 -> 数据来源 -> 可写边界 -> 禁止越界内容”的对应关系。每写一个小节，先补充或检查对应证据。

## 第3章 SWMM baseline 与 IE420 数据集构建

### 本章要支撑的表述

基于黄孝河-机场河流域工程资料划定研究子区，构建可独立运行的 SWMM 基线模型；在此基础上生成正常工况响应，并通过 PySWMM 批量注入 I/E 缺陷，导出全网 128 节点时序。数据处理中，从正常工况层选取一条 reference 响应作为 residual 对齐参照，形成第4章和第5章共用的正式母数据。

### 可写事实

- 正式 SWMM 基线模型文件为 `E:\11.16\input_data\2_tuned_v3_merged1.inp`。
- INP 解析统计：全网节点 128，Junction 113，Outfall 2，Storage 13，Conduit 137，Xsection 137。
- 模型配置水力输出字段：`depth`、`head`、`volume`、`lateral_inflow`、`total_inflow`、`total_outflow`、`flooding`。
- 模型配置水质组分：BODf、BODs、NH4、NO3、DO、TSSs、TSSn、TR_in、TR_ww；后续诊断主用 NH4 与 TSSs 作为水质伴随响应特征。
- 正式缺陷矩阵为 IE420：420 个 I/E 缺陷场景，其中 I=250、E=170；I 覆盖 50 个候选节点，E 覆盖 34 个合法渗漏节点。
- 正式数据包含 21 条正常工况响应和 420 条 I/E 缺陷工况响应，共 441 个场景；采样间隔 10 min；每场景 287 个时间点；每场景 36736 条节点记录。
- 正式训练组合为 `ie420_plus_normal20_v1`。正常工况响应处于同一数据层级，其中选取一条 reference 场景用于 residual 对齐，其余正常扰动场景用于刻画正常波动范围。
- 48 h 是统一观测窗口，不是缺陷寿命假设。
- 正式母数据为全网节点输出，`key_nodes_only=false`、`strict_monitor_only=false`，不是监测节点子集。
- 50 个候选节点均进入正式缺陷激活空间。

### 数据与文件来源

```text
E:\11.16\input_data\2_tuned_v3_merged1.inp
E:\11.16\script2_new\input_1\parsed_inp_data.json
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\monitor_nodes_degree_N25.json
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\dataset_manifest.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\scenario_summary.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F01_dataset_protocol_summary.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F02_ie420_defect_matrix_summary.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F03_normal_condition_layer_summary.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F04_sampling_and_record_count.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F05_residual_feature_definition.csv
E:\11.16\thesis_writing_repo\figures\ch3\source_data\CH3-F06_dataset_integrity_audit.csv
```

### 待恢复的外部工程资料

研究区域背景、排水系统概况与工程边界描述来自黄孝河-机场河流域工程资料。原始 PDF 与 DOCX 当前未保存在本仓库中，后续应在资料归档后补充稳定路径。正文可以使用已经核对过的工程背景表述，但在正式提交前需要恢复原始资料索引。

### 可写边界

- 可以写“结合现场监测结果对 baseline 工况进行校核”。
- 当前不展开具体误差指标，后续若补充实测水位、流量、NH4、TSSs 对比表，可再升级为更完整的实测率定与验证表述。
- 水质变量写作 I/E 水量扰动下的伴随响应特征，不写成 P 类水质污染源定位。

### 禁止越界

- 不写“从大 INP 文件截取一部分”，统一写作“基于排水分区、泵站服务范围和边界条件划定研究子区”。
- 不将第3章写成第4章模型性能结果。
- 不使用旧 300 场景、旧 `formal40` 或旧 `v2e_dense_ie` 作为正式证据。
- 不写“已经完成严格实测率定并给出误差指标”，除非后续补充真实监测对比数据。

## 第4章 面向缺陷定位的时空图诊断模型研究

### 第4章总论要支撑的表述

第4章在第3章 IE420 time-gated 连续缺陷场景基础上，研究固定 `degree N25` 稀疏监测布局下的 I/E 缺陷诊断与候选节点定位问题。模型保留 128 节点全图拓扑，使用 25 个监测节点动态观测，在 50 个候选缺陷节点空间内形成定位排序；诊断链条组织为“滑动窗口样本 -> 窗口级诊断证据 -> 场景时间级定位 -> 场景空间级定位 -> 场景报警级判断 -> 综合诊断”。

### 第4章可写事实

- 正式缺陷类型：I/E。
- 正式缺陷矩阵：IE420。
- 正式数据口径：time-gated，即缺陷在 `start_hour` 和 `duration_h` 定义的时间段内激活。
- 正式训练组合：ie420_plus_normal20_v1（421 场景 + 20 normal = 441 场景）。
- 图输入范围：全网 128 节点拓扑。
- 固定监测布局：`degree N25`，25 个监测节点。
- `degree N25` 监测节点与候选缺陷节点交集为 12。
- 定位评价空间：50 个候选缺陷节点。
- 正式训练入口：`scripts/train_privileged_teacher_student.py`。
- 正式输入协议：full-graph sparse-observation，保留拓扑和 observed mask，非观测节点动态特征不作为可见观测。
- 正式业务时序特征为 `raw_plus_residual`：4 维原始特征、4 维绝对残差和 4 维相对残差，共 12 维。数据加载阶段另行追加 2 维小时周期编码和 1 维 `observed_mask`，因此时序编码器实际接收 15 维节点动态输入。
- 主模型还读取 `shortest_dist`、`pipe_length_dist`、`flow_direction` 和 `elevation_diff` 四类节点对静态路径先验，用于液压逆向注意力计算；这些关系特征不计入节点动态输入维度。
- 正式空间定位基线：`sequence_length=36`，约 6 h；`window_stride=6`，约 1 h。
- 第5章任务：在第4章固定诊断任务、模型协议和候选空间基础上优化监测节点集合 `S`。

### 第4章核心证据来源

```text
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\thesis_writing_repo\ppt\part4_model_diagnosis_ppt_text.md
E:\11.16\script2_new\README.md
E:\11.16\script2_new\scripts\train_privileged_teacher_student.py
E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F06_main_model_multiseed.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F07_task_level_results_summary.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42
```

### 第4章禁止越界

- 不能写成在 128 个节点中自由定位缺陷；正式定位评价空间是 50 个候选缺陷节点。
- 不能把 P 类水质污染源定位写成本论文已完成任务。
- 不能把 I/E 分组定位分析写成 I/E 自动分类任务。
- 不能把 `node_holdout` 写成已经解决未见节点泛化。
- 不能使用旧 `v2e_dense_ie`、旧 `MRR>=0.91` 或旧 `dynamic_only` 时间线结果作为正式主证据。
- 不能把 `always_on` 写成正式全程注入实验；真正全程注入需要单独数据闭环。

## 第4章第4.1节 连续场景下的缺陷诊断任务定义

### 本节要支撑的表述

第4章的诊断对象是一条连续缺陷场景，工程问题可拆解为“是否存在缺陷响应、缺陷大致发生在哪段时间、缺陷更可能位于哪些节点”。本节应说明 `V=128`、`S=25`、`C=50`、`D` 四类集合，以及滑动窗口如何把连续场景转化为窗口级诊断样本。

### 可写事实

- 诊断链条：IE420 连续缺陷场景 -> 滑动窗口样本构建 -> 窗口级诊断证据提取 -> 场景级活跃期定位 -> 场景级空间定位 -> 场景级综合诊断。
- `V=128` 表示全图拓扑。
- `S=25` 表示固定监测节点集合。
- `C=50` 表示候选定位空间。
- `D` 表示实际激活缺陷节点集合，随场景变化。
- 正式窗口设置：采样间隔 10 min，`sequence_length=36`，`window_stride=6`。
- 窗口 active 标签来自窗口与真实 active 时段的 overlap ratio。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\monitor_nodes_degree_N25.json
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\dataset_manifest.json
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F10b_candidate_observability_counts.csv
```

### 可写边界

- 可以写“粗粒度活跃期定位”，不写成分钟级起止时间回归。
- 可以写“第5章固定 V 和 C，优化 S”。

### 禁止越界

- 不在任务定义中提前写性能数值。
- 不把候选空间 C=50 写成临时后处理技巧；它是工程排查范围定义。

## 第4章第4.2节 稀疏观测图输入与时空诊断模型

### 本节要支撑的表述

主模型 `hydraulic_inverse_deepattn` 接收全图拓扑和稀疏动态观测输入，输出窗口级 active 判断和节点级定位分数；模型中保留类型相关输出头，但第4章正式监督和评价主线不包含 I/E 自动分类。

### 可写事实

- 正式训练入口为 `scripts/train_privileged_teacher_student.py`。
- 主模型类型为 `hydraulic_inverse_deepattn`。
- 模型主输出：
  - `logits_has_defect` -> `p_active(t)` -> active 识别与场景级活跃期定位。
  - `logits_node` -> `node_scores(t)` -> 窗口级与场景级节点定位。
  - `logits_defect_type` 存在于代码结构中，但正式训练 `lambda_type=0.0`。
- 当前 I/E 结果来自真实类型分组统计，不来自 `logits_defect_type` 分类评价。

### 数据与文件来源

```text
E:\11.16\script2_new\models\anomaly_detection_model.py
E:\11.16\script2_new\scripts\train_privileged_teacher_student.py
E:\11.16\script2_new\utils\evaluation.py
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\README.md
```

### 禁止越界

- 不写“模型完成 I/E 类型分类”。
- 不把 `logits_defect_type` 的存在等同于正式类型分类结果。
- 不把 full-graph sparse-observation 写成全节点动态观测可见。

## 第4章第4.3节 训练协议与评价指标

### 本节要支撑的表述

第4章评价指标按任务链分层组织：窗口级 active 识别、窗口级节点定位、场景级活跃期定位、场景级空间定位、场景报警级判断和综合诊断审查。`scenario split` 是正式主协议，`node_holdout` 是泛化压力测试。

### 可写事实

- `scenario split` 保证同一场景窗口不跨训练、验证和测试集合。
- `node_holdout` 用于未见缺陷节点压力测试，不作为正式主性能口径。
- 窗口级 active 指标：Active Accuracy、Active Recall、Active-period Recall、Active F1、Normal Window FPR。
- 节点定位指标：MRR、Top-1、Top-3、Top-5。
- 场景级空间定位指标：Event Top-1、Event Top-3、Event Top-5。
- 场景级活跃期定位指标：onset error、±1/±2/±3 滑动步长命中、active interval IoU。正式实验中滑动步长固定为 1 h。
- 场景报警级指标：Scene Precision、Scene Recall、Scene FPR、Scene F1。
- 综合诊断指标：起点命中与节点 Top-K 同时满足的联合指标，作为补充审查。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\utils\evaluation.py
E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py
```

### 禁止越界

- 不把 true-active 聚合 Event Top-K 写成完整 predicted-active 综合诊断结果。
- 不把 predicted-active scene Top-K 写成纯空间定位能力。

## 第4章第4.4节 缺陷诊断主实验结果

### 本节要支撑的表述

在固定 `degree N25` sparse-observation 协议和 IE420 + normal20 正式数据下，主模型能够稳定完成窗口级诊断证据提取和场景级事件定位；特征组合与定位损失权重分析确认 residual 是主要有效信息来源；窗口长度实验揭示时间段定位与空间定位稳定性之间的尺度权衡。

### 可写事实

- 正式协议：ie420+normal20 / raw_plus_residual / lambda_loc=0.5 / hydraulic_inverse_deepattn / degree_N25 / scenario split / seeds=7/42/123。
- seed42 主结果（正式协议）：MRR=0.8457，Top-1=0.7728，Top-3=0.8973，Top-5=0.9463，Active F1=0.9790，Normal Window FPR=0.0005，Scene F1=0.9917。
- 多 seed（正式协议，Degree_N25_formal）：
  - seed7：MRR=0.8477，Top-1=0.7413，Top-3=0.9443，Top-5=0.9741，Event Top-1=0.7969，Scene F1=1.0000。
  - seed42：MRR=0.8457，Top-1=0.7728，Top-3=0.8973，Top-5=0.9463，Event Top-1=0.8197，Scene F1=0.9917。
  - seed123：MRR=0.7827，Top-1=0.6425，Top-3=0.9161，Top-5=0.9759，Event Top-1=0.6885，Scene F1=1.0000。
- 模型结构正式对比（`IE420 + normal20 / raw_plus_residual / lambda_loc=0.5 / degree_N25 / scenario split / seeds=7,42,123`）：
  - `gru_only`：MRR=0.2110±0.0092。
  - `gru_gcn`：MRR=0.2550±0.0116。
  - `lstm_graphsage_edge`：MRR=0.4664±0.0090。
  - `hydraulic_inverse`：MRR=0.4269±0.0463。
  - `hydraulic_inverse_deepattn`：MRR=0.8254±0.0370，Top-1=0.7189，Top-3=0.9192，Normal Window FPR=0.0009。
  - 可写结论：深层液压注意力模型在统一协议下明显优于纯时序、普通图卷积、边关系建模和单层液压注意力结构。
以下特征组合结果来自历史探索协议，用于解释正式协议的形成过程，不作为当前 `IE420 + normal20` 正式主性能证据。

- 特征组合对照（历史 seedset10 数据，调参依据，非正式协议性能）：
  - raw_only：MRR=0.2419。
  - residual_only：MRR=0.8082。
  - raw_plus_residual：MRR=0.8290。
- 窗口长度正式复核（`IE420 + normal20`，seed42，仅改变输入长度，滑动步长固定为 1 h）：
  - 2h：Active F1=0.9877，Normal FPR=0.0023，MRR=0.8289，Top-1=0.7187，Top-3=0.9302，Top-5=0.9646，onset error=0.7459h，interval IoU=0.9165。
  - 3h：Active F1=0.9866，Normal FPR=0.0010，MRR=0.8531，Top-1=0.7564，Top-3=0.9435，Top-5=0.9889，onset error=0.7842h，interval IoU=0.8397。
  - 4h：Active F1=0.9927，Normal FPR=0.0035，MRR=0.8511，Top-1=0.7483，Top-3=0.9541，Top-5=0.9866，onset error=1.5874h，interval IoU=0.8104。
  - 6h：Active F1=0.9790，Normal FPR=0.0005，MRR=0.8457，Top-1=0.7728，Top-3=0.8973，Top-5=0.9463，onset error=2.1831h，interval IoU=0.7437。
  - 可写结论：窗口长度影响并非单调；3h/4h 的排序覆盖指标较强，6h 的窗口 Top-1 与误报控制更稳。本文保留 6h 作为第5章固定空间诊断基线，短窗口用于尺度敏感性分析。
- I/E 分组定位正式复核（`IE420 + normal20`，seeds=7/42/123，按真实缺陷类型事后分层）：
  - I 类窗口级：MRR=0.8540±0.0312，Top-1=0.7571±0.0607，Top-5=0.9809±0.0103。
  - E 类窗口级：MRR=0.7885±0.0494，Top-1=0.6693±0.0823，Top-5=0.9463±0.0347。
  - I 类事件级：Event MRR=0.8788±0.0407，Event Top-1=0.7909±0.0705，Event Top-5=1.0000±0.0000。
  - E 类事件级：Event MRR=0.8320±0.0535，Event Top-1=0.7391±0.0739，Event Top-5=0.9757±0.0210。
  - 可写结论：I 类整体定位效果优于 E 类；两类缺陷在 Event Top-5 上均具有较高可用性。该分析不是 I/E 自动分类任务。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F06_main_model_multiseed.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F07_task_level_results_summary.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F08_feature_set_comparison.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F08_formal_model_comparison_multiseed_summary.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F09a_time_boundary_audit_summary.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F09b_formal_time_window_length_eval_summary.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F10a_formal_ie_type_group_multiseed_summary.csv
```

### 可写边界

- 6h 是空间定位主基线，用于第5章衔接。
- 2h/3h/4h 是输入尺度敏感性分析，不替代第5章固定 6h 空间诊断基线。
- 时间位置、trend、always_on 等早期结果可放备答，不作为第4章主结果。

### 禁止越界

- 不使用旧 `MRR>=0.91` 或旧 `v2e_dense_ie` 结果作为正式主证据。
- 不把时间窗口实验写成已经完成精细起止时间回归。
- 不把 I/E 分组统计写成 I/E 分类模型结果。

## 第4章第4.5节 泛化边界、可观测性与综合分析

### 本节要支撑的表述

`node_holdout` 是未见缺陷节点压力测试，用于说明泛化边界；direct/near/far 可观测性用于解释候选节点与监测节点距离对定位难度的影响；predicted-active 综合诊断审查用于说明“先时间、再空间”的完整流程仍需要更稳健的跨窗口节点分数融合。

### 可写事实

- node_holdout 下定位性能明显低于 scenario split，说明严格未见节点泛化仍然困难。
- direct/near/far 可观测性分层可解释不同候选节点定位难度。
- 使用预测 active 时间段聚合 node scores 的 scene-level Top-K 更严格，会同时受到时间段选择和节点分数融合影响。
- predicted-active scene Top-K 同时受到时间段恢复与节点分数聚合影响；该指标可作为综合诊断审计，不替代 true-active Event Top-K。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F10b_nodehold_observability_summary.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F10b_candidate_observability_counts.csv
E:\11.16\thesis_writing_repo\figures\ch4\source_data\CH4-F09b_formal_time_window_length_eval_summary.csv
```

### 禁止越界

- 不把 node_holdout 写成已经解决未见节点泛化。
- 不把 predicted-active scene Top-K 低写成主模型空间定位失败。
- 不把 oracle active 结果写成实际模型诊断性能。

## 第5章 融合诊断反馈与节点表征的排水管网监测布局优化

### 第5章总论要支撑的表述

第5章在第3章 IE420 母数据和第4章诊断任务、模型结构、窗口设置与评价协议固定的前提下，只改变监测节点集合 `S` 与 observed mask，研究监测布局对 I/E 缺陷空间定位性能的影响。本章主线是从拓扑规则布局走向诊断表征驱动布局。所有结果均在统一协议 `IE420 + normal20 / raw_plus_residual / lambda_loc=0.5` 下获得，采用 3 个诊断 seed 评价。

### 第5章核心可写事实

- 固定内容：IE420+normal20 母数据、128 节点全图拓扑、50 个候选缺陷节点、第4章诊断任务、模型结构、窗口设置与评价协议。
- 唯一变化：监测节点集合 `S`、`monitor_nodes_file`、observed mask。
- 主评价：`scenario split`、预算 `N=25`、诊断 seed 7/42/123。
- 主排名指标：MRR、Top-1、Top-3、Top-5、Event Top-1、Event Top-3、Event Top-5、Scene F1。
- 6 种布局方法：Degree、Betweenness、Cand-Obs、Two-stage v1、Node-Feedback (val)、Embedding-Guided。
- 方法命名：正式表中 `Node-Feedback (val)` 为 Node-Feedback 的 scenario val 口径；CSV 中的内部名称 `Embedding-Guided-new` 在论文正文中统一写为 `Embedding-Guided`。
- Two-stage v1 定位为”离线仿真信息充分条件下的任务导向启发式参考”，不作为本文创新。
- Node-Feedback 定位为”探索性反馈学习方法”，训练数据仅 3 种布局 x 3 种子 = 9 组。
- Embedding-Guided 为正文主方法，利用诊断编码器节点嵌入的 max-min diversity 选点。
- 所有 mean±std 使用 ddof=1（样本标准差）。
- 预算曲线仅 seed42，写趋势不写稳定性。

### 第5章核心证据来源

```text
thesis_writing_repo/figures/ch5/source_data/CH5-EXPT_fixed_protocol_N25_main_table.csv    — 正式主表，6 方法 x 3 种子
thesis_writing_repo/figures/ch5/source_data/CH5-budget_sweep_seed42.csv                     — 预算曲线 seed42
thesis_writing_repo/figures/ch5/source_data/CH5-N25_hard_candidate_analysis.csv            — 困难候选分析
thesis_writing_repo/figures/ch5/source_data/CH5-N25_by_defect_type_analysis.csv            — I/E 类型分析
thesis_writing_repo/figures/ch5/source_data/CH5-N25_pairwise_jaccard.csv                   — Jaccard 布局相似度
thesis_writing_repo/figures/ch5/source_data/CH5-N25_layout_structure.csv                   — 布局结构特征
```

### 第5章禁止越界

- 不把第5章写成重新训练或重新定义诊断任务的章节。
- 不把第5章结果倒灌回第4章固定 `degree N25` 主结果。
- 不把 Two-stage v1 写成本文创新。
- 不把 Embedding-Guided 写成”完全独立于候选机制”。
- 不把 Node-Feedback 写成”学习通用布局模式”。
- 不把预算曲线写成稳定性结论。
- 不把结构指标更优直接写成诊断性能必然更优。
- 不使用旧方法名 `v0_2 clean`/`v2_2 clean`；正式命名见主表 CSV。
- 不把 Surrogate-Search 放入主表（已移除）。

## 第5章第5.1节 监测节点布局优化问题定义

### 本节要支撑的表述

第5章将监测节点集合 `S` 从第4章的固定输入条件转化为待优化变量。传统拓扑中心性布局是合理基线，但不必然服务于候选缺陷节点空间定位。

### 可写事实

- `V=128` 表示全图拓扑节点。
- `C=50` 表示候选缺陷节点空间。
- `S=25` 表示本章主预算下的监测节点集合。
- `degree N25` 是第4章固定布局和第5章对照基线。
- 第5章优化变量是 `S`，不是 `V` 或 `C`。

### 数据与文件来源

```text
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\monitor_nodes_degree_N25.json
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

### 禁止越界

- 不在问题定义里提前写方法优劣。
- 不把 `degree N25` 写成错误布局。

## 第5章第5.2节 固定诊断协议下的布局评价闭环

### 本节要支撑的表述

每个布局方案只改变监测节点集合和 observed mask，在相同数据、模型结构、窗口设置、训练评价协议和候选空间下比较空间定位结果。

### 可写事实

- 统一数据来源、统一候选空间、统一训练与评价协议。
- 不共用同一个 checkpoint，而是在相同诊断协议下比较不同布局。
- 主排名指标为 MRR、Top-1、Top-3、Top-5 和 event-level 空间定位 Top-K。
- 多 seed 评价口径：诊断 seed 7/42/123，mean ± std（ddof=1）。
- 实验分组：纯拓扑基线（Degree, Betweenness）→ 覆盖导向基线（Cand-Obs, Two-stage v1）→ 诊断表征驱动方法（Node-Feedback, Embedding-Guided）。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_table.csv
```

### 禁止越界

- 不用”同一诊断评价器固定”造成共用 checkpoint 的误解。
- 不把第4章活跃期定位指标（onset error、interval IoU）混入第5章布局主排名。

## 第5章第5.3节 对比方法：拓扑规则、覆盖导向与诊断表征

### 本节要支撑的表述

六种布局方法按”诊断信息介入程度”排列，分别代表不同信息来源：纯拓扑规则（Degree、Betweenness）、任务设计经验（Cand-Obs、Two-stage v1）、诊断模型反馈（Node-Feedback、Embedding-Guided）。

### 可写事实

- 层次一（规则驱动）：Degree、Betweenness — 无诊断信息，纯拓扑中心性。
- 层次二（覆盖导向）：Cand-Obs、Two-stage v1 — 基于候选节点位置和 SWMM 仿真响应的任务设计经验。
- 层次三（诊断表征驱动）：Node-Feedback、Embedding-Guided — 诊断模型的外部评价或内部表征。
- 关键定位：
  - Two-stage v1：离线仿真信息充分条件下的任务导向启发式参考，非本文创新。
  - Node-Feedback：探索性反馈学习方法，训练数据仅 9 组。
  - Embedding-Guided：正文主方法，利用诊断编码器节点嵌入的 max-min diversity 选点。
- 结构统计（来自 CH5-N25_layout_structure.csv）：
  - Degree：direct=12，near=21，far=17，mean_hop=3.48。
  - Betweenness：结构特征见正式表。
  - Cand-Obs：direct=15，near=34，far=1，mean_hop=0.94。
  - Two-stage v1：direct=18，near=31，far=1，mean_hop=0.92。
  - Node-Feedback (val)：结构特征见正式表。
  - Embedding-Guided：结构特征见正式表。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_layout_structure.csv
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
```

### 禁止越界

- 不把 Surrogate-Search 放入主表或本节方法列表（已移除）。
- 不使用旧版本名（`v0_2 clean`、`v2_2 clean`）。

## 第5章第5.4节 不同布局方法的定位性能对比

### 本节要支撑的表述

在 N=25、3 种子条件下，6 种布局方法的空间定位性能存在系统性差异。诊断表征驱动方法（尤其是 Embedding-Guided）在 MRR 和 Top-1 上整体优于纯拓扑规则基线；Two-stage v1 在 Event Top-1 上表现最高，但依赖全部缺陷场景仿真响应。

### 可写事实（来自 CH5-EXPT_fixed_protocol_N25_main_table.csv，3 seed mean±std, ddof=1）

- Degree：MRR=0.825±0.037，Top-1=0.719±0.069，Top-3=0.919±0.024，Top-5=0.965±0.016，Event Top-1=0.768±0.070，Scene F1=0.997±0.005。
- Betweenness：MRR=0.868±0.009，Top-1=0.772±0.011，Top-3=0.961±0.019，Top-5=0.990±0.009，Event Top-1=0.785±0.016，Scene F1=0.994±0.010。
- Cand-Obs：MRR=0.878±0.034，Top-1=0.795±0.053，Top-3=0.951±0.022，Top-5=0.983±0.010，Event Top-1=0.807±0.044，Scene F1=0.997±0.005。
- Two-stage v1：MRR=0.905±0.027，Top-1=0.832±0.043，Top-3=0.974±0.018，Top-5=0.989±0.014，Event Top-1=0.855±0.024，Scene F1=1.000±0.000。
- Node-Feedback (val)：MRR=0.896±0.032，Top-1=0.815±0.058，Top-3=0.970±0.013，Top-5=0.996±0.002，Event Top-1=0.856±0.082，Scene F1=1.000±0.000。
- Embedding-Guided：MRR=0.897±0.017，Top-1=0.818±0.029，Top-3=0.981±0.008，Top-5=0.999±0.002，Event Top-1=0.828±0.041，Scene F1=0.997±0.005。

### 叙事主线（不是排行榜）

1. 纯拓扑布局仍有优化空间（Degree MRR=0.825±0.037）。
2. 覆盖邻近并不是唯一有效策略（Cand-Obs 0.878±0.034，Two-stage 0.905±0.027）。
3. Embedding-Guided 是正文主方法（MRR 0.897±0.017，三条独立证据）。
4. 结论落点：诊断表征能够提供不同于拓扑和覆盖规则的布局依据。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_table.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_layout_structure.csv
```

### 禁止越界

- 不用 seed42 单次结果替代多 seed 主结论。
- 不把 node_holdout 放入主排名。
- 不把 Two-stage v1 写成”普通规则基线”或本文创新。

## 第5章第5.5节 预算约束下的性能变化

### 本节要支撑的表述

不同预算下各方法的性能趋势不同，存在交叉点；低预算时 Embedding-Guided 占优，中高预算时 Two-stage v1 领先。

### 可写事实

- 预算曲线仅 seed42，写趋势不写稳定性。
- 交叉点：N=5 时 Embedding-Guided 最高（MRR≈0.607），N≥10 时 Two-stage v1 最高。
- 必须标注”仅 seed 42，趋势参考，不用于稳定性结论”。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-budget_sweep_seed42.csv
```

### 禁止越界

- 不写多 seed 稳定性结论（预算曲线仅 seed 42）。

## 第5章第5.6节 机制分析

### 本节要支撑的表述

困难观测区域、I/E 缺陷类型适应性、布局相似度分别从可观测性、缺陷类型和布局独立性角度解释方法差异。

### 可写事实

- 5.6.1 困难候选：0 个候选在所有布局下均 far，7 个候选在所有布局下均 near/direct。措辞用”在当前六类布局下，没有候选节点始终处于远距离观测状态”。
- 5.6.2 I/E 类型：Embedding-Guided 的 I-E gap 最小（0.009），Degree 最大（0.066）。
- 5.6.3 Jaccard：Embedding-Guided 与所有其他方法的 Jaccard ≤ 0.136，与 Degree 仅 0.042。Node-Feedback 与 Degree 高度重叠（0.563）。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_hard_candidate_analysis.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_by_defect_type_analysis.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-N25_pairwise_jaccard.csv
```

### 禁止越界

- 不写”没有候选节点天生不可观测”（过度泛化）。
- 不写 Embedding-Guided “完全独立于候选机制”（应写”不显式依赖候选节点覆盖目标”）。

## 第5章第5.7节 本章小结与局限性

### 本节要支撑的表述

第5章可稳定支持四个主结论和四个局限性。

### 四个主结论

1. 纯拓扑中心性布局不是诊断任务的最优选择（Degree MRR=0.825，显著低于其他方法）。
2. 覆盖邻近并不是唯一有效策略（Cand-Obs 0.878 低于 Two-stage 0.905 和 Embedding-Guided 0.897）。
3. 诊断表征能够提供不同于拓扑中心性和邻近覆盖规则的布局依据（Embedding-Guided 三条独立证据）。
4. 预算敏感性存在交叉点（N=5 时 Embedding-Guided 占优，N≥10 时 Two-stage v1 领先）。

### 四个局限性

1. Node-Feedback 训练数据仅 9 组，布局结构多样性有限。
2. Two-stage v1 利用全部缺陷场景仿真响应，属于信息充分参考。
3. 预算曲线仅 seed 42，趋势结论有待多 seed 验证。
4. 所有实验在同一管网（128 节点）上进行，跨管网泛化性待验证。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch5_layout_optimization.md
E:\11.16\thesis_writing_repo\notes\evidence_map.md
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_table.csv
```

### 禁止越界

- 不新增正文没有证明的优势。
- 不把第5章写成已形成可直接现场部署的最终布点规范。
- 不对第4章主结果进行反向改写。

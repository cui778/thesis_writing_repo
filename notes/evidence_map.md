# 论文证据地图

本文件用于记录“论文结论 -> 数据来源 -> 可写边界 -> 禁止越界内容”的对应关系。每写一个小节，先补充或检查对应证据。

## 第3章 SWMM baseline 与 IE420 数据集构建

### 本章要支撑的表述

基于黄孝河-机场河流域工程资料划定研究子区，构建可独立运行的 SWMM baseline 模型；在此基础上通过 PySWMM 批量注入 I/E 缺陷，导出全网 128 节点时序，并与 baseline 对齐构造 residual 特征，形成第4章和第5章共用的正式母数据。

### 可写事实

- 正式 SWMM 基线模型文件为 `E:\11.16\input_data\2_tuned_v3_merged1.inp`。
- INP 解析统计：全网节点 128，Junction 113，Outfall 2，Storage 13，Conduit 137，Xsection 137。
- 模型配置水力输出字段：`depth`、`head`、`volume`、`lateral_inflow`、`total_inflow`、`total_outflow`、`flooding`。
- 模型配置水质组分：BODf、BODs、NH4、NO3、DO、TSSs、TSSn、TR_in、TR_ww；后续诊断主用 NH4 与 TSSs 作为水质伴随响应特征。
- 正式缺陷矩阵为 IE420：420 个 I/E 缺陷场景，其中 I=250、E=170；I 覆盖 50 个候选节点，E 覆盖 34 个合法渗漏节点。
- 正式母数据包含 baseline + IE420，共 421 个场景；采样间隔 10 min；每场景 287 个时间点；每场景 36736 条节点记录。
- 正式母数据为全网节点输出，`key_nodes_only=false`、`strict_monitor_only=false`，不是监测节点子集。
- 50 个候选节点均进入正式缺陷激活空间；固定监测节点与实际激活缺陷节点交集为 12。

### 数据与文件来源

```text
E:\11.16\input_data\2_tuned_v3_merged1.inp
E:\11.16\script2_new\input_1\parsed_inp_data.json
E:\11.16\script2_new\input_1\node_list.json
E:\11.16\script2_new\input_1\candidate_nodes_new.json
E:\11.16\script2_new\input_1\monitor_nodes_degree_N25.json
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\dataset_manifest.json
E:\11.16\script2_new\training_data_new\time_gated_full_ie_v4_formal_conservative420_seed42\scenario_summary.csv
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_formal_dataset_statistics.csv
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_node_set_relationships.csv
E:\11.16\script2_new\chapter3_data_generation\outputs\chapter3_residual_energy_by_scenario.csv
E:\11.16\01 黄机项目资料情况\黄机排水系统.pdf
E:\11.16\01 黄机项目资料情况\黄机污水系统.pdf
E:\11.16\01 黄机项目资料情况\黄机流域水环境问题.pdf
E:\11.16\01 黄机项目资料情况\黄机流域整体调度现状与问题总结.docx
E:\11.16\01 黄机项目资料情况\武汉市黄孝河、机场河水环境综合治理二期PPP项目主要子项功能.docx
```

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

第4章在第3章 IE420 time-gated 连续缺陷场景基础上，研究固定 `degree N25` 稀疏监测布局下的 I/E 缺陷诊断与候选节点定位问题。模型保留 128 节点全图拓扑，使用 25 个监测节点动态观测，在 50 个候选缺陷节点空间内形成定位排序；诊断链条组织为“滑动窗口样本 -> 窗口级诊断证据 -> 场景级活跃期定位 -> 场景级空间定位 -> 综合诊断”。

### 第4章可写事实

- 正式缺陷类型：I/E。
- 正式缺陷矩阵：IE420。
- 正式数据口径：time-gated，即缺陷在 `start_hour` 和 `duration_h` 定义的时间段内激活。
- 图输入范围：全网 128 节点拓扑。
- 固定监测布局：`degree N25`，25 个监测节点。
- 定位评价空间：50 个候选缺陷节点。
- 正式训练入口：`scripts/train_privileged_teacher_student.py`。
- 正式输入协议：full-graph sparse-observation，保留拓扑和 observed mask，非观测节点动态特征不作为可见观测。
- 正式空间定位基线：`sequence_length=36`，约 6 h；`window_stride=6`，约 1 h。
- 第5章任务：在第4章固定诊断任务、模型协议和候选空间基础上优化监测节点集合 `S`。

### 第4章核心证据来源

```text
E:\11.16\thesis_writing_repo\chapters\ch4_model_diagnosis.md
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\thesis_writing_repo\ppt\part4_model_diagnosis_ppt_text.md
E:\11.16\script2_new\scripts\README.md
E:\11.16\script2_new\scripts\train_privileged_teacher_student.py
E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py
E:\11.16\script2_new\scripts\summarize_time_window_length_eval.py
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.csv
E:\11.16\script2_new\input_1\defect_matrix_diverse_ie_v4_formal_conservative420_seed42.summary.json
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
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_candidate_observability_counts.csv
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
E:\11.16\script2_new\scripts\README.md
```

### 禁止越界

- 不写“模型完成 I/E 类型分类”。
- 不把 `logits_defect_type` 的存在等同于正式类型分类结果。
- 不把 full-graph sparse-observation 写成全节点动态观测可见。

## 第4章第4.3节 训练协议与评价指标

### 本节要支撑的表述

第4章评价指标按任务链分层组织：窗口级 active 识别、窗口级节点定位、场景级活跃期定位、场景级空间定位和综合诊断审查。`scenario split` 是正式主协议，`node_holdout` 是泛化压力测试。

### 可写事实

- `scenario split` 保证同一场景窗口不跨训练、验证和测试集合。
- `node_holdout` 用于未见缺陷节点压力测试，不作为正式主性能口径。
- 窗口级 active 指标：Active Accuracy、Active Recall、Active-period Recall。
- 节点定位指标：MRR、Top-1、Top-3、Top-5。
- 场景级空间定位指标：Event Top-1、Event Top-3、Event Top-5。
- 场景级活跃期定位指标：onset error、±1/±2/±3 窗口命中、active interval IoU。
- 综合诊断指标：起点命中与节点 Top-K 同时满足的联合指标，作为补充审查。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch4_task_metric_definition.md
E:\11.16\script2_new\utils\evaluation.py
E:\11.16\script2_new\scripts\evaluate_scene_timeline_diagnosis.py
E:\11.16\script2_new\scripts\summarize_time_window_length_eval.py
```

### 禁止越界

- 不把 true-active 聚合 Event Top-K 写成完整 predicted-active 综合诊断结果。
- 不把 predicted-active scene Top-K 写成纯空间定位能力。

## 第4章第4.4节 缺陷诊断主实验结果

### 本节要支撑的表述

在固定 `degree N25` sparse-observation 协议和 IE420 time-gated 数据下，主模型能够稳定完成窗口级诊断证据提取和场景级事件定位；与三类基线相比，主模型具有明显优势；窗口长度实验揭示时间段定位与空间定位稳定性之间的尺度权衡。

### 可写事实

- 正式主线为 `ch1_fullgraph_degree_ie420_s*_fix1`。
- 主模型 seed 7/42/123 已完成多种子复核。
- 主模型三种子均值：MRR=0.7778，Top-1=0.6426，Top-5=0.9503，Event Top-5=0.9735，Active Recall=0.9590。
- seed42 主结果：MRR=0.7933，Top-1=0.6721，Top-5=0.9545，Event Top-5=0.9841。
- 多 seed 模型对比均值：
  - `hydraulic_inverse_deepattn`：MRR=0.7778，Top-5=0.9503，Event Top-5=0.9735。
  - `gru_gcn`：MRR=0.2049，Top-5=0.2585，Event Top-5=0.2646。
  - `hydraulic_inverse`：MRR=0.3423，Top-5=0.4211，Event Top-5=0.4550。
  - `lstm_graphsage_edge`：MRR=0.4139，Top-5=0.4522，Event Top-5=0.4656。
- 窗口长度实验：
  - 2h：onset error=0.7131h，interval IoU=0.9124，窗口 Top-5=0.9303。
  - 3h：onset error=0.8497h，interval IoU=0.8455，窗口 Top-5=0.9044。
  - 6h：onset error=2.2151h，interval IoU=0.7226，窗口 Top-5=0.9545。
- I/E 分组定位：
  - I 类：MRR=0.8076，Top-1=0.6862，Top-5=0.9711。
  - E 类：MRR=0.7377，Top-1=0.5838，Top-5=0.9224。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\CH4_RESULT_AUDIT_FOR_WRITING.md
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_main_model_multiseed.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_model_comparison_multiseed_long.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_ie_type_group_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_main_multiseed.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_model_comparison_multiseed.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_ie_type_group.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_tradeoff.png
```

### 可写边界

- 6h 是空间定位主基线，用于第5章衔接。
- 2h/3h 是时间段定位补充分析，不替代第5章空间定位基线。
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
- 6h predicted-active scene Top-5=0.3175；2h predicted-active scene Top-5=0.1587；该指标不替代 true-active Event Top-K。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_nodehold_observability_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\chapter4_candidate_observability_counts.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\time_window_length_eval\chapter4_time_window_length_eval_summary.csv
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_split_vs_nodehold.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_observability_analysis.png
E:\11.16\script2_new\chapter4_diagnosis_model\outputs\thesis_results\figures\fig_ch4_timeline_case.png
```

### 禁止越界

- 不把 node_holdout 写成已经解决未见节点泛化。
- 不把 predicted-active scene Top-K 低写成主模型空间定位失败。
- 不把 oracle active 结果写成实际模型诊断性能。

## 第5章 诊断反馈驱动的监测节点布局优化

### 第5章总论要支撑的表述

第5章在第3章 IE420 母数据和第4章诊断任务、模型结构、窗口设置与评价协议固定的前提下，只改变监测节点集合 `S` 与 observed mask，研究监测布局对 I/E 缺陷空间定位性能的影响。本章主线是从人工规则选点走向诊断结果反馈指导布点，正式学习型方法采用 clean 双层口径：`v0_2 clean` 表示节点级反馈学习，`v2_2 clean` 表示布局级代理搜索。

### 第5章核心可写事实

- 固定内容：IE420 母数据、128 节点全图拓扑、50 个候选缺陷节点、第4章诊断任务、模型结构、窗口设置与评价协议。
- 唯一变化：监测节点集合 `S`、`monitor_nodes_file`、observed mask。
- 主评价：`scenario split`、预算 `N=25`、seed 7/42/123。
- 主排名指标：MRR、Top-1、Top-3、Top-5、event-level Top-K 空间定位指标。
- 不作为第5章主排名：onset error、active interval IoU、活跃期起止边界误差。
- 人工规则与任务驱动基线：`Degree`、`Cand-Obs`、`Two-stage v1`。
- clean 学习型主线：
  - `v0_2 clean`：节点级反馈学习，回答“哪些节点值得被选”。
  - `v2_2 clean`：布局级代理搜索，回答“哪些节点组合整体更优”。
- `v0_2 generalization` 可作为性能参考或内部记录，不作为中期正式主线。
- 旧 `v2_2`、`v1_1/v1_2/v1_3` 图上下文探索不进入中期正式答辩主线。

### 第5章核心证据来源

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_FINAL_EXPERIMENT_CLOSURE_AND_OUTLINE_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_4_node_holdout_boundary_seed42.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\ch5_thesis_main_results_by_seed.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_summary.csv
```

### 第5章禁止越界

- 不把第5章写成重新训练或重新定义诊断任务的章节。
- 不把第5章结果倒灌回第4章固定 `degree N25` 主结果。
- 不把 `node_holdout` 写成已经解决严格未见节点泛化。
- 不把非 clean 探索版本写入中期正式答辩主线。
- 不把结构指标更优直接写成诊断性能必然更优。

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
E:\11.16\script2_new\thesis_writing_package\03_CH5_WRITING_CONTEXT.md
```

### 禁止越界

- 不在问题定义里提前写方法优劣。
- 不把 `degree N25` 写成错误布局。

## 第5章第5.2节 固定诊断协议下的布局评价闭环

### 本节要支撑的表述

每个布局方案只改变监测节点集合和 observed mask，在相同数据、模型结构、窗口设置、训练评价协议和候选空间下比较空间定位结果。

### 可写事实

- 固定诊断任务、模型结构、窗口设置和评价协议。
- 不共用同一个 checkpoint，而是在相同协议下比较不同布局。
- 主排名只看空间定位指标。
- `node_holdout` 是压力测试，不是主排名。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\README.md
```

### 禁止越界

- 不用“同一诊断评价器固定”造成共用 checkpoint 的误解。
- 不把第4章活跃期定位指标混入第5章布局主排名。

## 第5章第5.3节 人工规则与任务驱动布局基线

### 本节要支撑的表述

`Degree`、`Cand-Obs` 和 `Two-stage v1` 构成人工规则与任务驱动基线，用于说明从拓扑中心性到候选可观测性和平衡约束的递进。

### 可写事实

- `Degree`：拓扑度数基线。
- `Cand-Obs`：候选可观测性布局。
- `Two-stage v1`：两阶段平衡布局。
- 结构统计：
  - `Degree`：direct=12，near=21，far=17，mean_hop=3.48。
  - `Cand-Obs`：direct=15，near=34，far=1，mean_hop=0.94。
  - `Two-stage v1`：direct=18，near=31，far=1，mean_hop=0.92。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_1_layout_structure.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\degree\summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\candidate_observability\summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layouts\two_stage_balanced_layout_v1\summary.csv
```

### 禁止越界

- 不把 `Two-stage v1` 写成第五章最高创新点；它是可解释规则框架和基线。

## 第5章第5.4节 诊断反馈驱动的学习型布局方法

### 本节要支撑的表述

第5章正式学习型方法采用 clean 双层口径：`v0_2 clean` 学习节点级布设价值，`v2_2 clean` 搜索布局级组合质量。二者不是版本堆叠，而是从“哪些节点值得选”到“哪些节点组合更优”的递进。

### 可写事实

- `v0_2 clean`：
  - MRR=0.8658±0.0142；
  - Top-1=0.7725±0.0111；
  - Top-5=0.9934±0.0029；
  - event Top-1=0.8254±0.0420。
- `v2_2 clean`：
  - MRR=0.8856±0.0423；
  - Top-1=0.8070±0.0675；
  - Top-5=0.9916±0.0100；
  - event Top-1=0.8307±0.0458。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\ch5_thesis_main_results_by_seed.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\structural_innovation\learnable_layout_network_v0_2_clean_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\structural_innovation\learnable_layout_network_v2_2_clean_summary.csv
```

### 可写边界

- 可以写 `v0_2 clean` 是节点级反馈学习。
- 可以写 `v2_2 clean` 是布局级代理搜索。
- 可以写 `v2_2 clean` 的 Top-1 更高，但方差较大。

### 禁止越界

- 不把 `v0_2 generalization` 当作中期正式主线。
- 不把 `v2_2 clean` 写成稳定全面最优。
- 不把学习型布局写成在线自适应布点。

## 第5章第5.5节 不同布局方案的空间定位结果

### 本节要支撑的表述

在主协议下，任务驱动和学习型布局整体优于 `Degree`，说明监测节点布局会显著影响空间定位性能。

### 可写事实

- `Degree`：MRR=0.7778±0.0146，Top-1=0.6426±0.0260，Top-5=0.9503±0.0366。
- `Cand-Obs`：MRR=0.8664±0.0381，Top-1=0.7827±0.0534，Top-5=0.9697±0.0247。
- `Two-stage v1`：MRR=0.8715±0.0257，Top-1=0.7811±0.0407，Top-5=0.9838±0.0064。
- `v0_2 clean`：MRR=0.8658±0.0142，Top-1=0.7725±0.0111，Top-5=0.9934±0.0029。
- `v2_2 clean`：MRR=0.8856±0.0423，Top-1=0.8070±0.0675，Top-5=0.9916±0.0100。
- Event Top-K 已补齐：`v2_2 clean` 的 event Top-3 为 0.9841±0.0000，event Top-5 为 1.0000±0.0000；其他方法见成品表。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_2_main_scenario_seed_summary_with_event_topk.csv
E:\11.16\script2_new\chapter5_layout_optimization\figures\ch5_fig_5_1_main_scenario_performance_mean_std.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_main_spatial_performance_event_topk.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_learning_level_comparison.png
```

### 已完成补强

- event Top-3 / event Top-5 成品表已补齐。
- 主性能图已更新为 clean 双层主线。

### 禁止越界

- 不用 seed42 单次结果替代多 seed 主结论。
- 不把 node_holdout 放入主排名。

## 第5章第5.6节 预算、难点候选与泛化边界分析

### 本节要支撑的表述

预算变化、难点候选、布局相似度和 node_holdout 用于补强机制与边界，而不是推翻主结果。

### 已有事实

- `Degree` 的 `far` 候选数量为 17。
- `Cand-Obs` 和 `Two-stage v1` 的 `far` 候选数量为 1。
- `Degree N25` 下已定义 17 个 `far` 候选作为 hard candidates 清单。
- Jaccard 热力图显示 `v0_2 clean` 与 `v2_2 clean` 的节点集合相似度为 0.47，高于二者与人工规则布局的相似度。
- `node_holdout` 下所有方法整体下降，说明严格未见节点泛化仍是边界。

### 已完成补强

- 预算结构趋势表与图已完成，但只支持结构变化，不支持性能变化结论。
- direct / near / far 结构堆叠图已完成。
- hard candidates 定义清单已完成，性能分层仍待逐候选结果。
- Jaccard 布局相似度已完成。
- surrogate 可信度散点图已完成。

### 数据与文件来源

```text
E:\11.16\script2_new\chapter5_layout_optimization\outputs\layout_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_6_budget_observability_summary.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_7_layout_jaccard_similarity.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_8_surrogate_prediction_quality.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_9_hard_candidate_definition.csv
E:\11.16\script2_new\chapter5_layout_optimization\outputs\thesis_tables\table_5_4_node_holdout_boundary_seed42.csv
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_budget_observability_curve.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_direct_near_far_stack.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_layout_jaccard_heatmap.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_surrogate_prediction_scatter.png
E:\11.16\script2_new\chapter5_layout_optimization\figures\fig_ch5_node_holdout_boundary.png
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
```

### 禁止越界

- 不把 `node_holdout` 写成正式主排名。
- 不把预算结构趋势写成性能趋势，除非后续补齐训练结果。

## 第5章第5.7节 本章小结

### 本节要支撑的表述

第5章可总结为：传统拓扑布局不是定位任务最优；候选可观测性和两阶段平衡布局提供任务驱动规则基线；clean 学习型布局进一步将诊断结果反馈用于节点级价值学习和布局级组合搜索；未见节点泛化和难点候选改善仍需后续补充实验。

### 数据与文件来源

```text
E:\11.16\thesis_writing_repo\chapters\ch5_experiment_plan.md
E:\11.16\thesis_writing_repo\notes\evidence_map.md
E:\11.16\script2_new\chapter5_layout_optimization\docs\CH5_THESIS_MAIN_RESULTS_SEED_SUMMARY_20260413.md
```

### 禁止越界

- 不新增正文没有证明的优势。
- 不把第5章写成已形成可直接现场部署的最终布点规范。

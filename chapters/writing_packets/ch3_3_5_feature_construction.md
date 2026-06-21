## 3.5 节点时序特征构造

### 3.5.1 原始时序特征组织

3.4节通过PySWMM批量仿真获得了全网节点级水力水质时序数据。该数据以场景、时间和节点为基本索引，记录不同I/E缺陷场景、reference场景和normal扰动场景下128个节点的动态响应。对于任一场景 (s)，其原始时序可表示为：

[
\mathbf{X}^{raw}*{s} \in \mathbb{R}^{T \times N \times F*{raw}}
]

其中，(T=287) 表示48 h观测窗口内的有效时间点数，(N=128) 表示研究子区全网节点数，(F_{raw}) 表示原始输出变量数。SWMM批量仿真输出共包含16类节点变量，其中水力变量7类，包括 `depth`、`head`、`volume`、`lateral_inflow`、`total_inflow`、`total_outflow` 和 `flooding`；水质变量9类，包括BODf、BODs、NH4、NO3、DO、TSSs、TSSn、TR_in和TR_ww。

原始时序特征直接反映排水管网在不同运行状态下的节点响应。水力变量描述节点水深、流量交换和蓄水状态，能够表征I/E水量扰动引起的局部变化及上下游传播过程；水质变量描述污染物浓度随水流输移、混合和停留时间变化产生的伴随响应。将上述变量按照 ((scenario_id, time_step, node_id)) 三维索引统一组织后，可以形成面向时空图模型的节点级特征张量。

在正式诊断任务中，原始时序并不直接以全部16类变量进入模型，而是在完整输出基础上进行任务导向的特征选择。该处理保留SWMM水力水质仿真的完整输出，同时使第4章诊断模型的输入变量更加集中于I/E水量异常响应及其可观测伴随变化。

### 3.5.2 正式输入变量选择

本文正式诊断特征从水力响应、水质伴随响应和工程可获取性三个方面进行选择。水力响应方面，I/E缺陷首先改变节点水量平衡和上下游输移过程，因此选择 `depth` 和 `total_outflow` 作为主要水力特征。`depth` 表征节点水位状态，能够反映入流增加、流量削减及下游控制条件变化对节点水深的影响；`total_outflow` 表征节点出流过程，能够反映缺陷扰动在管网中的输移和汇流响应。

水质伴随响应方面，本文选择 `pollut_NH4` 和 `pollut_TSSs` 作为正式水质输入变量。NH4代表溶解性氮素组分，TSSs代表可沉降悬浮物组分，二者能够从浓度变化角度补充描述I/E水量扰动引起的稀释、混合和停留时间变化。水质变量在本文中作为伴随响应特征，与水力变量共同构成多变量节点状态输入。

工程可获取性方面，水深、流量、氨氮和悬浮物均属于排水管网监测和水环境评估中较常见的指标。将这些变量纳入正式输入，有助于保持仿真特征与工程监测指标之间的对应关系。由此，本文从完整SWMM输出中确定4个正式原始变量：

[
\mathbf{x}^{raw} =
[\text{depth},\ \text{total_outflow},\ \text{pollut_NH4},\ \text{pollut_TSSs}]
]

其中，`depth` 和 `total_outflow` 构成水力状态输入，`pollut_NH4` 和 `pollut_TSSs` 构成水质伴随输入。后续residual和relative residual特征均基于这4个正式变量派生得到。

### 3.5.3 Residual与relative residual特征构造

不同节点的管径、高程、上下游位置和DWF基准流量存在差异。为突出I/E缺陷相对于正常运行状态的增量变化，本文以无缺陷reference场景作为逐时刻、逐节点、逐变量的参照基准，构造residual派生特征。对于场景 (s)、时间步 (t)、节点 (n) 和变量 (f)，绝对残差定义为：

[
r_{s,t,n,f} = x_{s,t,n,f} - x_{ref,t,n,f}
]

其中，(x_{s,t,n,f}) 为场景 (s) 下变量 (f) 的节点响应，(x_{ref,t,n,f}) 为reference场景在相同时间步和相同节点上的对应响应。绝对残差 (r_{s,t,n,f}) 表示当前场景相对于无缺陷基准状态的偏离方向和偏离幅度。对于I类渗入场景，部分节点可能表现为水深或出流量增加；对于E类渗漏场景，部分节点可能表现为流量削减及上下游响应重分布。通过reference对齐，缺陷响应被转化为相对于正常运行轨迹的增量表达。

在绝对残差基础上，本文进一步构造相对残差，用于表达缺陷偏离相对于节点正常量级的比例关系。相对残差定义为：

[
r^{rel}*{s,t,n,f} = \frac{x*{s,t,n,f} - x_{ref,t,n,f}}{|x_{ref,t,n,f}| + \epsilon}
]

其中，(\epsilon = 10^{-8})，用于保证数值计算稳定。相对残差将绝对偏差转换为相对于reference响应的比例偏差，使不同基准量级节点上的异常变化能够在统一尺度下表达。该特征与3.2节中节点DWF基准流量跨量级分布相对应，有助于增强不同水力条件节点之间的特征可比性。

reference场景和normal扰动场景在特征构造中承担不同功能。reference场景提供residual计算所需的统一对齐基准；normal扰动场景在同一无缺陷运行机制下提供正常波动样本。缺陷场景、reference场景和normal扰动场景均共享相同SWMM模型结构、DWF输入机制和输出变量定义，因此residual特征能够在统一时间索引和统一节点索引下构造。

【可选图文段：若3.5配特征构造图，保留本段；若暂不配图，删除本段】

为展示原始时序、reference对齐、绝对残差和相对残差之间的构造关系，本文设置特征构造示意图，如图3-X所示。该图以单个场景的节点级时序为输入，展示从SWMM原始输出到 `raw_plus_residual` 输入特征的转换过程。

【图3-X占位符：raw / residual / relative residual 特征构造流程】

建议待生成图件位置：
figures/ch3/generated_results/10_CH3_raw_residual_feature_construction/10_CH3_raw_residual_feature_construction.svg

建议备用位图：
figures/ch3/generated_results/10_CH3_raw_residual_feature_construction/10_CH3_raw_residual_feature_construction.png

建议图源：
figures/ch3/source_data/CH3-F05_residual_feature_definition.csv

图3-X体现了正式输入特征的三层组织关系。第一层为raw特征，保留节点在当前场景下的水力水质状态；第二层为residual特征，表达当前场景相对于reference响应的绝对偏离；第三层为relative residual特征，表达偏离量相对于reference响应的比例变化。三层特征共同构成第4章诊断模型的 `raw_plus_residual` 输入，使模型同时获得节点状态、异常增量和相对偏离信息。

【可选图文段结束】

【可选图文段：若3.5前移数据有效性图，保留本段；若将图放入3.6，删除本段】

为展示residual特征在典型I/E场景中的响应形态，本文进一步引入normal20包络与缺陷residual曲线对比，如图3-X所示。图中以20个normal扰动场景构造正常波动包络，并将典型缺陷场景的水力residual曲线叠加到同一时间坐标下。

【图3-X占位符：normal20包络与典型I/E缺陷residual响应】

图件位置：
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02a_CH3_normal_envelope_defect_residual_case01.svg
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02b_CH3_normal_envelope_defect_residual_case02.svg

备用位图：
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02a_CH3_normal_envelope_defect_residual_case01.png
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02b_CH3_normal_envelope_defect_residual_case02.png

配套数据：
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02_CH3_normal_envelope_defect_residual_normal_envelope.csv
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02_CH3_normal_envelope_defect_residual_plot_timeseries.csv
figures/ch3/generated_results/02_CH3_normal_envelope_defect_residual/02_CH3_normal_envelope_defect_residual_selected_gallery_cases.csv

由图3-X可以看出，典型缺陷场景在缺陷活跃期内形成明确的residual响应，并与normal20正常波动包络形成可区分的时间过程。该结果表明，reference对齐后的residual特征能够突出缺陷场景相对于正常运行状态的增量变化，为第4章基于时间窗口的活跃检测和缺陷定位提供输入基础。

【可选图文段结束】

### 3.5.4 正式特征矩阵与输入组织

综合原始状态、绝对残差和相对残差三类表达，本文正式采用 `raw_plus_residual` 作为第4章和第5章诊断模型的输入特征集。该特征集共包含12维变量，其中原始特征4维、绝对残差4维、相对残差4维，如表3-10所示。

**表3-10  正式输入特征定义**

| 特征类别   | 特征变量                         | 维度 | 含义                    |
| ------ | ---------------------------- | -: | --------------------- |
| 原始水力   | `depth`                      |  1 | 节点水深状态                |
| 原始水力   | `total_outflow`              |  1 | 节点总出流状态               |
| 原始水质   | `pollut_NH4`                 |  1 | NH4浓度状态               |
| 原始水质   | `pollut_TSSs`                |  1 | TSSs浓度状态              |
| 水力残差   | `depth_residual`             |  1 | 水深相对于reference的偏差     |
| 水力残差   | `total_outflow_residual`     |  1 | 总出流量相对于reference的偏差   |
| 水质残差   | `pollut_NH4_residual`        |  1 | NH4浓度相对于reference的偏差  |
| 水质残差   | `pollut_TSSs_residual`       |  1 | TSSs浓度相对于reference的偏差 |
| 水力相对残差 | `depth_residual_rel`         |  1 | 水深相对偏差                |
| 水力相对残差 | `total_outflow_residual_rel` |  1 | 总出流量相对偏差              |
| 水质相对残差 | `pollut_NH4_residual_rel`    |  1 | NH4浓度相对偏差             |
| 水质相对残差 | `pollut_TSSs_residual_rel`   |  1 | TSSs浓度相对偏差            |

表3-10表明，正式输入特征同时保留节点原始状态、相对于reference的绝对偏离以及相对于正常量级的比例偏离。原始特征提供当前场景下的节点运行状态，绝对残差突出缺陷引起的增量响应，相对残差增强不同基准量级节点之间的可比性。三类特征在同一时间步和同一节点上对齐，共同形成面向I/E缺陷诊断的节点特征表示。

对于每个场景，最终特征矩阵可表示为：

[
\mathbf{X}_{s} \in \mathbb{R}^{287 \times 128 \times 12}
]

其中，287为时间点数，128为全网节点数，12为正式输入特征维度。所有场景均按照相同节点顺序和相同时间索引组织，使不同场景之间可以在场景维度上直接堆叠，并进一步转换为模型训练所需的批量输入。

在第4章诊断模型训练中，(\mathbf{X}_{s}) 通过滑动时间窗口切分为窗口级样本。设窗口长度为 (L)，则单个窗口样本可表示为：

[
\mathbf{X}_{s,\tau:\tau+L} \in \mathbb{R}^{L \times 128 \times 12}
]

其中，(\tau) 为窗口起始时间步。窗口样本对应缺陷活跃标签和候选节点定位标签，用于支持窗口级活跃检测、场景级报警和缺陷节点排序。

由于第4章和第5章均在稀疏观测条件下开展诊断实验，本文进一步引入观测掩码 (\mathbf{M}) 表示监测节点集合。对于给定监测布局 (\mathcal{S})，观测掩码定义为：

[
M_n =
\begin{cases}
1, & n \in \mathcal{S} \
0, & n \notin \mathcal{S}
\end{cases}
]

在模型输入中，监测节点对应有效观测，非监测节点对应掩码输入。第4章采用Degree-N25固定监测布局，第5章在保持数据集、缺陷协议和诊断模型一致的基础上改变监测节点集合。由此，3.5节构造的全网特征矩阵既支持固定布局诊断，也支持后续监测布局优化实验。

【可选图文段：若3.5配空间residual图，保留本段；若将图放入3.6，删除本段】

为展示residual特征在管网空间中的分布形式，本文设置管网空间residual传播图，如图3-X所示。该图在研究子区管网拓扑底图上展示缺陷发生前、活跃期、峰值时刻和缺陷结束后的水力residual分布。

【图3-X占位符：管网空间residual传播图】

图件位置：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map.svg

备用位图：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map.png

配套数据：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map_active_node_energy.csv

图3-X表明，residual响应在缺陷活跃期内呈现与管网拓扑相关的空间分布，并随时间在相邻或水力连接节点之间展开。该空间响应形态与本文后续采用图结构建模相对应：节点特征提供局部水力水质状态，管网拓扑提供节点之间的传播关系，时空图模型则在有限观测条件下聚合监测节点响应并输出候选缺陷节点排序。

【可选图文段结束】

综上，3.5节完成了从SWMM原始节点级时序到诊断模型输入特征的转换。原始变量选择保证特征与I/E水量扰动及其伴随水质响应相对应；reference对齐和residual构造突出缺陷相对于正常运行状态的增量变化；relative residual进一步提供跨节点尺度可比的比例偏离；观测掩码则将全网仿真数据转换为稀疏监测条件下的模型输入。后续3.6节将从场景完整性、时间一致性和响应有效性角度，对正式数据集进行质量验证。

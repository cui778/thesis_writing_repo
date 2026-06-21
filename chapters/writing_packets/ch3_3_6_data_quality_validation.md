## 3.6 数据质量验证

### 3.6.1 场景完整性与时间一致性检查

在完成I/E缺陷场景批量仿真和节点时序特征构造后，本文从场景完整性、时间一致性、节点覆盖性和特征一致性四个方面对正式数据集进行质量验证。该步骤用于确认第3章生成的数据能够稳定支撑第4章固定监测布局下的缺陷诊断实验，以及第5章监测布局优化实验。

场景完整性方面，IE420缺陷母数据包含1个reference场景和420个I/E缺陷场景，共421个场景；加入20个normal扰动场景后，正式合并数据集共包含441个场景。420个缺陷场景由250个I类渗入场景和170个E类渗漏场景构成，与3.3节定义的正式IE420缺陷协议一致。reference场景、缺陷场景和normal扰动场景均基于同一SWMM基线模型和正常输入机制生成，保证不同场景之间具有统一的模型基础。

时间一致性方面，正式合并数据集中所有场景均采用48 h连续观测窗口和10 min采样间隔，每个场景保留287个有效时间点。所有场景共享统一的时间索引，因此任意缺陷场景或normal扰动场景均可与reference场景在同一时间步上逐节点对齐。该时间结构为3.5节中residual和relative residual特征构造提供了对齐基础，也为第4章滑动时间窗口样本构造提供了统一时间坐标。

节点覆盖性方面，所有场景均保留研究子区128个全网节点的节点级时序输出。缺陷注入空间由50个候选缺陷节点构成，其中I类渗入场景覆盖全部50个候选节点，E类渗漏场景覆盖34个具备入流管段条件的候选节点。第4章固定监测节点集采用Degree-N25布局，包含25个监测节点；监测节点集与候选缺陷节点集存在12个重叠节点。上述节点集合关系与3.3节定义一致，保证缺陷注入、全网输出和稀疏观测输入之间的空间对象统一。

特征一致性方面，正式数据集以统一节点顺序和统一时间索引组织特征矩阵。每个场景对应 (287 \times 128 \times 12) 的 `raw_plus_residual` 特征结构，其中12维特征由4维原始变量、4维绝对残差和4维相对残差组成。所有特征均由3.5节定义的变量选择和reference对齐规则生成，使不同场景之间能够在相同变量空间中直接比较。

正式数据集的完整性检查结果如表3-11所示。

**表3-11  正式数据集完整性与一致性检查**

| 检查项目        | 检查结果 | 作用                                 |
| ----------- | ---: | ---------------------------------- |
| IE420母数据场景数 |  421 | 1个reference场景 + 420个I/E缺陷场景        |
| 正式合并数据集场景数  |  441 | reference + IE420 + normal20       |
| I类渗入场景数     |  250 | 覆盖50个候选缺陷节点                        |
| E类渗漏场景数     |  170 | 覆盖34个合法渗漏节点                        |
| normal扰动场景数 |   20 | 表征无缺陷正常波动                          |
| 全网节点数       |  128 | SWMM输出和图模型空间范围                     |
| 候选缺陷节点数     |   50 | I/E缺陷发生候选位置                        |
| 固定监测节点数     |   25 | 第4章Degree-N25观测布局                  |
| 每场景有效时间点数   |  287 | 48 h观测窗口，10 min采样间隔                |
| 正式输入特征维度    |   12 | raw + residual + relative residual |

表3-11表明，正式数据集在场景数量、节点数量、时间点数量和特征维度上形成统一结构。reference场景提供残差对齐基准，IE420缺陷场景提供受控异常样本，normal扰动场景提供正常波动样本；三类场景共同构成第4章和第5章共用的数据基础。该结构保证后续实验能够在同一数据集、同一缺陷协议和同一特征定义下展开。

### 3.6.2 缺陷响应有效性检查

在完整性与一致性检查基础上，本文进一步从典型响应、空间传播、强度分层和峰值动态四个角度检查缺陷响应特征。该部分重点分析I/E水量扰动是否能够在节点级时序数据中形成与缺陷活跃期、扰动强度和管网拓扑相对应的响应形态。

第一，典型场景与normal20包络对比用于展示缺陷响应相对于正常波动的偏离过程。以20个normal扰动场景构造正常波动包络，并将典型I/E缺陷场景的水力residual曲线叠加到同一时间坐标下，可以观察缺陷活跃期内residual响应的变化。代表性案例中，`depth_residual` 或 `total_outflow_residual` 在缺陷活跃区间内形成明显峰值，并与normal20包络呈现可区分的时间过程。两个代表性depth案例的包络外比例分别为0.740和0.476，缺陷响应绝对值相对normal包络95%分位数的比值分别为1.360和1.163。该结果说明，reference对齐后的水力residual能够突出缺陷场景相对于正常运行状态的增量变化。

【可选图文段：若3.6保留normal包络图，使用本段；若该图已放入3.5，删除本段】

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

由图3-X可以看出，典型I/E缺陷场景在缺陷活跃期内形成连续的水力residual响应，并与normal20包络呈现清晰区分。该图支撑了residual特征用于表达缺陷增量响应的合理性，也为第4章窗口级活跃检测提供了时间过程依据。

【可选图文段结束】

第二，管网空间residual分布用于展示缺陷响应的空间传播形态。在缺陷发生前、active期、峰值时刻和缺陷结束后的多个时间片上，水力residual在管网拓扑中的分布会随时间发生变化。缺陷活跃期内，高响应区域通常围绕缺陷节点及其水力连接区域展开，并在相邻或上下游节点之间形成空间关联。该结果说明，全网节点级输出中包含与管网拓扑相关的响应信息，为第4章采用图结构建模提供数据基础。

【可选图文段：若3.6保留空间residual图，使用本段；若该图已放入3.5，删除本段】

【图3-X占位符：管网空间residual传播图】

图件位置：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map.svg

备用位图：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map.png

配套数据：
figures/ch3/generated_results/04_CH3_topology_residual_spatial_map/04_CH3_topology_residual_spatial_map_active_node_energy.csv

图3-X展示了典型缺陷场景下residual响应从缺陷发生前到缺陷活跃期、峰值时刻和缺陷结束后的空间变化过程。图中高响应区域与管网连接关系共同构成空间定位信息，说明节点特征与拓扑结构可以共同服务于后续缺陷节点排序任务。

【可选图文段结束】

第三，缺陷强度分层响应用于展示扰动规模与水力residual峰值之间的关系。将场景按低、中、高强度分层后，可以观察不同强度水平下active区间内的响应差异；进一步对420个缺陷场景汇总绝对注入流量与active-window峰值水力响应，可以得到强度—响应关系。总体上，绝对缺陷流量较大的场景对应较高峰值响应的概率增加，同时节点基准流量、发生位置、持续时间和传播路径共同影响响应幅值。该结果说明，正式数据集中保留了强度差异及其引起的响应差异。

【可选图文段：若3.6保留强度分层图，使用本段；若图件作为附录或备答，删除本段】

【图3-X占位符：缺陷强度分层与峰值水力residual响应】

图件位置：
figures/ch3/generated_results/08_CH3_strength_stratified_event_response/08d_CH3_strength_response_scatter.svg

备用位图：
figures/ch3/generated_results/08_CH3_strength_stratified_event_response/08d_CH3_strength_response_scatter.png

配套数据：
figures/ch3/generated_results/08_CH3_strength_stratified_event_response/08_CH3_strength_stratified_event_response_summary.csv

图3-X展示了420个缺陷场景中绝对注入流量与active-window峰值水力响应之间的对应关系。随着缺陷流量增大，峰值响应整体呈增强趋势；同一强度水平下的离散分布反映出管网位置、节点基准流量和传播路径对响应过程的共同作用。该图补充说明IE420协议中的强度参数能够在仿真输出中形成可观测的响应差异。

【可选图文段结束】

第四，峰值出现时间与空间层级用于展示缺陷响应的动态过程。对420个缺陷场景逐一提取active区间内的峰值记录，可以统计峰值相对缺陷起点的时间位置及其主导拓扑层级。结果显示，不同场景的峰值响应分布在不同时间位置和不同拓扑层级上，体现了缺陷响应的时空传播差异。该结果与第4章滑动时间窗口建模和图结构聚合相衔接，为后续模型同时处理时间过程和空间传播关系提供数据依据。

【可选图文段：若3.6保留峰值时滞图，使用本段；若图件作为附录或备答，删除本段】

【图3-X占位符：缺陷响应峰值时滞与主导拓扑层级】

图件位置：
figures/ch3/generated_results/09_CH3_response_peak_timing/09_CH3_response_peak_timing.svg

备用位图：
figures/ch3/generated_results/09_CH3_response_peak_timing/09_CH3_response_peak_timing.png

配套数据：
figures/ch3/generated_results/09_CH3_response_peak_timing/09_CH3_response_peak_timing_peak_records.csv

图3-X展示了420个缺陷场景中active区间峰值响应的时间位置和主导拓扑层级。峰值响应分布于不同时间阶段和空间层级，说明I/E缺陷在管网中形成具有时滞特征和空间层级特征的动态响应。该图为第4章采用时间窗口样本和图结构聚合提供了数据支撑。

【可选图文段结束】

综合上述检查，正式数据集在场景结构、时间索引、节点覆盖和特征组织上保持一致，水力residual在典型场景、空间分布、强度分层和峰值动态方面均呈现与缺陷协议相对应的响应特征。NH4和TSSs作为水质伴随变量保留于正式输入特征中，与水力变量共同构成多变量节点状态表示；其具体贡献将在第4章通过输入特征对照实验进一步分析。

### 3.6.3 面向后续诊断实验的数据交付

经过3.6节质量验证，本文形成的正式数据集具备三方面特征。第一，数据口径稳定。正式数据集由reference、IE420缺陷场景和normal20扰动场景组成，场景数量、时间点数量、节点数量和特征维度均已统一。第二，响应特征明确。I/E水量扰动能够在节点级水力residual中形成与活跃期、强度和空间传播相关的响应形态。第三，实验接口统一。全网特征矩阵和观测掩码共同支持第4章固定监测布局诊断实验，也支持第5章在同一数据基础上的监测布局优化实验。

因此，第3章最终交付的数据对象可以概括为：

[
\mathcal{D} =
\left{
\mathbf{X}*{s} \in \mathbb{R}^{287 \times 128 \times 12},
\ y^{active}*{s,t},
\ y^{loc}*{s},
\ \mathbf{M}*{\mathcal{S}}
\right}
]

其中，(\mathbf{X}*{s}) 表示场景 (s) 的全网节点级特征矩阵，(y^{active}*{s,t}) 表示时间步或时间窗口上的缺陷活跃标签，(y^{loc}*{s}) 表示缺陷候选节点定位标签，(\mathbf{M}*{\mathcal{S}}) 表示给定监测节点集合下的观测掩码。该数据对象将第3章的仿真生成结果转化为第4章诊断模型可读取的输入—标签结构。

由此，第3章完成了从SWMM基线模型、I/E缺陷协议、PySWMM批量仿真、节点特征构造到数据质量验证的完整流程。下一节对本章工作进行概括，并衔接第4章固定监测布局下的时空图缺陷诊断模型构建与实验评价。

# 技术路线图 S5-CANDIDATE-IMAGE：正式候选图清单

## 1. 阶段边界

本轮仅执行 `S5-CANDIDATE-IMAGE`。

- 已分别生成 3 张正式 raster 候选图；
- 每张候选图均单独生成；
- 未拼接候选板；
- 已执行事实核对；
- 未筛选最终方案；
- 未进入 `S6-FINAL-SELECT`。

生成方式：

```text
内置 image_gen
```

候选合同：

`E:\11.16\thesis_writing_repo\notes\technical_route_s4_candidate_briefs_top-horizontal_lower-vertical.md`

## 2. 正式候选图

### CANDIDATE-A：均衡论文版

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s5_formal_candidates\CANDIDATE-A_balanced-thesis-page.png`

视觉特征：

- 上层数据底座完整；
- 左下诊断模型完整且较克制；
- `水力传播关联建模` 可见；
- 右侧方法演进清楚；
- 页面密度适中。

事实核对：

| 检查项 | 结果 | 说明 |
|---|---|---|
| residual 箭头进入第 4 章稀疏观测输入 | `PASS` | 蓝灰折线箭头准确落入 `稀疏观测时空图输入` |
| 橙色桥梁进入第 5 章监测节点布局优化 | `FAIL` | 箭头视觉上落入最终 `面向缺陷诊断的监测节点优化方案` |
| 水力传播关联建模可见 | `PASS` | 深绿色模块清楚 |
| 右侧方法演进清楚 | `PASS` | 三层方法关系清楚 |

### CANDIDATE-B：诊断创新突出版

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s5_formal_candidates\CANDIDATE-B_diagnosis-innovation.png`

视觉特征：

- 第 4 章诊断模型视觉权重最高；
- `水力传播关联建模` 使用深绿色并配有轻量管网示意；
- 双输出与场景级聚合清楚；
- 右侧方法演进完整。

事实核对：

| 检查项 | 结果 | 说明 |
|---|---|---|
| residual 箭头进入第 4 章稀疏观测输入 | `FAIL` | 蓝灰跨区域箭头方向与交付路径发生串线，未清楚表达“上层 residual 向下并向左交付” |
| 橙色桥梁进入第 5 章监测节点布局优化 | `FAIL` | 图中出现通向最终方案的橙色路径，桥梁语义不够唯一 |
| 水力传播关联建模可见 | `PASS` | 三张候选中最突出 |
| 右侧方法演进清楚 | `PASS` | 三层方法关系清楚 |

### CANDIDATE-C：简洁整页版

文件：

`E:\11.16\thesis_writing_repo\figures\technical_route\s5_formal_candidates\CANDIDATE-C_concise-thesis-page.png`

视觉特征：

- 整体留白较多；
- 模块标签精简；
- 两条跨区域箭头具有较强可读性；
- 水力传播关联建模与右侧方法演进仍然保留。

事实核对：

| 检查项 | 结果 | 说明 |
|---|---|---|
| residual 箭头进入第 4 章稀疏观测输入 | `PASS` | 蓝灰箭头从上层 residual 特征向下并向左，落入第 4 章输入卡片 |
| 橙色桥梁进入第 5 章监测节点布局优化 | `PASS` | 橙色箭头从固定布局诊断验证进入 `监测节点布局优化` |
| 水力传播关联建模可见 | `PASS` | 深绿色模块可见 |
| 右侧方法演进清楚 | `PASS` | 拓扑、规则和信息驱动布局关系清楚 |

## 3. 横向核对

| 检查项 | CANDIDATE-A | CANDIDATE-B | CANDIDATE-C |
|---|---|---|---|
| residual 箭头落点 | `PASS` | `FAIL` | `PASS` |
| 橙色桥梁落点 | `FAIL` | `FAIL` | `PASS` |
| 水力传播关联建模可见 | `PASS` | `PASS` | `PASS` |
| 右侧方法演进清楚 | `PASS` | `PASS` | `PASS` |

## 4. S5 检查结论

本轮只记录事实，不进行最终筛选。

```text
CANDIDATE-A：
结构均衡，但橙色桥梁落点需要修订。

CANDIDATE-B：
诊断创新表达最强，但跨区域箭头存在串线，需要修订。

CANDIDATE-C：
两条跨区域箭头均满足合同，结构简洁。
```

## 5. 提示词策略记录

三张候选均使用正式学术框架图提示词，并共同锁定：

- 横向 `16:9` 画布；
- 上层第 3 章横向数据底座；
- 左下第 4 章竖向诊断泳道；
- 右下第 5 章竖向优化泳道；
- 低饱和蓝灰、绿色和橙色；
- 章节虚线边界；
- residual 向第 4 章输入交付；
- 固定布局诊断验证向第 5 章布局优化交付；
- 无反馈回环；
- 无实验参数；
- 无海报式装饰。

差异化提示：

| 候选 | 提示词重心 |
|---|---|
| CANDIDATE-A | 均衡、正文可读性、适度图标 |
| CANDIDATE-B | 诊断模型内部结构、水力传播关联、双输出 |
| CANDIDATE-C | 简洁、留白、减少交叉线、准确箭头落点 |

## 6. S6 使用说明

进入 `S6-FINAL-SELECT` 时，应：

1. 比较三张正式候选；
2. 结合事实核对结果选择最终方向；
3. 对未满足合同的箭头问题给出修订意见；
4. 返回最终标题、图注草稿、图例和正文引用句；
5. 不自动进入 `S7-FINAL-JOINT-AUDIT`。

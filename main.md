# 论文正文草稿

> 当前阶段：Markdown 内容草稿。  
> 排版阶段：内容稳定后再转换为 Overleaf/LaTeX 或学校 Word 模板。

## 论文题目暂定

面向排水管网缺陷诊断的时空图建模与监测点布设优化研究

## 写作顺序

1. 第3章：基于SWMM的I/E缺陷多场景数据生成
2. 第4章：固定监测布局下的缺陷诊断与定位模型
3. 第5章：面向定位性能提升的监测点布设优化
4. 第6章：总结与展望
5. 第1章：绪论
6. 第2章：研究区域与研究方法
7. 摘要、目录、图表清单、格式整理

## 写作导航入口

每次写作前先打开：

- [网页端论文写作入口](WEB_WRITING_START_HERE.md)
- [第4章结果证据矩阵](chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md)
- [第5章结果证据矩阵](chapters/CH5_RESULTS_EVIDENCE_MATRIX_FINAL.md)
- [第4、5章结果逻辑](chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md)
- [正式数据源政策](figures/DATA_SOURCE_POLICY.md)

固定顺序：

```text
确认章级主线与正式口径
-> 建立当前二级节写作包
-> 读取本节对应表格、图件和代码证据
-> 按三级节逐段撰写
-> 单节事实与结论边界审查
-> 全章跨节一致性检查
-> 最终语言润色
```

## 章节入口

- [第1章 绪论](chapters/ch1_intro.md)
- [第2章 研究区域与研究方法](chapters/ch2_theory_and_related_work.md)
- [第3章 基于SWMM的I/E缺陷多场景数据生成](chapters/ch3_data_generation.md)
- [第4章 固定监测布局下的缺陷诊断与定位模型](chapters/ch4_model_diagnosis.md)
- [第5章 面向定位性能提升的监测点布设优化](chapters/ch5_layout_optimization.md)
- [第6章 总结与展望](chapters/ch6_conclusion.md)

## 写作检查

每完成一个小节后检查：

- 本节是否只回答一个核心问题？
- 本节是否遵循 [网页端论文写作入口](WEB_WRITING_START_HERE.md) 中的正式口径？
- 每个数值是否能追溯到正式结果表或 cleaned CSV？
- 正文引用的图件是否属于对应章节正式图件索引？
- 是否误用了旧实验口径？
- 是否把 50 个候选节点定位误写成 128 节点自由定位？
- 是否把 I/E 缺陷误写成 P 类水质污染源定位？
- 是否区分了 scenario split 和 node_holdout？

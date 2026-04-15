# 论文正文草稿

> 当前阶段：Markdown 内容草稿。  
> 排版阶段：内容稳定后再转换为 Overleaf/LaTeX 或学校 Word 模板。

## 论文题目暂定

面向排水管网缺陷诊断的时空图建模与监测点布设优化研究

## 写作顺序

1. 第3章：数据构建与任务定义
2. 第4章：固定监测布局下的缺陷诊断与定位模型
3. 第5章：面向定位性能提升的监测点布设优化
4. 第6章：总结与展望
5. 第1章：绪论
6. 第2章：理论基础与相关研究
7. 摘要、目录、图表清单、格式整理

## 写作导航入口

每次写作前先打开：

- [章节阅读路线图](notes/chapter_reading_routes.md)
- [证据地图](notes/evidence_map.md)
- [小节规划提示词](prompts/plan_one_section.md)
- [小节写作提示词](prompts/write_one_section.md)
- [事实审查提示词](prompts/review_one_section.md)

固定顺序：

```text
先读路线图
-> 让 AI 规划当前小节
-> 读取计划中列出的证据
-> 更新证据地图
-> 写正文
-> 审查事实
-> 提交版本
```

## 章节入口

- [第1章 绪论](chapters/ch1_intro.md)
- [第2章 理论基础与相关研究](chapters/ch2_theory_and_related_work.md)
- [第3章 数据构建与任务定义](chapters/ch3_data_generation.md)
- [第4章 固定监测布局下的缺陷诊断与定位模型](chapters/ch4_model_diagnosis.md)
- [第5章 面向定位性能提升的监测点布设优化](chapters/ch5_layout_optimization.md)
- [第6章 总结与展望](chapters/ch6_conclusion.md)

## 写作检查

每完成一个小节后检查：

- 本节是否只回答一个核心问题？
- 本节是否先参考了 [章节阅读路线图](notes/chapter_reading_routes.md)？
- 数据和结论是否已记录到 [证据地图](notes/evidence_map.md)？
- 是否误用了旧实验口径？
- 是否把 50 个候选节点定位误写成 128 节点自由定位？
- 是否把 I/E 缺陷误写成 P 类水质污染源定位？
- 是否区分了 scenario split 和 node_holdout？

# Thesis Writing Repository

本仓库用于管理论文正文草稿、正式实验口径、结果证据矩阵、图件及逐节写作规则。当前阶段先使用 Markdown 写正文，内容稳定后再根据学校模板转换为 Word 或 LaTeX 格式。

## 写作原则

1. 每次只写一个小节，不跨章节扩写。
2. 每个结论必须能追溯到实验表、图、过程记录或写作包。
3. 每次写作先读 [网页端论文写作入口](WEB_WRITING_START_HERE.md)，确认当前正式口径。
4. 第4、5章实验分析以对应结果证据矩阵和正式图件索引为准。
5. 正文先保证事实准确，再做语言润色。
6. 不使用旧高分口径、旧矩阵结果或已废弃实验作为正式主结论。
7. 第3章、第4章、第5章先写，第1章、摘要和结论最后回头写。

## 推荐工作流

```text
选择章节/小节
-> 打开 WEB_WRITING_START_HERE.md
-> 读取当前章节正文与章级证据矩阵
-> 读取正式图件索引和对应 cleaned/summary CSV
-> 建立当前二级节写作包
-> 按三级节逐段撰写
-> 运行单节事实与证据审查
-> 完成全章后执行跨节一致性检查
-> 最后进行语言润色
-> Git 提交
```

仓库内写作 skill：

```text
codex_skills/chinese-engineering-thesis-writing/
```

正文与证据入口：

```text
WEB_WRITING_START_HERE.md
chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md
chapters/CH5_RESULTS_EVIDENCE_MATRIX_FINAL.md
figures/ch3/generated_results/CH3_OFFICIAL_FIGURE_INDEX.md
figures/ch4/generated_results/CH4_OFFICIAL_FIGURE_INDEX.md
figures/ch5/generated_results/CH5_OFFICIAL_FIGURE_INDEX.md
```

主要实验材料位置：

```text
E:\11.16\script2_new\outputs\reports
E:\11.16\script2_new\chapter3_data_generation
E:\11.16\script2_new\chapter4_diagnosis_model
E:\11.16\script2_new\chapter5_layout_optimization
E:\11.16\process_diagnosis_revision_20260321
```

## 目录结构

```text
WEB_WRITING_START_HERE.md       网页端与新对话写作入口
main.md                         论文正文总入口
chapters/                       各章节正文、证据矩阵与写作包
figures/                        正式图件、绘图数据和数据源政策
codex_skills/                   论文、图件和PPT写作规则
```

## Git 提交粒度

建议每完成一个小节或一个工作流改动提交一次，例如：

```text
draft ch4 experiment protocol
polish ch4 main results
add evidence map for ch5 layout comparison
add chapter reading routes workflow
```

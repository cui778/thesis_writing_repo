# Thesis Writing Repository

本仓库用于管理论文正文草稿、章节阅读路线、证据地图和每日写作记录。当前阶段先使用 Markdown 写正文，暂不设置 Overleaf/LaTeX 模板；等内容稳定后，再根据学校模板转换为 Overleaf 或 Word 格式。

## 写作原则

1. 每次只写一个小节，不跨章节扩写。
2. 每个结论必须能追溯到实验表、图、过程记录或写作包。
3. 每章写作前先读 [章节阅读路线图](notes/chapter_reading_routes.md)，再决定本小节需要哪些材料。
4. 正文先保证事实准确，再做语言润色。
5. 不使用旧高分口径、旧矩阵结果或已废弃实验作为正式主结论。
6. 第3章、第4章、第5章先写，第1章、摘要和结论最后回头写。

## 推荐工作流

```text
选择章节/小节
-> 打开 notes/chapter_reading_routes.md
-> 读取全局口径和本章主线文件
-> 用 prompts/plan_one_section.md 让 AI 输出小节计划
-> 根据计划读取按需证据
-> 更新 notes/evidence_map.md
-> 用 prompts/write_one_section.md 写正文初稿
-> 用 prompts/review_one_section.md 做事实审查
-> 润色正文
-> Git 提交
```

写作包位置：

```text
E:\11.16\script2_new\thesis_writing_package
```

主导航文件：

```text
E:\11.16\thesis_writing_repo\notes\chapter_reading_routes.md
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
main.md                         论文总入口
chapters/                       各章节正文草稿
notes/chapter_reading_routes.md 每章写作前的阅读路线图
notes/evidence_map.md           论文结论与数据来源对应表
notes/writing_log.md            每日写作记录
notes/todo.md                   后续待办
prompts/plan_one_section.md     小节写作前规划提示词
prompts/write_one_section.md    小节正文写作提示词
prompts/review_one_section.md   小节事实审查提示词
```

## Git 提交粒度

建议每完成一个小节或一个工作流改动提交一次，例如：

```text
draft ch4 experiment protocol
polish ch4 main results
add evidence map for ch5 layout comparison
add chapter reading routes workflow
```

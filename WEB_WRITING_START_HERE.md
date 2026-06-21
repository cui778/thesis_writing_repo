# 网页端论文写作入口

本文件用于在新的网页对话中快速恢复论文写作上下文。开始写作前，应先读取本文件列出的正式正文、证据矩阵、图件索引和写作规则。

## 1. 当前正式正文

- `chapters/ch2_theory_and_related_work.md`
- `chapters/ch3_data_generation.md`
- `chapters/ch4_model_diagnosis.md`
- `chapters/ch4_task_metric_definition.md`
- `chapters/ch5_layout_optimization.md`

## 2. 结果逻辑与证据矩阵

- `chapters/CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md`
- `chapters/CH4_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- `chapters/CH5_RESULTS_EVIDENCE_MATRIX_FINAL.md`
- `chapters/writing_packets/`

## 3. 正式图件与数据索引

- `figures/DATA_SOURCE_POLICY.md`
- `figures/ch3/generated_results/CH3_OFFICIAL_FIGURE_INDEX.md`
- `figures/ch4/generated_results/CH4_OFFICIAL_FIGURE_INDEX.md`
- `figures/ch5/generated_results/CH5_OFFICIAL_FIGURE_INDEX.md`
- `figures/ch4/source_data/`
- `figures/ch5/source_data/`

图件分析应以 `generated_results` 中的当前正式图和对应 cleaned/summary CSV 为准，不使用 `old`、legacy 或其他历史目录。

## 4. 写作规则

仓库内写作 skill：

```text
codex_skills/chinese-engineering-thesis-writing/
```

执行方式固定为：

```text
章级主线
-> 当前二级节写作包
-> 按三级节逐段撰写
-> 单节证据审查
-> 全章跨节一致性检查
-> 最终语言润色
```

每次只撰写或审查一个二级节，不脱离正式证据一次性重写整章。

## 5. 固定实验口径

```text
dataset      = ie420_plus_normal20_v1
defect matrix= formal_conservative420_seed42
feature_set  = raw_plus_residual
chapter 4 layout = Degree-N25
chapter 4 model  = DeepAttn-L3
chapter 4 seeds  = 7, 42, 123
```

禁止自动采用 `persistent`、`fulltime`、`legacy`、`seedset10` 或其他历史数据。

IE420是用于方法开发和比较的受控仿真基准，不代表现实I/E缺陷的自然发生频率。I/E分组仅作补充观察。Reference用于residual对齐，normal20用于正常波动建模和误报评价。

## 6. 新网页对话建议提示词

```text
请先读取仓库根目录 WEB_WRITING_START_HERE.md，并使用
codex_skills/chinese-engineering-thesis-writing/SKILL.md 的流程继续论文写作。

本次只处理：【填写章节，例如 3.3 正式IE420缺陷协议】。

请先核对当前正文、证据矩阵、正式图件索引和对应CSV，再开始撰写。
不得编造数据、文献或统计显著性，不得使用历史实验口径。
```

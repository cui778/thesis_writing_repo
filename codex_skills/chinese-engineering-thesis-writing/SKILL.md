---
name: chinese-engineering-thesis-writing
description: 按章、按二级节撰写和审查中文工科硕士论文，基于真实代码、实验结果、图件索引和证据矩阵生成方法、实验结果与分析正文。用于章节规划、建立证据矩阵、逐节扩写、公式解释、图表结果解读、结论边界核查、跨节一致性检查及终稿学术润色；尤其适用于已有 Markdown/LaTeX 草稿和本地实验仓库的工程技术论文。不得用于脱离证据一次性生成整章、编造数据或文献。
---

# Chinese Engineering Thesis Writing

## 核心原则

以“可追溯证据驱动的逐节写作”代替一次性生成长篇正文。固定使用两层流程：每章一份章节总纲，每次只处理一个二级节写作卡。三级标题仅作为正文内部结构，不建立独立写作包或状态文件。所有定量结论必须能追溯到正式数据、图表、代码或用户确认材料。

本 skill 综合以下写作思想：

- 逐章、逐节执行与质量门控；
- 中文科研论文的正式表达；
- 中文工科学位论文的章引言、方法、实验分析和章末小结结构；
- 真实数据、正式图件、实验协议和结论边界约束。

## 工作模式

先判断当前请求属于哪个模式：

1. `chapter-master`：建立或更新全章唯一的章节总纲。
2. `section-card`：为当前二级节建立写作卡、证据矩阵和段落安排。
3. `section-draft`：基于已锁定证据撰写一个二级节。
4. `section-audit`：审查事实、图表、逻辑、术语和结论强度。
5. `chapter-coherence`：完成整章后的跨节闭合与重复检查。
6. `final-polish`：事实稳定后进行学术表达润色；需要时配合 `academic-polish`，但禁用文学化隐喻和人文社科批判腔。

若用户要求“写完整一章”，先建立章节总纲，再按二级节顺序执行，不在一次输出中直接生成整章。

## 固定两层流程

### 第一层：章节总纲

读取目标章现有草稿、相关代码、正式结果、图件索引和证据矩阵。输出：

- 本章研究问题；
- 本章唯一主结论；
- 各二级节承担的论证任务；
- 每节可使用的表格、图件、公式和实验；
- 各节禁止承担的结论；
- 章节之间的输入与输出关系。

每章只保留一份：

```text
chapters/writing_packets/ch4_master.md
```

可运行：

```powershell
python scripts/build_chapter_master.py --project-root <repo> --chapter 4 --title "面向缺陷定位的多层水力路径注意力诊断模型"
```

详细规则见 [references/chapter-workflow.md](references/chapter-workflow.md)。

### 第二层：当前二级节写作卡

写一个二级节前读取章节总纲，再形成：

```markdown
# 当前小节写作卡
- 目标章节：
- 科学问题：
- 本节核心结论：
- 在全章故事线中的位置：
- 与上一节的关系：
- 向下一节交付什么：
- 目标篇幅：

# 证据矩阵
| 证据ID | 类型 | 文件/图表 | 正式口径 | 可支持结论 | 不可支持结论 |

# 正文段落安排
| 顺序 | 段落任务 | 证据ID | 局部结论 |
```

可运行：

```powershell
python scripts/build_section_packet.py --project-root <repo> --chapter 4 --section 4.3 --title "模型性能与方法机制验证"
```

写作卡是临时执行文件。二级节通过审查并合入正文后可归档，不再创建三级节卡片。

### 二级节正文撰写

根据写作卡直接撰写完整二级节。三级标题可按内容需要组织，但不改变两层管理流程。正文通常覆盖：

1. 本节技术问题或实验目的；
2. 方法、对比设置或控制变量；
3. 公式、图表或数值证据；
4. 结果对应的结构机制；
5. 结论适用范围；
6. 向下一二级节的交付。

方法节读取 [references/method-writing.md](references/method-writing.md)。实验节读取 [references/experiment-analysis.md](references/experiment-analysis.md)。涉及图件时同时读取 [references/figure-interpretation.md](references/figure-interpretation.md)。

### 单节质量门控

每个二级节完成后，必须检查：

- 每个数字是否能定位到证据文件；
- 主实验、多 seed、单 seed、机制探针和个例是否被正确区分；
- 图件是否在正文中被引用并得到实质分析；
- 机制解释是否有消融或结构证据；
- 是否出现结论过重、因果越界或旧协议混入；
- 术语、符号和方法名是否与全章一致；
- 是否存在重复解释、PPT口吻或面向作者的说明性话语。

运行：

```powershell
python scripts/audit_section_draft.py <section-file>
```

证据强度和禁止口径见 [references/evidence-boundaries.md](references/evidence-boundaries.md)。

### 全章一致性检查

一章全部二级节完成后再进行：

- 章首承诺是否全部被后续方法与实验兑现；
- 每个实验是否服务于明确的方法假设；
- 同一组结果是否在多个小节重复报告；
- 方法定义、实验设置和结果是否使用一致口径；
- 章末结论是否只汇总已被正文证明的内容；
- 本章向下一章交付的条件是否明确。

不得在跨节检查前进行大规模语言润色。

### 最终润色

最后才处理句式、连接词、段落节奏和 AI 腔。遵循 [references/style-guide-zh.md](references/style-guide-zh.md)。使用 `academic-polish` 时仅启用逻辑踏空、结论过重、术语与语言检查，不采用文学隐喻、学者仿写或批判性修辞。

## 证据读取顺序

优先级固定为：

1. 用户确认的正式协议与结论边界；
2. 代码和实验配置；
3. 正式多 seed 原始结果或汇总表；
4. 正式图件及 cleaned CSV；
5. 单 seed 消融或机制实验；
6. 个例图与可视化；
7. 旧草稿和历史说明。

若高优先级证据与旧正文冲突，修正旧正文。不得用旧正文反向覆盖正式结果。

## 项目适配

当工作目录为 `E:\11.16\thesis_writing_repo` 或用户讨论当前排水管网论文时，必须读取 [references/project-profile.md](references/project-profile.md)。不得自动搜索并采用 persistent、fulltime、legacy、seedset10 或其他历史口径。

## 输出要求

- 正文使用可直接进入硕士论文的书面语，不使用“你可以”“这一页”“建议讲”等面向作者的表达。
- 分析以自然段为主；表格只用于设置、证据或对比，不用条目替代正文。
- 不捏造文献、数据、统计显著性、实验设置或机制。
- 证据不足时写明“当前结果表明”或“该结果仅用于……”，不得补写虚构原因。
- 修改已有章节时只改当前目标二级节及必要衔接，不顺手重写无关章节。

---
name: thesis-ppt-writing
description: Use when drafting, reorganizing, polishing, or auditing thesis defense/progress PPT text for this project. Enforces merged academic sections, slide-ready Chinese wording, figure-linked result interpretation, and non-overclaiming conclusions for Chapters 3-5.
---

# Thesis PPT Writing

Use this skill for PPT outlines, slide text, speech notes, chapter merging, and page-by-page revisions in `E:/11.16/thesis_writing_repo/ppt`.

This skill is about **how to write the PPT**, not how to draw figures. For drawing rules, use `thesis-figure-studio`. For interpreting existing generated figures, use `thesis-figure-result-analyst`.

## Core Style

PPT text must sound like formal research reporting, not like an assistant explaining to the user how to speak.

Write in slide-ready Chinese:

- direct conclusions
- compact academic phrasing
- evidence-oriented statements
- clear chapter logic
- no conversational guidance in on-screen text

Avoid meta-writing:

- "本页的主结论不是..."
- "应该讲成..."
- "不要写成..."
- "这一页可以这样讲..."
- "后续需要..."
- "我建议..."

Replace with direct claims:

- "监测布局变化显著改变空间定位质量。"
- "强方法进入相近性能区间，结构证据成为区分布局策略的关键依据。"
- "覆盖结构与诊断表征共同塑造定位性能。"

Keep explanatory notes only in `使用注意` or speaker-note style sections, never inside `结果解读（可上屏）`.

## Slide Unit

Every slide entry should include:

```markdown
#### Slide X-Y

**页面标题**

主标题：<merged academic section title>  
副标题：<specific slide focus>

**页面文字**

- ...

**结果解读（可上屏）** or **图示结论（可上屏）**

- ...

**页面图片**

图片建议：...
图片来源：...
图片画的是什么：...
图片反映的问题：...
图片结果分析：...
图片如何支撑结论：...
使用注意：...

**页面总结**

...
```

Do not delete useful tables just to make text shorter. Tables are often the clearest way to present protocols, definitions, method comparisons, and figure interpretation boundaries.

## Section Merging

Use merged academic subsections as slide main-title sources. A main title should cover 2-3 related pages when possible.

Good pattern:

- Main title: `缺陷响应的可观测性验证`
- Slide subtitles:
  - `典型场景 residual 是否突破 normal20 波动包络`
  - `缺陷响应在管网拓扑上的空间分布`
  - `全场景缺陷强度与响应幅值关系`

Avoid returning to the old style where every original slide becomes a separate academic subsection.

## Chapter Logic

### Chapter 3

Purpose: prove the data are credible and useful for downstream diagnosis.

Main logic:

1. SWMM model and topology are based on engineering data.
2. Defect scenarios are time-gated and auditable.
3. Residual features turn scenario simulation into diagnostic evidence.
4. Typical and all-scenario figures show defect responses exist in time, space, and strength dimensions.

Do not use `draw_01` parameter matrix or `draw_03` node-time heatmap as formal main PPT figures unless the user explicitly revives them.

Preferred figure evidence:

- `02_CH3_normal_envelope_defect_residual`
- `04_CH3_topology_residual_spatial_map`
- `08_CH3_strength_stratified_event_response`
- `09_CH3_response_peak_timing`
- `10_CH3_topology_residual_spatial_animation` for PPT visual support

### Chapter 4

Purpose: show model diagnosis ability and its boundaries under fixed layout.

Main logic:

1. Define the diagnosis task and evaluation口径.
2. Present the fixed formal protocol before model variations.
3. Show the main model has usable low-false-alarm spatial ranking performance.
4. Use model comparison and window experiments to show structure and temporal scale matter.
5. Use fixed-layout observability analysis to transition to Chapter 5.

Do not over-expand single-scenario failure cases as main results. They are useful for diagnosis process explanation or backup, but can expose method limitations if not framed carefully.

### Chapter 5

Purpose: show monitoring layout affects diagnosis and that different layout strategies can reach similar performance through different structural paths.

Current core story:

1. Degree is the fixed-layout baseline.
2. Optimized layouts improve MRR relative to Degree.
3. Strong methods have close MRR values; tiny rank differences are not the scientific point.
4. Two-stage v1 represents the structure-coverage-oriented optimization path.
5. Cand-Obs shows near-defect coverage alone is not sufficient.
6. Embedding-Guided represents the diagnostic-representation-oriented optimization path and reaches similar performance with different selected nodes.

Preferred terms:

- `缺陷节点结构覆盖`
- `显式近邻覆盖`
- `显式缺陷节点覆盖约束`
- `诊断表征驱动`
- `结构路径差异`

Avoid:

- `候选覆盖偏好`
- `机制分组`
- "Embedding-Guided 全面最优"
- overclaiming small MRR gaps

## Result Interpretation Pattern

A strong slide result interpretation has four layers:

1. Observation: what the figure shows numerically or visually.
2. Contrast: which methods, scenarios, or metrics differ.
3. Inference: what simple explanation is supported or ruled out.
4. Boundary: what the figure cannot prove.

Example for Chapter 5:

```markdown
- Two-stage v1 将 Far 缺陷节点压缩到 1 个，并取得 MRR=0.905，说明结构覆盖导向策略能够形成较高定位性能。
- Cand-Obs 同样将 Far 压缩到 1 个，但 MRR 只有 0.878，说明“把缺陷节点放近监测点”并不能单独解释全部定位性能。
- Embedding-Guided 的 Far 为 19，结构覆盖明显不占优，但 MRR 仍达到 0.897，说明诊断表征能够从缺陷响应模式中形成有效选点结构。
- 覆盖结构与诊断表征共同塑造定位性能，单纯覆盖最大化不足以解释全部结果。
```

Bad pattern:

```markdown
- E-G 与 Degree 的 Jaccard 约为 0.042。
- E-G 与 Cand-Obs、Two-stage v1 的 Jaccard 均约为 0.064。
- Jaccard 结果支撑 E-G 的结构独立性。
```

Why bad: it only reads numbers and does not explain what is ruled out, what is supported, or how the result advances the argument.

## Figure Text Rules

For every important figure, include:

- 图片画的是什么
- 图片反映的问题
- 图片结果分析
- 图片如何支撑结论
- 使用注意

`图片结果分析` should be evidence-based, not a generic description. Use real numbers when available, but do not stop at the numbers.

## Common Repairs

If the text sounds like a private explanation to the user, convert it to a formal finding.

Private explanation:

> 本页不强调单一方法绝对领先，重点放在不同布局策略均可显著改善 Degree 基线。

Formal finding:

> 优化布局相对 Degree 基线形成明确提升，强方法进入相近性能区间。

Private explanation:

> 后续分析重点转向：相近性能是否来自相同的布局结构。

Formal finding:

> 相近定位性能并不必然来自相同布局结构，结构证据成为方法区分的关键依据。

## Validation Checklist

Before finishing:

1. Each slide has main title, subtitle, page text, figure section, and summary.
2. Main titles come from merged academic sections, not one-off slide labels.
3. On-screen result interpretations are not meta-instructions.
4. Figures have result analysis, not only "what the figure is".
5. Tables with protocol or method information are preserved when useful.
6. Chapter 5 does not overclaim tiny MRR differences.
7. Backup figures are labeled as backup/defense instead of promoted to main results.

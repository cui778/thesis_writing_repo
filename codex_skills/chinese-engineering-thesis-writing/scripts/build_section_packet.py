from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a thesis section writing card.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    out = args.output
    if out is None:
        out = root / "chapters" / "writing_packets" / (
            f"ch{args.chapter}_{args.section.replace('.', '_')}_card.md"
        )
    out.parent.mkdir(parents=True, exist_ok=True)

    evidence_candidates = [
        root / "chapters" / f"CH{args.chapter}_RESULTS_EVIDENCE_MATRIX_FINAL.md",
        root / "chapters" / "CH4_CH5_FINAL_STORYLINE_WITH_RESULTS.md",
        root / "figures" / f"ch{args.chapter}" / "generated_results"
        / f"CH{args.chapter}_OFFICIAL_FIGURE_INDEX.md",
        root / "figures" / "DATA_SOURCE_POLICY.md",
    ]
    evidence_lines = "\n".join(
        f"- `{path}`" for path in evidence_candidates if path.exists()
    ) or "- `[待补充正式证据文件]`"

    master = root / "chapters" / "writing_packets" / f"ch{args.chapter}_master.md"

    text = f"""# 第{args.chapter}章 {args.section} {args.title} 写作卡

## 当前小节任务

- 目标章节：{args.section} {args.title}
- 章节总纲：`{master}`
- 科学问题：
- 本节核心结论：
- 在全章故事线中的位置：
- 与上一节的关系：
- 向下一节交付：
- 目标篇幅：

## 必读证据

{evidence_lines}

## 证据矩阵

| 证据ID | 等级 | 类型 | 文件/图表 | 正式口径 | 可支持结论 | 不可支持结论 |
|---|---|---|---|---|---|---|
| E01 |  |  |  |  |  |  |

## 正文段落安排

| 顺序 | 段落任务 | 证据ID | 局部结论 |
|---:|---|---|---|
| P1 |  |  |  |

## 图表计划

| 图表 | 身份 | 画的是什么 | 需要报告的结果 | 支撑结论 | 使用边界 |
|---|---|---|---|---|---|

## 事实与结论核查

- [ ] 所有数值可追溯
- [ ] 多 seed 与单 seed 已区分
- [ ] 正式结果与历史口径未混合
- [ ] 每张图均有实质结果分析
- [ ] 机制解释具有消融或结构证据
- [ ] 禁止结论未进入正文
- [ ] 术语与全章一致
"""
    out.write_text(text, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

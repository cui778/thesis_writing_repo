from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a chapter master outline.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    out = args.output or (
        root / "chapters" / "writing_packets" / f"ch{args.chapter}_master.md"
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

    text = f"""# 第{args.chapter}章章节总纲

## 基本信息

- 章节标题：{args.title}
- 本章研究问题：
- 本章主结论：
- 上一章交付：
- 向下一章交付：

## 全章故事线

```text
[问题定义] -> [方法设计] -> [实验验证] -> [边界分析] -> [本章结论]
```

## 必读证据

{evidence_lines}

## 二级节职责与证据分配

| 二级节 | 科学问题 | 承接内容 | 本节产出 | 正式证据 | 禁止结论 | 向后续交付 |
|---|---|---|---|---|---|---|
| {args.chapter}.1 |  |  |  |  |  |  |

## 定义与结果唯一出现位置

| 内容 | 首次定义/报告位置 | 后续引用方式 |
|---|---|---|

## 全章统一术语

| 概念 | 固定写法 | 禁止混用 |
|---|---|---|

## 全章完成检查

- [ ] 章首研究问题已由后续内容回答
- [ ] 每个二级节职责互不重复
- [ ] 方法假设均有对应实验
- [ ] 正式图表均有唯一论证角色
- [ ] 单 seed 与多 seed 结论边界清楚
- [ ] 章末结论未引入新证据
- [ ] 已明确向下一章交付的条件
"""
    out.write_text(text, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

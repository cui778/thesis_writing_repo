from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


STRONG_PATTERNS = {
    "unqualified_significance": r"(?<!统计)显著(?!性|水平)",
    "absolute_best": r"(全面最优|绝对最优|所有指标.*最优|显著碾压)",
    "ppt_voice": r"(这一页|本页|你可以|建议讲|故事线|为了让.*好看)",
    "weak_claim": r"(效果很好|非常有效|充分利用|有效融合|全面提升)",
    "missing_evidence_marker": r"\[(NEEDS_DATA|NEEDS_CITATION)\]",
}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Audit a Chinese thesis section draft.")
    parser.add_argument("draft", type=Path)
    args = parser.parse_args()
    text = args.draft.read_text(encoding="utf-8")

    findings: list[str] = []
    for name, pattern in STRONG_PATTERNS.items():
        hits = []
        for hit in re.finditer(pattern, text):
            prefix = text[max(0, hit.start() - 16):hit.start()]
            if name == "absolute_best" and re.search(r"(不存在|并非|不宣称|不能称为)", prefix):
                continue
            hits.append(hit)
        if hits:
            samples = ", ".join(repr(hit.group(0)) for hit in hits[:5])
            findings.append(f"{name}: {len(hits)} hit(s): {samples}")

    numeric_claims = len(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?%?", text))
    figure_refs = len(re.findall(r"(?:如)?图\s*\d+(?:[-.]\d+)?", text))
    table_refs = len(re.findall(r"(?:如)?表\s*\d+(?:[-.]\d+)?", text))
    headings = len(re.findall(r"^#{2,4}\s+", text, flags=re.MULTILINE))

    print(f"file: {args.draft}")
    print(f"headings: {headings}")
    print(f"numeric expressions: {numeric_claims}")
    print(f"figure references: {figure_refs}")
    print(f"table references: {table_refs}")
    if findings:
        print("findings:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)
    print("findings: none")


if __name__ == "__main__":
    main()

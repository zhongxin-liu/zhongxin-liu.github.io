#!/usr/bin/env python3
"""One-time migration of descriptions from a legacy publications.tex file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUBSECTION_RE = re.compile(
    r"\\begin\{rSubsection\}\{\}\{\}\{\}\{\}(.*?)\\end\{rSubsection\}",
    re.DOTALL,
)
CITATION_RE = re.compile(
    r"\\(?:pubitem|publication)\{\\fullcite\{([^}]+)\}\}"
    r"(?:\\aca\{\\\\\}|\\\\)?"
)


def _strip_outer_ind(text: str) -> str:
    marker = text.find(r"\ind{")
    if marker < 0:
        return text.strip()
    opening = marker + len(r"\ind")
    depth = 1
    index = opening + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                inner = text[opening + 1 : index]
                suffix = text[index + 1 :].strip()
                return (inner + ("\n" + suffix if suffix else "")).strip()
        index += 1
    return text.strip()


def _has_active_tex(text: str) -> bool:
    active_lines = [
        line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("%")
    ]
    return bool(active_lines)


def migrate(source: Path) -> str:
    legacy = source.read_text(encoding="utf-8")
    definitions: list[tuple[str, str]] = []
    drafts: list[tuple[str, str]] = []

    for subsection in SUBSECTION_RE.finditer(legacy):
        block = subsection.group(1).strip()
        citation = CITATION_RE.search(block)
        if not citation:
            continue
        key = citation.group(1)
        description = block[citation.end() :].strip()
        if not description:
            continue
        if _has_active_tex(description):
            definitions.append((key, _strip_outer_ind(description)))
        else:
            drafts.append((key, description))

    lines = [
        "% Publication descriptions migrated from the former manual publication list.",
        "% Set \\publicationdescriptions to 1 or 0 before loading main.tex to show or",
        "% hide these descriptions (see industry.tex and academic.tex).",
        "",
    ]
    for key, description in definitions:
        lines.extend(
            [
                f"\\publicationdescription{{{key}}}{{%",
                description,
                "}",
                "",
            ]
        )

    if drafts:
        lines.extend(
            [
                "% ------------------------------------------------------------------",
                "% Archived drafts that were already commented out in the legacy file.",
                "% Uncomment and wrap the desired text in \\publicationdescription to use it.",
                "% ------------------------------------------------------------------",
                "",
            ]
        )
        for key, description in drafts:
            lines.append(f"% Draft for {key}:")
            lines.extend(description.splitlines())
            lines.append("")

    print(f"Migrated {len(definitions)} active descriptions and {len(drafts)} drafts")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = migrate(args.source)
    args.output.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()

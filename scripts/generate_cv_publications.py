#!/usr/bin/env python3
"""Generate CV publication sections from the canonical BibTeX file.

The input order is preserved.  Chinese-language duplicate entries are omitted
from the English CV and replace their English counterparts in the Chinese CV.
An entry is treated as a first/corresponding-author paper when Zhongxin Liu is
the first author or when his author token contains ``*``.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]


def _read_braced_value(text: str, start: int) -> tuple[str, int]:
    depth = 1
    index = start + 1
    value_start = index
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[value_start:index], index + 1
        index += 1
    raise ValueError("Unterminated braced BibTeX value")


def _read_quoted_value(text: str, start: int) -> tuple[str, int]:
    index = start + 1
    value_start = index
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == '"':
            return text[value_start:index], index + 1
        index += 1
    raise ValueError("Unterminated quoted BibTeX value")


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0
    while index < len(body):
        while index < len(body) and (body[index].isspace() or body[index] == ","):
            index += 1
        if index >= len(body):
            break

        name_start = index
        while index < len(body) and (body[index].isalnum() or body[index] in "_-"):
            index += 1
        name = body[name_start:index].lower()
        while index < len(body) and body[index].isspace():
            index += 1
        if not name or index >= len(body) or body[index] != "=":
            next_comma = body.find(",", index)
            index = len(body) if next_comma < 0 else next_comma + 1
            continue

        index += 1
        while index < len(body) and body[index].isspace():
            index += 1
        if index >= len(body):
            fields[name] = ""
            break
        if body[index] == "{":
            value, index = _read_braced_value(body, index)
        elif body[index] == '"':
            value, index = _read_quoted_value(body, index)
        else:
            value_start = index
            while index < len(body) and body[index] != ",":
                index += 1
            value = body[value_start:index].strip()
        fields[name] = value.strip()
    return fields


def parse_bibtex(text: str) -> list[BibEntry]:
    entries: list[BibEntry] = []
    index = 0
    while True:
        match = re.search(r"@([A-Za-z]+)\s*\{", text[index:])
        if not match:
            break
        entry_type = match.group(1).lower()
        opening = index + match.end() - 1
        comma = text.find(",", opening + 1)
        if comma < 0:
            raise ValueError(f"Missing key separator after position {opening}")
        key = text[opening + 1 : comma].strip()

        depth = 1
        cursor = opening + 1
        while cursor < len(text) and depth:
            char = text[cursor]
            if char == "\\":
                cursor += 2
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError(f"Unterminated BibTeX entry: {key}")

        if entry_type not in {"comment", "preamble", "string"}:
            body = text[comma + 1 : cursor - 1]
            entries.append(BibEntry(entry_type, key, _parse_fields(body)))
        index = cursor
    return entries


def _plain_author(author: str) -> str:
    previous = None
    while previous != author:
        previous = author
        author = re.sub(
            r"\\(?:textbf|textit|emph)\s*\{([^{}]*)\}", r"\1", author
        )
    author = re.sub(r"\\[A-Za-z]+", "", author)
    return author.replace("{", "").replace("}", "").strip()


def _is_zhongxin(author: str) -> bool:
    compact = re.sub(r"\s+", " ", _plain_author(author)).lower()
    return (
        "zhongxin liu" in compact
        or "liu, zhongxin" in compact
        or "刘忠鑫" in compact
    )


def is_first_or_corresponding(entry: BibEntry) -> bool:
    authors = re.split(r"\s+and\s+", entry.fields.get("author", ""))
    if not authors:
        return False
    if _is_zhongxin(authors[0]):
        return True
    return any(_is_zhongxin(author) and "*" in _plain_author(author) for author in authors)


def _doi(entry: BibEntry) -> str:
    return entry.fields.get("doi", "").strip().lower()


def select_entries(entries: list[BibEntry], language: str) -> list[BibEntry]:
    chinese_variants = [entry for entry in entries if "chinese" in entry.key.lower()]
    variants_by_doi = {_doi(entry): entry for entry in chinese_variants if _doi(entry)}
    entries_by_key = {entry.key: entry for entry in entries}

    selected: list[BibEntry] = []
    for entry in entries:
        if "chinese" in entry.key.lower():
            continue
        if language == "zh":
            explicit_key = entry.fields.get("cvzhkey", "")
            if explicit_key:
                entry = entries_by_key.get(explicit_key, entry)
            elif _doi(entry) in variants_by_doi:
                entry = variants_by_doi[_doi(entry)]
        selected.append(entry)
    return selected


def _render_calls(entries: list[BibEntry], command: str) -> list[str]:
    lines: list[str] = []
    for position, entry in enumerate(entries):
        lines.append(f"\\{command}{{{entry.key}}}")
        if position != len(entries) - 1:
            lines.append("\\vspace{\\subvspace}")
    return lines


def render_publications(entries: list[BibEntry], language: str) -> str:
    header = [
        "% AUTO-GENERATED FILE. DO NOT EDIT.",
        "% Edit the shared metadata/pub2.bib file and rerun the CV compile script.",
        "",
    ]
    if language == "en":
        lines = header + ["\\begin{rSection}{Publications}"]
        lines.extend(_render_calls(entries, "cvpublication"))
        lines.append("\\end{rSection}")
        return "\n".join(lines) + "\n"

    primary = [entry for entry in entries if is_first_or_corresponding(entry)]
    other = [entry for entry in entries if not is_first_or_corresponding(entry)]
    lines = header + ["\\begin{rSection}{一作或通讯论文}"]
    lines.extend(_render_calls(primary, "cvprimarypublication"))
    lines.extend(["\\end{rSection}", "", "\\begin{rSection}{其他论文}", "\\vspace{+0.025in}"])
    lines.extend(_render_calls(other, "cvotherpublication"))
    lines.append("\\end{rSection}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", required=True, type=Path)
    parser.add_argument("--language", required=True, choices=("en", "zh"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    entries = parse_bibtex(args.bib.read_text(encoding="utf-8"))
    selected = select_entries(entries, args.language)
    output = render_publications(selected, args.language)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(
        f"Generated {args.output} from {args.bib} "
        f"({len(selected)} publications, language={args.language})"
    )


if __name__ == "__main__":
    main()

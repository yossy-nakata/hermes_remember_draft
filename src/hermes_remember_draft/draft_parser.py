import re
from dataclasses import dataclass
from pathlib import Path

from .markdown_io import MarkdownFile
from .paths import validate_relative_path

_FILE_BLOCK_RE = re.compile(
    r"<<<FILE:\s*(?P<path>.+?)\s*>>>\r?\n"
    r"(?P<content>.*?)"
    r"\r?\n<<<END FILE>>>",
    re.DOTALL,
)


@dataclass(frozen=True)
class DraftFile:
    relative_path: Path
    content: str


def parse_draft_files(
    raw_output: str,
    *,
    input_markdowns: list[MarkdownFile],
) -> list[DraftFile]:
    if raw_output.strip() == "<<<NO CHANGES>>>":
        return []

    input_by_path = {
        markdown.relative_path: markdown
        for markdown in input_markdowns
    }

    seen_paths: set[Path] = set()
    draft_files: list[DraftFile] = []

    matches = list(_FILE_BLOCK_RE.finditer(raw_output))

    if not matches:
        raise ValueError("No valid FILE blocks found in LLM output")

    for match in matches:
        raw_path = match.group("path").strip()
        content = match.group("content")

        relative_path = validate_relative_path(raw_path)

        if relative_path not in input_by_path:
            raise ValueError(f"Draft output path was not an input file: {relative_path}")

        if relative_path in seen_paths:
            raise ValueError(f"Duplicate draft output path: {relative_path}")

        seen_paths.add(relative_path)

        original = input_by_path[relative_path]

        if _normalize_content_for_compare(content) == _normalize_content_for_compare(original.content):
            continue

        draft_files.append(
            DraftFile(
                relative_path=relative_path,
                content=content,
            )
        )

    return draft_files


def _normalize_content_for_compare(content: str) -> str:
    return content.rstrip()
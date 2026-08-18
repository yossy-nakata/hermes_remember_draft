from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .draft_parser import DraftFile
from .markdown_io import MarkdownFile


@dataclass(frozen=True)
class ManifestData:
    created_at: datetime
    slug: str
    model: str
    input_files: list[MarkdownFile]
    changed_files: list[DraftFile]
    summary: str = "Draft generated from conversation and input Markdown files."


def build_manifest(data: ManifestData) -> str:
    changed_paths = {file.relative_path for file in data.changed_files}

    unchanged_files = [
        file
        for file in data.input_files
        if file.relative_path not in changed_paths
    ]

    return "\n".join(
        [
            "# Remember Draft",
            "",
            "Status: draft",
            f"Created: {data.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Slug: {data.slug}",
            f"Model: {data.model}",
            "",
            "## Input Files",
            "",
            *_format_markdown_paths(
                [file.relative_path for file in data.input_files]
            ),
            "",
            "## Changed Files",
            "",
            *_format_markdown_paths(
                [file.relative_path for file in data.changed_files]
            ),
            "",
            "## Unchanged Files",
            "",
            *_format_markdown_paths(
                [file.relative_path for file in unchanged_files]
            ),
            "",
            "## Summary",
            "",
            data.summary,
            "",
        ]
    )


def _format_markdown_paths(paths: list[Path]) -> list[str]:
    if not paths:
        return ["- None"]

    return [
        f"- {path.as_posix()}"
        for path in paths
    ]
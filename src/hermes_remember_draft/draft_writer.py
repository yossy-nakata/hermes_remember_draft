from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .draft_parser import DraftFile
from .manifest import ManifestData, build_manifest
from .markdown_io import MarkdownFile


@dataclass(frozen=True)
class DraftWriteResult:
    draft_dir: Path
    manifest_path: Path
    written_files: list[Path]


def build_draft_id(
    *,
    created_at: datetime,
    slug: str,
) -> str:
    timestamp = created_at.strftime("%Y-%m-%d_%H%M")
    safe_slug = _sanitize_slug(slug)

    return f"{timestamp}__{safe_slug}"


def write_draft(
    *,
    memory_root: Path,
    slug: str,
    model: str,
    input_files: list[MarkdownFile],
    changed_files: list[DraftFile],
    created_at: datetime | None = None,
    summary: str = "Draft generated from conversation and input Markdown files.",
) -> DraftWriteResult:
    created_at = created_at or datetime.now(UTC)
    draft_id = build_draft_id(
        created_at=created_at,
        slug=slug,
    )

    draft_dir = memory_root / ".remember" / "drafts" / draft_id
    files_dir = draft_dir / "files"

    draft_dir.mkdir(parents=True, exist_ok=False)
    files_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []

    for changed_file in changed_files:
        output_path = files_dir / changed_file.relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(changed_file.content, encoding="utf-8")
        written_files.append(output_path)

    manifest = build_manifest(
        ManifestData(
            created_at=created_at,
            slug=slug,
            model=model,
            input_files=input_files,
            changed_files=changed_files,
            summary=summary,
        )
    )

    manifest_path = draft_dir / "_manifest.md"
    manifest_path.write_text(manifest, encoding="utf-8")

    return DraftWriteResult(
        draft_dir=draft_dir,
        manifest_path=manifest_path,
        written_files=written_files,
    )


def _sanitize_slug(slug: str) -> str:
    safe = "".join(
        char if char.isalnum() or char in ("-", "_") else "-"
        for char in slug.strip().lower()
    )
    safe = "-".join(part for part in safe.split("-") if part)

    return safe or "remember-draft"

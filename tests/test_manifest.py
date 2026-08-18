from datetime import UTC, datetime
from pathlib import Path

from hermes_remember_draft.draft_parser import DraftFile
from hermes_remember_draft.manifest import ManifestData, build_manifest
from hermes_remember_draft.markdown_io import MarkdownFile


def markdown_file(relative_path: str) -> MarkdownFile:
    return MarkdownFile(
        path=Path("/tmp/memory") / relative_path,
        relative_path=Path(relative_path),
        content="# Test\n",
    )


def test_build_manifest_lists_files() -> None:
    manifest = build_manifest(
        ManifestData(
            created_at=datetime(2026, 8, 17, 22, 17, tzinfo=UTC),
            slug="memory-mvp",
            model="lfm2-24b",
            input_files=[
                markdown_file("hermes-agent.md"),
                markdown_file("lfm2.md"),
            ],
            changed_files=[
                DraftFile(
                    relative_path=Path("hermes-agent.md"),
                    content="# Hermes Agent\n\nUpdated.\n",
                )
            ],
            summary="Updated Hermes Agent memory.",
        )
    )

    assert "# Remember Draft" in manifest
    assert "Status: draft" in manifest
    assert "Created: 2026-08-17 22:17" in manifest
    assert "Slug: memory-mvp" in manifest
    assert "Model: lfm2-24b" in manifest
    assert "- hermes-agent.md" in manifest
    assert "- lfm2.md" in manifest
    assert "Updated Hermes Agent memory." in manifest


def test_build_manifest_uses_none_for_empty_changed_files() -> None:
    manifest = build_manifest(
        ManifestData(
            created_at=datetime(2026, 8, 17, 22, 17, tzinfo=UTC),
            slug="memory-mvp",
            model="lfm2-24b",
            input_files=[
                markdown_file("lfm2.md"),
            ],
            changed_files=[],
        )
    )

    assert "## Changed Files\n\n- None" in manifest
    assert "## Unchanged Files\n\n- lfm2.md" in manifest

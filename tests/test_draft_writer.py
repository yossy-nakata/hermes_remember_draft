from datetime import UTC, datetime
from pathlib import Path

from hermes_remember_draft.draft_parser import DraftFile
from hermes_remember_draft.draft_writer import build_draft_id, write_draft
from hermes_remember_draft.markdown_io import MarkdownFile


def markdown_file(memory_root: Path, relative_path: str) -> MarkdownFile:
    return MarkdownFile(
        path=memory_root / relative_path,
        relative_path=Path(relative_path),
        content="# Original\n",
    )


def test_build_draft_id() -> None:
    result = build_draft_id(
        created_at=datetime(2026, 8, 17, 22, 17, tzinfo=UTC),
        slug="Memory MVP",
    )

    assert result == "2026-08-17_2217__memory-mvp"


def test_write_draft_with_changed_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    result = write_draft(
        memory_root=memory_root,
        slug="memory-mvp",
        model="lfm2-24b",
        input_files=[
            markdown_file(memory_root, "architecture/remember-flow.md"),
            markdown_file(memory_root, "lfm2.md"),
        ],
        changed_files=[
            DraftFile(
                relative_path=Path("architecture") / "remember-flow.md",
                content="# Remember Flow\n\nUpdated.\n",
            )
        ],
        created_at=datetime(2026, 8, 17, 22, 17, tzinfo=UTC),
    )

    assert result.draft_dir == (
        memory_root
        / ".remember"
        / "drafts"
        / "2026-08-17_2217__memory-mvp"
    )

    draft_file = (
        result.draft_dir
        / "files"
        / "architecture"
        / "remember-flow.md"
    )

    assert draft_file.read_text(encoding="utf-8") == "# Remember Flow\n\nUpdated.\n"
    assert result.manifest_path.read_text(encoding="utf-8").startswith("# Remember Draft")


def test_write_draft_with_no_changed_files(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    result = write_draft(
        memory_root=memory_root,
        slug="memory-mvp",
        model="lfm2-24b",
        input_files=[
            markdown_file(memory_root, "lfm2.md"),
        ],
        changed_files=[],
        created_at=datetime(2026, 8, 17, 22, 17, tzinfo=UTC),
    )

    assert result.written_files == []
    assert (result.draft_dir / "files").exists()
    assert "## Changed Files\n\n- None" in result.manifest_path.read_text(
        encoding="utf-8"
    )

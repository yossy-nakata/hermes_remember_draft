from pathlib import Path

import pytest

from hermes_remember_draft.draft_diff import build_draft_diffs


def test_build_draft_diffs_with_changed_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"

    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)

    source.write_text("# Title\n\nOld.\n", encoding="utf-8")
    draft_file.write_text("# Title\n\nNew.\n", encoding="utf-8")

    result = build_draft_diffs(memory_root=memory_root, draft_dir=draft_dir)

    assert len(result) == 1
    assert result[0].relative_path == Path("foo.md")
    assert "--- foo.md" in result[0].diff_text
    assert "+++ draft/foo.md" in result[0].diff_text
    assert "-Old." in result[0].diff_text
    assert "+New." in result[0].diff_text


def test_build_draft_diffs_ignores_unchanged_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"

    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)

    source.write_text("# Same\n", encoding="utf-8")
    draft_file.write_text("# Same\n", encoding="utf-8")

    result = build_draft_diffs(memory_root=memory_root, draft_dir=draft_dir)

    assert result == []


def test_build_draft_diffs_handles_subdirectory(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "architecture" / "remember-flow.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "architecture" / "remember-flow.md"

    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)

    source.write_text("# Flow\n\nOld.\n", encoding="utf-8")
    draft_file.write_text("# Flow\n\nNew.\n", encoding="utf-8")

    result = build_draft_diffs(memory_root=memory_root, draft_dir=draft_dir)

    assert len(result) == 1
    assert result[0].relative_path == Path("architecture") / "remember-flow.md"


def test_build_draft_diffs_rejects_missing_source_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "new.md"

    draft_file.parent.mkdir(parents=True)
    draft_file.write_text("# New\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="no corresponding source file"):
        build_draft_diffs(memory_root=memory_root, draft_dir=draft_dir)


def test_build_draft_diffs_rejects_missing_draft_dir(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    with pytest.raises(FileNotFoundError, match="Draft directory not found"):
        build_draft_diffs(
            memory_root=memory_root,
            draft_dir=memory_root / ".remember" / "drafts" / "missing",
        )


def test_build_draft_diffs_rejects_missing_files_dir(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"

    draft_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="Draft files directory not found"):
        build_draft_diffs(memory_root=memory_root, draft_dir=draft_dir)
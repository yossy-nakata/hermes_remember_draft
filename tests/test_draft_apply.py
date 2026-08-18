from pathlib import Path

import pytest
from typer.testing import CliRunner

from hermes_remember_draft.cli import app
from hermes_remember_draft.draft_apply import apply_draft, build_apply_plan

runner = CliRunner()


def test_build_apply_plan_includes_corresponding_source(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"

    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)

    assert len(result) == 1
    assert result[0].relative_path == Path("foo.md")
    assert result[0].source_path == source.resolve()
    assert result[0].draft_path == draft_file.resolve()


def test_build_apply_plan_handles_subdirectory(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    relative_path = Path("architecture") / "remember-flow.md"
    source = memory_root / relative_path
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / relative_path

    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)

    assert len(result) == 1
    assert result[0].relative_path == relative_path


def test_build_apply_plan_rejects_missing_draft_dir(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    with pytest.raises(FileNotFoundError, match="Draft directory not found"):
        build_apply_plan(
            memory_root=memory_root,
            draft_dir=memory_root / ".remember" / "drafts" / "missing",
        )


def test_build_apply_plan_rejects_missing_files_dir(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="Draft files directory not found"):
        build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)


def test_build_apply_plan_rejects_missing_source_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "new.md"
    draft_file.parent.mkdir(parents=True)
    draft_file.write_text("# New\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="no corresponding source file"):
        build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)


def test_build_apply_plan_rejects_source_directory(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    source.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    draft_file.write_text("# New\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Source path is not a file"):
        build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)


def test_apply_dry_run_does_not_change_source_or_move_draft(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "apply",
            "--dry-run",
            "--memory-root",
            str(memory_root),
            str(draft_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Files that would be overwritten:" in result.output
    assert "- foo.md" in result.output
    assert "OK: dry run complete." in result.output
    assert source.read_text(encoding="utf-8") == "# Old\n"
    assert draft_dir.is_dir()
    assert draft_file.read_text(encoding="utf-8") == "# New\n"


def test_apply_dry_run_reports_no_files(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    (draft_dir / "files").mkdir(parents=True)

    result = runner.invoke(
        app,
        [
            "apply",
            "--dry-run",
            "--memory-root",
            str(memory_root),
            str(draft_dir),
        ],
    )

    assert result.exit_code == 0
    assert "No files to apply." in result.output


def test_apply_draft_overwrites_source_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = apply_draft(memory_root=memory_root, draft_dir=draft_dir)

    assert source.read_text(encoding="utf-8") == "# New\n"
    assert result.overwritten_files == [Path("foo.md")]


def test_apply_draft_overwrites_subdirectory_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    relative_path = Path("architecture") / "remember-flow.md"
    source = memory_root / relative_path
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / relative_path
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = apply_draft(memory_root=memory_root, draft_dir=draft_dir)

    assert source.read_text(encoding="utf-8") == "# New\n"
    assert result.overwritten_files == [relative_path]


def test_apply_draft_moves_draft_to_applied(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = apply_draft(memory_root=memory_root, draft_dir=draft_dir)

    applied_dir = memory_root / ".remember" / "applied" / "draft-1"
    assert result.applied_dir == applied_dir.resolve()
    assert not draft_dir.exists()
    assert (applied_dir / "files" / "foo.md").read_text(encoding="utf-8") == "# New\n"


def test_apply_draft_rejects_existing_applied_dir(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    applied_dir = memory_root / ".remember" / "applied" / "draft-1"
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    applied_dir.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Applied draft already exists"):
        apply_draft(memory_root=memory_root, draft_dir=draft_dir)

    assert source.read_text(encoding="utf-8") == "# Old\n"
    assert draft_dir.is_dir()


def test_apply_draft_rejects_missing_source_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "new.md"
    draft_file.parent.mkdir(parents=True)
    draft_file.write_text("# New\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="no corresponding source file"):
        apply_draft(memory_root=memory_root, draft_dir=draft_dir)

    assert draft_dir.is_dir()


def test_apply_command_applies_and_reports_result(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "foo.md"
    draft_dir = memory_root / ".remember" / "drafts" / "draft-1"
    draft_file = draft_dir / "files" / "foo.md"
    source.parent.mkdir(parents=True)
    draft_file.parent.mkdir(parents=True)
    source.write_text("# Old\n", encoding="utf-8")
    draft_file.write_text("# New\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "apply",
            "--memory-root",
            str(memory_root),
            str(draft_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Applied files:" in result.output
    assert "- foo.md" in result.output
    assert "Draft moved to:" in result.output
    assert "OK: draft applied." in result.output
    assert source.read_text(encoding="utf-8") == "# New\n"
    assert not draft_dir.exists()

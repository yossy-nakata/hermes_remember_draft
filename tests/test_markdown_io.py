from pathlib import Path

import pytest

from hermes_remember_draft.markdown_io import read_markdown, read_markdown_files


def test_read_markdown_file_under_memory_root(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "architecture" / "remember-flow.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Remember Flow\n\nHello.\n", encoding="utf-8")

    result = read_markdown(source, memory_root=memory_root)

    assert result.path == source.resolve()
    assert result.relative_path == Path("architecture") / "remember-flow.md"
    assert result.content == "# Remember Flow\n\nHello.\n"
    assert result.char_count == len(result.content)
    assert result.byte_size == len(result.content.encode("utf-8"))


def test_read_markdown_files(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    first = memory_root / "hermes-agent.md"
    second = memory_root / "lfm2.md"
    memory_root.mkdir()
    first.write_text("# Hermes\n", encoding="utf-8")
    second.write_text("# LFM2\n", encoding="utf-8")

    results = read_markdown_files(
        [first, second],
        memory_root=memory_root,
    )

    assert [item.relative_path for item in results] == [
        Path("hermes-agent.md"),
        Path("lfm2.md"),
    ]


def test_rejects_missing_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    with pytest.raises(FileNotFoundError, match="Markdown file not found"):
        read_markdown(
            memory_root / "missing.md",
            memory_root=memory_root,
        )


def test_rejects_directory(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "notes.md"
    source.mkdir(parents=True)

    with pytest.raises(ValueError, match="Not a file"):
        read_markdown(source, memory_root=memory_root)


def test_rejects_non_markdown_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / "notes.txt"
    memory_root.mkdir()
    source.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="Not a Markdown file"):
        read_markdown(source, memory_root=memory_root)


def test_rejects_file_outside_memory_root(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    outside = tmp_path / "outside.md"
    memory_root.mkdir()
    outside.write_text("# Outside\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside root"):
        read_markdown(outside, memory_root=memory_root)


def test_rejects_remember_directory(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    source = memory_root / ".remember" / "drafts" / "old.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Old Draft\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"\.remember"):
        read_markdown(source, memory_root=memory_root)
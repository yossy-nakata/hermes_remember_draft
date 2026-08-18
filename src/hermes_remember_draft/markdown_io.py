from dataclasses import dataclass
from pathlib import Path

from .paths import normalize_root, relative_to_root


@dataclass(frozen=True)
class MarkdownFile:
    path: Path
    relative_path: Path
    content: str

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def byte_size(self) -> int:
        return len(self.content.encode("utf-8"))


def read_markdown(
    path: Path,
    *,
    memory_root: Path,
) -> MarkdownFile:
    root = normalize_root(memory_root)
    source_path = path.expanduser().resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {source_path}")

    if not source_path.is_file():
        raise ValueError(f"Not a file: {source_path}")

    if source_path.suffix.lower() != ".md":
        raise ValueError(f"Not a Markdown file: {source_path}")

    relative_path = relative_to_root(source_path, root)

    if ".remember" in relative_path.parts:
        raise ValueError(
            f"Files under .remember are not valid source Markdown: {source_path}"
        )

    return MarkdownFile(
        path=source_path,
        relative_path=relative_path,
        content=source_path.read_text(encoding="utf-8"),
    )


def read_markdown_files(
    paths: list[Path],
    *,
    memory_root: Path,
) -> list[MarkdownFile]:
    return [read_markdown(path, memory_root=memory_root) for path in paths]
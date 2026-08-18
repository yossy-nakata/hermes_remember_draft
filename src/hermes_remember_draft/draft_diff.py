import difflib
from dataclasses import dataclass
from pathlib import Path

from .paths import normalize_root, validate_relative_path


@dataclass(frozen=True)
class DraftDiff:
    relative_path: Path
    source_path: Path
    draft_path: Path
    diff_text: str


def build_draft_diffs(memory_root: Path, draft_dir: Path) -> list[DraftDiff]:
    memory_root = normalize_root(memory_root)
    draft_dir = draft_dir.expanduser().resolve()
    files_dir = draft_dir / "files"

    if not draft_dir.exists():
        raise FileNotFoundError(f"Draft directory not found: {draft_dir}")

    if not draft_dir.is_dir():
        raise ValueError(f"Not a draft directory: {draft_dir}")

    if not files_dir.exists():
        raise FileNotFoundError(f"Draft files directory not found: {files_dir}")

    if not files_dir.is_dir():
        raise ValueError(f"Not a draft files directory: {files_dir}")

    diffs: list[DraftDiff] = []

    for draft_path in sorted(files_dir.rglob("*.md")):
        relative_path = validate_relative_path(draft_path.relative_to(files_dir))
        source_path = memory_root / relative_path

        if not source_path.exists():
            raise FileNotFoundError(
                f"Draft file has no corresponding source file: {relative_path.as_posix()}"
            )

        if not source_path.is_file():
            raise ValueError(f"Source path is not a file: {source_path}")

        source_text = source_path.read_text(encoding="utf-8")
        draft_text = draft_path.read_text(encoding="utf-8")

        diff_text = "".join(
            difflib.unified_diff(
                source_text.splitlines(keepends=True),
                draft_text.splitlines(keepends=True),
                fromfile=relative_path.as_posix(),
                tofile=f"draft/{relative_path.as_posix()}",
            )
        )

        if diff_text:
            diffs.append(
                DraftDiff(
                    relative_path=relative_path,
                    source_path=source_path,
                    draft_path=draft_path,
                    diff_text=diff_text,
                )
            )

    return diffs
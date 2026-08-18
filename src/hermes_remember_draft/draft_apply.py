import shutil
from dataclasses import dataclass
from pathlib import Path

from .paths import normalize_root, validate_relative_path


@dataclass(frozen=True)
class ApplyPlan:
    relative_path: Path
    source_path: Path
    draft_path: Path


@dataclass(frozen=True)
class ApplyResult:
    applied_dir: Path
    overwritten_files: list[Path]


def build_apply_plan(memory_root: Path, draft_dir: Path) -> list[ApplyPlan]:
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

    plan: list[ApplyPlan] = []

    for draft_path in sorted(files_dir.rglob("*.md")):
        relative_path = validate_relative_path(draft_path.relative_to(files_dir))
        source_path = memory_root / relative_path

        if not source_path.exists():
            raise FileNotFoundError(
                f"Draft file has no corresponding source file: {relative_path.as_posix()}"
            )

        if not source_path.is_file():
            raise ValueError(f"Source path is not a file: {source_path}")

        plan.append(
            ApplyPlan(
                relative_path=relative_path,
                source_path=source_path,
                draft_path=draft_path,
            )
        )

    return plan


def apply_draft(memory_root: Path, draft_dir: Path) -> ApplyResult:
    memory_root = normalize_root(memory_root)
    draft_dir = draft_dir.expanduser().resolve()
    draft_id = draft_dir.name
    expected_drafts_dir = memory_root / ".remember" / "drafts"
    applied_dir = memory_root / ".remember" / "applied" / draft_id

    if draft_dir.parent != expected_drafts_dir:
        raise ValueError(f"Draft directory must be under: {expected_drafts_dir}")

    if applied_dir.exists():
        raise FileExistsError(f"Applied draft already exists: {applied_dir}")

    plan = build_apply_plan(memory_root=memory_root, draft_dir=draft_dir)

    applied_dir.parent.mkdir(parents=True, exist_ok=True)

    for item in plan:
        item.source_path.write_text(
            item.draft_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    shutil.move(str(draft_dir), str(applied_dir))

    return ApplyResult(
        applied_dir=applied_dir,
        overwritten_files=[item.relative_path for item in plan],
    )


from pathlib import Path, PurePosixPath, PureWindowsPath


def validate_relative_path(path: Path | str) -> Path:
    raw_path = str(path)

    posix_path = PurePosixPath(raw_path)
    windows_path = PureWindowsPath(raw_path)

    if posix_path.is_absolute() or windows_path.is_absolute():
        raise ValueError(f"Absolute path is not allowed: {raw_path}")

    if ".." in posix_path.parts or ".." in windows_path.parts:
        raise ValueError(f"Parent traversal is not allowed: {raw_path}")

    return Path(raw_path)

def normalize_root(path: Path) -> Path:
    return path.expanduser().resolve()


def relative_to_root(path: Path, root: Path) -> Path:
    resolved_root = normalize_root(root)
    resolved_path = path.expanduser().resolve()

    try:
        relative_path = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Path is outside root: {resolved_path}") from exc

    if relative_path.is_absolute():
        raise ValueError(f"Relative path must not be absolute: {relative_path}")

    if ".." in relative_path.parts:
        raise ValueError(f"Parent traversal is not allowed: {relative_path}")

    return relative_path
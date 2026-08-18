from pathlib import Path

import pytest

from hermes_remember_draft.draft_parser import parse_draft_files
from hermes_remember_draft.markdown_io import MarkdownFile


def markdown_file(relative_path: str, content: str) -> MarkdownFile:
    return MarkdownFile(
        path=Path("/tmp/memory") / relative_path,
        relative_path=Path(relative_path),
        content=content,
    )


def test_parse_changed_file() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes Agent\n\nOld.\n"),
    ]

    raw_output = """<<<FILE: hermes-agent.md>>>
# Hermes Agent

Updated.
<<<END FILE>>>"""

    result = parse_draft_files(raw_output, input_markdowns=inputs)

    assert len(result) == 1
    assert result[0].relative_path == Path("hermes-agent.md")
    assert result[0].content == "# Hermes Agent\n\nUpdated."


def test_no_changes_marker_returns_empty_list() -> None:
    result = parse_draft_files(
        "<<<NO CHANGES>>>",
        input_markdowns=[
            markdown_file("lfm2.md", "# LFM2\n"),
        ],
    )

    assert result == []


def test_unchanged_file_is_filtered_out() -> None:
    inputs = [
        markdown_file("lfm2.md", "# LFM2\n\nInitial note.\n"),
    ]

    raw_output = """<<<FILE: lfm2.md>>>
# LFM2

Initial note.
<<<END FILE>>>"""

    result = parse_draft_files(raw_output, input_markdowns=inputs)

    assert result == []


def test_rejects_unknown_output_path() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes\n"),
    ]

    raw_output = """<<<FILE: unknown.md>>>
# Unknown
<<<END FILE>>>"""

    with pytest.raises(ValueError, match="not an input file"):
        parse_draft_files(raw_output, input_markdowns=inputs)


def test_rejects_duplicate_output_path() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes\n"),
    ]

    raw_output = """<<<FILE: hermes-agent.md>>>
# Hermes

One.
<<<END FILE>>>

<<<FILE: hermes-agent.md>>>
# Hermes

Two.
<<<END FILE>>>"""

    with pytest.raises(ValueError, match="Duplicate"):
        parse_draft_files(raw_output, input_markdowns=inputs)


def test_rejects_parent_traversal_path() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes\n"),
    ]

    raw_output = """<<<FILE: ../README.md>>>
bad
<<<END FILE>>>"""

    with pytest.raises(ValueError, match="Parent traversal"):
        parse_draft_files(raw_output, input_markdowns=inputs)


def test_rejects_absolute_path() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes\n"),
    ]

    raw_output = """<<<FILE: /tmp/secret.md>>>
bad
<<<END FILE>>>"""

    with pytest.raises(ValueError, match="Absolute path"):
        parse_draft_files(raw_output, input_markdowns=inputs)


def test_rejects_output_without_file_blocks() -> None:
    inputs = [
        markdown_file("hermes-agent.md", "# Hermes\n"),
    ]

    with pytest.raises(ValueError, match="No valid FILE blocks"):
        parse_draft_files(
            "Here is the updated file.",
            input_markdowns=inputs,
        )



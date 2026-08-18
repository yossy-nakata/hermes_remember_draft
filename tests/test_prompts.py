from pathlib import Path

from hermes_remember_draft.markdown_io import MarkdownFile
from hermes_remember_draft.prompts import build_update_prompt


def test_build_update_prompt_contains_markdown_files_and_conversation() -> None:
    markdowns = [
        MarkdownFile(
            path=Path("/tmp/memory/hermes-agent.md"),
            relative_path=Path("hermes-agent.md"),
            content="# Hermes Agent\n\nOld content.\n",
        ),
        MarkdownFile(
            path=Path("/tmp/memory/architecture/remember-flow.md"),
            relative_path=Path("architecture") / "remember-flow.md",
            content="# Remember Flow\n\nOld flow.\n",
        ),
    ]

    prompt = build_update_prompt(
        markdowns=markdowns,
        conversation="We decided to store drafts under .remember/drafts/.",
    )

    assert "<<<INPUT FILE: hermes-agent.md>>>" in prompt
    assert "<<<INPUT FILE: architecture/remember-flow.md>>>" in prompt
    assert "# Hermes Agent\n\nOld content.\n" in prompt
    assert "# Remember Flow\n\nOld flow.\n" in prompt
    assert "We decided to store drafts under .remember/drafts/." in prompt
    assert "<<<CONVERSATION>>>" in prompt
    assert "<<<END CONVERSATION>>>" in prompt


def test_build_update_prompt_includes_output_format_rules() -> None:
    prompt = build_update_prompt(
        markdowns=[
            MarkdownFile(
                path=Path("/tmp/memory/lfm2.md"),
                relative_path=Path("lfm2.md"),
                content="# LFM2\n",
            )
        ],
        conversation="No meaningful update.",
    )

    assert "<<<FILE: relative/path.md>>>" in prompt
    assert "<<<END FILE>>>" in prompt
    assert "<<<NO CHANGES>>>" in prompt
    assert "Do not output diffs or patches." in prompt
    assert "Do not output unchanged files." in prompt
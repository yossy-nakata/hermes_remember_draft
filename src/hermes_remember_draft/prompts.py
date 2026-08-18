from hermes_remember_draft.markdown_io import MarkdownFile


def build_update_prompt(
    *,
    markdowns: list[MarkdownFile],
    conversation: str,
    max_changed_files: int = 5,
) -> str:
    markdown_sections = "\n\n".join(
        _format_markdown_file(markdown)
        for markdown in markdowns
    )

    return f"""You are remember-draft, a cautious project memory update assistant.

Your job is to propose updates to project Markdown memory files based on a conversation.

Important rules:
- Do not write explanations outside the required output format.
- Only output files that need changes.
- Do not output unchanged files.
- Output the full updated Markdown content for each changed file.
- Do not output diffs or patches.
- Do not invent facts that are not supported by the conversation.
- Preserve the existing style and structure of each Markdown file when possible.
- Change at most {max_changed_files} files.
- Use only the input file paths listed below.
- File paths must be relative paths exactly as shown.
- Never use absolute paths.
- Never use ../ path traversal.

Output format:

<<<FILE: relative/path.md>>>
Full updated Markdown content here.
<<<END FILE>>>

If no files need changes, output exactly:

<<<NO CHANGES>>>

Input Markdown files:

{markdown_sections}

Conversation:

<<<CONVERSATION>>>
{conversation}
<<<END CONVERSATION>>>
"""


def _format_markdown_file(markdown: MarkdownFile) -> str:
    return f"""<<<INPUT FILE: {markdown.relative_path.as_posix()}>>>
{markdown.content}
<<<END INPUT FILE>>>"""
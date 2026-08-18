from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .draft_apply import apply_draft, build_apply_plan
from .draft_diff import build_draft_diffs
from .draft_parser import parse_draft_files
from .draft_writer import write_draft
from .llm_client import LlmConfig, complete_text
from .markdown_io import MarkdownFile, read_markdown_files
from .prompts import build_update_prompt

app = typer.Typer(no_args_is_help=True)
console = Console()

def print_input_files(markdowns: list[MarkdownFile]) -> None:
    table = Table(title="Input files")
    table.add_column("Path")
    table.add_column("Chars", justify="right")
    table.add_column("Bytes", justify="right")

    for markdown in markdowns:
        table.add_row(
            markdown.relative_path.as_posix(),
            f"{markdown.char_count:,}",
            f"{markdown.byte_size:,}",
        )

    console.print()
    console.print(table)

@app.callback()
def main():
    """
    Hermes remember draft tools.
    """


@app.command("draft")
def draft_command(
    files: Annotated[
        list[Path],
        typer.Argument(help="Markdown files to use as update targets"),
    ],
    memory_root: Annotated[
        Path,
        typer.Option("--memory-root", help="Project memory root"),
    ] = Path("memory"),
    conversation: Annotated[
        Path,
        typer.Option("--conversation", help="Conversation text file"),
    ] = Path("conversation.txt"),
    slug: Annotated[
        str,
        typer.Option("--slug", help="Draft slug"),
    ] = "remember-draft",
    dry_run_prompt: Annotated[
        bool,
        typer.Option(
            "--dry-run-prompt",
            help="Build and print the LLM prompt without calling the model",
        ),
    ] = False,
    show_raw_output: Annotated[
        bool,
        typer.Option(
            "--show-raw-output",
            help="Show the raw LLM output",
        ),
    ] = False,
    base_url: Annotated[
        str,
        typer.Option("--base-url", help="OpenAI-compatible API base URL"),
    ] = "http://localhost:8080/v1",
    api_key: Annotated[
        str,
        typer.Option("--api-key", help="API key for OpenAI-compatible API"),
    ] = "local",
    model: Annotated[
        str,
        typer.Option("--model", help="Model name"),
    ] = "lfm2-24b",



):
    console.print("[bold]remember-draft v0.1[/bold]")
    console.print(f"memory_root: {memory_root}")
    console.print(f"conversation: {conversation}")
    console.print(f"slug: {slug}")

    if not conversation.exists():
        console.print(f"[red]Conversation file not found:[/red] {conversation}")
        raise typer.Exit(1)

    try:
        markdowns = read_markdown_files(
            files,
            memory_root=memory_root,
        )
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Input error:[/red] {exc}")
        raise typer.Exit(1) from exc

    print_input_files(markdowns)

    conversation_text = conversation.read_text(encoding="utf-8")
    console.print(f"\n[bold]Conversation chars:[/bold] {len(conversation_text)}")

    prompt = build_update_prompt(
        markdowns=markdowns,
        conversation=conversation_text,
    )

    if dry_run_prompt:
        console.print()
        console.print(
            Panel(
                prompt,
                title="Dry run prompt",
                expand=False,
            )
        )
        console.print("\n[green]OK: prompt built.[/green]")
        raise typer.Exit(0)


    console.print("\n[bold]Calling LLM...[/bold]")

    try:
        raw_output = complete_text(
            prompt,
            config=LlmConfig(
                base_url=base_url,
                api_key=api_key,
                model=model,
            ),
        )
    except Exception as exc:
        console.print(f"[red]LLM call failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    if show_raw_output:
        console.print()
        console.print(
            Panel(
                raw_output,
                title="LLM raw output",
                expand=False,
            )
        )

    try:
        draft_files = parse_draft_files(
            raw_output,
            input_markdowns=markdowns,
        )
    except ValueError as exc:
        console.print(f"[red]Draft parse failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"\n[bold]Parsed changed files:[/bold] {len(draft_files)}")

    for draft_file in draft_files:
        console.print(f"- {draft_file.relative_path.as_posix()}")

    try:
        result = write_draft(
            memory_root=memory_root,
            slug=slug,
            model=model,
            input_files=markdowns,
            changed_files=draft_files,
        )
    except FileExistsError as exc:
        console.print(f"[red]Draft already exists:[/red] {exc}")
        raise typer.Exit(1) from exc
    except OSError as exc:
        console.print(f"[red]Failed to write draft:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"\n[bold]Draft written:[/bold] {result.draft_dir}")
    console.print(f"[bold]Manifest:[/bold] {result.manifest_path}")

    if result.written_files:
        console.print("\n[bold]Written files:[/bold]")
        for path in result.written_files:
            console.print(f"- {path}")
    else:
        console.print("\n[bold]Written files:[/bold] None")

    console.print("\n[green]OK: draft written.[/green]")


@app.command("diff")
def diff_command(
    draft_dir: Annotated[
        Path,
        typer.Argument(help="Draft directory to review"),
    ],
    memory_root: Annotated[
        Path,
        typer.Option("--memory-root", help="Project memory root"),
    ] = Path("memory"),
):
    console.print("[bold]remember-draft v0.1[/bold]")
    console.print(f"memory_root: {memory_root}")
    console.print(f"draft_dir: {draft_dir}")

    try:
        diffs = build_draft_diffs(
            memory_root=memory_root,
            draft_dir=draft_dir,
        )
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Diff error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not diffs:
        console.print("\n[green]No changes.[/green]")
        return

    console.print(f"\n[bold]Changed files:[/bold] {len(diffs)}")

    for item in diffs:
        console.rule(item.relative_path.as_posix())
        console.print(item.diff_text)

    console.print("\n[green]OK: diff generated.[/green]")


@app.command("apply")
def apply_command(
    draft_dir: Annotated[
        Path,
        typer.Argument(help="Draft directory to apply"),
    ],
    memory_root: Annotated[
        Path,
        typer.Option("--memory-root", help="Project memory root"),
    ] = Path("memory"),
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show files that would be overwritten without changing them",
        ),
    ] = False,
):
    console.print("[bold]remember-draft v0.1[/bold]")
    console.print(f"memory_root: {memory_root}")
    console.print(f"draft_dir: {draft_dir}")

    if dry_run:
        console.print("mode: dry-run")

        try:
            plan = build_apply_plan(
                memory_root=memory_root,
                draft_dir=draft_dir,
            )
        except (FileNotFoundError, ValueError) as exc:
            console.print(f"[red]Apply error:[/red] {exc}")
            raise typer.Exit(1) from exc

        if not plan:
            console.print("\n[green]No files to apply.[/green]")
            return

        console.print("\n[bold]Files that would be overwritten:[/bold]")
        for item in plan:
            console.print(f"- {item.relative_path.as_posix()}")

        console.print("\n[green]OK: dry run complete.[/green]")
        return

    try:
        result = apply_draft(
            memory_root=memory_root,
            draft_dir=draft_dir,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Apply error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print("\n[bold]Applied files:[/bold]")
    if result.overwritten_files:
        for path in result.overwritten_files:
            console.print(f"- {path.as_posix()}")
    else:
        console.print("None")

    console.print("\n[bold]Draft moved to:[/bold]")
    console.print(result.applied_dir)

    console.print("\n[green]OK: draft applied.[/green]")

if __name__ == "__main__":
    app()

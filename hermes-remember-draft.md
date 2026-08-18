# hermes-remember-draft

`hermes-remember-draft` is a small CLI helper for creating safe draft updates to project Markdown memory files used with Hermes Agent.

The tool does **not** directly modify your canonical `memory/*.md` files.  
Instead, it asks an LLM to propose updates and saves those proposals as draft revisions under `.remember/drafts/`.

## Concept

This project is for workflows where Hermes Agent reads project memory through Context References such as:

```text
@memory/hermes-agent.md
@memory/architecture/remember-flow.md
```

The main conversation model may use those Markdown files as context, but it should not directly save changes back to them.

Instead, `remember-draft` creates a Git-like draft revision:

```text
memory/*.md
  = canonical project memory

memory/.remember/drafts/<draft-id>/
  = AI-generated update proposal
```

A human can then inspect the generated draft and decide whether to manually apply it.

## MVP Scope

Current MVP supports:

- Reading selected Markdown files safely
- Reading a conversation text file
- Building an update prompt for an OpenAI-compatible LLM endpoint
- Calling a local or remote `llama-server`
- Parsing `<<<FILE: ...>>>` marker output
- Filtering out unchanged files
- Writing draft revisions under `memory/.remember/drafts/`
- Writing `_manifest.md`
- Preserving original relative paths under `files/`

Current MVP does **not** support:

- Directly modifying canonical `memory/*.md`
- Applying drafts automatically
- Managing Git commits
- Reading Hermes Context References directly
- Tool-calling based memory updates

## Expected Memory Layout

```text
memory/
├── hermes-agent.md
├── lfm2.md
├── architecture/
│   └── remember-flow.md
└── .remember/
    ├── sessions/
    │   └── <session-id>.jsonl
    ├── drafts/
    │   └── 2026-08-17_2221__memory-mvp/
    │       ├── _manifest.md
    │       └── files/
    │           ├── hermes-agent.md
    │           └── architecture/
    │               └── remember-flow.md
    ├── applied/
    └── rejected/
```

## Path Rules

Internally, file paths are always handled relative to `--memory-root`.

For example:

```text
memory/architecture/remember-flow.md
```

is represented internally as:

```text
architecture/remember-flow.md
```

This same relative path is used when writing draft files:

```text
memory/.remember/drafts/<draft-id>/files/architecture/remember-flow.md
```

Important rules:

- `memory_root` is normalized as the root of project memory.
- Input Markdown files must be under `memory_root`.
- `.remember/` files are rejected as source Markdown.
- Absolute paths in LLM output are rejected.
- `../` path traversal in LLM output is rejected.
- LLM output paths must match one of the input Markdown files.

## Installation

This project uses `uv`.

```powershell
uv sync
```

The CLI entry point is:

```powershell
remember-draft
```

During development, run it through `uv`:

```powershell
uv run remember-draft
```

## Usage

Create a draft from selected Markdown files and a conversation file:

```powershell
uv run remember-draft draft `
  --memory-root memory `
  --conversation conversation.txt `
  --slug memory-mvp `
  --base-url "http://localhost:8080/v1" `
  --api-key "local" `
  --model "lfm2-24b" `
  memory\hermes-agent.md `
  memory\lfm2.md
```

Example output:

```text
remember-draft v0.1
memory_root: memory
conversation: conversation.txt
slug: memory-mvp

            Input files
┏━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Path            ┃ Chars ┃ Bytes ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ hermes-agent.md │    30 │    30 │
│ lfm2.md         │    22 │    22 │
└─────────────────┴───────┴───────┘

Conversation chars: 89

Calling LLM...

Parsed changed files: 1
- hermes-agent.md

Draft written: memory\.remember\drafts\2026-08-17_2221__memory-mvp
Manifest: memory\.remember\drafts\2026-08-17_2221__memory-mvp\_manifest.md

Written files:
- memory\.remember\drafts\2026-08-17_2221__memory-mvp\files\hermes-agent.md

OK: draft written.
```

## Dry Run Prompt

To inspect the generated prompt without calling the model:

```powershell
uv run remember-draft draft `
  --memory-root memory `
  --conversation conversation.txt `
  --slug memory-mvp `
  --dry-run-prompt `
  memory\hermes-agent.md `
  memory\lfm2.md
```

This is useful when tuning `prompts.py`.

## Show Raw LLM Output

By default, raw LLM output is hidden.

To show it:

```powershell
uv run remember-draft draft `
  --memory-root memory `
  --conversation conversation.txt `
  --slug memory-mvp `
  --base-url "http://localhost:8080/v1" `
  --api-key "local" `
  --model "lfm2-24b" `
  --show-raw-output `
  memory\hermes-agent.md `
  memory\lfm2.md
```

## LLM Output Format

The LLM is instructed to output changed files using this marker format:

```text
<<<FILE: relative/path.md>>>
Full updated Markdown content here.
<<<END FILE>>>
```

If no files need changes, it should output exactly:

```text
<<<NO CHANGES>>>
```

The parser only accepts valid file blocks and filters unchanged files by comparing them to the original input Markdown content.

## Draft Output

Each run creates a draft directory:

```text
memory/.remember/drafts/YYYY-MM-DD_HHMM__slug/
```

Inside it:

```text
_manifest.md
files/
```

`files/` contains only changed files, and each file contains the full updated Markdown content, not a diff.

Example:

```text
memory/.remember/drafts/2026-08-17_2221__memory-mvp/
├── _manifest.md
└── files/
    └── hermes-agent.md
```

## Manifest

Each draft includes `_manifest.md`:

```markdown
# Remember Draft

Status: draft
Created: 2026-08-17 22:21
Slug: memory-mvp
Model: lfm2-24b

## Input Files

- hermes-agent.md
- lfm2.md

## Changed Files

- hermes-agent.md

## Unchanged Files

- lfm2.md

## Summary

Draft generated from conversation and input Markdown files.
```

## Reviewing a Draft

Use `git diff --no-index` to compare a canonical Markdown file with the generated draft file.

```powershell
git diff --no-index `
  memory\hermes-agent.md `
  memory\.remember\drafts\2026-08-17_2221__memory-mvp\files\hermes-agent.md
```

If the draft looks good, manually copy or apply the change to the canonical Markdown file.

MVP intentionally does not provide an `apply` command.

## Development

Run tests:

```powershell
uv run pytest
```

Current test coverage includes:

- Safe Markdown input loading
- `memory_root`-relative path handling
- Rejection of invalid paths
- Prompt generation
- LLM draft output parsing
- Manifest generation
- Draft writing

Run the CLI help:

```powershell
uv run remember-draft
```

## Suggested `.gitignore`

Generated `.remember/` contents are usually runtime artifacts and should not be committed unless intentionally used as fixtures.

```gitignore
memory/.remember/sessions/
memory/.remember/drafts/
memory/.remember/applied/
memory/.remember/rejected/
```

## Design Principle

`remember-draft` is not a Git replacement.

It only creates AI-generated draft proposals from conversations and project Markdown memory.

Git remains responsible for real project history.
Human review remains responsible for accepting or rejecting memory updates.
# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Creating a Note

Via the CLI entrypoint:

```bash
uv run secondbrain new "Remember this idea"
uv run --env-file .env secondbrain new "Use settings from .env"
```

Or as a Python module:

```bash
uv run python -m secondbrain new "Created through Python"
```

On success, the command reports the new file:

```text
Created note: /Users/you/second_brain/20260712-143208-123456.md
```

Run `secondbrain` without a subcommand to see help. The `new` command requires
one `TEXT` argument; quote text containing spaces or shell-special characters.

The file contains exactly the supplied UTF-8 text. Its local-time filename uses
`YYYYMMDD-HHMMSS-ffffff.md`. A collision is stored with a numeric suffix such as
`-1.md` or `-2.md`, and an existing file is never overwritten.

## Listing Notes

List Markdown notes with:

```bash
uv run secondbrain list
```

The command prints the absolute configured note directory and a one-based,
lexicographically ordered list of filenames:

```text
Notes: /Users/you/second_brain
1. project-outline.md
2. reading-list.md
```

Only lowercase `.md` files are included, and only filenames are printed. Empty or
missing note directories are successful and print only the `Notes:` line; `list`
does not create the directory.

## Showing a Note

Use a number from the current list output to print that note in the terminal:

```bash
uv run secondbrain show 2
```

The number is one-based and uses the same note discovery and lexicographic
ordering as `list`. The note is read as UTF-8 and its Markdown contents are
written unchanged, with no rendering, labels, or added trailing newline.

A zero, negative, out-of-range, or stale number produces a concise error and a
non-zero exit status. A missing note directory likewise has no valid indices and
is not created by `show`.

## Environment Variables

| Variable           | Default          | Description                          |
|--------------------|------------------|--------------------------------------|
| `SECOND_BRAIN_DIR` | `~/second_brain` | Note directory                       |
| `LOG_LEVEL`        | `INFO`           | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`         | `app.log`        | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

`SECOND_BRAIN_DIR` may be absolute, relative to the current directory, or start
with `~`. The directory and missing parents are created on the first note.

## Log Output

Both console and file logs use second-resolution timestamps and a compact source
position:

```text
YYYY-MM-DD HH:mm:ss | LVL | module:function:line | message
```

The standard Loguru levels are shown as `TRC`, `DBG`, `INF`, `SUC`, `WRN`,
`ERR`, and `CRT`. The complete name is shown for a custom level.

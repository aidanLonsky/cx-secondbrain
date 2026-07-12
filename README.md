# secondbrain

A small command-line tool for capturing Markdown notes quickly.

## Installation

Clone the repository, then install dependencies:

```bash
uv sync
```

## Usage

Create a note via the CLI entrypoint:

```bash
uv run secondbrain new "Remember to review the project outline"
```

Run with the development environment:

```bash
uv run --env-file .env secondbrain new "An idea from today"
```

Or run as a Python module:

```bash
uv run python -m secondbrain new "A note created through Python"
```

List the Markdown notes in the configured directory:

```bash
uv run secondbrain list
```

Print a listed note directly in the terminal:

```bash
uv run secondbrain show 2
```

The command prints the path it created:

```text
Created note: /Users/you/second_brain/20260712-143208-123456.md
```

Running `secondbrain` without a subcommand displays its help and available
commands.

## Environment Variables

`.env.example` is the committed template. Copy it to `.env` for development.

- `LOG_LEVEL` defaults to `INFO`; `.env` sets it to `DEBUG` for verbose console output.
- `LOG_FILE` defaults to `app.log` and specifies the log-file path.
- `SECOND_BRAIN_DIR` defaults to `~/second_brain` and specifies where notes are stored. Relative paths and paths beginning with `~` are supported.

`uv run --env-file .env` loads the development environment explicitly; it is not loaded automatically.

## Note Files

Notes contain exactly the text supplied to `new`, encoded as UTF-8. Filenames use
the local time in `YYYYMMDD-HHMMSS-ffffff.md` format. If that name already
exists, `secondbrain` appends `-1`, `-2`, and so on rather than overwriting it.

The target directory and any missing parent directories are created automatically.

## Listing Notes

`secondbrain list` prints the absolute configured notes path, followed by Markdown
filenames in lexicographic order with one-based numbering:

```text
Notes: /Users/you/second_brain
1. project-outline.md
2. reading-list.md
```

Only lowercase `.md` files are listed, and filenames (rather than full paths) are
shown. An empty or missing note directory is successful: only the `Notes:` line is
printed, and the directory is not created.

## Showing a Note

`secondbrain show NUMBER` prints the selected note's UTF-8 Markdown contents
unchanged. `NUMBER` is the one-based index from the current `secondbrain list`
output, using the same discovery and ordering rules. The command adds no heading,
formatting, or trailing newline of its own.

If the number is zero, negative, out of range, or stale because the current list
has changed, the command reports an error and exits with a non-zero status.

## Logging

Console and file logs use the same compact format:

```text
YYYY-MM-DD HH:mm:ss | LVL | module:function:line | message
```

Standard levels use the labels `TRC`, `DBG`, `INF`, `SUC`, `WRN`, `ERR`, and
`CRT`. Custom log levels keep their full names.

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview documentation locally:

```bash
uv run python scripts/serve_docs.py
```

Build static documentation:

```bash
uv run mkdocs build
```

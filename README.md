# second-brain

## Installation

Clone the repository, enter the project directory, and install dependencies:

```bash
uv sync
```

## Usage

Run the CLI entrypoint:

```bash
uv run second_brain
```

Load development settings explicitly:

```bash
uv run --env-file .env second_brain
```

Or run the Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

`.env.example` is the configuration template. Copy it to `.env` for development.

- `LOG_LEVEL` defaults to `INFO`; `.env` sets it to `DEBUG` for verbose console output.
- `LOG_FILE` defaults to `app.log` and controls the log file path.

Use `uv run --env-file .env` to load the development environment explicitly; `.env` is not loaded automatically.

## Log Format

Console and file logs use the same compact structure:

```text
2026-07-11 13:07:00 | INF | second_brain.app:main:40 | Hello from second_brain!
```

Each record includes a timestamp with second precision, a three-character severity
label, and the module, function, and source line. Console and file output have an
identical field structure.

## Testing

```bash
uv run pytest
uv run pytest --cov
```

## Documentation

Preview the documentation locally or build the static site:

```bash
uv run python scripts/serve_docs.py
uv run mkdocs build
```

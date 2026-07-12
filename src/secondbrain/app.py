import os
import sys
from datetime import datetime
from pathlib import Path

import click
from loguru import logger

STANDARD_LEVEL_LABELS = {
    "TRACE": "TRC",
    "DEBUG": "DBG",
    "INFO": "INF",
    "SUCCESS": "SUC",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}


def _compact_log_format(record):
    """Return the compact log template with a label derived for this record."""
    level_name = record["level"].name
    record["extra"]["level_label"] = STANDARD_LEVEL_LABELS.get(level_name, level_name)
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{extra[level_label]}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>\n{exception}"
    )


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
    - File handler at DEBUG level writing to LOG_FILE (default: app.log)
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE", "app.log")
    logger.remove()
    logger.add(sys.stderr, level=log_level, format=_compact_log_format)
    logger.add(
        log_file,
        level="DEBUG",
        rotation="50 KB",
        retention=1,
        format=_compact_log_format,
    )


class _HelpGroup(click.Group):
    """A command group that treats an empty invocation as successful help."""

    def parse_args(self, ctx, args):
        if not args and self.no_args_is_help:
            click.echo(ctx.get_help(), color=ctx.color)
            ctx.exit(0)
        return super().parse_args(ctx, args)


def _current_time():
    """Return the current local time."""
    return datetime.now()


def _note_directory():
    """Resolve the configured directory for Markdown notes."""
    configured = os.environ.get("SECOND_BRAIN_DIR")
    if configured is None:
        return Path.home() / "second_brain"
    if configured == "~":
        return Path.home()
    if configured.startswith("~/"):
        return Path.home() / configured[2:]

    directory = Path(configured)
    return directory.expanduser()


def _markdown_notes():
    """Return the absolute note directory and its Markdown files by filename."""
    directory = _note_directory().resolve()
    if not directory.is_dir():
        return directory, []

    notes = sorted(
        (path for path in directory.glob("*.md") if path.is_file()),
        key=lambda path: path.name,
    )
    return directory, notes


def _write_note(directory, text):
    """Create a timestamped note without overwriting an existing file."""
    timestamp = _current_time().strftime("%Y%m%d-%H%M%S-%f")
    suffix = 0

    while True:
        collision_suffix = "" if suffix == 0 else f"-{suffix}"
        path = directory / f"{timestamp}{collision_suffix}.md"
        try:
            with path.open("x", encoding="utf-8") as note:
                note.write(text)
        except FileExistsError:
            suffix += 1
            continue
        except OSError as error:
            raise click.ClickException(f"Could not write note: {error}") from error
        return path


@click.group(cls=_HelpGroup, no_args_is_help=True)
def main():
    """Capture and manage Markdown notes."""


@main.command("new")
@click.argument("text")
def new_note(text):
    """Create a Markdown note containing TEXT."""
    directory = _note_directory()
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise click.ClickException(
            f"Could not prepare note directory {directory}: {error}"
        ) from error

    path = _write_note(directory, text)
    click.echo(f"Created note: {path}")


@main.command("list")
def list_notes():
    """List Markdown notes in the configured directory."""
    directory, notes = _markdown_notes()
    click.echo(f"Notes: {directory}")
    for number, note in enumerate(notes, start=1):
        click.echo(f"{number}. {note.name}")


@main.command("show", context_settings={"ignore_unknown_options": True})
@click.argument("number", type=int)
def show_note(number):
    """Print the note identified by its list NUMBER."""
    _directory, notes = _markdown_notes()
    if number < 1 or number > len(notes):
        raise click.ClickException(f"No note numbered {number}.")

    note = notes[number - 1]
    try:
        content = note.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise click.ClickException(f"Could not read note: {error}") from error

    click.echo(content, nl=False)

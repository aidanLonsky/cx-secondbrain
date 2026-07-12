import re
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import call

from click.testing import CliRunner
from loguru import logger

from secondbrain import app
from secondbrain.app import configure_logging, main

COMPACT_LOG_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| "
    r"(?P<level>\w+) \| (?P<module>[\w.]+):(?P<function>\w+):\d+ \| "
    r"(?P<message>.+)$"
)


def test_bare_command_shows_help_and_new_command():
    result = CliRunner().invoke(main)

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "new" in result.output


def test_new_requires_note_text():
    result = CliRunner().invoke(main, ["new"])

    assert result.exit_code != 0
    assert "Missing argument 'TEXT'" in result.output


def test_new_uses_default_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("SECOND_BRAIN_DIR", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    result = CliRunner().invoke(main, ["new", "default location"])

    assert result.exit_code == 0
    notes = list((tmp_path / "second_brain").glob("*.md"))
    assert len(notes) == 1
    assert notes[0].read_text(encoding="utf-8") == "default location"


def test_new_honors_configured_directory_and_expands_tilde(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("SECOND_BRAIN_DIR", "~/custom/notes")

    result = CliRunner().invoke(main, ["new", "configured location"])

    assert result.exit_code == 0
    notes = list((tmp_path / "custom" / "notes").glob("*.md"))
    assert len(notes) == 1
    assert notes[0].read_text(encoding="utf-8") == "configured location"


def test_new_creates_missing_parent_directories(tmp_path, monkeypatch):
    notes_dir = tmp_path / "missing" / "parents" / "notes"
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(notes_dir))

    result = CliRunner().invoke(main, ["new", "nested"])

    assert result.exit_code == 0
    assert notes_dir.is_dir()


def test_new_writes_exact_markdown_and_reports_path(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))
    text = "# Idea\n\nKeep the *formatting*."

    result = CliRunner().invoke(main, ["new", text])

    assert result.exit_code == 0
    notes = list(tmp_path.glob("*.md"))
    assert len(notes) == 1
    assert notes[0].read_text(encoding="utf-8") == text
    assert result.output == f"Created note: {notes[0]}\n"


def test_new_adds_numeric_suffix_on_timestamp_collision(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))
    monkeypatch.setattr(
        app, "_current_time", lambda: datetime(2026, 7, 12, 9, 8, 7, 654321)
    )
    original = tmp_path / "20260712-090807-654321.md"
    original.write_text("original", encoding="utf-8")

    result = CliRunner().invoke(main, ["new", "second"])

    suffixed = tmp_path / "20260712-090807-654321-1.md"
    assert result.exit_code == 0
    assert original.read_text(encoding="utf-8") == "original"
    assert suffixed.read_text(encoding="utf-8") == "second"


def test_new_reports_directory_preparation_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path / "notes"))
    monkeypatch.setattr(
        Path, "mkdir", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("denied"))
    )

    result = CliRunner().invoke(main, ["new", "text"])

    assert result.exit_code != 0
    assert "Error: Could not prepare note directory" in result.output
    assert "denied" in result.output
    assert "Traceback" not in result.output


def test_new_reports_note_write_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))
    monkeypatch.setattr(
        Path,
        "open",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("read-only")),
    )

    result = CliRunner().invoke(main, ["new", "text"])

    assert result.exit_code != 0
    assert "Error: Could not write note" in result.output
    assert "read-only" in result.output
    assert "Traceback" not in result.output


def test_list_resolves_configured_path_and_reports_exact_output(tmp_path, monkeypatch):
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SECOND_BRAIN_DIR", "notes")

    result = CliRunner().invoke(main, ["list"])

    assert result.exit_code == 0
    assert result.output == f"Notes: {notes_dir.resolve()}\n"


def test_list_shows_sorted_markdown_filenames_only(tmp_path, monkeypatch):
    (tmp_path / "zebra.md").write_text("zebra", encoding="utf-8")
    (tmp_path / "alpha.md").write_text("alpha", encoding="utf-8")
    (tmp_path / "ignored.MD").write_text("ignored", encoding="utf-8")
    (tmp_path / "also-ignored.txt").write_text("ignored", encoding="utf-8")
    (tmp_path / "directory.md").mkdir()
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))

    result = CliRunner().invoke(main, ["list"])

    assert result.exit_code == 0
    assert result.output == (f"Notes: {tmp_path.resolve()}\n1. alpha.md\n2. zebra.md\n")


def test_list_handles_an_empty_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))

    result = CliRunner().invoke(main, ["list"])

    assert result.exit_code == 0
    assert result.output == f"Notes: {tmp_path.resolve()}\n"


def test_list_handles_a_missing_directory_without_creating_it(tmp_path, monkeypatch):
    notes_dir = tmp_path / "missing" / "notes"
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(notes_dir))

    result = CliRunner().invoke(main, ["list"])

    assert result.exit_code == 0
    assert result.output == f"Notes: {notes_dir.resolve()}\n"
    assert not notes_dir.exists()


def test_show_prints_exact_utf8_markdown_using_list_order(tmp_path, monkeypatch):
    (tmp_path / "zebra.md").write_text("not selected", encoding="utf-8")
    content = "# Café\n\nKeep *Markdown* unchanged."
    (tmp_path / "alpha.md").write_text(content, encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))

    result = CliRunner().invoke(main, ["show", "1"])

    assert result.exit_code == 0
    assert result.output == content


def test_show_preserves_a_trailing_newline(tmp_path, monkeypatch):
    content = "line one\nline two\n"
    (tmp_path / "note.md").write_text(content, encoding="utf-8")
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))

    result = CliRunner().invoke(main, ["show", "1"])

    assert result.exit_code == 0
    assert result.output == content


def test_show_rejects_indices_not_in_the_current_list(tmp_path, monkeypatch):
    (tmp_path / "note.md").write_text("content", encoding="utf-8")
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))

    for number in ("0", "-1", "2"):
        result = CliRunner().invoke(main, ["show", number])

        assert result.exit_code != 0
        assert result.output == f"Error: No note numbered {number}.\n"
        assert "Traceback" not in result.output


def test_show_rejects_an_index_when_note_directory_is_missing(tmp_path, monkeypatch):
    notes_dir = tmp_path / "missing" / "notes"
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(notes_dir))

    result = CliRunner().invoke(main, ["show", "1"])

    assert result.exit_code != 0
    assert result.output == "Error: No note numbered 1.\n"
    assert not notes_dir.exists()


def test_show_requires_an_integer_number():
    runner = CliRunner()

    missing = runner.invoke(main, ["show"])
    invalid = runner.invoke(main, ["show", "first"])

    assert missing.exit_code != 0
    assert "Missing argument 'NUMBER'" in missing.output
    assert invalid.exit_code != 0
    assert "'first' is not a valid integer" in invalid.output


def test_show_reports_note_read_errors(tmp_path, monkeypatch):
    (tmp_path / "note.md").write_text("content", encoding="utf-8")
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path))
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("denied")),
    )

    result = CliRunner().invoke(main, ["show", "1"])

    assert result.exit_code != 0
    assert "Error: Could not read note" in result.output
    assert "denied" in result.output
    assert "Traceback" not in result.output


def test_standard_levels_use_compact_labels(capfd, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()

    messages_and_labels = [
        ("TRACE", "TRC"),
        ("DEBUG", "DBG"),
        ("INFO", "INF"),
        ("SUCCESS", "SUC"),
        ("WARNING", "WRN"),
        ("ERROR", "ERR"),
        ("CRITICAL", "CRT"),
    ]
    for level, _label in messages_and_labels:
        logger.log(level, f"message-{level.lower()}")

    lines = capfd.readouterr().err.splitlines()
    assert len(lines) == len(messages_and_labels)
    for line, (level, label) in zip(lines, messages_and_labels, strict=True):
        match = COMPACT_LOG_PATTERN.fullmatch(line)
        assert match is not None
        assert match.group("level") == label
        assert match.group("module").endswith("test_app")
        assert match.group("message") == f"message-{level.lower()}"


def test_custom_level_keeps_its_full_name(capfd, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    try:
        logger.level("NOTICE")
    except ValueError:
        logger.level("NOTICE", no=35)
    configure_logging()

    logger.log("NOTICE", "custom-level")

    line = capfd.readouterr().err.strip()
    match = COMPACT_LOG_PATTERN.fullmatch(line)
    assert match is not None
    assert match.group("level") == "NOTICE"


def test_console_and_file_use_compact_output(capfd, tmp_path, monkeypatch):
    log_file = tmp_path / "compact.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))
    configure_logging()

    logger.info("compact-output")

    console_line = capfd.readouterr().err.strip()
    file_line = log_file.read_text().strip()
    for line in (console_line, file_line):
        match = COMPACT_LOG_PATTERN.fullmatch(line)
        assert match is not None
        assert match.group("level") == "INF"
        assert match.group("module").endswith("test_app")
        assert match.group("function") == "test_console_and_file_use_compact_output"
        assert match.group("message") == "compact-output"
        assert not re.search(r"\d{2}:\d{2}:\d{2}\.\d+", line)


def test_sink_configuration_is_preserved(monkeypatch):
    log_file = "/tmp/preserved.log"
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("LOG_FILE", log_file)

    # Capture calls without configuring real sinks.
    calls = []
    monkeypatch.setattr(
        "secondbrain.app.logger.add",
        lambda *args, **kwargs: calls.append(call(*args, **kwargs)),
    )
    configure_logging()

    assert len(calls) == 2
    console_args, console_kwargs = calls[0].args, calls[0].kwargs
    file_args, file_kwargs = calls[1].args, calls[1].kwargs
    assert console_args == (sys.stderr,)
    assert console_kwargs["level"] == "WARNING"
    assert file_args == (log_file,)
    assert file_kwargs["level"] == "DEBUG"
    assert file_kwargs["rotation"] == "50 KB"
    assert file_kwargs["retention"] == 1
    assert console_kwargs["format"] is file_kwargs["format"]

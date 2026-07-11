import re

from loguru import logger

from second_brain.app import main


def test_main_uses_compact_format_for_console_and_file(capfd, tmp_path, monkeypatch):
    log_file = tmp_path / "compact.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    main()

    captured = capfd.readouterr()
    console_record = captured.err.rstrip("\n")
    file_record = log_file.read_text().rstrip("\n")

    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        r" \| INF \| second_brain\.app:main:\d+"
        r" \| Hello from second_brain!",
        console_record,
    )
    assert " - " not in console_record
    assert file_record == console_record


def test_standard_log_levels_are_truncated_to_three_characters(capfd):
    main()
    capfd.readouterr()

    logger.debug("debug")
    logger.info("info")
    logger.success("success")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

    records = capfd.readouterr().err.splitlines()
    assert [record.split(" | ")[1] for record in records] == [
        "DEB",
        "INF",
        "SUC",
        "WAR",
        "ERR",
        "CRI",
    ]

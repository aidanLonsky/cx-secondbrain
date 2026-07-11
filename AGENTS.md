Scaffold a best-practice Python application project. Before starting, ask me the following as plain questions in your reply, then wait for my answers before creating any files:

1. The project/package name (e.g. "myapp")
2. The starting version (default: 0.0.1)
3. Where to scaffold: in the current directory, or in a new subdirectory named after the project

Sanitize the package name: convert it to a valid Python package name by lowercasing, replacing hyphens/spaces/special characters with underscores, stripping leading numbers, and ensuring it's a valid Python identifier. Use the sanitized name for the package directory and imports. For the project directory and pyproject.toml project name, lowercase the input and replace spaces/special characters with hyphens.

Then create the following structure (rooted at the chosen location):

<project-root>/
  src/
    <packagename>/
      __init__.py
      __main__.py
      app.py
  tests/
    __init__.py
    conftest.py
    test_app.py
  scripts/
    serve_docs.py
  docs/
    index.md
    usage.md
    api.md
  mkdocs.yml
  pyproject.toml
  README.md
  .gitignore
  .env.example
  .env          (not committed — in .gitignore)
  .env.test     (not committed — in .gitignore)

If the user chose "current directory", <project-root> is the current working directory. If the user chose "new subdirectory", create a project-name/ directory and use that as <project-root>.

Requirements:

- **Package manager:** uv
- **Config:** pyproject.toml only (no setup.py, no setup.cfg)
- **Layout:** src/ layout, installable package
- **Type hints:** none
- **Versioning:** single source of truth in pyproject.toml

### pyproject.toml
- Use the uv_build build backend:
  ```
  [build-system]
  requires = ["uv_build>=0.10.9,<0.11.0"]
  build-backend = "uv_build"
  ```
- Set the version from the user's answer
- Configure ruff for linting + formatting:
  - Set line-length to 88
  - Set target-version to "py313"
  - Under [tool.ruff.lint], set select = ["E", "F", "B", "I", "UP"] and ignore = ["E501"]
  - Under [tool.ruff.format], set quote-style = "double" and indent-style = "space"
- Add loguru as a dependency
- Add dev dependencies using [dependency-groups]:
  ```
  [dependency-groups]
  dev = [
      "ruff>=0.11",
      "pytest>=8.0",
      "pytest-cov>=6.0",
      "pytest-env>=1.1",
      "mkdocs>=1.6",
      "mkdocs-material>=9.6",
      "mkdocstrings[python]>=0.27",
  ]
  ```
- Add a [project.scripts] entrypoint: <packagename> = "<packagename>.app:main"
- Set requires-python to >= 3.13
- Add pytest configuration:
  ```
  [tool.pytest.ini_options]
  addopts = [
      "--import-mode=importlib",
      "--strict-markers",
      "--strict-config",
      "-ra",
  ]
  testpaths = ["tests"]
  ```
- Add pytest-env configuration to load test environment variables:
  ```
  [tool.pytest_env]
  env_files = [".env.test"]
  ```
- Add coverage configuration:
  ```
  [tool.coverage.run]
  branch = true
  source = ["src"]
  omit = ["src/*/__main__.py"]

  [tool.coverage.report]
  show_missing = true
  fail_under = 80
  exclude_also = [
      "if __name__ == .__main__.:",
      "if TYPE_CHECKING:",
  ]
  ```

### src/<packagename>/__init__.py
- Empty file

### src/<packagename>/__main__.py
- Import and call main() from app.py

### src/<packagename>/app.py
- Define a `configure_logging()` function that:
  1. Imports `os`
  2. Reads `LOG_LEVEL` from `os.environ.get("LOG_LEVEL", "INFO")`
  3. Reads `LOG_FILE` from `os.environ.get("LOG_FILE", "app.log")`
  4. Removes the default loguru handler
  5. Adds a stderr handler at the `LOG_LEVEL` level (default: INFO)
  6. Adds a file handler at DEBUG level using the `LOG_FILE` path with 50 KB rotation and 1 retained backup (no compression)
  Add a Google-style docstring:
  ```python
  def configure_logging():
      """Configure loguru for console and file logging.

      Removes the default handler and sets up:
      - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
      - File handler at DEBUG level writing to LOG_FILE (default: app.log)
      """
      import os
      log_level = os.environ.get("LOG_LEVEL", "INFO")
      log_file = os.environ.get("LOG_FILE", "app.log")
      logger.remove()
      logger.add(sys.stderr, level=log_level)
      logger.add(log_file, level="DEBUG", rotation="50 KB", retention=1)
  ```
- Define a `main()` function decorated with `@logger.catch` (to automatically log unhandled exceptions with full tracebacks) that:
  1. Calls `configure_logging()`
  2. Logs an info message: "Hello from <packagename>!" (so the user sees output in the console and the log file)
  Add a Google-style docstring:
  ```python
  def main():
      """Run the application.

      Configures logging and prints a greeting to verify the setup works.
      """
  ```

### tests/__init__.py
- Empty file

### tests/conftest.py
- Module docstring: """Shared test fixtures."""
- Add an autouse fixture that redirects log file output to pytest's `tmp_path` (so tests never write to `app.log` in the project root):
  ```python
  @pytest.fixture(autouse=True)
  def _test_log_file(tmp_path, monkeypatch):
      monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))
  ```

### tests/test_app.py
- Import `main` from `<packagename>.app`
- Write a test function `test_main_logs_greeting()` that:
  1. Calls `main()`
  2. Asserts that "Hello from <packagename>!" appears in the captured log output
  Use `capfd` to capture stderr (where loguru writes by default). Example approach:
  ```python
  def test_main_logs_greeting(capfd):
      main()
      captured = capfd.readouterr()
      assert "Hello from <packagename>!" in captured.err
  ```

### .env.example
This file IS committed to version control as a template:
```
# Environment configuration for <packagename>
# Copy to .env for development: cp .env.example .env
LOG_LEVEL=DEBUG
LOG_FILE=app.log
```

### .env
This file is created by the scaffold for convenience but must NOT be committed (it's in .gitignore):
```
# Development environment
LOG_LEVEL=DEBUG
LOG_FILE=app.log
```

### .env.test
This file is NOT committed (it's in .gitignore). It is loaded automatically by pytest-env during test runs:
```
# Test environment
LOG_LEVEL=DEBUG
```

### mkdocs.yml
Create a minimal but modern Material for MkDocs configuration:
```yaml
site_name: <project-name>
site_description: Documentation for <project-name>

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - content.code.copy
    - navigation.footer

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            docstring_style: google
            show_source: true

markdown_extensions:
  - admonition
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.details

nav:
  - Home: index.md
  - Usage: usage.md
  - API Reference: api.md
```

### docs/index.md
```markdown
# <project-name>

Welcome to the **<project-name>** documentation.

## Overview

<project-name> is a Python application.

## Quick Links

- [Usage Guide](usage.md) — installation and running instructions
- [API Reference](api.md) — auto-generated from source code
```

### docs/usage.md
```markdown
# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run <packagename>                          # production defaults
uv run --env-file .env <packagename>          # dev settings
```

Or as a Python module:

```bash
uv run python -m <packagename>
```

## Environment Variables

| Variable    | Default    | Description                          |
|-------------|------------|--------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`  | `app.log`  | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.
```

### docs/api.md
```markdown
# API Reference

::: <packagename>
    options:
      show_submodules: true
```

### scripts/serve_docs.py
A small wrapper that runs `mkdocs serve` and tees output to both the terminal and `mkdocs.log`, so the coding agent can read server logs from a file:
```python
#!/usr/bin/env python3
"""Serve MkDocs with output captured to mkdocs.log."""
import subprocess
import sys


def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "mkdocs", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    try:
        with open("mkdocs.log", "w") as log:
            for line in proc.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
```

### README.md
- Project title as h1
- An "Installation" section explaining how to set up the project:
  - Clone the repo
  - Run `uv sync` to install dependencies
- A "Usage" section explaining how to run the app:
  - Via the CLI entrypoint: `uv run <packagename>`
  - With dev environment: `uv run --env-file .env <packagename>`
  - Via python module: `uv run python -m <packagename>`
- An "Environment Variables" section:
  - Explain that `.env.example` is the template — copy it to `.env` for development
  - Document `LOG_LEVEL` (default: INFO, set to DEBUG in `.env` for verbose console output)
  - Document `LOG_FILE` (default: app.log, path to the log file)
  - Note that `uv run --env-file .env` loads the dev environment explicitly (no auto-loading)
- A "Testing" section:
  - Run tests: `uv run pytest`
  - Run tests with coverage: `uv run pytest --cov`
- A "Documentation" section:
  - Preview docs locally: `uv run python scripts/serve_docs.py`
  - Build static docs: `uv run mkdocs build`

### .gitignore
- Fetch the contents from https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore and use it as the .gitignore
- Append entries for: .ruff_cache, *.log, site/, htmlcov/, .coverage, .env, .env.test

After scaffolding:
1. Run `uv sync` to set up the environment
2. Run `uv run pytest` to verify the starter test passes
3. Remind the user to:
   - Commit `uv.lock` to version control for reproducible installs
   - Try `uv run python scripts/serve_docs.py` to preview the documentation locally

# Flowcharts

These diagrams describe the package structure, command-line interface, and a
typical note-taking workflow.

## Package overview

```mermaid
flowchart LR
    subgraph Package["secondbrain package"]
        direction TB
        Init["__init__.py<br/>package marker"]
        Main["__main__.py"]
        App["app.py"]

        Main -->|"from .app import main"| CLI["main()"]

        subgraph Commands["Click commands in app.py"]
            direction TB
            CLI --> New["new_note(text)"]
            CLI --> List["list_notes()"]
            CLI --> Show["show_note(number)"]
            Help["_HelpGroup.parse_args()"] -->|"no command: print help"| CLI
        end

        subgraph Helpers["Supporting functions in app.py"]
            direction TB
            Time["_current_time()"]
            NoteDir["_note_directory()"]
            Notes["_markdown_notes()"]
            Write["_write_note(directory, text)"]
            Logging["configure_logging()"]
            Format["_compact_log_format(record)"]
        end
    end

    subgraph Libraries["Python libraries"]
        direction TB
        Click["click<br/>commands, arguments, errors"]
        Pathlib["pathlib.Path<br/>files and directories"]
        DateTime["datetime<br/>timestamp"]
        OS["os<br/>environment variables"]
        Sys["sys<br/>stderr"]
        Loguru["loguru.logger<br/>logging handlers"]
    end

    subgraph Storage["User storage"]
        direction TB
        Env["Environment<br/>SECOND_BRAIN_DIR"]
        NoteFiles["Configured note folder<br/>*.md files"]
        LogFile["LOG_FILE<br/>app.log by default"]
    end

    CLI --> Click
    New --> NoteDir
    New --> Write
    List --> Notes
    Show --> Notes
    NoteDir --> Env
    Notes --> NoteDir
    Notes --> NoteFiles
    Write --> Time
    Write --> NoteFiles
    Time --> DateTime
    NoteDir --> OS
    NoteDir --> Pathlib
    Notes --> Pathlib
    Write --> Pathlib
    Logging --> Format
    Logging --> Sys
    Logging --> Loguru
    Logging --> LogFile
```

`configure_logging()` is available for callers to configure Loguru, but the
current CLI entry points do not call it themselves.

## CLI entry points and commands

```mermaid
flowchart LR
    subgraph WaysIn["Ways to start the package"]
        direction TB
        Script["secondbrain<br/>installed console script"]
        Module["python -m secondbrain"]
    end

    Script --> AppMain["secondbrain.app:main"]
    Module --> ModuleFile["__main__.py"]
    ModuleFile -->|"imports main"| AppMain

    AppMain --> Group["Click group: main()"]
    Group --> Empty["No subcommand"]
    Empty --> Help["_HelpGroup<br/>show help; exit 0"]

    Group --> NewCmd["new TEXT"]
    Group --> ListCmd["list"]
    Group --> ShowCmd["show NUMBER"]

    NewCmd --> NewFn["new_note(text)"]
    NewFn --> NewDir["Resolve SECOND_BRAIN_DIR<br/>default: ~/second_brain"]
    NewDir --> MakeDir["Create directory if needed"]
    MakeDir --> WriteFile["Write timestamped UTF-8<br/>Markdown file"]
    WriteFile --> Created["Print: Created note: PATH"]

    ListCmd --> ListFn["list_notes()"]
    ListFn --> Discover["Find lowercase *.md files<br/>sort by filename"]
    Discover --> Listed["Print numbered filenames"]

    ShowCmd --> ShowFn["show_note(number)"]
    ShowFn --> DiscoverShow["Find and sort current *.md files"]
    DiscoverShow --> Validate["NUMBER is a valid<br/>one-based index?"]
    Validate -->|"Yes"| PrintFile["Print selected UTF-8 content"]
    Validate -->|"No"| Error["Click error; non-zero exit"]
```

## Example user flow

```mermaid
flowchart LR
    Start(["User has an idea"]) --> Create["Run:<br/>secondbrain new 'Buy milk'"]
    Create --> Configured{"SECOND_BRAIN_DIR<br/>configured?"}
    Configured -->|"No"| DefaultDir["Use ~/second_brain"]
    Configured -->|"Yes"| CustomDir["Use configured folder"]
    DefaultDir --> Ensure["Create folder if missing"]
    CustomDir --> Ensure
    Ensure --> Saved["Save a timestamped<br/>.md note"]
    Saved --> Confirm["See created file path"]

    Confirm --> Review["Later, run:<br/>secondbrain list"]
    Review --> Results{"Notes found?"}
    Results -->|"No"| Empty["See folder path only"]
    Results -->|"Yes"| Choose["Read a number from the list"]
    Choose --> Open["Run:<br/>secondbrain show 1"]
    Open --> Valid{"Number still valid?"}
    Valid -->|"Yes"| Read["Read note text in terminal"]
    Valid -->|"No"| Retry["See error, then list again"]
    Retry --> Review
```

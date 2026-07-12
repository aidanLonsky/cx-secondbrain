# API Reference

The installed `secondbrain` entry point and `python -m secondbrain` both invoke
the same Click command group.

::: secondbrain.app
    options:
      members:
        - main
        - new_note
        - list_notes
        - configure_logging

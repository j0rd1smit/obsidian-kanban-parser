# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Just commands to run in the terminal for development and testing:
```bash
just install      # uv sync --all-extras
just test         # run pytest
just format       # run pre-commit on all files (ruff lint + format + mypy + yaml checks)
just typecheck    # run mypy only
```
Prefer these over direct command (like `uv run pytest`) since they set the right environment variables and ensure consistency, unless absolutely necessary to run a command directly.

Single test:
```bash
uv run pytest tests/test_high_level_smoketest.py::test_name
```



## Architecture

This library parses Obsidian Kanban plugin markdown files into Python objects and writes them back with round-trip fidelity.

**Data flow:** `parse(text)` → `KanbanBoard` → mutate → `write(board)` → text

**Domain layer** (`domain.py`): Three dataclasses — `KanbanBoard` (top-level, holds lanes + archive + frontmatter + settings), `KanbanLane` (column with items + WIP limit), `KanbanItem` (card with `title_raw` as canonical source of truth). Metadata (tags, dates, inline fields) is parsed on-the-fly from `title_raw` via properties.

**Parser** (`parser.py`): Regex-based parser that handles: YAML frontmatter, `%% kanban:settings %%` JSON block, `## Lane` headings with optional WIP limit `(n)`, `- [x]` checkbox items with optional block IDs (`^id`), and `*** / ## Archive` sections. Raw strings are preserved in `_frontmatter_raw` and `_settings_raw` for write-back fidelity.

**Writer** (`writer.py`): Mirrors the Obsidian plugin's own serialization (`itemToMd`, `laneToMd`, etc.). Uses preserved raw strings when available; falls back to regenerating from parsed data.

**Data manipulation** (`data_manipulation.py`): Higher-level helpers for querying and mutating boards — `find_items_by_tag`, `find_items_by_date`, `find_items_by_inline_field`, `move_item`, `archive_item`, `add_item`, `add_subtask`, etc.

**Public API** (`__init__.py`): Exports `parse`, `write`, and the main query/manipulation functions.

**Parsing utils** (`utils/parsing_utils.py`): Low-level string transforms mirroring the Obsidian plugin's JS functions — `_indent_newlines` / `_dedent_newlines` (4-space or tab continuation), `_replace_brs` / `_replace_newlines` (lane title `<br>` handling).

## Key design decisions

- `title_raw` is the single source of truth for a `KanbanItem`'s content. Never construct display text separately.
- The parser preserves raw frontmatter and settings strings to avoid reformatting on write-back.
- All utility functions in `parsing_utils.py` are intentionally private (underscore prefix) — they mirror JS internals and are not part of the public API.
- Requires Python 3.14+.

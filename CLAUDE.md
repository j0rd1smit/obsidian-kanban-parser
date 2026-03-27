# CLAUDE.md

## Commands

Just commands to run in the terminal for development and testing:
```bash
just install
just linting    # Format the code and check for linting issues
just typecheck  # type checks the codebase
just test       # run the test suite
```
Prefer these over direct command (like `uv run pytest`) since they set the right environment variables and ensure consistency, unless absolutely necessary to run a command directly.




## Architecture

This library parses Obsidian Kanban plugin markdown files into Python objects and writes them back with round-trip fidelity.

**Data flow:** `parse(text)` → `KanbanBoard` → mutate → `write(board)` → text

**Domain layer** (`domain.py`): Three dataclasses — `KanbanBoard` (top-level, holds lanes + archive + frontmatter + settings), `KanbanLane` (column with items + WIP limit), `KanbanItem` (card with `title_raw` as canonical source of truth). Metadata (tags, dates, inline fields) is parsed on-the-fly from `title_raw` via properties.

**Parser** (`parser.py`): Regex-based parser that handles: YAML frontmatter, `%% kanban:settings %%` JSON block, `## Lane` headings with optional WIP limit `(n)`, `- [x]` checkbox items with optional block IDs (`^id`), and `*** / ## Archive` sections. Raw strings are preserved in `_frontmatter_raw` and `_settings_raw` for write-back fidelity.

**Writer** (`writer.py`): Mirrors the Obsidian plugin's own serialization (`itemToMd`, `laneToMd`, etc.). Uses preserved raw strings when available; falls back to regenerating from parsed data.

**Data manipulation** (`data_manipulation.py`): Higher-level helpers for querying and mutating boards — `find_items_by_tag`, `find_items_by_inline_field`, `find_lane_by_name`, `move_item`, `archive_item`, `unarchive_item`, `add_item`, `remove_item`, `add_subtask`, `remove_subtask`, `get_subtasks`.

**Public API** (`__init__.py`): Exports `parse`, `write`, and the main query/manipulation functions.

**Parsing utils** (`utils/parsing_utils.py`): Low-level string transforms mirroring the Obsidian plugin's JS functions — `_indent_newlines` / `_dedent_newlines` (4-space or tab continuation), `_replace_brs` / `_replace_newlines` (lane title `<br>` handling).

## Key design decisions

- `title_raw` is the single source of truth for a `KanbanItem`'s content. Never construct display text separately.
- The parser preserves raw frontmatter and settings strings to avoid reformatting on write-back.
- All utility functions in `parsing_utils.py` are intentionally private (underscore prefix) — they mirror JS internals and are not part of the public API.
- Requires Python 3.14+.

## Way of working
- When adding a new feature do this in a test driven way: write test -> write feature -> ensure test pass -> refactor -> repeat as necessary.
- Before finishing any coding task, make sure that:
    - You verified that the code base is in the correct state by run the `just linting`, `just typecheck`, and `just test` commands.
    - You updated out-of-date information in this `CLAUDE.md` file.
    - The `README.md` file is up to date and your changes are reflected in the documentation and examples.
- When implementing tests, keep the following in mind:
  - Test suite should focus on high-level functionality read -> manipulate -> write such that the implementation details can easily be changed without breaking tests, as long as the high-level functionality is preserved. So the arrange part should focus on creating input boards in markdown format, while the assert part should focus on comparing the output markdown with expected markdown.
  - Test suite should have various helper function to make the arrange-act-assert pattern easy to follow and repeat across test cases. E.g. builder function, common assertions, etc.
  - Test cases should follow the arrange-act-assert pattern, and be structured in a way that is easy to read and understand.
  - Keep arrange, act, and assert strictly separated — helpers must not cross these boundaries. Assertion helpers accept already-resolved objects (`KanbanBoard`, `KanbanLane`) rather than raw markdown; callers are responsible for parsing and resolving before asserting. This keeps helpers small, composable, and reusable. For example: parse the board, call `find_lane_by_name`, then pass the lane to `assert_item_in_lane` — don't bundle those steps inside the assertion helper.
- You can store memories and other things you want to remember from feedback and previous conversations in the `memories` directory. It contains an index file at `memory/MEMORY.md` that has an overview of the different memories and there paths.

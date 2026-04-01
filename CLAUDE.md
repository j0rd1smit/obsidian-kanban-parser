# CLAUDE.md

## Commands

Just commands to run in the terminal for development and testing:
```bash
just install
just linting      # Format the code and check for linting issues
just typecheck    # type checks the codebase
just test         # run the test suite
just ruff_check   # run ruff check with --fix to automatically fix issues
just ruff_format  # run ruff format to format the code
```
Prefer these over direct command (like `uv run pytest`) since they set the right environment variables and ensure consistency, unless absolutely necessary to run a command directly.




## Architecture

This library parses Obsidian Kanban plugin markdown files into Python objects and writes them back with round-trip fidelity.

**Data flow:** `parse(text)` → `KanbanBoard` → mutate → `write(board)` → text

**Domain layer** (`domain.py`): Four dataclasses — `KanbanBoard` (top-level, holds lanes + archive + frontmatter + settings), `KanbanLane` (column with items + WIP limit), `KanbanItem` (card with `content` as canonical source of truth), `SubTask` (subtask with `checked` and `text`). Metadata (dates, inline fields) is parsed on-the-fly from `content` via properties. Each class exposes Pythonic dunder methods:
- `KanbanItem`: `content` (str field, canonical source of truth), `checked` (readable/writable bool property), `tags` (`Tags` proxy — set-like with `add`, `remove`, `__contains__`, `__len__`, `__iter__`), `inline_fields` (`InlineFields` proxy — dict-like with `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`), `subtasks` (returns `list[SubTask]`), `add_subtask`, `remove_subtask`, `create(content, checked, block_id)` (static factory).
- `KanbanLane`: `__iter__`, `__contains__`, `__len__`, `__getitem__`, `add_item(content, checked, position)`, `remove_item`, `sort(key=None)`.
- `KanbanBoard`: `__iter__`, `__len__`, `__getitem__` (by lane title str or int index), `lane(title)` (returns `None` if missing), `archive_item`, `unarchive_item`.

**Parser** (`parser.py`): Regex-based parser that handles: YAML frontmatter, `%% kanban:settings %%` JSON block, `## Lane` headings with optional WIP limit `(n)`, `- [x]` checkbox items with optional block IDs (`^id`), and `*** / ## Archive` sections. Raw strings are preserved in `_frontmatter_raw` and `_settings_raw` for write-back fidelity.

**Writer** (`writer.py`): Mirrors the Obsidian plugin's own serialization (`itemToMd`, `laneToMd`, etc.). Uses preserved raw strings when available; falls back to regenerating from parsed data.

**Data manipulation** (`data_manipulation.py`): Contains only `move_item(item, from_lane, to_lane, position=-1)` — operates directly on lane objects, no board or string lookups needed.

**Public API** (`__init__.py`): Exports `parse`, `write`, `move_item`, `KanbanBoard`, `KanbanLane`, `KanbanItem`, `SubTask`.

**Parsing utils** (`utils/parsing_utils.py`): Low-level string transforms mirroring the Obsidian plugin's JS functions — `_indent_newlines` / `_dedent_newlines` (4-space or tab continuation), `_replace_brs` / `_replace_newlines` (lane title `<br>` handling).

## Key design decisions

- `content` is the single source of truth for a `KanbanItem`'s text. Never construct display text separately.
- The parser preserves raw frontmatter and settings strings to avoid reformatting on write-back.
- All utility functions in `parsing_utils.py` are intentionally private (underscore prefix) — they mirror JS internals and are not part of the public API.
- Requires Python 3.14+.

## Obsidian kanban plugin source code references
The source code of the Obsidian kanban plugin can be found in the git submodule at `./obsidian-kanban`.
Some files of interest are:
- `./obsidian-kanbansrc/parsers/helpers/parser.ts`
- `./obsidian-kanbansrc/parsers/helpers/parser`
- `./obsidian-kanbansrc/parsers/formats/list.ts`
- `./obsidian-kanbansrc/parsers/common.ts`
- etc.

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
  - Keep arrange, act, and assert strictly separated — helpers must not cross these boundaries. Assertion helpers accept already-resolved objects (`KanbanBoard`, `KanbanLane`) rather than raw markdown; callers are responsible for parsing and resolving before asserting. This keeps helpers small, composable, and reusable. For example: parse the board, call `board.lane(title)`, then pass the lane to `assert_item_in_lane` — don't bundle those steps inside the assertion helper.
- You can store memories and other things you want to remember from feedback and previous conversations in the `memories` directory. It contains an index file at `memory/MEMORY.md` that has an overview of the different memories and there paths.

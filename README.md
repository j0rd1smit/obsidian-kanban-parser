# obsidian-kanban-parser
This libray is a Python based parser and writer for Markdown files created by the [Obsidian Kanban plugin](https://github.com/obsidian-community/obsidian-kanban).
It purpose is to allow users to manipulate their Kanban boards programmatically, via Python based scripts, while ensuring the that resulting Markdown files remain fully compatible with the Obsidian plugin.


## Design Principles
- Round-trip fidelity: parsing and then writing a file should produce identical content, preserving formatting and metadata.
- To ensure compatibility with the Obsidian plugin, the library should mirror the plugin's own parsing and serialization logic as closely as possible (e.g. mimicking files like: [src/parsers/helpers/parser.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/helpers/parser.ts), [src/parsers/formats/list.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/formats/list.ts), [src/parsers/common.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/common.ts), , etc.).
- The library should provide a clean and well design API with properties such as:
  - Pythonic data structures.
  - There should only be a single way of doing things, and it should be the most intuitive way.
  - There should be a single source of truth for each piece of data.
  - The library should be designed with extensibility in mind.
  - The code must be easy to read and understand by both humans and machines (e.g. for LLMs).
  - The library should be well tested, with a comprehensive test suite covering all functionality and edge
  - The API exposed via the package should be stable and not expose internal implementation details or utilities that are not intended for public use.

### Testing principles
- Test cases should follow the arrange-act-assert pattern, and be structured in a way that is easy to read and understand.
- Test suite should have various helper function to make the arrange-act-assert pattern easy to follow and repeat across test cases. E.g. builder function, common assertions, etc.
- Test suite should focus on high-level functionality read -> manipulate -> write such that the implementation details can easily be changed without breaking tests, as long as the high-level functionality is preserved. So the arrange part should focus on creating input boards in markdown format, while the assert part should focus on comparing the output markdown with expected markdown.
- Whenever possible, test cases should use parameterization to cover multiple scenarios with the same test logic, to reduce code duplication and improve readability.


## Features
The API should allow users to easily make script that preform actions such as:

- Read and write Kanban board(s).
- Find tasks with specific tags or inline fields.
- Add, update, and remove tags and inline fields from tasks.
- Find lanes with specific names.
- Update line properties such as WIP limits, title, etc.
- Move tasks between lanes and boards.
- Loop through tasks in a lane or board.
- Loop through subtasks of a task.
- Add and remove tasks from lanes.
- Archive and unarchive tasks.
- Read, update, remove, and add frontmatter and settings.

## API

### Public exports

```python
from obsidian_kanban_parser import parse, write, move_item, KanbanBoard, KanbanLane, KanbanItem, SubTask
```

### Parsing and writing

```python
board = parse(markdown_text)   # str -> KanbanBoard
text = write(board)            # KanbanBoard -> str
```

### Navigating the board

```python
# Iterate over lanes
for lane in board:
    print(lane.title, len(lane))

# Access lanes by name or index
todo_lane = board["Todo"]       # KeyError if not found
first_lane = board[0]
todo_lane = board.lane("Todo")  # None if not found

# Iterate over items in a lane
for item in todo_lane:
    print(item.content)

# Index into a lane
first_item = todo_lane[0]

# Check membership
if item in todo_lane:
    ...
```

### Tags

```python
item = lane.items[0]

# Read
list(item.tags)          # ["#bug", "#frontend"]
len(item.tags)           # 2
"#bug" in item.tags      # True
"bug" in item.tags       # True (# prefix optional)

# Mutate
item.tags.add("#urgent")         # idempotent
item.tags.remove("#bug")         # safe if absent
```

### Inline fields

```python
item.inline_fields["due"]               # datetime.date | int | float | str | None
item.inline_fields["due"] = date(2024, 6, 1)
del item.inline_fields["due"]
"due" in item.inline_fields             # True / False
```

### Checked state

```python
item.checked          # bool
item.checked = True   # writable
```

### Subtasks

```python
item.subtasks                        # list[SubTask]  (SubTask.checked, SubTask.text)
item.add_subtask("Step 1")           # unchecked
item.add_subtask("Done", checked=True)
item.remove_subtask("Step 1")        # returns True if found
```

### Adding and removing items

```python
new_item = lane.add_item("My new task")
new_item = lane.add_item("My new task", position=0)   # prepend
new_item = lane.add_item("Done task", checked=True)
lane.remove_item(item)   # returns True on success

# Factory for manual construction
item = KanbanItem.create("My task", checked=False)
```

### Sorting items in a lane

```python
# Default: alphabetical by content
lane.sort()

# Custom key: sort by due date
lane.sort(key=lambda item: item.inline_fields["due"])

# Multi-key: priority tag group, then due date within each group
PRIORITY = {"#priority/critical": 0, "#priority/essential": 1, "#priority/enhancing": 2}
lane.sort(key=lambda item: (
    next((PRIORITY[t] for t in item.tags if t in PRIORITY), len(PRIORITY)),
    item.inline_fields["due"] or datetime.date.max,
))
```

### Moving items

```python
from obsidian_kanban_parser import move_item

move_item(item, from_lane=board["Todo"], to_lane=board["Done"])
move_item(item, from_lane=board["Todo"], to_lane=board["Done"], position=0)
```

### Archiving

```python
board.archive_item(item, from_lane=board["Todo"])       # returns True on success
board.unarchive_item(item, to_lane=board["Backlog"])    # returns True on success
```

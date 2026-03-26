# obsidian-kanban-parser
This libray is a Python based parser and writer for Markdown files created by the [Obsidian Kanban plugin](https://github.com/obsidian-community/obsidian-kanban).
It purpose is to allow users to manipulate their Kanban boards programmatically, via Python based scripts, while ensuring the that resulting Markdown files remain fully compatible with the Obsidian plugin.


## Design Principles
- Round-trip fidelity: parsing and then writing a file should produce identical content, preserving formatting and metadata.
- The library should be purely Python-based, with no external dependencies beyond the standard library. Libraries maybe use for development and testing, but not in the installable package.
- To ensure compatibility with the Obsidian plugin, the library should mirror the plugin's own parsing and serialization logic as closely as possible (e.g. mimicking files like: [src/parsers/helpers/parser.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/helpers/parser.ts), [src/parsers/formats/list.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/formats/list.ts), [src/parsers/common.ts](https://github.com/obsidian-community/obsidian-kanban/blob/main/src/parsers/common.ts), , etc.).
- The library should provide a clean and well design API with properties such as:
  - Pythonic data structures.
  - There should only be a single way of doing things, and it should be the most intuitive way.
  - There should be a single source of truth for each piece of data.
  - The library should be designed with extensibility in mind.
  - The code must be easy to read and understand by both humans and machines (e.g. for LLMs).
  - The library should be well tested, with a comprehensive test suite covering all functionality and edge
  - The API exposed via the package should be stable and not expose internal implementation details or utilities that are not intended for public use.



## Features

### Read and writing Kanban boards
```python
from obsidian_kanban_parser import parse, write

with open("board.md", "r") as f:
    text = f.read()
board = parse(text)

# manipulate board object as needed
...

with open("board.md", "w") as f:
    f.write(write(board))

```

### Move tasks between lanes
```python
from obsidian_kanban_parser import move_item, parse, write, find_lane_by_name

board = ...
todo_lane = find_lane_by_name(board, "To Do")
in_progress_lane = find_lane_by_name(board, "In Progress")

for item in todo_lane.items:
    move_item(board=board, item=item, lane=in_progress_lane)

```

### Move tasks between boards
```python
from obsidian_kanban_parser import move_item, parse, write, find_lane_by_name

with open("board1.md", "r") as f:
    text1 = f.read()
board1 = parse(text1)
with open("board2.md", "r") as f:
    text2 = f.read()
board2 = parse(text2)

todo_lane_board1 = find_lane_by_name(board1, "To Do")
todo_lane_board2 = find_lane_by_name(board2, "To Do")

for item in todo_lane_board1.items:
    move_item(board=board1, item=item, lane=todo_lane_board2)
```

### Find tasks with inline fields
```python
from obsidian_kanban_parser import parse, find_items_by_inline_field, move_item, find_lane_by_name
import datetime

board = ...
items_with_due_date = find_items_by_inline_field(board, "due")
find_lane_by_name = find_lane_by_name(board, "Overdue")
for item in items_with_due_date:
    if item.inline_fields["due"] < datetime.date.today():
        move_item(board=board, item=item, lane=find_lane_by_name)


```

### Inline fields
```python
import datetime
item = ...

# Accessing inline fields
item.inline_fields["due"]  # returns a datetime.date object if the field is a date
item.inline_fields["rating"]  # returns an int or float if the field is a number
item.inline_fields["status"]  # returns a string if the field is a string
item.inline_fields["unknown_field"]  # returns None if the field is not present.

# Adding or updating inline field
item.inline_fields["scheduled"] = datetime.date(2024, 6, 1)  # add the inline field: `[scheduled:: 2024-06-01]`
item.inline_fields["priority"] = "high"  # add the inline field: `[priority:: high]`
item.inline_fields["cost"] = 4.5  # add the inline field: `[cost:: 4.5]`

# Removing an inline field
del item.inline_fields["scheduled"]

# Checking if an inline field exists
"due" in item.inline_fields # True if the "due" inline field exists, False otherwise
```

### Finding items by tag
```python
from obsidian_kanban_parser import parse, find_items_by_tag
board = ...

items_with_important_tag = find_items_by_tag(board, "important")

for item in items_with_important_tag:
    assert "important" in item.tags
    del item.tags["important"]  # remove the tag from the item
    item.tags.append("important")  # add it back to the end of the tags list
```

### Archiving items
```python
from obsidian_kanban_parser import parse, archive_item, unarchive_item, find_lane_by_name
board = ...
lane = find_lane_by_name(board, "Done")
item = None
for item in lane.items:
    archive_item(board=board, item=item, lane=lane)

if item is not None:
    # undo last archive
    unarchive_item(board=board, item=item, lane=lane)
```

### Create and remove a items
```python
from obsidian_kanban_parser import parse, add_item, find_lane_by_name, remove_item
board = ...
lane = find_lane_by_name(board, "To Do")
item = add_item(board=board, lane=lane, title="New Task")

# and undo it:
remove_item(board=board, item=item, lane=lane)
```

### Add and remove subtasks
```python
from obsidian_kanban_parser import parse, add_subtask, remove_subtask, find_lane_by_name, get_subtasks
board = ...
lane = find_lane_by_name(board, "To Do")

for item in lane.items:
    # remove all existing subtasks
    for is_done, subtask_text in get_subtasks(item):
        remove_subtask(item=item, subtask_text=subtask_text)

    # adding new ones subtasks
    for i in range(3):
        add_subtask(item=item, subtask_text=f"Subtask {i+1}", checked=(i%2==0))

```

## Which tasks are checked / done?
```python
board = ...
done_lane = find_lane_by_name(board, "Done")
todo_lane = find_lane_by_name(board, "To Do")

for item in done_lane.items:
    assert item.checked == True  # all items in the "Done" lane should be marked as done

for item in todo_lane.items:
    assert item.checked == False  # all items in the "To Do" lane should be marked as not done


item.checked = True  # mark all item as checked `- [x]`
item.checked = False  # mark all item as unchecked `- [ ]`


```

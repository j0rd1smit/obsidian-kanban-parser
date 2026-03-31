# API Change Proposals

## 1. Move subtask operations to KanbanItem methods

Subtasks live entirely within `title_raw` of a single item — they don't touch lanes or boards. Having them as standalone functions in `data_manipulation.py` is inconsistent with `add_tag`/`remove_tag` which are already methods.

### Original API
```python
from obsidian_kanban_parser import add_subtask, remove_subtask, get_subtasks

add_subtask(item, "Write tests", checked=False)
remove_subtask(item, "Write tests")
subtasks = get_subtasks(item)  # [(False, "Write tests"), ...]
```

### Proposed API
```python
item.add_subtask("Write tests", checked=False)
item.remove_subtask("Write tests")
item.subtasks  # [(False, "Write tests"), ...] — property like .tags
```

---

## 2. Move `find_lane_by_name` to `KanbanBoard` only (remove standalone function)

`find_lane_by_name(board, name)` is an exact duplicate of `board.lane(name)`. The standalone function should be removed from the public API. The method already exists.

### Original API
```python
from obsidian_kanban_parser import find_lane_by_name

lane = find_lane_by_name(board, "Todo")
# or equivalently:
lane = board.lane("Todo")
```

### Proposed API
```python
lane = board.lane("Todo")  # the only way
```

---

## 3. Move `find_items_by_tag` and `find_items_by_inline_field` to KanbanBoard methods

These search across a single board's lanes. They belong on the board object.

### Original API
```python
from obsidian_kanban_parser import find_items_by_tag, find_items_by_inline_field

results = find_items_by_tag(board, "#bug")
results = find_items_by_inline_field(board, "priority", "1")
```

### Proposed API
```python
results = board.find_items_by_tag("#bug")
results = board.find_items_by_inline_field("priority", "1")
```

---

## 4. Move `add_item` and `remove_item` to KanbanLane methods

Currently these take a `board` + `lane_title: str`, do an internal lookup, and operate on the lane. The caller typically already has the lane object. Let the caller pass the lane directly.

### Original API
```python
from obsidian_kanban_parser import add_item, remove_item

new_item = add_item(board, "Todo", "Fix the bug", position=0)
remove_item(board, item, "Todo")
```

### Proposed API
```python
lane = board.lane("Todo")
new_item = lane.add_item("Fix the bug", position=0)
lane.remove_item(item)
```

---

## 5. Move `archive_item` and `unarchive_item` to KanbanBoard methods

These operate on a board's lanes and archive list. They take `from_lane: str` / `to_lane: str` as string lookups. Accept lane objects instead for consistency.

### Original API
```python
from obsidian_kanban_parser import archive_item, unarchive_item

archive_item(board, item, "Done")
unarchive_item(board, item, "Todo")
```

### Proposed API
```python
board.archive_item(item, from_lane=done_lane)
board.unarchive_item(item, to_lane=todo_lane)
```

---

## 6. Change `move_item` to accept lane objects instead of strings

`move_item` makes sense as a standalone function (cross-board moves), but it should accept lane objects rather than doing internal string-based lookups. This also enables future cross-board moves where lanes come from different boards.

### Original API
```python
from obsidian_kanban_parser import move_item

move_item(board, item, "Todo", "In Progress", position=0)
```

### Proposed API
```python
from obsidian_kanban_parser import move_item

todo = board.lane("Todo")
in_progress = board.lane("In Progress")
move_item(item, from_lane=todo, to_lane=in_progress, position=0)
```

Note: `board` parameter removed — no longer needed since lanes are passed directly.

---

## 7. Make `checked` a writable property (setter)

Currently `checked` is read-only. Users have to manually set `check_char` to toggle a card's completion status, which leaks implementation details.

### Original API
```python
item.checked        # True/False (read-only)
item.check_char = "x"  # to mark complete — leaks internal detail
```

### Proposed API
```python
item.checked        # True/False (read)
item.checked = True   # sets check_char to "x"
item.checked = False  # sets check_char to " "
```

---

## 8. Dict-like `tags` proxy (like InlineFields)

Inline fields have a nice dict-like interface. Tags should get a similar Pythonic set-like interface instead of separate `has_tag` / `add_tag` / `remove_tag` methods.

### Original API
```python
item.tags              # ['#bug', '#frontend'] — read-only list
item.has_tag("bug")    # True
item.add_tag("urgent")
item.remove_tag("bug")
```

### Proposed API
```python
item.tags              # Tags proxy object
list(item.tags)        # ['#bug', '#frontend'] — iterable
"#bug" in item.tags    # True (via __contains__)
item.tags.add("urgent")
item.tags.remove("bug")
```

This mirrors Python's `set` interface (`add`, `remove`, `in`). The `has_tag`, `add_tag`, `remove_tag` methods are removed from `KanbanItem` — the proxy handles everything.

---

## 9. `__contains__` on KanbanLane for item membership

Make `item in lane` work naturally, useful for assertions and conditionals.

### Original API
```python
if item in lane.items:
    ...
```

### Proposed API
```python
if item in lane:
    ...
```

---

## 10. `__len__` on KanbanLane and KanbanBoard

Pythonic way to check how many items are in a lane or how many lanes a board has.

### Original API
```python
len(lane.items)
len(board.lanes)
```

### Proposed API
```python
len(lane)   # number of items in the lane
len(board)  # number of lanes on the board
```

---

## 11. `__iter__` on KanbanBoard for lane iteration

KanbanLane already supports `for item in lane`. KanbanBoard should support `for lane in board` for symmetry.

### Original API
```python
for lane in board.lanes:
    ...
```

### Proposed API
```python
for lane in board:
    ...
```

---

## 12. `__getitem__` on KanbanBoard and KanbanLane for index/name access

Allow bracket-based access for common lookups.

### Original API
```python
board.lane("Todo")       # by name
board.lanes[0]           # by index
lane.items[0]            # by index
```

### Proposed API
```python
board["Todo"]    # by name (str) — equivalent to board.lane("Todo")
board[0]         # by index (int) — equivalent to board.lanes[0]
lane[0]          # by index (int) — equivalent to lane.items[0]
```

---

## 13. Fix duplicate `add_subtask` in `__all__`

Minor bug: `add_subtask` appears twice in `__init__.py`'s `__all__` list (lines 26 and 30). Should appear once.

This will be resolved naturally as part of proposal 1 (subtask methods move to KanbanItem, removed from `__all__`).

---

## 14. Slim down `__init__.py` public exports

With methods moving onto domain objects, the public API of the package becomes much cleaner. Only truly standalone functions remain as top-level exports.

### Original API
```python
from obsidian_kanban_parser import (
    parse, write,
    find_items_by_tag, find_items_by_inline_field,
    find_lane_by_name,
    move_item,
    add_item, remove_item,
    archive_item, unarchive_item,
    add_subtask, remove_subtask, get_subtasks,
)
```

### Proposed API
```python
from obsidian_kanban_parser import parse, write, move_item
# Everything else is accessed via domain objects:
#   board.lane(), board.find_items_by_tag(), board.archive_item(), ...
#   lane.add_item(), lane.remove_item(), item in lane, ...
#   item.subtasks, item.add_subtask(), item.tags, item.checked = True, ...
```

The domain classes (`KanbanBoard`, `KanbanLane`, `KanbanItem`) should also be exported for type annotations:
```python
from obsidian_kanban_parser import KanbanBoard, KanbanLane, KanbanItem
```

import re

from obsidian_kanban_parser.domain import KanbanBoard, KanbanItem, KanbanLane


def find_items_by_tag(board: KanbanBoard, tag: str) -> list[tuple[KanbanLane, KanbanItem]]:
    """Return [(lane, item), ...] for every item that has the given tag.

    ``tag`` may be passed with or without a leading #.
    """
    tag = tag if tag.startswith("#") else f"#{tag}"
    results = []
    for lane in board.lanes:
        for item in lane.items:
            if item.has_tag(tag):
                results.append((lane, item))
    return results


def find_items_by_inline_field(
    board: KanbanBoard,
    key: str,
    value: str | None = None,
) -> list[tuple[KanbanLane, KanbanItem]]:
    """Return [(lane, item), ...] where the item has [key::...] (optionally matching value)."""
    results = []
    for lane in board.lanes:
        for item in lane.items:
            v = item.inline_fields[key]
            if v is not None and (value is None or str(v) == value):
                results.append((lane, item))
    return results


def move_item(
    board: KanbanBoard,
    item: KanbanItem,
    from_lane: str,
    to_lane: str,
    position: int = -1,
) -> bool:
    """Move ``item`` from one lane to another.

    ``position`` is the index in the destination lane (-1 = append).
    Returns True if the move succeeded, False if item or lanes were not found.
    """
    src = board.lane(from_lane)
    dst = board.lane(to_lane)
    if src is None or dst is None:
        return False
    if item not in src.items:
        return False

    src.items.remove(item)
    if position < 0 or position >= len(dst.items):
        dst.items.append(item)
    else:
        dst.items.insert(position, item)
    return True


def archive_item(board: KanbanBoard, item: KanbanItem, from_lane: str) -> bool:
    """Remove ``item`` from a lane and append it to the archive.

    Returns True on success.
    """
    lane = board.lane(from_lane)
    if lane is None or item not in lane.items:
        return False
    lane.items.remove(item)
    board.archive.append(item)
    return True


def unarchive_item(board: KanbanBoard, item: KanbanItem, to_lane: str) -> bool:
    """Move an archived item back into a lane.

    Returns True on success.
    """
    if item not in board.archive:
        return False
    dst = board.lane(to_lane)
    if dst is None:
        return False
    board.archive.remove(item)
    dst.items.append(item)
    return True


def add_item(
    board: KanbanBoard,
    lane_title: str,
    title_raw: str,
    check_char: str = " ",
    position: int = -1,
) -> KanbanItem | None:
    """Create a new item and insert it into a lane.

    Returns the new KanbanItem, or None if the lane was not found.
    """
    lane = board.lane(lane_title)
    if lane is None:
        return None
    item = KanbanItem(title_raw=title_raw, check_char=check_char)
    if position < 0 or position >= len(lane.items):
        lane.items.append(item)
    else:
        lane.items.insert(position, item)
    return item


def remove_item(board: KanbanBoard, item: KanbanItem, lane_title: str) -> bool:
    """Remove an item from a lane (does not archive it).

    Returns True on success.
    """
    lane = board.lane(lane_title)
    if lane is None or item not in lane.items:
        return False
    lane.items.remove(item)
    return True


def add_subtask(item: KanbanItem, subtask_text: str, checked: bool = False) -> None:
    """Append a checklist sub-task line to an item's title_raw.

    Sub-tasks are stored as markdown checklist lines within the card body,
    e.g.:
        Main card text
        - [ ] Sub-task A
        - [x] Sub-task B (done)
    """
    char = "x" if checked else " "
    subtask_line = f"\n- [{char}] {subtask_text}"
    item.title_raw = item.title_raw.rstrip() + subtask_line


def remove_subtask(item: KanbanItem, subtask_text: str) -> bool:
    """Remove a sub-task line from an item's title_raw by matching its text.

    Returns True if a line was removed, False otherwise.
    """
    pattern = re.compile(
        r"\n- \[.\] " + re.escape(subtask_text) + r"[ \t]*",
    )
    new, count = pattern.subn("", item.title_raw)
    if count:
        item.title_raw = new.rstrip()
        return True
    return False


def get_subtasks(item: KanbanItem) -> list[tuple[bool, str]]:
    """Return a list of (checked, text) for each sub-task line in title_raw."""
    results = []
    for m in re.finditer(r"\n- \[(.)\] (.+)", item.title_raw):
        results.append((m.group(1).lower() == "x", m.group(2)))
    return results


def find_lane_by_name(
    board: KanbanBoard,
    name: str,
) -> KanbanLane | None:
    """Return the first lane with the given name, or None if not found."""
    for lane in board.lanes:
        if lane.title == name:
            return lane
    return None

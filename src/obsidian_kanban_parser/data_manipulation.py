from obsidian_kanban_parser.domain import KanbanItem, KanbanLane


def move_item(
    item: KanbanItem,
    from_lane: KanbanLane,
    to_lane: KanbanLane,
    position: int = -1,
) -> bool:
    """Move ``item`` from one lane to another.

    ``position`` is the index in the destination lane (-1 = append).
    Returns True if the move succeeded, False if item was not found in from_lane.
    """
    if item not in from_lane.items:
        return False

    from_lane.items.remove(item)
    if position < 0 or position >= len(to_lane.items):
        to_lane.items.append(item)
    else:
        to_lane.items.insert(position, item)
    return True

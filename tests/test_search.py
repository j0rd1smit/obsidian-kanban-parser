"""Search / read tests.

Each test arranges a known markdown input, calls a read/query API,
and asserts on the returned domain objects (not on raw markdown).
"""

from obsidian_kanban_parser import find_items_by_inline_field, find_items_by_tag, find_lane_by_name, get_subtasks, parse

from tests.helpers import make_board, make_item, make_lane


# ---------------------------------------------------------------------------
# find_items_by_tag
# ---------------------------------------------------------------------------


def test_find_items_by_tag_single_match() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Fix bug #backend")))
    board = parse(md)

    # act
    results = find_items_by_tag(board, "#backend")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert "#backend" in item.title_raw


def test_find_items_by_tag_multiple_matches_across_lanes() -> None:
    # arrange
    md = make_board(
        make_lane("Todo", make_item("Task A #urgent")),
        make_lane("In Progress", make_item("Task B #urgent")),
    )
    board = parse(md)

    # act
    results = find_items_by_tag(board, "#urgent")

    # assert
    assert len(results) == 2
    titles = [item.title_raw for _, item in results]
    assert any("Task A" in t for t in titles)
    assert any("Task B" in t for t in titles)


def test_find_items_by_tag_no_match_returns_empty_list() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task without tags")))
    board = parse(md)

    # act
    results = find_items_by_tag(board, "#nonexistent")

    # assert
    assert results == []


def test_find_items_by_tag_without_hash_prefix() -> None:
    # arrange — tag passed without leading #
    md = make_board(make_lane("Todo", make_item("Task #feature")))
    board = parse(md)

    # act
    results = find_items_by_tag(board, "feature")

    # assert
    assert len(results) == 1


# ---------------------------------------------------------------------------
# find_items_by_inline_field
# ---------------------------------------------------------------------------


def test_find_items_by_inline_field_key_only() -> None:
    # arrange
    md = make_board(
        make_lane(
            "Todo",
            make_item("Task A [due::2024-06-01]"),
            make_item("Task B [priority::high]"),
        )
    )
    board = parse(md)

    # act
    results = find_items_by_inline_field(board, "due")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert item.inline_field("due") == "2024-06-01"


def test_find_items_by_inline_field_key_and_value() -> None:
    # arrange
    md = make_board(
        make_lane(
            "Todo",
            make_item("Task A [priority::high]"),
            make_item("Task B [priority::low]"),
        )
    )
    board = parse(md)

    # act
    results = find_items_by_inline_field(board, "priority", "high")

    # assert
    assert len(results) == 1
    _, item = results[0]
    assert "Task A" in item.title_raw


def test_find_items_by_inline_field_no_match_returns_empty_list() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("Task [priority::low]")))
    board = parse(md)

    # act
    results = find_items_by_inline_field(board, "due")

    # assert
    assert results == []


# ---------------------------------------------------------------------------
# find_lane_by_name
# ---------------------------------------------------------------------------


def test_find_lane_by_name_exists() -> None:
    # arrange
    md = make_board(make_lane("Backlog"), make_lane("In Progress"))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "In Progress")

    # assert
    assert lane is not None
    assert lane.title == "In Progress"


def test_find_lane_by_name_not_found_returns_none() -> None:
    # arrange
    md = make_board(make_lane("Todo"))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Nonexistent")

    # assert
    assert lane is None


# ---------------------------------------------------------------------------
# Iteration
# ---------------------------------------------------------------------------


def test_iterate_items_in_lane() -> None:
    # arrange
    md = make_board(make_lane("Todo", make_item("A"), make_item("B"), make_item("C")))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Todo")
    assert lane is not None
    titles = [item.title_raw for item in lane]

    # assert
    assert titles == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# get_subtasks
# ---------------------------------------------------------------------------


def test_get_subtasks_returns_checked_and_unchecked() -> None:
    # arrange
    md = make_board(make_lane("Backlog", make_item("Epic\n- [ ] Step 1\n- [x] Step 2")))
    board = parse(md)

    # act
    lane = find_lane_by_name(board, "Backlog")
    assert lane is not None
    item = lane.items[0]
    subtasks = get_subtasks(item)

    # assert
    assert subtasks == [(False, "Step 1"), (True, "Step 2")]
